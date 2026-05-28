# Review findings — RedisRaft extension

## Verified
- Required smoke labels reproduce on the extracted 1000-iter slice. Command:
  `.venv/bin/python -c "from src.protocols.redisraft import RedisRaftProtocol; p = RedisRaftProtocol(); print(p.get_num_nodes(), len(p.get_fields()), p.get_bug_types()); print(p.classify_run('data/redisraft/run_0/iter_00000')); print(p.classify_run('data/redisraft/run_0/iter_00049'))"` printed `3 36 ...`, `set()`, and `{'Bug 3'}`.
- Re-extraction worked. Command: `.venv/bin/python -m scripts.extract_redisraft redisraft/run_0.tar.gz --limit 1000` printed `extracted 1000 iterations, 3000 files written into data/redisraft`.
- The 1000-iter classifier distribution matches the handover expectation for the slice. Command:
  `.venv/bin/python - <<'PY' ... Counter(p.classify_run(path)) ... PY` produced `{'Bug 3': 18, 'Bug 5': 1, 'Bug 8': 3, 'PASS': 978}`.
- `build_predicates(RedisRaftProtocol())` produces 357312 predicates. Command:
  `.venv/bin/python - <<'PY' ... build_predicates(RedisRaftProtocol()) ... PY` printed `357312`.
- All 1000 extracted iterations contain at least one `Crash` choice. Command:
  `.venv/bin/python - <<'PY' ... count Crash choices ... PY` printed `total 1000 with_crash_choice 1000 zero_crash 0`.
- The end-to-end 100-run pipeline reaches Phase 3 and removes exactly the two expected failing reports. Command: `.venv/bin/python -m scripts.main --protocol redisraft --limit 100` printed `Phase 3: Isolating failure-causing predicates...`, `2 failed reports`, and `removed 2 data/redisraft/run_0/iter_00051, data/redisraft/run_0/iter_00049`.
- `data/redisraft/` is covered by `.gitignore` via the broad `data/` rule (`.gitignore:5`).
- The active venv is not reproducible from a manifest. Command: `.venv/bin/python -m pip list --format=freeze` showed only `pytest`, `rich`, `tqdm`, and their small dependency closure; there is no `pyproject.toml` or `requirements.txt`.
- `ruff` and `pyright` are not installed. Commands `.venv/bin/python -m ruff check src/protocols/redisraft.py` and `.venv/bin/python -m pyright src/protocols/redisraft.py` both failed with `No module named ...`.

## Holds with caveats
- `redis_bug` is a crash-report substring oracle in the public fuzzer source: public `cluster.go` raises `ErrRedisBug` when stdout/stderr contain `redis bug report`. However, the `status.json` writer is not in the public source, so the stronger claim that `status.json.redis_bug` cannot be set by any other patched-writer path is not independently verified here.
- Bugs 11-13 are not labelable by `redis_bug` alone: this follows from the paper’s Table 6 wording for silent term-update misses and from the public crash-report oracle, but the current adapter does not successfully recover those labels on this dataset.
- Bug 9 and Bug 10 should not be treated as one clean bucket. Table 6 distinguishes “message from the leader” from “message of a higher term”; issue #650 has an accept-leader/AppendEntries path, while issue #651 has `raft_set_current_term` in the stack. Folding both to `'Bug 9'` in `src/protocols/redisraft.py:354` can bias per-bug evaluation.
- The RedisRaft baseline no-op is defensible but too quiet. Command `.venv/bin/python scripts/baseline.py --protocol redisraft; printf 'exit=%s\n' $?` printed the skip message and `exit=0`; that is honest for “no PRED annotations”, but easy to miss in automation.

## Wrong or misleading
- The previous top-predicate claim did not reproduce. The handoff says the 100-run top predicate was `AppendEntries -> RequestVote where term eq term, index eq index` with score `0.374`; my run produced `0.6486486486486486 "Predicate(at least 1 AppendEntries -> AppendEntriesResp where term ne term, index ne index, log_term eq term)" > 2`. The removal set was the same two failures, so the pipeline is functioning but the reported top predicate is not stable/reproduced.
- `protocol.md` overstates the term oracle. `src/protocols/redisraft.py:302` skips any iteration with a `Crash` choice, and all 1000 extracted iterations have `Crash`; therefore `_term_oracle` fired zero times on this slice. The statement in `redisraft/protocol.md:80` that it “catches silent term-update bugs” reads like a working detector, not an inert placeholder.
- The final-state term rule is not shown correct. Forcing `_term_oracle(..., choices=[])` on the 1000 extracted iterations labels every iteration as Bug 11 and many as Bug 12/13: `{'Bug 12': 754, 'Bug 11': 1000, 'Bug 13': 218}`. That does not prove false positives in a true no-crash trace, because no no-crash trace exists in this slice, but it does refute confidence in the final-state formulation as documented in `redisraft/protocol.md:214`.
- `changes.md` and code have drifted. `changes.md:328` documents a windowed consecutive-state oracle, but the implementation uses final-state comparison plus a whole-iteration Crash guard (`src/protocols/redisraft.py:292`). `changes.md:269` also still contains stale method sketches using pre-extraction paths and `is_successful == not redis_bug`.
- The CLI limit behavior is misleading. `scripts/main.py:198` applies `--limit` only to the mined reports, but `scripts/analyze.py:132` prints stats over all extracted runs. After a 100-run Phase 3, the console immediately printed `- found 1000 runs`.
- PBFT was not successfully spot-checked. Command `.venv/bin/python scripts/analyze.py --protocol pbft` failed with `FileNotFoundError: [Errno 2] No such file or directory: 'out'`. That is an environment/data-path failure, not a RedisRaft regression proof, but the claim “new flag works on PBFT” is not verified here.

## Critique
- Oracle correctness is the largest research risk. The crash classifier is a heuristic over one assertion or the first `redisraft.so` frame (`src/protocols/redisraft.py:362`); on the 1000 slice it produced 0 Unknown among 22 failures, but this does not validate the full archive or bugs 1/2/9/10.
- The term oracle should be treated as disabled. Documentation should say: “v1 term oracle has zero coverage on the current ModelFuzz traces because every iteration contains Crash choices.” Do not count Bugs 11-13 as supported labels until a windowed event/state alignment rule is implemented and manually validated.
- The predicate vocabulary admits known nonsense. `MembershipChange.action` and `ClientRequest.request` both use `op` (`src/protocols/redisraft.py:450` and `:454`), generating 288 predicates such as `MembershipChange -> ClientRequest where action eq request`; in the 100-run cache these contributed 43200 rows, 3600 observed rows, and 800 true rows. Use a separate `action` category.
- `entries_count` shares `seqno` with indices and commits (`src/protocols/redisraft.py:417` and `:420`). I counted 111936 generated predicates mixing `entries_count` with `index`; these are mostly semantically meaningless. Split count-like fields from log indices.
- Predicate-space waste is material. In the 100-run cache, 67410514 of 107193600 rows were never observed (62.89%). Cache files were ~2.0-2.1 MB per node in my run, not the handoff’s ~1.2 MB, so 25000 iters × 3 nodes is roughly 150 GB per archive before aggregation pickles.
- Storage needs a different layout before scaling. Concrete proposal: store one archive-level Parquet/Arrow dataset with columns `(iter, node, predicate_id, observed, observed_true)` plus a separate predicate dictionary, partitioned by `run_N` and compressed with zstd. Also store only observed rows plus implicit false defaults for never-observed predicates. Based on the 100-run cache, this removes ~63% of rows before compression and avoids millions of tiny gzip files.
- `Timeout.__eq__` collapses repeated timeouts on one node (`src/protocols/redisraft.py:166`). That loses count/order signal for election instability; add a sequence/window identifier if timeout multiplicity is intended to matter.
- `from_` is idiomatic Python but awkward for paper-facing output. I would not rename it casually because it affects predicate strings and caches, but `src`/`dst` would be clearer if the RedisRaft cache is rebuilt anyway.
- Documentation hygiene needs another pass. `changes.md` has sections 1-11, not the requested 1-10 flow, and still mixes “open decision”, “decided”, and post-review caveat states. `protocol.md` says Bug 10 is folded into Bug 9, while `changes.md` uses “Bug 9 / 10 candidate”; align on “Bug 9 or Bug 10”.
- No adapter tests exist, and no formatter/linter/type-checker has been run. This was user-approved scope in the prior session, but it remains a verification gap.

## Recommended next steps
1. Fix the documentation first: mark the term oracle as inert on current traces, record the reproduced top predicate, and remove stale windowed-oracle claims from `changes.md` until implemented.
2. Add minimal tests for `iter_00000`, `iter_00049`, and the 1000-slice distribution (`Bug 3=18`, `Bug 5=1`, `Bug 8=3`).
3. Split RedisRaft field categories (`action`, `count`, maybe `term` vs `log_term`) and rebuild caches before drawing conclusions from ranked predicates.
4. Implement a validated windowed term oracle for Bugs 11-13, then manually inspect flagged traces before treating them as ground truth.
5. Add `requirements.txt` or `pyproject.toml` with pinned runtime/dev dependencies, including `rich`, `tqdm`, `pytest`, `ruff`, and `pyright`.
6. Re-run on a larger slice before using the isolated predicate in thesis claims; with only 2 failing reports in the 100-run subset, the score can easily be a spurious correlation.
