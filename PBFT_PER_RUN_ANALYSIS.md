# PBFT Per-Run Crosscheck Analysis

Detailed crosscheck of every failing run (except Partition Timeout) against the root cause analysis.
For each run: what mutation occurred, what violation resulted, and what predicate (if any) catches it.

---

## Group A — Invalid Operation (22 runs)

**Common mechanism:** Byzantine leader (R0) mutates `operation.first` by -1 in a PRE-PREPARE sent to a subset of replicas. Because `digest=""`, receivers accept the mutated content, build valid Prepare/Commit certificates for the wrong value, and commit it.

### D0-C1-ss (no partitions, 1 corruption)

| Run | Mutation | Recipients | Violations | Notes |
|---|---|---|---|---|
| out95 | `op.first` 1→0, round 1 | R1 | VALIDITY R1, AGREEMENT R3 | R1 commits AddOp(0,1)=1, others commit AddOp(1,1)=2 |
| out108 | `op.first` 2→1, round 5 | R3,R4 | VALIDITY R3, AGREEMENT R1 | R3 commits AddOp(1,2)=3, others commit AddOp(2,2)=4 |
| out121 | `op.first` 2→1, round 5 | R2,R3 | VALIDITY R3,R2; AGREEMENT R1 | R2,R3 commit AddOp(1,2)=3, R0,R1 commit AddOp(2,2)=4 |
| out143 | `op.first` 2→1, round 5 | R1,R2,R3 (all) | VALIDITY R3,R2,R1 | All backups get wrong value → "2+2=3" |

### D0-C2-ss (no partitions, 2 corruptions)

| Run | Mutation | Recipients | Violations | Notes |
|---|---|---|---|---|
| out91 | `op.first` 2→1, round 5 | R2 | VALIDITY R2, AGREEMENT R1 | Also REPLY mutation (secondary) |
| out93 | `op.first` 2→1, round 5 | R1,R3 | VALIDITY R1,R3; AGREEMENT R2 | — |
| out95 | `op.first` 2→1, round 5 | R2 | VALIDITY R2, AGREEMENT R1 | Also REPLY mutation (secondary) |
| out100 | `op.first` 2→1, round 5 | R1 | VALIDITY R1 | — |
| out126 | `op.first` 2→1, round 5 | R2 | VALIDITY R2, AGREEMENT R1 | Also REPLY mutation in round 8 |
| out148 | `op.first` 2→1, round 5 | R2 | VALIDITY R2, AGREEMENT R1 | — |

### D1-C1-ss (1 partition, 1 corruption)

| Run | Mutation | Recipients | Violations | Notes |
|---|---|---|---|---|
| out109 | `op.first` 1→0, round 1 | R2,R3 | VALIDITY R3,R2; AGREEMENT R1 | Partition in round 6 drops Prepares |
| out136 | `op.first` 2→1, round 5 | R3 | VALIDITY R3,R2,R0,R1 | Partition [[0,3],[1,2]] — mutated prepared-proof propagates via view-change; all replicas commit wrong value "2+2=3" |

### D1-C2-ss (1 partition, 2 corruptions)

| Run | Mutation | Recipients | Violations | Notes |
|---|---|---|---|---|
| out100 | `op.first` 1→0, round 1 | R1 | VALIDITY R1 | Also COMMIT mutations (secondary) |
| out109 | `op.first` 1→0, round 1 | R1,R3 | AGREEMENT R2; VALIDITY R3,R1 | Partition drops round 6 Prepares |
| out120 | `op.first` 2→1, round 5 | R1,R3 | AGREEMENT R2; VALIDITY R3,R1 | Also COMMIT mutations; partition [[0,2],[1],[3]] |
| out126 | `op.first` 1→0, round 1 | R1,R2,R3 (all) | VALIDITY R3,R2,R1 | Also COMMIT mutations (view_number=0→-1) |
| out130 | `op.first` 2→1, round 5 | R1,R2,R3 (all) | VALIDITY R2,R3,R1 | Partition [[0,3],[1],[2]]; all backups commit wrong value |
| out43 | `op.first` 2→1, round 5 | R1,R3 | VALIDITY R3,R1; AGREEMENT R2 | Also REPLY mutation |
| **out167** | **`seq_number` 0→1**, round 1 | R1,R2 | AGREEMENT R2,R3,R1 | **Misclassified**: this is a seq-number mutation, should be Group B |

### D2-C1-ss (2 partitions, 1 corruption)

| Run | Mutation | Recipients | Violations | Notes |
|---|---|---|---|---|
| out100 | `op.first` 1→0, round 1 | R3 | VALIDITY R3; AGREEMENT R2,R1 | Partitions drop round 5-6 messages |
| out181 | `op.first` 1→0, round 1 | R1 | VALIDITY R1 | Heavy partition drops |

### D2-C2-ss (2 partitions, 2 corruptions)

| Run | Mutation | Recipients | Violations | Notes |
|---|---|---|---|---|
| out143 | `op.first` 1→0, round 1 | R3 | AGREEMENT R1; VALIDITY R3; AGREEMENT R2 | Also REPLY mutation |
| out181 | `op.first` 1→0, round 1 | R3 | AGREEMENT R2; VALIDITY R3; AGREEMENT R1 | Also REPLY mutation; extensive drops |

### Predicate coverage for Group A

The `operation_first` and `operation_second` fields are only present on PrePrepare messages. Prepare and Commit do not carry operation content. Therefore, **no pairwise predicate can directly compare the mutated operation against the correct one** — there is no second message type that carries the operation field for comparison.

ISOLATION's predicate #5 (`>=1 Commit → PrePrepare where seq_no ne`) appears to have 100% precision for Invalid Operation, but this is misleading. Its `s_true = 818` (fires on 818/819 correct runs) — it is **near-vacuously true** since any run with multiple requests will have Commits and PrePrepares at different sequence numbers. It achieves 100% precision only because predicates #1–#4 have already removed all other failing runs in earlier recursion rounds. Its importance score (4.3e-5) is essentially zero. This predicate does not detect Invalid Operation; it is a leftover catch-all.

A predicate that *would* detect Invalid Operation would need to compare the committed operation value against the proposed one — e.g., whether the Commit's operation matches the PrePrepare's operation at the same seqNo. However, COMMIT messages in the ByzzFuzz PBFT implementation do not carry `operation` fields (only `view_no`, `seq_no`, `replica_id`), making this comparison impossible within the grammar.

Another theoretical approach would be `PrePrepare → PrePrepare where operation_first ne, seq_no eq` (two PrePrepares at the same seq with different operations), which is exactly what the mutation creates. But this requires the observer to see *both* the original and mutated PrePrepare, which only happens if the log records both versions — and in practice the log only records what each recipient actually received.

### Misclassification finding

**D1-C2-ss/out167** has a `seq-number` 0→1 mutation, not an `operation.first` mutation. It should be classified as Group B (Seq-No Replay), not Group A. This is a ground-truth error in the root cause analysis.

---

## Group B — Seq-No Replay (5 runs)

**Common mechanism:** Byzantine leader mutates `seq-number` by +1 in a PRE-PREPARE. Affected replicas store the request at the wrong sequence slot. When the legitimate request for that slot arrives, they have conflicting content, causing AGREEMENT violations.

### Per-run analysis

#### D1-C1-ss/out143
- **Mutation:** PP seq 0→1, sent to R1 only
- **Violation:** AGREEMENT at R1 (viewNo=0, seqNo=1) — R1 committed AddOp{1,1} at seq=1 while others committed AddOp{2,2}
- **Causal chain:** R1 stores first request (1+1) at seq=1 due to mutation. When legitimate PP(seq=1, op=2+2) arrives, R1 already has conflicting content. R1 commits 1+1 at slot 1; others commit 2+2.

#### D1-C2-ss/out7
- **Mutation:** PP seq 1→2, sent to ALL backups (R1,R2,R3)
- **Violation:** AGREEMENT at R1,R2,R3 across views 1 and 2 (seqNo=2)
- **Causal chain:** All backups process second request as seq=2 (skipping seq=1). During view-change, conflicting prepared-proofs for seq=2 propagate. New leader re-proposes conflicting values. Violations cascade through views 1→2.
- **Notable:** Most severe seq-replay — affects all backups simultaneously, causing multi-view cascading failures.

#### D2-C2-ss/out40
- **Mutation:** PP seq 0→1, sent to R2 only (R1,R3 dropped by partition)
- **Violation:** AGREEMENT at R1,R2,R3 (viewNo=0, seqNo=1)
- **Causal chain:** R2 is the only replica that receives any PP for the first request, and it's the mutated seq=1 version. R2 sends PREPARE(s=1) while no other replica has seen this request. When legitimate PP(seq=1, op=2+2) arrives, R2 already has conflicting content at slot 1.

#### D2-C2-ss/out100
- **Mutation:** PP seq 0→1 to R1,R3; also COMMIT view 0→-1 to R1,R2 (secondary)
- **Violation:** AGREEMENT at R1 (viewNo=0, seqNo=1) — R1 committed 1+1, others committed 2+2
- **Causal chain:** Same as out143. Secondary COMMIT mutation disrupts R1/R2's commit phase but doesn't change the root cause.

#### D2-C2-ss/out16
- **Mutation:** PP seq 0→1 to R1; also COMMIT view 0→-1 to R1,R2 (secondary)
- **Violation:** AGREEMENT at R1 (viewNo=0, seqNo=1) — R1 committed 1+1, others committed 2+2
- **Causal chain:** Identical to out143/out100. Secondary COMMIT mutation is non-causal.

### Predicate coverage for Group B

The seq-replay bug is fundamentally **invisible** to the current grammar when evaluated on (view_no, seq_no) equality alone. The mutation creates a Prepare whose (view_no, seq_no) *matches* a legitimate PrePrepare at the same slot — either the mutated PP itself, or the genuine later PP. The predicate `Prepare → PrePrepare where view_no eq, seq_no eq` sees superficial agreement on those fields and does not flag the run.

To detect seq-replay, a predicate would need to:
1. Compare **operation** or **timestamp** fields across Prepare and PrePrepare (but Prepare doesn't carry operation/timestamp), OR
2. Check **message ordering** (Prepare arriving before the legitimate PP), which is outside the grammar's capabilities, OR
3. Detect the **gap in sequence numbers** (no activity at the skipped slot), which requires counting/existence predicates the grammar doesn't support.

The same near-vacuous predicate #5 (`Commit → PrePrepare where seq_no ne`) ends up assigned to some Seq-No Replay runs, but only because all other failing runs have already been eliminated in earlier recursion rounds — it does not detect the seq-replay bug.

### Interaction with D1-C2-ss/out167 (misclassified)

If out167 were reclassified from Group A to Group B, the Seq-No Replay group would have 6 runs, not 5. The detection mechanism is the same.

---

## Group C — View-Change Fault (10 runs)

**Common mechanism:** Byzantine replica sends a malformed VIEW-CHANGE or NEW-VIEW message with corrupted prepared-proofs, view-number, or last-seq-number. The new primary cannot assemble a consistent NEW-VIEW, causing protocol stall (termination) or wrong value installation (agreement).

### Per-run analysis

#### D1-C2-ss/out49 — TERMINATION
- **Mutation:** VC prepared-proofs injection: `[]` → `[{seq:1, PP+2×Prepare}]` (fabricated prepared-proof inserted into 12 VIEW-CHANGE messages from R0 to R1,R2,R3)
- **Top-level fields unchanged:** `new_view_no=1, last_seq_no=0, replica_id=0` — identical in original and mutated versions
- **Violation:** None explicit; system times out at 10000ms
- **Top-level visible?** **NO** — mutation is entirely within nested `prepared-proofs` array

#### D2-C1-ss/out49 — AGREEMENT
- **Mutation:** VC `new-view-number` 1→2 (single receiver: R2); also PREPARE `view-number` 1→2
- **Violation:** AGREEMENT at R3,R1 — R3 committed AddOp{1,1} at seqNo=0 in view 2, while others committed AddOp{2,2} in view 1
- **Top-level visible?** YES, but indistinguishable — legitimate view-2 VCs also occur later in the run

#### D2-C1-ss/out65 — AGREEMENT
- **Mutation:** VC `last-seq-number` 0→1 (from R3 to R0, two mutations)
- **Violation:** AGREEMENT at R1,R2 (viewNo=1, seqNo=0)
- **Top-level visible?** YES, but `last_seq_no=1` is a perfectly valid value — cannot distinguish from normal state without replica commit history

#### D2-C1-ss/out24 — TERMINATION
- **Mutation:** VC prepared-proofs injection: `[]` → `[{seq:1, PP+2×Prepare}]` (9 mutations from R0 to R1,R2,R3)
- **Top-level fields unchanged:** `new_view_no=1, last_seq_no=0, replica_id=0`
- **Violation:** None; timeout
- **Top-level visible?** **NO** — same injected-prepared-proof pattern as D1-C2-ss/out49

#### D2-C1-ss/out175 — TERMINATION
- **Mutation:** NV sub-structural mutation (R1→R2, 2 mutations). Sent and Mutated JSON appear byte-identical; mutation affects encoding-level or internal field not visible in JSON
- **Also:** COMMIT mutation (view-number:0, seq-number:1)
- **Violation:** None; timeout
- **Top-level visible?** **NO** — completely invisible at JSON/field level

#### D2-C2-ss/out87 — TERMINATION
- **Mutation:** NV sub-structural mutation (R1→R2, 2 mutations). JSON content identical between Sent and Mutated. Also COMMIT mutation (identical content)
- **Violation:** None; timeout
- **Top-level visible?** **NO** — sub-structural mutation invisible

#### D2-C2-ss/out151 — TERMINATION
- **Mutation:** VC `new-view-number` 1→2 (R1→R0,R3; 6 mutations total)
- **Violation:** None; timeout
- **Top-level visible?** YES, but indistinguishable from cascading view-changes

#### D2-C2-ss/out73 — TERMINATION
- **Mutation:** VC prepared-proofs injection: `[]` → `[{seq:1, PP+2×Prepare}]` (R0→R1,R2; 6 mutations). Also PREPARE view-number mutations
- **Violation:** None; timeout
- **Top-level visible?** **NO**

#### D2-C2-ss/out175 — TERMINATION
- **Mutation:** VC prepared-proofs injection: `[]` → `[{seq:1, PP+2×Prepare}]` (R1→R2,R3; 8 mutations). Also COMMIT mutations
- **Violation:** None; timeout
- **Top-level visible?** **NO**

#### D2-C2-ss/out31 — TERMINATION
- **Mutation:** VC prepared-proofs injection: `[]` → `[{seq:1, PP+2×Prepare}]` (R2→R1,R3; 8 mutations)
- **Violation:** None; timeout
- **Top-level visible?** **NO**

### Summary of mutation types

| Mutation Type | Runs | Top-Level Visible? |
|---|---|---|
| VC prepared-proofs injection | 6 (out49-D1, out24, out73, out175-D2C2, out31, out49-D1C2) | **NO** |
| VC `new-view-number` mutation | 2 (out49-D2C1, out151) + 1 partial (out65) | YES, but indistinguishable |
| VC `last-seq-number` mutation | 1 (out65) | YES, but valid value |
| NV sub-structural mutation | 2 (out175-D2C1, out87) | **NO** |

### Predicate coverage for Group C

**The current grammar fundamentally cannot detect View-Change Fault.** The reasons:

1. **6 of 10 runs** have prepared-proofs injection where all top-level fields (`new_view_no`, `last_seq_no`, `replica_id`) are unchanged. The corruption lives in nested arrays that the pairwise field grammar cannot access.

2. **3 runs** have top-level field mutations (`new_view_no` or `last_seq_no`), but these values are indistinguishable from legitimate view-change behavior. A VC with `new_view_no=2` or `last_seq_no=1` is perfectly normal during cascading view changes.

3. **2 runs** have sub-structural NV mutations that produce byte-identical JSON — completely invisible at any level.

**What would be needed:** A `num_prepared_proofs` field on ViewChange (currently only on NewView) would detect the injection pattern (prepared-proofs count changing from 0 to 1). However, as demonstrated in the extended grammar experiment, even structural count fields fail to reliably separate VCF from Partition Timeout runs because the mutation affects content VALUES within proofs, not proof COUNTS in most edge cases.

---

## Group E — Split Brain (7 runs)

**Common mechanism:** Two three-way network partitions across different rounds force the protocol through multiple view-changes (viewNo ≥ 2). Different replica subsets carry inconsistent prepared-proof state from prior views. The new leader installs conflicting values for the same seqNo, producing AGREEMENT violations without any message mutation.

### Per-run analysis

#### D2-C0/out87
- **Partitions:** Round 2 `[[0,1],[3],[2]]`, Round 5 `[[0],[1,2],[3]]`
- **Mutations:** NONE (0 Mutated lines)
- **VC/NV count:** 113 VIEW-CHANGE, 29 NEW-VIEW
- **Violation:** AGREEMENT at R0 (viewNo=3, seqNo=2) — R0 committed AddOp{2,2}, others committed AddOp{1,1} at same seqNo

#### D2-C0/out197
- **Partitions:** Round 1 `[[1,3],[2],[0]]`, Round 5 `[[0],[2],[1,3]]`
- **Mutations:** NONE
- **VC/NV count:** 91 VIEW-CHANGE, 12 NEW-VIEW
- **Violation:** AGREEMENT at R1,R0 (viewNo=2, seqNo=2)

#### D2-C1-ss/out66
- **Partitions:** Round 5 `[[1,2],[0],[3]]`, Round 2 `[[0,3],[2],[1]]`
- **Mutations:** NONE (despite c=1, configured corruption produced no visible mutation)
- **VC/NV count:** 108 VIEW-CHANGE, 24 NEW-VIEW
- **Violation:** AGREEMENT at R2,R3,R0 (viewNo=3, seqNo=4)

#### D2-C2-ss/out15
- **Partitions:** Round 6 `[[1],[2],[0,3]]`, Round 1 `[[0,1,3],[2]]`
- **Mutations:** NONE (despite c=2)
- **VC/NV count:** 36 VIEW-CHANGE, 8 NEW-VIEW
- **Violation:** AGREEMENT at R1 (viewNo=1, seqNo=0)

#### D2-C2-ss/out199
- **Partitions:** Round 7 `[[0],[2],[1,3]]`, Round 2 `[[1],[0,3],[2]]`
- **Mutations:** NONE
- **VC/NV count:** 96 VIEW-CHANGE, 21 NEW-VIEW
- **Violation:** AGREEMENT at R3,R0 (viewNo=2, seqNo=2)

#### D2-C2-ss/out66
- **Partitions:** Round 5 `[[1,2],[0],[3]]`, Round 2 `[[0,3],[2],[1]]`
- **Mutations:** NONE (identical config to D2-C1-ss/out66)
- **VC/NV count:** 114 VIEW-CHANGE, 27 NEW-VIEW
- **Violation:** AGREEMENT at R2,R3,R0 (viewNo=3, seqNo=2)

#### D2-C2-ss/out176
- **Partitions:** Round 3 `[[0],[1],[2,3]]`, Round 5 `[[0],[3],[1,2]]`
- **Mutations:** NONE
- **VC/NV count:** 134 VIEW-CHANGE, 38 NEW-VIEW
- **Violation:** AGREEMENT at R1,R0 (viewNo=3, seqNo=0)

### Key characteristics of all Split Brain runs

1. **Zero mutations** in every run, despite D2-C1/C2 configs having process faults configured. Configured corruptions either targeted nonexistent receivers or rounds where the byzantine replica sent no messages.

2. **All violations at viewNo ≥ 2.** The split brain only manifests after multiple view-change rounds allow inconsistent state to accumulate.

3. **Very high VC/NV counts** (91–134 VCs, 12–38 NVs) — far more than Group D runs (typically 12–24 VCs).

4. **Two three-way partitions** in every run. Each splits 4 replicas into 3 groups where no group has quorum (2f+1=3).

### Predicate coverage for Group E

**No pairwise predicate on top-level fields can reliably distinguish Split Brain.**

The distinguishing feature is that the same seqNo gets committed with different operation values by different replicas — but the ISOLATION grammar does not expose `operation` fields on COMMIT messages (only `view_no`, `seq_no`, `replica_id`). A predicate like `2×Commit→Commit where view_no ne, seq_no eq` (same slot committed at different views) would partially correlate, since Split Brain runs always show multi-view commits at the same seqNo. However, this pattern also occurs in Group C and normal view-change recovery.

Split Brain is an **emergent property of message sequencing** — which replicas saw which messages in which order — not a property of any individual message or pair of messages.

---

## Commit Corruption (2 runs)

### D0-C2-as/out191
- **Mutation:** COMMIT from R0→R2: `view-number` 0→**-1949330706** (wildly corrupted, as-scope)
- **Also:** Omitted PRE-PREPAREs for seqNo=0 (round 1 corruption prevents delivery)
- **Partitions:** NONE (D0)
- **VC/NV count:** 108 VIEW-CHANGE, 27 NEW-VIEW
- **Violation:** None — both requests eventually complete through view-changes, but system reaches 10000ms timeout during view-change loops caused by the corrupted COMMIT
- **Root cause:** R2 receives COMMIT with view=-1949330706, cannot match it to any view. R2 loses a quorum vote, must wait for view-change recovery. System cycles through views 0→1→2→3 before delivering.

### D0-C2-ss/out191
- **Mutation:** COMMIT from R0→R2: small-scope mutation (visible `view-number` stays 0; possibly digest or other non-top-level field changed)
- **Also:** Omitted PRE-PREPAREs for seqNo=0 (same as as-variant)
- **Partitions:** NONE (D0)
- **VC/NV count:** 96 VIEW-CHANGE, 21 NEW-VIEW
- **Violation:** None — requests complete through view-changes, timeout reached
- **Root cause:** Omitted PPs in round 1 prevent seq=0 progress in view 0. Small-scope COMMIT mutation adds disruption. System cycles through views before delivering.

### Why separate from Partition Timeout

1. **No network partition exists** (D0 config). The timeout is caused by a corrupted COMMIT, not by message non-delivery.
2. **The root cause is a process fault** (message mutation), not a network fault.
3. Current `classify_run` correctly labels these as "Commit Corruption" since the D0-C2 edge case was explicitly added.

### Predicate coverage for Commit Corruption

In the as-variant, the `view-number=-1949330706` would be detectable by a predicate comparing Commit `view_no` values (e.g., `Commit→Commit where view_no ne`). However, this predicate would fire on any multi-view run. The ss-variant shows no top-level field change, making it invisible.

With only 2 runs, Commit Corruption is too rare for ISOLATION to discover a statistically significant predicate.

---

## Overall Summary

| Bug Group | Runs | Directly Detectable? | How Caught | Fundamental Limitation |
|---|---|---|---|---|
| **Invalid Operation** | 22 (21 + 1 misclassified) | No | Indirectly via `Commit→PP seq_no ne` (survivorship bias) | `operation` field only exists on PrePrepare; no other message type carries it for comparison |
| **Seq-No Replay** | 5 (+ 1 from Group A) | No | Indirectly via same predicate | Mutated seq_no creates a Prepare that matches a legitimate PP at the same slot |
| **View-Change Fault** | 10 | No | Not caught at all | 6/10 mutations in nested prepared-proofs; 3/10 top-level mutations indistinguishable from normal VC; 2/10 sub-structural |
| **Split Brain** | 7 | No | Not caught at all | Emergent from message sequencing, no individual message anomaly; `operation` not on Commit |
| **Commit Corruption** | 2 | Partially (as-scope) | Not caught (too rare) | Only 2 runs; ss-variant invisible |

### Key insights

1. **The grammar's blind spots are structural, not incidental.** The pairwise field comparison grammar cannot detect bugs that manifest as (a) content mismatches in fields that only one message type carries, (b) corruption inside nested message structures, or (c) emergent ordering-dependent phenomena.

2. **Groups A and B are NOT meaningfully caught** by the grammar. Predicate #5 (`Commit → PrePrepare where seq_no ne`) fires on 818/819 correct runs — it is near-vacuously true and only appears as a 100%-precision Invalid Operation predictor because all other failing runs have been removed by earlier recursion rounds. The grammar lacks the structural capability to detect these bugs: Commit messages do not carry operation fields, so the mutated-vs-correct operation comparison is impossible.

3. **Groups C, E, and Commit Corruption are invisible** to the current grammar. View-Change Fault requires inspecting nested prepared-proof content. Split Brain requires cross-replica state comparison. Commit Corruption is too rare for statistical significance.

4. **One misclassification found:** D1-C2-ss/out167 is listed as Group A (Invalid Operation) but has a `seq-number` 0→1 mutation, making it Group B (Seq-No Replay).
