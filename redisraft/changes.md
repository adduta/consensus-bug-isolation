# Extending the pipeline to RedisRaft

This document captures everything established so far about adding **RedisRaft**
as the third consensus protocol supported by the bug-isolation pipeline
(alongside XRPL and PBFT). All planning for the RedisRaft extension lives in
this `redisraft/` directory.

The dataset itself also lives here as `run_{0,1,2}.tar.gz` (ModelFuzz output
archives, one per fuzzing run).

---

## 1. Context and goal

The thesis topic is **statistical bug isolation** for distributed consensus
systems: mine predicates from execution traces that correlate with failure,
rank them, validate that top-ranked predicates point at real root causes.

The existing codebase already supports two protocols:

- **XRPL** — `src/protocols/xrpl.py` (7-node Ripple consensus, validator logs).
- **PBFT** — `src/protocols/pbft.py` (4-node ByzzFuzz test logs).

Both implement the abstract contract in `src/protocols/base.py`
(`ConsensusProtocol`). The shared infrastructure lives in
`src/analysis/{cache,fault_localization}.py` and `src/models/`.

The plan is to add a third adapter, `src/protocols/redisraft.py`, that ingests
ModelFuzz output and feeds the same predicate-mining / CBI pipeline.

The dataset comes from **ModelFuzz** (Gulcan et al., OOPSLA 2025,
`3763060.pdf`), a model-guided fuzzer for distributed systems that tests
RedisRaft. Each fuzzer iteration runs a fresh 3-node RedisRaft cluster, makes
~125 scheduling decisions, and labels the iteration as passing or as having
triggered a Redis bug.

---

## 2. The dataset

### 2.1 Archive layout

Three completed `run_N.tar.gz` archives, ~187 MB each, ~25 000 iterations per
archive. Unpacks to:

```
run_N/
  0/                       # worker id (1 worker per archive)
    tlc_<i>.status.json    # per-iter label + fuzzer choices
    tlc_<i>.messages.json  # raw Raft wire messages
    tlc_<i>.log            # combined Redis stdout/stderr for all 3 nodes
  tlc_traces/
    tlc_<i>.json           # event_trace + TLA+ state_trace
  _run.log                 # fuzzer-side console log
  0_data.json              # coverage time series
  0.png                    # coverage plot
  DONE                     # presence => run finished cleanly
```

Per archive: ~100 003 files. Join key between trace and per-iter artifacts is
the integer `<i>` (dense 0..24 998).

### 2.2 Label distribution (verified on run_0)

| `(success, redis_bug)` | count | meaning |
|---|---:|---|
| `(True,  False)` | 24 277 | clean pass |
| `(False, True)`  |   721  | **the failures we mine** |
| `(False, False)` |     2  | environment error: TCP connect refused while bringing up the cluster |

≈ **2.9 % bug rate** — matches the handover's ~3 % estimate.

**Use `redis_bug` as the label, not `success`.** `success=false ∧ redis_bug=false`
is infrastructure noise, not a bug.

### 2.3 File schemas

**`0/tlc_<i>.status.json`** — the label:
```json
{"iter": 49, "benchmark": "tlc", "success": false, "redis_bug": true,
 "error": "failed to terminate: redis bug encountered",
 "choices": [...]}
```
`choices` is a fixed 125-entry list of fuzzer scheduling decisions:

| Type | count/iter | semantics | key fields |
|---|---:|---|---|
| `Node`          | 100 | deliver up to `MaxMessages` from queue `From→To` at `Step` | From, To, MaxMessages |
| `Crash`         |  10 | kill node `Node` at `Step` | Node, Step |
| `Start`         |  10 | (re)start node `Node` at `Step` | Node, Step |
| `ClientRequest` |   5 | submit `read`/`write` op at `Step` | Op, Step |

**`tlc_traces/tlc_<i>.json`** — the rich signal:
- `event_trace.Events` — ordered, not timestamped. Each event:
  `{Name, Params, Reset}`.
- `state_trace` — TLA+ snapshots `{Repr: "stringified record", Key: int64}`.
  Much sparser than events (iter 0: 178 events vs 17 states).
- `trace.Choices` — duplicate of `status.json.choices`.

Observed event names: `MembershipChange`, `Timeout`, `BecomeLeader`,
`ClientRequest`, `SendMessage`, `DeliverMessage`, `Add`, `Remove`, plus a
single `Reset: true` empty event marking iteration boundary in truncated
(failing) iters.

`SendMessage`/`DeliverMessage` params carry the full Raft message:
`{from, to, term, type, index, log_term, commit, entries, reject}` with
`type ∈ {MsgApp, MsgAppResp, MsgVote, MsgVoteResp}`.

TLA+ `state_trace.Repr` is a stringified record containing
`matchIndex, log, state, commitIndex, currentTerm, votesResponded,
nextIndex, votesGranted, votedFor` — per-node arrays.

**`0/tlc_<i>.messages.json`** — raw wire messages, redundant with
`event_trace` but the only source of `time_ms` (since-iteration-start).

**`0/tlc_<i>.log`** — three node logs concatenated, separated by
`logs for node: <N>`. Crash dumps in Stderr include `=== REDIS BUG REPORT
START …`. Encoding is dirty (memory dumps break UTF-8) — read as bytes.

---

## 3. The `redis_bug` oracle — verified from source

Read from `https://github.com/zeu5/redisraft-fuzzing` (default branch
`master`).

`cluster.go:19` defines:
```go
ErrRedisBug = errors.New("failed to terminate: redis bug encountered")
```

`cluster.go:160–166` is the **only** raise-site:
```go
func (r *RedisNode) Terminate() error {
    r.Stop(); r.Cleanup()
    stdout := strings.ToLower(r.stdout.String())
    stderr := strings.ToLower(r.stderr.String())
    if strings.Contains(stdout, "redis bug report") ||
       strings.Contains(stderr, "redis bug report") {
        return ErrRedisBug
    }
    return nil
}
```

So the oracle is purely substring search for `"redis bug report"` (the header
Redis emits on assertion/SIGSEGV/SIGABRT) in the captured process output.
**`redis_bug: true` ≡ Redis emitted its crash report.**

Cross-checks on our data:
- iter 49 contains `=== REDIS BUG REPORT START …` twice in `tlc_49.log` →
  `redis_bug: true`. ✓
- The 2 `(success=false, redis_bug=false)` iters have errors like
  `"failed to initialize: dial tcp …: connection refused"` — raised *before*
  `Terminate()` runs, so they bypass the bug-report check. ✓

The GitHub repo does not contain the `status.json` writer (the handover noted
the container binary is patched on the Windows host with a newer source). That
patched writer must source `redis_bug` from the same `ErrRedisBug`. The
substring oracle is the only ground truth available.

---

## 4. Paper cross-check (Tables 6 and 7)

Table 6 describes the **11 new bugs** (3–13). Bugs 1 and 2 are previously
known and not described.

| ID | Description (Table 6) | First-occurrence (Table 7, ModelFuzz) |
|---|---|---|
| 1  | (previously known)                                                                     | 0.14 h  (21/21) |
| 2  | (previously known)                                                                     | 4.13 h  (21/21) |
| 3  | Crash restoring the log from a snapshot stored on disk                                 | 0.02 h  (21/21) |
| 4  | Crash polling peer connections (SEGV reading peer conn info)                           | 3.63 h  (12/21) |
| 5  | Crash setting "added" flag after a new node is added                                   | 1.75 h  (21/21) |
| 6  | Crash checking active client connections                                               | 9.80 h  ( 1/21) |
| 7  | Crash updating log after AppendEntries (deleting existing entries)                     | **—** (never found by ModelFuzz) |
| 8  | Crash sending AppendEntries while reading from a corrupt log                           | 1.14 h  (21/21) |
| 9  | Crash updating state to follower on leader message                                     | 4.71 h  ( 5/21) |
| 10 | Crash updating state to follower on higher-term message                                | 3.89 h  ( 1/21) |
| **11** | **Fails to update current term on AppendEntries with higher term**                | 11.41 h ( 1/21) |
| **12** | **Fails to update current term on RequestVote with higher term**                  | 3.93 h  ( 1/21) |
| **13** | **Fails to update current term on RequestVoteResponse with higher term**          | 0.51 h  ( 1/21) |

### 4.1 Critical implication: bugs 11–13 are silent

Bugs 11–13 are correctness violations, not crashes. Redis keeps running, no
assertion fires, no `"redis bug report"` header is printed → `ErrRedisBug` is
never raised → **`redis_bug: false`**.

These bugs sit unlabeled inside the `(success=true, redis_bug=false)` pile of
24 277 "passing" iters in run_0. The paper's authors detect them via the TLA+
side (state-trace divergence — a `currentTerm` that should have advanced but
didn't); the `status.json` flag is blind to them.

---

## 5. Failure clustering on run_0

Stack-frame + assertion-text clustering of all 721 failing iters in run_0:

| Cluster | Count | Likely paper bug |
|---|---:|---|
| Assertion `0 < raft_get_current_idx(me)` @ `raft_server.c:1702` via `callRaftPeriodic` | 590 | **Bug 3** — snapshot restore. `callRaftPeriodic` touches the log after a snapshot reset `current_idx` to 0. |
| Top frame `raft_restore_log` (no assertion) | 26 | **Bug 3** variant. |
| SIGSEGV @ `raft_node_set_addition_committed` / `raft_handle_apply_cfg_change` | ≈20 | **Bug 5** — paper's "crashes when setting a flag indicating the node has been successfully added" matches the symbol exactly. |
| Top frame `raft_get_entry_from_idx` (mostly no-assert SIGABRT) | 73 | **Bug 8** — send-AppendEntries reads log via this fn. |
| Top frame `ConnIsConnected` | 3 | **Bug 4** — peer connection segfault. |
| Top frame `handleBeforeSleep` / `redis_test_map_exists_index` | 4 | **Bug 6** candidate. |
| Top frame `raft_become_precandidate` | 1 | **Bug 9 / 10** candidate. |
| Top frame `FileGets` / `FileRead` / `FileWrite` | 6 | Likely **Bug 3** (file I/O during restore). |
| Assertion `node` (truncated by regex) at `raft_get_entry_from_idx` | 5 | Sub-case of **Bug 8**. |
| No-assert SIGABRT, no `redisraft.so` frame matched | ≈70 | Long tail — probably mostly **Bug 3** that abort()'d via libc. |

Not identified with confidence in run_0: bugs 1, 2, 9, 10. Bugs 11–13 are
not labelable from `redis_bug` at all (see §4.1).

---

## 6. Mapping the dataset onto the existing framework

### 6.1 Granularity decision

**1 ModelFuzz iteration = 1 "run" in the pipeline.** Each iteration is a
self-contained mini-trial with a fresh cluster — exactly what `parse_log`,
`is_successful`, and `classify_run` expect to operate on. run_0 alone yields
~25 000 runs with ~720 failures, which is plenty to prototype on without
waiting for the remaining 7 archives mentioned in the handover.

### 6.2 No baseline pipeline for RedisRaft

PBFT and XRPL traces carry `PRED ...` instrumentation lines that drive the
baseline approach (`parse_baseline_observations`). **ModelFuzz traces do
not.** `RedisRaftProtocol.parse_baseline_observations` will return `None`.

### 6.3 Per-node inboxes

The `0/tlc_<i>.log` is single-file but multi-node (concatenated). Following
PBFT's pattern, build per-node inboxes from `event_trace.Events` using
`Params.from` / `Params.to` / `Params.node`. `filter_messages(messages,
node_id)` returns messages where `node_id ∈ peers`.

### 6.4 Message vocabulary (mined from `event_trace`, not `messages.json`)

`event_trace` is the level the paper mines at and includes the high-level
events (`BecomeLeader`, `Timeout`, `ClientRequest`, `MembershipChange`) that
the raw wire log doesn't carry.

| Class | Sourced from event | Fields |
|---|---|---|
| `AppendEntries`     | `SendMessage/DeliverMessage` type=MsgApp     | from, to, term, index, log_term, commit, entries_count, peers |
| `AppendEntriesResp` | type=MsgAppResp                              | from, to, term, index, reject, peers |
| `RequestVote`       | type=MsgVote                                 | from, to, term, index, log_term, peers |
| `RequestVoteResp`   | type=MsgVoteResp                             | from, to, term, reject, peers |
| `BecomeLeader`      | `BecomeLeader`                               | node, term, peers |
| `Timeout`           | `Timeout`                                    | node, peers |
| `ClientRequest`     | `ClientRequest`                              | leader, request, peers |
| `MembershipChange`  | `MembershipChange`                           | action ("Add"/"Remove"), node, peers |

`peers` is `{from, to}` for messages, `{node}` / `{leader}` for the rest.

Deferred to v2:
- **`state_trace` predicates** — `currentTerm`, `state`, `commitIndex`, `log`.
  These are per-node arrays at coarse snapshots; they don't fit the existing
  pair-predicate grammar. A separate predicate family.
- **Run-level scheduling features** — crash count, restart count, etc., from
  `choices`. Don't fit the message grammar.

### 6.5 `RedisRaftProtocol` method sketch

| Method | Behavior |
|---|---|
| `get_num_nodes()`              | `3` |
| `parse_log(run_path)`          | Read `tlc_traces/tlc_<i>.json`, walk `event_trace.Events`, emit message objects. |
| `filter_messages(msgs, n)`     | Return messages where `n ∈ m.peers`. |
| `is_successful(run_path)`      | Read `0/tlc_<i>.status.json`; return `not redis_bug`. |
| `classify_run(run_path)`       | Read `0/tlc_<i>.log` as bytes, regex assertion + top `redisraft.so(SYM+0x…)` frame, bucket to a paper bug ID. |
| `get_bug_types()`              | Paper bug IDs (final list pending §7). |
| `wrap_observations(p, nodes)`  | `{f'"{p}" > {i}': len(nodes) > i for i in range(3)}` — PBFT-style threshold sweep over 3 nodes. |
| `parse_baseline_observations`  | Return `None`. |
| `filter_aggregation(agg)`      | Identity for v1; revisit if e.g. `term` dominates the ranking. |
| `get_data_dir()`               | `'data/redisraft'`. |
| `get_run_paths()` / `iter_run_configs()` | One config group per archive (`run_0`, `run_1`, `run_2`); runs are extracted iter directories. |
| `get_log_path()` / `get_cache_path()`    | Flat under each iter directory. |

### 6.6 Storage layout

Pre-extract archives once into `data/redisraft/run_N/iter_<i>/...` via a
helper script under `scripts/`. ~1 GB uncompressed per archive, ~3 GB for all
three; ~225 k tiny files total. Streaming-from-tar is possible but
complicates `parse_log` (path-as-tar://); pre-extraction is simpler for v1.

---

## 7. Open design decisions

1. **`get_bug_types()` labels**
   - Option A — paper bug IDs verbatim (`'Bug 1'..'Bug 13'`, drop 7).
   - Option B — semantic labels with a docstring cross-reference.
   - Recommendation: **A** — easier cross-referencing against the paper.

2. **Bugs 1, 2** (previously known, undescribed in the paper)
   - No description → no obvious pattern-match. Either grep the RedisRaft
     issue tracker for the original reports, or bucket into `'Unknown'` and
     accept the loss.

3. **Pre-extract vs stream-from-tar.** Default to pre-extract for v1.

4. **Predicate-field types for response booleans (`reject`).** Decide after
   looking at how PBFT handles its booleans; default to including in equality
   predicates.

5. **Whether to ingest lower-level `Add` / `Remove` events** in addition to
   `MembershipChange`. Sample suggests they're redundant; default to skip,
   reconsider if the predicates need finer granularity.

---

## 8. Supplementary term-update oracle (bugs 11–13) — DECIDED

The `redis_bug` flag is blind to silent correctness violations (§4.1). We add
a **second oracle** that re-labels traces by walking `state_trace` against
`event_trace`, looking for the term-update-miss pattern described in
Table 6 rows 11–13. This is independent of `classify_run`'s crash-cluster
labels and produces non-overlapping bug IDs by construction (11–13 require
Redis to *not* crash).

### 8.1 Detection rule

For each pair of consecutive TLA+ state snapshots
`state_trace[k-1] → state_trace[k]` and each event `e` that occurred between
them (the events bracketed by the two abstract transitions that produced
those snapshots):

- `e.Name == "DeliverMessage"` AND
- `e.Params.type ∈ {MsgApp, MsgVote, MsgVoteResp}` AND
- let `T = e.Params.term`, `n = e.Params.to` AND
- `T > currentTerm[n]` in `state_trace[k-1]` AND
- `currentTerm[n]` in `state_trace[k]` is **still** `< T`

then flag the trace:

| `type`        | bug    |
|---|---|
| `MsgApp`      | Bug 11 |
| `MsgVote`     | Bug 12 |
| `MsgVoteResp` | Bug 13 |

`currentTerm` is one of the per-node arrays in `state_trace.Repr` — extracted
via the same Repr parser the fuzzer uses
(`redisraft-fuzzing/guider.go:parseTLCStateTrace`), to be mirrored in Python.

### 8.2 Edge cases and conservatism

- **State_trace is sparser than event_trace** (iter 0: 17 states vs 178
  events). Multiple events can fall between two snapshots. The bracketing
  pair check (before / after the event window) is correct as long as no
  other event in the same window legitimately advances `currentTerm[n]` to
  `≥ T`. If one does, the post-state catches up and the rule does not fire —
  no false positive. A *later* catch-up in a *subsequent* window is not a
  miss for this window.
- **Crash-and-restart races.** A node that crashes between snapshots and
  restarts with `currentTerm = 0` may look like a term-update miss after
  delivery. Mitigation: require `e` to be delivered after the most recent
  `Start` for node `n` in the same window (cross-reference `choices`).
- **Truncated trailing windows.** Failing iters end with `Reset: true` and
  an incomplete final state. Skip the final window when its trailing
  snapshot is missing. Iters already labeled `redis_bug: true` can still be
  scanned (a crash doesn't preclude a prior silent miss), but in v1 we keep
  the two label sources disjoint and skip them.
- **Conservative start.** Begin with the strict bracketing rule plus the
  crash/restart guard. Manually inspect ~10 flagged traces before trusting
  the count. If false-positive rate is high, tighten further.

### 8.3 Integration

The combined classification logic:

```
labels = set()
if redis_bug:
    labels.add(<crash-cluster from §5>)
else:
    labels |= term_oracle(event_trace, state_trace, choices)
return labels
```

`is_successful(run_path)` becomes
`redis_bug == False AND term_oracle == ∅`, not `not redis_bug`. This
re-classifies some previously-"passing" iters as buggy. We will measure the
re-classification rate on run_0 once implemented.

### 8.4 Thesis angle

This is a strict improvement over ModelFuzz's crash-only oracle: ground
truth for bugs 11–13 changes from "implicit in TLA+ divergence, not emitted"
to "explicit per-trace label, available for predicate mining and
evaluation." Worth its own paragraph in the thesis: our taxonomy materially
extends what the upstream tool publishes.

---

## 9. Implementation skeleton (subject to refinement)

Files to add:

- `src/protocols/redisraft.py` — new adapter, modelled on `pbft.py`.
- `scripts/extract_redisraft.py` — one-time unpacker:
  `redisraft/run_N.tar.gz` → `data/redisraft/run_N/`, plus a small index
  listing iters and labels.
- `src/protocols/redisraft_term_oracle.py` (or inline in `redisraft.py`) —
  the §8 oracle, plus a TLA+ `Repr` parser for `currentTerm` etc.
- `tests/test_redisraft_protocol.py` — mirror `tests/test_pbft_protocol.py`:
  load a known passing iter and a known failing iter, assert message counts
  and `classify_run` bucket.
- `tests/test_redisraft_term_oracle.py` — synthetic event/state pair
  covering a positive case, a negative case (catch-up within window), and a
  crash-restart guard case.
- Wire `redisraft` into `scripts/main.py` / `scripts/analyze.py` dispatch
  following the pattern PBFT used.

Risks / things to watch:
- ~225 k tiny cache files. May want to pack per-archive.
- The patched fuzzer source on the Windows host is the source of truth for
  the `status.json` writer; only the substring-based `ErrRedisBug` oracle is
  publicly verifiable (cross-checked in §3).
- `event_trace` is ordered but not timestamped — for cross-node
  happened-before, fall back to `messages.json.time_ms`.
- The Repr parser must handle TLA+'s comma-and-newline-comma quirks (visible
  in the iter 0 / iter 49 `Repr` samples).

---

## 10. Reference paper sections

- §4.2.1 — Testing implementations of the Raft protocol (abstract model & event mapping).
- §5.4 — RedisRaft experimental setup, coverage results.
- Table 3 (handover) / Table 6 (paper) — the new bugs (reproduced in §4 above).
- Table 7 — average first-occurrence times per guidance strategy.
- §5.5.1 — Comparison vs Mallory; trace-vs-state coverage trade-off.

Full PDF: `/Users/addacarutasu/consensus-bug-isolation/3763060.pdf`.
Handover: `/Users/addacarutasu/consensus-bug-isolation/HANDOVER.md`.

---

## 11. Caveat — Bug 9 / Bug 10 are merged by the crash classifier (2026-05-28)

Bugs 9 and 10 are semantically distinct in Table 6:

- **Bug 9** — crash transitioning to follower on receiving a message *from the
  current leader* (no term change).
- **Bug 10** — crash transitioning to follower on receiving a message with a
  *strictly higher term*.

The v1 `_classify_crash` in `src/protocols/redisraft.py` maps the single
top-of-stack `redisraft.so(SYM+0x…)` frame to a paper bug ID. Both bugs surface
through the same state-transition code path and produce
`raft_become_precandidate` as the top frame in the samples we inspected, so v1
labels both as `'Bug 9'` (the more frequent of the two per Table 7 — 5/21 vs
1/21).

**This merge is a classifier choice, not a property of the dataset.** The two
bugs are distinguishable from data we already load in `classify_run`. Options
for separating them, in increasing order of effort:

1. **Term comparison from the state trace.** Parse `currentTerm[crashing-node]`
   from the last good `state_trace.Repr` entry, then walk back through
   `event_trace.Events` to find the last `DeliverMessage` addressed to that
   node. If `params.term > currentTerm` → Bug 10; if `params.term == currentTerm`
   and `params.from` is the current leader → Bug 9. Cheapest and uses
   information `classify_run` already has in memory.
2. **Deeper stack frames.** The 2nd / 3rd `redisraft.so` frames likely differ —
   Bug 10 should arrive through the "term update + step-down" branch
   (`raft_set_current_term` in the call chain), Bug 9 through the "leader
   discovery" branch. Requires sampling more crash dumps to confirm.
3. **Upstream issue cross-reference.** The paper's fix commits for 9 and 10
   touch different functions; matching those names in the dump disambiguates.

Until one of these lands, downstream evaluation should treat the `'Bug 9'`
bucket as `'Bug 9 or Bug 10'`. The predicate miner *can* separate them on its
own (Bug 9's signature is `AE→AE where to eq to, term eq term`; Bug 10's is
`AE→AE where to eq to, term gt term`), so a finding that lumps both into
`'Bug 9'` may still be correct for one underlying bug while being wrong for
the other.

Mirrored open issues:
- `redisraft/HANDOFF.md` § "Open Issues" — "Bug 9 vs Bug 10 not
  disambiguated".
- `redisraft/REVIEW.md` §2.3 — adversarial check for the same.
