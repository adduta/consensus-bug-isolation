"""Count failures per bug class across the dataset."""
import sys
import os
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.protocols.pbft import PBFTProtocol

def main():
    proto = PBFTProtocol(data_dir='out copy')
    paths = proto.get_run_paths()

    total = len(paths)
    correct = 0
    failures = 0
    bug_counts = Counter()
    multi_label = Counter()
    per_config = defaultdict(lambda: Counter())

    for p in paths:
        try:
            ok = proto.is_successful(p)
        except Exception as e:
            print(f"err is_successful {p}: {e}")
            continue
        if ok:
            correct += 1
            continue
        failures += 1
        try:
            groups = proto.classify_run(p)
        except Exception as e:
            print(f"err classify {p}: {e}")
            continue
        if not groups:
            bug_counts['(unclassified)'] += 1
            continue
        for g in groups:
            bug_counts[g] += 1
        multi_label[len(groups)] += 1

        config = os.path.basename(os.path.dirname(p))
        for g in groups:
            per_config[config][g] += 1

    print(f"Total runs:    {total}")
    print(f"Correct:       {correct}")
    print(f"Failures:      {failures}")
    print()
    print("Bug class counts (a single failure may be multi-labeled):")
    for cls, n in bug_counts.most_common():
        pct = 100.0 * n / failures if failures else 0
        print(f"  {cls:<25}  {n:>5}  ({pct:5.1f}% of failures)")
    print()
    print("Labels per failure:")
    for k in sorted(multi_label):
        print(f"  {k} label(s):  {multi_label[k]}")
    print()
    print("Per-config breakdown:")
    for cfg in sorted(per_config):
        cnts = per_config[cfg]
        line = ', '.join(f'{k}={v}' for k, v in sorted(cnts.items()))
        print(f"  {cfg:<25}  {line}")

if __name__ == '__main__':
    main()
