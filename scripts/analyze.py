#! /usr/bin/python3

import os
import re
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rich.table import Table
from rich.console import Console

version = ''

cap = 1000000
if len(sys.argv) == 3 and sys.argv[1] == 'cap':
    cap = int(sys.argv[2])

if len(sys.argv) == 3:
    if sys.argv[1] == 'show':
        for config in os.listdir(f'data/{version}'):
            if os.path.exists(f'data/{version}' + config + '/' + sys.argv[2]):
                print(open(f'data/{version}' + config + '/' + sys.argv[2] + '/results.txt').read(), end = '')
                exit(0)

def f_or(x, y):
    return lambda z: x(z) or y(z)

def f_not(x):
    return lambda y: not x(y)

def f_insufficient(line):
    return bool(re.search(r'\[flag\] Ledger \d+ diverged and has insufficient support\n', line))

def f_timeout(line):
    return bool(re.search(r'\[flag\] Timeout after \d+ messages\n', line))

def f_incompatible(line):
    return bool(re.search(r'\[flag\] Incompatible ledger <.+>\n', line))

def count(f, flags):
    return len(list(filter(f, flags)))

built_ledger = re.compile(r'Built ledger #(\d+): (.*)')
def new_insufficient_support(path):
    hashes: dict[int, dict[int, str]] = {}
    for i in range(0, 7):
        with open(os.path.join(path, f'validator_{i}.txt'), 'r') as f:
            for line in f.readlines():
                if match := built_ledger.search(line.strip()):
                    if match.groups()[0] not in hashes:
                        hashes[match.groups()[0]] = {}
                    hashes[match.groups()[0]][i] = match.groups()[1]
    for ledger, vs in hashes.items():
        l, r = {}, {}
        lc, rc = 0, 0
        if 0 in vs:
            l.setdefault(vs[0], set())
            l[vs[0]].add(0)
            lc += 1
        if 1 in vs:
            l.setdefault(vs[1], set())
            l[vs[1]].add(1)
            lc += 1
        if 2 in vs:
            l.setdefault(vs[2], set())
            l[vs[2]].add(2)
            r.setdefault(vs[2], set())
            r[vs[2]].add(2)
            lc += 1
        if 4 in vs:
            l.setdefault(vs[4], set())
            l[vs[4]].add(4)
            r.setdefault(vs[4], set())
            r[vs[4]].add(4)
            rc += 1
        if 5 in vs:
            r.setdefault(vs[5], set())
            r[vs[5]].add(5)
            rc += 1
        if 6 in vs:
            r.setdefault(vs[6], set())
            r[vs[6]].add(6)
            rc += 1
        # if len(vs) < 7 and vs[0] == vs[1] and vs[1] == vs[2] and vs[2] != vs[4] and vs[4] == vs[5] and vs[5] == vs[6]:
        #     return True
        for lLedger in l:
            for rLedger in r:
                if len(l[lLedger]) > 2 and len(r[rLedger]) > 2:
                    if lLedger != rLedger:
                        return True
    return False

def new_incompatible_ledger(path):
    nodes = set()
    for i in range(0, 7):
        with open(os.path.join(path, f'validator_{i}.txt'), 'r') as f:
            for line in f.readlines():
                if 'Not validating incompatible' in line:
                    nodes.add(i)
    return len(nodes.intersection([0, 1, 2, 3, 4])) > 1 or len(nodes.intersection([2, 3, 4, 5, 6])) > 1


def stats(filters, protocol=None, return_agg=False, use_baseline_configs=False):
    if protocol is None:
        from src.protocols.xrpl import XRPLProtocol
        protocol = XRPLProtocol()

    bug_types = protocol.get_bug_types()

    # Build agg dict dynamically from protocol's bug types
    agg = {bt: {'TP': set(), 'FP': set(), 'TN': set(), 'FN': set()} for bt in bug_types}
    all_runs = []
    filters = list(map(str, filters))

    table = Table()
    scores = Table()

    table.add_column("Configuration", justify="right", style="cyan", no_wrap=True)
    table.add_column("Total", justify='right')
    table.add_column("Correct", style='green', justify='right')
    for bt in bug_types:
        table.add_column(bt, justify='right')

    scores.add_column('Metric')
    for bt in bug_types:
        scores.add_column(bt, justify='right')

    config_iter = protocol.iter_baseline_run_configs() if use_baseline_configs else protocol.iter_run_configs()
    for config_label, run_paths in config_iter:
        print(f'- found {len(run_paths)} runs')
        correct = []
        bug_counts = {bt: [] for bt in bug_types}
        run_paths_capped = run_paths[:cap]
        all_runs += run_paths_capped
        for run_path in run_paths_capped:
            run_id = run_path.replace("\\", "/")
            p = len(filters) == 0 or run_id in filters

            actual_bugs = protocol.classify_run(run_path)

            if not actual_bugs:
                correct.append(run_id)

            for bt in bug_types:
                if bt in actual_bugs:
                    agg[bt]['TP' if p else 'FN'].add(run_id)
                    bug_counts[bt].append(run_id)
                else:
                    agg[bt]['FP' if p else 'TN'].add(run_id)

        table.add_row(config_label, str(len(run_paths_capped)), str(len(correct)),
                       *[str(len(bug_counts[bt])) for bt in bug_types])

    console = Console()
    console.print(table)

    def safe_div(a, b):
        return a / b if b > 0 else 0.0

    sensitivity = lambda l: safe_div(len(agg[l]['TP']), len(agg[l]['TP']) + len(agg[l]['FN']))
    specifity = lambda l: safe_div(len(agg[l]['TN']), len(agg[l]['TN']) + len(agg[l]['FP']))
    precision = lambda l: safe_div(len(agg[l]['TP']), len(agg[l]['TP']) + len(agg[l]['FP']))
    f1 = lambda l: 0 if precision(l) + sensitivity(l) == 0 else 2 * (precision(l) * sensitivity(l)) / (precision(l) + sensitivity(l))
    f0_5 = lambda l: 0 if precision(l) + sensitivity(l) == 0 else 1.25 * (precision(l) * sensitivity(l)) / (0.25 * precision(l) + sensitivity(l))
    accuracy = lambda l: safe_div(len(agg[l]['TP']) + len(agg[l]['TN']),
                                  len(agg[l]['TP']) + len(agg[l]['TN']) + len(agg[l]['FP']) + len(agg[l]['FN']))

    scores.add_row('Precision', *['{:.1%}'.format(precision(bt)) for bt in bug_types])
    scores.add_row('Recall', *['{:.1%}'.format(sensitivity(bt)) for bt in bug_types])
    scores.add_row('F1', *['{:.1%}'.format(f1(bt)) for bt in bug_types])
    scores.add_row('F0.5', *['{:.1%}'.format(f0_5(bt)) for bt in bug_types])
    scores.add_row('Specifity', *['{:.1%}'.format(specifity(bt)) for bt in bug_types])
    scores.add_row('Accuracy', *['{:.1%}'.format(accuracy(bt)) for bt in bug_types])

    console.print(scores)

    if return_agg:
        return agg

if __name__ == '__main__':
    import argparse
    from src.protocols import PROTOCOL_CHOICES, make_protocol

    parser = argparse.ArgumentParser(description='Print the per-bug confusion matrix for a protocol.')
    parser.add_argument('--protocol', choices=PROTOCOL_CHOICES, default='xrpl',
                        help='Which consensus protocol adapter to use.')
    # Ignore the legacy positional `cap N` and `show <run>` forms — they are
    # consumed by module-top-level parsing.
    args, _ = parser.parse_known_args()
    stats([], protocol=make_protocol(args.protocol))
