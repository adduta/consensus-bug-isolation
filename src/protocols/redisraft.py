"""RedisRaft protocol adapter for the ModelFuzz dataset.

See `redisraft/protocol.md` for vocabulary, storage layout, and bug taxonomy.
"""

import json
import os
import re

from .base import ConsensusProtocol


# ---- Message types ----
#
# All message classes follow the project convention used by PBFT/XRPL:
#   - identifying fields drive __eq__ / __hash__ (so the same logical
#     SendMessage + DeliverMessage compare equal and dedup in cache.py)
#   - `peers` is initialized to the directly involved node set and is
#     merged across duplicates by the cache loop
#
# ModelFuzz / RedisRaft traces use Raft node IDs 1..3. The shared pipeline
# iterates node IDs as range(get_num_nodes()), so normalize node IDs to 0..2
# at the adapter boundary.


def _node_id(value) -> int:
    if isinstance(value, int) and value > 0:
        return value - 1
    return 0


class AppendEntries:
    __slots__ = ['from_', 'to', 'term', 'index', 'log_term',
                 'commit', 'entries_count', 'peers']

    def __init__(self, params: dict) -> None:
        self.from_         = _node_id(params.get('from', 0))
        self.to            = _node_id(params.get('to', 0))
        self.term          = params.get('term', 0)
        self.index         = params.get('index', 0)
        self.log_term      = params.get('log_term', 0)
        self.commit        = params.get('commit', 0)
        self.entries_count = len(params.get('entries') or [])
        self.peers         = {self.from_, self.to}

    def __eq__(self, o):
        return isinstance(o, AppendEntries) and (
            self.from_ == o.from_ and self.to == o.to and
            self.term == o.term and self.index == o.index and
            self.log_term == o.log_term and self.commit == o.commit and
            self.entries_count == o.entries_count
        )

    def __hash__(self):
        return hash((self.from_, self.to, self.term, self.index,
                     self.log_term, self.commit, self.entries_count))

    def __str__(self):
        return (f'AE({self.from_}->{self.to}, t={self.term}, i={self.index}, '
                f'lt={self.log_term}, c={self.commit}, n={self.entries_count})')


class AppendEntriesResp:
    __slots__ = ['from_', 'to', 'term', 'index', 'reject', 'peers']

    def __init__(self, params: dict) -> None:
        self.from_  = _node_id(params.get('from', 0))
        self.to     = _node_id(params.get('to', 0))
        self.term   = params.get('term', 0)
        self.index  = params.get('index', 0)
        self.reject = bool(params.get('reject', False))
        self.peers  = {self.from_, self.to}

    def __eq__(self, o):
        return isinstance(o, AppendEntriesResp) and (
            self.from_ == o.from_ and self.to == o.to and
            self.term == o.term and self.index == o.index and
            self.reject == o.reject
        )

    def __hash__(self):
        return hash((self.from_, self.to, self.term, self.index, self.reject))

    def __str__(self):
        return (f'AEResp({self.from_}->{self.to}, t={self.term}, '
                f'i={self.index}, rej={self.reject})')


class RequestVote:
    __slots__ = ['from_', 'to', 'term', 'index', 'log_term', 'peers']

    def __init__(self, params: dict) -> None:
        self.from_    = _node_id(params.get('from', 0))
        self.to       = _node_id(params.get('to', 0))
        self.term     = params.get('term', 0)
        self.index    = params.get('index', 0)
        self.log_term = params.get('log_term', 0)
        self.peers    = {self.from_, self.to}

    def __eq__(self, o):
        return isinstance(o, RequestVote) and (
            self.from_ == o.from_ and self.to == o.to and
            self.term == o.term and self.index == o.index and
            self.log_term == o.log_term
        )

    def __hash__(self):
        return hash((self.from_, self.to, self.term, self.index, self.log_term))

    def __str__(self):
        return (f'RV({self.from_}->{self.to}, t={self.term}, '
                f'i={self.index}, lt={self.log_term})')


class RequestVoteResp:
    __slots__ = ['from_', 'to', 'term', 'reject', 'peers']

    def __init__(self, params: dict) -> None:
        self.from_  = _node_id(params.get('from', 0))
        self.to     = _node_id(params.get('to', 0))
        self.term   = params.get('term', 0)
        self.reject = bool(params.get('reject', False))
        self.peers  = {self.from_, self.to}

    def __eq__(self, o):
        return isinstance(o, RequestVoteResp) and (
            self.from_ == o.from_ and self.to == o.to and
            self.term == o.term and self.reject == o.reject
        )

    def __hash__(self):
        return hash((self.from_, self.to, self.term, self.reject))

    def __str__(self):
        return (f'RVResp({self.from_}->{self.to}, t={self.term}, '
                f'rej={self.reject})')


class BecomeLeader:
    __slots__ = ['node', 'term', 'peers']

    def __init__(self, params: dict) -> None:
        self.node  = _node_id(params.get('node', 0))
        self.term  = params.get('term', 0)
        self.peers = {self.node}

    def __eq__(self, o):
        return isinstance(o, BecomeLeader) and (
            self.node == o.node and self.term == o.term
        )

    def __hash__(self):
        return hash((self.node, self.term))

    def __str__(self):
        return f'BecomeLeader(n={self.node}, t={self.term})'


class Timeout:
    __slots__ = ['node', 'peers']

    def __init__(self, params: dict) -> None:
        self.node  = _node_id(params.get('node', 0))
        self.peers = {self.node}

    def __eq__(self, o):
        return isinstance(o, Timeout) and self.node == o.node

    def __hash__(self):
        return hash(('Timeout', self.node))

    def __str__(self):
        return f'Timeout(n={self.node})'


class ClientRequest:
    __slots__ = ['leader', 'request', 'peers']

    def __init__(self, params: dict) -> None:
        self.leader  = _node_id(params.get('leader', 0))
        self.request = params.get('request', 0)
        self.peers   = {self.leader}

    def __eq__(self, o):
        return isinstance(o, ClientRequest) and (
            self.leader == o.leader and self.request == o.request
        )

    def __hash__(self):
        return hash((self.leader, self.request))

    def __str__(self):
        return f'ClientRequest(leader={self.leader}, req={self.request})'


class MembershipChange:
    __slots__ = ['action', 'node', 'peers']

    def __init__(self, params: dict) -> None:
        self.action = params.get('action', '')
        self.node   = _node_id(params.get('node', 0))
        self.peers  = {self.node}

    def __eq__(self, o):
        return isinstance(o, MembershipChange) and (
            self.action == o.action and self.node == o.node
        )

    def __hash__(self):
        return hash((self.action, self.node))

    def __str__(self):
        return f'MembershipChange({self.action}, n={self.node})'


# ---- Event-trace parsing ----

_MSG_CLASSES = {
    'MsgApp':     AppendEntries,
    'MsgAppResp': AppendEntriesResp,
    'MsgVote':    RequestVote,
    'MsgVoteResp': RequestVoteResp,
}


def _parse_events(events: list) -> list:
    """Translate event_trace.Events entries into message objects.

    SendMessage and DeliverMessage carry the underlying Raft message in
    Params; both produce a message object that compares equal to its
    counterpart, so cache.py's dedup merges their peers.
    """
    messages = []
    for ev in events or []:
        name = ev.get('Name', '')
        params = ev.get('Params') or {}

        if name in ('SendMessage', 'DeliverMessage'):
            cls = _MSG_CLASSES.get(params.get('type'))
            if cls is not None:
                messages.append(cls(params))
        elif name == 'BecomeLeader':
            messages.append(BecomeLeader(params))
        elif name == 'Timeout':
            messages.append(Timeout(params))
        elif name == 'ClientRequest':
            messages.append(ClientRequest(params))
        elif name == 'MembershipChange':
            messages.append(MembershipChange(params))
        # 'Add' / 'Remove' (sub-records of MembershipChange) and the trailing
        # {Reset: true} boundary event are intentionally ignored.

    return messages


# ---- TLA+ Repr parsing ----
#
# state_trace[k].Repr is a TLA+ record string like
#   "matchIndex = [[0,5,4], [0,0,0], [0,0,0]], log = [...], state = [...],
#    commitIndex = [3, 0, 0], currentTerm = [1, 0, 0], ..."
#
# We only need the currentTerm array for the term oracle in v1.
# Mirrors `redisraft-fuzzing/guider.go:parseTLCStateTrace`.

_CURRENT_TERM_RE = re.compile(r'currentTerm\s*=\s*\[([^\]]+)\]')


def _parse_current_term(repr_str: str) -> list[int] | None:
    """Extract the currentTerm per-node array from a TLA+ Repr string.

    Returns None if the field cannot be parsed (e.g. truncated Repr).
    """
    m = _CURRENT_TERM_RE.search(repr_str or '')
    if not m:
        return None
    parts = [p.strip() for p in m.group(1).split(',')]
    try:
        return [int(p) for p in parts if p != '']
    except ValueError:
        return None


# ---- Term-update oracle (silent bugs 11 / 12 / 13) ----

_TERM_BUG_BY_MSG_TYPE = {
    'MsgApp':      'Bug 11',
    'MsgVote':     'Bug 12',
    'MsgVoteResp': 'Bug 13',
}


def _term_oracle(events: list, state_trace: list, choices: list) -> set[str]:
    """Detect silent term-update misses (paper bugs 11, 12, 13).

    v1 rule (see redisraft/protocol.md §7.2):
      - Skip iterations that contain any Crash choice (a crash-restart can
        legitimately reset currentTerm and confuse a naive check).
      - For each delivered MsgApp / MsgVote / MsgVoteResp, if its term is
        greater than the final-state currentTerm of the recipient, flag the
        corresponding bug.
    """
    # Crash-restart guard
    if any(c.get('Type') == 'Crash' for c in (choices or [])):
        return set()

    if not state_trace:
        return set()

    final_terms = _parse_current_term(state_trace[-1].get('Repr', ''))
    if not final_terms:
        return set()

    labels: set[str] = set()
    for ev in events or []:
        if ev.get('Name') != 'DeliverMessage':
            continue
        params = ev.get('Params') or {}
        bug = _TERM_BUG_BY_MSG_TYPE.get(params.get('type'))
        if bug is None:
            continue
        to = params.get('to', 0)
        # Nodes are 1-indexed in event params; currentTerm is 0-indexed.
        idx = to - 1
        if idx < 0 or idx >= len(final_terms):
            continue
        if params.get('term', 0) > final_terms[idx]:
            labels.add(bug)

    return labels


# ---- Crash classifier ----
#
# Reads the per-iter `log` file as bytes (Redis crash dumps contain raw
# memory regions that break UTF-8 decoding). Maps assertion text + the top
# `redisraft.so(SYM+0x…)` stack frame to a paper bug ID.

_ASSERT_RE     = re.compile(rb"Assertion `([^']+)' failed")
_RAFT_FRAME_RE = re.compile(rb"redisraft\.so\(([A-Za-z0-9_]+)\+0x")

_ASSERT_TO_BUG = {
    b'0 < raft_get_current_idx(me)': 'Bug 3',
}

_FRAME_TO_BUG = {
    b'callRaftPeriodic':                'Bug 3',
    b'raft_restore_log':                'Bug 3',
    b'raft_node_set_addition_committed': 'Bug 5',
    b'raft_handle_apply_cfg_change':     'Bug 5',
    b'raft_get_entry_from_idx':          'Bug 8',
    b'ConnIsConnected':                  'Bug 4',
    b'handleBeforeSleep':                'Bug 6',
    b'redis_test_map_exists_index':      'Bug 6',
    # Bug 9 (state→follower on leader msg) and Bug 10 (state→follower on
    # higher-term msg) are not reliably distinguishable from the stack
    # frames alone; both surface around state-transition code paths and
    # Bug 9 is much more frequent per Table 7 (5/21 vs 1/21).
    b'raft_become_precandidate':         'Bug 9',
}


def _classify_crash(log_bytes: bytes) -> str:
    """Return the paper bug ID for a `redis_bug: true` iteration's log."""
    m = _ASSERT_RE.search(log_bytes)
    if m:
        bug = _ASSERT_TO_BUG.get(m.group(1))
        if bug is not None:
            return bug

    m = _RAFT_FRAME_RE.search(log_bytes)
    if m:
        bug = _FRAME_TO_BUG.get(m.group(1))
        if bug is not None:
            return bug

    return 'Unknown'


# ---- Protocol class ----


class RedisRaftProtocol(ConsensusProtocol):
    """RedisRaft consensus protocol adapter (ModelFuzz dataset).

    Each `run_path` is an iter_<NNN> directory containing `status.json`,
    `trace.json`, and `log` (see scripts/extract_redisraft.py).
    """

    NUM_NODES = 3
    CACHE_VERSION = 'nodeids1-fieldsplit'

    BUG_TYPES = [
        'Bug 1', 'Bug 2', 'Bug 3', 'Bug 4', 'Bug 5', 'Bug 6',
        'Bug 8', 'Bug 9', 'Bug 10',
        'Bug 11', 'Bug 12', 'Bug 13',
        'Unknown',
    ]

    def __init__(self, data_dir: str | None = None):
        self.scope = self.CACHE_VERSION
        self._data_dir = data_dir
        self._cached_path: str | None = None
        self._cached_messages: list | None = None
        self._cached_status: dict | None = None
        self._cached_trace: dict | None = None

    # ---- Contract methods ----

    def get_num_nodes(self) -> int:
        return self.NUM_NODES

    def get_fields(self) -> list[tuple[type, str, str]]:
        return [
            (AppendEntries,     'from_',          'rid'),
            (AppendEntries,     'to',             'rid'),
            (AppendEntries,     'term',           'term'),
            (AppendEntries,     'index',          'log_index'),
            (AppendEntries,     'log_term',       'log_term'),
            (AppendEntries,     'commit',         'log_index'),
            (AppendEntries,     'entries_count',  'count'),
            (AppendEntries,     'peers',          set[int]),

            (AppendEntriesResp, 'from_',          'rid'),
            (AppendEntriesResp, 'to',             'rid'),
            (AppendEntriesResp, 'term',           'term'),
            (AppendEntriesResp, 'index',          'log_index'),
            (AppendEntriesResp, 'reject',         'reject'),
            (AppendEntriesResp, 'peers',          set[int]),

            (RequestVote,       'from_',          'rid'),
            (RequestVote,       'to',             'rid'),
            (RequestVote,       'term',           'term'),
            (RequestVote,       'index',          'log_index'),
            (RequestVote,       'log_term',       'log_term'),
            (RequestVote,       'peers',          set[int]),

            (RequestVoteResp,   'from_',          'rid'),
            (RequestVoteResp,   'to',             'rid'),
            (RequestVoteResp,   'term',           'term'),
            (RequestVoteResp,   'reject',         'reject'),
            (RequestVoteResp,   'peers',          set[int]),

            (BecomeLeader,      'node',           'rid'),
            (BecomeLeader,      'term',           'term'),
            (BecomeLeader,      'peers',          set[int]),

            (Timeout,           'node',           'rid'),
            (Timeout,           'peers',          set[int]),

            (ClientRequest,     'leader',         'rid'),
            (ClientRequest,     'request',        'op'),
            (ClientRequest,     'peers',          set[int]),

            (MembershipChange,  'action',         'action'),
            (MembershipChange,  'node',           'rid'),
            (MembershipChange,  'peers',          set[int]),
        ]

    def parse_log(self, path: str) -> list:
        """Parse an iter_<NNN> directory into a flat message list.

        Caches the parsed status / trace alongside the message list so
        is_successful / classify_run on the same path avoid re-reading.
        """
        run_path = self._iter_dir(path)
        if self._cached_path != run_path:
            self._load(run_path)
        return list(self._cached_messages or [])

    def filter_messages(self, messages: list, node_id: int) -> list:
        return [m for m in messages if node_id in m.peers]

    def is_successful(self, run_path: str) -> bool:
        return not self.classify_run(run_path)

    def classify_run(self, run_path: str) -> set[str]:
        run_path = self._iter_dir(run_path)
        if self._cached_path != run_path:
            self._load(run_path)
        status = self._cached_status or {}
        labels: set[str] = set()

        if status.get('redis_bug'):
            log_path = os.path.join(run_path, 'log')
            try:
                with open(log_path, 'rb') as f:
                    log_bytes = f.read()
            except FileNotFoundError:
                log_bytes = b''
            labels.add(_classify_crash(log_bytes))
        else:
            trace = self._cached_trace or {}
            events = (trace.get('event_trace') or {}).get('Events') or []
            state_trace = trace.get('state_trace') or []
            choices = status.get('choices') or []
            labels |= _term_oracle(events, state_trace, choices)

        return labels

    def get_bug_types(self) -> list[str]:
        return list(self.BUG_TYPES)

    def wrap_observations(self, pred: str, observed_nodes: set) -> dict[str, bool]:
        n = len(observed_nodes)
        return {f'"{pred}" > {i}': n > i for i in range(self.NUM_NODES)}

    def parse_baseline_observations(
        self, run_path: str
    ) -> tuple[bool, dict[str, bool], str] | None:
        # ModelFuzz traces carry no PRED annotations.
        return None

    # ---- Run discovery / path helpers ----

    def get_data_dir(self) -> str:
        return self._data_dir or 'data/redisraft'

    def get_run_paths(self) -> list[str]:
        paths = []
        root = self.get_data_dir()
        if not os.path.isdir(root):
            return paths
        for run_name in sorted(os.listdir(root)):
            run_dir = os.path.join(root, run_name)
            if not os.path.isdir(run_dir):
                continue
            for iter_name in sorted(os.listdir(run_dir)):
                iter_dir = os.path.join(run_dir, iter_name)
                if os.path.isdir(iter_dir) and iter_name.startswith('iter_'):
                    paths.append(iter_dir)
        return paths

    def iter_run_configs(self):
        root = self.get_data_dir()
        if not os.path.isdir(root):
            return
        for run_name in sorted(os.listdir(root)):
            run_dir = os.path.join(root, run_name)
            if not os.path.isdir(run_dir):
                continue
            iters = sorted(
                os.path.join(run_dir, d) for d in os.listdir(run_dir)
                if d.startswith('iter_') and os.path.isdir(os.path.join(run_dir, d))
            )
            yield run_name, iters

    def get_log_path(self, run_path: str, node_id: int) -> str:
        # The log is combined across nodes; the same path is returned for
        # every node_id. parse_log handles the per-node split via the
        # event_trace and filter_messages does the inbox filter.
        return self._iter_dir(run_path)

    def get_cache_path(self, run_path: str, node_id: int) -> str:
        return os.path.join(self._iter_dir(run_path),
                            f'predicates-cache-{self.CACHE_VERSION}-{node_id}.txt.gz')

    # ---- Internal helpers ----

    def _iter_dir(self, run_path: str) -> str:
        # Tolerate callers that hand us either the iter dir directly or
        # one of the files inside it (parse_log historically takes a file).
        if os.path.isdir(run_path):
            return run_path
        return os.path.dirname(run_path)

    def _load(self, run_path: str) -> None:
        status_path = os.path.join(run_path, 'status.json')
        trace_path  = os.path.join(run_path, 'trace.json')
        with open(status_path, 'r') as f:
            self._cached_status = json.load(f)
        with open(trace_path, 'r') as f:
            self._cached_trace = json.load(f)
        events = (self._cached_trace.get('event_trace') or {}).get('Events') or []
        self._cached_messages = _parse_events(events)
        self._cached_path = run_path
