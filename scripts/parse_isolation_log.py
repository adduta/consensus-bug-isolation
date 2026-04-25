"""Parse a run_analysis.py log and produce a markdown results document.

Reads the log line-by-line, extracts each isolation iteration's predicate,
Tarantula score, aggregation counts, removed-run list, per-config bug counts,
and full metrics table (Precision/Recall/F1/F0.5/Specificity/Accuracy per
bug class). Writes a markdown summary to the given output path.
"""
import re
import sys
from pathlib import Path

LOG_PATH = sys.argv[1] if len(sys.argv) > 1 else '/tmp/pbft_isolation.log'
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else 'PBFT_NEW_TAXONOMY_RESULTS.md'

PREDICATE_RE = re.compile(
    r'^([0-9]+\.[0-9]+) "Predicate\((.+?)\)" > (\d+) '
    r'\(f_true: (\d+), f_false: (\d+), s_true: (\d+), s_false: (\d+)\)'
)
FAILED_RE = re.compile(r'^(\d+) failed reports')
REMOVED_RE = re.compile(r'^removed (\d+) (.+)')
REPORTS_LINE_RE = re.compile(r'^(\d+) reports')
AGG_LINE_RE = re.compile(r'^(\d+) aggregations')
FILT_LINE_RE = re.compile(r'^(\d+) filtered aggregations')
BUG_HEADER_RE = re.compile(r'┃ Configuration ┃')
SCORE_HEADER_RE = re.compile(r'┃ Metric')
SCORE_ROW_RE = re.compile(
    r'^│\s+(\w[\w.]*)\s+│\s+([\d.]+)%\s+│\s+([\d.]+)%\s+│\s+([\d.]+)%\s+│\s+([\d.]+)%\s+│'
)
COUNT_ROW_RE = re.compile(
    r'^│\s+(\S.*?)\s+│\s+(\d+)\s+│\s+(\d+)\s+│\s+(\d+)\s+│\s+(\d+)\s+│\s+(\d+)\s+│\s+(\d+)\s+│'
)


def parse(log_text: str):
    lines = log_text.splitlines()
    iterations = []
    current = None
    pending_failed = None
    pending_reports = None
    pending_agg = None
    pending_filt = None
    in_count_table = False
    in_score_table = False

    for raw in lines:
        # Strip ANSI carriage returns + tqdm progress lines
        line = raw.split('\r')[-1].rstrip()
        if not line:
            continue

        if line.startswith('Phase'):
            continue

        m = REPORTS_LINE_RE.match(line)
        if m:
            pending_reports = int(m.group(1))
            continue
        m = AGG_LINE_RE.match(line)
        if m:
            pending_agg = int(m.group(1))
            continue
        m = FILT_LINE_RE.match(line)
        if m:
            pending_filt = int(m.group(1))
            continue
        m = FAILED_RE.match(line)
        if m:
            pending_failed = int(m.group(1))
            continue

        m = PREDICATE_RE.match(line)
        if m:
            current = {
                'iteration': len(iterations) + 1,
                'tarantula': float(m.group(1)),
                'predicate': m.group(2),
                'tolerance': int(m.group(3)),
                'f_true': int(m.group(4)),
                'f_false': int(m.group(5)),
                's_true': int(m.group(6)),
                's_false': int(m.group(7)),
                'failed_at_start': pending_failed,
                'reports_at_start': pending_reports,
                'aggregations': pending_agg,
                'filtered_aggregations': pending_filt,
                'removed_count': 0,
                'removed_runs': [],
                'config_counts': [],
                'metrics': {},
            }
            iterations.append(current)
            continue

        m = REMOVED_RE.match(line)
        if m and current is not None:
            current['removed_count'] = int(m.group(1))
            paths = [p.strip() for p in m.group(2).split(',') if p.strip()]
            current['removed_runs'] = paths
            continue

        if BUG_HEADER_RE.search(line):
            in_count_table = True
            in_score_table = False
            continue
        if SCORE_HEADER_RE.search(line):
            in_score_table = True
            in_count_table = False
            continue

        if in_count_table and current is not None:
            m = COUNT_ROW_RE.match(line)
            if m:
                current['config_counts'].append({
                    'config': m.group(1).strip(),
                    'total': int(m.group(2)),
                    'correct': int(m.group(3)),
                    'oc': int(m.group(4)),
                    'vcf': int(m.group(5)),
                    'qs': int(m.group(6)),
                    'sb': int(m.group(7)),
                })
                continue

        if in_score_table and current is not None:
            m = SCORE_ROW_RE.match(line)
            if m:
                metric_name = m.group(1)
                current['metrics'][metric_name] = {
                    'OC': float(m.group(2)),
                    'VCF': float(m.group(3)),
                    'QS': float(m.group(4)),
                    'SB': float(m.group(5)),
                }
                continue

    return iterations


CLASS_LABEL = {
    'OC': 'Operation Corruption',
    'VCF': 'View-Change Fault',
    'QS': 'Quorum Stall',
    'SB': 'Split Brain',
}
METRIC_ORDER = ['Precision', 'Recall', 'F1', 'F0.5', 'Specifity', 'Accuracy']


def best_class(metrics: dict) -> str:
    if 'Precision' not in metrics:
        return ''
    p = metrics['Precision']
    return max(p, key=p.get)


def render(iterations):
    out = []
    out.append('# PBFT ISOLATION Results — New 4-Class Taxonomy')
    out.append('')
    out.append('Dataset: `out copy/` — 2800 runs across 14 configs (200 per config), '
               '2380 correct, 420 failures.')
    out.append('')
    out.append('Bug classes: **Operation Corruption (OC)**, **View-Change Fault (VCF)**, '
               '**Quorum Stall (QS)**, **Split Brain (SB)**.')
    out.append('')
    out.append(f'Iterations: {len(iterations)} (every failure isolated).')
    out.append('')

    # ---- Top-level summary table
    out.append('## Iteration summary')
    out.append('')
    out.append('| # | Predicate | Tol. | Tarantula | f_true | f_false | s_true | s_false | Removed | Best class | P | R | F1 | F0.5 |')
    out.append('|---|-----------|------|-----------|--------|---------|--------|---------|---------|-----------|---|---|-----|------|')
    for it in iterations:
        bc = best_class(it['metrics'])
        bc_label = CLASS_LABEL.get(bc, bc)
        p = it['metrics'].get('Precision', {}).get(bc, 0.0)
        r = it['metrics'].get('Recall', {}).get(bc, 0.0)
        f1 = it['metrics'].get('F1', {}).get(bc, 0.0)
        f05 = it['metrics'].get('F0.5', {}).get(bc, 0.0)
        out.append(
            f"| {it['iteration']} "
            f"| `{it['predicate']}` "
            f"| >{it['tolerance']} "
            f"| {it['tarantula']:.4f} "
            f"| {it['f_true']} "
            f"| {it['f_false']} "
            f"| {it['s_true']} "
            f"| {it['s_false']} "
            f"| {it['removed_count']} "
            f"| {bc_label} "
            f"| {p:.1f}% "
            f"| {r:.1f}% "
            f"| {f1:.1f}% "
            f"| {f05:.1f}% |"
        )
    out.append('')

    # ---- Detailed per-iteration sections
    out.append('## Detailed iteration breakdown')
    out.append('')
    for it in iterations:
        out.append(f"### Iteration {it['iteration']} — Tarantula {it['tarantula']:.4f}")
        out.append('')
        out.append(f"**Predicate**: `{it['predicate']}` > {it['tolerance']}")
        out.append('')
        out.append(f"**Aggregation**: f_true={it['f_true']}, f_false={it['f_false']}, "
                   f"s_true={it['s_true']}, s_false={it['s_false']}")
        out.append('')
        if it['reports_at_start'] is not None:
            out.append(f"**Pipeline state at iteration start**: "
                       f"{it['reports_at_start']} reports, "
                       f"{it['aggregations']} aggregations, "
                       f"{it['filtered_aggregations']} filtered aggregations, "
                       f"{it['failed_at_start']} failed reports.")
            out.append('')
        out.append(f"**Removed runs**: {it['removed_count']}")
        out.append('')

        # Metrics table
        if it['metrics']:
            out.append('| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |')
            out.append('|--------|----------------------|-------------------|--------------|-------------|')
            for metric in METRIC_ORDER:
                row = it['metrics'].get(metric)
                if not row:
                    continue
                display_name = 'Specificity' if metric == 'Specifity' else metric
                out.append(
                    f"| {display_name} "
                    f"| {row['OC']:.1f}% "
                    f"| {row['VCF']:.1f}% "
                    f"| {row['QS']:.1f}% "
                    f"| {row['SB']:.1f}% |"
                )
            out.append('')

        # Per-config counts table (counts of which bug class each config holds —
        # static across iterations, so render once below; skip here for brevity).

        # Removed run list
        if it['removed_runs']:
            out.append('<details><summary>Removed run paths</summary>')
            out.append('')
            for path in it['removed_runs']:
                out.append(f'- `{path}`')
            out.append('')
            out.append('</details>')
            out.append('')

    # ---- Per-config bug counts (use first iteration; static)
    if iterations and iterations[0]['config_counts']:
        out.append('## Per-config bug-class distribution')
        out.append('')
        out.append('Counts are static across iterations (the classifier is run once per run path).')
        out.append('')
        out.append('| Configuration | Total | Correct | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |')
        out.append('|---------------|-------|---------|----------------------|-------------------|--------------|-------------|')
        for row in iterations[0]['config_counts']:
            out.append(
                f"| {row['config']} "
                f"| {row['total']} "
                f"| {row['correct']} "
                f"| {row['oc']} "
                f"| {row['vcf']} "
                f"| {row['qs']} "
                f"| {row['sb']} |"
            )
        out.append('')

    # ---- Aggregate sums
    if iterations and iterations[0]['config_counts']:
        totals = {'total': 0, 'correct': 0, 'oc': 0, 'vcf': 0, 'qs': 0, 'sb': 0}
        for row in iterations[0]['config_counts']:
            for k in totals:
                totals[k] += row[k]
        out.append('**Totals across all configs**: '
                   f"{totals['total']} runs, {totals['correct']} correct, "
                   f"{totals['oc']} Operation Corruption, "
                   f"{totals['vcf']} View-Change Fault, "
                   f"{totals['qs']} Quorum Stall, "
                   f"{totals['sb']} Split Brain.")
        out.append('')

    return '\n'.join(out)


def main():
    log = Path(LOG_PATH).read_text(errors='replace')
    iterations = parse(log)
    if not iterations:
        print('No iterations parsed from log.', file=sys.stderr)
        sys.exit(1)
    md = render(iterations)
    Path(OUT_PATH).write_text(md)
    print(f'Wrote {len(iterations)} iterations to {OUT_PATH}')


if __name__ == '__main__':
    main()
