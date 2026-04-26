#!/usr/bin/env python3
"""Assemble a reveal-time receipt after score lock for blinded adjacent-transfer runs.

This helper is intentionally narrow:
- reads private blinded assignment map and commitment hashes from local-private storage
- emits a public-safe reveal receipt with only hashes + lane mapping metadata
- never publishes reviewer identity map or answer keys
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from normalize_reviewer_packets import refresh_public_provenance

PACK_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = PACK_ROOT / "results_blinded_adjacent_transfer_v1"
DEFAULT_PRIVATE = PACK_ROOT / "local_private_blinding_materials" / "results_blinded_adjacent_transfer_v1"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_assignment_map(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def validate_commitment_hashes(path: Path) -> None:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise SystemExit(f"Commitment hash file is empty: {path}")
    if "Run 07_scripts/generate_private_commitment_hashes.py" in text:
        raise SystemExit(
            "Commitment hash file is still placeholder content. "
            "Run 07_scripts/generate_private_commitment_hashes.py before assembling reveal receipt."
        )
    sha256_pattern = re.compile(r"^[0-9a-f]{64}$")
    has_hash_line = any(
        len(line.split()) >= 2 and bool(sha256_pattern.fullmatch(line.split()[0]))
        for line in text.splitlines()
        if line and not line.startswith("#")
    )
    if not has_hash_line:
        raise SystemExit(
            "Commitment hash file does not contain SHA-256 hash records. "
            "Regenerate with 07_scripts/generate_private_commitment_hashes.py."
        )


def get_first(row: dict[str, str], keys: list[str]) -> str:
    for key in keys:
        if key in row:
            return row.get(key, "")
    raise KeyError(f"Missing expected header(s): {', '.join(keys)}")


def get_first_optional(row: dict[str, str], keys: list[str], default: str = "") -> str:
    for key in keys:
        if key in row:
            return row.get(key, "")
    return default


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default=str(DEFAULT_RESULTS))
    parser.add_argument("--private-dir", default=str(DEFAULT_PRIVATE))
    parser.add_argument(
        "--confirm-score-lock",
        action="store_true",
        help="required safety flag; indicates scorecard adjudication has been locked",
    )
    args = parser.parse_args()

    if not args.confirm_score_lock:
        raise SystemExit("Refusing reveal assembly without --confirm-score-lock")

    results_dir = Path(args.results_dir)
    private_dir = Path(args.private_dir)

    assignment_map = private_dir / "blinded_assignment_map.private.csv"
    commitment_hashes = private_dir / "private_commitment_hashes.txt"

    missing = [str(p) for p in [assignment_map, commitment_hashes] if not p.exists()]
    if missing:
        raise SystemExit("Missing required private files:\n- " + "\n- ".join(missing))
    validate_commitment_hashes(commitment_hashes)

    mapping_rows = load_assignment_map(assignment_map)
    if not mapping_rows:
        raise SystemExit(
            "Assignment map has zero data rows. "
            "Fill blinded_assignment_map.private.csv before assembling reveal receipt."
        )
    lanes_only = []
    for row in mapping_rows:
        try:
            lane_id = get_first(row, ["blinded_lane_id", "lane_id", "blinded_output_id"])
            assigned_kit = get_first_optional(
                row,
                ["kit_variant", "assigned_kit"],
                default="UNSPECIFIED_LEGACY_TEMPLATE",
            )
            assignment_role = get_first(row, ["actual_lane", "assignment_role"])
        except KeyError as exc:
            raise SystemExit(str(exc)) from exc
        lanes_only.append(
            {
                "artifact_set": row.get("artifact_set", ""),
                "lane_id": lane_id,
                "assigned_kit": assigned_kit,
                "assignment_role": assignment_role,
                "revealed_after_score_lock": "true",
                "revealed_after_score_lock_source": row.get("revealed_after_score_lock", ""),
            }
        )

    receipt = {
        "receipt_type": "blinded_adjacent_transfer_reveal_receipt",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "score_lock_confirmed": True,
        "private_assignment_map_sha256": sha256_file(assignment_map),
        "private_commitment_hashes_sha256": sha256_file(commitment_hashes),
        "lane_assignments": lanes_only,
        "notes": [
            "This receipt intentionally excludes reviewer identities and answer keys.",
            "Reveal should happen only after adjudication and scorecard lock.",
        ],
    }

    out_path = results_dir / "scorecard_outputs" / "reveal_receipt_public.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    refresh_public_provenance(results_dir)
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
