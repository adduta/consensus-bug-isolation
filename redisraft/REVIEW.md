# Review instructions — RedisRaft extension

You are a senior research engineer reviewing the RedisRaft extension that
the previous agent built. **Your job is to critique it, not to rubber-stamp
it.** Operate under the principles in `AGENTS.md` at the repository root:
correctness before speed, evidence-based reasoning, research integrity. The
previous agent's claims are unverified by you until you re-run them or
re-read the source.

If a claim turns out to be wrong or overstated, say so plainly. If a
limitation is acknowledged but glossed over, name it. Do not pad the report.

---

## 0. Required reading order

Read these files, in order, before forming any opinion:

1. `AGENTS.md` (repository root) — your operating principles.
2. `redisraft/HANDOFF.md` — the previous agent's continuity note.
3. `redisraft/protocol.md` — the canonical vocabulary / architecture.
4. `redisraft/changes.md` — the design log and open decisions.
5. `HANDOVER.md` (root) — the upstream dataset handover from the
   Windows-host owner.
6. `src/protocols/base.py` — the contract.
7. `src/protocols/redisraft.py` — the new adapter.
8. `src/protocols/__init__.py` — the registry.
9. `scripts/extract_redisraft.py` — the tar unpacker.
10. The three edited CLIs: `scripts/main.py`, `scripts/analyze.py`,
    `scripts/baseline.py`.
11. `src/analysis/cache.py` — the engine consuming the adapter (note the
    single-line change to `OPERATORS_BY_TYPE`).

Cross-check `redisraft/protocol.md` and `redisraft/changes.md` against
the actual files. If they drift, flag it.

---

## 1. Verification probes (run these)

The previous agent reported specific results. Verify them. Do not trust
the claims without re-execution.

### 1.1 Smoke probes on the extracted slice

```bash
# 1000 iterations should already be extracted; if not, re-run:
.venv/bin/python -m scripts.extract_redisraft redisraft/run_0.tar.gz --limit 1000

# Adapter sanity
.venv/bin/python -c "
from src.protocols.redisraft import RedisRaftProtocol
p = RedisRaftProtocol()
print(p.get_num_nodes(), len(p.get_fields()), p.get_bug_types())
print(p.classify_run('data/redisraft/run_0/iter_00000'))   # should be: set()
print(p.classify_run('data/redisraft/run_0/iter_00049'))   # should be: {'Bug 3'}
"

# Bug-distribution tally
.venv/bin/python scripts/analyze.py --protocol redisraft
```

Expected outcomes (from the handover):
- `iter_00000` → `set()` (passing).
- `iter_00049` → `{'Bug 3'}`.
- Bug 3 count on 1000-iter slice ≈ 18; Bug 5 ≈ 1; Bug 8 ≈ 3.

If numbers differ, the classifier has changed behavior or the slice was
re-extracted differently. Investigate before continuing.

### 1.2 End-to-end pipeline reproduction

If caches from the previous session are still on disk
(`data/redisraft/run_0/iter_*/predicates-cache-*.gz`), the run will skip
cache generation and finish in seconds. If they were cleared, expect
~6 min for the first 100 iters.

```bash
.venv/bin/python -m scripts.main --protocol redisraft --limit 100
```

Verify:

- Pipeline reaches "Phase 3: Isolating failure-causing predicates...".
- The top isolated predicate has the form
  `AppendEntries -> RequestVote where term eq term, index eq index` (or
  a variant) and a non-zero score.
- The pipeline removes exactly 2 failing reports (`iter_00049`,
  `iter_00051`) in the first isolation round.

If the predicate string differs, that is interesting on its own (could
be a non-deterministic ordering bug or a real change). Report it.

---

## 2. Adversarial checks (push on the claims)

Each item below is a place where the previous agent's reasoning *might*
be wrong, weak, or glossed-over. Investigate each. Report your verdict
(holds / partially holds / wrong) with evidence.

### 2.1 Oracle correctness

- **Claim:** `redis_bug: true` is set exactly when Redis emitted its
  crash report (substring `"redis bug report"`). Source verified at
  `zeu5/redisraft-fuzzing/cluster.go:160-166`.
  - The `status.json` writer itself is **not** in the public GitHub
    source; it is in the patched fuzzer on the Windows host. Confirm
    independently that `status.json.redis_bug` cannot be set by any
    other path. If you cannot confirm, mark the claim as unverified.
- **Claim:** bugs 11–13 (silent term-update misses) cannot be labeled
  by ModelFuzz's `redis_bug` flag.
  - Verify by sampling 5–10 `(success=True, redis_bug=False)` iters
    from the slice and checking by hand whether any look like a missed
    term update (incoming `MsgApp/MsgVote/MsgVoteResp` with
    `term > currentTerm[recipient]` and no subsequent term advance).

### 2.2 Term oracle (`_term_oracle`)

- **Issue:** The v1 rule skips any iteration containing a `Crash`
  choice. Every iter in the dataset has 10 `Crash` choices. Therefore
  the oracle has fired **zero times** on the slice. Verify this.
- **Question:** Does the documentation (`protocol.md` §7.2 and
  `changes.md` §8) make this gap obvious to a reader, or does it read
  like a working detector? Critique the wording.
- **Question:** Is the "final-state" formulation actually correct in
  the no-crash case? Construct or find one passing, no-crash iter and
  manually trace whether a term miss could exist there. If so, does the
  rule fire?

### 2.3 Crash classifier (`_classify_crash`)

- **Issue:** Maps the *first* assertion string OR the *first*
  `redisraft.so(SYM+0x…)` frame to a single paper bug ID.
- Probe: what fraction of failing iters fall through to `'Unknown'`?
  (Hand-cluster ~20 of them; the previous agent's clustering numbers
  are in `changes.md` §5 but are not re-verified.)
- Probe: Bug 9 and Bug 10 are folded into a single `'Bug 9'` bucket
  based on a single stack frame. Is that defensible? Read the paper's
  Table 6 descriptions for 9 and 10 and check whether the merge can
  bias downstream evaluation.
- Probe: Bug 1 and Bug 2 are always `'Unknown'`. Could either be
  inferred from the assertion text via the upstream issue tracker
  (`RedisLabs/redisraft#643-#649` and earlier issues for 1/2)?

### 2.4 Message vocabulary and `__eq__`

- `Timeout.__eq__` ignores any notion of "which timeout this is" —
  multiple timeouts on the same node collapse via dedup. Is signal
  lost? Consider an iteration where a follower times out 3 times
  before a `BecomeLeader`. The cache will see one logical `Timeout`,
  not three.
- `MembershipChange.action` (string `"Add"`/`"Remove"`) shares the
  `'op'` operator category with `ClientRequest.op`
  (`"read"`/`"write"`). The cache may now generate predicates of the
  form `MembershipChange.action eq ClientRequest.op` which are
  meaningless. Check whether this happens in practice. If yes, propose
  a new operator category (e.g. `'action'`) and report the size of the
  noise.
- `AppendEntries.entries_count` is bucketed as `'seqno'` (the same
  bucket as `index`, `commit`). Is that semantically fair? `seqno`
  operators are `[eq, ne, lt, gt]`, which is fine, but predicates may
  mix counts and indices in ways that are nonsensical (e.g.
  `entries_count lt index`).
- `from_` trailing-underscore field name: idiomatic but
  inconsistent with the paper's vocabulary. Decide whether you would
  push to rename (e.g. `src` / `dst`).

### 2.5 Predicate-space size

- `build_predicates(RedisRaftProtocol())` produced 357 312 predicates.
  That is comparable to XRPL but RedisRaft has 8 message types, not
  5. The growth is dominated by `set[int]` and the `view_current`
  category. Are any of these predicates trivially true / false (e.g.
  comparing the same field of the same message pair)? `cache.py` does
  not deduplicate on assertion semantics, so `term eq term` between
  `AppendEntries` and `AppendEntries` is generated *and* evaluated.
  Quantify the share of predicates that never observe anything in the
  100-iter slice (the cached file has `observed=False` flags). If most
  predicates never fire, that is wasted compute and should be flagged.

### 2.6 Storage and reproducibility

- Cache files: ~1.2 MB × 3 nodes × N iters. At N = 25 000 per archive,
  ~90 GB per archive. There are 10 archives planned upstream
  (`HANDOVER.md` mentions ~250 000 traces total). The plan as written
  does not scale; the agent acknowledged this in `HANDOFF.md` but
  did not fix it. Propose a concrete packing scheme (one tar/zstd per
  iter dir? one parquet per archive?) with a back-of-envelope size
  estimate.
- No `pyproject.toml` or `requirements.txt`. The handover names
  `.venv/bin/python` as the canonical interpreter and relies on it
  having `rich` / `tqdm`. This is not reproducible per `AGENTS.md` §2.
  Verify what is actually installed (`pip list`) and propose a pinned
  manifest.
- `data/redisraft/` is generated content; verify it is in `.gitignore`.

### 2.7 CLI wiring

- `scripts/main.py --protocol redisraft --limit 100` caps Phase 1/2
  but `scripts/analyze.py` (invoked by `stats`) walks all extracted
  iters. The console output therefore reports "found 1000 runs" right
  after Phase 3 finished on 100. This is misleading. Decide whether
  `--limit` should also pass into the analyze table or whether the
  current behaviour is intentional.
- `scripts/baseline.py --protocol redisraft` prints a message and
  exits. Is that exit code 0 honest? (RedisRaft has no PRED baseline,
  so 0 is arguably correct, but a future maintainer may invoke this
  expecting analysis.)
- The new flag works on XRPL (`--protocol xrpl`) and PBFT
  (`--protocol pbft`) without behavior change. Spot-check by running
  `scripts/analyze.py --protocol pbft` with the existing PBFT data;
  the previous agent did not.

### 2.8 Documentation hygiene

- Cross-check section numbering in `changes.md` — section ordering was
  manually rewritten when the term-oracle decision moved from "open
  decision" to "decided". Confirm headings still flow §1..§10
  contiguously.
- `protocol.md` claims "Bug 9" subsumes Bug 10 in the v1 classifier.
  `changes.md` §5 has a different framing ("Bug 9 / 10 candidate"
  for the same frame). Pick one and align.
- `protocol.md` §6 maps each bug to "exactly one oracle". `Unknown`
  is a fallback in both oracles' implementations but is listed only
  under the crash classifier. State the catch-all behaviour
  explicitly.
- Mark anything not yet executed as **not verified**, per `AGENTS.md`.

---

## 3. Out-of-scope but worth noting

- No tests exist for the new adapter (the user explicitly skipped
  them). Note this in your review as a remaining gap, not a critique
  of the agent's behavior.
- No formatter / linter / type-checker has been run. Per `AGENTS.md`
  §8, suggest `ruff check src/protocols/redisraft.py` and
  `pyright src/protocols/redisraft.py` as a minimum.
- The 0.374 isolated predicate has not been validated against the
  ground truth. With only 2 failing reports, it could be a spurious
  correlation. Recommend re-running on a larger slice before drawing
  any thesis-grade conclusions.

---

## 4. Report format

Produce a single Markdown report at `redisraft/REVIEW_FINDINGS.md`
with this structure:

```markdown
# Review findings — RedisRaft extension

## Verified
- <fact>: <evidence (file:line, command output, etc.)>

## Holds with caveats
- <claim>: <what is correct, what is glossed over>

## Wrong or misleading
- <claim>: <evidence, with the corrected statement>

## Critique
- <issue>: <why it matters>, <suggested fix>

## Recommended next steps
1. <step>
2. <step>
```

Do not pad. If an item is verified-and-fine, one line is enough. The
sections most worth your effort are **Wrong or misleading** and
**Critique** — the rest is noise.

Verification commands you ran must be quoted verbatim. Numbers you
report must come from a command you actually ran in this review session;
do not copy numbers from `HANDOFF.md` and present them as your own
verification. If a probe is impractical, say so and explain why instead
of skipping silently.
