#!/usr/bin/env python3
"""Export deterministic OpenAPI JSON for release provenance bundles."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.main import app


def main() -> None:
    root = ROOT
    out_dir = root / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)
    output = out_dir / "openapi-v2.6.0-rc.1.json"

    spec = app.openapi()
    output.write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {output.relative_to(root)}")


if __name__ == "__main__":
    main()
