#!/usr/bin/env python3
"""
Baseline PRED-based Analysis Pipeline

This module implements the baseline approach that reads predicate observations
directly from PRED annotations in validator/replica logs (as opposed to the
message-based approach that evaluates predicates on message pairs).

Both approaches are equal, first-class approaches for consensus bug isolation:
- Baseline (this file): Uses pre-annotated PRED observations
- Message-based (main.py): Evaluates predicates on message pairs

This baseline uses the same statistical fault localization algorithm from
src/analysis/fault_localization.py but gets observations from PRED markers.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.analysis.fault_localization import isolate, Report
from scripts.analyze import stats


def run_baseline_analysis(protocol=None):
    """
    Run baseline PRED-based analysis pipeline.

    Reads PRED annotations from logs and performs statistical
    fault localization to identify failure-correlated predicates.

    Works for any protocol that implements parse_baseline_observations().
    """
    if protocol is None:
        from src.protocols.xrpl import XRPLProtocol
        protocol = XRPLProtocol()

    reports = []

    # Use protocol-specific baseline run discovery
    run_paths = protocol.get_baseline_run_paths()

    for run_path in run_paths:
        result = protocol.parse_baseline_observations(run_path)
        if result is None:
            continue
        correct, observations, run_name = result
        reports.append(Report(correct, observations, run_name))

    # Perform statistical fault localization using shared algorithm
    print(f"\nProcessed {len(reports)} runs with PRED annotations")
    print("Starting statistical fault localization...\n")
    isolate(reports, stats_fn=lambda filters: stats(
        filters, protocol=protocol, use_baseline_configs=True
    ))


if __name__ == '__main__':
    import argparse
    from src.protocols import PROTOCOL_CHOICES, make_protocol

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', choices=PROTOCOL_CHOICES, default='xrpl',
                        help='Which consensus protocol adapter to use.')
    args = parser.parse_args()

    protocol = make_protocol(args.protocol)
    if args.protocol == 'redisraft':
        # ModelFuzz traces do not carry PRED annotations.
        print('redisraft has no PRED-based baseline; skipping.')
    else:
        run_baseline_analysis(protocol)
