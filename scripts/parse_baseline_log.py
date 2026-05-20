"""Parse a baseline (--baseline) run_analysis.py log into a markdown summary.

Baseline iteration headers look like:
    0.5473493795128186 BRANCH DefaultReplica.java:621 is false (f_true: 292, ...)

This is structurally identical to the message-based parser, but the predicate
syntax is different (PRED-annotation form, not Predicate(...) form), so it
needs its own regex.
"""
import re
import sys
from pathlib import Path

LOG_PATH = sys.argv[1] if len(sys.argv) > 1 else 'logs/pbft_baseline.log'
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else 'PBFT_BASELINE_NEW_TAXONOMY_RESULTS.md'

PREDICATE_RE = re.compile(
    r'^([0-9]+\.[0-9]+(?:[eE][+-]?\d+)?)\s+(\S.*?)\s+'
    r'\(f_true: (\d+), f_false: (\d+), s_true: (\d+), s_false: (\d+)\)'
)
FAILED_RE = re.compile(r'^(\d+) failed reports')
REMOVED_RE = re.compile(r'^removed (\d+) (.+)')
REPORTS_LINE_RE = re.compile(r'^(\d+) reports')
AGG_LINE_RE = re.compile(r'^(\d+) aggregations')
FILT_LINE_RE = re.compile(r'^(\d+) filtered aggregations')
BUG_HEADER_RE = re.compile(r'┃ Configuration ┃')
SCORE_HEADER_RE = re.compile(r'┃ Metric')
PERCENT_CELL_RE = re.compile(r'^([\d.]+)%$')

# Bug classes in the order produced by PBFTProtocol.get_bug_types().
CLASS_ORDER = ['OC', 'VCF', 'PT', 'NPP', 'SB']
CLASS_LABEL = {
    'OC': 'Operation Corruption',
    'VCF': 'View-Change Fault',
    'PT': 'Partition Timeout',
    'NPP': 'Non-PP Mutation',
    'SB': 'Split Brain',
}


def _split_row(line: str) -> list[str] | None:
    """Split a │-delimited rich-table row into stripped cells."""
    s = line.strip()
    if not (s.startswith('│') and s.endswith('│')):
        return None
    return [c.strip() for c in s[1:-1].split('│')]


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
        line = raw.split('\r')[-1].rstrip()
        if not line:
            continue
        if line.startswith('Phase') or line.startswith('Processed') \
                or line.startswith('Starting') or line.startswith('Predicates partitioned'):
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
                'f_true': int(m.group(3)),
                'f_false': int(m.group(4)),
                's_true': int(m.group(5)),
                's_false': int(m.group(6)),
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
            cells = _split_row(line)
            if cells and len(cells) == 3 + len(CLASS_ORDER):
                try:
                    total = int(cells[1])
                    correct = int(cells[2])
                    per_class = {cls: int(cells[3 + i]) for i, cls in enumerate(CLASS_ORDER)}
                except ValueError:
                    pass
                else:
                    current['config_counts'].append({
                        'config': cells[0],
                        'total': total,
                        'correct': correct,
                        **per_class,
                    })
                    continue

        if in_score_table and current is not None:
            cells = _split_row(line)
            if cells and len(cells) == 1 + len(CLASS_ORDER):
                vals = []
                ok = True
                for c in cells[1:]:
                    mp = PERCENT_CELL_RE.match(c)
                    if not mp:
                        ok = False
                        break
                    vals.append(float(mp.group(1)))
                if ok:
                    current['metrics'][cells[0]] = dict(zip(CLASS_ORDER, vals))
                    continue

    return iterations


METRIC_ORDER = ['Precision', 'Recall', 'F1', 'F0.5', 'Specifity', 'Accuracy']


def best_class(metrics: dict) -> str:
    if 'Precision' not in metrics:
        return ''
    p = metrics['Precision']
    return max(p, key=p.get)


def render(iterations):
    out = []
    out.append('# PBFT BASELINE Results — 5-Class Taxonomy')
    out.append('')
    out.append('Pipeline: **PRED-annotation baseline** (`scripts/baseline.py`). Predicates '
               'come from `PRED` markers emitted by the instrumented PBFT replica '
               '(`DefaultReplica.java`), not from message-pair evaluation.')
    out.append('')
    out.append('Dataset: `out copy/` — 2800 runs across 14 configs (200 per config), '
               '2380 correct, 420 failures.')
    out.append('')
    out.append('Bug classes: **Operation Corruption (OC)**, **View-Change Fault (VCF)**, '
               '**Partition Timeout (PT)**, **Non-PP Mutation (NPP)**, '
               '**Split Brain (SB)**.')
    out.append('')
    out.append(f'Iterations: {len(iterations)}.')
    out.append('')

    # ---- Top-level summary table
    out.append('## Iteration summary')
    out.append('')
    out.append('| # | Predicate | Tarantula | f_true | f_false | s_true | s_false | Removed | Best class | P | R | F1 | F0.5 |')
    out.append('|---|-----------|-----------|--------|---------|--------|---------|---------|-----------|---|---|-----|------|')
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
        out.append(f"**Predicate**: `{it['predicate']}`")
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

        if it['metrics']:
            header = '| Metric | ' + ' | '.join(CLASS_LABEL[c] for c in CLASS_ORDER) + ' |'
            sep = '|--------|' + '|'.join(['-' * (len(CLASS_LABEL[c]) + 2) for c in CLASS_ORDER]) + '|'
            out.append(header)
            out.append(sep)
            for metric in METRIC_ORDER:
                row = it['metrics'].get(metric)
                if not row:
                    continue
                display_name = 'Specificity' if metric == 'Specifity' else metric
                cells = ' | '.join(f"{row[c]:.1f}%" for c in CLASS_ORDER)
                out.append(f"| {display_name} | {cells} |")
            out.append('')

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
        header = ('| Configuration | Total | Correct | '
                  + ' | '.join(CLASS_LABEL[c] for c in CLASS_ORDER) + ' |')
        sep = ('|---------------|-------|---------|'
               + '|'.join(['-' * (len(CLASS_LABEL[c]) + 2) for c in CLASS_ORDER]) + '|')
        out.append(header)
        out.append(sep)
        for row in iterations[0]['config_counts']:
            cells = ' | '.join(str(row[c]) for c in CLASS_ORDER)
            out.append(
                f"| {row['config']} | {row['total']} | {row['correct']} | {cells} |"
            )
        out.append('')

    if iterations and iterations[0]['config_counts']:
        totals = {k: 0 for k in ['total', 'correct'] + CLASS_ORDER}
        for row in iterations[0]['config_counts']:
            for k in totals:
                totals[k] += row[k]
        class_phrase = ', '.join(f"{totals[c]} {CLASS_LABEL[c]}" for c in CLASS_ORDER)
        out.append('**Totals across all configs**: '
                   f"{totals['total']} runs, {totals['correct']} correct, "
                   f"{class_phrase}.")
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
