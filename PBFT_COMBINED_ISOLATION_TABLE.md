# PBFT ISOLATION Results — Combined (SS + AS)

Dataset: 2800 runs (14 configs x 200), 1853 correct, 947 failures. 14 iterations total.

## Top 4 Predicates

| # | Predicate | Tol. | #Runs | Tarantula | s_true | Best Bug | P | R | F1 | F0.5 |
|---|-----------|------|-------|-----------|--------|----------|---|---|---|---|
| 1 | NV→NV new_view ne, vc_proofs gt | >0 | 661 | 0.778 | 1 | Partition Timeout | 91.1% | 72.4% | 80.7% | 86.6% |
| **2** | **PP→RC view eq, seq eq, op_first ne** | **>0** | **36** | **0.732** | **0** | **Invalid Operation** | **88.9%** | **61.5%** | **72.7%** | **81.6%** |
| 3 | VC→VC new_view ne | >3 | 48 | 0.691 | 12 | Partition Timeout | 91.7% | 5.3% | 10.0% | 21.5% |
| 4 | PP→RC view eq, seq lt | >3 | 55 | 0.662 | 25 | Partition Timeout | 96.4% | 6.4% | 12.0% | 25.2% |

Iteration 2 (`PP→RC view eq, seq eq, op_first ne`) is the causal predicate for Invalid Operation with s_true=0 (zero false positives).

## All 14 Iterations

| # | Predicate | Tol. | #Runs | Tarantula | Best Bug |
|---|-----------|------|-------|-----------|----------|
| 1 | NV→NV new_view ne, vc_proofs gt | >0 | 661 | 0.778 | PT |
| 2 | PP→RC view eq, seq eq, op_first ne | >0 | 36 | 0.732 | Invalid Op |
| 3 | VC→VC new_view ne | >3 | 48 | 0.691 | PT |
| 4 | PP→RC view eq, seq lt | >3 | 55 | 0.662 | PT |
| 5 | NV→VC new_view eq | >2 | 46 | 0.548 | PT |
| 6 | NV→NV vc_proofs lt, prep_proofs gt | >0 | 15 | 0.498 | PT |
| 7 | PP→PP op_first eq | >3 | 9 | 0.385 | PT |
| 8 | VC→NV new_view gt | >0 | 3 | 0.373 | PT |
| 9 | VC→VC new_view ne | >0 | 32 | 0.284 | PT |
| 10 | RC→Commit view eq, seq gt | >2 | 8 | 0.122 | PT |
| 11 | RC→VC seq ne last_seq | >0 | 20 | 0.069 | PT |
| 12 | Prepare→VC seq eq last_seq, rid eq | >1 | 3 | 0.002 | SeqNo |
| 13 | PP→RC seq gt, op_first ne | >0 | 2 | 0.001 | Invalid Op |
| 14 | Commit→Prepare view eq, seq ne | >3 | 9 | 0.001 | PT |
