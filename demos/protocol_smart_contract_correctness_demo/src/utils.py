from __future__ import annotations
from pathlib import Path
import json
import shutil

DEMO_TIMESTAMP = "2026-01-01T00:00:00Z"


def load_json(path: Path):
    return json.loads(path.read_text())


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def reset_dir(path: Path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def demo_timestamp() -> str:
    return DEMO_TIMESTAMP
