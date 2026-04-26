from __future__ import annotations

from pathlib import Path

from .utils import load_json, write_json


def load_parent_business(path: Path):
    return load_json(path)


def emit_parent_business_artifact(parent_business: dict, out_dir: Path):
    write_json(out_dir / "protocol_cybersecurity_studio.json", parent_business)
    # Compatibility alias for older references.
    write_json(out_dir / "protocol_assurance_studio.json", parent_business)
