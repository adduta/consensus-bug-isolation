"""
Main Analysis Pipeline for Consensus Bug Isolation

# v1
This module orchestrates the two-phase analysis pipeline:

Phase 1 - Cache Generation:
  - Processes validator logs from 7-node consensus network
  - Evaluates predicates on message pairs per node
  - Caches results to predicates-cache-{node_id}.txt files

Phase 2 - Statistical Fault Localization:
  - Loads cached predicate evaluations
  - Aggregates observations across successful and failed runs
  - Uses statistical fault localization (Tarantula-based) to identify suspicious predicates
  - Recursively isolates failure-causing predicates by importance score

# v2 - refactored to use protocol-aware predicate generation
Removed hard-coded XRPL-specific logic and replaced with protocol-aware methods.


Network topology:
- Left partition: validators 0-4
- Right partition: validators 2-6
- Overlap: validators 2-4
"""

import itertools as it
import os
import pickle
import sys
from multiprocessing import Pool
from pathlib import Path
from src.protocols.base import ConsensusProtocol

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tqdm import tqdm

from src.analysis.cache import generate_predicate_cache, load_predicate_cache, set_protocol
from src.analysis.fault_localization import Aggregation, Report, isolate

# Import stats function if needed for analysis
try:
    from scripts.analyze import stats
except ImportError:
    stats = None

def _cache_paths_for(protocol):
    """Derive unique cache paths per protocol/scope so distinct runs don't clobber each other."""
    name = type(protocol).__name__.lower().replace('protocol', '')
    scope = getattr(protocol, 'scope', None)
    suffix = f'_{scope}' if scope else ''
    return (
        f'cache/aggregation_cache_{name}{suffix}.pickle',
        f'cache/reports_cache_{name}{suffix}.pickle',
    )


def process_run_to_report(args):
    path, protocol = args
    """
    Process a single consensus run and convert to a Report object.

    This function:
    1. Loads cached predicate evaluations from all 7 validator nodes
    2. Aggregates predicate observations across nodes
    3. Checks if predicate was observed in left/right network partitions
    4. Determines if run succeeded or failed based on results.txt

    Args:
        path: Path to run directory (e.g., data/buggy-7.../timestamp/)

    Returns:
        Report object with success status and predicate observations,
        or None if cache files are missing
    """
    # Load cached predicates from all validator nodes
    results = list(map(load_predicate_cache, zip(it.repeat(path), range(protocol.get_num_nodes()))))

    # If any node is missing cache, skip this run
    if None in results:
        return None

    # Aggregate predicate observations across nodes
    # Key: predicate string, Value: set of node IDs where predicate was observed true
    aggregated = {}
    for node_id, results_per_node in enumerate(results):
        for result in results_per_node:
            # Initialize entry even if not observed (needed for tracking)
            aggregated.setdefault(str(result), set())
            if result.observed_true:
                aggregated[str(result)].add(node_id)

    # For each predicate, check if it was observed in network partitions
    # Generate observations for different threshold levels (> 0, > 1, > 2, > 3, > 4)
    partition_observations = {}
    for pred, observed_nodes in aggregated.items():
        # Count how many nodes in each partition observed this predicate
        # TODO: should use protocol.wrap_observations()
        # nodes_low = len(observed_nodes.intersection(_SET_LOW))
        # nodes_high = len(observed_nodes.intersection(_SET_HIGH))

        # Check each threshold: predicate observed in > i nodes in at least one partition
        partition_observations.update(protocol.wrap_observations(pred, observed_nodes))

    # Determine if this run succeeded or failed
    successful = protocol.is_successful(path)

    # Extract run name from path (normalize Windows backslashes)
    run_name = path.replace("\\", "/")

    return Report(successful, partition_observations, run_name)


def aggregate_predicate_observations(reports: list[Report], aggregation: dict[str, Aggregation] = {}):
    """
    Aggregate predicate observations across multiple runs.

    Builds a statistical model of each predicate's behavior by categorizing
    observations into four categories:
    - successful_true: Predicate observed in successful run
    - successful_false: Predicate not observed in successful run
    - failure_true: Predicate observed in failed run
    - failure_false: Predicate not observed in failed run

    This aggregation enables statistical fault localization to identify
    predicates correlated with failures.

    Args:
        reports: List of Report objects from consensus runs
        aggregation: Existing aggregation dict to update (for incremental processing)

    Returns:
        Dictionary mapping predicate IDs to Aggregation objects with statistics
    """
    for report in reports:
        for (predicate_id, observed_true) in report.observations.items():
            # Initialize aggregation for this predicate if needed
            if predicate_id not in aggregation:
                aggregation[predicate_id] = Aggregation()

            # Categorize this observation based on success and observation status
            if report.successful and observed_true:
                aggregation[predicate_id].successful_true.add(report.name)
            elif report.successful and not observed_true:
                aggregation[predicate_id].successful_false.add(report.name)
            elif not report.successful and observed_true:
                aggregation[predicate_id].failure_true.add(report.name)
            elif not report.successful and not observed_true:
                aggregation[predicate_id].failure_false.add(report.name)

    return aggregation


class LightweightReport:
    """
    Lightweight version of Report containing only success status and run name.

    Used for memory efficiency during iterative fault isolation, where we don't
    need the full observation data after initial aggregation.
    """

    def __init__(self, successful, name) -> None:
        self.successful = successful
        self.name = name


def run_message_based_analysis(protocol: ConsensusProtocol = None):
    """
    Run message-based consensus-aware analysis pipeline.

    Evaluates predicates on message pairs from validator logs and performs
    statistical fault localization to identify failure-correlated predicates.
    """
    if protocol is None:
        from src.protocols.xrpl import XRPLProtocol
        protocol = XRPLProtocol()

    from src.analysis.cache import set_protocol
    set_protocol(protocol)

    num_nodes = protocol.get_num_nodes()

    # Initialize multiprocessing pool; initializer propagates _PROTOCOL to workers
    pool = Pool(initializer=set_protocol, initargs=(protocol,))

    # Discover all run paths via protocol (handles protocol-specific data directory)
    paths = protocol.get_run_paths()

    reports = []
    aggregation = {}

    aggregation_cache_file, reports_cache_file = _cache_paths_for(protocol)

    # Control whether to regenerate cache or load from pickle
    # Set to False to load cached aggregation (much faster on re-runs)
    REGENERATE_CACHE = False

    if not REGENERATE_CACHE and os.path.exists(aggregation_cache_file) and os.path.exists(reports_cache_file):
        # Load pre-computed aggregation from pickle cache (much faster on re-runs)
        print("Loading cached aggregation...")
        with open(aggregation_cache_file, 'rb') as handle:
            aggregation = pickle.load(handle)
        with open(reports_cache_file, 'rb') as handle:
            reports = pickle.load(handle)

    else:
        # Phase 1: Generate predicate cache files for all runs
        print("Phase 1: Generating predicate caches...")

        # Prepare cache generation tasks: (path, node_id) for all nodes per run
        cache_tasks = [(path, node_id) for path in paths for node_id in range(num_nodes)]

        # Parallelize cache generation across all nodes and runs
        list(tqdm(
            pool.imap_unordered(generate_predicate_cache, cache_tasks),
            total=len(cache_tasks),
            desc="Generating cache"
        ))

        # Phase 2: Load caches and aggregate observations
        print("\nPhase 2: Aggregating observations...")

        for report in tqdm(
            pool.imap_unordered(process_run_to_report, [(path, protocol) for path in paths]),
            total=len(paths),
            desc="Generating reports"
        ):
            if report is not None:
                # Create lightweight report for memory efficiency
                reports.append(LightweightReport(report.successful, report.name))
                # Aggregate observations incrementally
                aggregate_predicate_observations([report], aggregation)

        # Save aggregation to disk for fast re-loading
        os.makedirs(os.path.dirname(aggregation_cache_file), exist_ok=True)
        with open(aggregation_cache_file, 'wb') as handle:
            pickle.dump(aggregation, handle, protocol=pickle.HIGHEST_PROTOCOL)
        with open(reports_cache_file, 'wb') as handle:
            pickle.dump(reports, handle, protocol=pickle.HIGHEST_PROTOCOL)

    pool.close()
    pool.terminate()

    # Apply protocol-specific aggregation filter (e.g. XRPL drops consensus_hash
    # predicates to match the original paper's pipeline).
    aggregation = protocol.filter_aggregation(aggregation)

    # Phase 3: Perform statistical fault localization
    print("\nPhase 3: Isolating failure-causing predicates...")
    isolate(reports, aggregations=aggregation, stats_fn=lambda filters: stats(filters, protocol=protocol))


if __name__ == '__main__':
    run_message_based_analysis()
