#!/usr/bin/env python3
"""Generate SHA-256 commitment hashes for private blinding files."""

from __future__ import annotations

import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path

PACK_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRIVATE_DIR = PACK_ROOT / "local_private_blinding_materials" / "results_blinded_adjacent_transfer_v1"

REQUIRED_PRIVATE_FILES = [
    "answer_key_m1.private.md",
    "answer_key_m2.private.md",
    "answer_key_m3.private.md",
    "blinded_assignment_map.private.csv",
    "reviewer_identity_map.private.csv",
]

KIT_SUBDIRS = ["Kit Blue", "Kit Gold"]
KIT_REQUIRED_FILES = [
    "ontology.json",
    "query_bundle.json",
    "workflow_template.md",
    "mechanism_library.json",
    "safety_routing_rules.md",
    "scoring_rubric.md",
    "extraction_schema.json",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-dir", default=str(DEFAULT_PRIVATE_DIR))
    parser.add_argument("--signer", default="REPLACE_WITH_BLINDING_OFFICER")
    args = parser.parse_args()

    private_dir = Path(args.private_dir)
    missing = [name for name in REQUIRED_PRIVATE_FILES if not (private_dir / name).exists()]
    for kit_name in KIT_SUBDIRS:
        for filename in KIT_REQUIRED_FILES:
            path = private_dir / "kits" / kit_name / filename
            if not path.exists():
                missing.append(f"kits/{kit_name}/{filename}")
    if missing:
        raise SystemExit(f"Missing private files in {private_dir}: {', '.join(missing)}")

    ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    lines = [
        "# Private commitment hashes",
        f"timestamp_utc: {ts}",
        f"signer: {args.signer}",
        "",
    ]
    for name in REQUIRED_PRIVATE_FILES:
        digest = sha256_file(private_dir / name)
        lines.append(f"{digest}  {name}")
    for kit_name in KIT_SUBDIRS:
        for filename in KIT_REQUIRED_FILES:
            rel = f"kits/{kit_name}/{filename}"
            digest = sha256_file(private_dir / rel)
            lines.append(f"{digest}  {rel}")

    out_path = private_dir / "private_commitment_hashes.txt"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
