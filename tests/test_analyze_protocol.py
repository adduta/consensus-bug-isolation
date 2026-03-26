import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.protocols.xrpl import XRPLProtocol
from scripts.analyze import stats

def test_stats_returns_agg_dict():
    protocol = XRPLProtocol()
    # Pass empty filters = treat all runs as not predicted (all FN for buggy, TN for correct)
    agg = stats([], protocol=protocol, return_agg=True)
    assert 'Incompatible' in agg
    assert 'Insufficient' in agg
    assert 'Agreement' in agg
    for bug_type in ['Incompatible', 'Insufficient', 'Agreement']:
        for key in ['TP', 'FP', 'TN', 'FN']:
            assert key in agg[bug_type]