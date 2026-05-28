# Handoff — RedisRaft extension

## Current Goal

Add **RedisRaft** as the third consensus protocol supported by the
statistical bug-isolation pipeline (alongside XRPL and PBFT), using the
ModelFuzz dataset (Gulcan et al., OOPSLA 2025, `3763060.pdf`) as the
labelled trace source.

Design history, paper cross-check, and bug-taxonomy decisions are in
`redisraft/changes.md`. The vocabulary and architecture reference is in
`redisraft/protocol.md`. Read both before reading code.

## Current State

End-to-end pipeline runs on a 100-iter slice of `redisraft/run_0.tar.gz`
and produces a non-trivial isolated predicate. Verified items:

- Extraction (`scripts/extract_redisraft.py`) writes
  `data/redisraft/run_<N>/iter_<NNN>/{status.json, trace.json, log}` one
  directory per ModelFuzz iteration. `messages.json` is intentionally not
  extracted; rationale in `protocol.md` §4 and a discussion in chat is
  preserved as: redundant for the v1 predicate grammar; needed only if
  latency / drop-detection predicates are later added.
- `src/protocols/redisraft.py` implements the full `ConsensusProtocol`
  contract: 8 message classes (`AppendEntries`, `AppendEntriesResp`,
  `RequestVote`, `RequestVoteResp`, `BecomeLeader`, `Timeout`,
  `ClientRequest`, `MembershipChange`), `_parse_events`, a regex-based
  TLA+ `Repr` parser for `currentTerm`, a stack-frame-based
  `_classify_crash`, and `_term_oracle` (silent bugs 11–13 with the v1
  conservative rule).
- `src/protocols/__init__.py` adds `make_protocol(name)` and
  `PROTOCOL_CHOICES = ('xrpl', 'pbft', 'redisraft')`.
- `src/analysis/cache.py` adds RedisRaft-specific operator categories:
  `'reject'`, `'term'`, `'log_term'`, `'log_index'`, `'count'`, and
  `'action'`. This prevents predicates that directly compare unrelated
  fields such as `MembershipChange.action == ClientRequest.request`,
  `AppendEntries.entries_count < AppendEntries.index`, or `term == log_term`.
- `scripts/main.py`, `scripts/analyze.py`, `scripts/baseline.py` all
  accept `--protocol {xrpl,pbft,redisraft}`. `scripts/main.py` also
  accepts `--limit N` to cap discovered runs. `baseline.py` short-circuits
  for redisraft because the dataset has no `PRED` annotations.
- Current field-split cache version is `nodeids1-fieldsplit`. The
  field-split vocabulary reduces RedisRaft predicates from 357,312 to
  130,848. A 100-iter slice run produced top isolated predicate score
  0.305, `AppendEntries -> AppendEntriesResp where term gt term` > 2
  nodes, on 2 failing reports (both Bug 3 / snapshot-restore crash).
- Bug-distribution check on the 1000-iter slice matches full-archive
  ratios (Bug 3 ≈ 82 %, Bug 5 ≈ 5 %, Bug 8 ≈ 14 % of failing iters).

Not verified / not done:

- Full 1000-iter slice has not been run through `main.py --protocol
  redisraft` after the `nodeids1-fieldsplit` vocabulary change. Only the
  first 100 iterations have rebuilt field-split predicate caches.
- No tests written; per user instruction in this session.
- No formatting / linting / type-checking executed against the new code.
- The term oracle has **never fired** on the slice (every iter contains
  at least one `Crash` choice and the v1 crash-restart guard skips those
  iters). v1 is intentionally conservative; see `changes.md` §8.2 for the
  windowed-alignment v2 plan.

## Important Files

- `redisraft/changes.md` — design history, paper cross-check (Tables 6
  and 7), bug-oracle source verification, open decisions.
- `redisraft/protocol.md` — vocabulary, storage layout, bug taxonomy.
  Entry point for anyone new.
- `redisraft/run_{0,1,2}.tar.gz` — input dataset; immutable.
- `src/protocols/redisraft.py` — adapter.
- `src/protocols/__init__.py` — `make_protocol` registry.
- `src/protocols/base.py` — the contract every adapter implements.
- `src/protocols/pbft.py` — closest sibling adapter; reference for
  per-node-inbox style.
- `src/protocols/xrpl.py` — second sibling; reference for
  directory-per-run style.
- `src/analysis/cache.py` — `OPERATORS_BY_TYPE` (the one-line edit lives
  here) and the message-pair predicate engine.
- `src/analysis/fault_localization.py` — `isolate()` and `Aggregation`.
- `scripts/extract_redisraft.py` — tar → `data/redisraft/run_N/iter_<NNN>/`.
- `scripts/main.py` — message-based pipeline entry point.
- `scripts/analyze.py` — confusion-matrix entry point.
- `scripts/baseline.py` — PRED-based baseline; no-op for redisraft.
- `HANDOVER.md` (repo root) — the original Windows-side handover; data
  provenance and lower-level dataset notes.

## Commands That Worked

```bash
# Extract first 1000 iterations of run_0 into data/redisraft/.
.venv/bin/python -m scripts.extract_redisraft redisraft/run_0.tar.gz --limit 1000

# Print the per-bug confusion matrix.
.venv/bin/python scripts/analyze.py --protocol redisraft

# Full pipeline (cache + aggregate + isolate + analyze) on 100 iters.
.venv/bin/python -m scripts.main --protocol redisraft --limit 100

# Confirm the current field-split predicate space.
.venv/bin/python - <<'PY'
from src.analysis.cache import build_predicates
from src.protocols.redisraft import RedisRaftProtocol
p = RedisRaftProtocol()
preds, _ = build_predicates(p)
print(p.CACHE_VERSION, len(preds))
PY
```

Outputs after the runs:

- `data/redisraft/run_0/iter_*/` (1000 iter directories)
- `data/redisraft/run_0/iter_00000` through `iter_00099` have
  `predicates-cache-nodeids1-fieldsplit-{0,1,2}.txt.gz` (300 cache files,
  ~456-464 KB each in checked examples).
- `cache/aggregation_cache_redisraft_nodeids1-fieldsplit.pickle` (~55 MB)
- `cache/reports_cache_redisraft_nodeids1-fieldsplit.pickle` (~8 KB)

## Commands That Failed

```bash
# System python lacks rich/tqdm; must use .venv/bin/python instead.
python3 scripts/analyze.py --protocol redisraft
```

Failure reason: `ModuleNotFoundError: No module named 'rich'`. The
project venv at `.venv/bin/python` has `rich` and `tqdm`. There is no
`pyproject.toml` / `requirements.txt` pinning yet.

## Open Issues

- **Term oracle never fires.** v1 skips any iter with a `Crash` choice
  in the schedule. Every ModelFuzz iter has 10 `Crash` choices, so
  effectively no iter is eligible. Either accept that the oracle is
  inert in the current dataset, or implement the windowed-alignment
  rule sketched in `changes.md` §8.2.
- **Bug 9 vs Bug 10 not disambiguated.** Both fold into `'Bug 9'` based
  on the `raft_become_precandidate` frame heuristic. Bug 10 may be
  silently mis-labeled.
- **Bug 1 and Bug 2 always classify as `'Unknown'`.** The paper does
  not describe them; their issue-tracker descriptions were never pulled
  in. Anything currently in `Unknown` may include them.
- **Disk usage still scales aggressively.** The field-split vocabulary cuts
  checked cache files to ~0.46 MB per node, but 25,000 iters × 3 nodes is
  still roughly 35 GB per archive before aggregation outputs. Full-archive
  runs need cache packing or per-archive pickling before they are
  sustainable.
- **Heuristic crash classifier.** Single top-of-stack frame match. Two
  observed buckets in `redisraft/changes.md` §5 ("no-assert SIGABRT
  without redisraft.so frame", ~70 iters in run_0) fall through to
  `'Unknown'`.
- **TLA+ `Repr` parser is regex-based.** Brittle to TLA+ formatter
  changes upstream. Currently only extracts `currentTerm`; will need
  more fields if state-trace predicates are added.
- **`Timeout.__eq__` collapses repeated timeouts** on the same node into
  one logical message. May lose signal for predicates that count
  timeouts.
- **Predicate vocabulary was narrowed in `nodeids1-fieldsplit`.**
  `MembershipChange.action`, `entries_count`, `term`, and `log_term` no
  longer directly compare against unrelated fields. Old `nodeids0` cache
  files may still exist on disk but should not be used for new analysis.
- **`from_` field name** in `AppendEntries` / `RequestVote` etc. uses
  the trailing-underscore convention because `from` is reserved. Will
  surprise readers who expect Raft-paper-style naming.

## Next Steps

1. Run the full pipeline on the extracted 1000-iter slice
   (`--protocol redisraft` without `--limit`), in the background, using
   the `nodeids1-fieldsplit` cache version. Compare top-predicate scores
   against the 100-iter score 0.305 to check whether it stays stable.
2. Decide whether the term oracle should be upgraded to the windowed
   formulation (`changes.md` §8.2). If yes, prototype the
   event-to-state alignment heuristic on a hand-picked passing iter and
   verify the parser handles all four TLA+ array fields.
3. Add a smoke test that loads one passing iter and one failing iter
   and asserts (a) message counts, (b) `classify_run` bucket, (c) at
   least one expected predicate fires in the cache. This catches the
   most likely regression: a Redis upgrade changing log text.
4. Resolve the Bug 9 / Bug 10 collision: read the relevant
   `redisraft/src/raft_server.c` paths to find a distinguishing frame,
   or accept the merge and rename the label.
5. Pin the venv dependencies (`pyproject.toml` or `requirements.txt`).

## Assumptions

- One ModelFuzz iteration = one "run" in the pipeline's sense (matches
  XRPL / PBFT's notion of "labelled trial").
- `ErrRedisBug` (and therefore `status.json.redis_bug`) is raised
  exclusively by a substring match for `"redis bug report"` in Redis
  stderr — verified against
  `https://github.com/zeu5/redisraft-fuzzing/blob/master/cluster.go:160-166`.
- The patched fuzzer binary on the Windows host preserves that oracle
  semantics when it writes `status.json` (the writer itself is not in
  the public GitHub source; we have no way to inspect it from this
  machine).
- `event_trace.Events` is sufficient signal for the v1 predicate
  grammar; `messages.json` is not extracted.
- 100-iter slice failures (2 Bug 3) are representative of run_0's full
  failure mix at the same ratios (≈ 82 % Bug 3 in run_0 overall).
- The project's venv (`.venv/bin/python`) is the canonical Python; no
  reproducible dependency file currently exists.

## Last Updated

2026-05-28, after splitting RedisRaft field categories and rebuilding the
first 100 iterations with cache version `nodeids1-fieldsplit`.
