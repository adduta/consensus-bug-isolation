# PBFT Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the PRED-based baseline statistical bug isolation method for PBFT, mirroring what already exists for XRPL, so the two approaches (baseline vs ISOLATION) can be compared for PBFT just as they are for XRPL in the thesis.

**Architecture:** The existing `scripts/baseline.py` is hardcoded for XRPL (walks `data/`, reads `results.txt`, iterates 7 `validator_{i}.txt` files). We refactor it to be protocol-aware by adding a `parse_baseline_observations()` method to the protocol classes. PBFT logs in `out copy/` already contain `PRED BRANCH`/`PRED WHILE` annotations with per-replica identifiers (R0-R3). The baseline parses these, aggregates per-replica observations with OR logic, and feeds them through the same `isolate()` + `stats()` pipeline.

**Tech Stack:** Python 3, existing `src/analysis/fault_localization.py` (Tarantula), `rich` for output tables.

---

## Key Differences: XRPL vs PBFT Baseline

| Aspect | XRPL | PBFT |
|--------|------|------|
| Data dir | `data/` | `out copy/` |
| Run structure | Directory per run with `validator_{i}.txt` files | Single `.txt` file per run |
| Num nodes | 7 validators | 4 replicas |
| PRED format | `PRED <id> <0\|1>` | `PRED BRANCH <file>:<line> R<id> <0\|1>` |
| Success check | `results.txt` contains "reason: all committed" | No "Violation of" AND no "Reached test duration" in log |
| Configs | `buggy-7-{c}-{d}-6-small-scope/` dirs | `tests-D{0-2}-C{0-2}-{ss\|as}/` dirs |

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `src/protocols/base.py` | Modify | Add abstract `parse_baseline_observations()` method |
| `src/protocols/xrpl.py` | Modify | Implement `parse_baseline_observations()` extracting current XRPL logic from baseline.py |
| `src/protocols/pbft.py` | Modify | Implement `parse_baseline_observations()` for PBFT PRED format; add `get_baseline_data_dir()` returning `'out copy'` |
| `scripts/baseline.py` | Modify | Refactor to use protocol methods instead of hardcoded XRPL logic |
| `tests/test_pbft_baseline.py` | Create | Tests for PBFT PRED parsing and baseline pipeline |

---

### Task 1: Add `parse_baseline_observations()` to the Base Protocol

**Files:**
- Modify: `src/protocols/base.py:52-54` (after `is_successful`)

- [ ] **Step 1: Add the abstract method to ConsensusProtocol**

Add after the `is_successful` method (around line 53):

```python
@abstractmethod
def parse_baseline_observations(self, run_path: str) -> tuple[bool, dict[str, bool], str] | None:
    """
    Parse PRED annotations from a run's log files for the baseline pipeline.

    Returns:
        Tuple of (is_successful, observations_dict, run_name), or None if
        the run should be skipped.
        observations_dict maps predicate IDs like "BRANCH File.java:123 is true"
        to bool values, aggregated across all nodes/replicas with OR logic.
    """
```

- [ ] **Step 2: Verify no import errors**

Run: `.venv/bin/python -c "from src.protocols.base import ConsensusProtocol; print('OK')"`
Expected: OK (abstract class doesn't need implementation yet)

- [ ] **Step 3: Commit**

```bash
git add src/protocols/base.py
git commit -m "feat(base): add abstract parse_baseline_observations method"
```

---

### Task 2: Implement `parse_baseline_observations()` for XRPL

This extracts the existing XRPL PRED-parsing logic from `baseline.py` into the XRPL protocol class.

**Files:**
- Modify: `src/protocols/xrpl.py`

- [ ] **Step 1: Read `src/protocols/xrpl.py` to find the right insertion point**

Read the file to understand its current structure before modifying.

- [ ] **Step 2: Implement `parse_baseline_observations` in XRPLProtocol**

Add this method to the `XRPLProtocol` class:

```python
def parse_baseline_observations(self, run_path: str) -> tuple[bool, dict[str, bool], str] | None:
    """Parse PRED annotations from XRPL validator logs."""
    import os

    # Determine success from results.txt
    with open(os.path.join(run_path, 'results.txt'), 'r') as f:
        correct = 'reason: all committed' in f.read()

    observations = {}

    # Read PRED annotations from all 7 validator logs
    for i in range(self.get_num_nodes()):
        log_path = os.path.join(run_path, f'validator_{i}.txt')
        if not os.path.exists(log_path):
            continue
        with open(log_path, 'r') as f:
            for line in f.readlines():
                if not line.startswith('PRED'):
                    continue

                line = line.strip()[5:]  # Remove "PRED " prefix
                pred_id = " ".join(line.split(" ")[:-1])

                # Skip malformed PRED lines
                if 'PRED' in pred_id:
                    continue

                observation = line.split(" ")[-1] == "1"

                if pred_id not in observations:
                    observations[pred_id + ' is true'] = observation
                    observations[pred_id + ' is false'] = not observation
                else:
                    # Aggregate across nodes with OR logic
                    observations[pred_id + ' is true'] = observation or observations[pred_id + ' is true']
                    observations[pred_id + ' is false'] = (not observation) or observations[pred_id + ' is false']

    run_name = run_path.split('/')[-1]
    return (correct, observations, run_name)
```

- [ ] **Step 3: Verify import works**

Run: `.venv/bin/python -c "from src.protocols.xrpl import XRPLProtocol; p = XRPLProtocol(); print('OK')"`
Expected: OK

- [ ] **Step 4: Commit**

```bash
git add src/protocols/xrpl.py
git commit -m "feat(xrpl): implement parse_baseline_observations"
```

---

### Task 3: Implement `parse_baseline_observations()` for PBFT

**Files:**
- Modify: `src/protocols/pbft.py`

- [ ] **Step 1: Write a test for PBFT PRED parsing**

Create `tests/test_pbft_baseline.py`:

```python
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.protocols.pbft import PBFTProtocol


def test_parse_baseline_observations_successful_run(tmp_path):
    """A run with no violations should be marked successful."""
    log = tmp_path / "out1.txt"
    log.write_text(
        "PRED BRANCH DefaultReplica.java:282 R0 0\n"
        "PRED BRANCH DefaultReplica.java:282 R1 1\n"
        "PRED BRANCH DefaultReplica.java:393 R0 1\n"
        "PRED WHILE PropertyChecker.java:119 R2 0\n"
        "Task completed.\n"
    )
    proto = PBFTProtocol()
    result = proto.parse_baseline_observations(str(log))
    assert result is not None
    success, obs, name = result
    assert success is True
    # "BRANCH DefaultReplica.java:282" observed true by R1 → "is true" should be True
    assert obs["BRANCH DefaultReplica.java:282 is true"] is True
    # R0 observed it as false → "is false" should also be True (OR logic)
    assert obs["BRANCH DefaultReplica.java:282 is false"] is True
    # "BRANCH DefaultReplica.java:393" only observed as true
    assert obs["BRANCH DefaultReplica.java:393 is true"] is True
    assert obs["BRANCH DefaultReplica.java:393 is false"] is False
    assert name == "out1.txt"


def test_parse_baseline_observations_failing_run(tmp_path):
    """A run with a violation should be marked as failed."""
    log = tmp_path / "out42.txt"
    log.write_text(
        "PRED BRANCH DefaultReplica.java:282 R0 1\n"
        "Violation of AGREEMENT at Replica: 0 viewNo: 0 seqNo: 1\n"
        "Task completed.\n"
    )
    proto = PBFTProtocol()
    result = proto.parse_baseline_observations(str(log))
    assert result is not None
    success, obs, name = result
    assert success is False
    assert name == "out42.txt"


def test_parse_baseline_observations_timeout_run(tmp_path):
    """A run that times out should be marked as failed."""
    log = tmp_path / "out99.txt"
    log.write_text(
        "PRED BRANCH DefaultReplica.java:282 R0 0\n"
        "Reached test duration\n"
    )
    proto = PBFTProtocol()
    result = proto.parse_baseline_observations(str(log))
    success, obs, name = result
    assert success is False


def test_parse_baseline_or_aggregation_across_replicas(tmp_path):
    """OR aggregation: if any replica observes true, 'is true' should be True."""
    log = tmp_path / "out1.txt"
    log.write_text(
        "PRED BRANCH DefaultReplica.java:100 R0 0\n"
        "PRED BRANCH DefaultReplica.java:100 R1 0\n"
        "PRED BRANCH DefaultReplica.java:100 R2 0\n"
        "PRED BRANCH DefaultReplica.java:100 R3 1\n"
        "Task completed.\n"
    )
    proto = PBFTProtocol()
    success, obs, name = proto.parse_baseline_observations(str(log))
    # R3 observed true → "is true" = True; R0-R2 observed false → "is false" = True
    assert obs["BRANCH DefaultReplica.java:100 is true"] is True
    assert obs["BRANCH DefaultReplica.java:100 is false"] is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_pbft_baseline.py -v`
Expected: FAIL (method not implemented)

- [ ] **Step 3: Implement `parse_baseline_observations` in PBFTProtocol**

Add to `PBFTProtocol` class in `src/protocols/pbft.py`, and also add a `get_baseline_data_dir()` method:

```python
def get_baseline_data_dir(self) -> str:
    """Data directory containing PBFT logs with PRED annotations."""
    return 'out copy'

def parse_baseline_observations(self, run_path: str) -> tuple[bool, dict[str, bool], str] | None:
    """Parse PRED BRANCH/WHILE annotations from a single PBFT log file.

    PBFT PRED format: PRED BRANCH <file>:<line> R<id> <0|1>
                      PRED WHILE  <file>:<line> R<id> <0|1>

    Aggregates observations across all replicas using OR logic (same
    approach as the XRPL baseline for its 7 validators).
    """
    with open(run_path, 'r') as f:
        text = f.read()

    # Determine success (same logic as is_successful)
    correct = 'Violation of' not in text and 'Reached test duration' not in text

    observations: dict[str, bool] = {}

    for line in text.splitlines():
        if not line.startswith('PRED '):
            continue

        # Format: "PRED BRANCH DefaultReplica.java:282 R0 0"
        #     or: "PRED WHILE  PropertyChecker.java:119 R2 1"
        parts = line.strip().split()
        # parts: ['PRED', 'BRANCH', 'DefaultReplica.java:282', 'R0', '0']
        if len(parts) < 5:
            continue

        # Predicate ID = type + location (e.g. "BRANCH DefaultReplica.java:282")
        pred_id = parts[1] + ' ' + parts[2]
        observation = parts[4] == '1'

        key_true = pred_id + ' is true'
        key_false = pred_id + ' is false'

        if key_true not in observations:
            observations[key_true] = observation
            observations[key_false] = not observation
        else:
            # OR aggregation across replicas
            observations[key_true] = observation or observations[key_true]
            observations[key_false] = (not observation) or observations[key_false]

    run_name = os.path.basename(run_path)
    return (correct, observations, run_name)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_pbft_baseline.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/protocols/pbft.py tests/test_pbft_baseline.py
git commit -m "feat(pbft): implement parse_baseline_observations for PRED parsing"
```

---

### Task 4: Add `get_baseline_run_paths()` to PBFTProtocol

The existing `get_run_paths()` reads from `out/`. The baseline needs to read from `out copy/`. We add a dedicated method.

**Files:**
- Modify: `src/protocols/base.py`
- Modify: `src/protocols/pbft.py`

- [ ] **Step 1: Add default `get_baseline_run_paths()` to base class**

Add to `ConsensusProtocol` in `src/protocols/base.py`:

```python
def get_baseline_run_paths(self) -> list[str]:
    """Run paths for the baseline pipeline. Defaults to get_run_paths()."""
    return self.get_run_paths()
```

- [ ] **Step 2: Override in PBFTProtocol**

Add to `PBFTProtocol` in `src/protocols/pbft.py`:

```python
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
            if f.endswith('.txt'):
                paths.append(os.path.join(config_dir, f))
    return paths
```

- [ ] **Step 3: Add `iter_baseline_run_configs()` to PBFTProtocol**

The `stats()` function calls `protocol.iter_run_configs()` to build the distribution table. For the baseline, this needs to iterate over `out copy/` instead of `out/`. Add:

```python
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
            if f.endswith('.txt')
        ])
        label = f'd={d} c={c} {scope}'.rstrip()
        yield label, run_paths
```

Also add a default in `base.py`:

```python
def iter_baseline_run_configs(self):
    """Yield (config_label, run_paths) for baseline pipeline. Defaults to iter_run_configs()."""
    return self.iter_run_configs()
```

- [ ] **Step 4: Verify import**

Run: `.venv/bin/python -c "from src.protocols.pbft import PBFTProtocol; p = PBFTProtocol(); print(len(p.get_baseline_run_paths()), 'runs')"`
Expected: `2800 runs`

- [ ] **Step 5: Commit**

```bash
git add src/protocols/base.py src/protocols/pbft.py
git commit -m "feat(pbft): add get_baseline_run_paths and iter_baseline_run_configs"
```

---

### Task 5: Refactor `baseline.py` to Be Protocol-Aware

**Files:**
- Modify: `scripts/baseline.py`

- [ ] **Step 1: Rewrite `run_baseline_analysis` to use protocol methods**

Replace the body of `scripts/baseline.py` with:

```python
#!/usr/bin/env python3
"""
Baseline PRED-based Analysis Pipeline

This module implements the baseline approach that reads predicate observations
directly from PRED annotations in validator/replica logs (as opposed to the
message-based approach that evaluates predicates on message pairs).

Both approaches are equal, first-class approaches for consensus bug isolation:
- Baseline (this file): Uses pre-annotated PRED observations
- Message-based (main.py): Evaluates predicates on message pairs

This baseline uses the same statistical fault localization algorithm from
src/analysis/fault_localization.py but gets observations from PRED markers.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.analysis.fault_localization import isolate, Report
from scripts.analyze import stats


def run_baseline_analysis(protocol=None):
    """
    Run baseline PRED-based analysis pipeline.

    Reads PRED annotations from logs and performs statistical
    fault localization to identify failure-correlated predicates.

    Works for any protocol that implements parse_baseline_observations().
    """
    if protocol is None:
        from src.protocols.xrpl import XRPLProtocol
        protocol = XRPLProtocol()

    reports = []

    # Use protocol-specific baseline run discovery
    run_paths = protocol.get_baseline_run_paths()

    for run_path in run_paths:
        result = protocol.parse_baseline_observations(run_path)
        if result is None:
            continue
        correct, observations, run_name = result
        reports.append(Report(correct, observations, run_name))

    # Perform statistical fault localization using shared algorithm
    print(f"\nProcessed {len(reports)} runs with PRED annotations")
    print("Starting statistical fault localization...\n")
    isolate(reports, stats_fn=lambda filters: stats(
        filters, protocol=protocol, use_baseline_configs=True
    ))


if __name__ == '__main__':
    run_baseline_analysis()
```

- [ ] **Step 2: Update `stats()` in `analyze.py` to support baseline config iteration**

Add a `use_baseline_configs` parameter to `stats()` in `scripts/analyze.py`. Find the line:

```python
def stats(filters, protocol=None, return_agg=False):
```

Change to:

```python
def stats(filters, protocol=None, return_agg=False, use_baseline_configs=False):
```

And change the iteration line from:

```python
for config_label, run_paths in protocol.iter_run_configs():
```

To:

```python
config_iter = protocol.iter_baseline_run_configs() if use_baseline_configs else protocol.iter_run_configs()
for config_label, run_paths in config_iter:
```

- [ ] **Step 3: Verify XRPL baseline still works**

Run: `.venv/bin/python scripts/run_analysis.py --protocol xrpl --baseline`
Expected: Same 3 predicates and metrics as before (View.cpp:655, Consensus.h:732, LedgerTiming.h:110). Verify the super-bug predicate `View.cpp:655 is false` shows 142 runs and Precision ~34.5% for Incompatible.

- [ ] **Step 4: Commit**

```bash
git add scripts/baseline.py scripts/analyze.py
git commit -m "refactor(baseline): make protocol-aware using parse_baseline_observations"
```

---

### Task 6: Run the PBFT Baseline and Capture Results

**Files:**
- No new files, just running the pipeline

- [ ] **Step 1: Run the PBFT baseline**

Run: `.venv/bin/python scripts/run_analysis.py --protocol pbft --baseline`

This will:
1. Parse PRED annotations from all 2800 runs in `out copy/`
2. Build Reports with per-predicate observations
3. Run Tarantula-based statistical fault localization
4. Print the distribution table and per-predicate precision/recall/F-scores

- [ ] **Step 2: Inspect the output**

Check:
- How many runs were processed (should be ~2800)
- How many predicates were identified by the isolation algorithm
- The precision/recall/F-scores for each bug type
- Compare with the ISOLATION results from `PBFT_COMBINED_ISOLATION_TABLE.md`

- [ ] **Step 3: Try scoped runs if needed**

Run with scope filters to see if certain configs produce cleaner results:

```bash
.venv/bin/python scripts/run_analysis.py --protocol pbft --baseline --scope ss
.venv/bin/python scripts/run_analysis.py --protocol pbft --baseline --scope as
```

- [ ] **Step 4: Commit any final adjustments**

```bash
git add -A
git commit -m "feat(pbft): baseline results captured"
```

---

## Summary

| Task | What | Key Change |
|------|------|-----------|
| 1 | Abstract method in base | `parse_baseline_observations()` signature |
| 2 | XRPL implementation | Extract existing logic from baseline.py |
| 3 | PBFT implementation | Parse `PRED BRANCH/WHILE <file>:<line> R<id> <0\|1>` |
| 4 | Baseline run discovery | `get_baseline_run_paths()`, `iter_baseline_run_configs()` for `out copy/` |
| 5 | Refactor baseline.py | Protocol-aware, delegates to protocol methods |
| 6 | Run and capture results | Execute PBFT baseline, compare with ISOLATION |
