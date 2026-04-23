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

7 predicates identified across 7 isolation iterations.

| # | Predicate | #Runs | Importance | Best Bug | P | R | F1 | F0.5 |
|---|-----------|-------|-----------|----------|---|---|----|----|
| 1 | `DefaultReplica.java:292 is true` | 649 | 0.650 | Partition Timeout | 91.7% | 67.2% | 77.6% | 85.5% |
| **2** | **`PropertyChecker.java:59 is true`** | **44** | **0.731** | **Invalid Operation** | **84.1%** | **72.5%** | **77.9%** | **81.5%** |
| 3 | `DefaultReplica.java:94 is true` | 21 | 0.592 | Partition Timeout | 85.7% | 2.0% | 4.0% | 9.3% |
| 4 | `DefaultReplica.java:319 is true` | 47 | 0.514 | Partition Timeout | 95.7% | 5.1% | 9.7% | 21.0% |
| 5 | `DefaultReplica.java:621 is false` | 56 | 0.400 | Partition Timeout | 89.3% | 5.6% | 10.6% | 22.5% |
| 6 | `DefaultReplica.java:173 is true` | 174 | 0.342 | Partition Timeout | 100.0% | 19.7% | 32.9% | 55.0% |
| 7 | `DefaultReplica.java:244 is true` | 4 | 0.011 | View-Change Fault | 50.0% | 4.9% | 8.9% | 17.5% |

### Per-Bug Metrics for Top 2 Baseline Predicates

| Predicate | Bug Type | Precision | Recall | F1 | F0.5 |
|-----------|----------|-----------|--------|----|----|
| `:292 is true` (649 runs) | Partition Timeout | 91.7% | 67.2% | 77.6% | 85.5% |
| | Invalid Operation | 2.2% | 27.5% | 4.0% | 2.6% |
| | View-Change Fault | 4.3% | 68.3% | 8.1% | 5.3% |
| | Seq-No Replay | 1.7% | 61.1% | 3.3% | 2.1% |
| `PC:59 is true` (44 runs) | Invalid Operation | 84.1% | 72.5% | 77.9% | 81.5% |
| | Seq-No Replay | 15.9% | 38.9% | 22.6% | 18.0% |
| | Partition Timeout | 2.3% | 0.1% | 0.2% | 0.5% |

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
| **F1** | **77.6%** | **80.7%** |
| **F0.5** | **85.5%** | **86.6%** |
| Interpretability | Branch condition taken; no root-cause insight | "NewView messages disagree on view number with escalating VC proofs" — directly explains view-change divergence |

Both methods perform similarly on Partition Timeout because it's a **liveness** failure driven by network topology, not message content corruption. Neither method can express "not enough messages arrived," so both act as residual absorbers. ISOLATION has a slight edge in F1 (+3.1pp) and provides a semantically meaningful predicate.

### Invalid Operation (most interesting bug)

| Metric | Baseline | ISOLATION |
|--------|----------|-----------|
| Predicate | `PropertyChecker.java:59 is true` | `PP->RC view eq, seq eq, op_first ne` >0 |
| #Runs absorbed | 44 | 36 |
| Precision | 84.1% | 88.9% |
| Recall | 72.5% | 61.5% |
| **F1** | **77.9%** | **72.7%** |
| **F0.5** | **81.5%** | **81.6%** |
| s_true (false positives in correct runs) | 0 | 0 |
| Interpretability | "PropertyChecker violation branch was taken" — detects the symptom | "PrePrepare and ReplicaCommit agree on view+seq but disagree on operation" — directly captures the Byzantine mutation |

The baseline has **higher recall** (+11pp) because `PropertyChecker.java:59` fires for _any_ violation detected by the property checker, not just operation mutations. This over-captures: 7 of the 44 runs are Seq-No Replay, not Invalid Operation (hence precision 84.1% vs 88.9%).

ISOLATION's predicate is **causally specific**: it says exactly _what_ went wrong ("the committed operation differs from the proposed one at the same slot"), while the baseline predicate says _that_ something went wrong ("the checker detected a violation"). The ISOLATION predicate has `s_true = 0` — it **never fires in correct runs**.

### View-Change Fault

| Metric | Baseline | ISOLATION |
|--------|----------|-----------|
| Best predicate | `:292 is true` (mixed with PT) | `VC->VC new_view ne` >3 (AS) |
| Dedicated precision | 4.3% (from iter 1) | 16.7% (AS iter 2) |
| Recall | 68.3% (absorbed by iter 1) | 14.3% (AS) |
| Isolation quality | Not isolated — mixed into PT residual | Partially isolated in AS scope |

Neither method cleanly isolates VCF because it shares symptoms with PT (both cause view-change cascades and timeouts).

### Seq-No Replay, Split Brain, Commit Corruption

| Bug Type | #Runs | Baseline | ISOLATION |
|----------|-------|----------|-----------|
| Seq-No Replay | 18 | Partially captured by PC:59 (P=15.9% R=38.9%) | Not isolated (too few samples) |
| Split Brain | 2 | Not isolated | Not isolated |
| Commit Corruption | 2 | Not isolated | Not isolated |

Both methods fail on rare bugs due to insufficient sample size for statistical separation.

---

## Summary

| Aspect | Baseline | ISOLATION |
|--------|----------|-----------|
| Total predicates | 7 | 14 |
| Bug types with dedicated predicate | 2 (PT + Invalid Op) | 2 (PT + Invalid Op) |
| PT: F0.5 | 85.5% | **86.6%** |
| Invalid Op: F0.5 | 81.5% | **81.6%** |
| Invalid Op: Precision | 84.1% | **88.9%** |
| Invalid Op: Recall | **72.5%** | 61.5% |
| Root-cause explanatory power | Low (branch taken / not taken) | **High** (message field differences) |
| Predicate type | Source-code branch conditions | Message-pair field comparisons |
| Instrumentation required | Source-to-source compiler | Message interception layer |

### Conclusion

For PBFT, the baseline and ISOLATION perform comparably on aggregate metrics (F0.5 within 1pp for both key bug types). The baseline achieves slightly higher recall for Invalid Operation because branch predicates over-capture violations. However, ISOLATION's predicates are **semantically richer**: they explain _which message fields diverged_ and _between which message types_, giving developers actionable root-cause information rather than "this branch was taken."

This mirrors the XRPL finding where ISOLATION's F-scores exceeded the baseline's across all bug types, while additionally providing interpretable message-level predicates that map directly to the underlying Byzantine fault mechanism.
