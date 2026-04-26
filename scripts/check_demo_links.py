#!/usr/bin/env python3
"""Validate demo ladder links, role labels, and active RC target markers."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    ROOT / "README.md",
    ROOT / "demos" / "README.md",
    ROOT / "demos" / "protocol_smart_contract_correctness_demo" / "README.md",
    ROOT / "demos" / "adjacent_mandate_reuse_proof_demo" / "README.md",
    ROOT / "demos" / "adjacent_mandate_reuse_proof_real_v1" / "README.md",
    ROOT / "demos" / "open-ended-rsi-system" / "README.md",
    ROOT / "demos" / "unbounded-rsi-system" / "README.md",
]

REQUIRED_PATHS = [
    "demos/protocol_smart_contract_correctness_demo/",
    "demos/adjacent_mandate_reuse_proof_demo/",
    "demos/adjacent_mandate_reuse_proof_real_v1/",
    "demos/open-ended-rsi-system/",
    "demos/unbounded-rsi-system/",
]

REQUIRED_PHRASES = [
    "Flagship synthetic wedge demo",
    "Adjacent synthetic proof demo",
    "Real-world proof pack",
    "Accelerating-loop demo",
]



BADGE_CONFIG = ROOT / "release" / "badges.json"


def _load_release_target() -> str:
    data = json.loads(BADGE_CONFIG.read_text(encoding="utf-8"))
    target = data.get("release_target", "")
    if not target:
        raise ValueError("release/badges.json missing release_target")
    return target


RC_TARGET_MARKERS = {
    "demos/README.md": "Demo Ladder ({target} target)",
    "demos/open-ended-rsi-system/README.md": "Open-Ended RSI System Demo ({target} target)",
}

REQUIRED_CROSSLINKS = {
    "demos/open-ended-rsi-system/README.md": [
        "../protocol_smart_contract_correctness_demo/",
        "../adjacent_mandate_reuse_proof_demo/",
        "../adjacent_mandate_reuse_proof_real_v1/",
        "../README.md",
    ],
    "demos/unbounded-rsi-system/README.md": [
        "../open-ended-rsi-system/",
        "../README.md",
    ],
}


def main() -> int:
    errors: list[str] = []
    try:
        expected_rc_target = _load_release_target()
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL\n- unable to load release target from release/badges.json: {exc}")
        return 1

    for file in FILES:
        if not file.exists():
            errors.append(f"missing file: {file.relative_to(ROOT)}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for path in REQUIRED_PATHS:
        if path not in readme:
            errors.append(f"README missing demo path: {path}")
        if not (ROOT / path).exists():
            errors.append(f"README path target missing: {path}")

    demos_readme = (ROOT / "demos" / "README.md").read_text(encoding="utf-8")
    for phrase in REQUIRED_PHRASES:
        if phrase not in demos_readme:
            errors.append(f"demos/README.md missing phrase: {phrase}")

    for path in (ROOT / "demos").glob("*/README.md"):
        text = path.read_text(encoding="utf-8")
        if "../README.md" not in text:
            errors.append(f"missing ladder index link in {path.relative_to(ROOT)}")


    for rel_path, marker_template in RC_TARGET_MARKERS.items():
        target = ROOT / rel_path
        if not target.exists():
            errors.append(f"missing RC marker target file: {rel_path}")
            continue
        text = target.read_text(encoding="utf-8")
        marker = marker_template.format(target=expected_rc_target)
        if marker not in text:
            errors.append(
                f"{rel_path} missing expected RC target marker: {marker}"
            )

    for rel_path, required_links in REQUIRED_CROSSLINKS.items():
        target = ROOT / rel_path
        if not target.exists():
            errors.append(f"missing cross-link target file: {rel_path}")
            continue
        text = target.read_text(encoding="utf-8")
        for required_link in required_links:
            if required_link not in text:
                errors.append(
                    f"{rel_path} missing required cross-link reference: {required_link}"
                )

    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PASS: demo ladder links and labels are coherent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
