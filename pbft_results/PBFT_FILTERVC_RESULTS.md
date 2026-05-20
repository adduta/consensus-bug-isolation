# PBFT ISOLATION Results — 5-Class Taxonomy

Dataset: `out copy/` — 2800 runs across 14 configs (200 per config), 2380 correct, 420 failures.

Bug classes: **Operation Corruption (OC)**, **View-Change Fault (VCF)**, **Partition Timeout (PT)**, **Non-PP Mutation (NPP)**, **Split Brain (SB)**.

Iterations: 23 (every failure isolated).

## Iteration summary

| # | Predicate | Tol. | Tarantula | f_true | f_false | s_true | s_false | Removed | Best class | P | R | F1 | F0.5 |
|---|-----------|------|-----------|--------|---------|--------|---------|---------|-----------|---|---|-----|------|
| 1 | `at least 1 PrePrepare -> Prepare where view_no gt view_no` | >2 | 0.8339 | 182 | 238 | 8 | 2372 | 182 | Partition Timeout | 75.8% | 51.7% | 61.5% | 69.3% |
| 2 | `at least 1 PrePrepare -> ReplicaCommit where view_no eq view_no, seq_no eq seq_no, operation_first ne operation_first` | >0 | 0.7750 | 49 | 189 | 3 | 2377 | 49 | Operation Corruption | 87.8% | 79.6% | 83.5% | 86.0% |
| 3 | `at least 3 Prepare -> Prepare where view_no eq view_no, seq_no gt seq_no` | >1 | 0.6879 | 90 | 99 | 49 | 2331 | 90 | Partition Timeout | 68.9% | 23.2% | 34.7% | 49.4% |
| 4 | `at least 1 Prepare -> Prepare where view_no gt view_no, seq_no eq seq_no` | >3 | 0.5279 | 6 | 93 | 1 | 2379 | 6 | Partition Timeout | 83.3% | 1.9% | 3.7% | 8.6% |
| 5 | `at least 2 Prepare -> Commit where seq_no gt seq_no, peers isdisjoint peers` | >3 | 0.4672 | 22 | 71 | 34 | 2346 | 22 | Partition Timeout | 68.2% | 5.6% | 10.4% | 21.1% |
| 6 | `at least 1 PrePrepare -> PrePrepare where seq_no eq seq_no, operation_first ne operation_first` | >2 | 0.4164 | 7 | 64 | 10 | 2370 | 7 | Partition Timeout | 71.4% | 1.9% | 3.6% | 8.5% |
| 7 | `at least 3 Commit -> Commit where view_no eq view_no, seq_no gt seq_no, peers ne peers` | >2 | 0.4161 | 6 | 58 | 8 | 2372 | 6 | Partition Timeout | 83.3% | 1.9% | 3.7% | 8.6% |
| 8 | `at least 2 Commit -> Commit where seq_no gt seq_no, peers isdisjoint peers` | >3 | 0.3476 | 5 | 53 | 10 | 2370 | 5 | Partition Timeout | 60.0% | 1.1% | 2.2% | 5.2% |
| 9 | `at least 2 Prepare -> Prepare where view_no ne view_no, peers issubset peers` | >3 | 0.3293 | 4 | 49 | 8 | 2372 | 4 | Partition Timeout | 75.0% | 1.1% | 2.2% | 5.3% |
| 10 | `at least 1 PrePrepare -> ReplicaCommit where operation_first ne operation_first, operation_second eq operation_second` | >1 | 0.3014 | 2 | 47 | 0 | 2380 | 2 | Operation Corruption | 100.0% | 3.7% | 7.1% | 16.1% |
| 11 | `at least 1 Prepare -> Prepare where view_no gt view_no, seq_no gt seq_no, peers issubset peers` | >1 | 0.2288 | 2 | 45 | 4 | 2376 | 2 | Partition Timeout | 100.0% | 0.7% | 1.5% | 3.6% |
| 12 | `at least 2 Prepare -> Prepare where view_no ne view_no, seq_no gt seq_no, peers eq peers` | >2 | 0.2166 | 2 | 43 | 5 | 2375 | 2 | Partition Timeout | 100.0% | 0.7% | 1.5% | 3.6% |
| 13 | `at least 1 ReplicaCommit -> PrePrepare where seq_no eq seq_no, operation_first ne operation_first` | >1 | 0.1939 | 2 | 41 | 7 | 2373 | 2 | Operation Corruption | 50.0% | 1.9% | 3.6% | 8.1% |
| 14 | `at least 2 Prepare -> Commit where view_no eq view_no, seq_no gt seq_no, peers isdisjoint peers` | >2 | 0.1434 | 2 | 39 | 13 | 2367 | 2 | Partition Timeout | 100.0% | 0.7% | 1.5% | 3.6% |
| 15 | `at least 3 Commit -> Prepare where view_no eq view_no, peers eq peers` | >2 | 0.1309 | 4 | 35 | 38 | 2342 | 4 | Partition Timeout | 50.0% | 0.7% | 1.5% | 3.5% |
| 16 | `at least 1 Prepare -> Commit where view_no eq view_no, seq_no gt seq_no, peers isdisjoint peers` | >3 | 0.0851 | 3 | 32 | 44 | 2336 | 3 | Partition Timeout | 100.0% | 1.1% | 2.2% | 5.4% |
| 17 | `at least 1 Commit -> Commit where view_no eq view_no, seq_no gt seq_no, peers isdisjoint peers` | >1 | 0.0816 | 2 | 30 | 29 | 2351 | 2 | Non-PP Mutation | 100.0% | 2.6% | 5.1% | 11.8% |
| 18 | `at least 2 Commit -> Prepare where view_no ne view_no, seq_no lt seq_no, peers isdisjoint peers` | >3 | 0.0667 | 4 | 26 | 78 | 2302 | 4 | Partition Timeout | 100.0% | 1.5% | 3.0% | 7.1% |
| 19 | `at least 2 Prepare -> Commit where view_no gt view_no, peers issuperset peers` | >0 | 0.0489 | 2 | 24 | 50 | 2330 | 2 | Non-PP Mutation | 100.0% | 2.6% | 5.1% | 11.8% |
| 20 | `at least 2 Commit -> Prepare where seq_no gt seq_no, peers isdisjoint peers` | >2 | 0.0333 | 5 | 19 | 179 | 2201 | 5 | Partition Timeout | 80.0% | 1.5% | 2.9% | 7.0% |
| 21 | `at least 1 PrePrepare -> Commit where view_no eq view_no, seq_no lt seq_no, peers eq peers` | >0 | 0.0204 | 9 | 10 | 484 | 1896 | 9 | Partition Timeout | 66.7% | 2.2% | 4.3% | 9.9% |
| 22 | `at least 1 Prepare -> Prepare where view_no eq view_no, seq_no lt seq_no, peers isdisjoint peers` | >0 | 0.0048 | 4 | 6 | 603 | 1777 | 4 | Operation Corruption | 50.0% | 3.7% | 6.9% | 14.3% |
| 23 | `at least 1 PrePrepare -> ReplicaCommit where view_no eq view_no, seq_no lt seq_no, operation_first ne operation_first` | >2 | 0.0013 | 5 | 1 | 1569 | 811 | 1 | View-Change Fault | 100.0% | 4.5% | 8.7% | 19.2% |

## Detailed iteration breakdown

### Iteration 1 — Tarantula 0.8339

**Predicate**: `at least 1 PrePrepare -> Prepare where view_no gt view_no` > 2

**Aggregation**: f_true=182, f_false=238, s_true=8, s_false=2372

**Pipeline state at iteration start**: 2800 reports, 64608 aggregations, 13085 filtered aggregations, 420 failed reports.

**Removed runs**: 182

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 3.8% | 75.8% | 20.3% | 0.0% |
| Recall | 0.0% | 31.8% | 51.7% | 48.1% | 0.0% |
| F1 | 0.0% | 6.9% | 61.5% | 28.6% | 0.0% |
| F0.5 | 0.0% | 4.7% | 69.3% | 23.0% | 0.0% |
| Specificity | 93.4% | 93.7% | 98.3% | 94.7% | 93.5% |
| Accuracy | 91.6% | 93.2% | 93.8% | 93.4% | 93.4% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D1-C1-as/out66.txt`
- `out copy/tests-D1-C0/out166.txt`
- `out copy/tests-D1-C0/out41.txt`
- `out copy/tests-D2-C1-as/out145.txt`
- `out copy/tests-D2-C1-as/out96.txt`
- `out copy/tests-D2-C2-as/out20.txt`
- `out copy/tests-D2-C2-as/out60.txt`
- `out copy/tests-D1-C0/out115.txt`
- `out copy/tests-D2-C2-as/out14.txt`
- `out copy/tests-D1-C1-ss/out115.txt`
- `out copy/tests-D2-C1-as/out87.txt`
- `out copy/tests-D2-C2-ss/out163.txt`
- `out copy/tests-D2-C1-ss/out119.txt`
- `out copy/tests-D2-C1-ss/out37.txt`
- `out copy/tests-D1-C0/out11.txt`
- `out copy/tests-D1-C2-as/out156.txt`
- `out copy/tests-D2-C1-ss/out33.txt`
- `out copy/tests-D1-C2-ss/out60.txt`
- `out copy/tests-D2-C0/out7.txt`
- `out copy/tests-D2-C1-ss/out137.txt`
- `out copy/tests-D1-C1-ss/out93.txt`
- `out copy/tests-D1-C2-as/out11.txt`
- `out copy/tests-D1-C1-as/out11.txt`
- `out copy/tests-D2-C2-ss/out186.txt`
- `out copy/tests-D1-C1-ss/out56.txt`
- `out copy/tests-D2-C2-as/out140.txt`
- `out copy/tests-D1-C0/out77.txt`
- `out copy/tests-D2-C2-ss/out178.txt`
- `out copy/tests-D2-C2-ss/out153.txt`
- `out copy/tests-D2-C0/out185.txt`
- `out copy/tests-D2-C1-as/out162.txt`
- `out copy/tests-D1-C2-as/out53.txt`
- `out copy/tests-D2-C0/out51.txt`
- `out copy/tests-D2-C2-ss/out27.txt`
- `out copy/tests-D1-C1-as/out79.txt`
- `out copy/tests-D2-C1-ss/out196.txt`
- `out copy/tests-D2-C2-as/out94.txt`
- `out copy/tests-D1-C1-as/out174.txt`
- `out copy/tests-D2-C1-ss/out20.txt`
- `out copy/tests-D1-C1-ss/out79.txt`
- `out copy/tests-D2-C2-ss/out77.txt`
- `out copy/tests-D1-C2-as/out73.txt`
- `out copy/tests-D1-C0/out107.txt`
- `out copy/tests-D1-C2-as/out19.txt`
- `out copy/tests-D2-C2-as/out73.txt`
- `out copy/tests-D2-C0/out151.txt`
- `out copy/tests-D2-C2-ss/out60.txt`
- `out copy/tests-D1-C1-ss/out90.txt`
- `out copy/tests-D2-C2-as/out7.txt`
- `out copy/tests-D2-C0/out14.txt`
- `out copy/tests-D2-C1-as/out119.txt`
- `out copy/tests-D1-C2-as/out137.txt`
- `out copy/tests-D1-C1-as/out95.txt`
- `out copy/tests-D2-C1-as/out132.txt`
- `out copy/tests-D1-C1-ss/out170.txt`
- `out copy/tests-D2-C1-as/out52.txt`
- `out copy/tests-D1-C1-ss/out137.txt`
- `out copy/tests-D1-C1-ss/out94.txt`
- `out copy/tests-D1-C1-ss/out103.txt`
- `out copy/tests-D2-C1-as/out44.txt`
- `out copy/tests-D2-C1-ss/out19.txt`
- `out copy/tests-D2-C1-ss/out178.txt`
- `out copy/tests-D1-C1-ss/out195.txt`
- `out copy/tests-D2-C1-as/out123.txt`
- `out copy/tests-D1-C2-as/out149.txt`
- `out copy/tests-D1-C1-as/out27.txt`
- `out copy/tests-D1-C2-as/out103.txt`
- `out copy/tests-D1-C2-ss/out156.txt`
- `out copy/tests-D1-C2-ss/out56.txt`
- `out copy/tests-D2-C0/out87.txt`
- `out copy/tests-D2-C2-as/out45.txt`
- `out copy/tests-D2-C1-as/out160.txt`
- `out copy/tests-D2-C0/out20.txt`
- `out copy/tests-D2-C0/out99.txt`
- `out copy/tests-D2-C1-as/out136.txt`
- `out copy/tests-D1-C2-ss/out11.txt`
- `out copy/tests-D1-C1-as/out119.txt`
- `out copy/tests-D1-C1-as/out123.txt`
- `out copy/tests-D1-C0/out36.txt`
- `out copy/tests-D2-C2-ss/out119.txt`
- `out copy/tests-D1-C0/out73.txt`
- `out copy/tests-D2-C1-ss/out110.txt`
- `out copy/tests-D2-C1-ss/out40.txt`
- `out copy/tests-D2-C2-ss/out7.txt`
- `out copy/tests-D1-C1-ss/out199.txt`
- `out copy/tests-D2-C2-as/out110.txt`
- `out copy/tests-D1-C1-ss/out119.txt`
- `out copy/tests-D1-C2-as/out36.txt`
- `out copy/tests-D1-C2-ss/out123.txt`
- `out copy/tests-D1-C1-ss/out3.txt`
- `out copy/tests-D1-C0/out133.txt`
- `out copy/tests-D1-C2-as/out86.txt`
- `out copy/tests-D2-C2-as/out132.txt`
- `out copy/tests-D2-C0/out61.txt`
- `out copy/tests-D2-C1-ss/out44.txt`
- `out copy/tests-D1-C1-ss/out174.txt`
- `out copy/tests-D1-C2-ss/out41.txt`
- `out copy/tests-D2-C1-ss/out26.txt`
- `out copy/tests-D1-C1-ss/out186.txt`
- `out copy/tests-D1-C0/out3.txt`
- `out copy/tests-D2-C0/out144.txt`
- `out copy/tests-D2-C0/out136.txt`
- `out copy/tests-D1-C2-ss/out157.txt`
- `out copy/tests-D2-C0/out96.txt`
- `out copy/tests-D2-C2-as/out77.txt`
- `out copy/tests-D2-C1-as/out53.txt`
- `out copy/tests-D2-C2-as/out36.txt`
- `out copy/tests-D2-C2-ss/out140.txt`
- `out copy/tests-D2-C0/out123.txt`
- `out copy/tests-D2-C2-as/out157.txt`
- `out copy/tests-D2-C1-ss/out77.txt`
- `out copy/tests-D1-C1-ss/out15.txt`
- `out copy/tests-D1-C0/out182.txt`
- `out copy/tests-D1-C2-ss/out149.txt`
- `out copy/tests-D1-C1-ss/out37.txt`
- `out copy/tests-D1-C2-as/out145.txt`
- `out copy/tests-D1-C1-as/out146.txt`
- `out copy/tests-D1-C2-ss/out93.txt`
- `out copy/tests-D1-C2-as/out93.txt`
- `out copy/tests-D2-C2-as/out96.txt`
- `out copy/tests-D2-C1-as/out14.txt`
- `out copy/tests-D2-C2-as/out99.txt`
- `out copy/tests-D2-C1-as/out192.txt`
- `out copy/tests-D1-C2-ss/out146.txt`
- `out copy/tests-D2-C1-ss/out58.txt`
- `out copy/tests-D1-C0/out141.txt`
- `out copy/tests-D2-C2-ss/out199.txt`
- `out copy/tests-D2-C2-as/out178.txt`
- `out copy/tests-D1-C1-as/out166.txt`
- `out copy/tests-D1-C0/out186.txt`
- `out copy/tests-D2-C2-as/out24.txt`
- `out copy/tests-D2-C2-ss/out56.txt`
- `out copy/tests-D1-C2-ss/out94.txt`
- `out copy/tests-D2-C2-as/out19.txt`
- `out copy/tests-D2-C2-ss/out36.txt`
- `out copy/tests-D1-C0/out123.txt`
- `out copy/tests-D1-C0/out95.txt`
- `out copy/tests-D1-C2-ss/out140.txt`
- `out copy/tests-D2-C1-ss/out186.txt`
- `out copy/tests-D1-C1-ss/out27.txt`
- `out copy/tests-D2-C0/out56.txt`
- `out copy/tests-D1-C2-ss/out116.txt`
- `out copy/tests-D2-C1-as/out19.txt`
- `out copy/tests-D1-C0/out49.txt`
- `out copy/tests-D1-C0/out157.txt`
- `out copy/tests-D2-C1-ss/out9.txt`
- `out copy/tests-D1-C1-as/out157.txt`
- `out copy/tests-D2-C1-ss/out140.txt`
- `out copy/tests-D1-C2-as/out15.txt`
- `out copy/tests-D2-C2-as/out153.txt`
- `out copy/tests-D2-C2-as/out159.txt`
- `out copy/tests-D2-C2-ss/out196.txt`
- `out copy/tests-D1-C2-as/out133.txt`
- `out copy/tests-D2-C1-as/out66.txt`
- `out copy/tests-D1-C0/out146.txt`
- `out copy/tests-D1-C2-ss/out99.txt`
- `out copy/tests-D1-C1-ss/out145.txt`
- `out copy/tests-D1-C2-ss/out73.txt`
- `out copy/tests-D1-C2-ss/out19.txt`
- `out copy/tests-D1-C1-ss/out44.txt`
- `out copy/tests-D1-C1-as/out178.txt`
- `out copy/tests-D2-C1-as/out18.txt`
- `out copy/tests-D2-C1-as/out149.txt`
- `out copy/tests-D2-C1-as/out79.txt`
- `out copy/tests-D1-C1-as/out141.txt`
- `out copy/tests-D2-C2-ss/out104.txt`
- `out copy/tests-D2-C2-ss/out141.txt`
- `out copy/tests-D1-C2-ss/out44.txt`
- `out copy/tests-D2-C2-as/out37.txt`
- `out copy/tests-D2-C1-ss/out179.txt`
- `out copy/tests-D2-C1-ss/out123.txt`
- `out copy/tests-D2-C2-ss/out20.txt`
- `out copy/tests-D2-C0/out186.txt`
- `out copy/tests-D1-C2-as/out49.txt`
- `out copy/tests-D0-C2-ss/out191.txt`
- `out copy/tests-D2-C1-ss/out73.txt`
- `out copy/tests-D2-C0/out37.txt`
- `out copy/tests-D2-C1-ss/out79.txt`
- `out copy/tests-D1-C1-as/out57.txt`
- `out copy/tests-D2-C2-ss/out190.txt`
- `out copy/tests-D1-C2-as/out33.txt`
- `out copy/tests-D2-C2-ss/out19.txt`

</details>

### Iteration 2 — Tarantula 0.7750

**Predicate**: `at least 1 PrePrepare -> ReplicaCommit where view_no eq view_no, seq_no eq seq_no, operation_first ne operation_first` > 0

**Aggregation**: f_true=49, f_false=189, s_true=3, s_false=2377

**Pipeline state at iteration start**: 2618 reports, 64607 aggregations, 12238 filtered aggregations, 238 failed reports.

**Removed runs**: 49

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 87.8% | 2.0% | 10.2% | 0.0% | 0.0% |
| Recall | 79.6% | 4.5% | 1.9% | 0.0% | 0.0% |
| F1 | 83.5% | 2.8% | 3.2% | 0.0% | 0.0% |
| F0.5 | 86.0% | 2.3% | 5.4% | 0.0% | 0.0% |
| Specificity | 99.8% | 98.3% | 98.3% | 98.2% | 98.2% |
| Accuracy | 99.4% | 97.5% | 89.1% | 95.5% | 98.2% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-ss/out143.txt`
- `out copy/tests-D0-C1-as/out108.txt`
- `out copy/tests-D0-C1-ss/out143.txt`
- `out copy/tests-D2-C1-ss/out41.txt`
- `out copy/tests-D1-C1-ss/out136.txt`
- `out copy/tests-D1-C1-ss/out143.txt`
- `out copy/tests-D0-C2-ss/out148.txt`
- `out copy/tests-D0-C2-ss/out93.txt`
- `out copy/tests-D2-C2-as/out181.txt`
- `out copy/tests-D0-C1-as/out143.txt`
- `out copy/tests-D0-C1-ss/out108.txt`
- `out copy/tests-D2-C1-ss/out100.txt`
- `out copy/tests-D1-C2-ss/out7.txt`
- `out copy/tests-D2-C2-ss/out16.txt`
- `out copy/tests-D1-C2-ss/out120.txt`
- `out copy/tests-D1-C2-ss/out167.txt`
- `out copy/tests-D1-C2-as/out109.txt`
- `out copy/tests-D0-C2-as/out126.txt`
- `out copy/tests-D0-C2-as/out95.txt`
- `out copy/tests-D1-C2-as/out43.txt`
- `out copy/tests-D1-C2-ss/out109.txt`
- `out copy/tests-D0-C2-as/out91.txt`
- `out copy/tests-D2-C2-as/out48.txt`
- `out copy/tests-D2-C1-as/out121.txt`
- `out copy/tests-D1-C2-as/out120.txt`
- `out copy/tests-D2-C2-ss/out176.txt`
- `out copy/tests-D2-C0/out41.txt`
- `out copy/tests-D0-C2-as/out100.txt`
- `out copy/tests-D1-C1-ss/out109.txt`
- `out copy/tests-D0-C2-ss/out100.txt`
- `out copy/tests-D2-C2-as/out66.txt`
- `out copy/tests-D0-C1-ss/out121.txt`
- `out copy/tests-D1-C2-ss/out43.txt`
- `out copy/tests-D1-C2-as/out126.txt`
- `out copy/tests-D2-C2-ss/out100.txt`
- `out copy/tests-D1-C2-ss/out126.txt`
- `out copy/tests-D0-C2-ss/out126.txt`
- `out copy/tests-D2-C2-ss/out181.txt`
- `out copy/tests-D1-C2-as/out130.txt`
- `out copy/tests-D2-C2-ss/out40.txt`
- `out copy/tests-D0-C2-as/out148.txt`
- `out copy/tests-D0-C2-ss/out91.txt`
- `out copy/tests-D0-C2-as/out93.txt`
- `out copy/tests-D1-C2-ss/out130.txt`
- `out copy/tests-D0-C1-as/out121.txt`
- `out copy/tests-D0-C2-ss/out95.txt`
- `out copy/tests-D1-C1-as/out109.txt`
- `out copy/tests-D2-C2-as/out143.txt`
- `out copy/tests-D2-C1-as/out100.txt`

</details>

### Iteration 3 — Tarantula 0.6879

**Predicate**: `at least 3 Prepare -> Prepare where view_no eq view_no, seq_no gt seq_no` > 1

**Aggregation**: f_true=90, f_false=99, s_true=49, s_false=2331

**Pipeline state at iteration start**: 2569 reports, 64606 aggregations, 12047 filtered aggregations, 189 failed reports.

**Removed runs**: 90

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 2.2% | 10.0% | 68.9% | 20.0% | 1.1% |
| Recall | 3.7% | 40.9% | 23.2% | 23.4% | 50.0% |
| F1 | 2.8% | 16.1% | 34.7% | 21.6% | 2.2% |
| F0.5 | 2.4% | 11.8% | 49.4% | 20.6% | 1.4% |
| Specificity | 96.8% | 97.1% | 98.9% | 97.4% | 96.8% |
| Accuracy | 95.0% | 96.6% | 91.7% | 95.3% | 96.8% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D1-C2-ss/out145.txt`
- `out copy/tests-D2-C2-as/out9.txt`
- `out copy/tests-D2-C2-as/out129.txt`
- `out copy/tests-D2-C0/out6.txt`
- `out copy/tests-D2-C1-as/out41.txt`
- `out copy/tests-D2-C1-as/out9.txt`
- `out copy/tests-D2-C0/out9.txt`
- `out copy/tests-D2-C2-ss/out197.txt`
- `out copy/tests-D2-C2-ss/out31.txt`
- `out copy/tests-D2-C2-ss/out156.txt`
- `out copy/tests-D2-C1-as/out197.txt`
- `out copy/tests-D2-C2-ss/out41.txt`
- `out copy/tests-D2-C0/out199.txt`
- `out copy/tests-D2-C2-ss/out151.txt`
- `out copy/tests-D1-C1-ss/out53.txt`
- `out copy/tests-D2-C0/out73.txt`
- `out copy/tests-D2-C2-as/out52.txt`
- `out copy/tests-D2-C0/out159.txt`
- `out copy/tests-D2-C2-ss/out185.txt`
- `out copy/tests-D2-C0/out66.txt`
- `out copy/tests-D1-C1-ss/out85.txt`
- `out copy/tests-D2-C1-ss/out59.txt`
- `out copy/tests-D1-C2-as/out196.txt`
- `out copy/tests-D2-C2-as/out141.txt`
- `out copy/tests-D2-C0/out59.txt`
- `out copy/tests-D1-C2-as/out48.txt`
- `out copy/tests-D2-C1-as/out26.txt`
- `out copy/tests-D1-C1-as/out103.txt`
- `out copy/tests-D2-C1-ss/out151.txt`
- `out copy/tests-D2-C2-as/out156.txt`
- `out copy/tests-D2-C1-ss/out191.txt`
- `out copy/tests-D1-C0/out15.txt`
- `out copy/tests-D2-C1-ss/out175.txt`
- `out copy/tests-D2-C1-as/out159.txt`
- `out copy/tests-D1-C0/out170.txt`
- `out copy/tests-D2-C1-as/out40.txt`
- `out copy/tests-D2-C1-as/out191.txt`
- `out copy/tests-D2-C2-ss/out79.txt`
- `out copy/tests-D2-C1-ss/out66.txt`
- `out copy/tests-D2-C2-as/out175.txt`
- `out copy/tests-D2-C1-as/out175.txt`
- `out copy/tests-D2-C1-ss/out159.txt`
- `out copy/tests-D2-C0/out178.txt`
- `out copy/tests-D1-C0/out136.txt`
- `out copy/tests-D2-C2-ss/out95.txt`
- `out copy/tests-D2-C1-as/out99.txt`
- `out copy/tests-D2-C2-as/out43.txt`
- `out copy/tests-D2-C2-as/out59.txt`
- `out copy/tests-D2-C0/out40.txt`
- `out copy/tests-D2-C0/out43.txt`
- `out copy/tests-D2-C2-as/out79.txt`
- `out copy/tests-D2-C1-ss/out51.txt`
- `out copy/tests-D2-C1-ss/out185.txt`
- `out copy/tests-D2-C2-as/out27.txt`
- `out copy/tests-D2-C1-ss/out129.txt`
- `out copy/tests-D2-C0/out175.txt`
- `out copy/tests-D2-C2-ss/out52.txt`
- `out copy/tests-D2-C2-ss/out96.txt`
- `out copy/tests-D2-C1-ss/out162.txt`
- `out copy/tests-D2-C0/out90.txt`
- `out copy/tests-D2-C1-ss/out95.txt`
- `out copy/tests-D2-C1-as/out151.txt`
- `out copy/tests-D2-C2-ss/out87.txt`
- `out copy/tests-D1-C1-ss/out7.txt`
- `out copy/tests-D2-C0/out79.txt`
- `out copy/tests-D2-C0/out115.txt`
- `out copy/tests-D2-C2-as/out104.txt`
- `out copy/tests-D2-C1-ss/out18.txt`
- `out copy/tests-D2-C2-as/out41.txt`
- `out copy/tests-D2-C2-as/out136.txt`
- `out copy/tests-D1-C2-as/out41.txt`
- `out copy/tests-D2-C2-as/out6.txt`
- `out copy/tests-D2-C2-as/out135.txt`
- `out copy/tests-D2-C2-as/out95.txt`
- `out copy/tests-D2-C1-as/out59.txt`
- `out copy/tests-D2-C1-ss/out136.txt`
- `out copy/tests-D2-C2-as/out68.txt`
- `out copy/tests-D1-C2-ss/out196.txt`
- `out copy/tests-D2-C2-ss/out175.txt`
- `out copy/tests-D2-C1-ss/out52.txt`
- `out copy/tests-D1-C1-as/out36.txt`
- `out copy/tests-D2-C2-as/out26.txt`
- `out copy/tests-D2-C0/out129.txt`
- `out copy/tests-D2-C2-as/out197.txt`
- `out copy/tests-D2-C0/out18.txt`
- `out copy/tests-D2-C0/out50.txt`
- `out copy/tests-D2-C2-ss/out57.txt`
- `out copy/tests-D2-C1-as/out95.txt`
- `out copy/tests-D2-C1-as/out6.txt`
- `out copy/tests-D2-C1-as/out43.txt`

</details>

### Iteration 4 — Tarantula 0.5279

**Predicate**: `at least 1 Prepare -> Prepare where view_no gt view_no, seq_no eq seq_no` > 3

**Aggregation**: f_true=6, f_false=93, s_true=1, s_false=2379

**Pipeline state at iteration start**: 2479 reports, 64605 aggregations, 10818 filtered aggregations, 99 failed reports.

**Removed runs**: 6

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 0.0% | 83.3% | 16.7% | 0.0% |
| Recall | 0.0% | 0.0% | 1.9% | 1.3% | 0.0% |
| F1 | 0.0% | 0.0% | 3.7% | 2.4% | 0.0% |
| F0.5 | 0.0% | 0.0% | 8.6% | 5.0% | 0.0% |
| Specificity | 99.8% | 99.8% | 100.0% | 99.8% | 99.8% |
| Accuracy | 97.9% | 99.0% | 90.6% | 97.1% | 99.7% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C1-as/out20.txt`
- `out copy/tests-D1-C2-as/out190.txt`
- `out copy/tests-D2-C2-ss/out3.txt`
- `out copy/tests-D1-C2-ss/out36.txt`
- `out copy/tests-D2-C2-ss/out51.txt`
- `out copy/tests-D2-C0/out137.txt`

</details>

### Iteration 5 — Tarantula 0.4672

**Predicate**: `at least 2 Prepare -> Commit where seq_no gt seq_no, peers isdisjoint peers` > 3

**Aggregation**: f_true=22, f_false=71, s_true=34, s_false=2346

**Pipeline state at iteration start**: 2473 reports, 64604 aggregations, 10632 filtered aggregations, 93 failed reports.

**Removed runs**: 22

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 0.0% | 68.2% | 27.3% | 4.5% |
| Recall | 0.0% | 0.0% | 5.6% | 7.8% | 50.0% |
| F1 | 0.0% | 0.0% | 10.4% | 12.1% | 8.3% |
| F0.5 | 0.0% | 0.0% | 21.1% | 18.2% | 5.6% |
| Specificity | 99.2% | 99.2% | 99.7% | 99.4% | 99.2% |
| Accuracy | 97.3% | 98.4% | 90.8% | 96.9% | 99.2% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D1-C0/out57.txt`
- `out copy/tests-D2-C2-ss/out136.txt`
- `out copy/tests-D2-C2-ss/out53.txt`
- `out copy/tests-D1-C1-as/out90.txt`
- `out copy/tests-D2-C1-ss/out153.txt`
- `out copy/tests-D1-C2-as/out136.txt`
- `out copy/tests-D2-C2-ss/out184.txt`
- `out copy/tests-D1-C0/out116.txt`
- `out copy/tests-D2-C0/out36.txt`
- `out copy/tests-D2-C1-as/out157.txt`
- `out copy/tests-D2-C1-ss/out12.txt`
- `out copy/tests-D2-C1-ss/out6.txt`
- `out copy/tests-D2-C0/out156.txt`
- `out copy/tests-D2-C1-as/out174.txt`
- `out copy/tests-D2-C2-as/out192.txt`
- `out copy/tests-D2-C1-as/out168.txt`
- `out copy/tests-D2-C0/out112.txt`
- `out copy/tests-D2-C1-ss/out174.txt`
- `out copy/tests-D2-C2-as/out116.txt`
- `out copy/tests-D2-C2-ss/out89.txt`
- `out copy/tests-D1-C2-ss/out66.txt`
- `out copy/tests-D1-C2-ss/out170.txt`

</details>

### Iteration 6 — Tarantula 0.4164

**Predicate**: `at least 1 PrePrepare -> PrePrepare where seq_no eq seq_no, operation_first ne operation_first` > 2

**Aggregation**: f_true=7, f_false=64, s_true=10, s_false=2370

**Pipeline state at iteration start**: 2451 reports, 64603 aggregations, 10153 filtered aggregations, 71 failed reports.

**Removed runs**: 7

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 28.6% | 71.4% | 0.0% | 0.0% |
| Recall | 0.0% | 9.1% | 1.9% | 0.0% | 0.0% |
| F1 | 0.0% | 13.8% | 3.6% | 0.0% | 0.0% |
| F0.5 | 0.0% | 20.0% | 8.5% | 0.0% | 0.0% |
| Specificity | 99.7% | 99.8% | 99.9% | 99.7% | 99.7% |
| Accuracy | 97.8% | 99.1% | 90.6% | 97.0% | 99.7% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-ss/out194.txt`
- `out copy/tests-D2-C1-as/out187.txt`
- `out copy/tests-D2-C1-ss/out121.txt`
- `out copy/tests-D2-C2-ss/out58.txt`
- `out copy/tests-D2-C2-as/out194.txt`
- `out copy/tests-D2-C1-as/out194.txt`
- `out copy/tests-D2-C1-as/out114.txt`

</details>

### Iteration 7 — Tarantula 0.4161

**Predicate**: `at least 3 Commit -> Commit where view_no eq view_no, seq_no gt seq_no, peers ne peers` > 2

**Aggregation**: f_true=6, f_false=58, s_true=8, s_false=2372

**Pipeline state at iteration start**: 2444 reports, 64602 aggregations, 9770 filtered aggregations, 64 failed reports.

**Removed runs**: 6

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 0.0% | 83.3% | 16.7% | 0.0% |
| Recall | 0.0% | 0.0% | 1.9% | 1.3% | 0.0% |
| F1 | 0.0% | 0.0% | 3.7% | 2.4% | 0.0% |
| F0.5 | 0.0% | 0.0% | 8.6% | 5.0% | 0.0% |
| Specificity | 99.8% | 99.8% | 100.0% | 99.8% | 99.8% |
| Accuracy | 97.9% | 99.0% | 90.6% | 97.1% | 99.7% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-ss/out11.txt`
- `out copy/tests-D2-C1-ss/out99.txt`
- `out copy/tests-D2-C2-as/out18.txt`
- `out copy/tests-D2-C0/out166.txt`
- `out copy/tests-D2-C2-ss/out43.txt`
- `out copy/tests-D1-C1-ss/out182.txt`

</details>

### Iteration 8 — Tarantula 0.3476

**Predicate**: `at least 2 Commit -> Commit where seq_no gt seq_no, peers isdisjoint peers` > 3

**Aggregation**: f_true=5, f_false=53, s_true=10, s_false=2370

**Pipeline state at iteration start**: 2438 reports, 64601 aggregations, 9573 filtered aggregations, 58 failed reports.

**Removed runs**: 5

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 0.0% | 60.0% | 40.0% | 0.0% |
| Recall | 0.0% | 0.0% | 1.1% | 2.6% | 0.0% |
| F1 | 0.0% | 0.0% | 2.2% | 4.9% | 0.0% |
| F0.5 | 0.0% | 0.0% | 5.2% | 10.3% | 0.0% |
| Specificity | 99.8% | 99.8% | 99.9% | 99.9% | 99.8% |
| Accuracy | 97.9% | 99.0% | 90.5% | 97.2% | 99.8% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C1-as/out16.txt`
- `out copy/tests-D2-C0/out174.txt`
- `out copy/tests-D2-C0/out187.txt`
- `out copy/tests-D2-C2-ss/out4.txt`
- `out copy/tests-D2-C2-ss/out137.txt`

</details>

### Iteration 9 — Tarantula 0.3293

**Predicate**: `at least 2 Prepare -> Prepare where view_no ne view_no, peers issubset peers` > 3

**Aggregation**: f_true=4, f_false=49, s_true=8, s_false=2372

**Pipeline state at iteration start**: 2433 reports, 64600 aggregations, 9385 filtered aggregations, 53 failed reports.

**Removed runs**: 4

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 0.0% | 75.0% | 25.0% | 0.0% |
| Recall | 0.0% | 0.0% | 1.1% | 1.3% | 0.0% |
| F1 | 0.0% | 0.0% | 2.2% | 2.5% | 0.0% |
| F0.5 | 0.0% | 0.0% | 5.3% | 5.4% | 0.0% |
| Specificity | 99.9% | 99.9% | 100.0% | 99.9% | 99.9% |
| Accuracy | 97.9% | 99.1% | 90.5% | 97.2% | 99.8% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D1-C2-ss/out174.txt`
- `out copy/tests-D2-C1-as/out12.txt`
- `out copy/tests-D1-C1-as/out7.txt`
- `out copy/tests-D1-C1-ss/out178.txt`

</details>

### Iteration 10 — Tarantula 0.3014

**Predicate**: `at least 1 PrePrepare -> ReplicaCommit where operation_first ne operation_first, operation_second eq operation_second` > 1

**Aggregation**: f_true=2, f_false=47, s_true=0, s_false=2380

**Pipeline state at iteration start**: 2429 reports, 64599 aggregations, 8952 filtered aggregations, 49 failed reports.

**Removed runs**: 2

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Recall | 3.7% | 0.0% | 0.0% | 0.0% | 0.0% |
| F1 | 7.1% | 0.0% | 0.0% | 0.0% | 0.0% |
| F0.5 | 16.1% | 0.0% | 0.0% | 0.0% | 0.0% |
| Specificity | 100.0% | 99.9% | 99.9% | 99.9% | 99.9% |
| Accuracy | 98.1% | 99.1% | 90.4% | 97.2% | 99.9% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-ss/out64.txt`
- `out copy/tests-D1-C1-as/out136.txt`

</details>

### Iteration 11 — Tarantula 0.2288

**Predicate**: `at least 1 Prepare -> Prepare where view_no gt view_no, seq_no gt seq_no, peers issubset peers` > 1

**Aggregation**: f_true=2, f_false=45, s_true=4, s_false=2376

**Pipeline state at iteration start**: 2427 reports, 64598 aggregations, 8707 filtered aggregations, 47 failed reports.

**Removed runs**: 2

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 0.0% | 100.0% | 0.0% | 0.0% |
| Recall | 0.0% | 0.0% | 0.7% | 0.0% | 0.0% |
| F1 | 0.0% | 0.0% | 1.5% | 0.0% | 0.0% |
| F0.5 | 0.0% | 0.0% | 3.6% | 0.0% | 0.0% |
| Specificity | 99.9% | 99.9% | 100.0% | 99.9% | 99.9% |
| Accuracy | 98.0% | 99.1% | 90.5% | 97.2% | 99.9% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-ss/out129.txt`
- `out copy/tests-D2-C2-ss/out132.txt`

</details>

### Iteration 12 — Tarantula 0.2166

**Predicate**: `at least 2 Prepare -> Prepare where view_no ne view_no, seq_no gt seq_no, peers eq peers` > 2

**Aggregation**: f_true=2, f_false=43, s_true=5, s_false=2375

**Pipeline state at iteration start**: 2425 reports, 64597 aggregations, 8506 filtered aggregations, 45 failed reports.

**Removed runs**: 2

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 0.0% | 100.0% | 0.0% | 0.0% |
| Recall | 0.0% | 0.0% | 0.7% | 0.0% | 0.0% |
| F1 | 0.0% | 0.0% | 1.5% | 0.0% | 0.0% |
| F0.5 | 0.0% | 0.0% | 3.6% | 0.0% | 0.0% |
| Specificity | 99.9% | 99.9% | 100.0% | 99.9% | 99.9% |
| Accuracy | 98.0% | 99.1% | 90.5% | 97.2% | 99.9% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C0/out30.txt`
- `out copy/tests-D1-C1-ss/out112.txt`

</details>

### Iteration 13 — Tarantula 0.1939

**Predicate**: `at least 1 ReplicaCommit -> PrePrepare where seq_no eq seq_no, operation_first ne operation_first` > 1

**Aggregation**: f_true=2, f_false=41, s_true=7, s_false=2373

**Pipeline state at iteration start**: 2423 reports, 64596 aggregations, 7996 filtered aggregations, 43 failed reports.

**Removed runs**: 2

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 50.0% | 0.0% | 50.0% | 0.0% | 0.0% |
| Recall | 1.9% | 0.0% | 0.4% | 0.0% | 0.0% |
| F1 | 3.6% | 0.0% | 0.7% | 0.0% | 0.0% |
| F0.5 | 8.1% | 0.0% | 1.8% | 0.0% | 0.0% |
| Specificity | 100.0% | 99.9% | 100.0% | 99.9% | 99.9% |
| Accuracy | 98.1% | 99.1% | 90.5% | 97.2% | 99.9% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-as/out112.txt`
- `out copy/tests-D2-C2-ss/out15.txt`

</details>

### Iteration 14 — Tarantula 0.1434

**Predicate**: `at least 2 Prepare -> Commit where view_no eq view_no, seq_no gt seq_no, peers isdisjoint peers` > 2

**Aggregation**: f_true=2, f_false=39, s_true=13, s_false=2367

**Pipeline state at iteration start**: 2421 reports, 64595 aggregations, 7712 filtered aggregations, 41 failed reports.

**Removed runs**: 2

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 0.0% | 100.0% | 0.0% | 0.0% |
| Recall | 0.0% | 0.0% | 0.7% | 0.0% | 0.0% |
| F1 | 0.0% | 0.0% | 1.5% | 0.0% | 0.0% |
| F0.5 | 0.0% | 0.0% | 3.6% | 0.0% | 0.0% |
| Specificity | 99.9% | 99.9% | 100.0% | 99.9% | 99.9% |
| Accuracy | 98.0% | 99.1% | 90.5% | 97.2% | 99.9% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C1-ss/out11.txt`
- `out copy/tests-D2-C2-as/out191.txt`

</details>

### Iteration 15 — Tarantula 0.1309

**Predicate**: `at least 3 Commit -> Prepare where view_no eq view_no, peers eq peers` > 2

**Aggregation**: f_true=4, f_false=35, s_true=38, s_false=2342

**Pipeline state at iteration start**: 2419 reports, 64594 aggregations, 7489 filtered aggregations, 39 failed reports.

**Removed runs**: 4

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 25.0% | 50.0% | 25.0% | 0.0% |
| Recall | 0.0% | 4.5% | 0.7% | 1.3% | 0.0% |
| F1 | 0.0% | 7.7% | 1.5% | 2.5% | 0.0% |
| F0.5 | 0.0% | 13.2% | 3.5% | 5.4% | 0.0% |
| Specificity | 99.9% | 99.9% | 99.9% | 99.9% | 99.9% |
| Accuracy | 97.9% | 99.1% | 90.5% | 97.2% | 99.8% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C1-as/out17.txt`
- `out copy/tests-D2-C2-ss/out48.txt`
- `out copy/tests-D1-C0/out196.txt`
- `out copy/tests-D2-C1-ss/out30.txt`

</details>

### Iteration 16 — Tarantula 0.0851

**Predicate**: `at least 1 Prepare -> Commit where view_no eq view_no, seq_no gt seq_no, peers isdisjoint peers` > 3

**Aggregation**: f_true=3, f_false=32, s_true=44, s_false=2336

**Pipeline state at iteration start**: 2415 reports, 64593 aggregations, 5858 filtered aggregations, 35 failed reports.

**Removed runs**: 3

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 0.0% | 100.0% | 0.0% | 0.0% |
| Recall | 0.0% | 0.0% | 1.1% | 0.0% | 0.0% |
| F1 | 0.0% | 0.0% | 2.2% | 0.0% | 0.0% |
| F0.5 | 0.0% | 0.0% | 5.4% | 0.0% | 0.0% |
| Specificity | 99.9% | 99.9% | 100.0% | 99.9% | 99.9% |
| Accuracy | 98.0% | 99.1% | 90.6% | 97.1% | 99.8% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C0/out58.txt`
- `out copy/tests-D2-C2-ss/out166.txt`
- `out copy/tests-D1-C1-as/out44.txt`

</details>

### Iteration 17 — Tarantula 0.0816

**Predicate**: `at least 1 Commit -> Commit where view_no eq view_no, seq_no gt seq_no, peers isdisjoint peers` > 1

**Aggregation**: f_true=2, f_false=30, s_true=29, s_false=2351

**Pipeline state at iteration start**: 2412 reports, 64592 aggregations, 3278 filtered aggregations, 32 failed reports.

**Removed runs**: 2

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 0.0% | 0.0% | 100.0% | 0.0% |
| Recall | 0.0% | 0.0% | 0.0% | 2.6% | 0.0% |
| F1 | 0.0% | 0.0% | 0.0% | 5.1% | 0.0% |
| F0.5 | 0.0% | 0.0% | 0.0% | 11.8% | 0.0% |
| Specificity | 99.9% | 99.9% | 99.9% | 100.0% | 99.9% |
| Accuracy | 98.0% | 99.1% | 90.4% | 97.3% | 99.9% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C1-as/out141.txt`
- `out copy/tests-D2-C2-as/out42.txt`

</details>

### Iteration 18 — Tarantula 0.0667

**Predicate**: `at least 2 Commit -> Prepare where view_no ne view_no, seq_no lt seq_no, peers isdisjoint peers` > 3

**Aggregation**: f_true=4, f_false=26, s_true=78, s_false=2302

**Pipeline state at iteration start**: 2410 reports, 64591 aggregations, 2232 filtered aggregations, 30 failed reports.

**Removed runs**: 4

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 0.0% | 100.0% | 0.0% | 0.0% |
| Recall | 0.0% | 0.0% | 1.5% | 0.0% | 0.0% |
| F1 | 0.0% | 0.0% | 3.0% | 0.0% | 0.0% |
| F0.5 | 0.0% | 0.0% | 7.1% | 0.0% | 0.0% |
| Specificity | 99.9% | 99.9% | 100.0% | 99.9% | 99.9% |
| Accuracy | 97.9% | 99.1% | 90.6% | 97.1% | 99.8% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-as/out35.txt`
- `out copy/tests-D2-C0/out35.txt`
- `out copy/tests-D2-C0/out57.txt`
- `out copy/tests-D2-C0/out149.txt`

</details>

### Iteration 19 — Tarantula 0.0489

**Predicate**: `at least 2 Prepare -> Commit where view_no gt view_no, peers issuperset peers` > 0

**Aggregation**: f_true=2, f_false=24, s_true=50, s_false=2330

**Pipeline state at iteration start**: 2406 reports, 64590 aggregations, 920 filtered aggregations, 26 failed reports.

**Removed runs**: 2

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 0.0% | 0.0% | 100.0% | 0.0% |
| Recall | 0.0% | 0.0% | 0.0% | 2.6% | 0.0% |
| F1 | 0.0% | 0.0% | 0.0% | 5.1% | 0.0% |
| F0.5 | 0.0% | 0.0% | 0.0% | 11.8% | 0.0% |
| Specificity | 99.9% | 99.9% | 99.9% | 100.0% | 99.9% |
| Accuracy | 98.0% | 99.1% | 90.4% | 97.3% | 99.9% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-ss/out146.txt`
- `out copy/tests-D2-C2-as/out146.txt`

</details>

### Iteration 20 — Tarantula 0.0333

**Predicate**: `at least 2 Commit -> Prepare where seq_no gt seq_no, peers isdisjoint peers` > 2

**Aggregation**: f_true=5, f_false=19, s_true=179, s_false=2201

**Pipeline state at iteration start**: 2404 reports, 64589 aggregations, 1107 filtered aggregations, 24 failed reports.

**Removed runs**: 5

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 0.0% | 80.0% | 20.0% | 0.0% |
| Recall | 0.0% | 0.0% | 1.5% | 1.3% | 0.0% |
| F1 | 0.0% | 0.0% | 2.9% | 2.4% | 0.0% |
| F0.5 | 0.0% | 0.0% | 7.0% | 5.2% | 0.0% |
| Specificity | 99.8% | 99.8% | 100.0% | 99.9% | 99.8% |
| Accuracy | 97.9% | 99.0% | 90.6% | 97.1% | 99.8% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D1-C1-ss/out49.txt`
- `out copy/tests-D2-C2-as/out114.txt`
- `out copy/tests-D2-C1-as/out50.txt`
- `out copy/tests-D2-C0/out82.txt`
- `out copy/tests-D2-C2-ss/out182.txt`

</details>

### Iteration 21 — Tarantula 0.0204

**Predicate**: `at least 1 PrePrepare -> Commit where view_no eq view_no, seq_no lt seq_no, peers eq peers` > 0

**Aggregation**: f_true=9, f_false=10, s_true=484, s_false=1896

**Pipeline state at iteration start**: 2399 reports, 64588 aggregations, 295 filtered aggregations, 19 failed reports.

**Removed runs**: 9

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 0.0% | 66.7% | 33.3% | 0.0% |
| Recall | 0.0% | 0.0% | 2.2% | 3.9% | 0.0% |
| F1 | 0.0% | 0.0% | 4.3% | 7.0% | 0.0% |
| F0.5 | 0.0% | 0.0% | 9.9% | 13.3% | 0.0% |
| Specificity | 99.7% | 99.7% | 99.9% | 99.8% | 99.7% |
| Accuracy | 97.8% | 98.9% | 90.6% | 97.1% | 99.6% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-ss/out102.txt`
- `out copy/tests-D2-C2-ss/out71.txt`
- `out copy/tests-D2-C2-ss/out91.txt`
- `out copy/tests-D2-C2-as/out91.txt`
- `out copy/tests-D2-C2-as/out71.txt`
- `out copy/tests-D1-C1-ss/out151.txt`
- `out copy/tests-D2-C2-ss/out98.txt`
- `out copy/tests-D1-C2-as/out81.txt`
- `out copy/tests-D1-C1-as/out151.txt`

</details>

### Iteration 22 — Tarantula 0.0048

**Predicate**: `at least 1 Prepare -> Prepare where view_no eq view_no, seq_no lt seq_no, peers isdisjoint peers` > 0

**Aggregation**: f_true=4, f_false=6, s_true=603, s_false=1777

**Pipeline state at iteration start**: 2390 reports, 64587 aggregations, 413 filtered aggregations, 10 failed reports.

**Removed runs**: 4

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 50.0% | 25.0% | 0.0% | 25.0% | 0.0% |
| Recall | 3.7% | 4.5% | 0.0% | 1.3% | 0.0% |
| F1 | 6.9% | 7.7% | 0.0% | 2.5% | 0.0% |
| F0.5 | 14.3% | 13.2% | 0.0% | 5.4% | 0.0% |
| Specificity | 99.9% | 99.9% | 99.8% | 99.9% | 99.9% |
| Accuracy | 98.1% | 99.1% | 90.3% | 97.2% | 99.8% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-ss/out45.txt`
- `out copy/tests-D2-C1-ss/out181.txt`
- `out copy/tests-D2-C1-as/out181.txt`
- `out copy/tests-D2-C2-as/out186.txt`

</details>

### Iteration 23 — Tarantula 0.0013

**Predicate**: `at least 1 PrePrepare -> ReplicaCommit where view_no eq view_no, seq_no lt seq_no, operation_first ne operation_first` > 2

**Aggregation**: f_true=5, f_false=1, s_true=1569, s_false=811

**Pipeline state at iteration start**: 2386 reports, 64586 aggregations, 298 filtered aggregations, 6 failed reports.

**Removed runs**: 1

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 100.0% | 0.0% | 0.0% | 0.0% |
| Recall | 0.0% | 4.5% | 0.0% | 0.0% | 0.0% |
| F1 | 0.0% | 8.7% | 0.0% | 0.0% | 0.0% |
| F0.5 | 0.0% | 19.2% | 0.0% | 0.0% | 0.0% |
| Specificity | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |
| Accuracy | 98.0% | 99.2% | 90.4% | 97.2% | 99.9% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D1-C2-as/out171.txt`

</details>

## Per-config bug-class distribution

Counts are static across iterations (the classifier is run once per run path).

| Configuration | Total | Correct | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|---------------|-------|---------|----------------------|-------------------|-------------------|-----------------|-------------|
| d=0 c=1 as | 200 | 196 | 4 | 0 | 0 | 0 | 0 |
| d=0 c=1 ss | 200 | 196 | 4 | 0 | 0 | 0 | 0 |
| d=0 c=2 as | 200 | 194 | 6 | 0 | 0 | 0 | 0 |
| d=0 c=2 ss | 200 | 193 | 6 | 0 | 0 | 1 | 0 |
| d=1 c=0 | 200 | 176 | 0 | 0 | 24 | 0 | 0 |
| d=1 c=1 as | 200 | 178 | 2 | 0 | 17 | 3 | 0 |
| d=1 c=1 ss | 200 | 169 | 4 | 0 | 24 | 3 | 0 |
| d=1 c=2 as | 200 | 171 | 6 | 2 | 12 | 9 | 0 |
| d=1 c=2 ss | 200 | 169 | 8 | 1 | 17 | 5 | 0 |
| d=2 c=0 | 200 | 153 | 0 | 0 | 46 | 0 | 1 |
| d=2 c=1 as | 200 | 152 | 2 | 2 | 37 | 7 | 0 |
| d=2 c=1 ss | 200 | 153 | 3 | 3 | 38 | 4 | 0 |
| d=2 c=2 as | 200 | 143 | 3 | 6 | 27 | 21 | 0 |
| d=2 c=2 ss | 200 | 137 | 6 | 8 | 25 | 24 | 1 |

**Totals across all configs**: 2800 runs, 2380 correct, 54 Operation Corruption, 22 View-Change Fault, 267 Partition Timeout, 77 Non-PP Mutation, 2 Split Brain.
