#!/usr/bin/env python3
"""Normalize lane output artifacts into public-safe blinded reviewer packets."""

from __future__ import annotations

import argparse
import json
import shutil
import hashlib
import re
from pathlib import Path

PACK_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = PACK_ROOT / "results_blinded_adjacent_transfer_v1"
DEFAULT_PRIVATE = PACK_ROOT / "local_private_blinding_materials" / "results_blinded_adjacent_transfer_v1"

ALLOWED_FILENAMES = {
    "findings.md",
    "tests.md",
    "evidence_index.json",
    "repro_steps.md",
    "notes.md",
}
DISALLOWED_PATTERNS = [
    "operator",
    "kit blue",
    "kit gold",
    "control",
    "treatment",
]


def _label_regex(pattern: str) -> re.Pattern[str]:
    """Match only full standalone labels (or full phrases), not substrings in identifiers."""
    parts = [re.escape(token) for token in pattern.split()]
    body = r"\s+".join(parts)
    return re.compile(rf"(?<![A-Za-z0-9_]){body}(?![A-Za-z0-9_])", flags=re.IGNORECASE)


def sanitize_text(text: str) -> str:
    output = text
    for pattern in DISALLOWED_PATTERNS:
        output = _label_regex(pattern).sub("[redacted]", output)
    return output


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_lane(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    copied = 0
    for name in sorted(ALLOWED_FILENAMES):
        in_file = src / name
        if not in_file.exists():
            continue
        out_file = dst / name
        text = in_file.read_text(encoding="utf-8")
        out_file.write_text(sanitize_text(text), encoding="utf-8")
        copied += 1
    (dst / "README.md").write_text(
        "# Normalized blinded reviewer packet\n\n"
        "This packet intentionally excludes operator identity, explicit lane type labels, "
        "and private assignment metadata.\n",
        encoding="utf-8",
    )
    print(f"Normalized {copied} files from {src} -> {dst}")


def validate_source_packet_dir(src: Path) -> None:
    if not src.exists() or not src.is_dir():
        raise SystemExit(f"Missing source packet directory: {src}")
    present = [name for name in ALLOWED_FILENAMES if (src / name).is_file()]
    if not present:
        raise SystemExit(
            f"Source packet directory has no allowed reviewer artifacts: {src}. "
            f"Expected one or more of: {', '.join(sorted(ALLOWED_FILENAMES))}"
        )


def refresh_public_provenance(results_dir: Path) -> None:
    manifest_path = results_dir / "provenance_manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"Missing provenance manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    tracked_paths: set[str] = set()
    for item in manifest.get("file_hashes", []):
        rel = item.get("path")
        if rel:
            tracked_paths.add(rel)

    for lane in ["blue", "gold"]:
        for stage in ["stage_a", "stage_b"]:
            packet_dir = results_dir / f"lane_{lane}_packet_public" / stage
            if not packet_dir.exists():
                continue
            for file_path in sorted(packet_dir.glob("*")):
                if file_path.is_file():
                    tracked_paths.add(str(file_path.relative_to(results_dir)))
    scorecard_out_dir = results_dir / "scorecard_outputs" / "out"
    if scorecard_out_dir.exists():
        for file_path in sorted(scorecard_out_dir.glob("*")):
            if file_path.is_file():
                tracked_paths.add(str(file_path.relative_to(results_dir)))
    reveal_receipt = results_dir / "scorecard_outputs" / "reveal_receipt_public.json"
    if reveal_receipt.exists() and reveal_receipt.is_file():
        tracked_paths.add(str(reveal_receipt.relative_to(results_dir)))

    hashes = []
    for rel in sorted(tracked_paths):
        p = results_dir / rel
        if p.exists() and p.is_file():
            hashes.append({"path": rel, "sha256": sha256_file(p)})
    manifest["file_hashes"] = hashes
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default=str(DEFAULT_RESULTS))
    parser.add_argument("--private-dir", default=str(DEFAULT_PRIVATE))
    parser.add_argument("--stage", choices=["stage_a", "stage_b"], default="stage_a")
    parser.add_argument(
        "--refresh-only",
        action="store_true",
        help="refresh public provenance hashes without reading raw reviewer packet sources",
    )
    parser.add_argument("--force", action="store_true", help="overwrite existing normalized packet files")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    private_dir = Path(args.private_dir)

    if args.refresh_only:
        refresh_public_provenance(results_dir)
        return 0

    if args.stage == "stage_a":
        src_blue = private_dir / "raw_packets" / "stage_a" / "lane_blue"
        src_gold = private_dir / "raw_packets" / "stage_a" / "lane_gold"
    else:
        src_blue = private_dir / "raw_packets" / "stage_b" / "lane_blue"
        src_gold = private_dir / "raw_packets" / "stage_b" / "lane_gold"

    dst_blue = results_dir / "lane_blue_packet_public" / args.stage
    dst_gold = results_dir / "lane_gold_packet_public" / args.stage

    validate_source_packet_dir(src_blue)
    validate_source_packet_dir(src_gold)

    if args.force:
        for dst in [dst_blue, dst_gold]:
            if dst.exists():
                shutil.rmtree(dst)

    normalize_lane(src_blue, dst_blue)
    normalize_lane(src_gold, dst_gold)
    refresh_public_provenance(results_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
