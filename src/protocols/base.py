import os
import re
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
    def classify_run(self, run_dir: str) -> str:
        """
        Classify a run into a bug type.

        Args:
            run_dir: Absolute path to the run directory.
        Returns:
            Bug type string ('Incompatible', 'Insufficient', 'Agreement', etc.).
        """

    @abstractmethod
    def get_bug_types(self) -> list[str]:
        """
        Return all possible bug-type labels for this protocol.

        Used by stats() to build the per-bug-type confusion matrix.
        Example (XRPL):  ['Incompatible', 'Insufficient', 'Agreement']
        Example (PBFT):  ['Mutated Operation', 'B', 'C', 'D', 'E']
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

    def get_data_dir(self) -> str:
        """Root directory containing all run data."""
        return 'data'

    def get_run_paths(self) -> list[str]:
        """Discover all run paths from get_data_dir(). Default: XRPL-style directory-per-run."""
        paths = []
        for dirpath, _, filenames in os.walk(self.get_data_dir()):
            if filenames:
                paths.append(dirpath)
        return sorted(paths)

    def get_log_path(self, run_path: str, node_id: int) -> str:
        """Return path to the log file for a given run and node."""
        return os.path.join(run_path, f'validator_{node_id}.txt')

    def get_cache_path(self, run_path: str, node_id: int) -> str:
        """Return path to the predicate cache file for a given run and node."""
        return os.path.join(run_path, f'predicates-cache-{node_id}.txt')

    def iter_run_configs(self):
        """
        Yield (config_label, run_paths) pairs, grouped by configuration.

        Used by stats() to iterate over runs while building the distribution table.
        Default: yields one group per top-level subdirectory in get_data_dir().
        """
        for config in sorted(os.listdir(self.get_data_dir())):
            config_dir = os.path.join(self.get_data_dir(), config)
            if not os.path.isdir(config_dir):
                continue
            run_paths = sorted([
                os.path.join(config_dir, r)
                for r in os.listdir(config_dir)
            ])
            yield config, run_paths