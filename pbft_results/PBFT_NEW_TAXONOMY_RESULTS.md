# PBFT ISOLATION Results — 5-Class Taxonomy

Dataset: `out copy/` — 2800 runs across 14 configs (200 per config), 2380 correct, 420 failures.

Bug classes: **Operation Corruption (OC)**, **View-Change Fault (VCF)**, **Partition Timeout (PT)**, **Non-PP Mutation (NPP)**, **Split Brain (SB)**.

Iterations: 19 (every failure isolated).

## Iteration summary

| # | Predicate | Tol. | Tarantula | f_true | f_false | s_true | s_false | Removed | Best class | P | R | F1 | F0.5 |
|---|-----------|------|-----------|--------|---------|--------|---------|---------|-----------|---|---|-----|------|
| 1 | `at least 2 ViewChange -> NewView where new_view_no gt new_view_no, pp_seq_set ne pp_seq_set` | >0 | 0.8483 | 232 | 188 | 12 | 2368 | 232 | Partition Timeout | 74.1% | 64.4% | 68.9% | 72.0% |
| 2 | `at least 1 PrePrepare -> ReplicaCommit where view_no eq view_no, seq_no eq seq_no, operation_first ne operation_first` | >0 | 0.8012 | 49 | 139 | 3 | 2377 | 49 | Operation Corruption | 87.8% | 79.6% | 83.5% | 86.0% |
| 3 | `at least 1 NewView -> ViewChange where new_view_no ne new_view_no, peers ne peers, prep_replica_set isdisjoint prep_replica_set` | >3 | 0.7354 | 46 | 93 | 15 | 2365 | 46 | Partition Timeout | 65.2% | 11.2% | 19.2% | 33.3% |
| 4 | `at least 1 ViewChange -> NewView where new_view_no gt new_view_no, pp_seq_set ne pp_seq_set, prep_replica_set eq prep_replica_set` | >0 | 0.6570 | 12 | 81 | 2 | 2378 | 12 | Partition Timeout | 66.7% | 3.0% | 5.7% | 12.7% |
| 5 | `at least 3 Prepare -> PrePrepare where ` | >2 | 0.5693 | 19 | 62 | 17 | 2363 | 19 | Partition Timeout | 73.7% | 5.2% | 9.8% | 20.4% |
| 6 | `at least 1 ViewChange -> ViewChange where new_view_no gt new_view_no, peers issubset peers, proof_count eq proof_count` | >2 | 0.5279 | 10 | 52 | 9 | 2371 | 10 | Partition Timeout | 70.0% | 2.6% | 5.1% | 11.4% |
| 7 | `at least 1 ViewChange -> ViewChange where new_view_no gt new_view_no, proof_count ne proof_count, prep_replica_set issuperset prep_replica_set` | >0 | 0.5426 | 5 | 24 | 1 | 1362 | 5 | Non-PP Mutation | 60.0% | 3.9% | 7.3% | 15.5% |
| 8 | `at least 2 Commit -> NewView where peers isdisjoint peers, seq_no notin vc_inner_last_seq_set` | >3 | 0.4740 | 8 | 15 | 10 | 1007 | 8 | Partition Timeout | 75.0% | 2.2% | 4.4% | 10.0% |
| 9 | `at least 1 NewView -> NewView where new_view_no eq new_view_no, num_vc_proofs lt num_vc_proofs, vc_replica_set eq vc_replica_set` | >3 | 0.4785 | 4 | 35 | 2 | 2378 | 4 | Partition Timeout | 100.0% | 1.5% | 3.0% | 7.1% |
| 10 | `at least 1 PrePrepare -> ReplicaCommit where operation_first ne operation_first, operation_second eq operation_second` | >1 | 0.3255 | 2 | 33 | 0 | 2380 | 2 | Operation Corruption | 100.0% | 3.7% | 7.1% | 16.1% |
| 11 | `at least 3 ViewChange -> ViewChange where new_view_no eq new_view_no, proof_count lt proof_count, prep_replica_set isdisjoint prep_replica_set` | >3 | 0.2961 | 4 | 29 | 12 | 2368 | 4 | Partition Timeout | 100.0% | 1.5% | 3.0% | 7.1% |
| 12 | `at least 1 NewView -> NewView where num_vc_proofs eq num_vc_proofs, num_prepared_proofs eq num_prepared_proofs, vc_replica_set issubset vc_replica_set` | >3 | 0.2617 | 3 | 14 | 10 | 1353 | 3 | Partition Timeout | 100.0% | 1.1% | 2.2% | 5.4% |
| 13 | `at least 3 Prepare -> Commit where view_no eq view_no, seq_no lt seq_no, peers ne peers` | >3 | 0.2121 | 2 | 24 | 7 | 2373 | 2 | Partition Timeout | 100.0% | 0.7% | 1.5% | 3.6% |
| 14 | `at least 1 ReplicaCommit -> PrePrepare where seq_no eq seq_no, operation_first ne operation_first` | >1 | 0.2151 | 2 | 22 | 7 | 2373 | 2 | Operation Corruption | 50.0% | 1.9% | 3.6% | 8.1% |
| 15 | `at least 1 ViewChange -> NewView where new_view_no gt new_view_no, peers isdisjoint peers, prep_replica_set issubset prep_replica_set` | >1 | 0.1211 | 2 | 9 | 20 | 1343 | 2 | Partition Timeout | 100.0% | 0.7% | 1.5% | 3.6% |
| 16 | `at least 2 Prepare -> ViewChange where seq_no eq last_seq_no, peers issuperset peers, seq_no notin pp_seq_set` | >1 | 0.0663 | 6 | 5 | 125 | 892 | 6 | Partition Timeout | 50.0% | 1.1% | 2.2% | 5.2% |
| 17 | `at least 1 PrePrepare -> Commit where view_no eq view_no, seq_no lt seq_no, peers eq peers` | >0 | 0.0166 | 7 | 7 | 484 | 1896 | 7 | Partition Timeout | 57.1% | 1.5% | 2.9% | 6.8% |
| 18 | `at least 1 ViewChange -> NewView where peers issuperset peers, pp_seq_set isdisjoint pp_seq_set, prep_replica_set issubset prep_replica_set` | >1 | 0.0081 | 2 | 2 | 283 | 1080 | 2 | Operation Corruption | 50.0% | 1.9% | 3.6% | 8.1% |
| 19 | `at least 1 PrePrepare -> ReplicaCommit where view_no eq view_no, seq_no lt seq_no, operation_first ne operation_first` | >2 | 0.0022 | 5 | 0 | 1569 | 811 | 5 | Operation Corruption | 100.0% | 9.3% | 16.9% | 33.8% |

## Detailed iteration breakdown

### Iteration 1 — Tarantula 0.8483

**Predicate**: `at least 2 ViewChange -> NewView where new_view_no gt new_view_no, pp_seq_set ne pp_seq_set` > 0

**Aggregation**: f_true=232, f_false=188, s_true=12, s_false=2368

**Pipeline state at iteration start**: 2800 reports, 266048 aggregations, 67353 filtered aggregations, 420 failed reports.

**Removed runs**: 232

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.9% | 5.6% | 74.1% | 19.8% | 0.0% |
| Recall | 3.7% | 59.1% | 64.4% | 59.7% | 0.0% |
| F1 | 1.4% | 10.2% | 68.9% | 29.8% | 0.0% |
| F0.5 | 1.0% | 6.8% | 72.0% | 22.9% | 0.0% |
| Specificity | 91.6% | 92.1% | 97.6% | 93.2% | 91.7% |
| Accuracy | 89.9% | 91.9% | 94.5% | 92.2% | 91.6% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-as/out114.txt`
- `out copy/tests-D2-C0/out40.txt`
- `out copy/tests-D2-C2-ss/out79.txt`
- `out copy/tests-D1-C1-as/out178.txt`
- `out copy/tests-D2-C1-as/out52.txt`
- `out copy/tests-D1-C1-ss/out56.txt`
- `out copy/tests-D2-C1-as/out157.txt`
- `out copy/tests-D2-C0/out7.txt`
- `out copy/tests-D1-C2-as/out15.txt`
- `out copy/tests-D2-C0/out199.txt`
- `out copy/tests-D2-C1-as/out187.txt`
- `out copy/tests-D1-C0/out73.txt`
- `out copy/tests-D2-C1-as/out16.txt`
- `out copy/tests-D2-C2-as/out6.txt`
- `out copy/tests-D2-C2-as/out132.txt`
- `out copy/tests-D1-C2-as/out136.txt`
- `out copy/tests-D2-C1-as/out20.txt`
- `out copy/tests-D1-C0/out186.txt`
- `out copy/tests-D2-C1-ss/out26.txt`
- `out copy/tests-D2-C1-as/out132.txt`
- `out copy/tests-D2-C2-as/out79.txt`
- `out copy/tests-D2-C2-ss/out53.txt`
- `out copy/tests-D2-C1-as/out95.txt`
- `out copy/tests-D1-C0/out116.txt`
- `out copy/tests-D2-C0/out186.txt`
- `out copy/tests-D1-C1-ss/out85.txt`
- `out copy/tests-D1-C1-ss/out137.txt`
- `out copy/tests-D1-C2-as/out137.txt`
- `out copy/tests-D1-C2-ss/out157.txt`
- `out copy/tests-D2-C1-as/out197.txt`
- `out copy/tests-D2-C1-ss/out191.txt`
- `out copy/tests-D2-C2-ss/out36.txt`
- `out copy/tests-D2-C2-ss/out56.txt`
- `out copy/tests-D2-C0/out43.txt`
- `out copy/tests-D1-C2-as/out33.txt`
- `out copy/tests-D1-C1-ss/out94.txt`
- `out copy/tests-D1-C1-as/out174.txt`
- `out copy/tests-D2-C0/out185.txt`
- `out copy/tests-D2-C0/out82.txt`
- `out copy/tests-D2-C1-as/out136.txt`
- `out copy/tests-D1-C1-as/out119.txt`
- `out copy/tests-D1-C1-as/out141.txt`
- `out copy/tests-D1-C1-ss/out93.txt`
- `out copy/tests-D1-C2-ss/out11.txt`
- `out copy/tests-D1-C2-ss/out116.txt`
- `out copy/tests-D2-C1-ss/out12.txt`
- `out copy/tests-D2-C1-ss/out137.txt`
- `out copy/tests-D2-C1-ss/out196.txt`
- `out copy/tests-D2-C2-ss/out3.txt`
- `out copy/tests-D2-C1-ss/out51.txt`
- `out copy/tests-D1-C1-ss/out178.txt`
- `out copy/tests-D2-C2-as/out140.txt`
- `out copy/tests-D2-C1-as/out119.txt`
- `out copy/tests-D1-C1-ss/out15.txt`
- `out copy/tests-D1-C0/out146.txt`
- `out copy/tests-D2-C2-as/out186.txt`
- `out copy/tests-D2-C2-as/out7.txt`
- `out copy/tests-D1-C0/out11.txt`
- `out copy/tests-D2-C0/out187.txt`
- `out copy/tests-D2-C2-ss/out45.txt`
- `out copy/tests-D1-C0/out41.txt`
- `out copy/tests-D2-C1-ss/out77.txt`
- `out copy/tests-D2-C1-as/out114.txt`
- `out copy/tests-D2-C2-as/out77.txt`
- `out copy/tests-D1-C2-ss/out99.txt`
- `out copy/tests-D2-C2-ss/out27.txt`
- `out copy/tests-D2-C2-ss/out89.txt`
- `out copy/tests-D1-C1-as/out66.txt`
- `out copy/tests-D1-C2-ss/out44.txt`
- `out copy/tests-D1-C0/out157.txt`
- `out copy/tests-D1-C1-ss/out119.txt`
- `out copy/tests-D1-C2-ss/out196.txt`
- `out copy/tests-D2-C2-ss/out20.txt`
- `out copy/tests-D1-C1-as/out11.txt`
- `out copy/tests-D2-C1-as/out174.txt`
- `out copy/tests-D1-C2-ss/out60.txt`
- `out copy/tests-D2-C2-as/out52.txt`
- `out copy/tests-D2-C0/out6.txt`
- `out copy/tests-D2-C2-as/out60.txt`
- `out copy/tests-D1-C2-as/out19.txt`
- `out copy/tests-D1-C0/out36.txt`
- `out copy/tests-D1-C2-ss/out66.txt`
- `out copy/tests-D2-C2-ss/out19.txt`
- `out copy/tests-D1-C2-ss/out140.txt`
- `out copy/tests-D2-C0/out87.txt`
- `out copy/tests-D1-C1-as/out27.txt`
- `out copy/tests-D1-C1-ss/out37.txt`
- `out copy/tests-D2-C1-as/out50.txt`
- `out copy/tests-D2-C2-as/out191.txt`
- `out copy/tests-D1-C1-ss/out186.txt`
- `out copy/tests-D1-C0/out141.txt`
- `out copy/tests-D2-C2-as/out9.txt`
- `out copy/tests-D2-C2-as/out37.txt`
- `out copy/tests-D2-C0/out20.txt`
- `out copy/tests-D2-C1-as/out192.txt`
- `out copy/tests-D2-C2-ss/out194.txt`
- `out copy/tests-D1-C2-as/out93.txt`
- `out copy/tests-D2-C1-as/out160.txt`
- `out copy/tests-D2-C1-ss/out162.txt`
- `out copy/tests-D2-C2-as/out45.txt`
- `out copy/tests-D2-C1-ss/out20.txt`
- `out copy/tests-D2-C2-ss/out132.txt`
- `out copy/tests-D1-C2-ss/out93.txt`
- `out copy/tests-D2-C1-ss/out40.txt`
- `out copy/tests-D2-C2-ss/out178.txt`
- `out copy/tests-D1-C0/out182.txt`
- `out copy/tests-D2-C2-ss/out129.txt`
- `out copy/tests-D2-C2-as/out178.txt`
- `out copy/tests-D1-C1-ss/out115.txt`
- `out copy/tests-D1-C1-as/out44.txt`
- `out copy/tests-D2-C0/out51.txt`
- `out copy/tests-D2-C2-ss/out151.txt`
- `out copy/tests-D2-C2-as/out59.txt`
- `out copy/tests-D2-C1-ss/out151.txt`
- `out copy/tests-D2-C1-as/out96.txt`
- `out copy/tests-D1-C2-ss/out73.txt`
- `out copy/tests-D2-C0/out123.txt`
- `out copy/tests-D2-C2-as/out41.txt`
- `out copy/tests-D2-C2-as/out110.txt`
- `out copy/tests-D1-C1-as/out57.txt`
- `out copy/tests-D1-C2-as/out156.txt`
- `out copy/tests-D2-C2-as/out153.txt`
- `out copy/tests-D2-C0/out144.txt`
- `out copy/tests-D2-C1-as/out87.txt`
- `out copy/tests-D2-C2-ss/out196.txt`
- `out copy/tests-D1-C0/out77.txt`
- `out copy/tests-D2-C0/out90.txt`
- `out copy/tests-D2-C2-ss/out60.txt`
- `out copy/tests-D2-C2-ss/out140.txt`
- `out copy/tests-D2-C0/out137.txt`
- `out copy/tests-D2-C2-as/out14.txt`
- `out copy/tests-D2-C2-as/out20.txt`
- `out copy/tests-D2-C1-ss/out123.txt`
- `out copy/tests-D2-C2-as/out104.txt`
- `out copy/tests-D1-C2-ss/out156.txt`
- `out copy/tests-D1-C1-ss/out79.txt`
- `out copy/tests-D2-C2-ss/out77.txt`
- `out copy/tests-D1-C2-as/out73.txt`
- `out copy/tests-D2-C2-ss/out153.txt`
- `out copy/tests-D1-C0/out49.txt`
- `out copy/tests-D1-C1-ss/out27.txt`
- `out copy/tests-D2-C2-as/out94.txt`
- `out copy/tests-D1-C2-ss/out123.txt`
- `out copy/tests-D1-C1-as/out79.txt`
- `out copy/tests-D2-C2-ss/out163.txt`
- `out copy/tests-D1-C2-as/out49.txt`
- `out copy/tests-D2-C0/out57.txt`
- `out copy/tests-D1-C0/out133.txt`
- `out copy/tests-D1-C1-ss/out103.txt`
- `out copy/tests-D1-C2-as/out133.txt`
- `out copy/tests-D1-C2-ss/out41.txt`
- `out copy/tests-D1-C1-ss/out170.txt`
- `out copy/tests-D1-C0/out136.txt`
- `out copy/tests-D2-C2-as/out36.txt`
- `out copy/tests-D2-C2-ss/out96.txt`
- `out copy/tests-D1-C2-as/out11.txt`
- `out copy/tests-D2-C1-as/out145.txt`
- `out copy/tests-D2-C1-ss/out37.txt`
- `out copy/tests-D1-C0/out115.txt`
- `out copy/tests-D2-C1-ss/out19.txt`
- `out copy/tests-D2-C2-as/out24.txt`
- `out copy/tests-D2-C2-as/out116.txt`
- `out copy/tests-D1-C1-ss/out195.txt`
- `out copy/tests-D2-C2-ss/out51.txt`
- `out copy/tests-D1-C2-as/out149.txt`
- `out copy/tests-D2-C1-as/out191.txt`
- `out copy/tests-D2-C1-ss/out178.txt`
- `out copy/tests-D1-C2-ss/out36.txt`
- `out copy/tests-D2-C2-ss/out7.txt`
- `out copy/tests-D1-C1-ss/out90.txt`
- `out copy/tests-D2-C1-as/out123.txt`
- `out copy/tests-D2-C2-as/out99.txt`
- `out copy/tests-D1-C0/out123.txt`
- `out copy/tests-D1-C2-ss/out56.txt`
- `out copy/tests-D2-C2-as/out192.txt`
- `out copy/tests-D2-C2-as/out19.txt`
- `out copy/tests-D2-C0/out115.txt`
- `out copy/tests-D2-C2-as/out194.txt`
- `out copy/tests-D1-C0/out166.txt`
- `out copy/tests-D1-C2-as/out86.txt`
- `out copy/tests-D2-C1-as/out19.txt`
- `out copy/tests-D1-C2-as/out103.txt`
- `out copy/tests-D1-C1-ss/out199.txt`
- `out copy/tests-D1-C1-as/out146.txt`
- `out copy/tests-D2-C1-ss/out33.txt`
- `out copy/tests-D1-C1-as/out90.txt`
- `out copy/tests-D2-C2-ss/out186.txt`
- `out copy/tests-D1-C2-as/out190.txt`
- `out copy/tests-D2-C1-ss/out174.txt`
- `out copy/tests-D1-C1-as/out123.txt`
- `out copy/tests-D2-C1-ss/out58.txt`
- `out copy/tests-D2-C2-as/out141.txt`
- `out copy/tests-D1-C2-ss/out149.txt`
- `out copy/tests-D2-C1-as/out149.txt`
- `out copy/tests-D2-C2-as/out73.txt`
- `out copy/tests-D2-C0/out37.txt`
- `out copy/tests-D2-C1-as/out14.txt`
- `out copy/tests-D2-C1-ss/out52.txt`
- `out copy/tests-D1-C1-ss/out3.txt`
- `out copy/tests-D1-C1-ss/out49.txt`
- `out copy/tests-D1-C2-ss/out94.txt`
- `out copy/tests-D2-C0/out96.txt`
- `out copy/tests-D2-C2-ss/out58.txt`
- `out copy/tests-D1-C2-as/out36.txt`
- `out copy/tests-D2-C1-ss/out175.txt`
- `out copy/tests-D2-C2-ss/out141.txt`
- `out copy/tests-D1-C2-ss/out19.txt`
- `out copy/tests-D1-C0/out107.txt`
- `out copy/tests-D1-C1-ss/out7.txt`
- `out copy/tests-D2-C2-ss/out119.txt`
- `out copy/tests-D2-C0/out151.txt`
- `out copy/tests-D1-C0/out95.txt`
- `out copy/tests-D1-C1-as/out166.txt`
- `out copy/tests-D2-C1-ss/out6.txt`
- `out copy/tests-D2-C1-ss/out44.txt`
- `out copy/tests-D1-C1-ss/out44.txt`
- `out copy/tests-D1-C2-as/out145.txt`
- `out copy/tests-D1-C2-as/out196.txt`
- `out copy/tests-D2-C2-as/out159.txt`
- `out copy/tests-D2-C2-ss/out57.txt`
- `out copy/tests-D2-C0/out56.txt`
- `out copy/tests-D2-C1-as/out41.txt`
- `out copy/tests-D2-C1-as/out40.txt`
- `out copy/tests-D0-C2-ss/out191.txt`
- `out copy/tests-D2-C2-as/out135.txt`
- `out copy/tests-D2-C0/out99.txt`
- `out copy/tests-D2-C2-ss/out190.txt`
- `out copy/tests-D1-C1-as/out157.txt`
- `out copy/tests-D2-C1-ss/out11.txt`
- `out copy/tests-D2-C1-ss/out110.txt`
- `out copy/tests-D2-C2-ss/out104.txt`
- `out copy/tests-D1-C1-ss/out145.txt`

</details>

### Iteration 2 — Tarantula 0.8012

**Predicate**: `at least 1 PrePrepare -> ReplicaCommit where view_no eq view_no, seq_no eq seq_no, operation_first ne operation_first` > 0

**Aggregation**: f_true=49, f_false=139, s_true=3, s_false=2377

**Pipeline state at iteration start**: 2568 reports, 266047 aggregations, 63113 filtered aggregations, 188 failed reports.

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

- `out copy/tests-D2-C1-ss/out100.txt`
- `out copy/tests-D1-C1-ss/out143.txt`
- `out copy/tests-D0-C2-as/out148.txt`
- `out copy/tests-D0-C2-as/out126.txt`
- `out copy/tests-D2-C2-as/out181.txt`
- `out copy/tests-D2-C2-ss/out40.txt`
- `out copy/tests-D0-C1-ss/out143.txt`
- `out copy/tests-D0-C2-as/out93.txt`
- `out copy/tests-D2-C2-as/out66.txt`
- `out copy/tests-D2-C2-ss/out100.txt`
- `out copy/tests-D0-C1-ss/out108.txt`
- `out copy/tests-D1-C2-ss/out7.txt`
- `out copy/tests-D0-C2-ss/out126.txt`
- `out copy/tests-D2-C2-ss/out181.txt`
- `out copy/tests-D1-C2-as/out126.txt`
- `out copy/tests-D1-C2-as/out43.txt`
- `out copy/tests-D0-C2-as/out91.txt`
- `out copy/tests-D0-C1-as/out121.txt`
- `out copy/tests-D0-C2-ss/out148.txt`
- `out copy/tests-D2-C1-as/out121.txt`
- `out copy/tests-D1-C2-ss/out130.txt`
- `out copy/tests-D2-C2-ss/out16.txt`
- `out copy/tests-D1-C2-as/out120.txt`
- `out copy/tests-D0-C2-ss/out100.txt`
- `out copy/tests-D0-C1-as/out143.txt`
- `out copy/tests-D1-C2-ss/out43.txt`
- `out copy/tests-D1-C2-ss/out126.txt`
- `out copy/tests-D2-C2-as/out143.txt`
- `out copy/tests-D2-C2-ss/out176.txt`
- `out copy/tests-D0-C2-as/out100.txt`
- `out copy/tests-D1-C1-as/out109.txt`
- `out copy/tests-D1-C2-ss/out167.txt`
- `out copy/tests-D1-C2-ss/out109.txt`
- `out copy/tests-D0-C2-as/out95.txt`
- `out copy/tests-D0-C1-as/out108.txt`
- `out copy/tests-D2-C2-ss/out143.txt`
- `out copy/tests-D1-C2-as/out109.txt`
- `out copy/tests-D2-C1-as/out100.txt`
- `out copy/tests-D1-C1-ss/out109.txt`
- `out copy/tests-D2-C2-as/out48.txt`
- `out copy/tests-D1-C2-as/out130.txt`
- `out copy/tests-D2-C1-ss/out41.txt`
- `out copy/tests-D1-C1-ss/out136.txt`
- `out copy/tests-D0-C2-ss/out95.txt`
- `out copy/tests-D0-C2-ss/out91.txt`
- `out copy/tests-D1-C2-ss/out120.txt`
- `out copy/tests-D0-C2-ss/out93.txt`
- `out copy/tests-D0-C1-ss/out121.txt`
- `out copy/tests-D2-C0/out41.txt`

</details>

### Iteration 3 — Tarantula 0.7354

**Predicate**: `at least 1 NewView -> ViewChange where new_view_no ne new_view_no, peers ne peers, prep_replica_set isdisjoint prep_replica_set` > 3

**Aggregation**: f_true=46, f_false=93, s_true=15, s_false=2365

**Pipeline state at iteration start**: 2519 reports, 266046 aggregations, 62644 filtered aggregations, 139 failed reports.

**Removed runs**: 46

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 6.5% | 65.2% | 26.1% | 2.2% |
| Recall | 0.0% | 13.6% | 11.2% | 15.6% | 50.0% |
| F1 | 0.0% | 8.8% | 19.2% | 19.5% | 4.2% |
| F0.5 | 0.0% | 7.3% | 33.3% | 23.0% | 2.7% |
| Specificity | 98.3% | 98.5% | 99.4% | 98.8% | 98.4% |
| Accuracy | 96.4% | 97.8% | 91.0% | 96.5% | 98.4% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C1-as/out66.txt`
- `out copy/tests-D2-C1-as/out194.txt`
- `out copy/tests-D2-C1-as/out59.txt`
- `out copy/tests-D2-C1-as/out18.txt`
- `out copy/tests-D2-C1-as/out53.txt`
- `out copy/tests-D2-C2-ss/out199.txt`
- `out copy/tests-D2-C2-ss/out175.txt`
- `out copy/tests-D2-C0/out73.txt`
- `out copy/tests-D2-C1-as/out175.txt`
- `out copy/tests-D2-C0/out66.txt`
- `out copy/tests-D2-C2-as/out18.txt`
- `out copy/tests-D2-C1-as/out26.txt`
- `out copy/tests-D1-C1-ss/out53.txt`
- `out copy/tests-D2-C2-as/out26.txt`
- `out copy/tests-D2-C2-ss/out197.txt`
- `out copy/tests-D1-C1-ss/out174.txt`
- `out copy/tests-D2-C2-ss/out48.txt`
- `out copy/tests-D2-C0/out156.txt`
- `out copy/tests-D2-C1-ss/out140.txt`
- `out copy/tests-D2-C1-ss/out9.txt`
- `out copy/tests-D2-C2-ss/out182.txt`
- `out copy/tests-D2-C2-ss/out43.txt`
- `out copy/tests-D2-C2-ss/out95.txt`
- `out copy/tests-D2-C1-as/out12.txt`
- `out copy/tests-D2-C1-ss/out136.txt`
- `out copy/tests-D2-C1-as/out168.txt`
- `out copy/tests-D1-C2-as/out41.txt`
- `out copy/tests-D2-C2-as/out43.txt`
- `out copy/tests-D2-C1-ss/out66.txt`
- `out copy/tests-D2-C1-ss/out119.txt`
- `out copy/tests-D1-C1-as/out103.txt`
- `out copy/tests-D2-C2-ss/out184.txt`
- `out copy/tests-D2-C2-ss/out185.txt`
- `out copy/tests-D2-C0/out178.txt`
- `out copy/tests-D2-C2-as/out27.txt`
- `out copy/tests-D1-C2-ss/out170.txt`
- `out copy/tests-D2-C0/out61.txt`
- `out copy/tests-D1-C2-ss/out146.txt`
- `out copy/tests-D1-C1-as/out95.txt`
- `out copy/tests-D2-C1-as/out79.txt`
- `out copy/tests-D2-C2-ss/out11.txt`
- `out copy/tests-D2-C0/out112.txt`
- `out copy/tests-D2-C0/out175.txt`
- `out copy/tests-D1-C0/out170.txt`
- `out copy/tests-D2-C1-ss/out59.txt`
- `out copy/tests-D2-C1-ss/out121.txt`

</details>

### Iteration 4 — Tarantula 0.6570

**Predicate**: `at least 1 ViewChange -> NewView where new_view_no gt new_view_no, pp_seq_set ne pp_seq_set, prep_replica_set eq prep_replica_set` > 0

**Aggregation**: f_true=12, f_false=81, s_true=2, s_false=2378

**Pipeline state at iteration start**: 2473 reports, 266045 aggregations, 58363 filtered aggregations, 93 failed reports.

**Removed runs**: 12

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 16.7% | 66.7% | 16.7% | 0.0% |
| Recall | 0.0% | 9.1% | 3.0% | 2.6% | 0.0% |
| F1 | 0.0% | 11.8% | 5.7% | 4.5% | 0.0% |
| F0.5 | 0.0% | 14.3% | 12.7% | 8.0% | 0.0% |
| Specificity | 99.6% | 99.6% | 99.8% | 99.6% | 99.6% |
| Accuracy | 97.6% | 98.9% | 90.6% | 97.0% | 99.5% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-as/out175.txt`
- `out copy/tests-D2-C0/out30.txt`
- `out copy/tests-D2-C1-ss/out159.txt`
- `out copy/tests-D1-C0/out15.txt`
- `out copy/tests-D2-C1-as/out151.txt`
- `out copy/tests-D2-C0/out35.txt`
- `out copy/tests-D2-C2-as/out129.txt`
- `out copy/tests-D2-C1-ss/out79.txt`
- `out copy/tests-D2-C2-ss/out137.txt`
- `out copy/tests-D1-C1-ss/out112.txt`
- `out copy/tests-D2-C2-as/out197.txt`
- `out copy/tests-D2-C2-ss/out31.txt`

</details>

### Iteration 5 — Tarantula 0.5693

**Predicate**: `at least 3 Prepare -> PrePrepare where ` > 2

**Aggregation**: f_true=19, f_false=62, s_true=17, s_false=2363

**Pipeline state at iteration start**: 2461 reports, 266044 aggregations, 57512 filtered aggregations, 81 failed reports.

**Removed runs**: 19

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 5.3% | 73.7% | 21.1% | 0.0% |
| Recall | 0.0% | 4.5% | 5.2% | 5.2% | 0.0% |
| F1 | 0.0% | 4.9% | 9.8% | 8.3% | 0.0% |
| F0.5 | 0.0% | 5.1% | 20.4% | 13.1% | 0.0% |
| Specificity | 99.3% | 99.4% | 99.8% | 99.4% | 99.3% |
| Accuracy | 97.4% | 98.6% | 90.8% | 96.9% | 99.2% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-as/out157.txt`
- `out copy/tests-D2-C0/out50.txt`
- `out copy/tests-D1-C2-as/out48.txt`
- `out copy/tests-D2-C1-ss/out179.txt`
- `out copy/tests-D2-C2-as/out96.txt`
- `out copy/tests-D2-C0/out14.txt`
- `out copy/tests-D2-C2-ss/out52.txt`
- `out copy/tests-D2-C2-as/out68.txt`
- `out copy/tests-D1-C2-ss/out145.txt`
- `out copy/tests-D2-C1-ss/out30.txt`
- `out copy/tests-D2-C1-as/out162.txt`
- `out copy/tests-D2-C1-ss/out73.txt`
- `out copy/tests-D1-C2-as/out53.txt`
- `out copy/tests-D2-C0/out159.txt`
- `out copy/tests-D2-C1-ss/out186.txt`
- `out copy/tests-D1-C0/out3.txt`
- `out copy/tests-D2-C0/out136.txt`
- `out copy/tests-D2-C1-as/out44.txt`
- `out copy/tests-D2-C1-as/out99.txt`

</details>

### Iteration 6 — Tarantula 0.5279

**Predicate**: `at least 1 ViewChange -> ViewChange where new_view_no gt new_view_no, peers issubset peers, proof_count eq proof_count` > 2

**Aggregation**: f_true=10, f_false=52, s_true=9, s_false=2371

**Pipeline state at iteration start**: 2442 reports, 266043 aggregations, 55471 filtered aggregations, 62 failed reports.

**Removed runs**: 10

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 10.0% | 70.0% | 20.0% | 10.0% |
| Recall | 0.0% | 4.5% | 2.6% | 2.6% | 50.0% |
| F1 | 0.0% | 6.3% | 5.1% | 4.6% | 16.7% |
| F0.5 | 0.0% | 8.1% | 11.4% | 8.5% | 11.9% |
| Specificity | 99.6% | 99.7% | 99.9% | 99.7% | 99.7% |
| Accuracy | 97.7% | 98.9% | 90.6% | 97.0% | 99.6% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-as/out42.txt`
- `out copy/tests-D2-C2-ss/out87.txt`
- `out copy/tests-D2-C0/out166.txt`
- `out copy/tests-D2-C2-as/out156.txt`
- `out copy/tests-D2-C0/out149.txt`
- `out copy/tests-D2-C1-as/out17.txt`
- `out copy/tests-D2-C1-ss/out18.txt`
- `out copy/tests-D2-C2-ss/out41.txt`
- `out copy/tests-D1-C1-as/out7.txt`
- `out copy/tests-D2-C0/out18.txt`

</details>

### Iteration 7 — Tarantula 0.5426

**Predicate**: `at least 1 ViewChange -> ViewChange where new_view_no gt new_view_no, proof_count ne proof_count, prep_replica_set issuperset prep_replica_set` > 0

**Aggregation**: f_true=5, f_false=24, s_true=1, s_false=1362

**Pipeline state at iteration start**: 2432 reports, 266042 aggregations, 54264 filtered aggregations, 52 failed reports.

**Removed runs**: 5

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 0.0% | 40.0% | 60.0% | 0.0% |
| Recall | 0.0% | 0.0% | 0.7% | 3.9% | 0.0% |
| F1 | 0.0% | 0.0% | 1.5% | 7.3% | 0.0% |
| F0.5 | 0.0% | 0.0% | 3.5% | 15.5% | 0.0% |
| Specificity | 99.8% | 99.8% | 99.9% | 99.9% | 99.8% |
| Accuracy | 97.9% | 99.0% | 90.4% | 97.3% | 99.8% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-as/out35.txt`
- `out copy/tests-D2-C1-as/out159.txt`
- `out copy/tests-D2-C1-as/out43.txt`
- `out copy/tests-D2-C2-as/out136.txt`
- `out copy/tests-D2-C1-as/out141.txt`

</details>

### Iteration 8 — Tarantula 0.4740

**Predicate**: `at least 2 Commit -> NewView where peers isdisjoint peers, seq_no notin vc_inner_last_seq_set` > 3

**Aggregation**: f_true=8, f_false=15, s_true=10, s_false=1007

**Pipeline state at iteration start**: 2427 reports, 266041 aggregations, 53295 filtered aggregations, 47 failed reports.

**Removed runs**: 8

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 0.0% | 75.0% | 25.0% | 0.0% |
| Recall | 0.0% | 0.0% | 2.2% | 2.6% | 0.0% |
| F1 | 0.0% | 0.0% | 4.4% | 4.7% | 0.0% |
| F0.5 | 0.0% | 0.0% | 10.0% | 9.2% | 0.0% |
| Specificity | 99.7% | 99.7% | 99.9% | 99.8% | 99.7% |
| Accuracy | 97.8% | 98.9% | 90.6% | 97.1% | 99.6% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D1-C2-ss/out174.txt`
- `out copy/tests-D2-C2-ss/out166.txt`
- `out copy/tests-D2-C1-ss/out99.txt`
- `out copy/tests-D2-C1-ss/out153.txt`
- `out copy/tests-D2-C2-ss/out4.txt`
- `out copy/tests-D2-C2-ss/out136.txt`
- `out copy/tests-D2-C1-ss/out95.txt`
- `out copy/tests-D1-C1-ss/out182.txt`

</details>

### Iteration 9 — Tarantula 0.4785

**Predicate**: `at least 1 NewView -> NewView where new_view_no eq new_view_no, num_vc_proofs lt num_vc_proofs, vc_replica_set eq vc_replica_set` > 3

**Aggregation**: f_true=4, f_false=35, s_true=2, s_false=2378

**Pipeline state at iteration start**: 2419 reports, 266040 aggregations, 48939 filtered aggregations, 39 failed reports.

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

- `out copy/tests-D2-C0/out9.txt`
- `out copy/tests-D2-C0/out174.txt`
- `out copy/tests-D2-C0/out58.txt`
- `out copy/tests-D2-C1-ss/out129.txt`

</details>

### Iteration 10 — Tarantula 0.3255

**Predicate**: `at least 1 PrePrepare -> ReplicaCommit where operation_first ne operation_first, operation_second eq operation_second` > 1

**Aggregation**: f_true=2, f_false=33, s_true=0, s_false=2380

**Pipeline state at iteration start**: 2415 reports, 266039 aggregations, 44760 filtered aggregations, 35 failed reports.

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

- `out copy/tests-D1-C1-as/out136.txt`
- `out copy/tests-D2-C2-ss/out64.txt`

</details>

### Iteration 11 — Tarantula 0.2961

**Predicate**: `at least 3 ViewChange -> ViewChange where new_view_no eq new_view_no, proof_count lt proof_count, prep_replica_set isdisjoint prep_replica_set` > 3

**Aggregation**: f_true=4, f_false=29, s_true=12, s_false=2368

**Pipeline state at iteration start**: 2413 reports, 266038 aggregations, 44014 filtered aggregations, 33 failed reports.

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

- `out copy/tests-D2-C1-as/out9.txt`
- `out copy/tests-D2-C0/out59.txt`
- `out copy/tests-D2-C2-ss/out156.txt`
- `out copy/tests-D2-C0/out79.txt`

</details>

### Iteration 12 — Tarantula 0.2617

**Predicate**: `at least 1 NewView -> NewView where num_vc_proofs eq num_vc_proofs, num_prepared_proofs eq num_prepared_proofs, vc_replica_set issubset vc_replica_set` > 3

**Aggregation**: f_true=3, f_false=14, s_true=10, s_false=1353

**Pipeline state at iteration start**: 2409 reports, 266037 aggregations, 33604 filtered aggregations, 29 failed reports.

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

- `out copy/tests-D1-C1-as/out36.txt`
- `out copy/tests-D1-C0/out196.txt`
- `out copy/tests-D2-C0/out129.txt`

</details>

### Iteration 13 — Tarantula 0.2121

**Predicate**: `at least 3 Prepare -> Commit where view_no eq view_no, seq_no lt seq_no, peers ne peers` > 3

**Aggregation**: f_true=2, f_false=24, s_true=7, s_false=2373

**Pipeline state at iteration start**: 2406 reports, 266036 aggregations, 26731 filtered aggregations, 26 failed reports.

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

- `out copy/tests-D2-C1-as/out6.txt`
- `out copy/tests-D1-C0/out57.txt`

</details>

### Iteration 14 — Tarantula 0.2151

**Predicate**: `at least 1 ReplicaCommit -> PrePrepare where seq_no eq seq_no, operation_first ne operation_first` > 1

**Aggregation**: f_true=2, f_false=22, s_true=7, s_false=2373

**Pipeline state at iteration start**: 2404 reports, 266035 aggregations, 16443 filtered aggregations, 24 failed reports.

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

- `out copy/tests-D2-C2-ss/out15.txt`
- `out copy/tests-D2-C2-as/out112.txt`

</details>

### Iteration 15 — Tarantula 0.1211

**Predicate**: `at least 1 ViewChange -> NewView where new_view_no gt new_view_no, peers isdisjoint peers, prep_replica_set issubset prep_replica_set` > 1

**Aggregation**: f_true=2, f_false=9, s_true=20, s_false=1343

**Pipeline state at iteration start**: 2402 reports, 266034 aggregations, 12401 filtered aggregations, 22 failed reports.

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

- `out copy/tests-D2-C2-as/out95.txt`
- `out copy/tests-D2-C0/out36.txt`

</details>

### Iteration 16 — Tarantula 0.0663

**Predicate**: `at least 2 Prepare -> ViewChange where seq_no eq last_seq_no, peers issuperset peers, seq_no notin pp_seq_set` > 1

**Aggregation**: f_true=6, f_false=5, s_true=125, s_false=892

**Pipeline state at iteration start**: 2400 reports, 266033 aggregations, 4460 filtered aggregations, 20 failed reports.

**Removed runs**: 6

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 0.0% | 50.0% | 50.0% | 0.0% |
| Recall | 0.0% | 0.0% | 1.1% | 3.9% | 0.0% |
| F1 | 0.0% | 0.0% | 2.2% | 7.2% | 0.0% |
| F0.5 | 0.0% | 0.0% | 5.2% | 14.9% | 0.0% |
| Specificity | 99.8% | 99.8% | 99.9% | 99.9% | 99.8% |
| Accuracy | 97.9% | 99.0% | 90.5% | 97.2% | 99.7% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C1-ss/out43.txt`
- `out copy/tests-D2-C2-ss/out146.txt`
- `out copy/tests-D2-C1-ss/out185.txt`
- `out copy/tests-D2-C2-ss/out98.txt`
- `out copy/tests-D1-C1-ss/out151.txt`
- `out copy/tests-D2-C2-ss/out102.txt`

</details>

### Iteration 17 — Tarantula 0.0166

**Predicate**: `at least 1 PrePrepare -> Commit where view_no eq view_no, seq_no lt seq_no, peers eq peers` > 0

**Aggregation**: f_true=7, f_false=7, s_true=484, s_false=1896

**Pipeline state at iteration start**: 2394 reports, 266032 aggregations, 3711 filtered aggregations, 14 failed reports.

**Removed runs**: 7

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 0.0% | 0.0% | 57.1% | 42.9% | 0.0% |
| Recall | 0.0% | 0.0% | 1.5% | 3.9% | 0.0% |
| F1 | 0.0% | 0.0% | 2.9% | 7.1% | 0.0% |
| F0.5 | 0.0% | 0.0% | 6.8% | 14.3% | 0.0% |
| Specificity | 99.7% | 99.7% | 99.9% | 99.9% | 99.7% |
| Accuracy | 97.8% | 99.0% | 90.5% | 97.2% | 99.7% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-as/out71.txt`
- `out copy/tests-D2-C2-as/out146.txt`
- `out copy/tests-D1-C2-as/out81.txt`
- `out copy/tests-D2-C2-ss/out71.txt`
- `out copy/tests-D2-C2-ss/out91.txt`
- `out copy/tests-D1-C1-as/out151.txt`
- `out copy/tests-D2-C2-as/out91.txt`

</details>

### Iteration 18 — Tarantula 0.0081

**Predicate**: `at least 1 ViewChange -> NewView where peers issuperset peers, pp_seq_set isdisjoint pp_seq_set, prep_replica_set issubset prep_replica_set` > 1

**Aggregation**: f_true=2, f_false=2, s_true=283, s_false=1080

**Pipeline state at iteration start**: 2387 reports, 266031 aggregations, 7526 filtered aggregations, 7 failed reports.

**Removed runs**: 2

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 50.0% | 50.0% | 0.0% | 0.0% | 0.0% |
| Recall | 1.9% | 4.5% | 0.0% | 0.0% | 0.0% |
| F1 | 3.6% | 8.3% | 0.0% | 0.0% | 0.0% |
| F0.5 | 8.1% | 16.7% | 0.0% | 0.0% | 0.0% |
| Specificity | 100.0% | 100.0% | 99.9% | 99.9% | 99.9% |
| Accuracy | 98.1% | 99.2% | 90.4% | 97.2% | 99.9% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C1-as/out181.txt`
- `out copy/tests-D1-C2-as/out171.txt`

</details>

### Iteration 19 — Tarantula 0.0022

**Predicate**: `at least 1 PrePrepare -> ReplicaCommit where view_no eq view_no, seq_no lt seq_no, operation_first ne operation_first` > 2

**Aggregation**: f_true=5, f_false=0, s_true=1569, s_false=811

**Pipeline state at iteration start**: 2385 reports, 266030 aggregations, 2200 filtered aggregations, 5 failed reports.

**Removed runs**: 5

| Metric | Operation Corruption | View-Change Fault | Partition Timeout | Non-PP Mutation | Split Brain |
|--------|----------------------|-------------------|-------------------|-----------------|-------------|
| Precision | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Recall | 9.3% | 0.0% | 0.0% | 0.0% | 0.0% |
| F1 | 16.9% | 0.0% | 0.0% | 0.0% | 0.0% |
| F0.5 | 33.8% | 0.0% | 0.0% | 0.0% | 0.0% |
| Specificity | 100.0% | 99.8% | 99.8% | 99.8% | 99.8% |
| Accuracy | 98.2% | 99.0% | 90.3% | 97.1% | 99.8% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D0-C1-as/out95.txt`
- `out copy/tests-D0-C1-ss/out95.txt`
- `out copy/tests-D1-C2-as/out100.txt`
- `out copy/tests-D1-C2-ss/out100.txt`
- `out copy/tests-D2-C1-ss/out181.txt`

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
