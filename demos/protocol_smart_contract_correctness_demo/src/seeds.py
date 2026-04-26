from __future__ import annotations
from pathlib import Path
from .utils import load_json, write_json


def load_seed_packets(seed_dir: Path):
    packets = []
    for path in sorted(seed_dir.glob("*_seed.json")):
        packets.append(load_json(path))
    return packets


def emit_seed_packets(seed_packets: list[dict], out_dir: Path):
    for packet in seed_packets:
        write_json(out_dir / f"{packet['id']}_seed.json", packet)
