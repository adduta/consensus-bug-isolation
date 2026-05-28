# RedisRaft protocol — vocabulary and architecture

This is the entry-point reference for understanding how RedisRaft is wired
into the bug-isolation pipeline. Read this before reading
`src/protocols/redisraft.py`. For the *why* and the design history, see
`changes.md` next to this file.

---

## 1. The system in one paragraph

RedisRaft is a Redis module implementing the Raft consensus protocol over a
small cluster of Redis processes. Each fuzzing iteration runs **3 Redis nodes**
that elect a leader, replicate a log of client operations, and respond to
crashes / restarts injected by the fuzzer. The fuzzer
(`ModelFuzz`, Gulcan et al., OOPSLA 2025) drives ~125 scheduling decisions per
iteration over a fixed horizon and records both the wire trace and a TLA+
abstract state trace.

Key Raft concepts used downstream:

- **term** — monotonically increasing election epoch per node.
- **state** — `follower` / `candidate` / `leader` per node.
- **log** — per-node ordered list of replicated entries.
- **commitIndex** — highest index known to be replicated to a quorum.
- **AppendEntries (MsgApp)** — leader → follower log replication / heartbeat.
- **RequestVote (MsgVote)** — candidate → peers during leader election.
- **Responses** — `MsgAppResp`, `MsgVoteResp`, each carrying a `reject` bit.

---

## 2. One iteration = one "run"

In this codebase, **one ModelFuzz iteration is one `run`** for the
`ConsensusProtocol` contract (`src/protocols/base.py`). This is different
from XRPL (one dir per run) and PBFT (one .txt per run), but the contract
fits cleanly because each iteration is a self-contained mini-trial: fresh
cluster, fresh state, deterministic schedule, pass/fail outcome.

### Storage layout (after `scripts/extract_redisraft.py`)

```
data/redisraft/
  run_0/
    iter_00000/
      status.json    # the label + fuzzer choices
      trace.json     # event_trace + state_trace
      log           # combined Redis stdout/stderr (binary)
    iter_00001/
      ...
    iter_24999/
  run_1/...
  run_2/...
```

`run_path` passed into `parse_log` etc. is an `iter_<NNN>` directory.

The original archives stay in `redisraft/run_N.tar.gz` (this directory) — the
extractor only writes into `data/redisraft/`. `messages.json` is *not*
extracted in v1; the wire-message view is redundant with `event_trace` for
predicate mining.

---

## 3. The label

```json
// status.json
{"iter": 49, "benchmark": "tlc", "success": false, "redis_bug": true,
 "error": "failed to terminate: redis bug encountered",
 "choices": [...]}
```

`is_successful(run)` returns

```
redis_bug == False  AND  term_oracle(run) == ∅
```

`redis_bug` is the fuzzer's crash oracle (substring `"redis bug report"` in
Redis stderr — verified in `changes.md` §3). The term oracle (§7 below) is
ours; it catches silent term-update bugs the crash oracle is blind to.

The 125-entry `choices` array carries the schedule the fuzzer played:

| `Type`          | per-iter | meaning |
|---|---:|---|
| `Node`          | 100 | deliver up to `MaxMessages` from queue `From→To` at `Step` |
| `Crash`         |  10 | kill node `Node` at `Step` |
| `Start`         |  10 | (re)start node `Node` at `Step` |
| `ClientRequest` |   5 | submit `read` / `write` op at `Step` |

Used only by the term oracle's crash-restart guard (§7.2).

---

## 4. The event vocabulary

The mineable signal lives in `trace.json → event_trace.Events`, an ordered
(but untimestamped) list. Each entry is `{Name, Params, Reset}`. The
parser in `redisraft.py` translates each event into one of these
message classes:

| Class               | From event                             | Identifying fields                                  | `peers`        |
|---|---|---|---|
| `AppendEntries`     | `SendMessage`/`DeliverMessage` `MsgApp`     | from, to, term, index, log_term, commit, entries_count | `{from, to}`  |
| `AppendEntriesResp` | `MsgAppResp`                                 | from, to, term, index, reject                       | `{from, to}`  |
| `RequestVote`       | `MsgVote`                                    | from, to, term, index, log_term                     | `{from, to}`  |
| `RequestVoteResp`   | `MsgVoteResp`                                | from, to, term, reject                              | `{from, to}`  |
| `BecomeLeader`      | `BecomeLeader`                               | node, term                                          | `{node}`      |
| `Timeout`           | `Timeout`                                    | node                                                | `{node}`      |
| `ClientRequest`     | `ClientRequest`                              | leader, request                                     | `{leader}`    |
| `MembershipChange`  | `MembershipChange`                           | action ("Add" / "Remove"), node                     | `{node}`      |

Two events for the same logical message (a `SendMessage` and the matching
`DeliverMessage`) compare equal by design — `cache.py`'s dedup loop merges
their `peers` so a delivered MsgApp ends up with `peers = {from, to}`.

Lower-level `Add` / `Remove` events (sub-records of `MembershipChange`) and
the iteration-boundary `{Reset: true}` event are ignored.

Wire-level signal in `messages.json` (raw Raft wire with `time_ms`) is not
ingested in v1; `event_trace` is strictly richer for predicate mining and
matches the level the paper mines at.

The TLA+ `state_trace` (per-step abstract state with `currentTerm`, `state`,
`log`, `commitIndex` per node) is consumed only by the term oracle — not by
the message-pair predicate grammar.

---

## 5. Field types and predicate operators

`get_fields()` registers each (class, field, type_category) triple.
`cache.py:OPERATORS_BY_TYPE` maps each category to its comparison operator
list. The RedisRaft adapter reuses existing categories where possible and
adds one new one (`'reject'`).

| Field semantic     | Category used     | Operators                | Notes |
|---|---|---|---|
| term, log_term     | `view_current`    | eq, ne, lt, gt           | reused from PBFT |
| index, commit, entries_count | `seqno`  | eq, ne, lt, gt           | reused |
| node, leader       | `rid`             | eq, ne                   | reused |
| op (`read`/`write`), action (`Add`/`Remove`), request | `op` | eq, ne | reused |
| reject (bool)      | `reject`          | eq, ne                   | **new** — added in `cache.py:OPERATORS_BY_TYPE` |
| peers              | `set[int]`        | eq, ne, isdisjoint, issubset, issuperset | reused |

---

## 6. Bug taxonomy (paper bug IDs verbatim)

`get_bug_types()` returns the paper's bug IDs with `Bug 7` dropped (Table 7
shows ModelFuzz never finds it) and `Unknown` as a fallback.

```python
['Bug 1', 'Bug 2', 'Bug 3', 'Bug 4', 'Bug 5', 'Bug 6',
 'Bug 8', 'Bug 9', 'Bug 10', 'Bug 11', 'Bug 12', 'Bug 13', 'Unknown']
```

Each label is assigned by exactly one oracle:

| Bug | Manifests as | Oracle | Detection signature |
|---|---|---|---|
| 1   | crash | crash classifier | (no public description) → currently buckets to `Unknown` |
| 2   | crash | crash classifier | (no public description) → currently buckets to `Unknown` |
| 3   | crash | crash classifier | assertion `0 < raft_get_current_idx(me)` OR top frame `raft_restore_log` |
| 4   | crash | crash classifier | top frame `ConnIsConnected` (peer connection SEGV) |
| 5   | crash | crash classifier | top frame `raft_node_set_addition_committed` OR `raft_handle_apply_cfg_change` |
| 6   | crash | crash classifier | top frame `handleBeforeSleep` OR `redis_test_map_exists_index` |
| 8   | crash | crash classifier | top frame `raft_get_entry_from_idx` |
| 9   | crash | crash classifier | top frame `raft_become_precandidate` (state→follower on leader msg, tentative) |
| 10  | crash | crash classifier | not reliably distinguishable from Bug 9 in v1 → folded into Bug 9 |
| 11  | silent | **term oracle** | `DeliverMessage` `MsgApp` with `term > currentTerm[to]` and no term advance in following state |
| 12  | silent | **term oracle** | same with `MsgVote` |
| 13  | silent | **term oracle** | same with `MsgVoteResp` |

The two oracles are non-overlapping by construction: 11–13 require Redis to
*not* crash, so they never coexist with a crash label.

---

## 7. The two oracles

### 7.1 Crash classifier (`classify_run` when `redis_bug == True`)

`log` is read as bytes (memory dumps in Redis crash reports break UTF-8).
Detection is regex-based:

1. Search for `Assertion \`X' failed`. If matched, look at `X`:
   - `0 < raft_get_current_idx(me)` → `Bug 3`.
2. Otherwise, scan the **first** `redisraft.so(SYM+0x…)` frame in the
   first `Backtrace:` block and map `SYM` to a bug ID per the table above.
3. Unmapped → `Unknown`.

### 7.2 Term-update oracle (silent bugs 11–13)

Runs only when `redis_bug == False`. Walks `state_trace.Repr` to extract
the per-node `currentTerm` array via a TLA+ Repr parser (mirroring
`redisraft-fuzzing/guider.go:parseTLCStateTrace`).

**v1 detection rule (conservative).** For each `DeliverMessage` event with
`type ∈ {MsgApp, MsgVote, MsgVoteResp}`, recipient `n = Params.to`, term
`T = Params.term`:

- If `T > currentTerm[n]` in the **final** `state_trace` snapshot of the
  iteration → flag (`Bug 11` / `Bug 12` / `Bug 13` by message type).

**Crash-restart guard.** A node that crashes and restarts may legitimately
show `currentTerm = 0` again afterward. The v1 rule sidesteps this by
**only running on iterations with zero `Crash` choices**. Iterations with
crashes are excluded from the term oracle and labelled only by the crash
classifier.

The "final-state" formulation is intentionally coarse. It is correct
(no false positives modulo the crash guard) but conservative — it may miss
windowed term-update misses where a node legitimately advances its term
later in the trace via another message. A future v2 can refine by aligning
events to inter-state windows; see `changes.md` §8.2.

### 7.3 Composition in `classify_run`

```
labels = set()
if redis_bug:
    labels.add(<crash_classifier(log)>)        # one of Bug 1..10 or Unknown
else:
    labels |= term_oracle(trace, choices)       # subset of {Bug 11, Bug 12, Bug 13}
return labels                                   # ∅ means "passing"
```

`is_successful(run)` returns `True` iff `classify_run(run) == ∅`.

---

## 8. What is *not* in v1

- **`state_trace` predicates** — would let predicates assert on
  `currentTerm`, `state`, `commitIndex`, `log_length` per node directly.
  Doesn't fit the pair-grammar; needs a separate predicate family.
- **Run-level features** — `crash_count`, `restart_count` from `choices`,
  `time_ms` from `messages.json`. Don't fit the message grammar either.
- **`messages.json` ingestion** — redundant with `event_trace` for v1.
- **PRED-baseline pipeline** — ModelFuzz traces carry no `PRED ...`
  annotations. `parse_baseline_observations` returns `None`.
- **Windowed term-oracle alignment** — see §7.2.

---

## 9. Files

| Path | Role |
|---|---|
| `src/protocols/redisraft.py`        | adapter (message classes + `RedisRaftProtocol`) |
| `scripts/extract_redisraft.py`      | tar → `data/redisraft/run_N/iter_<NNN>/` |
| `src/analysis/cache.py`             | adds `'reject'` to `OPERATORS_BY_TYPE` (single-line edit) |
| `redisraft/run_{0,1,2}.tar.gz`      | input dataset (not extracted into git) |
| `redisraft/changes.md`              | design history and open decisions |
| `redisraft/protocol.md`             | **this file** — vocabulary & architecture reference |
