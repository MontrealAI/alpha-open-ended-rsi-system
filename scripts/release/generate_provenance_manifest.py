#!/usr/bin/env python3
"""Generate deterministic provenance manifest for release candidate artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

INCLUDE_GLOBS = [
    "contracts/*.sol",
    "contracts/interfaces/*.sol",
    "contracts/abi/*.json",
    "backend/migrations/*.sql",
    "backend/app/**/*.py",
    "sdk/**/*.ts",
    "docs/**/*.md",
    "schemas/**/*.json",
    "example_*_v25.json",
    "README.md",
    "CHANGELOG.md",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def iter_files() -> list[Path]:
    seen: set[Path] = set()
    files: list[Path] = []
    for pattern in INCLUDE_GLOBS:
        for p in sorted(REPO_ROOT.glob(pattern)):
            if p.is_file() and p not in seen:
                seen.add(p)
                files.append(p)
    return sorted(files)


def deterministic_timestamp() -> str:
    env_epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if env_epoch:
        return datetime.fromtimestamp(int(env_epoch), tz=timezone.utc).isoformat()

    git_commit_time = subprocess.check_output(
        ["git", "log", "-1", "--format=%cI", "HEAD"],
        cwd=REPO_ROOT,
        text=True,
    ).strip()
    if git_commit_time:
        return git_commit_time

    return datetime(1970, 1, 1, tzinfo=timezone.utc).isoformat()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    manifest = {
        "release_tag": args.tag,
        "generated_at_utc": deterministic_timestamp(),
        "generator": "scripts/release/generate_provenance_manifest.py",
        "files": [],
    }

    for fp in iter_files():
        rel = fp.relative_to(REPO_ROOT).as_posix()
        manifest["files"].append(
            {
                "path": rel,
                "size_bytes": fp.stat().st_size,
                "sha256": sha256_file(fp),
            }
        )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
