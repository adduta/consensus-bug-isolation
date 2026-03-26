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

_TYPE_CLASSES = {
    'PRE-PREPARE': PrePrepare,
    'PREPARE':     Prepare,
    'COMMIT':      Commit,
    'VIEW-CHANGE': ViewChange,
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

    def get_fields(self) -> list[tuple[type, str, str]]:
        return [
            # PRE-PREPARE — Group A (operation mutation) and Group B (seq mutation)
            (PrePrepare, 'view_no',          'seq'),
            (PrePrepare, 'seq_no',           'seq'),
            (PrePrepare, 'operation_first',  'seq'),
            (PrePrepare, 'operation_second', 'seq'),
            (PrePrepare, 'timestamp',        'time'),
            # PREPARE / COMMIT — Group D (quorum) and Group E (cross-view)
            (Prepare,    'view_no',          'seq'),
            (Prepare,    'seq_no',           'seq'),
            (Prepare,    'replica_id',       'seq'),
            (Commit,     'view_no',          'seq'),
            (Commit,     'seq_no',           'seq'),
            (Commit,     'replica_id',       'seq'),
            # VIEW-CHANGE — Group C
            (ViewChange, 'new_view_no',      'seq'),
            (ViewChange, 'last_seq_no',      'seq'),
            (ViewChange, 'replica_id',       'seq'),
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

    def classify_run(self, run_path: str) -> set[str]:
        with open(run_path, 'r') as f:
            text = f.read()

        # Successful run: no violations and no timeout
        if 'Violation of' not in text and 'Reached test duration' not in text:
            return set()

        violations = _parse_violations_from_log(text)
        mutations  = _parse_mutations_from_log(text)
        groups     = set()

        if not violations:
            # Termination-only failure (timeout with no safety violation)
            vc_mutated = any(m.get('type') in ('VIEW-CHANGE', 'NEW-VIEW') for m in mutations)
            groups.add('View-Change Fault' if vc_mutated else 'Partition Timeout')
            return groups

        if not mutations:
            # Pure network fault with safety violations → Split Brain or Partition Timeout
            high_view = any(v['view_no'] >= 2 for v in violations)
            if high_view and any(v['type'] == 'AGREEMENT' for v in violations):
                groups.add('Split Brain')
            else:
                groups.add('Partition Timeout')
            return groups

        # Mutations + violations present
        # View-Change Fault (C): VIEW-CHANGE or NEW-VIEW was mutated
        vc_mutated = any(m.get('type') in ('VIEW-CHANGE', 'NEW-VIEW') for m in mutations)
        if vc_mutated:
            groups.add('View-Change Fault')

        for m in mutations:
            if m.get('type') != 'PRE-PREPARE':
                continue
            ts  = m.get('timestamp')
            seq = m.get('seq-number')
            if ts is None or seq is None:
                continue
            if ts < seq:
                # Seq-No Replay (B): old request replayed at a higher slot
                groups.add('Seq-No Replay')
            elif ts == seq and 'operation' in m:
                # Invalid Operation (A): operation field mutated at the correct slot
                if any(v['type'] in ('VALIDITY', 'AGREEMENT') for v in violations):
                    groups.add('Invalid Operation')

        if not groups:
            groups.add('Partition Timeout')  # Non-critical mutations + partition → timeout

        return groups

    def get_bug_types(self) -> list[str]:
        return ['Invalid Operation', 'Seq-No Replay', 'View-Change Fault', 'Partition Timeout', 'Split Brain']

    def wrap_observations(self, pred: str, observed_nodes: set) -> dict[str, bool]:
        # PBFT: single threshold (observed by at least one replica)
        return {f'"{pred}" > 0': len(observed_nodes) > 0}

    def filter_aggregation(self, aggregation: dict) -> dict:
        return aggregation  # No post-processing needed for PBFT

    def get_data_dir(self) -> str:
        return 'out'

    def get_run_paths(self) -> list[str]:
        paths = []
        for dirpath, _, filenames in os.walk(self.get_data_dir()):
            for f in sorted(filenames):
                if f.endswith('.txt') and not f.startswith('predicates-cache'):
                    paths.append(os.path.join(dirpath, f))
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
            match = re.search(r'tests-D(\d)-C(\d)(?:-(.*))?$', config)
            if match is None:
                continue
            d, c = match.group(1), match.group(2)
            scope = match.group(3) or ''
            run_paths = sorted([
                os.path.join(config_dir, f)
                for f in os.listdir(config_dir)
                if f.endswith('.txt') and not f.startswith('predicates-cache')
            ])
            label = f'd={d} c={c} {scope}'.rstrip()
            yield label, run_paths