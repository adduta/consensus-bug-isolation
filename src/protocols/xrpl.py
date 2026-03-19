import os
import re

from .base import ConsensusProtocol
from ..models.messages import Proposal, Validation
from ..utils.config import FILTER_SET_LOW, FILTER_SET_HIGH, SET_LOW, SET_HIGH

__all__ = ['XRPLProtocol', 'Proposal', 'Validation']

_built_ledger = re.compile(r'Built ledger #(\d+): (.*)')

class XRPLProtocol(ConsensusProtocol):
    """XRPL consensus protocol adapter."""

    def get_fields(self) -> list[tuple[type, str, str]]:
        return [
            (Proposal,   'peers',            set[int]),
            (Proposal,   'close_time',        'time'),
            (Proposal,   'previous_ledger',   'hash_l'),
            (Proposal,   'propose_seq',       'seq_prp'),
            (Proposal,   'transaction_hash',  'hash_tx'),
            (Validation, 'peers',             set[int]),
            (Validation, 'consensus_hash',    'hash_tx'),
            (Validation, 'flags',             'flags'),
            (Validation, 'ledger_hash',       'hash_l'),
            (Validation, 'ledger_sequence',   'ledger_seq'),
            (Validation, 'signing_time',      'time'),
        ]

    def parse_log(self, path: str) -> list:
        from ..analysis.cache import read_multiline_json
        messages = []
        with open(path, 'r') as f:
            while line := f.readline():
                line = line.strip()
                if 'Received ProposeSet' in line:
                    messages.append(Proposal(read_multiline_json(f)))
                if 'Received Validation' in line:
                    messages.append(Validation(read_multiline_json(f)))
        return messages
    
    def get_num_nodes(self) -> int:
        return 7

    def filter_messages(self, messages: list, node_id: int) -> list:
        filter_set = FILTER_SET_LOW if node_id < 4 else FILTER_SET_HIGH
        return [m for m in messages if not m.peers.isdisjoint(filter_set)]

    def is_successful(self, run_dir: str) -> bool:
        with open(os.path.join(run_dir, 'results.txt'), 'r') as f:
            return 'reason: all committed' in f.read()

    def classify_run(self, run_dir: str) -> set:
        labels = set()
        if self.is_successful(run_dir):
            return labels
        if _new_insufficient_support(run_dir):
            labels.add('Insufficient')
        if _new_incompatible_ledger(run_dir):
            labels.add('Incompatible')
        if not labels:
            labels.add('Agreement')
        return labels

    def get_bug_types(self) -> list[str]:
        return ['Incompatible', 'Insufficient', 'Agreement']

    def wrap_observations(self, pred: str, observed_nodes: set) -> dict[str, bool]:
        nodes_low  = len(observed_nodes.intersection(SET_LOW))
        nodes_high = len(observed_nodes.intersection(SET_HIGH))
        return {
            f'"{pred}" > {t}': (nodes_low > t or nodes_high > t)
            for t in range(0, 5)
        }

# --- Ground-truth oracles (moved from analyze.py) ---
def _new_insufficient_support(path: str) -> bool:
    hashes: dict[str, dict[int, str]] = {}
    for i in range(7):
        with open(os.path.join(path, f'validator_{i}.txt'), 'r') as f:
            for line in f.readlines():
                if match := _built_ledger.search(line.strip()):
                    ledger_no, ledger_hash = match.groups()
                    hashes.setdefault(ledger_no, {})[i] = ledger_hash
    for _, vs in hashes.items():
        l: dict[str, set] = {}
        r: dict[str, set] = {}
        for node_id in [0, 1, 2, 3, 4]:
            if node_id in vs:
                l.setdefault(vs[node_id], set()).add(node_id)
        for node_id in [2, 3, 4, 5, 6]:
            if node_id in vs:
                r.setdefault(vs[node_id], set()).add(node_id)
        for lh in l:
            for rh in r:
                if lh != rh and len(l[lh]) > 2 and len(r[rh]) > 2:
                    return True
    return False

def _new_incompatible_ledger(path: str) -> bool:
    nodes = set()
    for i in range(7):
        with open(os.path.join(path, f'validator_{i}.txt'), 'r') as f:
            for line in f.readlines():
                if 'Not validating incompatible' in line:
                    nodes.add(i)
    return (
        len(nodes.intersection({0, 1, 2, 3, 4})) > 1 or
        len(nodes.intersection({2, 3, 4, 5, 6})) > 1
    )