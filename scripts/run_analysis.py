#!/usr/bin/env python3
"""
Unified analysis entry point.

Usage:
    .venv/bin/python scripts/run_analysis.py --protocol xrpl
    .venv/bin/python scripts/run_analysis.py --protocol pbft
    .venv/bin/python scripts/run_analysis.py --protocol xrpl --baseline
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def get_protocol(name: str, scope: str | None = None):
    if name == 'xrpl':
        from src.protocols.xrpl import XRPLProtocol
        return XRPLProtocol()
    elif name == 'pbft':
        from src.protocols.pbft import PBFTProtocol
        return PBFTProtocol(scope=scope)
    else:
        print(f"Unknown protocol '{name}'. Choose from: xrpl, pbft", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Run the ISOLATION fault-localization algorithm.'
    )
    parser.add_argument(
        '--protocol', required=True, choices=['xrpl', 'pbft'],
        help='Consensus protocol to analyse.'
    )
    parser.add_argument(
        '--baseline', action='store_true',
        help='Use PRED-based baseline pipeline instead of message-based pipeline.'
    )
    parser.add_argument(
        '--scope', choices=['ss', 'as'], default=None,
        help='PBFT only: restrict to small-scope (ss) or all-scope (as) configs.'
    )
    args = parser.parse_args()

    protocol = get_protocol(args.protocol, scope=args.scope)

    if args.baseline:
        from scripts.baseline import run_baseline_analysis
        run_baseline_analysis(protocol=protocol)
    else:
        from scripts.main import run_message_based_analysis
        run_message_based_analysis(protocol=protocol)

if __name__ == '__main__':
    main()