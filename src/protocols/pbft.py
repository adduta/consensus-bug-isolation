import re
import json
import os
from .base import ConsensusProtocol

# ---- Message types ----
class PrePrepare:
    __slots__ = ['view_no', 'seq_no', 'digest', 'operation_first',
                 'operation_second', 'timestamp', 'replica_id', 'peers']

    def __init__(self, sender: int, msg: dict) -> None:
        self.view_no          = msg.get('view-number', 0)
        self.seq_no           = msg.get('seq-number', 0)
        self.digest           = msg.get('digest', '')
        op                    = msg.get('operation', {})
        self.operation_first  = op.get('first', 0)
        self.operation_second = op.get('second', 0)
        self.timestamp        = msg.get('timestamp', 0)
        self.replica_id       = sender
        self.peers            = {sender}

    def __eq__(self, o):
        return isinstance(o, PrePrepare) and (
            self.view_no == o.view_no and self.seq_no == o.seq_no and
            self.operation_first == o.operation_first and
            self.operation_second == o.operation_second
        )

    def __hash__(self):
        return hash((self.view_no, self.seq_no, self.operation_first, self.operation_second))

    def __str__(self):
        return (f'PrePrepare(v={self.view_no}, s={self.seq_no}, '
                f'op=({self.operation_first},{self.operation_second}))')

class Prepare:
    __slots__ = ['view_no', 'seq_no', 'digest', 'replica_id', 'peers']

    def __init__(self, sender: int, msg: dict) -> None:
        self.view_no    = msg.get('view-number', 0)
        self.seq_no     = msg.get('seq-number', 0)
        self.digest     = msg.get('digest', '')
        self.replica_id = msg.get('replica-id', sender)
        self.peers      = {sender}

    def __eq__(self, o):
        return isinstance(o, Prepare) and (
            self.view_no == o.view_no and self.seq_no == o.seq_no and
            self.replica_id == o.replica_id
        )

    def __hash__(self):
        return hash((self.view_no, self.seq_no, self.replica_id))

    def __str__(self):
        return f'Prepare(v={self.view_no}, s={self.seq_no}, r={self.replica_id})'

class Commit:
    __slots__ = ['view_no', 'seq_no', 'digest', 'replica_id', 'peers']

    def __init__(self, sender: int, msg: dict) -> None:
        self.view_no    = msg.get('view-number', 0)
        self.seq_no     = msg.get('seq-number', 0)
        self.digest     = msg.get('digest', '')
        self.replica_id = msg.get('replica-id', sender)
        self.peers      = {sender}

    def __eq__(self, o):
        return isinstance(o, Commit) and (
            self.view_no == o.view_no and self.seq_no == o.seq_no and
            self.replica_id == o.replica_id
        )

    def __hash__(self):
        return hash((self.view_no, self.seq_no, self.replica_id))

    def __str__(self):
        return f'Commit(v={self.view_no}, s={self.seq_no}, r={self.replica_id})'

class ViewChange:
    __slots__ = ['new_view_no', 'last_seq_no', 'replica_id', 'peers']

    def __init__(self, sender: int, msg: dict) -> None:
        self.new_view_no = msg.get('new-view-number', 0)
        self.last_seq_no = msg.get('last-seq-number', 0)
        self.replica_id  = sender
        self.peers       = {sender}

    def __eq__(self, o):
        return isinstance(o, ViewChange) and (
            self.new_view_no == o.new_view_no and self.last_seq_no == o.last_seq_no and
            self.replica_id == o.replica_id
        )

    def __hash__(self):
        return hash((self.new_view_no, self.last_seq_no, self.replica_id))

    def __str__(self):
        return f'ViewChange(new_v={self.new_view_no}, last_s={self.last_seq_no})'

# ---- Parsing helpers ----

_SENT_RE    = re.compile(r'^Sent:\s+(\d+)\s+->\s+\S+\s+(\{.+\})\s+##\d+')
_MUTATED_RE = re.compile(r'^\s+-\s+Mutated:\s+\d+\s+->\s+\d+(\{.+\})\s+#\d+')
_VIOLATION_RE = re.compile(r'Violation of (\w+) at Replica:\s*(\d+).*viewNo:\s*(\d+).*seqNo:\s*(\d+)')
_DROPPED_RE = re.compile(r'^\s+-\s+Dropped:', re.MULTILINE)

class NewView:
    __slots__ = ['new_view_no', 'num_vc_proofs', 'num_prepared_proofs', 'replica_id', 'peers']

    def __init__(self, sender: int, msg: dict) -> None:
        self.new_view_no         = msg.get('new-view-number', 0)
        self.num_vc_proofs       = len(msg.get('view-change-proofs', []))
        self.num_prepared_proofs = len(msg.get('prepared-proofs', []))
        self.replica_id          = sender
        self.peers               = {sender}

    def __eq__(self, o):
        return isinstance(o, NewView) and (
            self.new_view_no == o.new_view_no and
            self.num_vc_proofs == o.num_vc_proofs and
            self.num_prepared_proofs == o.num_prepared_proofs and
            self.replica_id == o.replica_id
        )

    def __hash__(self):
        return hash((self.new_view_no, self.num_vc_proofs, self.num_prepared_proofs, self.replica_id))

    def __str__(self):
        return f'NewView(new_v={self.new_view_no}, vc={self.num_vc_proofs}, prep={self.num_prepared_proofs})'

_TYPE_CLASSES = {
    'PRE-PREPARE': PrePrepare,
    'PREPARE':     Prepare,
    'COMMIT':      Commit,
    'VIEW-CHANGE': ViewChange,
    'NEW-VIEW':    NewView,
}

def _parse_messages_from_log(text: str) -> list:
    """Extract all Sent: messages from a PBFT execution log."""
    messages = []
    for line in text.splitlines():
        m = _SENT_RE.match(line)
        if not m:
            continue

        sender_str, json_str = m.groups()
        sender = int(sender_str)
        try:
            msg = json.loads(json_str)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {json_str}")
            continue
        
        msg_type = msg.get('type', '')
        cls = _TYPE_CLASSES.get(msg_type)
        if not cls:
            print(f"Unknown message type: {msg_type}")
            continue

        messages.append(cls(sender, msg))
    return messages

def _parse_mutations_from_log(text: str) -> list[dict]:
    """Extract all mutated messages from a PBFT execution log."""
    
    mutations = []
    for line in text.splitlines():
        m = _MUTATED_RE.match(line)
        if not m:
            continue
        # The mutated JSON may be incomplete in the log; try best-effort parse
        try:
            msg = json.loads(m.group(1))
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {m.group(1)}")
            continue
        mutations.append(msg)
    return mutations

def _parse_violations_from_log(text: str) -> list[dict]:
    """Extract all violations from a PBFT execution log."""
    violations = []
    for line in text.splitlines():
        m = _VIOLATION_RE.search(line)
        if not m:
            continue
        vtype, replica, view_no, seq_no = m.groups()
        violations.append({
            'type': vtype, 'replica': int(replica),
            'view_no': int(view_no), 'seq_no': int(seq_no),
        })
    return violations

# ---- Protocol class ----

class PBFTProtocol(ConsensusProtocol):
    """PBFT consensus protocol adapter (ByzzFuzz test format)."""

    def __init__(self, scope: str | None = None):
        # scope: None = all configs, 'ss' = only -ss configs, 'as' = only -as configs
        self.scope = scope

    def _config_matches_scope(self, config: str) -> bool:
        if self.scope is None:
            return True
        if self.scope == 'ss':
            return config.endswith('-ss')
        if self.scope == 'as':
            return config.endswith('-as')
        return True

    def get_fields(self) -> list[tuple[type, str, str]]:
        return [
            (PrePrepare, 'view_no',             'view_current'),
            (PrePrepare, 'seq_no',              'seqno'),
            (PrePrepare, 'operation_first',     'op_first'),
            (PrePrepare, 'operation_second',    'op_second'),
            (PrePrepare, 'timestamp',           'time'),
            (Prepare,    'view_no',             'view_current'),
            (Prepare,    'seq_no',              'seqno'),
            (Prepare,    'replica_id',          'rid'),
            (Commit,     'view_no',             'view_current'),
            (Commit,     'seq_no',              'seqno'),
            (Commit,     'replica_id',          'rid'),
            (ViewChange, 'new_view_no',         'view_next'),
            (ViewChange, 'last_seq_no',         'seqno'),
            (ViewChange, 'replica_id',          'rid'),
            (NewView,    'new_view_no',         'view_next'),
            (NewView,    'num_vc_proofs',       'vc_proof_count'),
            (NewView,    'num_prepared_proofs', 'prep_proof_count'),
            (NewView,    'replica_id',          'rid'),
        ]

    def parse_log(self, path: str) -> list:
        with open(path, 'r') as f:
            text = f.read()
        return _parse_messages_from_log(text)

    def get_num_nodes(self) -> int:
        # Each PBFT run produces a single execution log; we treat it as 1 "node file"
        return 1
    
    def filter_messages(self, messages: list, node_id: int) -> list:
        return messages  # No partition filtering for PBFT

    def is_successful(self, run_path: str) -> bool:
        with open(run_path, 'r') as f:
            text = f.read()
        return 'Violation of' not in text and 'Reached test duration' not in text

    _CONFIG_RE = re.compile(r'tests-D(\d+)-C(\d+)')

    def _config_has_partition(self, run_path: str) -> bool:
        m = self._CONFIG_RE.search(run_path.replace('\\', '/'))
        return bool(m and int(m.group(1)) > 0)

    def classify_run(self, run_path: str) -> set[str]:
        with open(run_path, 'r') as f:
            text = f.read()

        if 'Violation of' not in text and 'Reached test duration' not in text:
            return set()

        violations = _parse_violations_from_log(text)
        mutations  = _parse_mutations_from_log(text)
        groups     = set()

        partition = self._config_has_partition(run_path)

        preprepare_ms   = [m for m in mutations if m.get('type') == 'PRE-PREPARE']
        vc_nv_mutated   = any(m.get('type') in ('VIEW-CHANGE', 'NEW-VIEW') for m in mutations)
        commit_mutated  = any(m.get('type') == 'COMMIT' for m in mutations)

        has_validity_or_agreement = any(v['type'] in ('VALIDITY', 'AGREEMENT') for v in violations)
        has_termination = 'Reached test duration' in text or any(v['type'] == 'TERMINATION' for v in violations)
        agreement_at_high_view = any(v['type'] == 'AGREEMENT' and v['view_no'] >= 2 for v in violations)

        # Group A — Invalid Operation: PRE-PREPARE operation mutation at the correct slot.
        # Require `operation` in the mutated payload in BOTH branches (was previously only
        # enforced in the violations+mutations branch); accept either a VALIDITY/AGREEMENT
        # violation OR a no-partition timeout as evidence the mutation caused the failure.
        for m in preprepare_ms:
            ts, seq = m.get('timestamp'), m.get('seq-number')
            if ts is None or seq is None:
                continue
            if ts == seq and 'operation' in m:
                if has_validity_or_agreement or (not partition and not violations):
                    groups.add('Invalid Operation')
            # Group B — Seq-No Replay: old request replayed at a higher slot.
            # Now detected in all branches, not only when a violation was observed.
            elif ts < seq:
                groups.add('Seq-No Replay')

        # Group C — View-Change Fault: VC/NV mutation that plausibly caused the failure.
        # Only attribute VCF when there is causal evidence (timeout or AGREEMENT at view>=1);
        # previously attributed whenever VC/NV was mutated, over-labeling partition-induced
        # failures that happened to contain a benign VC mutation.
        if vc_nv_mutated and (has_termination or any(v['type'] == 'AGREEMENT' and v['view_no'] >= 1 for v in violations)):
            groups.add('View-Change Fault')

        # Group E — Split Brain: AGREEMENT violation at view_no >= 2 (multi-view partition).
        # Threshold tightened from >=1 to >=2 to match root-cause doc; now reachable in the
        # violations+mutations branch as well (previously only when mutations were absent).
        if agreement_at_high_view:
            groups.add('Split Brain')

        # Commit Corruption: COMMIT mutation causing timeout without partition and without
        # any other explanatory mutation — covers the D0-C2 out191 edge case the root-cause
        # doc explicitly flagged as mis-classified as Partition Timeout.
        if commit_mutated and not partition and not violations and not vc_nv_mutated and not preprepare_ms:
            groups.add('Commit Corruption')

        # Group D — Partition Timeout: partition present, timeout outcome, no specific fault.
        # Preserved as a fallback so every failing run carries at least one label.
        if not groups:
            groups.add('Partition Timeout')

        return groups

    def get_bug_types(self) -> list[str]:
        return ['Invalid Operation', 'Seq-No Replay', 'View-Change Fault', 'Partition Timeout', 'Split Brain', 'Commit Corruption']

    def wrap_observations(self, pred: str, observed_nodes: set) -> dict[str, bool]:
        # PBFT: single threshold (observed by at least one replica)
        return {f'"{pred}" > 0': len(observed_nodes) > 0}

    def filter_aggregation(self, aggregation: dict) -> dict:
        return aggregation  # No post-processing needed for PBFT

    def get_data_dir(self) -> str:
        return 'out'

    def get_run_paths(self) -> list[str]:
        paths = []
        data_dir = self.get_data_dir()
        for config in sorted(os.listdir(data_dir)):
            config_dir = os.path.join(data_dir, config)
            if not os.path.isdir(config_dir):
                continue
            if not self._config_matches_scope(config):
                continue
            for f in sorted(os.listdir(config_dir)):
                if f.endswith('.txt') and '-predicates-cache-' not in f:
                    paths.append(os.path.join(config_dir, f))
        return paths

    def get_log_path(self, run_path: str, node_id: int) -> str:
        return run_path  # Each PBFT run is a single file

    def get_cache_path(self, run_path: str, node_id: int) -> str:
        stem = run_path[:-4]  # Strip .txt
        return f'{stem}-predicates-cache-{node_id}.txt'

    def iter_run_configs(self):
        for config in sorted(os.listdir(self.get_data_dir())):
            config_dir = os.path.join(self.get_data_dir(), config)
            if not os.path.isdir(config_dir):
                continue
            if not self._config_matches_scope(config):
                continue
            match = re.search(r'tests-D(\d)-C(\d)(?:-(.*))?$', config)
            if match is None:
                continue
            d, c = match.group(1), match.group(2)
            scope = match.group(3) or ''
            run_paths = sorted([
                os.path.join(config_dir, f)
                for f in os.listdir(config_dir)
                if f.endswith('.txt') and '-predicates-cache-' not in f
            ])
            label = f'd={d} c={c} {scope}'.rstrip()
            yield label, run_paths