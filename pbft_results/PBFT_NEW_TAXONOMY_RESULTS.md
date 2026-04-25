# PBFT ISOLATION Results — New 4-Class Taxonomy

Dataset: `out copy/` — 2800 runs across 14 configs (200 per config), 2380 correct, 420 failures.

Bug classes: **Operation Corruption (OC)**, **View-Change Fault (VCF)**, **Quorum Stall (QS)**, **Split Brain (SB)**.

Iterations: 19 (every failure isolated).

## Iteration summary

| # | Predicate | Tol. | Tarantula | f_true | f_false | s_true | s_false | Removed | Best class | P | R | F1 | F0.5 |
|---|-----------|------|-----------|--------|---------|--------|---------|---------|-----------|---|---|-----|------|
| 1 | `at least 2 ViewChange -> NewView where new_view_no gt new_view_no` | >0 | 0.8465 | 233 | 187 | 13 | 2367 | 233 | Quorum Stall | 94.0% | 63.7% | 75.9% | 85.8% |
| 2 | `at least 1 PrePrepare -> ReplicaCommit where view_no eq view_no, seq_no eq seq_no, operation_first ne operation_first` | >0 | 0.8018 | 49 | 138 | 3 | 2377 | 49 | Operation Corruption | 87.8% | 79.6% | 83.5% | 86.0% |
| 3 | `at least 1 NewView -> PrePrepare where peers ne peers` | >3 | 0.7116 | 45 | 93 | 18 | 2362 | 45 | Quorum Stall | 88.9% | 11.6% | 20.6% | 38.2% |
| 4 | `at least 1 ReplicaCommit -> Commit where view_no ne view_no, seq_no gt seq_no` | >3 | 0.5769 | 9 | 84 | 3 | 2377 | 9 | Quorum Stall | 77.8% | 2.0% | 4.0% | 9.2% |
| 5 | `at least 1 PrePrepare -> NewView where peers eq peers` | >3 | 0.5098 | 27 | 57 | 37 | 2343 | 27 | Quorum Stall | 100.0% | 7.8% | 14.6% | 29.9% |
| 6 | `at least 3 Commit -> Commit where view_no eq view_no, seq_no gt seq_no, peers ne peers` | >2 | 0.3788 | 5 | 52 | 8 | 2372 | 5 | Quorum Stall | 100.0% | 1.5% | 2.9% | 6.9% |
| 7 | `at least 2 ViewChange -> Commit where last_seq_no eq seq_no, peers isdisjoint peers` | >1 | 0.3836 | 4 | 48 | 5 | 2375 | 4 | Quorum Stall | 75.0% | 0.9% | 1.7% | 4.2% |
| 8 | `at least 2 Commit -> Commit where seq_no gt seq_no, peers isdisjoint peers` | >3 | 0.3575 | 5 | 43 | 10 | 2370 | 5 | Quorum Stall | 100.0% | 1.5% | 2.9% | 6.9% |
| 9 | `at least 1 PrePrepare -> ReplicaCommit where operation_first ne operation_first, operation_second eq operation_second` | >1 | 0.3104 | 2 | 41 | 0 | 2380 | 2 | Operation Corruption | 100.0% | 3.7% | 7.1% | 16.1% |
| 10 | `at least 1 ViewChange -> ViewChange where new_view_no gt new_view_no, peers issubset peers` | >2 | 0.3085 | 10 | 31 | 35 | 2345 | 10 | Quorum Stall | 90.0% | 2.6% | 5.1% | 11.7% |
| 11 | `at least 3 Commit -> Prepare where peers eq peers` | >3 | 0.3085 | 2 | 29 | 1 | 2379 | 2 | Quorum Stall | 100.0% | 0.6% | 1.2% | 2.8% |
| 12 | `at least 1 ReplicaCommit -> PrePrepare where view_no ne view_no, operation_first eq operation_first` | >2 | 0.3132 | 2 | 27 | 1 | 2379 | 2 | Quorum Stall | 100.0% | 0.6% | 1.2% | 2.8% |
| 13 | `at least 2 Commit -> NewView where peers isdisjoint peers` | >3 | 0.1562 | 5 | 22 | 43 | 2337 | 5 | Quorum Stall | 100.0% | 1.5% | 2.9% | 6.9% |
| 14 | `at least 3 Commit -> Prepare where view_no eq view_no, seq_no lt seq_no, peers eq peers` | >2 | 0.0791 | 2 | 20 | 33 | 2347 | 2 | Quorum Stall | 100.0% | 0.6% | 1.2% | 2.8% |
| 15 | `at least 2 Prepare -> Commit where view_no gt view_no, peers issuperset peers` | >0 | 0.0533 | 2 | 18 | 50 | 2330 | 2 | Quorum Stall | 100.0% | 0.6% | 1.2% | 2.8% |
| 16 | `at least 2 Prepare -> ViewChange where seq_no eq last_seq_no, peers issuperset peers` | >1 | 0.0312 | 8 | 10 | 333 | 2047 | 8 | Quorum Stall | 87.5% | 2.0% | 4.0% | 9.3% |
| 17 | `at least 1 PrePrepare -> Commit where view_no eq view_no, seq_no lt seq_no, peers eq peers` | >0 | 0.0080 | 4 | 6 | 484 | 1896 | 4 | Quorum Stall | 100.0% | 1.2% | 2.3% | 5.6% |
| 18 | `at least 1 PrePrepare -> ReplicaCommit where view_no eq view_no, seq_no lt seq_no, operation_first eq operation_first` | >1 | 0.0026 | 2 | 4 | 523 | 1857 | 2 | Operation Corruption | 100.0% | 3.7% | 7.1% | 16.1% |
| 19 | `at least 3 Commit -> ReplicaCommit where view_no eq view_no, seq_no lt seq_no` | >3 | 0.0024 | 4 | 0 | 1394 | 986 | 4 | Operation Corruption | 100.0% | 7.4% | 13.8% | 28.6% |

## Detailed iteration breakdown

### Iteration 1 — Tarantula 0.8465

**Predicate**: `at least 2 ViewChange -> NewView where new_view_no gt new_view_no` > 0

**Aggregation**: f_true=233, f_false=187, s_true=13, s_false=2367

**Pipeline state at iteration start**: 2800 reports, 79456 aggregations, 17326 filtered aggregations, 420 failed reports.

**Removed runs**: 233

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 0.9% | 5.6% | 94.0% | 0.0% |
| Recall | 3.7% | 59.1% | 63.7% | 0.0% |
| F1 | 1.4% | 10.2% | 75.9% | 0.0% |
| F0.5 | 1.0% | 6.8% | 85.8% | 0.0% |
| Specificity | 91.6% | 92.1% | 99.4% | 91.7% |
| Accuracy | 89.9% | 91.8% | 95.0% | 91.6% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D1-C2-ss/out99.txt`
- `out copy/tests-D2-C0/out144.txt`
- `out copy/tests-D2-C2-as/out59.txt`
- `out copy/tests-D2-C2-ss/out89.txt`
- `out copy/tests-D1-C1-ss/out79.txt`
- `out copy/tests-D2-C2-ss/out129.txt`
- `out copy/tests-D0-C2-ss/out191.txt`
- `out copy/tests-D2-C0/out20.txt`
- `out copy/tests-D2-C2-ss/out58.txt`
- `out copy/tests-D2-C2-ss/out96.txt`
- `out copy/tests-D1-C2-as/out36.txt`
- `out copy/tests-D2-C2-ss/out3.txt`
- `out copy/tests-D1-C1-ss/out119.txt`
- `out copy/tests-D1-C1-ss/out7.txt`
- `out copy/tests-D1-C0/out186.txt`
- `out copy/tests-D1-C0/out115.txt`
- `out copy/tests-D1-C1-ss/out137.txt`
- `out copy/tests-D2-C2-ss/out190.txt`
- `out copy/tests-D1-C2-as/out156.txt`
- `out copy/tests-D2-C1-as/out149.txt`
- `out copy/tests-D1-C2-ss/out56.txt`
- `out copy/tests-D2-C2-as/out192.txt`
- `out copy/tests-D2-C2-ss/out194.txt`
- `out copy/tests-D1-C1-ss/out37.txt`
- `out copy/tests-D2-C0/out37.txt`
- `out copy/tests-D2-C2-as/out141.txt`
- `out copy/tests-D2-C0/out82.txt`
- `out copy/tests-D2-C2-ss/out7.txt`
- `out copy/tests-D1-C2-as/out93.txt`
- `out copy/tests-D2-C1-ss/out77.txt`
- `out copy/tests-D1-C0/out123.txt`
- `out copy/tests-D2-C0/out186.txt`
- `out copy/tests-D2-C2-as/out19.txt`
- `out copy/tests-D2-C1-as/out119.txt`
- `out copy/tests-D2-C1-ss/out20.txt`
- `out copy/tests-D2-C1-as/out40.txt`
- `out copy/tests-D2-C2-as/out116.txt`
- `out copy/tests-D2-C2-as/out79.txt`
- `out copy/tests-D1-C2-as/out133.txt`
- `out copy/tests-D2-C1-as/out132.txt`
- `out copy/tests-D2-C1-as/out136.txt`
- `out copy/tests-D2-C2-as/out73.txt`
- `out copy/tests-D2-C1-ss/out191.txt`
- `out copy/tests-D2-C2-ss/out79.txt`
- `out copy/tests-D2-C1-ss/out178.txt`
- `out copy/tests-D1-C1-ss/out94.txt`
- `out copy/tests-D1-C0/out116.txt`
- `out copy/tests-D1-C1-as/out141.txt`
- `out copy/tests-D1-C2-ss/out196.txt`
- `out copy/tests-D1-C2-ss/out157.txt`
- `out copy/tests-D1-C2-as/out190.txt`
- `out copy/tests-D1-C2-ss/out93.txt`
- `out copy/tests-D2-C1-ss/out162.txt`
- `out copy/tests-D2-C0/out199.txt`
- `out copy/tests-D2-C0/out40.txt`
- `out copy/tests-D1-C0/out41.txt`
- `out copy/tests-D2-C2-as/out9.txt`
- `out copy/tests-D2-C2-as/out94.txt`
- `out copy/tests-D1-C0/out36.txt`
- `out copy/tests-D1-C0/out141.txt`
- `out copy/tests-D2-C1-as/out16.txt`
- `out copy/tests-D2-C2-as/out20.txt`
- `out copy/tests-D2-C2-as/out77.txt`
- `out copy/tests-D1-C0/out73.txt`
- `out copy/tests-D2-C2-ss/out36.txt`
- `out copy/tests-D1-C2-as/out86.txt`
- `out copy/tests-D2-C0/out185.txt`
- `out copy/tests-D2-C1-ss/out137.txt`
- `out copy/tests-D1-C2-as/out149.txt`
- `out copy/tests-D1-C1-ss/out115.txt`
- `out copy/tests-D2-C1-as/out145.txt`
- `out copy/tests-D2-C1-ss/out175.txt`
- `out copy/tests-D1-C2-as/out19.txt`
- `out copy/tests-D1-C2-ss/out123.txt`
- `out copy/tests-D2-C2-as/out132.txt`
- `out copy/tests-D2-C2-ss/out45.txt`
- `out copy/tests-D2-C1-as/out52.txt`
- `out copy/tests-D2-C1-ss/out110.txt`
- `out copy/tests-D2-C0/out57.txt`
- `out copy/tests-D2-C1-as/out160.txt`
- `out copy/tests-D2-C2-as/out7.txt`
- `out copy/tests-D2-C2-ss/out27.txt`
- `out copy/tests-D2-C1-ss/out196.txt`
- `out copy/tests-D2-C0/out43.txt`
- `out copy/tests-D2-C1-ss/out19.txt`
- `out copy/tests-D1-C2-ss/out116.txt`
- `out copy/tests-D1-C2-as/out11.txt`
- `out copy/tests-D1-C1-ss/out27.txt`
- `out copy/tests-D2-C0/out87.txt`
- `out copy/tests-D2-C0/out123.txt`
- `out copy/tests-D2-C0/out56.txt`
- `out copy/tests-D2-C1-ss/out51.txt`
- `out copy/tests-D2-C1-ss/out52.txt`
- `out copy/tests-D1-C0/out133.txt`
- `out copy/tests-D1-C2-ss/out36.txt`
- `out copy/tests-D1-C2-ss/out140.txt`
- `out copy/tests-D1-C1-ss/out186.txt`
- `out copy/tests-D2-C1-ss/out151.txt`
- `out copy/tests-D2-C2-as/out14.txt`
- `out copy/tests-D1-C1-as/out57.txt`
- `out copy/tests-D1-C2-ss/out94.txt`
- `out copy/tests-D1-C0/out11.txt`
- `out copy/tests-D2-C2-ss/out196.txt`
- `out copy/tests-D2-C1-ss/out12.txt`
- `out copy/tests-D2-C2-as/out37.txt`
- `out copy/tests-D1-C0/out157.txt`
- `out copy/tests-D1-C2-as/out196.txt`
- `out copy/tests-D2-C2-as/out99.txt`
- `out copy/tests-D1-C0/out77.txt`
- `out copy/tests-D2-C0/out7.txt`
- `out copy/tests-D2-C2-ss/out163.txt`
- `out copy/tests-D1-C1-as/out157.txt`
- `out copy/tests-D1-C0/out107.txt`
- `out copy/tests-D2-C0/out151.txt`
- `out copy/tests-D1-C0/out95.txt`
- `out copy/tests-D2-C1-as/out96.txt`
- `out copy/tests-D1-C2-as/out15.txt`
- `out copy/tests-D2-C2-as/out52.txt`
- `out copy/tests-D2-C2-as/out194.txt`
- `out copy/tests-D2-C2-as/out178.txt`
- `out copy/tests-D1-C1-as/out66.txt`
- `out copy/tests-D2-C0/out90.txt`
- `out copy/tests-D2-C2-ss/out77.txt`
- `out copy/tests-D1-C1-ss/out15.txt`
- `out copy/tests-D2-C1-ss/out44.txt`
- `out copy/tests-D2-C2-ss/out104.txt`
- `out copy/tests-D1-C1-as/out90.txt`
- `out copy/tests-D1-C1-as/out11.txt`
- `out copy/tests-D2-C1-as/out19.txt`
- `out copy/tests-D1-C1-as/out174.txt`
- `out copy/tests-D2-C2-as/out104.txt`
- `out copy/tests-D1-C1-ss/out3.txt`
- `out copy/tests-D1-C1-ss/out195.txt`
- `out copy/tests-D2-C1-ss/out174.txt`
- `out copy/tests-D2-C1-as/out197.txt`
- `out copy/tests-D1-C1-as/out119.txt`
- `out copy/tests-D2-C1-ss/out123.txt`
- `out copy/tests-D1-C1-ss/out49.txt`
- `out copy/tests-D1-C0/out49.txt`
- `out copy/tests-D1-C2-ss/out19.txt`
- `out copy/tests-D2-C1-as/out187.txt`
- `out copy/tests-D1-C1-as/out178.txt`
- `out copy/tests-D2-C2-ss/out56.txt`
- `out copy/tests-D2-C2-ss/out57.txt`
- `out copy/tests-D1-C1-as/out79.txt`
- `out copy/tests-D2-C2-ss/out141.txt`
- `out copy/tests-D2-C0/out51.txt`
- `out copy/tests-D1-C1-as/out166.txt`
- `out copy/tests-D2-C2-as/out41.txt`
- `out copy/tests-D1-C1-ss/out44.txt`
- `out copy/tests-D1-C2-ss/out73.txt`
- `out copy/tests-D2-C2-ss/out140.txt`
- `out copy/tests-D1-C1-as/out123.txt`
- `out copy/tests-D1-C1-ss/out145.txt`
- `out copy/tests-D1-C2-as/out33.txt`
- `out copy/tests-D1-C0/out146.txt`
- `out copy/tests-D2-C0/out137.txt`
- `out copy/tests-D2-C1-as/out87.txt`
- `out copy/tests-D2-C1-ss/out37.txt`
- `out copy/tests-D1-C0/out136.txt`
- `out copy/tests-D2-C1-as/out50.txt`
- `out copy/tests-D2-C2-ss/out178.txt`
- `out copy/tests-D1-C1-ss/out85.txt`
- `out copy/tests-D2-C0/out187.txt`
- `out copy/tests-D2-C0/out6.txt`
- `out copy/tests-D2-C0/out115.txt`
- `out copy/tests-D2-C1-as/out174.txt`
- `out copy/tests-D1-C2-ss/out60.txt`
- `out copy/tests-D2-C2-as/out60.txt`
- `out copy/tests-D2-C2-as/out114.txt`
- `out copy/tests-D2-C2-ss/out60.txt`
- `out copy/tests-D1-C1-as/out44.txt`
- `out copy/tests-D1-C2-as/out103.txt`
- `out copy/tests-D2-C1-as/out123.txt`
- `out copy/tests-D2-C1-ss/out6.txt`
- `out copy/tests-D2-C1-as/out114.txt`
- `out copy/tests-D2-C2-as/out110.txt`
- `out copy/tests-D1-C1-ss/out178.txt`
- `out copy/tests-D1-C2-ss/out156.txt`
- `out copy/tests-D1-C2-as/out73.txt`
- `out copy/tests-D2-C1-as/out157.txt`
- `out copy/tests-D2-C1-as/out20.txt`
- `out copy/tests-D2-C2-as/out6.txt`
- `out copy/tests-D2-C0/out61.txt`
- `out copy/tests-D1-C1-ss/out170.txt`
- `out copy/tests-D2-C1-as/out191.txt`
- `out copy/tests-D2-C1-ss/out33.txt`
- `out copy/tests-D1-C2-as/out137.txt`
- `out copy/tests-D1-C2-ss/out41.txt`
- `out copy/tests-D2-C1-ss/out26.txt`
- `out copy/tests-D1-C2-ss/out44.txt`
- `out copy/tests-D2-C2-as/out140.txt`
- `out copy/tests-D1-C0/out166.txt`
- `out copy/tests-D1-C1-as/out27.txt`
- `out copy/tests-D2-C2-ss/out153.txt`
- `out copy/tests-D1-C1-ss/out90.txt`
- `out copy/tests-D2-C1-as/out41.txt`
- `out copy/tests-D2-C1-ss/out11.txt`
- `out copy/tests-D1-C2-as/out145.txt`
- `out copy/tests-D2-C1-ss/out58.txt`
- `out copy/tests-D2-C1-ss/out40.txt`
- `out copy/tests-D2-C0/out99.txt`
- `out copy/tests-D2-C1-as/out14.txt`
- `out copy/tests-D2-C2-as/out153.txt`
- `out copy/tests-D2-C2-as/out191.txt`
- `out copy/tests-D2-C2-ss/out151.txt`
- `out copy/tests-D2-C2-ss/out186.txt`
- `out copy/tests-D1-C2-ss/out149.txt`
- `out copy/tests-D1-C1-ss/out93.txt`
- `out copy/tests-D2-C0/out96.txt`
- `out copy/tests-D2-C2-ss/out53.txt`
- `out copy/tests-D1-C1-ss/out56.txt`
- `out copy/tests-D1-C2-ss/out66.txt`
- `out copy/tests-D1-C1-ss/out103.txt`
- `out copy/tests-D1-C1-ss/out199.txt`
- `out copy/tests-D2-C2-as/out159.txt`
- `out copy/tests-D2-C1-as/out192.txt`
- `out copy/tests-D2-C2-as/out36.txt`
- `out copy/tests-D2-C2-as/out45.txt`
- `out copy/tests-D2-C1-as/out95.txt`
- `out copy/tests-D1-C1-as/out146.txt`
- `out copy/tests-D2-C2-ss/out132.txt`
- `out copy/tests-D1-C0/out182.txt`
- `out copy/tests-D2-C2-ss/out51.txt`
- `out copy/tests-D2-C2-as/out24.txt`
- `out copy/tests-D1-C2-as/out136.txt`
- `out copy/tests-D2-C2-as/out186.txt`
- `out copy/tests-D2-C2-ss/out119.txt`
- `out copy/tests-D1-C2-ss/out11.txt`
- `out copy/tests-D2-C2-ss/out20.txt`
- `out copy/tests-D2-C2-as/out135.txt`
- `out copy/tests-D1-C2-as/out49.txt`
- `out copy/tests-D2-C2-ss/out19.txt`

</details>

### Iteration 2 — Tarantula 0.8018

**Predicate**: `at least 1 PrePrepare -> ReplicaCommit where view_no eq view_no, seq_no eq seq_no, operation_first ne operation_first` > 0

**Aggregation**: f_true=49, f_false=138, s_true=3, s_false=2377

**Pipeline state at iteration start**: 2567 reports, 79455 aggregations, 16138 filtered aggregations, 187 failed reports.

**Removed runs**: 49

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 87.8% | 2.0% | 10.2% | 0.0% |
| Recall | 79.6% | 4.5% | 1.5% | 0.0% |
| F1 | 83.5% | 2.8% | 2.5% | 0.0% |
| F0.5 | 86.0% | 2.3% | 4.6% | 0.0% |
| Specificity | 99.8% | 98.3% | 98.2% | 98.2% |
| Accuracy | 99.4% | 97.5% | 86.3% | 98.2% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D0-C1-as/out121.txt`
- `out copy/tests-D0-C2-as/out91.txt`
- `out copy/tests-D1-C1-ss/out143.txt`
- `out copy/tests-D1-C2-as/out126.txt`
- `out copy/tests-D2-C2-as/out181.txt`
- `out copy/tests-D2-C2-ss/out181.txt`
- `out copy/tests-D0-C2-ss/out100.txt`
- `out copy/tests-D1-C2-as/out109.txt`
- `out copy/tests-D2-C2-ss/out143.txt`
- `out copy/tests-D0-C1-as/out108.txt`
- `out copy/tests-D1-C1-as/out109.txt`
- `out copy/tests-D2-C1-ss/out41.txt`
- `out copy/tests-D2-C2-ss/out16.txt`
- `out copy/tests-D1-C2-ss/out120.txt`
- `out copy/tests-D0-C2-as/out148.txt`
- `out copy/tests-D0-C2-as/out100.txt`
- `out copy/tests-D1-C2-ss/out7.txt`
- `out copy/tests-D0-C1-as/out143.txt`
- `out copy/tests-D2-C2-as/out48.txt`
- `out copy/tests-D0-C1-ss/out108.txt`
- `out copy/tests-D0-C1-ss/out143.txt`
- `out copy/tests-D0-C2-ss/out148.txt`
- `out copy/tests-D2-C2-as/out66.txt`
- `out copy/tests-D1-C2-as/out130.txt`
- `out copy/tests-D2-C2-ss/out100.txt`
- `out copy/tests-D1-C2-ss/out130.txt`
- `out copy/tests-D2-C1-as/out121.txt`
- `out copy/tests-D0-C2-ss/out126.txt`
- `out copy/tests-D1-C2-ss/out43.txt`
- `out copy/tests-D2-C0/out41.txt`
- `out copy/tests-D2-C2-as/out143.txt`
- `out copy/tests-D0-C2-ss/out93.txt`
- `out copy/tests-D0-C2-as/out93.txt`
- `out copy/tests-D0-C2-as/out95.txt`
- `out copy/tests-D0-C2-ss/out95.txt`
- `out copy/tests-D0-C1-ss/out121.txt`
- `out copy/tests-D2-C2-ss/out176.txt`
- `out copy/tests-D0-C2-as/out126.txt`
- `out copy/tests-D1-C2-ss/out109.txt`
- `out copy/tests-D0-C2-ss/out91.txt`
- `out copy/tests-D1-C1-ss/out136.txt`
- `out copy/tests-D1-C2-as/out120.txt`
- `out copy/tests-D1-C2-as/out43.txt`
- `out copy/tests-D1-C2-ss/out126.txt`
- `out copy/tests-D1-C1-ss/out109.txt`
- `out copy/tests-D2-C1-ss/out100.txt`
- `out copy/tests-D2-C1-as/out100.txt`
- `out copy/tests-D1-C2-ss/out167.txt`
- `out copy/tests-D2-C2-ss/out40.txt`

</details>

### Iteration 3 — Tarantula 0.7116

**Predicate**: `at least 1 NewView -> PrePrepare where peers ne peers` > 3

**Aggregation**: f_true=45, f_false=93, s_true=18, s_false=2362

**Pipeline state at iteration start**: 2518 reports, 79454 aggregations, 15774 filtered aggregations, 138 failed reports.

**Removed runs**: 45

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 0.0% | 8.9% | 88.9% | 2.2% |
| Recall | 0.0% | 18.2% | 11.6% | 50.0% |
| F1 | 0.0% | 11.9% | 20.6% | 4.3% |
| F0.5 | 0.0% | 9.9% | 38.2% | 2.7% |
| Specificity | 98.4% | 98.5% | 99.8% | 98.4% |
| Accuracy | 96.5% | 97.9% | 89.0% | 98.4% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C1-ss/out179.txt`
- `out copy/tests-D2-C1-as/out99.txt`
- `out copy/tests-D2-C0/out136.txt`
- `out copy/tests-D2-C2-ss/out43.txt`
- `out copy/tests-D2-C1-ss/out66.txt`
- `out copy/tests-D2-C0/out159.txt`
- `out copy/tests-D2-C1-ss/out140.txt`
- `out copy/tests-D2-C1-ss/out73.txt`
- `out copy/tests-D2-C2-ss/out199.txt`
- `out copy/tests-D2-C1-ss/out119.txt`
- `out copy/tests-D2-C1-as/out162.txt`
- `out copy/tests-D2-C0/out50.txt`
- `out copy/tests-D2-C0/out156.txt`
- `out copy/tests-D2-C1-as/out18.txt`
- `out copy/tests-D2-C0/out66.txt`
- `out copy/tests-D2-C0/out73.txt`
- `out copy/tests-D2-C1-as/out79.txt`
- `out copy/tests-D2-C2-ss/out31.txt`
- `out copy/tests-D2-C1-ss/out159.txt`
- `out copy/tests-D1-C1-ss/out174.txt`
- `out copy/tests-D2-C0/out14.txt`
- `out copy/tests-D2-C2-as/out129.txt`
- `out copy/tests-D2-C2-ss/out197.txt`
- `out copy/tests-D2-C2-as/out157.txt`
- `out copy/tests-D2-C1-as/out53.txt`
- `out copy/tests-D2-C2-as/out175.txt`
- `out copy/tests-D1-C1-ss/out53.txt`
- `out copy/tests-D1-C0/out3.txt`
- `out copy/tests-D1-C2-ss/out146.txt`
- `out copy/tests-D2-C1-as/out66.txt`
- `out copy/tests-D1-C2-as/out53.txt`
- `out copy/tests-D1-C1-as/out103.txt`
- `out copy/tests-D1-C2-as/out48.txt`
- `out copy/tests-D2-C0/out178.txt`
- `out copy/tests-D2-C1-ss/out9.txt`
- `out copy/tests-D2-C1-ss/out186.txt`
- `out copy/tests-D2-C2-as/out197.txt`
- `out copy/tests-D2-C0/out30.txt`
- `out copy/tests-D2-C2-ss/out175.txt`
- `out copy/tests-D2-C1-as/out44.txt`
- `out copy/tests-D2-C2-ss/out52.txt`
- `out copy/tests-D1-C2-ss/out145.txt`
- `out copy/tests-D2-C0/out112.txt`
- `out copy/tests-D2-C2-as/out96.txt`
- `out copy/tests-D1-C1-as/out95.txt`

</details>

### Iteration 4 — Tarantula 0.5769

**Predicate**: `at least 1 ReplicaCommit -> Commit where view_no ne view_no, seq_no gt seq_no` > 3

**Aggregation**: f_true=9, f_false=84, s_true=3, s_false=2377

**Pipeline state at iteration start**: 2473 reports, 79453 aggregations, 14962 filtered aggregations, 93 failed reports.

**Removed runs**: 9

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 0.0% | 22.2% | 77.8% | 11.1% |
| Recall | 0.0% | 9.1% | 2.0% | 50.0% |
| F1 | 0.0% | 12.9% | 4.0% | 18.2% |
| F0.5 | 0.0% | 17.2% | 9.2% | 13.2% |
| Specificity | 99.7% | 99.7% | 99.9% | 99.7% |
| Accuracy | 97.8% | 99.0% | 87.9% | 99.7% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C1-ss/out95.txt`
- `out copy/tests-D2-C0/out18.txt`
- `out copy/tests-D2-C2-as/out95.txt`
- `out copy/tests-D2-C1-as/out175.txt`
- `out copy/tests-D2-C1-ss/out121.txt`
- `out copy/tests-D2-C2-ss/out95.txt`
- `out copy/tests-D2-C2-ss/out87.txt`
- `out copy/tests-D2-C1-ss/out18.txt`
- `out copy/tests-D2-C2-as/out136.txt`

</details>

### Iteration 5 — Tarantula 0.5098

**Predicate**: `at least 1 PrePrepare -> NewView where peers eq peers` > 3

**Aggregation**: f_true=27, f_false=57, s_true=37, s_false=2343

**Pipeline state at iteration start**: 2464 reports, 79452 aggregations, 14568 filtered aggregations, 84 failed reports.

**Removed runs**: 27

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 0.0% | 0.0% | 100.0% | 0.0% |
| Recall | 0.0% | 0.0% | 7.8% | 0.0% |
| F1 | 0.0% | 0.0% | 14.6% | 0.0% |
| F0.5 | 0.0% | 0.0% | 29.9% | 0.0% |
| Specificity | 99.0% | 99.0% | 100.0% | 99.0% |
| Accuracy | 97.1% | 98.2% | 88.7% | 99.0% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-as/out26.txt`
- `out copy/tests-D2-C1-ss/out79.txt`
- `out copy/tests-D2-C2-ss/out185.txt`
- `out copy/tests-D2-C1-as/out151.txt`
- `out copy/tests-D2-C2-ss/out184.txt`
- `out copy/tests-D2-C1-as/out159.txt`
- `out copy/tests-D2-C0/out59.txt`
- `out copy/tests-D2-C0/out129.txt`
- `out copy/tests-D2-C1-ss/out185.txt`
- `out copy/tests-D2-C1-ss/out59.txt`
- `out copy/tests-D2-C1-ss/out136.txt`
- `out copy/tests-D2-C0/out79.txt`
- `out copy/tests-D2-C1-as/out12.txt`
- `out copy/tests-D1-C1-as/out36.txt`
- `out copy/tests-D2-C2-as/out43.txt`
- `out copy/tests-D2-C0/out9.txt`
- `out copy/tests-D2-C0/out175.txt`
- `out copy/tests-D2-C2-ss/out41.txt`
- `out copy/tests-D2-C1-ss/out129.txt`
- `out copy/tests-D2-C2-ss/out182.txt`
- `out copy/tests-D1-C2-as/out41.txt`
- `out copy/tests-D2-C1-as/out59.txt`
- `out copy/tests-D1-C0/out170.txt`
- `out copy/tests-D2-C2-as/out156.txt`
- `out copy/tests-D2-C1-as/out43.txt`
- `out copy/tests-D2-C2-as/out18.txt`
- `out copy/tests-D2-C1-as/out26.txt`

</details>

### Iteration 6 — Tarantula 0.3788

**Predicate**: `at least 3 Commit -> Commit where view_no eq view_no, seq_no gt seq_no, peers ne peers` > 2

**Aggregation**: f_true=5, f_false=52, s_true=8, s_false=2372

**Pipeline state at iteration start**: 2437 reports, 79451 aggregations, 14075 filtered aggregations, 57 failed reports.

**Removed runs**: 5

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 0.0% | 0.0% | 100.0% | 0.0% |
| Recall | 0.0% | 0.0% | 1.5% | 0.0% |
| F1 | 0.0% | 0.0% | 2.9% | 0.0% |
| F0.5 | 0.0% | 0.0% | 6.9% | 0.0% |
| Specificity | 99.8% | 99.8% | 100.0% | 99.8% |
| Accuracy | 97.9% | 99.0% | 87.9% | 99.8% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-ss/out11.txt`
- `out copy/tests-D2-C0/out166.txt`
- `out copy/tests-D1-C1-ss/out182.txt`
- `out copy/tests-D2-C1-ss/out153.txt`
- `out copy/tests-D2-C1-ss/out99.txt`

</details>

### Iteration 7 — Tarantula 0.3836

**Predicate**: `at least 2 ViewChange -> Commit where last_seq_no eq seq_no, peers isdisjoint peers` > 1

**Aggregation**: f_true=4, f_false=48, s_true=5, s_false=2375

**Pipeline state at iteration start**: 2432 reports, 79450 aggregations, 14099 filtered aggregations, 52 failed reports.

**Removed runs**: 4

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 25.0% | 0.0% | 75.0% | 0.0% |
| Recall | 1.9% | 0.0% | 0.9% | 0.0% |
| F1 | 3.4% | 0.0% | 1.7% | 0.0% |
| F0.5 | 7.1% | 0.0% | 4.2% | 0.0% |
| Specificity | 99.9% | 99.9% | 100.0% | 99.9% |
| Accuracy | 98.0% | 99.1% | 87.8% | 99.8% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C0/out58.txt`
- `out copy/tests-D2-C1-as/out194.txt`
- `out copy/tests-D2-C1-as/out168.txt`
- `out copy/tests-D2-C2-as/out112.txt`

</details>

### Iteration 8 — Tarantula 0.3575

**Predicate**: `at least 2 Commit -> Commit where seq_no gt seq_no, peers isdisjoint peers` > 3

**Aggregation**: f_true=5, f_false=43, s_true=10, s_false=2370

**Pipeline state at iteration start**: 2428 reports, 79449 aggregations, 13713 filtered aggregations, 48 failed reports.

**Removed runs**: 5

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 0.0% | 0.0% | 100.0% | 0.0% |
| Recall | 0.0% | 0.0% | 1.5% | 0.0% |
| F1 | 0.0% | 0.0% | 2.9% | 0.0% |
| F0.5 | 0.0% | 0.0% | 6.9% | 0.0% |
| Specificity | 99.8% | 99.8% | 100.0% | 99.8% |
| Accuracy | 97.9% | 99.0% | 87.9% | 99.8% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C1-as/out6.txt`
- `out copy/tests-D2-C2-ss/out137.txt`
- `out copy/tests-D2-C0/out174.txt`
- `out copy/tests-D2-C2-ss/out4.txt`
- `out copy/tests-D1-C0/out15.txt`

</details>

### Iteration 9 — Tarantula 0.3104

**Predicate**: `at least 1 PrePrepare -> ReplicaCommit where operation_first ne operation_first, operation_second eq operation_second` > 1

**Aggregation**: f_true=2, f_false=41, s_true=0, s_false=2380

**Pipeline state at iteration start**: 2423 reports, 79448 aggregations, 13278 filtered aggregations, 43 failed reports.

**Removed runs**: 2

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 100.0% | 0.0% | 0.0% | 0.0% |
| Recall | 3.7% | 0.0% | 0.0% | 0.0% |
| F1 | 7.1% | 0.0% | 0.0% | 0.0% |
| F0.5 | 16.1% | 0.0% | 0.0% | 0.0% |
| Specificity | 100.0% | 99.9% | 99.9% | 99.9% |
| Accuracy | 98.1% | 99.1% | 87.6% | 99.9% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-ss/out64.txt`
- `out copy/tests-D1-C1-as/out136.txt`

</details>

### Iteration 10 — Tarantula 0.3085

**Predicate**: `at least 1 ViewChange -> ViewChange where new_view_no gt new_view_no, peers issubset peers` > 2

**Aggregation**: f_true=10, f_false=31, s_true=35, s_false=2345

**Pipeline state at iteration start**: 2421 reports, 79447 aggregations, 13022 filtered aggregations, 41 failed reports.

**Removed runs**: 10

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 0.0% | 10.0% | 90.0% | 0.0% |
| Recall | 0.0% | 4.5% | 2.6% | 0.0% |
| F1 | 0.0% | 6.3% | 5.1% | 0.0% |
| F0.5 | 0.0% | 8.1% | 11.7% | 0.0% |
| Specificity | 99.6% | 99.7% | 100.0% | 99.6% |
| Accuracy | 97.7% | 98.9% | 88.0% | 99.6% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-ss/out156.txt`
- `out copy/tests-D2-C2-as/out42.txt`
- `out copy/tests-D1-C2-ss/out170.txt`
- `out copy/tests-D2-C2-ss/out48.txt`
- `out copy/tests-D2-C2-as/out35.txt`
- `out copy/tests-D1-C1-ss/out112.txt`
- `out copy/tests-D2-C1-as/out17.txt`
- `out copy/tests-D2-C0/out35.txt`
- `out copy/tests-D1-C1-as/out7.txt`
- `out copy/tests-D2-C0/out149.txt`

</details>

### Iteration 11 — Tarantula 0.3085

**Predicate**: `at least 3 Commit -> Prepare where peers eq peers` > 3

**Aggregation**: f_true=2, f_false=29, s_true=1, s_false=2379

**Pipeline state at iteration start**: 2411 reports, 79446 aggregations, 11114 filtered aggregations, 31 failed reports.

**Removed runs**: 2

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 0.0% | 0.0% | 100.0% | 0.0% |
| Recall | 0.0% | 0.0% | 0.6% | 0.0% |
| F1 | 0.0% | 0.0% | 1.2% | 0.0% |
| F0.5 | 0.0% | 0.0% | 2.8% | 0.0% |
| Specificity | 99.9% | 99.9% | 100.0% | 99.9% |
| Accuracy | 98.0% | 99.1% | 87.8% | 99.9% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C1-ss/out30.txt`
- `out copy/tests-D1-C0/out57.txt`

</details>

### Iteration 12 — Tarantula 0.3132

**Predicate**: `at least 1 ReplicaCommit -> PrePrepare where view_no ne view_no, operation_first eq operation_first` > 2

**Aggregation**: f_true=2, f_false=27, s_true=1, s_false=2379

**Pipeline state at iteration start**: 2409 reports, 79445 aggregations, 7819 filtered aggregations, 29 failed reports.

**Removed runs**: 2

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 0.0% | 0.0% | 100.0% | 0.0% |
| Recall | 0.0% | 0.0% | 0.6% | 0.0% |
| F1 | 0.0% | 0.0% | 1.2% | 0.0% |
| F0.5 | 0.0% | 0.0% | 2.8% | 0.0% |
| Specificity | 99.9% | 99.9% | 100.0% | 99.9% |
| Accuracy | 98.0% | 99.1% | 87.8% | 99.9% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-as/out68.txt`
- `out copy/tests-D2-C2-ss/out136.txt`

</details>

### Iteration 13 — Tarantula 0.1562

**Predicate**: `at least 2 Commit -> NewView where peers isdisjoint peers` > 3

**Aggregation**: f_true=5, f_false=22, s_true=43, s_false=2337

**Pipeline state at iteration start**: 2407 reports, 79444 aggregations, 5631 filtered aggregations, 27 failed reports.

**Removed runs**: 5

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 0.0% | 0.0% | 100.0% | 0.0% |
| Recall | 0.0% | 0.0% | 1.5% | 0.0% |
| F1 | 0.0% | 0.0% | 2.9% | 0.0% |
| F0.5 | 0.0% | 0.0% | 6.9% | 0.0% |
| Specificity | 99.8% | 99.8% | 100.0% | 99.8% |
| Accuracy | 97.9% | 99.0% | 87.9% | 99.8% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C1-as/out141.txt`
- `out copy/tests-D2-C0/out36.txt`
- `out copy/tests-D2-C1-as/out9.txt`
- `out copy/tests-D1-C2-ss/out174.txt`
- `out copy/tests-D2-C2-ss/out166.txt`

</details>

### Iteration 14 — Tarantula 0.0791

**Predicate**: `at least 3 Commit -> Prepare where view_no eq view_no, seq_no lt seq_no, peers eq peers` > 2

**Aggregation**: f_true=2, f_false=20, s_true=33, s_false=2347

**Pipeline state at iteration start**: 2402 reports, 79443 aggregations, 1999 filtered aggregations, 22 failed reports.

**Removed runs**: 2

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 0.0% | 0.0% | 100.0% | 0.0% |
| Recall | 0.0% | 0.0% | 0.6% | 0.0% |
| F1 | 0.0% | 0.0% | 1.2% | 0.0% |
| F0.5 | 0.0% | 0.0% | 2.8% | 0.0% |
| Specificity | 99.9% | 99.9% | 100.0% | 99.9% |
| Accuracy | 98.0% | 99.1% | 87.8% | 99.9% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-as/out27.txt`
- `out copy/tests-D1-C0/out196.txt`

</details>

### Iteration 15 — Tarantula 0.0533

**Predicate**: `at least 2 Prepare -> Commit where view_no gt view_no, peers issuperset peers` > 0

**Aggregation**: f_true=2, f_false=18, s_true=50, s_false=2330

**Pipeline state at iteration start**: 2400 reports, 79442 aggregations, 1118 filtered aggregations, 20 failed reports.

**Removed runs**: 2

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 0.0% | 0.0% | 100.0% | 0.0% |
| Recall | 0.0% | 0.0% | 0.6% | 0.0% |
| F1 | 0.0% | 0.0% | 1.2% | 0.0% |
| F0.5 | 0.0% | 0.0% | 2.8% | 0.0% |
| Specificity | 99.9% | 99.9% | 100.0% | 99.9% |
| Accuracy | 98.0% | 99.1% | 87.8% | 99.9% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-ss/out146.txt`
- `out copy/tests-D2-C2-as/out146.txt`

</details>

### Iteration 16 — Tarantula 0.0312

**Predicate**: `at least 2 Prepare -> ViewChange where seq_no eq last_seq_no, peers issuperset peers` > 1

**Aggregation**: f_true=8, f_false=10, s_true=333, s_false=2047

**Pipeline state at iteration start**: 2398 reports, 79441 aggregations, 1106 filtered aggregations, 18 failed reports.

**Removed runs**: 8

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 0.0% | 12.5% | 87.5% | 0.0% |
| Recall | 0.0% | 4.5% | 2.0% | 0.0% |
| F1 | 0.0% | 6.7% | 4.0% | 0.0% |
| F0.5 | 0.0% | 9.3% | 9.3% | 0.0% |
| Specificity | 99.7% | 99.7% | 100.0% | 99.7% |
| Accuracy | 97.8% | 99.0% | 87.9% | 99.6% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-ss/out98.txt`
- `out copy/tests-D2-C2-ss/out102.txt`
- `out copy/tests-D1-C2-as/out171.txt`
- `out copy/tests-D1-C2-as/out81.txt`
- `out copy/tests-D1-C1-as/out151.txt`
- `out copy/tests-D2-C1-ss/out43.txt`
- `out copy/tests-D1-C1-ss/out151.txt`
- `out copy/tests-D2-C2-ss/out15.txt`

</details>

### Iteration 17 — Tarantula 0.0080

**Predicate**: `at least 1 PrePrepare -> Commit where view_no eq view_no, seq_no lt seq_no, peers eq peers` > 0

**Aggregation**: f_true=4, f_false=6, s_true=484, s_false=1896

**Pipeline state at iteration start**: 2390 reports, 79440 aggregations, 1628 filtered aggregations, 10 failed reports.

**Removed runs**: 4

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 0.0% | 0.0% | 100.0% | 0.0% |
| Recall | 0.0% | 0.0% | 1.2% | 0.0% |
| F1 | 0.0% | 0.0% | 2.3% | 0.0% |
| F0.5 | 0.0% | 0.0% | 5.6% | 0.0% |
| Specificity | 99.9% | 99.9% | 100.0% | 99.9% |
| Accuracy | 97.9% | 99.1% | 87.9% | 99.8% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-as/out91.txt`
- `out copy/tests-D2-C2-ss/out91.txt`
- `out copy/tests-D2-C2-ss/out71.txt`
- `out copy/tests-D2-C2-as/out71.txt`

</details>

### Iteration 18 — Tarantula 0.0026

**Predicate**: `at least 1 PrePrepare -> ReplicaCommit where view_no eq view_no, seq_no lt seq_no, operation_first eq operation_first` > 1

**Aggregation**: f_true=2, f_false=4, s_true=523, s_false=1857

**Pipeline state at iteration start**: 2386 reports, 79439 aggregations, 2441 filtered aggregations, 6 failed reports.

**Removed runs**: 2

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 100.0% | 0.0% | 0.0% | 0.0% |
| Recall | 3.7% | 0.0% | 0.0% | 0.0% |
| F1 | 7.1% | 0.0% | 0.0% | 0.0% |
| F0.5 | 16.1% | 0.0% | 0.0% | 0.0% |
| Specificity | 100.0% | 99.9% | 99.9% | 99.9% |
| Accuracy | 98.1% | 99.1% | 87.6% | 99.9% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C1-ss/out181.txt`
- `out copy/tests-D2-C1-as/out181.txt`

</details>

### Iteration 19 — Tarantula 0.0024

**Predicate**: `at least 3 Commit -> ReplicaCommit where view_no eq view_no, seq_no lt seq_no` > 3

**Aggregation**: f_true=4, f_false=0, s_true=1394, s_false=986

**Pipeline state at iteration start**: 2384 reports, 79438 aggregations, 2229 filtered aggregations, 4 failed reports.

**Removed runs**: 4

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 100.0% | 0.0% | 0.0% | 0.0% |
| Recall | 7.4% | 0.0% | 0.0% | 0.0% |
| F1 | 13.8% | 0.0% | 0.0% | 0.0% |
| F0.5 | 28.6% | 0.0% | 0.0% | 0.0% |
| Specificity | 100.0% | 99.9% | 99.8% | 99.9% |
| Accuracy | 98.2% | 99.1% | 87.6% | 99.8% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D0-C1-ss/out95.txt`
- `out copy/tests-D0-C1-as/out95.txt`
- `out copy/tests-D1-C2-ss/out100.txt`
- `out copy/tests-D1-C2-as/out100.txt`

</details>

## Per-config bug-class distribution

Counts are static across iterations (the classifier is run once per run path).

| Configuration | Total | Correct | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|---------------|-------|---------|----------------------|-------------------|--------------|-------------|
| d=0 c=1 as | 200 | 196 | 4 | 0 | 0 | 0 |
| d=0 c=1 ss | 200 | 196 | 4 | 0 | 0 | 0 |
| d=0 c=2 as | 200 | 194 | 6 | 0 | 0 | 0 |
| d=0 c=2 ss | 200 | 193 | 6 | 0 | 1 | 0 |
| d=1 c=0 | 200 | 176 | 0 | 0 | 24 | 0 |
| d=1 c=1 as | 200 | 178 | 2 | 0 | 20 | 0 |
| d=1 c=1 ss | 200 | 169 | 4 | 0 | 27 | 0 |
| d=1 c=2 as | 200 | 171 | 6 | 2 | 21 | 0 |
| d=1 c=2 ss | 200 | 169 | 8 | 1 | 22 | 0 |
| d=2 c=0 | 200 | 153 | 0 | 0 | 46 | 1 |
| d=2 c=1 as | 200 | 152 | 2 | 2 | 44 | 0 |
| d=2 c=1 ss | 200 | 153 | 3 | 3 | 42 | 0 |
| d=2 c=2 as | 200 | 143 | 3 | 6 | 48 | 0 |
| d=2 c=2 ss | 200 | 137 | 6 | 8 | 49 | 1 |

**Totals across all configs**: 2800 runs, 2380 correct, 54 Operation Corruption, 22 View-Change Fault, 344 Quorum Stall, 2 Split Brain.
