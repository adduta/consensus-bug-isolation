# Multi-Protocol Isolation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Introduce a `ConsensusProtocol` abstraction layer so the ISOLATION algorithm can run against any consensus protocol (currently XRPL, with PBFT as the second implementation) without changing the core fault-localization code.

**Architecture:** A new `src/protocols/` package holds an abstract `ConsensusProtocol` base class and one concrete subclass per protocol. All protocol-specific knowledge (message types, field definitions, log parsing, network topology, run classification) lives in the concrete class. The core files — `fault_localization.py`, `predicates.py` — are untouched. `cache.py` and `main.py` accept a protocol instance instead of hard-coding XRPL assumptions. `analyze.py`'s `stats()` function delegates to `protocol.classify_run()` instead of calling `new_incompatible_ledger` / `new_insufficient_support` directly.

**Tech Stack:** Python 3.11, `abc.ABC`, existing `rich`/`tqdm`/`multiprocessing` stack in `.venv`.

---

## File Map


| Action | Path                                                       | Responsibility                                                                                                                          |
| ------ | ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Create | `src/protocols/__init__.py`                                | Package marker                                                                                                                          |
| Create | `src/protocols/base.py`                                    | Abstract `ConsensusProtocol` interface                                                                                                  |
| Create | `src/protocols/xrpl.py`                                    | XRPL concrete class — wraps existing Proposal/Validation logic and XRPL-specific classify_run                                           |
| Create | `src/protocols/pbft.py`                                    | PBFT concrete class — message types, log parsing, classify_run for Groups A-E                                                           |
| Modify | `src/models/predicates.py` lines 3-5                       | Remove hard-coded `from .messages import Proposal, Validation`; use generic `Any`                                                       |
| Modify | `src/analysis/cache.py` lines 23-24, 118, 128-178, 209-235 | Accept `protocol` parameter; defer predicate generation from module-level to `build_predicates(protocol)`                               |
| Modify | `scripts/main.py` lines 36-37, 62, 71-73, 74, 114          | Accept `protocol` argument; replace hard-coded 7-node / partition / results.txt logic with protocol calls                               |
| Modify | `scripts/analyze.py` lines 134-153, 196-303                | Replace hard-coded XRPL bug type dict and `new_incompatible_ledger` calls with `protocol.classify_run()` and `protocol.get_bug_types()` |
| Create | `scripts/run_analysis.py`                                  | New CLI entry point with `--protocol xrpl|pbft` flag                                                                                    |
| Create | `tests/test_xrpl_protocol.py`                              | Unit tests for XRPLProtocol                                                                                                             |
| Create | `tests/test_pbft_protocol.py`                              | Unit tests for PBFTProtocol                                                                                                             |
| Create | `tests/test_cache_protocol.py`                             | Tests that `build_predicates` and `generate_predicate_cache` work with both protocols                                                   |


---

## Task 1: Abstract protocol interface

**Files:**

- Create: `src/protocols/__init__.py`
- Create: `src/protocols/base.py`
- **Step 1: Write the failing import test**

```python
# tests/test_protocols_base.py
from src.protocols.base import ConsensusProtocol
import inspect

def test_is_abstract():
    assert inspect.isabstract(ConsensusProtocol)

def test_required_methods():
    # filter_aggregation is a concrete method with a default no-op — not abstract
    required = {
        'get_fields', 'parse_log', 'get_num_nodes',
        'filter_messages', 'is_successful', 'classify_run',
        'get_bug_types', 'wrap_observations',
    }
    abstract_methods = ConsensusProtocol.__abstractmethods__
    assert required == abstract_methods

def test_filter_aggregation_default_is_noop():
    """filter_aggregation has a default implementation so subclasses need not override it."""
    class MinimalProtocol(ConsensusProtocol):
        def get_fields(self): return []
        def parse_log(self, path): return []
        def get_num_nodes(self): return 1
        def filter_messages(self, msgs, node_id): return msgs
        def is_successful(self, run_dir): return True
        def classify_run(self, run_dir): return set()
        def get_bug_types(self): return []
        def wrap_observations(self, pred, observed_nodes): return {}
    p = MinimalProtocol()
    d = {'key': 'value'}
    assert p.filter_aggregation(d) is d  # default returns same dict unchanged
```

- **Step 2: Run test to verify it fails**

```bash
cd /Users/addacarutasu/thesis/consensus-bug-isolation
.venv/bin/python -m pytest tests/test_protocols_base.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.protocols'`

- **Step 3: Create the package and base class**

```python
# src/protocols/__init__.py
# (empty)
```

```python
# src/protocols/base.py
from abc import ABC, abstractmethod


class ConsensusProtocol(ABC):
    """
    Abstract base class for consensus protocol adapters.

    Each protocol subclass encapsulates all protocol-specific knowledge:
    - Message types and their fields (for predicate generation)
    - Log file parsing (extract messages from raw replica/validator logs)
    - Network topology (number of nodes, partition structure)
    - Run classification (which bug type, if any, did this run exhibit)
    - Observation wrapping (how per-node observations become predicate keys)
    """

    @abstractmethod
    def get_fields(self) -> list[tuple[type, str, str]]:
        """
        Return (MessageType, field_name, type_category) tuples.

        type_category groups fields that can be meaningfully compared with
        the same set of operators (e.g. 'time', 'seq', 'hash', set[int]).
        This list drives exhaustive predicate generation in cache.py.
        """

    @abstractmethod
    def parse_log(self, path: str) -> list:
        """
        Parse one replica/validator log file.

        Args:
            path: Absolute path to the log file.
        Returns:
            List of message objects (instances of this protocol's message types).
        """

    @abstractmethod
    def get_num_nodes(self) -> int:
        """Return the number of nodes/replicas per run (7 for XRPL, 4 for PBFT)."""

    @abstractmethod
    def filter_messages(self, messages: list, node_id: int) -> list:
        """
        Filter the message list to those relevant to a given node's perspective.

        For XRPL this applies the UNL partition filter.
        For PBFT this can return messages unchanged.
        """

    @abstractmethod
    def is_successful(self, run_dir: str) -> bool:
        """Return True if the run completed without any violations."""

    @abstractmethod
    def classify_run(self, run_dir: str) -> set[str]:
        """
        Return the set of bug-type labels this run exhibits.

        Returns an empty set for correct runs.
        Labels must be drawn from get_bug_types().

        Example (XRPL):  {'Incompatible'}
        Example (PBFT):  {'Invalid Operation'}   or   {'Partition Timeout'}   or   set()
        """

    @abstractmethod
    def get_bug_types(self) -> list[str]:
        """
        Return all possible bug-type labels for this protocol.

        Used by stats() to build the per-bug-type confusion matrix.
        Example (XRPL):  ['Incompatible', 'Insufficient', 'Agreement']
        Example (PBFT):  ['Invalid Operation', 'Seq-No Replay', 'View-Change Fault', 'Partition Timeout', 'Split Brain']
        """

    @abstractmethod
    def wrap_observations(self, pred: str, observed_nodes: set) -> dict[str, bool]:
        """
        Convert a set of node IDs that observed a predicate into keyed observations.

        For XRPL: generates 5 threshold entries per predicate using UNL partitions.
        For PBFT: can generate a single entry or quorum-based entries.

        Args:
            pred:           String representation of the predicate.
            observed_nodes: Set of node IDs that observed this predicate as true.
        Returns:
            Dict mapping observation key → bool for insertion into a Report.
        """

    def filter_aggregation(self, aggregation: dict) -> dict:
        """
        Optional post-processing of the aggregation dict after all reports are loaded.

        Default implementation: no-op (return unchanged).
        Override in protocol subclasses to drop irrelevant predicates before isolation.
        Example: XRPLProtocol removes predicates involving 'consensus_hash'.
        """
        return aggregation
```

- **Step 4: Run test to verify it passes**

```bash
.venv/bin/python -m pytest tests/test_protocols_base.py -v
```

Expected: 2 PASSED

- **Step 5: Commit**

```bash
git add src/protocols/__init__.py src/protocols/base.py tests/test_protocols_base.py
git commit -m "feat: add abstract ConsensusProtocol base class"
```

---

## Task 2: XRPLProtocol concrete class

**Files:**

- Create: `src/protocols/xrpl.py`
- Test: `tests/test_xrpl_protocol.py`

Note: `src/models/messages.py` and `src/utils/config.py` are **not deleted** — they are re-exported from `xrpl.py` for backwards compatibility with existing cache files and scripts.

- **Step 1: Write failing tests**

```python
# tests/test_xrpl_protocol.py
import os
import pytest
from src.protocols.xrpl import XRPLProtocol
from src.models.messages import Proposal, Validation

SAMPLE_RUN = 'data/buggy-7-1-0-6-small-scope/1686951117'

protocol = XRPLProtocol()

def test_get_num_nodes():
    assert protocol.get_num_nodes() == 7

def test_get_fields_returns_11_entries():
    fields = protocol.get_fields()
    assert len(fields) == 11

def test_get_fields_types():
    fields = protocol.get_fields()
    types = {f[0] for f in fields}
    assert Proposal in types
    assert Validation in types

def test_get_bug_types():
    assert set(protocol.get_bug_types()) == {'Incompatible', 'Insufficient', 'Agreement'}

def test_parse_log_returns_messages():
    path = os.path.join(SAMPLE_RUN, 'validator_0.txt')
    if not os.path.exists(path):
        pytest.skip('sample data not present')
    messages = protocol.parse_log(path)
    assert len(messages) > 0
    assert all(isinstance(m, (Proposal, Validation)) for m in messages)

def test_filter_messages_node_0_uses_low_partition():
    # node 0 is in SET_LOW; messages from nodes outside SET_LOW should be filtered
    from src.models.messages import Validation
    class FakeMsg:
        def __init__(self, peers):
            self.peers = set(peers)
    msgs = [FakeMsg([0, 1]), FakeMsg([5, 6]), FakeMsg([2, 3])]
    filtered = protocol.filter_messages(msgs, node_id=0)
    # node 5 and 6 are NOT in FILTER_SET_LOW, so message with only [5,6] is dropped
    assert all(not m.peers.isdisjoint({0,1,2,3,4}) for m in filtered)

def test_filter_messages_node_6_uses_high_partition():
    class FakeMsg:
        def __init__(self, peers):
            self.peers = set(peers)
    msgs = [FakeMsg([0, 1]), FakeMsg([5, 6])]
    filtered = protocol.filter_messages(msgs, node_id=6)
    # node 0 and 1 are NOT in FILTER_SET_HIGH, so [0,1] message is dropped
    assert all(not m.peers.isdisjoint({2,3,4,5,6}) for m in filtered)

def test_is_successful_correct_run():
    path = os.path.join(SAMPLE_RUN)
    if not os.path.exists(path):
        pytest.skip('sample data not present')
    # Most runs in the dataset are buggy; just confirm the method runs
    result = protocol.is_successful(path)
    assert isinstance(result, bool)

def test_wrap_observations_generates_5_thresholds():
    obs = protocol.wrap_observations('some_predicate', observed_nodes={0, 1, 2})
    assert len(obs) == 5
    # All threshold keys must be present
    for t in range(5):
        assert f'"some_predicate" > {t}' in obs
    # 3 nodes in SET_LOW={0..4}: thresholds 0,1,2 are True; 3,4 are False
    assert obs['"some_predicate" > 0'] is True
    assert obs['"some_predicate" > 2'] is True
    assert obs['"some_predicate" > 3'] is False

def test_wrap_observations_empty_nodes():
    obs = protocol.wrap_observations('pred', observed_nodes=set())
    assert all(v is False for v in obs.values())

def test_classify_run_returns_set():
    path = SAMPLE_RUN
    if not os.path.exists(path):
        pytest.skip('sample data not present')
    result = protocol.classify_run(path)
    assert isinstance(result, set)
    assert result.issubset({'Incompatible', 'Insufficient', 'Agreement'})
```

- **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_xrpl_protocol.py -v
```

Expected: `ImportError: cannot import name 'XRPLProtocol'`

- **Step 3: Implement XRPLProtocol**

```python
# src/protocols/xrpl.py
import os
import re

from .base import ConsensusProtocol  # single dot — same package
from ..models.messages import Proposal, Validation
from ..utils.config import FILTER_SET_LOW, FILTER_SET_HIGH, SET_LOW, SET_HIGH

# Re-export for backwards compatibility
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

    def classify_run(self, run_dir: str) -> set[str]:
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
```

- **Step 4: Run tests to verify they pass**

```bash
.venv/bin/python -m pytest tests/test_xrpl_protocol.py -v
```

Expected: all PASSED (skip if sample data absent)

- **Step 5: Commit**

```bash
git add src/protocols/xrpl.py tests/test_xrpl_protocol.py
git commit -m "feat: add XRPLProtocol concrete class"
```

---

## Task 3: Fix predicates.py — remove hard-coded XRPL import

**Files:**

- Modify: `src/models/predicates.py` lines 3-5

The `Message` type alias imports `Proposal` and `Validation` directly, creating a hidden XRPL dependency in what should be a protocol-agnostic file.

- **Step 1: Write test confirming predicates.py has no XRPL dependency after the change**

```python
# tests/test_predicates_generic.py
import operator as op
from src.models.predicates import Assertion, Predicate

class FakeMsg:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.peers = {0}  # Predicate.eval checks len(l.peers) >= threshold

def test_assertion_on_arbitrary_message_type():
    a = Assertion('x', 'x', op.eq)
    assert a.eval(FakeMsg(1, 2), FakeMsg(1, 9)) is True
    assert a.eval(FakeMsg(1, 2), FakeMsg(3, 9)) is False

def test_predicate_on_arbitrary_message_type():
    p = Predicate(FakeMsg, FakeMsg, threshold=1, assertions=[Assertion('x', 'y', op.eq)])
    assert p.eval(FakeMsg(5, 5), FakeMsg(5, 5)) is True
    assert p.eval(FakeMsg(1, 2), FakeMsg(3, 4)) is False
```

- **Step 2: Run test to verify it passes already (predicates are already generic, just confirm)**

```bash
.venv/bin/python -m pytest tests/test_predicates_generic.py -v
```

Expected: PASSED — confirms assertions work generically

- **Step 3: Remove XRPL import from predicates.py**

In `src/models/predicates.py` make three changes:

Remove lines 3-5 (the import and type alias):

```python
# Remove these two lines entirely:
from .messages import Proposal, Validation
Message = Proposal | Validation
```

Change the `eval` signature on `Assertion` (currently line 28) to drop the `Message` type hint, since `Message` will no longer be defined:

```python
# Before
def eval(self, l: Message, r: Message) -> bool:
# After
def eval(self, l, r) -> bool:
```

Do the same for `Predicate.eval` (currently line 52):

```python
# Before
def eval(self, l: Message, r: Message):
# After
def eval(self, l, r):
```

- **Step 4: Verify nothing breaks**

```bash
.venv/bin/python -m pytest tests/ -v
```

Expected: all existing tests still PASSED

- **Step 5: Commit**

```bash
git add src/models/predicates.py tests/test_predicates_generic.py
git commit -m "refactor: remove XRPL-specific import from predicates.py"
```

---

## Task 4: Refactor cache.py — defer predicate generation to runtime

**Files:**

- Modify: `src/analysis/cache.py`
- Test: `tests/test_cache_protocol.py`

**The core problem:** predicate generation currently runs at *import time* (module-level code, lines 118-178 in cache.py). This hard-codes XRPL fields and prevents swapping protocols. The fix is to move this into a `build_predicates(protocol)` function, and to accept a `protocol` parameter in `generate_predicate_cache`.

Because `generate_predicate_cache` is called via `multiprocessing.Pool.imap_unordered`, it cannot receive the protocol object as a regular argument (objects must be picklable). The solution is a module-level `_PROTOCOL` variable that is set in the main process **before the Pool is created**. Worker processes inherit it via `fork` (the default start method on macOS/Linux). Windows uses `spawn` and would require a `Pool(initializer=set_protocol, initargs=(protocol,))` call instead — not needed for this project's target platform (darwin).

Also remove the two module-level `print()` calls (lines 173 and 179-180) that were debugging aids; they run at every import and will produce noise in worker processes.

- **Step 1: Write failing tests**

```python
# tests/test_cache_protocol.py
import operator as op
from src.protocols.xrpl import XRPLProtocol
from src.analysis.cache import build_predicates, set_protocol

def test_build_predicates_xrpl_count():
    protocol = XRPLProtocol()
    predicates, by_type = build_predicates(protocol)
    # Baseline: XRPL currently generates ~4496 predicates
    assert len(predicates) > 4000

def test_build_predicates_returns_by_type_index():
    protocol = XRPLProtocol()
    _, by_type = build_predicates(protocol)
    from src.models.messages import Proposal, Validation
    assert (Proposal, Proposal) in by_type
    assert (Proposal, Validation) in by_type
    assert (Validation, Validation) in by_type

def test_set_protocol_stores_protocol():
    protocol = XRPLProtocol()
    set_protocol(protocol)
    from src.analysis import cache as c
    assert c._PROTOCOL is protocol

class MinimalProtocol(XRPLProtocol):
    """Protocol with a single field pair — generates far fewer predicates."""
    def get_fields(self):
        from src.models.messages import Proposal
        return [(Proposal, 'propose_seq', 'seq_prp')]

def test_build_predicates_respects_protocol_fields():
    protocol = MinimalProtocol()
    predicates, _ = build_predicates(protocol)
    # Only Proposal->Proposal predicates with seq_prp field
    assert len(predicates) < 100
```

- **Step 2: Run tests to confirm they fail**

```bash
.venv/bin/python -m pytest tests/test_cache_protocol.py -v
```

Expected: `ImportError: cannot import name 'build_predicates'`

- **Step 3: Refactor cache.py**

Replace the module-level field definitions and predicate generation block (lines 115-180) with a `build_predicates` function. Add `set_protocol` and `_PROTOCOL` module globals. Update `generate_predicate_cache` and `parse_validator_log` to use `_PROTOCOL`.

```python
# src/analysis/cache.py
# --- replace lines 23-24 (protocol-specific imports) ---
# Remove:
#   from ..models.messages import Proposal, Validation
#   from ..utils.config import FILTER_SET_LOW, FILTER_SET_HIGH
# Keep only:
from ..models.predicates import Assertion, Predicate

# --- add after imports ---
_PROTOCOL = None   # Set by set_protocol() before any worker processes are spawned

def set_protocol(protocol) -> None:
    """Register the active protocol. Must be called before generate_predicate_cache."""
    global _PROTOCOL
    _PROTOCOL = protocol
```

Replace the module-level `fields`, `OPERATORS_BY_TYPE`, and predicate generation loop (lines 115-180) with:

```python
# Mapping of type categories to valid comparison operators
OPERATORS_BY_TYPE = {
    'seq_prp':   [op.eq, op.ne, op.lt, op.gt],
    'seq':       [op.eq, op.ne, op.lt, op.gt],
    'flags':     [op.eq, op.ne],
    'ledger_seq':[op.eq, op.ne, op.lt, op.gt],
    set[int]:    [op.eq, op.ne, set.isdisjoint, set.issubset, set.issuperset],
    'hash_l':    [op.eq, op.ne],
    'hash_tx':   [op.eq, op.ne],
    'hash':      [op.eq, op.ne],
    'time':      [op.eq, op.ne],
}


def build_predicates(protocol) -> tuple[list[Predicate], dict]:
    """
    Build the full predicate list for the given protocol.

    Returns:
        (predicates, predicates_by_type)
        predicates:        flat list of all Predicate objects
        predicates_by_type: dict keyed by (typeL, typeR) for fast lookup
    """
    fields = protocol.get_fields()
    message_types = list({f[0] for f in fields})

    predicates: list[Predicate] = []

    for threshold in range(1, 5):
        for left_type, right_type in itertools.product(message_types, repeat=2):
            left_fields  = [f for f in fields if f[0] == left_type]
            right_fields = [f for f in fields if f[0] == right_type]
            compatible   = [
                (lf, rf)
                for lf, rf in itertools.product(left_fields, right_fields)
                if lf[2] == rf[2]
            ]
            for n_assertions in range(0, 4):
                for field_combo in itertools.combinations(compatible, n_assertions):
                    ops_per_field = [
                        [(lf, operator, rf) for operator in OPERATORS_BY_TYPE[lf[2]]]
                        for lf, rf in field_combo
                    ]
                    for op_combo in itertools.product(*ops_per_field):
                        assertions = [Assertion(lf[1], rf[1], o) for lf, o, rf in op_combo]
                        predicates.append(Predicate(left_type, right_type, threshold, assertions))

    predicates_by_type: dict[tuple[type, type], list[Predicate]] = {}
    for pred in predicates:
        predicates_by_type.setdefault((pred.typeL, pred.typeR), []).append(pred)

    return predicates, predicates_by_type
```

Update `parse_validator_log` to delegate to the protocol:

```python
def parse_validator_log(path: str) -> list:
    """Parse a log file using the active protocol."""
    return _PROTOCOL.parse_log(path)
```

Update `generate_predicate_cache` to use the protocol for filtering and predicate building:

```python
def generate_predicate_cache(args):
    path, node_id = args
    cache_path = os.path.join(path, f'predicates-cache-{node_id}.txt')
    if os.path.exists(cache_path):
        return

    log_path = os.path.join(path, f'validator_{node_id}.txt')
    messages = _PROTOCOL.parse_log(log_path)
    messages = _PROTOCOL.filter_messages(messages, node_id)

    # Build predicates fresh for this worker (inherited from fork, same protocol)
    _, preds_by_type = build_predicates(_PROTOCOL)

    active_predicates_by_type: dict = {}
    all_predicate_states = []
    for key, pred_list in preds_by_type.items():
        states = [PredicateState(p) for p in pred_list]
        active_predicates_by_type[key] = states
        all_predicate_states.extend(states)

    message_deduplication_map = {}
    for message in messages:
        if message in message_deduplication_map:
            message.peers.update(message_deduplication_map[message])
        for other_message, peers in message_deduplication_map.items():
            other_message.peers = peers
            type_key = (type(other_message), type(message))
            if type_key not in active_predicates_by_type:
                continue
            active_predicates = active_predicates_by_type[type_key]
            to_remove = [i for i, p in enumerate(active_predicates) if p.eval(other_message, message)]
            for i in reversed(to_remove):
                active_predicates.pop(i)
        message_deduplication_map.setdefault(message, set())
        message_deduplication_map[message] = message.peers

    output_lines = [
        f'{ps.observed} {ps.observed_true} {str(ps)}\n'
        for ps in all_predicate_states
    ]
    with open(cache_path, 'w') as f:
        f.writelines(output_lines)
```

- **Step 4: Run the cache tests**

```bash
.venv/bin/python -m pytest tests/test_cache_protocol.py -v
```

Expected: all PASSED

- **Step 5: Smoke-test XRPL pipeline still works end-to-end**

```bash
.venv/bin/python -c "
from src.protocols.xrpl import XRPLProtocol
from src.analysis.cache import set_protocol, build_predicates
p = XRPLProtocol()
set_protocol(p)
preds, by_type = build_predicates(p)
print(len(preds), 'predicates — OK')
"
```

Expected: prints `4496 predicates — OK` (or close)

- **Step 6: Commit**

```bash
git add src/analysis/cache.py tests/test_cache_protocol.py
git commit -m "refactor: make cache.py protocol-aware via set_protocol() and build_predicates()"
```

---

## Task 5: Refactor main.py — inject protocol

**Files:**

- Modify: `scripts/main.py`

Remove every hard-coded XRPL assumption and replace with protocol method calls.

- **Step 1: Identify all hard-coded spots**

Lines to change:

- Line 36-37: `from src.utils.config import SET_LOW, SET_HIGH` → remove (now in XRPLProtocol)
- Line 62: `zip(it.repeat(path), [0,1,2,3,4,5,6])` → `range(protocol.get_num_nodes())`
- Lines 71-73: partition threshold wrapping → `protocol.wrap_observations(pred, observed_nodes)`
- Line 74: `"reason: all committed" in f.read()` → `protocol.is_successful(path)`
- Line 114: `range(7)` → `range(protocol.get_num_nodes())`
- Line 128: `'consensus_hash' not in x` filter → move into XRPLProtocol or make configurable
- **Step 2: Update `run_message_based_analysis` signature to accept a protocol**

```python
# scripts/main.py — updated function signature and body

def run_message_based_analysis(protocol=None):
    """
    Run message-based consensus-aware analysis pipeline.

    Args:
        protocol: ConsensusProtocol instance. Defaults to XRPLProtocol()
                  for backwards compatibility.
    """
    if protocol is None:
        from src.protocols.xrpl import XRPLProtocol
        protocol = XRPLProtocol()

    # Register protocol with cache module BEFORE the Pool is created.
    # Worker processes are forked from the main process and inherit _PROTOCOL.
    # If set_protocol() is called after Pool(), workers see _PROTOCOL = None.
    from src.analysis.cache import set_protocol
    set_protocol(protocol)

    num_nodes = protocol.get_num_nodes()

    # Pool is created AFTER set_protocol() — critical ordering
    pool = Pool()

    # ... (rest of function; replace hard-coded spots below)
```

Replace line 62 (load cache for all nodes):

```python
# Before
results = list(map(load_predicate_cache, zip(it.repeat(path), [0, 1, 2, 3, 4, 5, 6])))
# After
results = list(map(load_predicate_cache, zip(it.repeat(path), range(num_nodes))))
```

Replace lines 71-73 (partition threshold wrapping):

```python
# Before
for threshold in range(0, 5):
    predicate_key = f'"{pred}" > {threshold}'
    partition_observations[predicate_key] = (nodes_low > threshold or nodes_high > threshold)
# After
partition_observations.update(protocol.wrap_observations(pred, observed_nodes))
```

Replace line 74 (success check):

```python
# Before
successful = "reason: all committed" in f.read()
# After
successful = protocol.is_successful(path)
```

Replace line 114 (cache task generation):

```python
# Before
cache_tasks = [(path, node_id) for path in paths for node_id in range(7)]
# After
cache_tasks = [(path, node_id) for path in paths for node_id in range(num_nodes)]
```

Replace line 128 (consensus_hash filter — move to XRPLProtocol.wrap_observations or a dedicated hook):

```python
# Add an optional filter_aggregation hook to ConsensusProtocol with default no-op:
# base.py addition:
def filter_aggregation(self, aggregation: dict) -> dict:
    """Optional post-processing of aggregation dict. Default: no-op."""
    return aggregation

# xrpl.py override:
def filter_aggregation(self, aggregation: dict) -> dict:
    return {k: v for k, v in aggregation.items() if 'consensus_hash' not in k}

# main.py line 128:
aggregation = protocol.filter_aggregation(aggregation)
```

- **Step 3: Verify XRPL pipeline still works with default protocol**

```bash
.venv/bin/python -c "
from scripts.main import run_message_based_analysis
# Dry-run: just imports and default protocol construction should work
print('main.py import OK')
"
```

- **Step 4: Commit**

```bash
git add src/protocols/base.py src/protocols/xrpl.py scripts/main.py
git commit -m "refactor: main.py accepts protocol parameter; remove hard-coded XRPL topology"
```

---

## Task 6: Refactor analyze.py stats() — use protocol.classify_run()

**Files:**

- Modify: `scripts/analyze.py`

`stats(filters)` currently has hard-coded XRPL bug types and calls `new_incompatible_ledger` / `new_insufficient_support` directly. Replace with a `protocol` parameter and dynamic `agg` dict construction.

- **Step 1: Write regression test that stats() output matches paper values with XRPLProtocol**

```python
# tests/test_analyze_protocol.py
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
```

- **Step 2: Run test to verify it fails**

```bash
.venv/bin/python -m pytest tests/test_analyze_protocol.py -v
```

Expected: `TypeError: stats() got unexpected keyword argument 'protocol'`

- **Step 3: Update stats() signature and internals**

```python
# scripts/analyze.py — new signature
def stats(filters, protocol=None, return_agg=False):
    if protocol is None:
        from src.protocols.xrpl import XRPLProtocol
        protocol = XRPLProtocol()

    bug_types = protocol.get_bug_types()

    # Build agg dict dynamically from protocol's bug types
    agg = {bt: {'TP': set(), 'FP': set(), 'TN': set(), 'FN': set()} for bt in bug_types}
    ...
```

Replace the body's classification block (lines 196-303). Instead of the long if/elif chain calling `new_insufficient_support` / `new_incompatible_ledger`, use:

```python
# For each run:
run_dir = f'data/{version}{config}/{run}'
actual_bugs = protocol.classify_run(run_dir)   # e.g. {'Incompatible'} or set()

for bt in bug_types:
    in_actual  = bt in actual_bugs
    if in_actual:
        agg[bt]['TP' if p else 'FN'].add(run)
    else:
        agg[bt]['FP' if p else 'TN'].add(run)
```

Add `return_agg` support at the end:

```python
    if return_agg:
        return agg
```

- **Step 4: Run regression test**

```bash
.venv/bin/python -m pytest tests/test_analyze_protocol.py -v
```

Expected: PASSED

- **Step 5: Confirm scores table still prints correctly**

```bash
.venv/bin/python scripts/analyze.py
```

Expected: same table output as before the refactoring.

- **Step 6: Commit**

```bash
git add scripts/analyze.py tests/test_analyze_protocol.py
git commit -m "refactor: analyze.py stats() accepts protocol; delegates bug classification to protocol.classify_run()"
```

---

## Task 7: PBFTProtocol — message types and concrete class

**Files:**

- Create: `src/protocols/pbft.py`
- Test: `tests/test_pbft_protocol.py`

This task implements the PBFT concrete class. The run data lives in `out/tests-D{d}-C{c}-{scope}/outN.txt`. Unlike XRPL, PBFT produces one execution log per run (not one per replica). `parse_log` therefore returns all messages from the single log; `get_num_nodes` returns 1 (one log file per run); and `filter_messages` is a no-op.

The `classify_run` oracle is derived directly from the root-cause taxonomy in `PBFT_ROOT_CAUSE_ANALYSIS.md`.

- **Step 1: Write failing tests**

```python
# tests/test_pbft_protocol.py
import pytest
from src.protocols.pbft import PBFTProtocol, PrePrepare, Prepare, Commit, ViewChange

protocol = PBFTProtocol()

# ---- group A sample (operation mutation, validity+agreement)
GROUP_A_FILE = 'out/tests-D0-C1-ss/out95.txt'
# ---- group B sample (seq-number mutation, agreement only after view-change)
GROUP_B_FILE = 'out/tests-D1-C2-ss/out7.txt'
# ---- group C sample (VIEW-CHANGE corruption, termination)
GROUP_C_FILE = 'out/tests-D1-C2-ss/out49.txt'
# ---- group D sample (partition only, termination)
GROUP_D_FILE = 'out/tests-D1-C0/out115.txt'
# ---- group E sample (split-brain, agreement, high viewNo)
GROUP_E_FILE = 'out/tests-D2-C0/out87.txt'
# ---- correct run (no violation)
CORRECT_FILE = 'out/tests-D1-C0/out1.txt'

def _skip_if_absent(path):
    import os
    if not os.path.exists(path):
        pytest.skip(f'{path} not present')

def test_get_num_nodes():
    assert protocol.get_num_nodes() == 1

def test_get_bug_types():
    assert set(protocol.get_bug_types()) == {
        'Invalid Operation', 'Seq-No Replay', 'View-Change Fault', 'Partition Timeout', 'Split Brain'
    }

def test_get_fields_covers_root_causes():
    fields = protocol.get_fields()
    field_names = [f[1] for f in fields]
    # Invalid Operation / Seq-No Replay require PRE-PREPARE fields
    assert 'operation_first' in field_names
    assert 'seq_no' in field_names
    # View-Change Fault requires VIEW-CHANGE
    assert 'new_view_no' in field_names

def test_classify_run_group_a():
    _skip_if_absent(GROUP_A_FILE)
    result = protocol.classify_run(GROUP_A_FILE)
    assert 'Invalid Operation' in result

def test_classify_run_group_b():
    _skip_if_absent(GROUP_B_FILE)
    result = protocol.classify_run(GROUP_B_FILE)
    assert 'Seq-No Replay' in result

def test_classify_run_group_c():
    _skip_if_absent(GROUP_C_FILE)
    result = protocol.classify_run(GROUP_C_FILE)
    assert 'View-Change Fault' in result

def test_classify_run_group_d():
    _skip_if_absent(GROUP_D_FILE)
    result = protocol.classify_run(GROUP_D_FILE)
    assert 'Partition Timeout' in result

def test_classify_run_group_e():
    _skip_if_absent(GROUP_E_FILE)
    result = protocol.classify_run(GROUP_E_FILE)
    assert 'Split Brain' in result

def test_is_successful_on_non_violation():
    _skip_if_absent(CORRECT_FILE)
    assert protocol.is_successful(CORRECT_FILE) is True

def test_is_successful_on_violation():
    _skip_if_absent(GROUP_A_FILE)
    assert protocol.is_successful(GROUP_A_FILE) is False

def test_parse_log_returns_preprepare():
    _skip_if_absent(GROUP_A_FILE)
    messages = protocol.parse_log(GROUP_A_FILE)
    assert any(isinstance(m, PrePrepare) for m in messages)

def test_filter_messages_is_noop():
    class Msg: pass
    msgs = [Msg(), Msg()]
    assert protocol.filter_messages(msgs, node_id=0) is msgs

def test_wrap_observations_single_entry():
    obs = protocol.wrap_observations('some_pred', observed_nodes={0})
    # PBFT: one threshold entry (observed by >= 1 replica)
    assert '"some_pred" > 0' in obs
    assert obs['"some_pred" > 0'] is True
```

- **Step 2: Run tests to confirm they fail**

```bash
.venv/bin/python -m pytest tests/test_pbft_protocol.py -v
```

Expected: `ImportError: cannot import name 'PBFTProtocol'`

- **Step 3: Implement src/protocols/pbft.py**

```python
# src/protocols/pbft.py
import re
from .base import ConsensusProtocol  # single dot — same package

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
_MUTATED_RE = re.compile(r'^\s+-\s+Mutated:\s+\d+\s+->\s+\S+\{(.+)\}\s+##\d+')

_TYPE_CLASSES = {
    'PRE-PREPARE': PrePrepare,
    'PREPARE':     Prepare,
    'COMMIT':      Commit,
    'VIEW-CHANGE': ViewChange,
}


def _parse_messages_from_log(text: str) -> list:
    """Extract all Sent: messages from a PBFT execution log."""
    import json
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
            continue
        msg_type = msg.get('type', '')
        cls = _TYPE_CLASSES.get(msg_type)
        if cls:
            messages.append(cls(sender, msg))
    return messages


def _parse_mutations(text: str) -> list[dict]:
    """Extract mutated message metadata from a PBFT execution log."""
    import json
    mutations = []
    for line in text.splitlines():
        m = _MUTATED_RE.match(line)
        if not m:
            continue
        # The mutated JSON may be incomplete in the log; try best-effort parse
        try:
            msg = json.loads('{' + m.group(1) + '}')
            mutations.append(msg)
        except json.JSONDecodeError:
            # Fallback: just record the raw string
            mutations.append({'_raw': m.group(1)})
    return mutations


def _parse_violations(text: str) -> list[dict]:
    """Extract violation entries from a PBFT execution log."""
    _VIOLATION_RE = re.compile(
        r'Violation of (\w+) at Replica:\s*(\d+).*viewNo:\s*(\d+).*seqNo:\s*(\d+)'
    )
    violations = []
    for line in text.splitlines():
        m = _VIOLATION_RE.search(line)
        if m:
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

        violations = _parse_violations(text)
        if not violations:
            return set()

        mutations  = _parse_mutations(text)
        groups     = set()

        if not mutations:
            # No logged mutations → purely network-induced
            high_view = any(v['view_no'] >= 2 for v in violations)
            if high_view and any(v['type'] == 'AGREEMENT' for v in violations):
                groups.add('Split Brain')
            else:
                groups.add('Partition Timeout')
            return groups

        # View-Change Fault (C): VIEW-CHANGE or NEW-VIEW was mutated
        vc_mutated = any(
            m.get('type') in ('VIEW-CHANGE', 'NEW-VIEW') for m in mutations
        )
        if vc_mutated:
            groups.add('View-Change Fault')

        # Seq-No Replay (B): seq-number mutation (old request replayed at a different slot)
        # Signature: PRE-PREPARE mutated + timestamp of earlier request used at later seq
        for m in mutations:
            if m.get('type') == 'PRE-PREPARE':
                ts  = m.get('timestamp')
                seq = m.get('seq-number')
                if ts is not None and seq is not None and ts < seq:
                    groups.add('Seq-No Replay')

        # Invalid Operation (A): operation field mutation (same seq but different first/second values)
        for m in mutations:
            if m.get('type') == 'PRE-PREPARE' and 'operation' in m:
                if any(v['type'] in ('VALIDITY', 'AGREEMENT') for v in violations):
                    groups.add('Invalid Operation')

        if not groups:
            groups.add('Partition Timeout')  # Partition with non-critical mutations → timeout

        return groups

    def get_bug_types(self) -> list[str]:
        return ['Invalid Operation', 'Seq-No Replay', 'View-Change Fault', 'Partition Timeout', 'Split Brain']

    def wrap_observations(self, pred: str, observed_nodes: set) -> dict[str, bool]:
        # PBFT: single threshold (observed by at least one replica)
        return {f'"{pred}" > 0': len(observed_nodes) > 0}

    def filter_aggregation(self, aggregation: dict) -> dict:
        return aggregation  # No post-processing needed for PBFT
```

- **Step 4: Run PBFT tests**

```bash
.venv/bin/python -m pytest tests/test_pbft_protocol.py -v
```

Expected: all PASSED (test_classify_run_* tests will skip if `out/` absent, others pass)

- **Step 5: Commit**

```bash
git add src/protocols/pbft.py tests/test_pbft_protocol.py
git commit -m "feat: add PBFTProtocol with message types and classify_run for Groups A-E"
```

---

## Task 8: New CLI entry point

**Files:**

- Create: `scripts/run_analysis.py`

Provides a single entry point for both protocols and both pipeline types (message-based or baseline).

Note: `scripts/baseline.py` already exists in the codebase. Task 6 adds the `protocol` parameter to `stats()` in `analyze.py`; baseline.py calls `stats` so it will need its own `protocol` parameter added to `run_baseline_analysis()`. That is a one-line change: add `protocol=None` to the signature and pass it through to `stats()`, following the same pattern as `run_message_based_analysis()`.

- **Step 1: Write test**

```python
# tests/test_run_analysis_cli.py
import subprocess, sys

def test_help_flag():
    result = subprocess.run(
        [sys.executable, 'scripts/run_analysis.py', '--help'],
        cwd='/Users/addacarutasu/thesis/consensus-bug-isolation',
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert '--protocol' in result.stdout

def test_unknown_protocol_exits():
    result = subprocess.run(
        [sys.executable, 'scripts/run_analysis.py', '--protocol', 'unknown'],
        cwd='/Users/addacarutasu/thesis/consensus-bug-isolation',
        capture_output=True, text=True
    )
    assert result.returncode != 0
```

- **Step 2: Run tests to confirm they fail**

```bash
.venv/bin/python -m pytest tests/test_run_analysis_cli.py -v
```

Expected: FAILED (file doesn't exist yet)

- **Step 3: Create run_analysis.py**

```python
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


def get_protocol(name: str):
    if name == 'xrpl':
        from src.protocols.xrpl import XRPLProtocol
        return XRPLProtocol()
    elif name == 'pbft':
        from src.protocols.pbft import PBFTProtocol
        return PBFTProtocol()
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
    args = parser.parse_args()

    protocol = get_protocol(args.protocol)

    if args.baseline:
        from scripts.baseline import run_baseline_analysis
        run_baseline_analysis(protocol=protocol)
    else:
        from scripts.main import run_message_based_analysis
        run_message_based_analysis(protocol=protocol)


if __name__ == '__main__':
    main()
```

- **Step 4: Run tests**

```bash
.venv/bin/python -m pytest tests/test_run_analysis_cli.py -v
```

Expected: PASSED

- **Step 5: Commit**

```bash
git add scripts/run_analysis.py tests/test_run_analysis_cli.py
git commit -m "feat: add run_analysis.py unified CLI with --protocol flag"
```

---

## Task 9: Full regression — XRPL pipeline end-to-end

Before calling the feature complete, verify the XRPL pipeline still produces the same Table 2 / Table 3 results as before the refactoring.

- **Step 1: Run baseline (Table 2) via new entry point**

```bash
.venv/bin/python scripts/run_analysis.py --protocol xrpl --baseline
```

Expected: same 3-predicate table as paper (see MEMORY.md for reference values)

- **Step 2: Run ISOLATION (Table 3) via new entry point**

```bash
.venv/bin/python scripts/run_analysis.py --protocol xrpl
```

Expected: same 8-predicate output as paper

- **Step 3: Run full test suite**

```bash
.venv/bin/python -m pytest tests/ -v
```

Expected: all tests PASSED

- **Step 4: Final commit**

```bash
git add -A
git commit -m "test: full regression confirms XRPL results unchanged after protocol abstraction"
```

---

## Checklist: adding a third protocol in the future

When a new protocol (e.g., Tendermint) needs to be supported:

1. Create `src/protocols/tendermint.py` with message classes and a `TendermintProtocol` subclass
2. Implement all 8 abstract methods from `ConsensusProtocol`
3. Register it in `run_analysis.py`'s `get_protocol()` function
4. Add tests in `tests/test_tendermint_protocol.py`

No changes to `cache.py`, `fault_localization.py`, `predicates.py`, or `main.py`.