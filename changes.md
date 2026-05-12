# Changes — PBFT Bug Taxonomy Consolidation

## Summary

Merged the PBFT bug classification in `src/protocols/pbft.py` from **6 classes**
to **4 classes**, aligning with the root-cause-oriented taxonomy used in the
original thesis (Winter, 2023).

## Motivation

The thesis groups bugs by **root cause**, not by which message was mutated.
Section 5.3 explicitly merges *Insufficient Support* and *Agreement Violation*
under one cluster because they share the same underlying fault (insufficient
UNL overlap), even though one manifests as a liveness failure and the other as
a safety violation.

The previous PBFT taxonomy was structured along the **mutation source axis**
(which message type was tampered with), which produced over-fine splits:

- **Non-PP Mutation** had no observable signal in the predicate space.
  `Prepare`/`Commit` mutations corrupt fields (typically `digest`) that are
  empty (`""`) in the log format used by this implementation, so no relational
  predicate can witness them. The class had the same symptom as Partition
  Timeout (stall, no violation) and was effectively undetectable through
  predicates.
- **Invalid Operation** and **Seq-No Replay** are both PRE-PREPARE content
  corruptions with the same root-cause family (primary's proposal tampered).

## New taxonomy

| Class | Merges | Root cause |
|---|---|---|
| **Operation Corruption** | Invalid Operation + Seq-No Replay | Primary's PRE-PREPARE proposal content tampered (op or timestamp/seq mismatch) |
| **View-Change Fault** | (unchanged) | View-change protocol corrupted via VC/NV mutation |
| **Quorum Stall** | Partition Timeout + Non-PP Mutation | Quorum cannot form (partition, or non-PP mutation that the predicate space cannot witness) |
| **Split Brain** | (unchanged) | AGREEMENT violation at view_no ≥ 2 — replicas commit conflicting values across views |

## 6 → 4 transformation

| Original | New | Why |
|---|---|---|
| Invalid Operation | **Operation Corruption** | PP-content corruption: the primary's proposed operation is tampered with so replicas reject it as invalid. |
| Seq-No Replay | **Operation Corruption** | Also PP-content corruption: an old request is rebroadcast at a higher slot, so `timestamp < seq-number`. Same root cause family as Invalid Operation (primary's proposal corrupted), just a different surface symptom. The thesis groups by root cause, not by symptom; merging removes a split with no explanatory power. |
| View-Change Fault | **View-Change Fault** | Unchanged. VC/NV mutations corrupt the view-change protocol itself — a structurally distinct fault from PP-content corruption, and the predicate space witnesses it directly via view-number relations. |
| Partition Timeout | **Quorum Stall** | Network partition prevents a quorum from forming → liveness failure (no termination). Manifests as a stall with no safety violation. |
| Non-PP Mutation | **Quorum Stall** | Mutations on Prepare/Commit `digest` fields prevent quorum certificates from forming → also a stall with no safety violation. **Crucially unobservable in this dataset**: the log format emits empty `""` digests, so equality predicates over `digest` cannot fire. The class had the same observable signature as Partition Timeout (stall, no violation) and was effectively undetectable through predicates. Merging into Quorum Stall is honest: the predicate space cannot disentangle the two sub-causes. |
| Split Brain | **Split Brain** | Unchanged. AGREEMENT violation at view ≥ 2 (replicas commit conflicting values across views) is a categorically distinct safety failure with its own predicate witnesses. |

**Net effect**: 6 → 4 classes, with two purely additive merges (IO+SNR; PT+Non-PP). Multi-label runs dropped from 4 → 2 because the two merge groups were also the only sources of overlap labels in the old taxonomy.

## Distribution shift (baseline `out copy/`, 420 failures)

Before:

| Class | Count | % |
|---|---|---|
| Partition Timeout | 267 | 63.6% |
| Non-PP Mutation | 77 | 18.3% |
| Invalid Operation | 46 | 11.0% |
| View-Change Fault | 22 | 5.2% |
| Seq-No Replay | 10 | 2.4% |
| Split Brain | 2 | 0.5% |

After:

Dataset: 2800 runs (14 configs × 200), 2380 correct (85.0%), **420 failures (15.0%)**.

| Bug class | Count | % of failures | % of all runs |
|---|---:|---:|---:|
| Quorum Stall | 344 | 81.9% | 12.3% |
| Operation Corruption | 54 | 12.9% | 1.9% |
| View-Change Fault | 22 | 5.2% | 0.8% |
| Split Brain | 2 | 0.5% | 0.07% |
| **Total failures** | **420** | **100.0%** | **15.0%** |

Multi-label runs: 2 (the rest are single-label).

Multi-label runs dropped from 4 → 2 (the IO+SNR and PT+NPP overlaps collapsed
cleanly into single labels).

## Implications

1. **Quorum Stall is heterogeneous by design.** It bundles partition-only stalls
   with logically distinct non-PP-mutation stalls that the predicate space
   cannot disentangle. Tarantula scores for Quorum Stall will look modest —
   that's a faithful reflection of the predicate space's ceiling, not a
   classifier failure.
2. **Stale downstream artifacts.** The following files reference the old
   6-class labels and need regeneration when next refreshed:
   - `PBFT_COMBINED_ISOLATION_TABLE.md`
   - `PBFT_ROOT_CAUSE_ANALYSIS.md`
   - `PBFT_PER_RUN_ANALYSIS.md`
   - `PBFT_BASELINE_VS_ISOLATION.md`
   - `PBFT_ISOLATION_RESULTS.md`

## Predicate-space gaps (not addressed by this change)

These are **observability** limitations of the log format, not classifier
issues:

- **Empty `digest` field** on PP/Prepare/Commit messages. Adding `digest` to
  `get_fields()` would not help — values are constant `""`, so equality
  predicates cannot fire. Recovering the lost Non-PP Mutation signal would
  require regenerating logs from an instrumented build that emits non-empty
  digests.
- **`(ReplicaCommit, ReplicaCommit)` excluded** at `pbft.py:299`. The canonical
  Split Brain witness (`RC→RC view ne, seq eq, op_first ne`) is suppressed.
  Given Split Brain is only 0.5% of failures in this dataset, re-enabling is
  low priority.

## Files changed

- `src/protocols/pbft.py` — `classify_run()` and `get_bug_types()` updated.
- `scripts/bug_distribution.py` — utility script that prints failure counts per
  class (used to verify the merge).
