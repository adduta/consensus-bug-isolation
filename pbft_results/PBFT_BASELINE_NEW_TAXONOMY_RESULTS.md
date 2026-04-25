# PBFT BASELINE Results — New 4-Class Taxonomy

Pipeline: **PRED-annotation baseline** (`scripts/baseline.py`). Predicates come from `PRED` markers emitted by the instrumented PBFT replica (`DefaultReplica.java`), not from message-pair evaluation.

Dataset: `out copy/` — 2800 runs across 14 configs (200 per config), 2380 correct, 420 failures.

Bug classes: **Operation Corruption (OC)**, **View-Change Fault (VCF)**, **Quorum Stall (QS)**, **Split Brain (SB)**.

Iterations: 7.

## Iteration summary

| # | Predicate | Tarantula | f_true | f_false | s_true | s_false | Removed | Best class | P | R | F1 | F0.5 |
|---|-----------|-----------|--------|---------|--------|---------|---------|-----------|---|---|-----|------|
| 1 | `BRANCH DefaultReplica.java:621 is false` | 0.5473 | 292 | 83 | 150 | 841 | 292 | Quorum Stall | 91.4% | 77.6% | 84.0% | 88.3% |
| 2 | `BRANCH DefaultReplica.java:319 is true` | 0.1606 | 27 | 101 | 163 | 2217 | 27 | Quorum Stall | 81.5% | 6.4% | 11.9% | 24.3% |
| 3 | `BRANCH DefaultReplica.java:292 is true` | 0.0879 | 44 | 57 | 461 | 1919 | 44 | Quorum Stall | 81.8% | 10.5% | 18.6% | 34.6% |
| 4 | `BRANCH DefaultReplica.java:173 is true` | 0.0159 | 32 | 25 | 987 | 1393 | 32 | Operation Corruption | 50.0% | 29.6% | 37.2% | 44.0% |
| 5 | `WHILE DefaultReplica.java:684 is false` | 0.0224 | 2 | 2 | 124 | 863 | 2 | View-Change Fault | 50.0% | 4.5% | 8.3% | 16.7% |
| 6 | `BRANCH DefaultReplica.java:526 is true` | 0.0005 | 20 | 3 | 2013 | 367 | 20 | Operation Corruption | 100.0% | 37.0% | 54.1% | 74.6% |
| 7 | `BRANCH DefaultReplica.java:244 is true` | 0.0029 | 3 | 0 | 1104 | 1276 | 3 | Quorum Stall | 66.7% | 0.6% | 1.2% | 2.8% |

## Detailed iteration breakdown

### Iteration 1 — Tarantula 0.5473

**Predicate**: `BRANCH DefaultReplica.java:621 is false`

**Aggregation**: f_true=292, f_false=83, s_true=150, s_false=841

**Pipeline state at iteration start**: 2800 reports, 76 aggregations, 23 filtered aggregations, 420 failed reports.

**Removed runs**: 292

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 2.7% | 6.2% | 91.4% | 0.3% |
| Recall | 14.8% | 81.8% | 77.6% | 50.0% |
| F1 | 4.6% | 11.5% | 84.0% | 0.7% |
| F0.5 | 3.3% | 7.6% | 88.3% | 0.4% |
| Specificity | 89.7% | 90.1% | 99.0% | 89.6% |
| Accuracy | 88.2% | 90.1% | 96.4% | 89.6% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D1-C2-ss/out157.txt`
- `out copy/tests-D2-C1-ss/out175.txt`
- `out copy/tests-D1-C1-ss/out93.txt`
- `out copy/tests-D1-C2-as/out49.txt`
- `out copy/tests-D2-C0/out18.txt`
- `out copy/tests-D2-C1-as/out159.txt`
- `out copy/tests-D1-C1-ss/out79.txt`
- `out copy/tests-D1-C2-as/out103.txt`
- `out copy/tests-D2-C1-as/out157.txt`
- `out copy/tests-D2-C2-ss/out163.txt`
- `out copy/tests-D1-C1-ss/out195.txt`
- `out copy/tests-D2-C0/out57.txt`
- `out copy/tests-D1-C2-ss/out99.txt`
- `out copy/tests-D2-C2-ss/out7.txt`
- `out copy/tests-D1-C0/out115.txt`
- `out copy/tests-D2-C1-ss/out73.txt`
- `out copy/tests-D2-C1-ss/out30.txt`
- `out copy/tests-D2-C1-ss/out77.txt`
- `out copy/tests-D2-C2-ss/out52.txt`
- `out copy/tests-D1-C1-as/out11.txt`
- `out copy/tests-D2-C2-as/out36.txt`
- `out copy/tests-D1-C1-as/out7.txt`
- `out copy/tests-D2-C2-as/out42.txt`
- `out copy/tests-D2-C2-as/out178.txt`
- `out copy/tests-D2-C0/out37.txt`
- `out copy/tests-D2-C1-as/out174.txt`
- `out copy/tests-D2-C2-ss/out40.txt`
- `out copy/tests-D1-C2-ss/out44.txt`
- `out copy/tests-D2-C2-ss/out51.txt`
- `out copy/tests-D2-C1-as/out160.txt`
- `out copy/tests-D1-C0/out182.txt`
- `out copy/tests-D2-C0/out186.txt`
- `out copy/tests-D1-C1-as/out119.txt`
- `out copy/tests-D2-C2-ss/out184.txt`
- `out copy/tests-D2-C0/out149.txt`
- `out copy/tests-D2-C1-as/out17.txt`
- `out copy/tests-D2-C0/out9.txt`
- `out copy/tests-D2-C2-ss/out197.txt`
- `out copy/tests-D2-C1-as/out132.txt`
- `out copy/tests-D2-C0/out90.txt`
- `out copy/tests-D1-C1-as/out174.txt`
- `out copy/tests-D2-C2-as/out94.txt`
- `out copy/tests-D2-C1-ss/out121.txt`
- `out copy/tests-D1-C2-as/out137.txt`
- `out copy/tests-D2-C2-as/out141.txt`
- `out copy/tests-D2-C2-ss/out141.txt`
- `out copy/tests-D1-C0/out123.txt`
- `out copy/tests-D2-C1-as/out43.txt`
- `out copy/tests-D1-C0/out157.txt`
- `out copy/tests-D2-C1-as/out26.txt`
- `out copy/tests-D2-C2-ss/out182.txt`
- `out copy/tests-D2-C1-ss/out95.txt`
- `out copy/tests-D2-C2-ss/out190.txt`
- `out copy/tests-D2-C2-ss/out151.txt`
- `out copy/tests-D1-C1-as/out44.txt`
- `out copy/tests-D1-C1-ss/out137.txt`
- `out copy/tests-D1-C2-as/out109.txt`
- `out copy/tests-D2-C0/out6.txt`
- `out copy/tests-D2-C2-as/out175.txt`
- `out copy/tests-D1-C0/out41.txt`
- `out copy/tests-D2-C2-as/out18.txt`
- `out copy/tests-D2-C2-ss/out58.txt`
- `out copy/tests-D2-C1-as/out194.txt`
- `out copy/tests-D2-C2-ss/out36.txt`
- `out copy/tests-D2-C1-as/out145.txt`
- `out copy/tests-D2-C2-ss/out104.txt`
- `out copy/tests-D2-C2-as/out68.txt`
- `out copy/tests-D2-C2-as/out156.txt`
- `out copy/tests-D2-C2-as/out14.txt`
- `out copy/tests-D2-C2-as/out194.txt`
- `out copy/tests-D2-C2-as/out45.txt`
- `out copy/tests-D1-C2-ss/out73.txt`
- `out copy/tests-D2-C2-as/out35.txt`
- `out copy/tests-D2-C0/out187.txt`
- `out copy/tests-D2-C2-as/out153.txt`
- `out copy/tests-D1-C1-as/out79.txt`
- `out copy/tests-D1-C1-as/out90.txt`
- `out copy/tests-D2-C2-as/out66.txt`
- `out copy/tests-D1-C0/out3.txt`
- `out copy/tests-D2-C1-ss/out151.txt`
- `out copy/tests-D2-C0/out123.txt`
- `out copy/tests-D2-C1-ss/out11.txt`
- `out copy/tests-D2-C2-as/out48.txt`
- `out copy/tests-D2-C1-as/out41.txt`
- `out copy/tests-D2-C1-as/out66.txt`
- `out copy/tests-D2-C1-ss/out196.txt`
- `out copy/tests-D2-C1-as/out149.txt`
- `out copy/tests-D1-C2-ss/out41.txt`
- `out copy/tests-D2-C2-as/out181.txt`
- `out copy/tests-D2-C2-ss/out175.txt`
- `out copy/tests-D2-C2-ss/out119.txt`
- `out copy/tests-D2-C2-ss/out186.txt`
- `out copy/tests-D2-C2-as/out41.txt`
- `out copy/tests-D2-C2-as/out24.txt`
- `out copy/tests-D2-C2-as/out99.txt`
- `out copy/tests-D1-C2-ss/out146.txt`
- `out copy/tests-D2-C2-ss/out137.txt`
- `out copy/tests-D1-C2-ss/out19.txt`
- `out copy/tests-D2-C1-as/out95.txt`
- `out copy/tests-D2-C0/out159.txt`
- `out copy/tests-D1-C1-ss/out56.txt`
- `out copy/tests-D2-C1-as/out20.txt`
- `out copy/tests-D2-C2-ss/out27.txt`
- `out copy/tests-D2-C1-as/out151.txt`
- `out copy/tests-D2-C2-ss/out53.txt`
- `out copy/tests-D2-C2-ss/out77.txt`
- `out copy/tests-D2-C1-ss/out123.txt`
- `out copy/tests-D2-C1-as/out187.txt`
- `out copy/tests-D1-C2-ss/out170.txt`
- `out copy/tests-D2-C2-as/out60.txt`
- `out copy/tests-D1-C2-as/out145.txt`
- `out copy/tests-D2-C0/out115.txt`
- `out copy/tests-D1-C0/out36.txt`
- `out copy/tests-D2-C1-ss/out66.txt`
- `out copy/tests-D2-C0/out87.txt`
- `out copy/tests-D1-C0/out95.txt`
- `out copy/tests-D2-C2-as/out95.txt`
- `out copy/tests-D2-C1-as/out168.txt`
- `out copy/tests-D2-C0/out7.txt`
- `out copy/tests-D1-C1-ss/out44.txt`
- `out copy/tests-D2-C1-ss/out179.txt`
- `out copy/tests-D2-C2-ss/out48.txt`
- `out copy/tests-D1-C2-ss/out11.txt`
- `out copy/tests-D2-C1-ss/out119.txt`
- `out copy/tests-D2-C0/out199.txt`
- `out copy/tests-D2-C0/out66.txt`
- `out copy/tests-D2-C1-ss/out137.txt`
- `out copy/tests-D1-C1-ss/out119.txt`
- `out copy/tests-D1-C2-as/out190.txt`
- `out copy/tests-D1-C2-as/out86.txt`
- `out copy/tests-D2-C0/out14.txt`
- `out copy/tests-D2-C0/out136.txt`
- `out copy/tests-D1-C1-as/out66.txt`
- `out copy/tests-D2-C2-ss/out199.txt`
- `out copy/tests-D1-C2-ss/out94.txt`
- `out copy/tests-D2-C2-as/out37.txt`
- `out copy/tests-D1-C2-as/out136.txt`
- `out copy/tests-D2-C2-as/out129.txt`
- `out copy/tests-D2-C0/out99.txt`
- `out copy/tests-D2-C2-as/out7.txt`
- `out copy/tests-D2-C1-as/out16.txt`
- `out copy/tests-D2-C1-as/out79.txt`
- `out copy/tests-D2-C0/out73.txt`
- `out copy/tests-D2-C1-ss/out191.txt`
- `out copy/tests-D2-C1-ss/out26.txt`
- `out copy/tests-D2-C2-as/out197.txt`
- `out copy/tests-D2-C1-ss/out18.txt`
- `out copy/tests-D2-C1-as/out44.txt`
- `out copy/tests-D1-C2-ss/out66.txt`
- `out copy/tests-D2-C1-ss/out12.txt`
- `out copy/tests-D1-C1-ss/out170.txt`
- `out copy/tests-D2-C1-as/out9.txt`
- `out copy/tests-D2-C1-as/out119.txt`
- `out copy/tests-D2-C0/out41.txt`
- `out copy/tests-D2-C2-ss/out87.txt`
- `out copy/tests-D2-C2-as/out159.txt`
- `out copy/tests-D1-C1-ss/out112.txt`
- `out copy/tests-D2-C2-as/out157.txt`
- `out copy/tests-D2-C1-ss/out37.txt`
- `out copy/tests-D2-C1-ss/out58.txt`
- `out copy/tests-D2-C1-as/out123.txt`
- `out copy/tests-D2-C2-ss/out31.txt`
- `out copy/tests-D2-C0/out174.txt`
- `out copy/tests-D1-C1-ss/out7.txt`
- `out copy/tests-D2-C1-ss/out33.txt`
- `out copy/tests-D2-C2-ss/out140.txt`
- `out copy/tests-D2-C1-as/out191.txt`
- `out copy/tests-D1-C2-ss/out109.txt`
- `out copy/tests-D1-C2-as/out33.txt`
- `out copy/tests-D2-C1-ss/out6.txt`
- `out copy/tests-D2-C2-ss/out194.txt`
- `out copy/tests-D2-C2-as/out140.txt`
- `out copy/tests-D2-C2-as/out59.txt`
- `out copy/tests-D1-C2-as/out53.txt`
- `out copy/tests-D1-C0/out116.txt`
- `out copy/tests-D2-C1-as/out50.txt`
- `out copy/tests-D2-C0/out35.txt`
- `out copy/tests-D2-C2-as/out43.txt`
- `out copy/tests-D2-C1-as/out197.txt`
- `out copy/tests-D2-C1-as/out40.txt`
- `out copy/tests-D2-C1-ss/out162.txt`
- `out copy/tests-D1-C1-as/out27.txt`
- `out copy/tests-D2-C0/out144.txt`
- `out copy/tests-D2-C0/out166.txt`
- `out copy/tests-D2-C2-as/out192.txt`
- `out copy/tests-D2-C1-ss/out159.txt`
- `out copy/tests-D2-C2-as/out114.txt`
- `out copy/tests-D1-C1-as/out141.txt`
- `out copy/tests-D1-C2-ss/out56.txt`
- `out copy/tests-D2-C0/out137.txt`
- `out copy/tests-D2-C1-as/out114.txt`
- `out copy/tests-D1-C1-ss/out199.txt`
- `out copy/tests-D2-C2-ss/out132.txt`
- `out copy/tests-D2-C2-ss/out89.txt`
- `out copy/tests-D1-C0/out49.txt`
- `out copy/tests-D2-C2-ss/out196.txt`
- `out copy/tests-D1-C1-as/out95.txt`
- `out copy/tests-D2-C0/out129.txt`
- `out copy/tests-D1-C2-as/out11.txt`
- `out copy/tests-D2-C2-as/out116.txt`
- `out copy/tests-D2-C2-ss/out20.txt`
- `out copy/tests-D2-C1-ss/out9.txt`
- `out copy/tests-D1-C0/out11.txt`
- `out copy/tests-D2-C2-as/out19.txt`
- `out copy/tests-D2-C2-as/out20.txt`
- `out copy/tests-D1-C2-ss/out156.txt`
- `out copy/tests-D2-C1-ss/out110.txt`
- `out copy/tests-D2-C2-ss/out79.txt`
- `out copy/tests-D2-C0/out51.txt`
- `out copy/tests-D2-C2-ss/out100.txt`
- `out copy/tests-D2-C1-ss/out20.txt`
- `out copy/tests-D2-C1-as/out12.txt`
- `out copy/tests-D1-C0/out15.txt`
- `out copy/tests-D1-C2-as/out15.txt`
- `out copy/tests-D2-C1-as/out18.txt`
- `out copy/tests-D2-C1-as/out192.txt`
- `out copy/tests-D2-C2-ss/out11.txt`
- `out copy/tests-D2-C1-ss/out19.txt`
- `out copy/tests-D1-C2-as/out73.txt`
- `out copy/tests-D2-C2-ss/out19.txt`
- `out copy/tests-D1-C1-ss/out115.txt`
- `out copy/tests-D2-C0/out151.txt`
- `out copy/tests-D2-C0/out175.txt`
- `out copy/tests-D1-C1-ss/out3.txt`
- `out copy/tests-D2-C0/out20.txt`
- `out copy/tests-D1-C1-ss/out178.txt`
- `out copy/tests-D2-C2-ss/out56.txt`
- `out copy/tests-D2-C2-ss/out176.txt`
- `out copy/tests-D2-C1-as/out96.txt`
- `out copy/tests-D2-C0/out58.txt`
- `out copy/tests-D2-C2-ss/out45.txt`
- `out copy/tests-D1-C1-ss/out94.txt`
- `out copy/tests-D1-C0/out136.txt`
- `out copy/tests-D2-C0/out156.txt`
- `out copy/tests-D1-C2-ss/out140.txt`
- `out copy/tests-D1-C2-ss/out116.txt`
- `out copy/tests-D1-C0/out73.txt`
- `out copy/tests-D1-C0/out186.txt`
- `out copy/tests-D2-C2-ss/out156.txt`
- `out copy/tests-D1-C0/out77.txt`
- `out copy/tests-D2-C2-as/out191.txt`
- `out copy/tests-D1-C2-ss/out149.txt`
- `out copy/tests-D2-C2-ss/out60.txt`
- `out copy/tests-D2-C2-ss/out3.txt`
- `out copy/tests-D1-C1-as/out146.txt`
- `out copy/tests-D1-C2-ss/out60.txt`
- `out copy/tests-D1-C1-as/out166.txt`
- `out copy/tests-D2-C2-ss/out57.txt`
- `out copy/tests-D1-C1-ss/out90.txt`
- `out copy/tests-D0-C2-ss/out191.txt`
- `out copy/tests-D2-C1-as/out87.txt`
- `out copy/tests-D2-C0/out30.txt`
- `out copy/tests-D1-C2-ss/out145.txt`
- `out copy/tests-D2-C2-as/out73.txt`
- `out copy/tests-D1-C0/out107.txt`
- `out copy/tests-D1-C1-as/out103.txt`
- `out copy/tests-D2-C1-ss/out40.txt`
- `out copy/tests-D1-C2-ss/out167.txt`
- `out copy/tests-D1-C2-as/out156.txt`
- `out copy/tests-D1-C1-ss/out103.txt`
- `out copy/tests-D1-C1-ss/out49.txt`
- `out copy/tests-D2-C2-as/out9.txt`
- `out copy/tests-D1-C1-as/out109.txt`
- `out copy/tests-D2-C1-as/out14.txt`
- `out copy/tests-D2-C2-ss/out95.txt`
- `out copy/tests-D2-C0/out61.txt`
- `out copy/tests-D2-C0/out82.txt`
- `out copy/tests-D2-C2-as/out132.txt`
- `out copy/tests-D2-C1-ss/out79.txt`
- `out copy/tests-D2-C1-ss/out51.txt`
- `out copy/tests-D2-C2-ss/out166.txt`
- `out copy/tests-D2-C1-as/out121.txt`
- `out copy/tests-D1-C2-ss/out123.txt`
- `out copy/tests-D1-C1-ss/out15.txt`
- `out copy/tests-D2-C1-ss/out99.txt`
- `out copy/tests-D2-C2-as/out77.txt`
- `out copy/tests-D1-C2-as/out196.txt`
- `out copy/tests-D1-C2-ss/out93.txt`
- `out copy/tests-D2-C1-as/out19.txt`
- `out copy/tests-D2-C2-as/out110.txt`
- `out copy/tests-D1-C0/out166.txt`
- `out copy/tests-D2-C2-as/out6.txt`
- `out copy/tests-D2-C1-ss/out174.txt`
- `out copy/tests-D2-C2-as/out79.txt`
- `out copy/tests-D2-C2-ss/out41.txt`
- `out copy/tests-D2-C2-as/out135.txt`
- `out copy/tests-D1-C2-as/out19.txt`
- `out copy/tests-D1-C0/out146.txt`
- `out copy/tests-D1-C1-ss/out145.txt`
- `out copy/tests-D2-C1-as/out141.txt`
- `out copy/tests-D2-C0/out96.txt`
- `out copy/tests-D2-C1-ss/out178.txt`

</details>

### Iteration 2 — Tarantula 0.1606

**Predicate**: `BRANCH DefaultReplica.java:319 is true`

**Aggregation**: f_true=27, f_false=101, s_true=163, s_false=2217

**Pipeline state at iteration start**: 2508 reports, 76 aggregations, 18 filtered aggregations, 128 failed reports.

**Removed runs**: 27

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 18.5% | 0.0% | 81.5% | 0.0% |
| Recall | 9.3% | 0.0% | 6.4% | 0.0% |
| F1 | 12.3% | 0.0% | 11.9% | 0.0% |
| F0.5 | 15.4% | 0.0% | 24.3% | 0.0% |
| Specificity | 99.2% | 99.0% | 99.8% | 99.0% |
| Accuracy | 97.5% | 98.2% | 88.3% | 99.0% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D1-C1-ss/out27.txt`
- `out copy/tests-D2-C1-as/out136.txt`
- `out copy/tests-D2-C0/out79.txt`
- `out copy/tests-D2-C1-ss/out52.txt`
- `out copy/tests-D1-C2-ss/out174.txt`
- `out copy/tests-D1-C1-as/out36.txt`
- `out copy/tests-D1-C2-as/out41.txt`
- `out copy/tests-D2-C2-ss/out4.txt`
- `out copy/tests-D2-C1-ss/out153.txt`
- `out copy/tests-D1-C1-ss/out182.txt`
- `out copy/tests-D2-C1-ss/out185.txt`
- `out copy/tests-D2-C2-ss/out153.txt`
- `out copy/tests-D1-C2-as/out149.txt`
- `out copy/tests-D1-C1-ss/out143.txt`
- `out copy/tests-D2-C1-ss/out59.txt`
- `out copy/tests-D1-C2-ss/out7.txt`
- `out copy/tests-D2-C1-as/out52.txt`
- `out copy/tests-D1-C0/out57.txt`
- `out copy/tests-D2-C0/out59.txt`
- `out copy/tests-D2-C2-ss/out16.txt`
- `out copy/tests-D2-C1-ss/out41.txt`
- `out copy/tests-D0-C2-ss/out93.txt`
- `out copy/tests-D1-C1-ss/out85.txt`
- `out copy/tests-D2-C1-as/out99.txt`
- `out copy/tests-D2-C0/out50.txt`
- `out copy/tests-D2-C2-ss/out43.txt`
- `out copy/tests-D1-C2-as/out48.txt`

</details>

### Iteration 3 — Tarantula 0.0879

**Predicate**: `BRANCH DefaultReplica.java:292 is true`

**Aggregation**: f_true=44, f_false=57, s_true=461, s_false=1919

**Pipeline state at iteration start**: 2481 reports, 76 aggregations, 13 filtered aggregations, 101 failed reports.

**Removed runs**: 44

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 11.4% | 4.5% | 81.8% | 2.3% |
| Recall | 9.3% | 9.1% | 10.5% | 50.0% |
| F1 | 10.2% | 6.1% | 18.6% | 4.3% |
| F0.5 | 10.9% | 5.1% | 34.6% | 2.8% |
| Specificity | 98.6% | 98.5% | 99.7% | 98.5% |
| Accuracy | 96.9% | 97.8% | 88.7% | 98.4% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D1-C1-as/out57.txt`
- `out copy/tests-D1-C1-as/out157.txt`
- `out copy/tests-D2-C1-ss/out136.txt`
- `out copy/tests-D1-C1-ss/out37.txt`
- `out copy/tests-D1-C2-as/out133.txt`
- `out copy/tests-D1-C2-ss/out36.txt`
- `out copy/tests-D2-C1-ss/out44.txt`
- `out copy/tests-D1-C2-as/out36.txt`
- `out copy/tests-D2-C2-as/out27.txt`
- `out copy/tests-D2-C1-as/out162.txt`
- `out copy/tests-D2-C1-as/out175.txt`
- `out copy/tests-D2-C1-ss/out129.txt`
- `out copy/tests-D2-C1-ss/out140.txt`
- `out copy/tests-D2-C2-ss/out96.txt`
- `out copy/tests-D2-C2-ss/out178.txt`
- `out copy/tests-D1-C1-ss/out53.txt`
- `out copy/tests-D2-C2-as/out96.txt`
- `out copy/tests-D1-C0/out133.txt`
- `out copy/tests-D2-C1-as/out53.txt`
- `out copy/tests-D2-C1-as/out6.txt`
- `out copy/tests-D1-C1-ss/out136.txt`
- `out copy/tests-D1-C1-as/out123.txt`
- `out copy/tests-D1-C2-as/out93.txt`
- `out copy/tests-D2-C0/out56.txt`
- `out copy/tests-D2-C2-ss/out64.txt`
- `out copy/tests-D2-C0/out43.txt`
- `out copy/tests-D1-C0/out170.txt`
- `out copy/tests-D2-C2-as/out104.txt`
- `out copy/tests-D2-C2-ss/out136.txt`
- `out copy/tests-D1-C0/out141.txt`
- `out copy/tests-D1-C1-ss/out186.txt`
- `out copy/tests-D2-C0/out185.txt`
- `out copy/tests-D2-C2-as/out112.txt`
- `out copy/tests-D2-C1-ss/out186.txt`
- `out copy/tests-D2-C0/out36.txt`
- `out copy/tests-D1-C1-ss/out174.txt`
- `out copy/tests-D2-C2-as/out136.txt`
- `out copy/tests-D2-C0/out178.txt`
- `out copy/tests-D1-C1-as/out178.txt`
- `out copy/tests-D1-C2-ss/out196.txt`
- `out copy/tests-D2-C0/out40.txt`
- `out copy/tests-D1-C1-as/out136.txt`
- `out copy/tests-D2-C0/out112.txt`
- `out copy/tests-D0-C2-as/out93.txt`

</details>

### Iteration 4 — Tarantula 0.0159

**Predicate**: `BRANCH DefaultReplica.java:173 is true`

**Aggregation**: f_true=32, f_false=25, s_true=987, s_false=1393

**Pipeline state at iteration start**: 2437 reports, 76 aggregations, 7 filtered aggregations, 57 failed reports.

**Removed runs**: 32

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 50.0% | 0.0% | 50.0% | 0.0% |
| Recall | 29.6% | 0.0% | 4.7% | 0.0% |
| F1 | 37.2% | 0.0% | 8.5% | 0.0% |
| F0.5 | 44.0% | 0.0% | 16.9% | 0.0% |
| Specificity | 99.4% | 98.8% | 99.3% | 98.9% |
| Accuracy | 98.1% | 98.1% | 87.7% | 98.8% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D1-C1-ss/out109.txt`
- `out copy/tests-D1-C1-as/out151.txt`
- `out copy/tests-D2-C2-as/out71.txt`
- `out copy/tests-D1-C1-ss/out151.txt`
- `out copy/tests-D2-C2-ss/out146.txt`
- `out copy/tests-D2-C1-as/out59.txt`
- `out copy/tests-D2-C2-as/out26.txt`
- `out copy/tests-D2-C2-as/out146.txt`
- `out copy/tests-D0-C1-ss/out121.txt`
- `out copy/tests-D2-C2-ss/out181.txt`
- `out copy/tests-D2-C2-ss/out129.txt`
- `out copy/tests-D0-C2-as/out91.txt`
- `out copy/tests-D1-C2-ss/out43.txt`
- `out copy/tests-D2-C2-ss/out91.txt`
- `out copy/tests-D1-C2-ss/out120.txt`
- `out copy/tests-D1-C2-as/out81.txt`
- `out copy/tests-D2-C1-as/out181.txt`
- `out copy/tests-D2-C2-ss/out98.txt`
- `out copy/tests-D2-C1-ss/out100.txt`
- `out copy/tests-D2-C1-ss/out43.txt`
- `out copy/tests-D1-C2-as/out43.txt`
- `out copy/tests-D0-C1-as/out121.txt`
- `out copy/tests-D2-C2-as/out143.txt`
- `out copy/tests-D2-C2-ss/out102.txt`
- `out copy/tests-D2-C1-as/out100.txt`
- `out copy/tests-D2-C2-ss/out71.txt`
- `out copy/tests-D2-C2-ss/out185.txt`
- `out copy/tests-D0-C2-ss/out91.txt`
- `out copy/tests-D1-C2-as/out120.txt`
- `out copy/tests-D0-C2-ss/out95.txt`
- `out copy/tests-D2-C2-as/out91.txt`
- `out copy/tests-D0-C2-as/out95.txt`

</details>

### Iteration 5 — Tarantula 0.0224

**Predicate**: `WHILE DefaultReplica.java:684 is false`

**Aggregation**: f_true=2, f_false=2, s_true=124, s_false=863

**Pipeline state at iteration start**: 2405 reports, 76 aggregations, 4 filtered aggregations, 25 failed reports.

**Removed runs**: 2

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 0.0% | 50.0% | 50.0% | 0.0% |
| Recall | 0.0% | 4.5% | 0.3% | 0.0% |
| F1 | 0.0% | 8.3% | 0.6% | 0.0% |
| F0.5 | 0.0% | 16.7% | 1.4% | 0.0% |
| Specificity | 99.9% | 100.0% | 100.0% | 99.9% |
| Accuracy | 98.0% | 99.2% | 87.7% | 99.9% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-ss/out15.txt`
- `out copy/tests-D1-C2-as/out171.txt`

</details>

### Iteration 6 — Tarantula 0.0005

**Predicate**: `BRANCH DefaultReplica.java:526 is true`

**Aggregation**: f_true=20, f_false=3, s_true=2013, s_false=367

**Pipeline state at iteration start**: 2403 reports, 76 aggregations, 4 filtered aggregations, 23 failed reports.

**Removed runs**: 20

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 100.0% | 0.0% | 0.0% | 0.0% |
| Recall | 37.0% | 0.0% | 0.0% | 0.0% |
| F1 | 54.1% | 0.0% | 0.0% | 0.0% |
| F0.5 | 74.6% | 0.0% | 0.0% | 0.0% |
| Specificity | 100.0% | 99.3% | 99.2% | 99.3% |
| Accuracy | 98.8% | 98.5% | 87.0% | 99.2% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D0-C1-ss/out143.txt`
- `out copy/tests-D2-C2-ss/out143.txt`
- `out copy/tests-D1-C2-ss/out100.txt`
- `out copy/tests-D0-C1-ss/out95.txt`
- `out copy/tests-D0-C2-as/out100.txt`
- `out copy/tests-D0-C2-as/out148.txt`
- `out copy/tests-D1-C2-as/out130.txt`
- `out copy/tests-D1-C2-ss/out126.txt`
- `out copy/tests-D0-C1-as/out143.txt`
- `out copy/tests-D1-C2-ss/out130.txt`
- `out copy/tests-D0-C2-ss/out148.txt`
- `out copy/tests-D2-C1-ss/out181.txt`
- `out copy/tests-D1-C2-as/out126.txt`
- `out copy/tests-D0-C1-ss/out108.txt`
- `out copy/tests-D1-C2-as/out100.txt`
- `out copy/tests-D0-C2-ss/out100.txt`
- `out copy/tests-D0-C1-as/out108.txt`
- `out copy/tests-D0-C1-as/out95.txt`
- `out copy/tests-D0-C2-ss/out126.txt`
- `out copy/tests-D0-C2-as/out126.txt`

</details>

### Iteration 7 — Tarantula 0.0029

**Predicate**: `BRANCH DefaultReplica.java:244 is true`

**Aggregation**: f_true=3, f_false=0, s_true=1104, s_false=1276

**Pipeline state at iteration start**: 2383 reports, 76 aggregations, 13 filtered aggregations, 3 failed reports.

**Removed runs**: 3

| Metric | Operation Corruption | View-Change Fault | Quorum Stall | Split Brain |
|--------|----------------------|-------------------|--------------|-------------|
| Precision | 0.0% | 33.3% | 66.7% | 0.0% |
| Recall | 0.0% | 4.5% | 0.6% | 0.0% |
| F1 | 0.0% | 8.0% | 1.2% | 0.0% |
| F0.5 | 0.0% | 14.7% | 2.8% | 0.0% |
| Specificity | 99.9% | 99.9% | 100.0% | 99.9% |
| Accuracy | 98.0% | 99.2% | 87.8% | 99.8% |

<details><summary>Removed run paths</summary>

- `out copy/tests-D2-C2-as/out52.txt`
- `out copy/tests-D2-C2-as/out186.txt`
- `out copy/tests-D1-C0/out196.txt`

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
