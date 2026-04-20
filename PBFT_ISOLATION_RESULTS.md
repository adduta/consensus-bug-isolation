# PBFT ISOLATION Results

## Setup

We extended the ISOLATION algorithm from the XRPL paper to PBFT with the following adaptations:

### Per-Replica Inboxes (from Paper Section 3.2, Algorithms 1-2)
PBFT logs contain `Sent: X -> Y` per-recipient deliveries with `Dropped: X -> Y` for lost messages.
Instead of treating the log as a single message stream, we parse **per-replica inboxes** (4 replicas),
giving each replica a different view of what messages it received. This aligns with the paper's
Algorithm 1 which iterates over each process's local trace independently.

### Tolerance Dimension
Following Algorithm 1, each predicate is evaluated at tolerance levels > 0 through > 3.
A predicate is true for a run at tolerance `t` only if more than `t` replicas observed it true.

### Message Types and Predicate Grammar
Six PBFT message types: PrePrepare, Prepare, Commit, ViewChange, NewView, ReplicaCommit.
Fields compared: `view_no`, `seq_no`, `operation_first`, `operation_second`, `timestamp`, `replica_id`, `digest`,
`new_view_no`, `last_seq_no`, `num_vc_proofs`, `num_prepared_proofs`.

Excluded type pair: ReplicaCommit -> ReplicaCommit (self-comparisons add noise without explanatory value).

### Dataset
1200 runs per scope (6 configs x 200 runs), two scopes: SS (small scope) and AS (all scope).

## Bug Type Distribution

| Bug Type | SS | AS |
|---|---|---|
| Correct | 819 | 805 |
| Partition Timeout (D) | 324 | 338 |
| Invalid Operation (A) | 25 | 27 |
| View-Change Fault (C) | 20 | 21 |
| Seq-No Replay (B) | 8 | 8 |
| Split Brain (E) | 6 | 2 |
| Commit Corruption | 1 | 1 |
| **Total failures** | **381** | **395** |

Partition Timeout dominates at ~85% of failures.

## ISOLATION Results — SS Scope (11 iterations)

| Iter | Predicate | Tol. | #Runs | Tarantula | Best Bug | P | R |
|------|-----------|------|-------|-----------|----------|---|---|
| 1 | NV→NV view_next ne, vc_proofs gt | >0 | 261 | 0.787 | PT (residual) | 89.3% | 71.9% |
| **2** | **PP→RC view eq, seq eq, op_first ne** | **>0** | **24** | **0.754** | **Invalid Op** | **87.5%** | **84.0%** |
| 3 | VC→VC new_view ne | >0 | 81 | 0.682 | PT | 95.1% | 23.8% |
| 4 | PP→Prepare view ne, seq gt | >3 | 3 | 0.389 | PT | 100% | 0.9% |
| 5 | RC→Commit view ne, seq gt | >0 | 18 | 0.359 | PT | 88.2% | 4.6% |
| 6 | RC→Prepare view eq, seq gt | >2 | 5 | 0.201 | Mixed | 80.0% | 1.2% |
| 7 | PP→RC seq gt, op_first ne | >2 | 4 | 0.155 | PT | 100% | 0.9% |
| 8 | Prepare→PP view eq, seq eq | >0 | 2 | 0.153 | PT | 100% | 0.6% |
| 9 | RC→Prepare view eq, seq gt | >2 | 2 | 0.082 | PT | 100% | 0.6% |
| 10 | RC→VC seq ne last_seq | >0 | 8 | 0.082 | PT | 100% | 2.5% |
| 11 | RC→Prepare view eq, seq ne | >3 | 2 | 0.001 | PT | 100% | 0.6% |

Iteration 1 absorbs 261 of 381 failures (68.5%). The absorbed runs include:
- PT: R=71.9%, VCF: R=85.0%, SeqNo: R=62.5%, SB: R=100%, CC: R=100%

## ISOLATION Results — AS Scope (12 iterations)

| Iter | Predicate | Tol. | #Runs | Tarantula | Best Bug | P | R |
|------|-----------|------|-------|-----------|----------|---|---|
| 1 | NV→Commit () | >3 | 268 | 0.781 | PT (residual) | 89.6% | 71.0% |
| 2 | VC→VC new_view ne | >3 | 18 | 0.653 | VCF | 16.7% | 14.3% |
| **3** | **PP→RC view eq, seq eq, op_first ne** | **>0** | **11** | **0.647** | **Invalid Op** | **100%** | **40.7%** |
| 4 | PP→RC seq gt, op_first ne | >1 | 30 | 0.627 | PT | 90.0% | 8.0% |
| 5 | Commit→PP seq eq | >0 | 12 | 0.554 | PT | 91.7% | 3.3% |
| 6 | VC→VC new_view ne | >0 | 26 | 0.423 | PT | 92.3% | 7.1% |
| 7 | NV→VC new_view eq | >2 | 4 | 0.245 | PT | 100% | 1.2% |
| 8 | NV→NV vc_proofs eq, prep_proofs lt | >2 | 2 | 0.250 | PT | 100% | 0.6% |
| 9 | RC→Commit view eq, seq gt | >2 | 4 | 0.130 | PT | 100% | 1.2% |
| 10 | RC→VC seq ne last_seq | >1 | 9 | 0.078 | PT | 100% | 2.7% |
| 11 | Prepare→VC seq eq last_seq, rid eq | >1 | 2 | 0.001 | SeqNo | 50.0% | 12.5% |
| 12 | Commit→Prepare view eq, seq ne | >3 | 9 | 0.001 | Mixed | — | — |

## Key Findings

### Successfully Detected: Invalid Operation (Bug A)
The predicate **`PP→RC view eq, seq eq, op_first ne`** at tolerance >0 cleanly isolates Invalid Operation:
- **SS**: P=87.5%, R=84.0% (24 runs, s_true=0 — never fires in successful runs)
- **AS**: P=100%, R=40.7% (11 runs, s_true=0)

This is a genuine **causal predicate**: it says "the PrePrepare operation differs from what was committed at the same view and sequence number" — directly capturing the Byzantine leader's operation mutation.

### Residual Class: Partition Timeout (Bug D)
Partition Timeout (85% of failures) is correctly absorbed as the residual class, analogous to XRPL's "Insufficient Support" bug.
PT is a **liveness failure caused by network topology**, not message content corruption. The predicate grammar compares scalar fields between message pairs and cannot express "not enough messages arrived." This is a fundamental expressiveness limitation, not a methodology failure.

### Not Detected

| Bug Type | # Runs | Why Not Detected |
|---|---|---|
| Seq-No Replay (B) | 8 | Too few samples for statistical separation. The seq mutation (`timestamp < seq_no`) is expressible but 8 runs cannot overcome the PT noise floor. |
| Split Brain (E) | 2-6 | Too few samples. The causal predicate (`RC→RC seq eq, op ne` — different replicas committed different values) is excluded (RC→RC removed). Even if included, 2-6 runs is statistically insufficient. |
| Commit Corruption | 1 | Single sample — impossible to isolate statistically. |
| View-Change Fault (C) | 20-21 | Partially detected (AS iter 2: VCF P=16.7%), but mostly absorbed by iteration 1. VCF causes the same view-change symptoms as PT, making statistical separation difficult. |

### Comparison with XRPL Results

| Aspect | XRPL | PBFT |
|---|---|---|
| Dominant residual | Insufficient Support (87.7%) | Partition Timeout (85.1%) |
| Clean causal predicate | VAL→VAL ledger ne, seq eq, time ne (P=100% R=87.1%) | PP→RC view eq, seq eq, op_first ne (P=87.5-100% R=40.7-84.0%) |
| Bug types isolated | 3 (Insufficient, Incompatible, Agreement) | 2 (PT as residual, Invalid Operation) |
| Total predicates found | 8 | 11-12 |
| Methodology adaptation | 7 nodes, 2 overlapping partitions | 4 replicas as per-process inboxes, tolerance 0-3 |
