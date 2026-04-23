# PBFT Root Cause Analysis — Any-Scope Mutations

Analysis of all failing ByzzFuzz PBFT scenarios for any-scope (as) mutation configurations.
Scope: any-scope mutations when process faults are present (D0/D1/D2-C1/C2-as); all runs for network-fault-only configs (D1-C0, D2-C0).

---

## Root Cause Groups

### Group A — Operation field mutation in PRE-PREPARE

**Mechanism:** Byzantine leader (R0) mutates the `operation` field (first or second) in the PRE-PREPARE sent to a subset of replicas. With any-scope mutations, the field value can change to an arbitrary integer (e.g., `0 -> 143065580`), unlike small-scope where the change is +/-1. Because every message carries `"digest":""`, there is no cryptographic binding between the PRE-PREPARE and the actual client request. Receivers accept the mutated content, build a valid Prepare certificate for the wrong value, and commit it — while unaffected replicas commit the correct value.

**Violations:** Validity, Agreement

| Config | Files |
|---|---|
| D0-C1-as | out95, out108, out121, out143 |
| D0-C2-as | out91, out93^ab, out95, out100, out126, out148 |
| D1-C1-as | out109, out136 |
| D1-C2-as | out43^t, out100, out109, out120^t, out126, out130 |
| D2-C1-as | out100, out181 |
| D2-C2-as | out112^a, out143, out181 |

^ab Also classified as Seq-No Replay (both operation and sequence mutations in the same run)
^t Also in termination list — partition causes timeout after violations are fired
^a Agreement violation only (no validity) — mutated view-number in PRE-PREPARE causes indirect agreement divergence

---

### Group B — Seq-number mutation in PRE-PREPARE

**Mechanism:** Byzantine leader (R0) mutates the `seq-number` field to an arbitrary value in a PRE-PREPARE sent to a subset of replicas. With any-scope mutations, the seq-number can jump to a wildly different value (e.g., `0 -> 1976177586` or `0 -> 644426466`), unlike small-scope's +/-1 increment. The affected replicas attempt to process a request at an incorrect sequence slot. Because `"digest":""` does not bind content to sequence number, the Prepare certificate for the wrong binding is accepted. When combined with network partitions, the stalled protocol triggers view-changes; replicas carrying bogus prepared-proofs from the corrupted slot disagree with those that did not.

**Violations:** Agreement (after view-change), Termination (when partition prevents recovery)

| Config | Files |
|---|---|
| D0-C2-as | out93^ab |
| D1-C1-as | out85, out143 |
| D1-C2-as | out7 |
| D2-C1-as | out64 |

^ab Also classified as Invalid Operation (multiple mutations in the same PRE-PREPARE)

**Note:** With any-scope mutations, the seq-number can jump so far that the replicas never complete the mutated slot, leading to termination rather than agreement violation (e.g., D1-C1-as/out85, out143). In small-scope the +1 offset is close enough that replicas may eventually complete the slot and only then disagree.

---

### Group C — VIEW-CHANGE / NEW-VIEW corruption

**Mechanism:** After a network partition forces a view-change, the Byzantine replica sends a malformed VIEW-CHANGE or NEW-VIEW message. With any-scope mutations, fields can be wildly corrupted (e.g., `new-view-number: -2049880611`). The new primary cannot assemble a consistent NEW-VIEW and the protocol stalls. In some cases the corrupted view-change data causes the new primary to install conflicting values, leading to Agreement violations.

**Violations:** Termination (timeout), Agreement (when corruption leads to conflicting commits)

| Config | Files |
|---|---|
| D1-C2-as | out49 (termination) |
| D2-C1-as | out125, out186 (termination) |
| D2-C2-as | out21, out48, out58^e, out79, out87, out151, out186 (termination; out58 also agreement) |

^e Also classified as Split Brain (VIEW-CHANGE corruption combined with multiple view-changes leads to agreement violation at viewNo >= 2)

---

### Group D — Network partition prevents quorum -> timeout

**Mechanism:** A partition splits the 4-replica network such that no 2f+1=3 replica subset can communicate. PREPARE/COMMIT phases stall; view-change is triggered. If the partition spans multiple rounds or the new primary's view is also disrupted, no view recovers the protocol. In D1/D2-Cx-as cases, concurrent process faults (PRE-PREPARE/PREPARE/COMMIT field mutations) are present but are on non-critical messages — the partition alone kills liveness.

**Violations:** Termination only

| Config | Count | Files |
|---|---|---|
| D1-C0 | 12 | out79, out86, out95, out115, out116, out123, out140, out145, out175, out178, out192, out195 |
| D2-C0 | 31 | out4, out11, out16, out20, out24, out27, out36, out44, out49, out51, out53, out56, out60, out66, out70, out73, out93, out96, out99, out114, out115, out132, out136, out144, out146, out151, out159, out168, out176, out178, out185 |
| D1-C1-as | 13 | out11, out27, out37, out41, out86, out90, out94, out151, out165, out170, out175, out178, out196 |
| D1-C2-as | 16 | out28, out33, out44, out53, out74, out81, out90, out116, out123, out137, out141, out145, out156, out165, out186, out196 |
| D2-C1-as | 40 | out9, out14, out18, out19, out35, out40, out41, out48, out50, out52, out58, out66, out70, out82, out90, out92, out94, out95, out108, out110, out111, out112, out113, out114, out123, out124, out129, out137, out144, out149, out153, out157, out163, out166, out174, out176, out185, out190, out191, out199 |
| D2-C2-as | 31 | out9, out17, out20, out27, out35, out36, out43, out44, out50, out52, out66, out70, out71, out77, out82, out91, out101, out104, out106, out129, out136, out137, out144, out146, out156, out157, out159, out162, out166, out174, out199 |

---

### Group E — Network partition induces split-brain across view-changes

**Mechanism:** Two or more network partitions across different rounds (D2 configurations) force the protocol through multiple view-changes (viewNo >= 2 in violations). Different replica subsets carry inconsistent prepared state from prior views into subsequent leaders. The new leader installs conflicting values for the same seqNo, producing Agreement violations without any single detectable Byzantine operation mutation.

**Violations:** Agreement only

| Config | Files |
|---|---|
| D2-C0 | out87, out197 |
| D1-C2-as | out112 |
| D2-C2-as | out58^c |

^c Also classified as View-Change Fault (corrupted VIEW-CHANGE message exacerbates split-brain at high view numbers)

---

## Edge Cases

### D2-C2-as/out15 — Agreement violation without mutations, viewNo=1

This scenario has an AGREEMENT violation at viewNo=1 caused by network partitions alone, but is classified as Partition Timeout because the Split Brain classification requires viewNo >= 2. The partition causes replicas to carry inconsistent prepared state through a single view-change, leading to agreement divergence. This is mechanistically similar to Group E but at a lower view number.

### D0-C2-as/out93 — Dual mutation (Group A + Group B)

Two PRE-PREPARE mutations in the same run: one mutates the operation field (Group A, `operation.first: 0 -> 143065580`), another mutates the sequence number (Group B, `seq-number: 0 -> 644426466`). Both exploit the empty digest vulnerability. The VALIDITY violations are triggered by the operation mutation.

### D2-C2-as/out112 — Operation mutation with Agreement only

The PRE-PREPARE has a wildly mutated `view-number` field (`2056981445`) rather than the typical operation field mutation. Combined with network partitions, this causes agreement divergence without a direct VALIDITY violation. Classified as Invalid Operation because the mutation is in a PRE-PREPARE at the expected sequence slot (`timestamp == seq-number`).

---

## Any-Scope vs Small-Scope Differences

| Aspect | Small-Scope (ss) | Any-Scope (as) |
|---|---|---|
| Operation mutation magnitude | +/-1 (e.g., `1 -> 2`) | Arbitrary (e.g., `0 -> 143065580`) |
| Seq-number mutation magnitude | +/-1 (e.g., `0 -> 1`) | Arbitrary (e.g., `0 -> 1976177586`) |
| View-number corruption | +/-1 | Arbitrary (e.g., `0 -> -2049880611`) |
| Seq-No Replay behavior | Replicas may complete the +1 slot -> Agreement violation | Replicas stall on unreachable slot -> Termination |
| Group A detection | Subtle value changes harder to spot in logs | Wildly different values are immediately obvious |
| Group C severity | Minor VC/NV corruption may be tolerated | Wild corruption ensures stall |
| Total failure count (D0-Cx) | ss: 10 | as: 10 |
| Total failure count (D1-Cx) | ss: 43 | as: 42 |
| Total failure count (D2-Cx) | ss: 95 | as: 87 |

Key observation: any-scope mutations generally produce the **same root cause groups** as small-scope, but the magnitude of corruption changes the **symptom** (termination vs agreement for Seq-No Replay) without changing the root cause mechanism.

---

## Summary by Configuration

| Config | Group A | Group B | Group C | Group D | Group E | Total failing |
|---|---|---|---|---|---|---|
| D0-C1-as | 4 | — | — | — | — | 4 |
| D0-C2-as | 6^1 | 1^1 | — | — | — | 6 |
| D1-C0 | — | — | — | 12 | — | 12 |
| D1-C1-as | 2 | 2 | — | 13 | — | 17 |
| D1-C2-as | 6 | 1 | 1 | 16 | 1 | 25 |
| D2-C0 | — | — | — | 31 | 2 | 33 |
| D2-C1-as | 2 | 1 | 2 | 40 | — | 45 |
| D2-C2-as | 3 | — | 7^2 | 31 | 1^2 | 42 |
| **Total** | **23** | **5** | **10** | **143** | **4** | **184** |

^1 out93 counted in both A and B (dual mutation)
^2 out58 counted in both C and E (VCF causes split-brain)

### Totals by Root Cause (deduplicated)

| Group | Unique Scenarios | % of Failures |
|---|---|---|
| A — Invalid Operation | 23 | 12.5% |
| B — Seq-No Replay | 5 | 2.7% |
| C — View-Change Fault | 10 | 5.4% |
| D — Partition Timeout | 143 | 77.7% |
| E — Split Brain | 4 | 2.2% |
| **Total unique scenarios** | **184** | |

(1 scenario is dual A+B, 1 scenario is dual C+E; total unique = 182)

---

## Enabling Condition

All Groups A and B are enabled by the **empty digest field** (`"digest":""`) in every PBFT message. In a correct implementation the digest cryptographically binds the PRE-PREPARE to the exact request content and sequence number, so any mutation would be detected during the PREPARE phase. With an empty digest, replicas cannot distinguish a legitimate PRE-PREPARE from a mutated one, allowing the Byzantine leader to commit arbitrary content (Group A) or create sequence-number confusion (Group B).

Group C is enabled by the same flaw in the view-change path: prepared-proofs embedded in VIEW-CHANGE messages are not verified against a content hash, so corrupted proofs are accepted.

Groups D and E are purely network-level faults and do not depend on the digest vulnerability.
