"""Unpack a ModelFuzz `run_N.tar.gz` archive into the data/redisraft layout.

Source archives live in `redisraft/run_*.tar.gz` (one per ModelFuzz fuzzing
run). Each archive contains ~25 000 iterations laid out as

    run_N/0/tlc_<i>.{status,messages,log}.json
    run_N/tlc_traces/tlc_<i>.json

The bug-isolation pipeline expects one directory per iteration, so this
script rewrites the layout into

    data/redisraft/run_N/iter_<NNN>/
        status.json   (from 0/tlc_<i>.status.json)
        trace.json    (from tlc_traces/tlc_<i>.json)
        log           (from 0/tlc_<i>.log, kept binary)

`messages.json` is skipped: its content is redundant with `event_trace` in
`trace.json` for v1 predicate mining.

Usage:
    python -m scripts.extract_redisraft redisraft/run_0.tar.gz
    python -m scripts.extract_redisraft redisraft/run_0.tar.gz --out data/redisraft
    python -m scripts.extract_redisraft redisraft/run_0.tar.gz --limit 100
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tarfile

_ITER_RE = re.compile(r'tlc_(\d+)\.(status\.json|log)$')
_TRACE_RE = re.compile(r'tlc_(\d+)\.json$')


def extract(
    archive_path: str,
    out_root: str = 'data/redisraft',
    limit: int | None = None,
) -> tuple[int, int]:
    """Extract one archive into `out_root/<run_name>/iter_<NNN>/...`.

    Returns (iters_written, files_written).
    """
    run_name = os.path.basename(archive_path)
    for suffix in ('.tar.gz', '.tgz'):
        if run_name.endswith(suffix):
            run_name = run_name[: -len(suffix)]
            break

    run_root = os.path.join(out_root, run_name)
    os.makedirs(run_root, exist_ok=True)

    files_written = 0
    iters_seen: set[int] = set()

    with tarfile.open(archive_path, 'r:gz') as tar:
        for member in tar:
            if not member.isfile():
                continue
            name = member.name

            iter_id: int | None = None
            target_name: str | None = None

            # 0/tlc_<i>.{status.json|log}
            m = _ITER_RE.search(name)
            if m and '/0/' in name:
                iter_id = int(m.group(1))
                ext = m.group(2)
                target_name = 'status.json' if ext == 'status.json' else 'log'

            # tlc_traces/tlc_<i>.json
            if target_name is None:
                m = _TRACE_RE.search(name)
                if m and 'tlc_traces/' in name:
                    iter_id = int(m.group(1))
                    target_name = 'trace.json'

            if target_name is None or iter_id is None:
                continue

            if limit is not None and iter_id >= limit:
                continue

            iter_dir = os.path.join(run_root, f'iter_{iter_id:05d}')
            os.makedirs(iter_dir, exist_ok=True)
            target_path = os.path.join(iter_dir, target_name)

            if os.path.exists(target_path):
                iters_seen.add(iter_id)
                continue

            f = tar.extractfile(member)
            if f is None:
                continue
            with open(target_path, 'wb') as out:
                while True:
                    chunk = f.read(64 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
            files_written += 1
            iters_seen.add(iter_id)

    return len(iters_seen), files_written


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('archive', help='Path to redisraft/run_N.tar.gz')
    p.add_argument('--out', default='data/redisraft',
                   help='Output root (default: data/redisraft)')
    p.add_argument('--limit', type=int, default=None,
                   help='Only extract iterations with iter_id < LIMIT')
    args = p.parse_args(argv)

    if not os.path.isfile(args.archive):
        print(f'archive not found: {args.archive}', file=sys.stderr)
        return 1

    iters, files = extract(args.archive, args.out, args.limit)
    print(f'extracted {iters} iterations, {files} files written into {args.out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
