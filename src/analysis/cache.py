"""
Predicate Cache Generation Module

This module is responsible for generating and loading predicate evaluation caches
for the consensus bug isolation tool. It processes validator logs to evaluate
predicates on message pairs and caches results for fast aggregation.

Key responsibilities:
1. Parse validator logs to extract Proposals and Validations
2. Generate exhaustive predicates for message field comparisons
3. Evaluate predicates on message pairs from each validator node
4. Cache results to avoid recomputation during statistical analysis
"""

# Standard library imports
import gzip
import itertools
import json
import operator as op
import os
import re

# Local imports
from ..models.predicates import Assertion, Predicate
from ..protocols.base import ConsensusProtocol

_PROTOCOL = None   # Set by set_protocol() before any worker processes are spawned

def set_protocol(protocol: ConsensusProtocol) -> None:
    """Set the protocol for the cache generation."""
    global _PROTOCOL
    _PROTOCOL = protocol

class CachedPredicate:
    """
    Represents a predicate that has been evaluated and loaded from cache.

    Attributes:
        observed: Whether the predicate's message pattern was observed
        observed_true: Whether the predicate matched when observed
        name: String representation of the predicate
    """

    def __init__(self, observed: bool, observed_true: bool, name: str) -> None:
        self.observed = observed
        self.observed_true = observed_true
        self.name = name

    def __str__(self) -> str:
        return self.name


class PredicateState:
    """
    Lightweight wrapper that tracks per-run state for a predicate without copying.

    Instead of deep copying predicates for each run, we share the immutable
    predicate logic and only track mutable state (observed, observed_true) here.
    This significantly reduces memory usage and initialization overhead.
    """
    __slots__ = ['predicate', 'observed', 'observed_true']

    def __init__(self, predicate: Predicate) -> None:
        self.predicate = predicate
        self.observed = False
        self.observed_true = False

    def eval(self, l, r) -> bool:
        """Evaluate predicate with this instance's state tracking."""
        if self.observed_true or not (isinstance(l, self.predicate.typeL) and
                                       isinstance(r, self.predicate.typeR) and
                                       self.predicate.threshold <= len(l.peers)):
            return False
        self.observed = True
        for assertion in self.predicate.assertions:
            if not assertion.eval(l, r):
                return False
        self.observed_true = True
        return True

    def __str__(self) -> str:
        return str(self.predicate)


# Regex for parsing cached predicate lines: "True/False True/False predicate_description"
cache_re = re.compile(r'^(True|False) (True|False) (.+)')

def read_multiline_json(file):
    """
    Read a multi-line JSON object from a file stream.

    Validator logs contain JSON objects spread across multiple lines.
    This reads until it finds a closing brace on its own line.

    Args:
        file: Open file handle positioned at start of JSON object

    Returns:
        Parsed JSON object as a dictionary
    """
    lines = []
    while line := file.readline():
        lines.append(line)
        if line == '}\n':
            break
    return json.loads(''.join(lines))


def parse_validator_log(path: str) -> list:
    """
    Parse a validator log file to extract consensus messages.

    Reads through a validator log searching for "Received ProposeSet" and
    "Received Validation" markers, then parses the JSON message that follows.

    Args:
        path: Path to validator log file (e.g., data/.../validator_0.txt)

    Returns:
        List of Proposal and Validation message objects
    """
    return _PROTOCOL.parse_log(path)

# Message field definitions for predicate generation
# Format: (MessageType, field_name, type_category)
# Type categories group fields that can be meaningfully compared
# fields = [
#     # Proposal fields
#     (Proposal, 'peers', set[int]),           # Set of validator IDs that sent this message
#     (Proposal, 'close_time', 'time'),        # Ledger close time
#     (Proposal, 'previous_ledger', 'hash_l'), # Hash of previous ledger
#     (Proposal, 'propose_seq', 'seq_prp'),    # Proposal sequence number
#     (Proposal, 'transaction_hash', 'hash_tx'),# Hash of transaction set

#     # Validation fields
#     (Validation, 'peers', set[int]),          # Set of validator IDs that sent this message
#     (Validation, 'consensus_hash', 'hash_tx'),# Hash of agreed-upon transaction set
#     (Validation, 'flags', 'flags'),           # Validation flags (bitfield)
#     (Validation, 'ledger_hash', 'hash_l'),    # Hash of validated ledger
#     (Validation, 'ledger_sequence', 'ledger_seq'), # Ledger sequence number
#     (Validation, 'signing_time', 'time')      # Time validation was signed
# ]

"""
Generate all possible predicates exhaustively.

This generates predicates in the form:
"At least N messages of TypeL -> TypeR where <assertions>"

Parameters explored:
- Threshold (N): 1-4 messages minimum
- Message type pairs: Proposal->Proposal, Proposal->Validation, etc.
- Assertions: 0-3 field comparisons
- Operators: Depends on field type (eq/ne for hashes, lt/gt for sequences, etc.)

This generates approximately 360,000 unique predicates to test.
"""
predicates: list[Predicate] = []

# Mapping of type categories to valid comparison operators
OPERATORS_BY_TYPE = {
    'seq_prp': [op.eq, op.ne, op.lt, op.gt],         # Proposal sequence numbers
    'flags': [op.eq, op.ne],                          # Validation flags
    'ledger_seq': [op.eq, op.ne, op.lt, op.gt],      # Ledger sequence numbers
    set[int]: [op.eq, op.ne, set.isdisjoint, set.issubset, set.issuperset],  # Peer sets
    'hash_l': [op.eq, op.ne],                         # Ledger hashes
    'hash_tx': [op.eq, op.ne],                        # Transaction hashes
    'time': [op.eq, op.ne],                           # Timestamps
    'seq':        [op.eq, op.ne, op.lt, op.gt],        # Generic sequence/integer fields (PBFT legacy)
    'view':       [op.eq, op.ne, op.lt, op.gt],
    'view_current': [op.eq, op.ne, op.lt, op.gt],
    'view_next':    [op.eq, op.ne, op.lt, op.gt],
    'seqno':      [op.eq, op.ne, op.lt, op.gt],
    'rid':        [op.eq, op.ne],
    'op':         [op.eq, op.ne],
    'op_first':   [op.eq, op.ne],
    'op_second':  [op.eq, op.ne],
    'proof_count':[op.eq, op.ne, op.lt, op.gt],
    'vc_proof_count':   [op.eq, op.ne, op.lt, op.gt],
    'prep_proof_count': [op.eq, op.ne, op.lt, op.gt],
    'distinct_count':   [op.eq, op.ne, op.lt, op.gt],
    # Proof-derived sets (extracted from VIEW-CHANGE / NEW-VIEW prepared-proofs).
    # Treated as set[int] but with distinct categories so unrelated semantic
    # fields (e.g. PrePrepare.peers vs ViewChange.pp_seq_set) don't pair up.
    # Subset/superset/disjoint comparators produced low-signal noise predicates
    # (high s_true, marginal increase) — restricted to eq/ne only.
    'pp_view_set':       [op.eq, op.ne],
    'pp_seq_set':        [op.eq, op.ne],
    'prep_view_set':     [op.eq, op.ne],
    'prep_seq_set':      [op.eq, op.ne],
    'prep_replica_set':  [op.eq, op.ne],
    'vc_replica_set':    [op.eq, op.ne],
    'vc_inner_last_seq_set': [op.eq, op.ne],
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
    excluded = getattr(protocol, 'get_excluded_type_pairs', lambda: set())()

    predicates: list[Predicate] = []

    for threshold in range(1, 5):
        for left_type, right_type in itertools.product(message_types, repeat=2):
            if (left_type, right_type) in excluded:
                continue
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

# Partition predicates by message type pairs for faster lookup
# This allows us to only evaluate relevant predicates for each message pair
predicates_by_type: dict[tuple[type, type], list[Predicate]] = {}
for predicate in predicates:
    key = (predicate.typeL, predicate.typeR)
    if key not in predicates_by_type:
        predicates_by_type[key] = []
    predicates_by_type[key].append(predicate)

print(f"Predicates partitioned: {len(predicates_by_type)} type pairs")
for key, pred_list in predicates_by_type.items():
    print(f"  {key[0].__name__}->{key[1].__name__}: {len(pred_list)} predicates")


def load_predicate_cache(args):
    """
    Load cached predicate evaluation results from disk.

    Reads a cache file containing predicate evaluation results for a single
    validator node's run. Each line contains: observed observed_true predicate_name

    Args:
        args: Tuple of (run_path, node_id)
              run_path: Path to run directory (e.g., data/buggy-7.../timestamp/)
              node_id: Validator ID (0-6)

    Returns:
        List of CachedPredicate objects, or None if cache doesn't exist
    """
    path, node_id = args
    cache_path = _PROTOCOL.get_cache_path(path, node_id)

    if not os.path.exists(cache_path):
        print(path, 'not cached')
        return None

    opener = gzip.open if cache_path.endswith('.gz') else open
    with opener(cache_path, 'rt') as f:
        cached_predicates = []
        for line in f.readlines():
            # Parse line format: "True/False True/False predicate_description"
            match = cache_re.search(line)
            if match:
                observed, observed_true, name = match.groups()
                cached_predicates.append(
                    CachedPredicate(observed == 'True', observed_true == 'True', name)
                )
        return cached_predicates


def generate_predicate_cache(args):
    """
    Generate and cache predicate evaluation results for a validator node's run.

    This function:
    1. Parses the validator log to extract messages
    2. Filters messages by network partition overlap
    3. Evaluates all predicates on message pairs
    4. Caches results to disk for fast re-loading

    The algorithm evaluates each predicate against all pairs of messages,
    deduplicating messages by content and tracking peer sets.

    Optimizations:
    - Partitions predicates by message type to only evaluate relevant ones
    - Removes predicates from active set after they match (observed_true)
    - Uses message type to select appropriate predicate subset

    Args:
        args: Tuple of (run_path, node_id)
              run_path: Path to run directory (e.g., data/buggy-7.../timestamp/)
              node_id: Validator ID (0-6)

    Returns:
        None (writes cache file as side effect)
    """
    path, node_id = args
    cache_path = _PROTOCOL.get_cache_path(path, node_id)

    # Skip if already cached
    if os.path.exists(cache_path):
        return

    log_path = _PROTOCOL.get_log_path(path, node_id)
    messages = _PROTOCOL.parse_log(log_path)
    messages = _PROTOCOL.filter_messages(messages, node_id)

    _, predicates_by_type = build_predicates(_PROTOCOL)
    active_predicates_by_type: dict = {}
    all_predicate_states = []

    for key, pred_list in predicates_by_type.items():
        states = [PredicateState(pred) for pred in pred_list]
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
    opener = gzip.open if cache_path.endswith('.gz') else open
    with opener(cache_path, 'wt') as f:
        f.writelines(output_lines)
