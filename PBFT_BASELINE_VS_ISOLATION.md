# PBFT: Baseline vs ISOLATION Comparison

## Dataset

2800 runs total (14 configs x 200 runs), 1805 correct, 995 failures.

| Bug Type | #Runs |
|---|---|
| Correct Execution | 1805 |
| Partition Timeout | 885 |
| Invalid Operation | 51 |
| View-Change Fault | 41 |
| Seq-No Replay | 18 |
| Split Brain | 2 |
| Commit Corruption | 2 |

Partition Timeout dominates at ~89% of failures.

---

## Baseline Results (PRED branch predicates)

Instrumented files: `DefaultReplica.java` only.

9 predicates identified across 9 isolation iterations.

| # | Predicate | #Runs | Importance | Best Bug | P | R | F1 | F0.5 |
|---|-----------|-------|-----------|----------|---|---|----|----|
| 1 | `DefaultReplica.java:292 is true` | 649 | 0.650 | Partition Timeout | 91.7% | 67.2% | 77.6% | 85.5% |
| 2 | `DefaultReplica.java:94 is true` | 21 | 0.577 | Partition Timeout | 85.7% | 2.0% | 4.0% | 9.3% |
| 3 | `DefaultReplica.java:319 is true` | 54 | 0.528 | Partition Timeout | 83.3% | 5.1% | 9.6% | 20.4% |
| 4 | `DefaultReplica.java:621 is false` | 56 | 0.390 | Partition Timeout | 89.3% | 5.6% | 10.6% | 22.5% |
| 5 | `DefaultReplica.java:173 is true` | 190 | 0.343 | Partition Timeout | 91.6% | 19.7% | 32.4% | 52.9% |
| 6 | `WHILE DefaultReplica.java:684 is false` | 2 | 0.055 | View-Change Fault | 50.0% | 2.4% | 4.7% | 10.2% |
| 7 | `WHILE DefaultReplica.java:684 is true` | 2 | 0.001 | Partition Timeout | 100.0% | 0.2% | 0.5% | 1.1% |
| 8 | `DefaultReplica.java:393 is true` | 21 | 0.0003 | Invalid Operation | 95.2% | 39.2% | 55.6% | 74.1% |

### Per-Bug Metrics for Key Baseline Predicates

**Iteration 1** — `DefaultReplica.java:292 is true` (649 runs):

| Bug Type | Precision | Recall | F1 | F0.5 |
|----------|-----------|--------|----|----|
| Partition Timeout | 91.7% | 67.2% | 77.6% | 85.5% |
| Invalid Operation | 2.2% | 27.5% | 4.0% | 2.6% |
| View-Change Fault | 4.3% | 68.3% | 8.1% | 5.3% |
| Seq-No Replay | 1.7% | 61.1% | 3.3% | 2.1% |

**Iteration 8** — `DefaultReplica.java:393 is true` (21 runs, late-stage):

| Bug Type | Precision | Recall | F1 | F0.5 |
|----------|-----------|--------|----|----|
| Invalid Operation | 95.2% | 39.2% | 55.6% | 74.1% |
| View-Change Fault | 4.8% | 2.4% | 3.2% | 4.0% |

**Iteration 3** — `DefaultReplica.java:319 is true` (54 runs):

| Bug Type | Precision | Recall | F1 | F0.5 |
|----------|-----------|--------|----|----|
| Partition Timeout | 83.3% | 5.1% | 9.6% | 20.4% |
| Seq-No Replay | 13.0% | 38.9% | 19.4% | 15.0% |

---

## ISOLATION Results (message-based predicates, combined SS+AS)

14 predicates identified across 14 isolation iterations. Top 4 shown.

| # | Predicate | Tol. | #Runs | Importance | Best Bug | P | R | F1 | F0.5 |
|---|-----------|------|-------|-----------|----------|---|---|----|----|
| 1 | `NV->NV new_view ne, vc_proofs gt` | >0 | 661 | 0.778 | Partition Timeout | 91.1% | 72.4% | 80.7% | 86.6% |
| **2** | **`PP->RC view eq, seq eq, op_first ne`** | **>0** | **36** | **0.732** | **Invalid Operation** | **88.9%** | **61.5%** | **72.7%** | **81.6%** |
| 3 | `VC->VC new_view ne` | >3 | 48 | 0.691 | Partition Timeout | 91.7% | 5.3% | 10.0% | 21.5% |
| 4 | `PP->RC view eq, seq lt` | >3 | 55 | 0.662 | Partition Timeout | 96.4% | 6.4% | 12.0% | 25.2% |

### Per-Scope Invalid Operation Detail

| Scope | Predicate | P | R | s_true |
|-------|-----------|---|---|--------|
| SS | `PP->RC view eq, seq eq, op_first ne` >0 | 87.5% | 84.0% | 0 |
| AS | `PP->RC view eq, seq eq, op_first ne` >0 | 100.0% | 40.7% | 0 |

---

## Head-to-Head Comparison

### Partition Timeout (dominant class, ~89% of failures)

| Metric | Baseline | ISOLATION |
|--------|----------|-----------|
| Predicate | `DefaultReplica.java:292 is true` | `NV->NV new_view ne, vc_proofs gt` >0 |
| #Runs absorbed | 649 | 661 |
| Precision | 91.7% | 91.1% |
| Recall | 67.2% | 72.4% |
| **F1** | 77.6% | **80.7%** |
| **F0.5** | 85.5% | **86.6%** |
| Interpretability | Branch condition taken; no root-cause insight | "NewView messages disagree on view number with escalating VC proofs" — directly explains view-change divergence |

Both methods perform similarly on Partition Timeout because it's a **liveness** failure driven by network topology, not message content corruption. Neither method can express "not enough messages arrived," so both act as residual absorbers. ISOLATION has a slight edge in F1 (+3.1pp) and provides a semantically meaningful predicate.

### Invalid Operation (most differentiating bug)

| Metric | Baseline | ISOLATION |
|--------|----------|-----------|
| Predicate | `DefaultReplica.java:393 is true` (iter 8) | `PP->RC view eq, seq eq, op_first ne` >0 (iter 2) |
| Isolation step | **8th** (after 7 other predicates removed) | **2nd** (immediately after PT residual) |
| #Runs absorbed | 21 | 36 |
| Precision | **95.2%** | 88.9% |
| Recall | 39.2% | **61.5%** |
| **F1** | 55.6% | **72.7%** |
| **F0.5** | 74.1% | **81.6%** |
| s_true (false positives in correct runs) | unknown | 0 |
| Interpretability | "A branch was taken in DefaultReplica" | "PrePrepare and ReplicaCommit agree on view+seq but disagree on operation" — directly captures the Byzantine mutation |

The baseline **cannot isolate Invalid Operation until iteration 8** — by that point, 972 of 995 failing runs have been removed by earlier predicates, and only 21 runs remain. The predicate achieves high precision (95.2%) but low recall (39.2%) because most Invalid Operation runs were already absorbed by earlier, non-specific predicates.

ISOLATION identifies Invalid Operation at **iteration 2** with much higher recall (61.5%) and an F0.5 of 81.6% vs 74.1%. The predicate is also **causally specific**: it says exactly _what_ went wrong ("the committed operation differs from the proposed one at the same slot"), while the baseline's `:393` just says a branch was taken somewhere in the replica code.

### View-Change Fault

| Metric | Baseline | ISOLATION |
|--------|----------|-----------|
| Best predicate | `:292 is true` (mixed with PT) | `VC->VC new_view ne` >3 (AS) |
| Dedicated precision | 4.3% (absorbed by iter 1) | 16.7% (AS iter 2) |
| Recall | 68.3% (absorbed by iter 1) | 14.3% (AS) |
| Isolation quality | Not isolated — mixed into PT residual | Partially isolated in AS scope |

Neither method cleanly isolates VCF because it shares symptoms with PT (both cause view-change cascades and timeouts).

### Seq-No Replay

| Metric | Baseline | ISOLATION |
|--------|----------|-----------|
| Best predicate | `:319 is true` (iter 3, P=13.0% R=38.9%) | Not isolated |
| Isolation quality | Weakly captured as secondary in iter 3 | Not isolated (too few samples) |

The baseline picks up some Seq-No Replay signal in iteration 3, but at only 13% precision — mixed with Partition Timeout.

### Split Brain, Commit Corruption

| Bug Type | #Runs | Baseline | ISOLATION |
|----------|-------|----------|-----------|
| Split Brain | 2 | Not isolated | Not isolated |
| Commit Corruption | 2 | Not isolated | Not isolated |

Both methods fail on rare bugs due to insufficient sample size for statistical separation.

---

## Summary

| Aspect | Baseline | ISOLATION |
|--------|----------|-----------|
| Total predicates | 9 | 14 |
| Bug types with dedicated predicate | 1 (PT as residual) | 2 (PT + Invalid Op) |
| PT: F0.5 | 85.5% | **86.6%** |
| Invalid Op: F0.5 | 74.1% (iter 8) | **81.6% (iter 2)** |
| Invalid Op: F1 | 55.6% | **72.7%** |
| Invalid Op isolation step | 8th | **2nd** |
| Root-cause explanatory power | Low (branch taken / not taken) | **High** (message field differences) |
| Predicate type | Source-code branch conditions | Message-pair field comparisons |
| Instrumentation required | Source-to-source compiler | Message interception layer |

### Conclusion

The baseline struggles to discriminate between bug types for PBFT. The branch predicates can only identify Partition Timeout as a clear cluster (F0.5=85.5%). Invalid Operation is not isolated until the 8th iteration with significantly lower scores (F0.5=74.1% vs 81.6%).

ISOLATION outperforms the baseline on Invalid Operation by a substantial margin (+17.1pp F1, +7.5pp F0.5) and identifies it at iteration 2 rather than iteration 8. The message-based predicates provide **causal explanations** ("the operation field was mutated") rather than opaque branch conditions.

This parallels the XRPL results where ISOLATION consistently outperformed the baseline. The gap is even larger for PBFT because:
1. PBFT has fewer instrumented source files (1 vs 14 for XRPL), giving the baseline fewer branch predicates to work with
2. The dominant failure mode (Partition Timeout) absorbs most fault classes in the first iteration, leaving little signal for the baseline to discriminate later bugs
3. Message-based predicates naturally express field-level mutations that branch predicates cannot capture
