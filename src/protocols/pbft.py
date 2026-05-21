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
            self.view_no == o.view_no and self.seq_no == o.seq_no
        )

    def __hash__(self):
        return hash((self.view_no, self.seq_no))

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
            self.view_no == o.view_no and self.seq_no == o.seq_no
        )

    def __hash__(self):
        return hash((self.view_no, self.seq_no))

    def __str__(self):
        return f'Commit(v={self.view_no}, s={self.seq_no}, r={self.replica_id})'

class Reply:
    __slots__ = ['view_no', 'seq_no', 'timestamp', 'result', 'replica_id', 'peers']

    def __init__(self, sender: int, msg: dict) -> None:
        self.view_no = msg.get('view-number', 0)
        self.seq_no = msg.get('seq-number', msg.get('timestamp', 0))
        self.timestamp = msg.get('timestamp', 0)
        self.result = msg.get('result', 0)
        self.replica_id = msg.get('replica-id', sender)
        self.peers = {sender}

    def __eq__(self, o):
        return isinstance(o, Reply) and (
            self.view_no == o.view_no and self.seq_no == o.seq_no and
            self.timestamp == o.timestamp and self.result == o.result
        )

    def __hash__(self):
        return hash((self.view_no, self.seq_no, self.timestamp, self.result))

    def __str__(self):
        return f'Reply(v={self.view_no}, s={self.seq_no}, r={self.replica_id}, result={self.result})'

def _extract_vc_proof_fields(prepared_proofs: list) -> dict:
    """Extract sets/counts derived from a VIEW-CHANGE's prepared-proofs list.

    Each proof entry has the form
        {'seq-number': int, 'messages': [PRE-PREPARE, PREPARE, ...]}.
    We collect raw values across all proofs and inner messages.
    """
    proof_seq_set = set()
    pp_view_set, pp_seq_set = set(), set()
    prep_view_set, prep_seq_set, prep_replica_set = set(), set(), set()
    prep_replica_total = 0
    for proof in prepared_proofs or []:
        if not isinstance(proof, dict):
            continue
        sn = proof.get('seq-number')
        if isinstance(sn, int):
            proof_seq_set.add(sn)
        for m in proof.get('messages', []) or []:
            if not isinstance(m, dict):
                continue
            t = m.get('type')
            v, s = m.get('view-number'), m.get('seq-number')
            if t == 'PRE-PREPARE':
                if isinstance(v, int): pp_view_set.add(v)
                if isinstance(s, int): pp_seq_set.add(s)
            elif t == 'PREPARE':
                if isinstance(v, int): prep_view_set.add(v)
                if isinstance(s, int): prep_seq_set.add(s)
                rid = m.get('replica-id')
                if isinstance(rid, int):
                    prep_replica_set.add(rid)
                    prep_replica_total += 1
    return {
        'proof_seq_set': proof_seq_set,
        'pp_view_set': pp_view_set,
        'pp_seq_set': pp_seq_set,
        'prep_view_set': prep_view_set,
        'prep_seq_set': prep_seq_set,
        'prep_replica_set': prep_replica_set,
        'prep_replica_total': prep_replica_total,
    }


class ViewChange:
    __slots__ = ['new_view_no', 'last_seq_no', 'replica_id', 'peers',
                 'proof_count',
                 'proof_seq_set', 'pp_view_set', 'pp_seq_set',
                 'prep_view_set', 'prep_seq_set', 'prep_replica_set',
                 'prep_replica_total', 'prep_replica_distinct']

    def __init__(self, sender: int, msg: dict) -> None:
        self.new_view_no = msg.get('new-view-number', 0)
        self.last_seq_no = msg.get('last-seq-number', 0)
        self.replica_id  = sender
        self.peers       = {sender}
        prepared_proofs  = msg.get('prepared-proofs', []) or []
        self.proof_count = len(prepared_proofs)
        f = _extract_vc_proof_fields(prepared_proofs)
        self.proof_seq_set       = f['proof_seq_set']
        self.pp_view_set         = f['pp_view_set']
        self.pp_seq_set          = f['pp_seq_set']
        self.prep_view_set       = f['prep_view_set']
        self.prep_seq_set        = f['prep_seq_set']
        self.prep_replica_set    = f['prep_replica_set']
        self.prep_replica_total  = f['prep_replica_total']
        self.prep_replica_distinct = len(f['prep_replica_set'])

    def __eq__(self, o):
        return isinstance(o, ViewChange) and (
            self.new_view_no == o.new_view_no and self.last_seq_no == o.last_seq_no
        )

    def __hash__(self):
        return hash((self.new_view_no, self.last_seq_no))

    def __str__(self):
        return f'ViewChange(new_v={self.new_view_no}, last_s={self.last_seq_no})'

# ---- Replica-level commit (parsed from LOG-Replica-Commit lines) ----

class ReplicaCommit:
    """Represents a committed operation as logged by a replica."""
    __slots__ = ['view_no', 'seq_no', 'replica_id',
                 'operation_first', 'operation_second', 'timestamp', 'peers']

    def __init__(self, replica_id: int, view_no: int, seq_no: int,
                 op_first: int, op_second: int, timestamp: int) -> None:
        self.view_no          = view_no
        self.seq_no           = seq_no
        self.replica_id       = replica_id
        self.operation_first  = op_first
        self.operation_second = op_second
        self.timestamp        = timestamp
        self.peers            = {replica_id}

    def __eq__(self, o):
        return isinstance(o, ReplicaCommit) and (
            self.view_no == o.view_no and self.seq_no == o.seq_no and
            self.operation_first == o.operation_first and
            self.operation_second == o.operation_second
        )

    def __hash__(self):
        return hash((self.view_no, self.seq_no,
                      self.operation_first, self.operation_second))

    def __str__(self):
        return (f'ReplicaCommit(v={self.view_no}, s={self.seq_no}, r={self.replica_id}, '
                f'op=({self.operation_first},{self.operation_second}))')

# ---- Parsing helpers ----

_SENT_RE    = re.compile(r'^Sent:\s+(\d+)\s+->\s+(\d+)\s+(\{.+\})\s+##(\d+)')
_SENT_REPLY_RE = re.compile(r'^Sent reply:\s+(\d+)\s+->\s+Client\s+(\{.+\})\s+##(\d+)')
_DROPPED_RE = re.compile(r'^\s+-\s+Dropped:\s+(\d+)\s+->\s+(\d+)\s*(\{.*\})?(?:\s+##(\d+))?')
_MUTATED_RE = re.compile(r'^\s+-\s+Mutated:\s+(\d+)\s+->\s+(\d+|client)\s*(\{.+\})(?:\s+#(\d+))?')
_VIOLATION_RE = re.compile(r'Violation of (\w+) at Replica:\s*(\d+).*viewNo:\s*(\d+).*seqNo:\s*(\d+)')
_REPLICA_COMMIT_RE = re.compile(
    r'^LOG-Replica-Commit:(\d+)\s+viewNo:\s*(\d+)\s+seqNo:\s*(\d+)\s+'
    r'request:.*operation=AddOp\{first=(-?\d+),\s*second=(-?\d+)\},\s*timestamp=(-?\d+)'
)

class NewView:
    __slots__ = ['new_view_no', 'num_vc_proofs', 'num_prepared_proofs', 'replica_id', 'peers',
                 'vc_replica_set', 'vc_replica_distinct',
                 'vc_inner_last_seq_set',
                 'pp_view_set', 'pp_seq_set',
                 'prep_view_set', 'prep_seq_set', 'prep_replica_set']

    def __init__(self, sender: int, msg: dict) -> None:
        self.new_view_no         = msg.get('new-view-number', 0)
        vc_proofs = msg.get('view-change-proofs', []) or []
        outer_pp_proofs = msg.get('prepared-proofs', []) or []
        self.num_vc_proofs       = len(vc_proofs)
        self.num_prepared_proofs = len(outer_pp_proofs)
        self.replica_id          = sender
        self.peers               = {sender}

        # Aggregate fields across the inner VIEW-CHANGEs
        vc_replica_set = set()
        vc_inner_last_seq_set = set()
        prep_view_set, prep_seq_set, prep_replica_set = set(), set(), set()
        inner_pp_view_set, inner_pp_seq_set = set(), set()
        for vc in vc_proofs:
            if not isinstance(vc, dict):
                continue
            rid = vc.get('replica-id')
            if isinstance(rid, int):
                vc_replica_set.add(rid)
            ls = vc.get('last-seq-number')
            if isinstance(ls, int):
                vc_inner_last_seq_set.add(ls)
            inner = _extract_vc_proof_fields(vc.get('prepared-proofs', []) or [])
            inner_pp_view_set.update(inner['pp_view_set'])
            inner_pp_seq_set.update(inner['pp_seq_set'])
            prep_view_set.update(inner['prep_view_set'])
            prep_seq_set.update(inner['prep_seq_set'])
            prep_replica_set.update(inner['prep_replica_set'])

        # Outer prepared-proofs is a flat list of PRE-PREPARE messages
        outer_pp_view_set, outer_pp_seq_set = set(), set()
        for m in outer_pp_proofs:
            if not isinstance(m, dict):
                continue
            v, s = m.get('view-number'), m.get('seq-number')
            if isinstance(v, int): outer_pp_view_set.add(v)
            if isinstance(s, int): outer_pp_seq_set.add(s)

        self.vc_replica_set        = vc_replica_set
        self.vc_replica_distinct   = len(vc_replica_set)
        self.vc_inner_last_seq_set = vc_inner_last_seq_set
        self.pp_view_set           = inner_pp_view_set | outer_pp_view_set
        self.pp_seq_set            = inner_pp_seq_set | outer_pp_seq_set
        self.prep_view_set         = prep_view_set
        self.prep_seq_set          = prep_seq_set
        self.prep_replica_set      = prep_replica_set

    def __eq__(self, o):
        return isinstance(o, NewView) and (
            self.new_view_no == o.new_view_no and
            self.num_vc_proofs == o.num_vc_proofs and
            self.num_prepared_proofs == o.num_prepared_proofs
        )

    def __hash__(self):
        return hash((self.new_view_no, self.num_vc_proofs, self.num_prepared_proofs))

    def __str__(self):
        return f'NewView(new_v={self.new_view_no}, vc={self.num_vc_proofs}, prep={self.num_prepared_proofs})'

_TYPE_CLASSES = {
    'PRE-PREPARE': PrePrepare,
    'PREPARE':     Prepare,
    'COMMIT':      Commit,
    'VIEW-CHANGE': ViewChange,
    'NEW-VIEW':    NewView,
    'REPLY':        Reply,
}

def _parse_inboxes_from_log(text: str) -> dict[int, list]:
    """Parse a PBFT log into per-replica inboxes.

    Returns a dict mapping replica_id -> list of messages that replica received.
    Dropped deliveries are excluded.  LOG-Replica-Commit entries are placed into
    the committing replica's inbox only.
    """
    # Collect line indices of Dropped and Mutated deliveries
    lines = text.splitlines()
    dropped_lines: set[int] = set()
    mutated_lines: dict[int, re.Match] = {}
    for i, line in enumerate(lines):
        if _DROPPED_RE.match(line):
            dropped_lines.add(i)
        mm = _MUTATED_RE.match(line)
        if mm:
            mutated_lines[i] = mm

    # Parse Sent lines and assign to receiver inboxes (skipping dropped deliveries)
    inboxes: dict[int, list] = {}
    for i, line in enumerate(lines):
        m = _SENT_RE.match(line)
        if m:
            sender_str, receiver_str, json_str, _round_str = m.groups()
            sender = int(sender_str)
            receiver = int(receiver_str)

            # Delivery artifacts may be separated from Sent by PRED lines.
            for j in range(i + 1, min(len(lines), i + 25)):
                if _SENT_RE.match(lines[j]) or _SENT_REPLY_RE.match(lines[j]):
                    break
                if j in dropped_lines:
                    dm = _DROPPED_RE.match(lines[j])
                    if dm and int(dm.group(1)) == sender and int(dm.group(2)) == receiver:
                        json_str = None
                        break
                if j in mutated_lines:
                    mm = mutated_lines[j]
                    if (int(mm.group(1)) == sender and mm.group(2).isdigit()
                            and int(mm.group(2)) == receiver):
                        json_str = mm.group(3)
                        break
            if json_str is None:
                continue

            try:
                msg = json.loads(json_str)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get('type', '')
            cls = _TYPE_CLASSES.get(msg_type)
            if not cls:
                continue

            inboxes.setdefault(receiver, []).append(cls(sender, msg))
            continue

        # LOG-Replica-Commit goes into the committing replica's inbox
        m = _REPLICA_COMMIT_RE.match(line)
        if m:
            replica_id = int(m.group(1))
            view_no, seq_no = int(m.group(2)), int(m.group(3))
            op_first, op_second, timestamp = int(m.group(4)), int(m.group(5)), int(m.group(6))
            inboxes.setdefault(replica_id, []).append(
                ReplicaCommit(replica_id, view_no, seq_no, op_first, op_second, timestamp)
            )
            continue

        # Client replies are global client-observed messages. Store them in a
        # synthetic observer inbox so reply quorum events can be synthesized.
        m = _SENT_REPLY_RE.match(line)
        if m:
            sender = int(m.group(1))
            try:
                msg = json.loads(m.group(2))
            except json.JSONDecodeError:
                continue
            inboxes.setdefault(0, []).append(Reply(sender, msg))

    return inboxes

def _parse_mutations_from_log(text: str) -> list[dict]:
    """Extract all mutated messages from a PBFT execution log.

    The returned dict is the post-mutation message with parser metadata under
    ``_sender``, ``_receiver``, ``_round``, ``_line_no``, and, when available,
    ``_original`` (the immediately preceding Sent message).
    """

    mutations = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = _MUTATED_RE.match(line)
        if not m:
            continue
        # The mutated JSON may be incomplete in the log; try best-effort parse
        try:
            msg = json.loads(m.group(3))
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {m.group(3)}")
            continue
        msg = dict(msg)
        receiver = m.group(2)
        msg['_sender'] = int(m.group(1))
        msg['_receiver'] = int(receiver) if receiver.isdigit() else receiver
        msg['_round'] = int(m.group(4)) if m.group(4) is not None else None
        msg['_line_no'] = i
        for prev in range(i - 1, max(-1, i - 25), -1):
            sent = _SENT_RE.match(lines[prev])
            if not sent:
                continue
            if sent.group(1) != m.group(1) or sent.group(2) != receiver:
                continue
            try:
                msg['_original'] = json.loads(sent.group(3))
            except json.JSONDecodeError:
                pass
            break
        mutations.append(msg)
    return mutations

def _parse_drops_from_log(text: str) -> list[dict]:
    """Extract dropped deliveries, including message type and line/round data."""
    drops = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = _DROPPED_RE.match(line)
        if not m:
            continue
        msg_type = None
        round_no = int(m.group(4)) if m.group(4) is not None else None
        if m.group(3):
            try:
                msg_type = json.loads(m.group(3)).get('type')
            except json.JSONDecodeError:
                pass
        if msg_type is None and i > 0:
            sent = _SENT_RE.match(lines[i - 1])
            if sent and sent.group(1) == m.group(1) and sent.group(2) == m.group(2):
                try:
                    msg_type = json.loads(sent.group(3)).get('type')
                    round_no = int(sent.group(4))
                except json.JSONDecodeError:
                    pass
        view_no = seq_no = None
        if m.group(3):
            try:
                drop_msg = json.loads(m.group(3))
                view_no = drop_msg.get('view-number')
                seq_no = drop_msg.get('seq-number')
            except json.JSONDecodeError:
                pass
        drops.append({
            'sender': int(m.group(1)),
            'receiver': int(m.group(2)),
            'type': msg_type,
            'round': round_no,
            'view_no': view_no,
            'seq_no': seq_no,
            'line_no': i,
        })
    return drops

def _parse_replica_commits_from_log(text: str) -> list[dict]:
    """Extract application-level commits from LOG-Replica-Commit lines."""
    commits = []
    for i, line in enumerate(text.splitlines()):
        m = _REPLICA_COMMIT_RE.match(line)
        if not m:
            continue
        commits.append({
            'replica': int(m.group(1)),
            'view_no': int(m.group(2)),
            'seq_no': int(m.group(3)),
            'operation': (int(m.group(4)), int(m.group(5))),
            'timestamp': int(m.group(6)),
            'line_no': i,
        })
    return commits

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

def _operation_tuple(msg: dict) -> tuple[int, int] | None:
    op = msg.get('operation')
    if not isinstance(op, dict):
        return None
    first, second = op.get('first'), op.get('second')
    if isinstance(first, int) and isinstance(second, int):
        return (first, second)
    return None

def _commit_split_brain(commits: list[dict]) -> bool:
    """Return True if a high-view commit conflicts with same-seq commits."""
    by_seq: dict[int, dict[tuple[int, int], set[tuple[int, int]]]] = {}
    for commit in commits:
        by_seq.setdefault(commit['seq_no'], {}).setdefault(
            commit['operation'], set()
        ).add((commit['replica'], commit['view_no']))
    for op_to_commits in by_seq.values():
        has_high_view_commit = any(
            view_no >= 2
            for commits_for_op in op_to_commits.values()
            for _replica, view_no in commits_for_op
        )
        if len(op_to_commits) < 2:
            continue
        if has_high_view_commit and sum(len(c) for c in op_to_commits.values()) >= 2:
            return True
    return False

def _preprepare_mutation_committed(mutation: dict, commits: list[dict]) -> bool:
    """Return True when a PRE-PREPARE mutation is reflected in a commit."""
    if mutation.get('type') != 'PRE-PREPARE':
        return False

    original = mutation.get('_original')
    if not isinstance(original, dict) or original.get('type') != 'PRE-PREPARE':
        return False

    mutated_op = _operation_tuple(mutation)
    original_op = _operation_tuple(original)
    mutated_seq = mutation.get('seq-number')
    original_seq = original.get('seq-number')
    mutated_ts = mutation.get('timestamp')
    original_ts = original.get('timestamp')

    if mutated_op is None or not isinstance(mutated_seq, int):
        return False

    changed = (
        mutated_op != original_op or
        mutated_seq != original_seq or
        mutated_ts != original_ts
    )
    if not changed:
        return False

    for commit in commits:
        if commit['seq_no'] != mutated_seq:
            continue
        if commit['operation'] != mutated_op:
            continue
        if mutated_ts is None or commit['timestamp'] == mutated_ts:
            return True
    return False

def _partition_precedes_mutation(drops: list[dict], mutations: list[dict]) -> bool:
    """Whether consensus-message drops already appear before any mutation."""
    first_mutation_line = min((m.get('_line_no', 10**12) for m in mutations),
                              default=10**12)
    consensus_types = {'PRE-PREPARE', 'PREPARE', 'COMMIT'}
    return any(
        drop.get('line_no', 10**12) < first_mutation_line and
        drop.get('type') in consensus_types
        for drop in drops
    )

# ---- Protocol class ----

class PBFTProtocol(ConsensusProtocol):
    """PBFT consensus protocol adapter (ByzzFuzz test format)."""

    NUM_REPLICAS = 4

    def __init__(self, scope: str | None = None, data_dir: str | None = None,
                 filter_vc: bool = False):
        # scope: None = all configs, 'ss' = only -ss configs, 'as' = only -as configs
        self.scope = scope
        self._data_dir = data_dir
        self._filter_vc = filter_vc
        self._cached_path: str | None = None
        self._cached_inboxes: dict[int, list] | None = None

    def _config_matches_scope(self, config: str) -> bool:
        if self.scope is None:
            return True
        if self.scope == 'ss':
            return config.endswith('-ss')
        if self.scope == 'as':
            return config.endswith('-as')
        return True

    def get_excluded_type_pairs(self) -> set[tuple[type, type]]:
        """Type pairs to exclude from predicate generation.

        Excluded:
        - ReplicaCommit→ReplicaCommit: self-comparisons add noise
        """
        return {(ReplicaCommit, ReplicaCommit)}

    def get_fields(self) -> list[tuple[type, str, str]]:
        return [
            (PrePrepare, 'view_no',             'view_current'),
            (PrePrepare, 'seq_no',              'seqno'),
            (PrePrepare, 'operation_first',     'op_first'),
            (PrePrepare, 'operation_second',    'op_second'),
            (PrePrepare, 'timestamp',           'time'),
            (PrePrepare, 'peers',               set[int]),
            (Prepare,    'view_no',             'view_current'),
            (Prepare,    'seq_no',              'seqno'),
            (Prepare,    'peers',               set[int]),
            (Commit,     'view_no',             'view_current'),
            (Commit,     'seq_no',              'seqno'),
            (Commit,     'peers',               set[int]),
            (Reply,      'view_no',             'view_current'),
            (Reply,      'seq_no',              'seqno'),
            (Reply,      'timestamp',           'time'),
            (Reply,      'result',              'op'),
            (Reply,      'peers',               set[int]),
            (ViewChange, 'new_view_no',           'view_next'),
            (ViewChange, 'last_seq_no',           'seqno'),
            (ViewChange, 'peers',                 set[int]),
            (ViewChange, 'proof_count',           'proof_count'),
            (ViewChange, 'pp_seq_set',            'pp_seq_set'),
            (ViewChange, 'prep_replica_set',      'prep_replica_set'),
            (NewView,    'new_view_no',           'view_next'),
            (NewView,    'num_vc_proofs',         'vc_proof_count'),
            (NewView,    'num_prepared_proofs',   'prep_proof_count'),
            (NewView,    'peers',                 set[int]),
            (NewView,    'vc_replica_set',        'vc_replica_set'),
            (NewView,    'vc_inner_last_seq_set', 'vc_inner_last_seq_set'),
            (NewView,    'pp_seq_set',            'pp_seq_set'),
            (NewView,    'prep_replica_set',      'prep_replica_set'),
            (ReplicaCommit, 'view_no',          'view_current'),
            (ReplicaCommit, 'seq_no',           'seqno'),
            (ReplicaCommit, 'operation_first',  'op_first'),
            (ReplicaCommit, 'operation_second', 'op_second'),
            (ReplicaCommit, 'timestamp',        'time'),
            (ReplicaCommit, 'peers',            set[int]),
        ]

    def _ensure_inboxes(self, path: str) -> None:
        """Parse and cache per-replica inboxes for the given log file."""
        if self._cached_path != path:
            with open(path, 'r') as f:
                text = f.read()
            self._cached_inboxes = _parse_inboxes_from_log(text)
            self._cached_path = path

    def parse_log(self, path: str) -> list:
        self._ensure_inboxes(path)
        # Flat list for backward compat (used by classify_run helpers)
        all_msgs = []
        for msgs in self._cached_inboxes.values():
            all_msgs.extend(msgs)
        return all_msgs

    def get_num_nodes(self) -> int:
        return self.NUM_REPLICAS

    def filter_messages(self, messages: list, node_id: int) -> list:
        """Return the inbox for a specific replica."""
        if self._cached_inboxes is None:
            return messages
        return self._cached_inboxes.get(node_id, [])

    def is_successful(self, run_path: str) -> bool:
        with open(run_path, 'r') as f:
            text = f.read()
        if 'Violation of' in text:
            return False
        # A run that reached the test duration but then completed successfully
        # (after delivering pending messages) is NOT a failure.
        if 'Timer for Request Timeout' in text:
            return False
        if 'Reached test duration' in text and 'Task completed' not in text:
            return False
        return True

    _CONFIG_RE = re.compile(r'tests-D(\d+)-C(\d+)')

    def _config_has_partition(self, run_path: str) -> bool:
        m = self._CONFIG_RE.search(run_path.replace('\\', '/'))
        return bool(m and int(m.group(1)) > 0)

    def classify_run(self, run_path: str) -> set[str]:
        with open(run_path, 'r') as f:
            text = f.read()

        has_violation = 'Violation of' in text
        has_timer_timeout = 'Timer for Request Timeout' in text
        has_reached_no_complete = ('Reached test duration' in text
                                  and 'Task completed' not in text)
        is_failing = has_violation or has_timer_timeout or has_reached_no_complete

        if not is_failing:
            return set()

        violations = _parse_violations_from_log(text)
        mutations  = _parse_mutations_from_log(text)
        drops      = _parse_drops_from_log(text)
        commits    = _parse_replica_commits_from_log(text)
        groups     = set()

        preprepare_ms = [m for m in mutations if m.get('type') == 'PRE-PREPARE']
        vc_nv_mutated = any(m.get('type') in ('VIEW-CHANGE', 'NEW-VIEW') for m in mutations)
        non_pp_mutated = any(m.get('type') in ('PREPARE', 'COMMIT', 'REPLY') for m in mutations)
        partition_dominated = (
            self._config_has_partition(run_path) and
            _partition_precedes_mutation(drops, mutations)
        )

        has_termination = has_timer_timeout or has_reached_no_complete
        agreement_at_high_view = any(v['type'] == 'AGREEMENT' and v['view_no'] >= 2 for v in violations)

        # Operation Corruption: a landed PRE-PREPARE mutation affected the
        # application-level commit stream.  This intentionally ignores
        # PRE-PREPARE mutations that are visible but never committed, allowing
        # partition-only stalls to remain Partition Timeout.
        if any(_preprepare_mutation_committed(m, commits) for m in preprepare_ms):
            groups.add('Operation Corruption')

        # View-Change Fault: VC/NV mutation with causal evidence
        # (timeout or AGREEMENT at view>=1).
        if vc_nv_mutated and (has_termination or any(v['type'] == 'AGREEMENT' and v['view_no'] >= 1 for v in violations)):
            groups.add('View-Change Fault')

        # Split Brain: direct commit-log disagreement, with the historical
        # high-view AGREEMENT violation retained as supporting evidence.
        if _commit_split_brain(commits) or agreement_at_high_view:
            groups.add('Split Brain')

        # Liveness-stall fallback, split by observable mutation footprint:
        #   - Non-PP Mutation: a PREPARE/COMMIT/REPLY mutation is visible in
        #     the log (Group F in the root-cause taxonomy). The mutation event
        #     itself is wire-observable even though digest equality predicates
        #     cannot fire on empty digests.
        #   - Partition Timeout: pure network-partition stall with no Byzantine
        #     mutation visible (Group D). The classifier reaches here only when
        #     OC, VCF, SB did not fire.
        if not groups:
            if non_pp_mutated and not partition_dominated:
                groups.add('Non-PP Mutation')
            else:
                groups.add('Partition Timeout')

        return groups

    def get_bug_types(self) -> list[str]:
        return ['Operation Corruption', 'View-Change Fault',
                'Partition Timeout', 'Non-PP Mutation', 'Split Brain']

    def wrap_observations(self, pred: str, observed_nodes: set) -> dict[str, bool]:
        # Tolerance dimension: predicate true for the run if observed by > i replicas
        n = len(observed_nodes)
        return {f'"{pred}" > {i}': n > i for i in range(self.NUM_REPLICAS)}

    def filter_aggregation(self, aggregation: dict) -> dict:
        if not self._filter_vc:
            return aggregation
        # Drop predicates involving ViewChange or NewView to suppress
        # the dominant view-change signal and surface consensus predicates.
        return {k: v for k, v in aggregation.items()
                if 'ViewChange' not in k and 'NewView' not in k}

    def get_data_dir(self) -> str:
        return self._data_dir or 'out'

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
        return f'{stem}-predicates-cache-{node_id}.txt.gz'

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

    # ---- Baseline (PRED-annotation) methods ----

    def parse_baseline_observations(self, run_path: str) -> tuple[bool, dict[str, bool], str] | None:
        with open(run_path, 'r') as f:
            text = f.read()

        has_violation = 'Violation of' in text
        has_timer_timeout = 'Timer for Request Timeout' in text
        has_reached_no_complete = ('Reached test duration' in text
                                  and 'Task completed' not in text)
        correct = not has_violation and not has_timer_timeout and not has_reached_no_complete

        observations: dict[str, bool] = {}

        for line in text.splitlines():
            if not line.startswith('PRED '):
                continue

            parts = line.strip().split()
            if len(parts) < 5:
                continue

            pred_id = parts[1] + ' ' + parts[2]

            # Skip test-harness predicates (PropertyChecker is the violation
            # oracle, not consensus logic — including it would be circular).
            if 'PropertyChecker' in pred_id:
                continue

            observation = parts[4] == '1'

            key_true = pred_id + ' is true'
            key_false = pred_id + ' is false'

            if key_true not in observations:
                observations[key_true] = observation
                observations[key_false] = not observation
            else:
                observations[key_true] = observation or observations[key_true]
                observations[key_false] = (not observation) or observations[key_false]

        run_name = run_path.replace("\\", "/")
        return (correct, observations, run_name)

    def get_baseline_data_dir(self) -> str:
        """Data directory containing PBFT logs with PRED annotations."""
        return 'out copy'

    def get_baseline_run_paths(self) -> list[str]:
        """Run paths from the 'out copy' directory containing PRED-instrumented logs."""
        data_dir = self.get_baseline_data_dir()
        paths = []
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

    def iter_baseline_run_configs(self):
        """Yield (config_label, run_paths) pairs from the baseline data directory."""
        data_dir = self.get_baseline_data_dir()
        for config in sorted(os.listdir(data_dir)):
            config_dir = os.path.join(data_dir, config)
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
