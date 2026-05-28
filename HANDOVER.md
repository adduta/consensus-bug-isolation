# Handover: ModelFuzz → Statistical Bug Isolation for RedisRaft

## 1. Project goal

The user is writing a thesis on **statistical bug isolation** — mining
predicates from execution logs that are statistically more likely to appear in
faulty traces than in passing traces, then ranking them as candidate root
causes (cf. Liblit's CBI / Cooperative Bug Isolation, Andrzej Wasylkowski's
work on predicate mining, etc.).

The user is using **ModelFuzz** (Gulcan et al., "Model-Guided Fuzzing of
Distributed Systems", `2410.02307v3.pdf` in this directory, also at
`dl.acm.org/doi/pdf/10.1145/3763060`) to *generate* the labeled trace dataset.
ModelFuzz tests **RedisRaft** (a Raft consensus implementation that compiles
into a Redis module), produces per-iteration logs, and labels each iteration
as either passing or as having triggered a Redis crash / assertion violation
("redis_bug").

The user is **not** trying to replicate the paper's coverage claims or
re-evaluate ModelFuzz. They are using its output as raw data. The downstream
contribution is the predicate-mining method, not the fuzzer.

## 2. Experiment state (as of handover)

A long-running experiment is **currently executing in the background** via
`C:\modelfuzz_artifact\run_modelfuzz_experiment.ps1`. It runs 10 sequential
ModelFuzz-only runs (`--bench tlc`) against RedisRaft, each `-e 25000 -w 4
-n 3 -r 5`, packaging each finished run as `results\run_N.tar.gz`.

- **Container:** `mf-experiment` (Docker, `modelfuzz:latest`).
- **Per-run wall-clock:** ~6 h (4 workers × 3.4 s/iter aggregate ≈ 1.18 iter/s).
- **Total wall-clock:** ~60 h (some early sleep gaps; user fixed power plan).
- **Throughput floor:** 3.4 s/iter/worker is a hard floor — the fuzzer has
  `time.Sleep(30ms)` × `Horizon=100` baked in. CPU is ~25-35% utilised on a
  6-core / 12-thread / 16 GB laptop. Closing apps does not speed it up.
- **Estimated total scenarios:** ~250,000 traces across 10 runs.
- **Observed failure rate:** **~3%** of traces have `redis_bug: true` (higher
  than the 1.5% the 200-iter calibration suggested). Expect ~7,500 failing
  traces in total.

Check progress with:

```powershell
docker exec mf-experiment bash -c 'for d in /Fuzzing/host_results/run_*/; do iters=$(ls "$d"/0/*.messages.json 2>/dev/null | wc -l); echo "$(basename $d): $iters iter"; done'
Get-ChildItem 'C:\modelfuzz_artifact\results'
```

**Do not stop the container or restart Docker** while the experiment is still
running — the script *is* resumable (it skips runs that already have a
`run_N.tar.gz`), but mid-run progress is lost on interruption.

## 3. Where the data lives

```
C:\modelfuzz_artifact\
  results\
    run_0.tar.gz          # completed run (immutable)
    run_1.tar.gz          # ...
    run_<live>\           # in-progress run — do not read until DONE marker appears
  run_modelfuzz_experiment.ps1   # the runner; resumable
  redisraft-fuzzing\             # host source for the fuzzer (patched, newer than container's pre-built binary)
  paper.txt                      # text dump of the paper
  HANDOVER.md                    # this file
```

Each `run_N.tar.gz` unpacks to:

```
run_N\
  0\                            # the "run 0" subdir of that fuzzing campaign (not to be confused with the outer run number)
    tlc_<i>.log                 # Redis cluster stdout/stderr for iteration <i>, all 3 nodes
    tlc_<i>.messages.json       # all intercepted Raft messages exchanged this iter
    tlc_<i>.status.json         # OUTCOME LABEL + trace choices for iter <i>
  tlc_traces\
    tlc_<i>.json                # event_trace + TLC abstract state_trace + raw trace
  _run.log                      # fuzzer console output for the whole run
  0_data.json                   # coverage time series
  0.png                         # coverage plot
  DONE                          # presence = run finished cleanly
```

Per iteration, ~138 KB raw / ~13 KB after the per-run gzip. A finished archive
is ~180 MB (25,000 iters).

## 4. File schemas (the bits the bug-analysis agent will read)

### `0/tlc_<i>.status.json` — the LABEL file

```json
{
  "iter": 12345,
  "benchmark": "tlc",
  "success": true,                // true == iteration completed without error
  "redis_bug": false,             // true == ErrRedisBug was raised (assertion / crash / segfault)
  "error": "...",                 // present only when success=false
  "choices": [                    // the fuzzer's scheduling decisions this iter
    { "Type": "Node",  "Step": 0,  "From": 2, "To": 3, "MaxMessages": 1 },
    { "Type": "Crash", "Step": 17, "Node": 2 },
    { "Type": "Start", "Step": 42, "Node": 2 },
    { "Type": "ClientRequest", "Step": 5, "Op": "write" },
    ...
  ]
}
```

**Use `redis_bug == true` as the failure label**, not `success == false`. The
latter also includes non-bug environment errors (e.g. cluster failed to start
for unrelated reasons). The fuzzer's source is at
`redisraft-fuzzing/sync.go` — `ErrRedisBug` is raised specifically for the
faults the paper cares about.

### `tlc_traces/tlc_<i>.json` — the RICH SIGNAL file

```json
{
  "trace": { "Choices": [ ... same as in status.json ... ] },
  "event_trace": {
    "Events": [
      { "Name": "MembershipChange", "Params": { "action": "Add", "node": 1 }, "Reset": false },
      { "Name": "BecomeLeader",     "Params": { ... } },
      { "Name": "ClientRequest",    "Params": { ... } },
      ...
    ]
  },
  "state_trace": [                  // TLA+ abstract state snapshots
    { "Repr": "/\\ currentTerm = [1 -> 0, ...] /\\ state = [1 -> Follower, ...] ...", "Key": 12345 },
    ...
  ]
}
```

**This is the file to mine predicates from.** The `event_trace.Events` list is
a sequence of high-level protocol events (membership changes, term changes,
leader elections, client requests, AppendEntries, RequestVote, etc.). The
`state_trace` is the corresponding TLA+ abstract state at each step. Each
state has a 64-bit `Key` for fast equality checks.

### `0/tlc_<i>.messages.json` — raw Raft messages (redundant signal)

Lower-level than `event_trace`: every intercepted Raft message with
`direction`, `time_ms`, `from`, `to`, `type` (`append_entries_request`,
`append_entries_response`, `request_vote_request`, etc.), `id`, and `data`
(parsed JSON). Use only if predicate mining over `event_trace` proves too
coarse.

### `0/tlc_<i>.log` — Redis stdout/stderr per node

Verbose, mostly useful for confirming *which* known bug a failing trace
tripped (assertion messages, stack traces). Lower priority than the
structured files; can be dropped to save disk if predicate mining doesn't
need it.

## 5. The 12 bugs known in RedisRaft (paper Table 3)

Listed for cross-referencing against the assertion text that appears in
`tlc_<i>.log` of failing traces. Bug 1, 2 are previously-known (from the
RedisRaft issue tracker); 3-13 are new and reported as RedisLabs/redisraft
issues #643-#649. Most occur on the path of process crash + restart with
specific orderings.

| ID | Description | Avg first-occurrence in 21 ModelFuzz runs (paper Table 7a) |
|----|-------------|----------------------------------------------------------|
| 1  | (previously known) | 0.14 h, 21/21 runs |
| 2  | (previously known) | 4.13 h, 21/21 |
| 3  | Process crashes when restoring the log from a snapshot stored on disk | 0.02 h, 21/21 |
| 4  | Segfault polling peer connections (reading peer info) | 3.63 h, 12/21 |
| 5  | Crash setting "added" flag after a new node is added | 1.75 h, 21/21 |
| 6  | Redis server crashes checking active client connections | 9.80 h, 1/21 |
| 7  | Crash updating log after AppendEntries (deleting existing entries) | — (not found by ModelFuzz) |
| 8  | Crash sending AppendEntries while reading from a corrupt log | 1.14 h, 21/21 |
| 9  | Crash updating state to follower on leader message | 4.71 h, 5/21 |
| 10 | Crash updating state to follower on higher-term message | 3.89 h, 1/21 |
| 11 | Fails to update current term on AppendEntries with higher term | 11.41 h, 1/21 |
| 12 | Fails to update current term on RequestVote with higher term | 3.93 h, 1/21 |
| 13 | Fails to update current term on RequestVoteResponse with higher term | 0.51 h, 1/21 |

In this experiment configuration (6 h/run × 10 runs) we expect runs to catch
bugs 1, 2, 3, 5, 8 reliably; bug 4 most of the time; bug 9 sometimes; the
others sporadically. Bugs 6, 7, 11 are unlikely to appear.

The bug-isolation agent should cluster failing traces (e.g. by assertion
message in `tlc_<i>.log` or by the protocol event preceding the crash) to
estimate how many distinct bug *populations* the dataset contains before
running predicate mining.

## 6. Suggested next steps for the bug-analysis agent

1. **Wait for the experiment to finish, OR start prototyping on the archives
   that are already present.** As of this handover, runs 0-2 (and possibly
   more) are already done. Each archive is self-contained and immutable; you
   can begin the pipeline immediately on partial data.

2. **Build an ingestion script** that walks a `run_N.tar.gz`, parses each
   pair `(tlc_traces/tlc_<i>.json, 0/tlc_<i>.status.json)`, and yields tuples
   of `(event_trace, state_trace, choices, redis_bug_label)`. Store in a
   columnar format (e.g. Parquet) for cheap querying.

3. **Cluster the failing traces** before mining predicates. Possible keys:
   - Final assertion message (extract via regex from `tlc_<i>.log`)
   - Last 3-5 events in `event_trace` before failure
   - Crash-injection pattern (which Node, which Step, from `choices`)

   Without clustering, predicates will be dominated by whichever bug fires
   most often (likely bug 3 or 5, ~21/21 in the paper).

4. **Pick a predicate language.** Reasonable candidates for Raft-shaped data:
   - Per-event boolean predicates: `event.Name == "BecomeLeader"`,
     `event.Params.node == X`
   - Sequence patterns: bigrams / trigrams of event names
   - State predicates: `currentTerm > 5`, `|state == Leader| == 0` (no
     leader), `commitIndex < lastApplied + 5`
   - Trace-level features: # of crashes, # of leader changes, max term

5. **Score predicates** by standard CBI metrics (Increase, Importance) or
   simpler χ² / mutual information against the `redis_bug` label, then rank.

6. **Validate** by checking whether the top-ranked predicates point at the
   protocol conditions cited in the paper's Table 3 (e.g. "Process fails to
   update current term on RequestVote with higher term" → predicate should
   correlate with traces that receive a `request_vote_request` with `term >
   currentTerm` and a follow-up that doesn't update term).

## 7. Important gotchas

- **The container's pre-built binary is broken** for log generation: it
  doesn't write `messages.json` or `status.json` files. The host source in
  `redisraft-fuzzing/*.go` is newer and the experiment runner *patches and
  rebuilds* the binary inside the container at first launch (touches
  `/Fuzzing/.experiment_built`). If you need to rerun anything, use the
  script — don't invoke the container's `./redisraft-fuzzing` directly.

- **`success: false` ≠ bug.** Iterations that fail to start the cluster, or
  hit a timeout, will have `success: false` but `redis_bug: false`. Use
  `redis_bug` for the label.

- **`event_trace` is ordered, not timestamped.** If you need wall-clock
  timing, cross-reference `messages.json` (each entry has `time_ms` since
  iteration start).

- **TLA+ state representation is a string in `Repr`** — pre-parse to
  extract fields (`currentTerm`, `state`, `log`, etc.) using the patterns
  in `redisraft-fuzzing/guider.go:parseTLCStateTrace`. The `Key` field is
  a hash, fine for grouping but not for analysis.

- **Bugs 1 and 2 are known bugs.** If you're trying to make a contribution
  by "discovering" them via predicate mining, lead with the new ones (3-13).

- **Disk:** ~3.5 GB total for all 10 archives. Decompress only what you're
  actively analysing — un-tarring all 10 at once is ~35 GB.

- **The user is on Windows with PowerShell 5.1.** Avoid `&&` in scripts you
  hand them; use `; if ($?) { ... }` or wrap multi-step bash inside
  `docker exec`.

## 8. Reference paper sections

- §4.2.1 (Testing Implementations of the Raft Protocol) — abstract model & event mapping
- §5.4 (RedisRaft) — experimental setup, coverage results
- Table 3 — the new bugs (reproduced above)
- Table 7a — average first-occurrence times per guidance strategy
- §5.5.1 (vs Mallory) — discussion of the trace-vs-state coverage trade-off
- §6 (Limitations) — caveats about model abstraction level

Full PDF: `C:\modelfuzz_artifact\2410.02307v3.pdf`
Plain-text dump: `C:\modelfuzz_artifact\paper.txt`
