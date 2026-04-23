# PBFT Root Cause Analysis

Analysis of all failing ByzzFuzz PBFT scenarios across 14 configurations from the `out copy` dataset.
Scope: both any-scope (as) and small-scope (ss) mutations when process faults are present; all runs for network-fault-only configs (D1-C0, D2-C0).

---

## Root Cause Groups

### Group A — Operation field mutation in PRE-PREPARE

**Mechanism:** Byzantine leader (R0) mutates the `operation` field in the PRE-PREPARE sent to a subset of replicas. With any-scope mutations, the field value can change to an arbitrary integer (e.g., `1 → -694650256`); with small-scope, the change is ±1 (e.g., `2 → 1`). Because every message carries `"digest":""`, there is no cryptographic binding between the PRE-PREPARE and the actual client request. Receivers accept the mutated content, build a valid Prepare certificate for the wrong value, and commit it — while unaffected replicas commit the correct value.

**Violations:** Validity, Agreement

| Config | Files |
|---|---|
| D0-C1-as | out95, out108, out121, out143 |
| D0-C1-ss | out95, out108, out121, out143 |
| D0-C2-as | out91, out93^ab, out95, out100, out126, out148 |
| D0-C2-ss | out91, out93^ab, out95, out100, out126, out148 |
| D1-C1-as | out109, out136 |
| D1-C1-ss | out109, out136 |
| D1-C2-as | out43, out100, out109, out120, out126, out130 |
| D1-C2-ss | out43, out100, out109, out120, out126, out130 |
| D2-C1-as | out100, out181 |
| D2-C1-ss | out100, out181 |
| D2-C2-as | out112^v, out143, out181 |
| D2-C2-ss | out64, out143, out181 |

^ab Also classified as Seq-No Replay (both operation and sequence mutations in the same run)
^v View-number mutation in PRE-PREPARE (`view-number: 2056981445`) rather than operation field — causes indirect agreement divergence

**Any-scope vs small-scope:** The same scenarios fail in both scopes with identical root causes but different mutation magnitudes. Any-scope values (e.g., `first: -694650256`) are immediately obvious in logs; small-scope values (e.g., `first: 1` instead of `2`) are subtler but equally harmful.

---

### Group B — Seq-number mutation in PRE-PREPARE

**Mechanism:** Byzantine leader (R0) mutates the `seq-number` field in a PRE-PREPARE sent to a subset of replicas. With any-scope, the seq-number can jump to a wildly different value (e.g., `0 → 644426466`); with small-scope, the change is +1 (e.g., `0 → 1`). The affected replicas process the request at an incorrect sequence slot. Because `"digest":""` does not bind content to sequence number, the Prepare certificate for the wrong binding is accepted. When the real request for that slot arrives, replicas that already committed the wrong binding disagree with those that committed correctly.

**Violations:** Agreement (after view-change), Termination (when seq jump is large enough to stall)

| Config | Files |
|---|---|
| D0-C2-as | out93^ab |
| D0-C2-ss | out93^ab |
| D1-C1-ss | out85^t, out143 |
| D1-C2-ss | out7, out167 |
| D2-C1-ss | out175^m |
| D2-C2-ss | out16, out40, out100 |

^ab Also classified as Invalid Operation (dual mutation in same run)
^t Termination only — seq confusion combined with partition prevents recovery
^m Multi-mutation scenario: also classified as View-Change Fault (Group C)

**Any-scope vs small-scope:** Group B is significantly more common in small-scope configurations. With small-scope, the +1 offset places the request at an adjacent and reachable sequence slot, creating a subtle but harmful binding conflict. With any-scope, the wildly different seq-number puts the request at an unreachable slot, causing the protocol to stall (termination) rather than creating an agreement conflict. The only any-scope Group B scenario (out93) involves a dual mutation where the operation mutation (Group A) is the primary violation trigger.

---

### Group C — VIEW-CHANGE / NEW-VIEW corruption

**Mechanism:** After a network partition forces a view-change, the Byzantine replica sends a malformed VIEW-CHANGE or NEW-VIEW message. With any-scope, fields can be wildly corrupted (e.g., `last-seq-number: 515435746`); with small-scope, the corruption is ±1. The new primary cannot assemble a consistent NEW-VIEW and the protocol stalls. In some cases the corrupted view-change data causes the new primary to install conflicting values, leading to Agreement violations.

**Violations:** Termination (timeout), Agreement (when corruption leads to conflicting commits)

| Config | Files |
|---|---|
| D1-C2-as | out49, out171 |
| D1-C2-ss | out157 |
| D2-C1-as | out175, out187 |
| D2-C1-ss | out33, out175^m, out186 |
| D2-C2-as | out24, out48, out73, out79, out175, out186 |
| D2-C2-ss | out31, out48, out58, out79, out87^e, out151, out175, out186 |

^m Multi-mutation scenario: COMMIT, VIEW-CHANGE, and PRE-PREPARE all corrupted in the same round; also classified as Seq-No Replay (Group B)
^e Also classified as Split Brain (Group E) — Agreement violation at viewNo ≥ 2 after corrupted VIEW-CHANGE

**Any-scope vs small-scope:** Group C appears more frequently in small-scope configurations, particularly at D2-C2-ss (8 scenarios) compared to D2-C2-as (6 scenarios). In small-scope, the ±1 corruption can be subtle enough that view-change processing partially succeeds but installs inconsistent state, while any-scope corruption is often so extreme that the message is simply rejected.

---

### Group D — Network partition prevents quorum → timeout

**Mechanism:** A partition splits the 4-replica network such that no 2f+1=3 replica subset can communicate. PREPARE/COMMIT phases stall; view-change is triggered. If the partition spans multiple rounds or the new primary's view is also disrupted, no view recovers the protocol. In Dx-Cy configs, concurrent process faults (PREPARE/COMMIT field mutations) may be present but are on non-critical messages — the partition alone kills liveness.

**Violations:** Termination only

| Config | Count | Files |
|---|---|---|
| D1-C0 | 24 | out3, out11, out15, out36, out41, out49, out57, out73, out77, out95, out107, out115, out116, out123, out133, out136, out141, out146, out157, out166, out170, out182, out186, out196 |
| D1-C1-as | 17 | out7, out11, out27, out36, out44, out66, out79, out90, out95, out103, out119, out123, out141, out151, out157, out166, out174 |
| D1-C1-ss | 24 | out3, out7, out15, out27, out37, out44, out49, out56, out79, out90, out93, out94, out103, out112, out115, out119, out137, out145, out151, out174, out182, out186, out195, out199 |
| D1-C2-as | 12 | out11, out15, out36, out48, out73, out81, out93, out103, out136, out145, out149, out196 |
| D1-C2-ss | 17 | out11, out19, out36, out44, out56, out60, out73, out93, out94, out99, out116, out123, out140, out145, out149, out174, out196 |
| D2-C0 | 46 | out6, out7, out9, out14, out18, out20, out30, out35, out36, out37, out40, out41, out43, out50, out51, out56, out57, out58, out59, out61, out66, out73, out79, out82, out87, out90, out96, out99, out115, out123, out129, out136, out137, out144, out149, out151, out156, out159, out166, out174, out175, out178, out185, out186, out187, out199 |
| D2-C1-as | 37 | out6, out9, out12, out14, out16, out17, out18, out19, out20, out26, out40, out41, out44, out50, out52, out59, out66, out79, out87, out95, out99, out114, out119, out121, out123, out132, out136, out149, out151, out157, out159, out160, out162, out174, out192, out194, out197 |
| D2-C1-ss | 38 | out6, out9, out11, out12, out18, out19, out20, out26, out37, out40, out41, out44, out51, out52, out58, out59, out66, out73, out79, out95, out99, out110, out119, out121, out123, out129, out136, out137, out140, out151, out153, out159, out162, out174, out178, out179, out185, out196 |
| D2-C2-as | 27 | out6, out7, out9, out18, out19, out20, out35, out36, out37, out52, out59, out60, out66, out71, out94, out95, out114, out116, out129, out132, out135, out156, out157, out159, out191, out192, out194 |
| D2-C2-ss | 25 | out3, out7, out11, out15, out20, out36, out51, out52, out60, out71, out95, out102, out129, out132, out156, out163, out166, out176, out178, out184, out190, out194, out196, out197, out199 |

---

### Group E — Network partition induces split-brain across view-changes

**Mechanism:** Two network partitions across different rounds force the protocol through multiple view-changes (viewNo ≥ 2 in violations). Different replica subsets carry inconsistent prepared state from prior views into subsequent leaders. The new leader installs conflicting values for the same seqNo, producing Agreement violations without any single detectable Byzantine operation mutation.

**Violations:** Agreement only

| Config | Files |
|---|---|
| D2-C0 | out112 |
| D2-C2-ss | out87^c |

^c Also classified as View-Change Fault (Group C) — VC/NV mutation present alongside Agreement at viewNo ≥ 2

---

### Group F — COMMIT / PREPARE / REPLY mutation causing timeout

**Mechanism:** The Byzantine replica mutates a COMMIT, PREPARE, or REPLY message (corrupted `view-number`, `seq-number`, or `replica-id` fields). Unlike PRE-PREPARE mutations which corrupt the request binding, these mutations disrupt the commit or reply phase. With any-scope, fields can be wildly corrupted (e.g., `view-number: -21162180`); with small-scope, the corruption is ±1 (e.g., `view-number: -1`). The corrupted message delays or prevents the protocol from completing the current round. Combined with a network partition that triggers view-changes, the system enters a livelock across views.

**Violations:** Termination only

| Config | Count | Files |
|---|---|---|
| D0-C2-ss | 1 | out191 |
| D1-C1-as | 3 | out57, out146, out178 |
| D1-C1-ss | 3 | out53, out170, out178 |
| D1-C2-as | 9 | out19, out33, out41, out53, out86, out133, out137, out156, out190 |
| D1-C2-ss | 5 | out41, out66, out146, out156, out170 |
| D2-C1-as | 7 | out43, out53, out96, out141, out145, out168, out191 |
| D2-C1-ss | 4 | out30, out43, out77, out191 |
| D2-C2-as | 21 | out14, out26, out27, out41, out42, out43, out45, out68, out77, out91, out96, out99, out104, out110, out136, out140, out141, out146, out153, out178, out197 |
| D2-C2-ss | 24 | out4, out19, out27, out41, out43, out45, out53, out56, out57, out77, out89, out91, out96, out98, out104, out119, out136, out137, out140, out141, out146, out153, out182, out185 |

**Any-scope vs small-scope:** Group F appears with similar frequency across both scopes. These mutations alone rarely cause safety violations — they primarily stall the protocol by disrupting the commit or view-change mechanics. The livelock pattern is characteristic: replicas repeatedly enter view-changes but never converge because the corrupted message poisons one or more views.

**Note:** In the pre-instrumentation analysis, Group F scenarios were incorrectly classified as "Partition Timeout" (Group D) because the classification heuristic defaulted to Group D for any termination-only failure. The distinction matters: Group D requires no Byzantine faults (partition alone kills liveness), while Group F requires a specific message corruption that disrupts the commit/view-change path. Group F is identifiable by the presence of a non-PRE-PREPARE mutation (COMMIT, PREPARE, or REPLY) in a scenario that terminates without safety violations.

---

## Edge Cases

### D0-C2-as/out93 and D0-C2-ss/out93 — Dual mutation (Group A + Group B)

Two PRE-PREPARE mutations in the same run: the first (round 1) mutates the operation field (Group A, `operation.first: 1 → 143065580` in as, `1 → 0` in ss), the second (round 5) mutates the sequence number (Group B, `seq-number: 1 → 644426466` in as, `1 → 2` in ss). Both exploit the empty digest vulnerability. The VALIDITY violations are triggered by the operation mutation. The seq-number mutation creates additional confusion but is secondary.

### D2-C2-as/out112 — View-number mutation in PRE-PREPARE

The PRE-PREPARE has a wildly mutated `view-number` field (`2056981445`) rather than an operation or seq-number mutation. The operation itself is correct (`first: 2, second: 2`). Combined with 2 network partitions, this causes agreement divergence without a direct VALIDITY violation — the mutated view-number confuses the replica's view tracking. Classified as Group A variant because the mutation is in a PRE-PREPARE at the expected sequence slot.

### D2-C1-ss/out175 — Multi-mutation scenario

Three types of mutations in the same run: COMMIT (view-number corruption), VIEW-CHANGE (last-seq-number corruption and prepared-proof corruption), and PRE-PREPARE (seq-number mutation at new view). This is a complex interaction where the COMMIT mutation disrupts the initial round, the VIEW-CHANGE corruption disrupts recovery, and the PRE-PREPARE mutation in the new view compounds the confusion. The system times out. Classified as Group B (Seq-No Replay, from the PRE-PREPARE seq-number mutation) and Group C (View-Change Fault, from the VC/NV corruption).

### D2-C2-ss/out87 — Split Brain with View-Change corruption

Agreement violation at viewNo ≥ 2 with a concurrent VIEW-CHANGE mutation. Classified as both Group C (View-Change Fault) and Group E (Split Brain). The VC/NV corruption may compound the partition-induced divergence, but the high-view Agreement violation is the defining characteristic of Split Brain.

### D2-C2-ss/out15 — Agreement violation without mutations, viewNo=1

Agreement violation at viewNo=1 caused by network partitions alone, without any visible Byzantine mutation affecting the safety-critical path. The partition causes replicas to carry inconsistent prepared state through a single view-change. Classified as Group D (Partition Timeout) by the automated classifier because viewNo=1 is below the Group E threshold (viewNo ≥ 2). Mechanistically similar to Group E but at a lower view number.

---

## Summary by Configuration

| Config | A | B | C | D | E | F | Total |
|---|---|---|---|---|---|---|---|
| D0-C1-as | 4 | — | — | — | — | — | 4 |
| D0-C1-ss | 4 | — | — | — | — | — | 4 |
| D0-C2-as | 6^1 | 1^1 | — | — | — | — | 6 |
| D0-C2-ss | 6^1 | 1^1 | — | — | — | 1 | 7 |
| D1-C0 | — | — | — | 24 | — | — | 24 |
| D1-C1-as | 2 | — | — | 17 | — | 3 | 22 |
| D1-C1-ss | 2 | 2 | — | 24 | — | 3 | 31 |
| D1-C2-as | 6 | — | 2 | 12 | — | 9 | 29 |
| D1-C2-ss | 6 | 2 | 1 | 17 | — | 5 | 31 |
| D2-C0 | — | — | — | 46 | 1 | — | 47 |
| D2-C1-as | 2 | — | 2 | 37 | — | 7 | 48 |
| D2-C1-ss | 2 | 1 | 3 | 38 | — | 4 | 47 |
| D2-C2-as | 3 | — | 6 | 27 | — | 21 | 57 |
| D2-C2-ss | 3 | 3 | 8 | 25 | 1 | 24 | 63 |
| **Total** | **46** | **10** | **22** | **267** | **2** | **77** | **420** |

^1 out93 counted in both A and B (dual mutation)

Note: some scenarios appear in multiple groups (dual mutations); total unique failing scenarios = 420.

---

### Totals by Root Cause

| Group | Scenarios | % of Failures |
|---|---|---|
| A — Invalid Operation | 46 | 11.0% |
| B — Seq-No Replay | 10 | 2.4% |
| C — View-Change Fault | 22 | 5.2% |
| D — Partition Timeout | 267 | 63.6% |
| E — Split Brain | 2 | 0.5% |
| F — Non-PP Mutation | 77 | 18.3% |
| **Total** | **420** | |

---

### Totals by Scope

| Scope | D0-Cx | D1-Cx | D2-Cx | Total |
|---|---|---|---|---|
| Network only (D1-C0, D2-C0) | — | 24 | 47 | 71 |
| Any-scope (as) | 10 | 51 | 105 | 166 |
| Small-scope (ss) | 11 | 62 | 110 | 183 |
| **Total** | **21** | **137** | **262** | **420** |

---

## Any-Scope vs Small-Scope Differences

| Aspect | Small-Scope (ss) | Any-Scope (as) |
|---|---|---|
| Operation mutation magnitude | ±1 (e.g., `2 → 1`) | Arbitrary (e.g., `1 → -694650256`) |
| Seq-number mutation magnitude | +1 (e.g., `0 → 1`) | Arbitrary (e.g., `0 → 644426466`) |
| View-number corruption | ±1 | Arbitrary (e.g., `0 → 2056981445`) |
| Group A scenarios | 23 | 23 |
| Group B scenarios | 9 | 1 (only in dual-mutation out93) |
| Group C scenarios | 12 | 10 |
| Group D scenarios | 104 | 93 + 24 (D1-C0) + 46 (D2-C0) |
| Group E scenarios | 1 | 0 (+1 in D2-C0) |
| Group F scenarios | 37 | 40 |
| Seq-No Replay behavior | +1 offset reaches adjacent slot → Agreement | Large offset → unreachable slot → Termination |
| Group A detection | Subtle value changes harder to spot | Wildly different values obvious |
| Group C severity | ±1 corruption may partially succeed | Wild corruption often rejected outright |
| Total failures | 183 (ss only) | 166 (as only) + 71 (network only) |

**Key observations:**
1. **Group A is scope-invariant.** The same scenarios fail with operation mutations in both as and ss, confirming the empty digest vulnerability is the root cause regardless of mutation magnitude.
2. **Group B is strongly scope-dependent.** Small-scope seq mutations (±1) create subtle binding conflicts that lead to Agreement violations. Any-scope seq mutations jump to unreachable slots, causing Termination instead.
3. **Group F is a newly identified category** not present in the pre-instrumentation analysis, where these scenarios were incorrectly lumped into Group D (Partition Timeout). The distinction is significant: Group F requires Byzantine message corruption to cause liveness failure, while Group D requires only network partitions.
4. **Group F is roughly balanced** between scopes (37 ss vs 40 as), confirming that the commit/prepare disruption pattern is scope-independent — both subtle (±1) and extreme mutations can stall the commit phase equally.
5. **Small-scope produces slightly more failures overall** (183 vs 166), primarily because the ±1 mutations can create subtle protocol state confusion that any-scope's extreme values do not.

---

## Enabling Condition

All Groups A and B are enabled by the **empty digest field** (`"digest":""`) in every PBFT message. In a correct implementation the digest cryptographically binds the PRE-PREPARE to the exact request content and sequence number, so any mutation would be detected during the PREPARE phase. With an empty digest, replicas cannot distinguish a legitimate PRE-PREPARE from a mutated one, allowing the Byzantine leader to commit arbitrary content (Group A) or create sequence-number confusion (Group B).

Group C is enabled by the same flaw in the view-change path: prepared-proofs embedded in VIEW-CHANGE messages are not verified against a content hash, so corrupted proofs are accepted.

Group F is partially enabled by the empty digest: COMMIT messages carry `"digest":""` which means replicas cannot verify that the COMMIT corresponds to a legitimate Prepare certificate. A corrupted COMMIT view-number or seq-number disrupts the commit counting logic.

Groups D and E are purely network-level faults and do not depend on the digest vulnerability.
