# PBFT Root Cause Analysis

Analysis of all failing ByzzFuzz PBFT scenarios across 8 configurations.
Scope: small-scope mutations when process faults are present (D0/D1/D2-C1/C2-ss); all runs for network-fault-only configs (D1-C0, D2-C0).

---

## Root Cause Groups

### Group A — Operation field mutation in PRE-PREPARE

**Mechanism:** Byzantine leader (R0) mutates `operation.first` by ±1 in the PRE-PREPARE sent to a subset of replicas. Because every message carries `"digest":""`, there is no cryptographic binding between the PRE-PREPARE and the actual client request. Receivers accept the mutated content, build a valid Prepare certificate for the wrong value, and commit it — while the unaffected replicas commit the correct value. The result is VALIDITY (committed value ≠ requested value) and/or AGREEMENT (replicas committed different values for the same seqNo).

**Violations:** Validity, Agreement

| Config | Files |
|---|---|
| D0-C1-ss | out95, out108, out121, out143 |
| D0-C2-ss | out91¹, out93, out95¹, out100, out126, out148 |
| D1-C1-ss | out109, out136 |
| D1-C2-ss | out100, out109, out120², out126, out130, out43², out167 |
| D2-C1-ss | out100, out181 |
| D2-C2-ss | out143, out181 |

¹ Also in termination list — partition causes timeout after violations are fired
² Also in termination list — same reason

---

### Group B — Seq-number mutation in PRE-PREPARE

**Mechanism:** Byzantine leader (R0) increments the `seq-number` field by +1 in a PRE-PREPARE sent to a subset of replicas. The affected replicas commit the wrong request (an older request's content replayed at a new slot). Because `"digest":""` does not bind content to sequence number, the Prepare certificate for the wrong binding is accepted. After view-changes propagate the inconsistent committed state, replicas that carried the bogus prepared-proof disagree with those that did not.

**Violations:** Agreement (often after view-change; viewNo > 0 in the violation log)

| Config | Files |
|---|---|
| D1-C1-ss | out143 |
| D1-C2-ss | out7 |
| D2-C2-ss | out40, out100, out16¹ |

¹ out16 also has a COMMIT view-number=−1 mutation as a secondary corruption; the seq-number mutation is the primary cause of the observed Agreement violation

---

### Group C — VIEW-CHANGE / NEW-VIEW corruption

**Mechanism:** After a network partition forces a view-change, the byzantine replica sends a malformed VIEW-CHANGE or NEW-VIEW message (corrupted prepared-proofs, checkpoint data, or view-number). The new primary cannot assemble a consistent NEW-VIEW and the protocol stalls. In some cases (D2-C1-ss out49, out65) the malformed NEW-VIEW causes the new primary to propose conflicting values to different replicas, resulting in an Agreement violation. In most cases the system times out.

**Violations:** Termination (timeout), Agreement (D2-C1-ss out49, out65)

| Config | Files |
|---|---|
| D1-C2-ss | out49 (termination) |
| D2-C1-ss | out49, out65 (agreement); out24, out175 (termination) |
| D2-C2-ss | out87, out151, out73, out175, out31 (termination) |

---

### Group D — Network partition prevents quorum → timeout

**Mechanism:** A partition splits the 4-replica network such that no 2f+1=3 replica subset can communicate. PREPARE/COMMIT phases stall; view-change is triggered. If the partition spans multiple rounds or the new primary's view is also disrupted, no view recovers the protocol. In D1/D2-Cx-ss cases, concurrent process faults (PREPARE/COMMIT field mutations) are present but are on non-critical messages — the partition alone kills liveness.

**Violations:** Termination only

| Config | Count | Files |
|---|---|---|
| D1-C0 | 12 | out115, out123, out192, out175, out116, out195, out140, out95, out86, out79, out178, out145 |
| D2-C0 | 31 | out20, out49, out93, out159, out115, out96, out151, out185, out73, out56, out70, out114, out11, out51, out168, out132, out44, out27, out136, out53, out4, out16, out66, out24, out178, out176, out144, out36, out146, out99, out60 |
| D1-C1-ss | 17 | out93, out90, out123, out122, out77, out15, out44, out118, out186, out66, out95, out112, out57, out103, out86, out36, out19 |
| D1-C2-ss | 14 | out190, out81, out166, out73, out56, out123, out107, out118, out94, out136, out41, out79, out196, out19 |
| D2-C1-ss | 35 | out194, out190, out87, out159, out48, out166, out151, out9, out123, out163, out50, out43, out70, out114, out11, out52, out45, out94, out136, out197, out121, out129, out95, out41, out12, out3, out30, out26, out174, out110, out19, out18, out150, out99, out145 |
| D2-C2-ss | 36 | out17, out20, out194, out104, out115, out185, out68, out56, out71, out162, out9, out43, out122, out11, out51, out52, out168, out116, out45, out59, out195, out89, out27, out140, out197, out121, out12, out30, out26, out196, out174, out91, out144, out110, out18, out150 |

---

### Group E — Network partition induces split-brain across view-changes

**Mechanism:** Two network partitions across different rounds (D2-C0) or combined with process faults that do not produce visible message mutations (D2-Cx-ss high-viewNo cases) force the protocol through multiple view-changes (viewNo ≥ 2 in violations). Different replica subsets carry inconsistent prepared state from prior views into subsequent leaders. The new leader installs conflicting values for the same seqNo, producing Agreement violations without any single detectable Byzantine operation mutation.

**Violations:** Agreement only

| Config | Files |
|---|---|
| D2-C0 | out87, out197 |
| D2-C1-ss | out66 |
| D2-C2-ss | out199, out15, out66, out176 |

---

## Summary by Configuration

| Config | Group A | Group B | Group C | Group D | Group E | Total failing |
|---|---|---|---|---|---|---|
| D0-C1-ss | out95, out108, out121, out143 | — | — | — | — | 4 |
| D0-C2-ss | out91, out93, out95, out100, out126, out148 | — | — | — | — | 6 |
| D1-C0 | — | — | — | 12 files | — | 12 |
| D1-C1-ss | out109, out136 | out143 | — | 17 files | — | 20 |
| D1-C2-ss | out100, out109, out120, out126, out130, out43, out167 | out7 | out49 | 14 files | — | 23 |
| D2-C0 | — | — | — | 31 files | out87, out197 | 33 |
| D2-C1-ss | out100, out181 | — | out49, out65, out24, out175 | 35 files | out66 | 43 |
| D2-C2-ss | out143, out181 | out40, out100, out16 | out87, out151, out73, out175, out31 | 36 files | out199, out15, out66, out176 | 52 |

---

## Enabling Condition

All Groups A and B are enabled by the same implementation flaw: **the empty digest field** (`"digest":""`) in every PBFT message. In a correct implementation the digest cryptographically binds the PRE-PREPARE to the exact request content and sequence number, so any mutation would be detected during the PREPARE phase. With an empty digest, replicas cannot distinguish a legitimate PRE-PREPARE from a mutated one, allowing the byzantine leader to commit arbitrary content (Group A) or sequence-number confusion (Group B) at will.

Group C is enabled by the same flaw in the view-change path: prepared-proofs embedded in VIEW-CHANGE messages are not verified against a content hash, so corrupted proofs are accepted.

Groups D and E are purely network-level faults and do not depend on the digest vulnerability.
