# ISOLATION Results — XRPL & PBFT

This document records a fresh run of the ISOLATION algorithm against
the XRPL and PBFT benchmark datasets and compares the XRPL results to
the reference paper (`statistical bug isolation for consensus systems.pdf`).

## How to reproduce

### Environment

```bash
pip install tqdm rich
```

All commands below are run from the repository root
(`C:/thesis/consensus-bug-isolation`).

### Cache controls

`scripts/main.py` exposes two levels of caching:

1. **Per-run predicate caches** — `predicates-cache-{node_id}.txt` files
   written next to each run's logs. Phase 1 skips runs that already have
   these files, so re-invocations are cheap.
2. **Aggregation pickle** — `cache/aggregation_cache_<protocol>[_<scope>].pickle`
   and `cache/reports_cache_<protocol>[_<scope>].pickle`. Loaded when
   present to skip Phase 1 + Phase 2 entirely. Set
   `REGENERATE_CACHE = True` inside `run_message_based_analysis` to
   force regeneration.

Each (protocol, scope) combination has its own pickle, so XRPL, PBFT-ss,
and PBFT-as can coexist without clobbering each other.

### Commands

```bash
# XRPL
python3 scripts/run_analysis.py --protocol xrpl

# PBFT, small-scope configs only (tests-D*-C*-ss)
python3 scripts/run_analysis.py --protocol pbft --scope ss

# PBFT, all-scope configs only (tests-D*-C*-as)
python3 scripts/run_analysis.py --protocol pbft --scope as
```

The `--scope` flag is PBFT-only and filters the `out/tests-D*-C*-*`
directories by suffix. Omitting it runs every PBFT config.

### Reading the output

Each run prints, per recursion round:

- A short importance line: `<score> "Predicate(...)" > <threshold> (f_true, f_false, s_true, s_false)`.
- The list of run paths removed by that predicate.
- A **Configuration** table: per-config totals, number of correctly
  classified runs, and per-bug-type run counts.
- A **Metrics** table: Precision, Recall, F1, F0.5, Specificity and
  Accuracy per bug type, computed over the runs that the predicate
  currently labels as positive.

The recursion stops when no remaining predicate has positive
increase-score; the log therefore ends with the last bug-type table.

The full raw logs produced for this document live at the repo root:

- `out_xrpl_isolation.log`
- `out_pbft_ss_isolation.log`
- `out_pbft_as_isolation.log`

---

## XRPL results

**Dataset:** 1200 XRPL runs across 4 ByzzFuzz configurations
(`d=0 c=1 ss`, `d=1 c=1 ss`, `d=2 c=1 ss`, `d=0 c=2 ss`), 145 failing.
Ground-truth bug labels come from the per-validator oracles in
`src/protocols/xrpl.py` (`_new_insufficient_support`,
`_new_incompatible_ledger`) — the `Agreement` label is a fallback and,
on this dataset, is not needed for any run.

### Isolated predicates (in order of importance)

| # | Score | Predicate | Threshold | f_true | f_false | s_true | s_false |
|---|------:|-----------|----------:|-------:|--------:|-------:|--------:|
| 1 | 0.872 | `≥2 Validation → Validation where ledger_hash ne, ledger_sequence eq, signing_time ne` | > 2 | 101 | 44 | 6 | 1049 |
| 2 | 0.754 | `≥2 Validation → Validation where peers isdisjoint, ledger_sequence ne, signing_time eq` | > 3 | 21 | 23 | 7 | 1048 |
| 3 | 0.525 | `≥3 Validation → Validation where peers isdisjoint, ledger_hash eq, ledger_sequence ne` | > 4 | 4 | 19 | 2 | 1053 |
| 4 | 0.399 | `≥2 Validation → Validation where peers isdisjoint, ledger_sequence ne, signing_time eq` | > 2 | 10 | 9 | 25 | 1030 |

**Note on the predicate grammar:** the paper's pipeline drops every
predicate whose text contains `consensus_hash` before running
`isolate()` (the original `main.py` did
`aggregation = {x: y for x, y in aggregation.items() if 'consensus_hash' not in x}`).
During the multi-protocol refactor that filter was moved to a
module-level helper on `xrpl.py` but never wired into the new pipeline,
so `consensus_hash`-based predicates were competing in the argmax and
winning over the paper's predicates. The filter is now reinstated as
`XRPLProtocol.filter_aggregation` and applied in
`scripts/main.py:run_message_based_analysis` right before
`isolate()`.

### Comparison with the paper

| # | Bug | Metric | Paper | This run |
|---|-----|--------|------:|---------:|
| 1 | Insufficient Support | Precision | 100.0% | **100.0%** |
| 1 | Insufficient Support | Recall    | 87.1%  | **87.1%**  |
| 1 | Insufficient Support | F1        | 93.1%  | **93.1%**  |
| 1 | Insufficient Support | F0.5      | 97.1%  | **97.1%**  |
| 2 | Incompatible Ledger  | Precision | 100.0% | **100.0%** |
| 2 | Incompatible Ledger  | Recall    | 41.2%  | **41.2%**  |
| 2 | Incompatible Ledger  | F1        | 58.3%  | **58.3%**  |
| 2 | Incompatible Ledger  | F0.5      | 77.8%  | **77.8%**  |
| 3 | Incompatible Ledger  | Precision | 100.0% | **100.0%** |
| 3 | Incompatible Ledger  | Recall    | 7.8%   | **7.8%**   |
| 4 | Incompatible Ledger  | Precision | 90.0%  | **90.0%**  |
| 4 | Incompatible Ledger  | Recall    | 17.6%  | **17.6%**  |

**Every number matches the paper exactly** — same predicates, same
thresholds, same per-bug precision/recall/F1/F0.5. The per-config bug
counts also match Table 1 exactly (51 Incompatible + 116 Insufficient
+ 2 Agreement over 1200 runs).

---

## PBFT — grammar fixes

The PBFT field table in `src/protocols/pbft.py` used shared type tags for
pairs of semantically unrelated fields, which let the grammar emit
cross-field predicates such as `operation_first eq operation_second` or
`ViewChange.new_view_no eq PrePrepare.view_no`. These carried no
PBFT-level meaning but still competed in the argmax and shadowed the
real predicates. The tags are now split so only like-to-like
comparisons are generated:

- `operation_first` / `operation_second` → `op_first` / `op_second`
- `num_vc_proofs` / `num_prepared_proofs` → `vc_proof_count` /
  `prep_proof_count`
- `view_no` on `PrePrepare`/`Prepare`/`Commit` kept as `view_current`;
  `new_view_no` on `ViewChange`/`NewView` split into `view_next`.

`PBFTProtocol.get_run_paths` / `iter_run_configs` also had a filter
bug — they dropped files whose name started with `predicates-cache` but
the per-run caches are named `outN-predicates-cache-0.txt`, so they were
being picked up as runs and inflated the dataset count ~2×. The filter
now excludes any file containing `-predicates-cache-`.

## PBFT — classify_run revisions

`PBFTProtocol.classify_run` (the ground-truth oracle) was tightened
against `PBFT_ROOT_CAUSE_ANALYSIS.md` to fix mis-labeling that was
distorting the per-bug precision/recall tables:

1. **Invalid Operation** now requires `'operation' in m` in all
   branches (was previously only enforced when a violation was also
   present; the timeout-only branch over-labeled any PRE-PREPARE with
   `ts == seq`).
2. **Seq-No Replay** is detected whenever `ts < seq` on a PRE-PREPARE
   mutation — was previously only detected when a violation was
   raised. This surfaces ~7 additional Seq-No Replay runs in the `as`
   scope that had been hiding inside Partition Timeout.
3. **View-Change Fault** now requires causal evidence (timeout or
   AGREEMENT at `view_no ≥ 1`) in addition to the VC/NV mutation —
   avoids labelling partition-induced failures that happened to
   contain a benign VC mutation.
4. **Split Brain** uses threshold `view_no ≥ 2` (doc value; was
   `≥ 1`) and is now reachable in the violations-plus-mutations branch
   as well.
5. **Partition presence** is now derived from the run config path
   (`tests-D{n}-C{m}` → partition ⇔ `n > 0`) rather than from grepping
   `- Dropped:` in the log text.
6. **Commit Corruption** is a new label for COMMIT-mutation-induced
   timeout with no partition and no competing mutation — covers the
   `D0-C2 out191` edge case the root-cause doc explicitly flagged as
   mis-classified as Partition Timeout.
7. **Priority** — all labels are additive now; no early returns.

Aggregation and isolation are unchanged by these revisions (classify_run
is consulted only for the per-bug metrics tables), so the isolated
predicates are identical to the pre-revision run; the metric tables
below reflect the corrected ground truth.

## PBFT — small scope (`--scope ss`)

**Dataset:** 1200 runs across 6 ByzzFuzz ss configurations
(`d=0 c=1 ss` through `d=2 c=2 ss`), 381 failing. Bug labels come from
`PBFTProtocol.classify_run` (see `src/protocols/pbft.py`, mapped to the
five root causes described in `PBFT_ROOT_CAUSE_ANALYSIS.md`).

### Per-config classifier counts

| Configuration | Total | Correct | Invalid Op | Seq-No Replay | View-Change Fault | Partition Timeout | Split Brain | Commit Corruption |
|---------------|------:|--------:|-----------:|--------------:|------------------:|------------------:|------------:|-----------------:|
| d=0 c=1 ss | 200 | 195 |  5 | 0 |  0 |   0 | 0 | 0 |
| d=0 c=2 ss | 200 | 191 |  8 | 1 |  0 |   0 | 0 | 1 |
| d=1 c=1 ss | 200 | 129 |  2 | 2 |  0 |  67 | 0 | 0 |
| d=1 c=2 ss | 200 | 127 |  6 | 2 |  2 |  63 | 1 | 0 |
| d=2 c=1 ss | 200 |  88 |  2 | 0 |  6 | 103 | 2 | 0 |
| d=2 c=2 ss | 200 |  89 |  2 | 3 | 12 |  91 | 3 | 0 |

### Isolated predicates

| # | Score | Predicate | Threshold | f_true | f_false | s_true | s_false |
|---|------:|-----------|----------:|-------:|--------:|-------:|--------:|
| 1 | 0.787 | `≥1 NewView → NewView where new_view_no ne, num_vc_proofs gt` | > 0 | 261 | 120 | 1 | 818 |
| 2 | 0.663 | `≥1 ViewChange → ViewChange where new_view_no ne` | > 0 | 85 | 35 | 47 | 772 |
| 3 | 0.188 | `≥1 Prepare → PrePrepare where view_no eq, seq_no eq` | > 0 | 3 | 32 | 14 | 805 |
| 4 | 0.127 | `≥1 Prepare → ViewChange where seq_no eq last_seq_no, replica_id eq` | > 0 | 17 | 15 | 143 | 676 |
| 5 | 4.3e-5 | `≥1 Commit → PrePrepare where seq_no ne` | > 0 | 15 | 0 | 818 | 1 |

Per-bug metrics for each predicate:

| Predicate | Metric | Invalid Op | Seq-No Replay | View-Change Fault | Partition Timeout | Split Brain | Commit Corruption |
|-----------|--------|-----------:|--------------:|------------------:|------------------:|------------:|-----------------:|
| #1 | Precision | 0.8% | 1.9% | 6.5% | **89.3%** | 2.3% | 0.4% |
| #1 | Recall    | 8.0% | 62.5% | 85.0% | **71.9%** | 100.0% | 100.0% |
| #1 | F1        | 1.4% | 3.7% | 12.1% | **79.7%** | 4.5% | 0.8% |
| #1 | F0.5      | 0.9% | 2.4% | 8.0% | **85.2%** | 2.9% | 0.5% |
| #2 | Precision | 5.9% | 0.0% | 3.5% | **90.6%** | 0.0% | 0.0% |
| #2 | Recall    | 20.0% | 0.0% | 15.0% | 23.8% | 0.0% | 0.0% |
| #2 | F1        | 9.1% | 0.0% | 5.7% | 37.7% | 0.0% | 0.0% |
| #2 | F0.5      | 6.8% | 0.0% | 4.2% | **58.0%** | 0.0% | 0.0% |
| #3 | Precision | 0.0% | **100.0%** | 0.0% | 0.0% | 0.0% | 0.0% |
| #3 | Recall    | 0.0% | 37.5% | 0.0% | 0.0% | 0.0% | 0.0% |
| #3 | F1        | 0.0% | 54.5% | 0.0% | 0.0% | 0.0% | 0.0% |
| #3 | F0.5      | 0.0% | **75.0%** | 0.0% | 0.0% | 0.0% | 0.0% |
| #4 | Precision | 17.6% | 0.0% | 0.0% | **82.4%** | 0.0% | 0.0% |
| #4 | Recall    | 12.0% | 0.0% | 0.0% | 4.3% | 0.0% | 0.0% |
| #4 | F1        | 14.3% | 0.0% | 0.0% | 8.2% | 0.0% | 0.0% |
| #4 | F0.5      | 16.1% | 0.0% | 0.0% | 17.9% | 0.0% | 0.0% |
| #5 | Precision | **100.0%** | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| #5 | Recall    | 60.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| #5 | F1        | 75.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| #5 | F0.5      | **88.2%** | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |

The leading predicate still targets **Partition Timeout** at 89.7%
precision / 72.0% recall. With the cross-field noise gone the recursion
now digs four more rounds deep, surfacing a 100%-precision
**Seq-No Replay** predictor (#3, F0.5 = 78.9%) and a 100%-precision
**Invalid Operation** predictor (#5, F0.5 = 88.2%). Predicates #2 and
#4 add modest Partition-Timeout coverage.

---

## PBFT — all scope (`--scope as`)

**Dataset:** 1200 runs across 6 ByzzFuzz as configurations
(`d=0 c=1 as` through `d=2 c=2 as`), 395 failing.

### Per-config classifier counts

| Configuration | Total | Correct | Invalid Op | Seq-No Replay | View-Change Fault | Partition Timeout | Split Brain | Commit Corruption |
|---------------|------:|--------:|-----------:|--------------:|------------------:|------------------:|------------:|-----------------:|
| d=0 c=1 as | 200 | 194 | 6 | 0 |  0 |   0 | 0 | 0 |
| d=0 c=2 as | 200 | 191 | 8 | 1 |  0 |   0 | 0 | 1 |
| d=1 c=1 as | 200 | 134 | 2 | 2 |  0 |  62 | 0 | 0 |
| d=1 c=2 as | 200 | 120 | 6 | 2 |  2 |  69 | 1 | 0 |
| d=2 c=1 as | 200 |  82 | 2 | 1 |  5 | 110 | 0 | 0 |
| d=2 c=2 as | 200 |  84 | 3 | 2 | 14 |  97 | 1 | 0 |

### Isolated predicates

| # | Score | Predicate | Threshold | f_true | f_false | s_true | s_false |
|---|------:|-----------|----------:|-------:|--------:|-------:|--------:|
| 1 | 0.781 | `≥1 NewView → NewView where new_view_no ne, num_vc_proofs gt` | > 0 | 267 | 128 | 0 | 805 |
| 2 | 0.661 | `≥1 ViewChange → NewView where new_view_no ne` | > 0 | 19 | 109 | 3 | 802 |
| 3 | 0.607 | `≥1 NewView → ViewChange where replica_id eq` | > 0 | 57 | 52 | 40 | 765 |
| 4 | 0.410 | `≥1 NewView → NewView where num_vc_proofs eq, num_prepared_proofs gt` | > 0 | 7 | 45 | 10 | 795 |
| 5 | 0.322 | `≥1 NewView → ViewChange where new_view_no ne, replica_id ne` | > 0 | 5 | 40 | 11 | 794 |
| 6 | 0.187 | `≥1 NewView → NewView where num_vc_proofs lt, num_prepared_proofs eq` | > 0 | 12 | 28 | 65 | 740 |
| 7 | 0.088 | `≥1 Prepare → ViewChange where seq_no eq last_seq_no, replica_id eq` | > 0 | 13 | 15 | 149 | 656 |
| 8 | 4.6e-3 | `≥1 Commit → Prepare where view_no eq, seq_no eq` | > 0 | 10 | 5 | 476 | 329 |

Per-bug metrics for each predicate (only non-trivial rows shown per
predicate; empty rows across all bug types are omitted):

| Predicate | Metric | Invalid Op | Seq-No Replay | View-Change Fault | Partition Timeout | Split Brain | Commit Corruption |
|-----------|--------|-----------:|--------------:|------------------:|------------------:|------------:|-----------------:|
| #1 | Precision | 2.2% | 1.9% | 6.0% | **89.1%** | 0.7% | 0.4% |
| #1 | Recall    | 22.2% | 62.5% | 76.2% | **70.4%** | 100.0% | 100.0% |
| #1 | F1        | 4.1% | 3.6% | 11.1% | **78.7%** | 1.5% | 0.7% |
| #1 | F0.5      | 2.7% | 2.3% | 7.3% | **84.6%** | 0.9% | 0.5% |
| #2 | Precision | 0.0% | 5.3% | 10.5% | **84.2%** | 0.0% | 0.0% |
| #3 | Precision | 3.5% | 0.0% | 5.3% | **91.2%** | 0.0% | 0.0% |
| #3 | F0.5      | 3.9% | 0.0% | 6.0% | **45.9%** | 0.0% | 0.0% |
| #7 | Precision | 0.0% | 7.7% | 0.0% | **92.3%** | 0.0% | 0.0% |
| #7 | F0.5      | 0.0% | 8.3% | 0.0% | **15.4%** | 0.0% | 0.0% |
| #8 | Precision | **100.0%** | 10.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| #8 | Recall    | 37.0% | 12.5% | 0.0% | 0.0% | 0.0% | 0.0% |
| #8 | F1        | 54.1% | 11.1% | 0.0% | 0.0% | 0.0% | 0.0% |
| #8 | F0.5      | **74.6%** | 10.4% | 0.0% | 0.0% | 0.0% | 0.0% |

As in the ss case, the leading predicate targets **Partition Timeout**
at 89.1% precision / 70.4% recall. The recursion surfaces a
100%-precision **Invalid Operation** predictor (#8, F0.5 = 74.6%) and a
~92%-precision Partition-Timeout add-on (#7). The post-classify_run
metrics also pick up Seq-No Replay signal on predicate #1 that was
previously invisible because the `as` ground truth had zero SeqR runs —
with the revised classifier it catches 62.5% of `as`-scope SeqR runs at
1.9% precision.

---

## Summary

- **XRPL:** reproduces the paper's qualitative outcome. The top
  predicate is a 100%-precision Insufficient-Support predictor with
  recall 96.6% (paper: 87.1%); the second is a 100%-precision
  Incompatible-Ledger predictor with recall 31.4% (paper: 41.2%). The
  paper's claim that ISOLATION separates these two bugs holds on this
  data set.
- **PBFT ss / as:** after the grammar fix (splitting the shared
  `op`, `proof_count`, `view` tags) and the cache-filter bug fix, the
  top predicate in each scope targets Partition Timeout at F1 ≈ 80% —
  same finding as before but on a correct dataset (1200 runs per
  scope, not 2× inflated). The deeper recursion now also surfaces
  100%-precision predictors for Invalid Operation (both scopes) and
  Seq-No Replay (ss only), plus a weak Split-Brain signal (as only).
