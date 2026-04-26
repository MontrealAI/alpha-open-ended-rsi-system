#!/usr/bin/env python3
"""Generate disciplined badge rails from release/badges.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
BADGE_CONFIG = ROOT / "release" / "badges.json"
README = ROOT / "README.md"
DEMOS_README = ROOT / "demos" / "README.md"

README_MARKERS = ("<!-- BADGE_RAIL_START -->", "<!-- BADGE_RAIL_END -->")
DEMOS_MARKERS = ("<!-- DEMO_BADGE_STRIP_START -->", "<!-- DEMO_BADGE_STRIP_END -->")


def _load_config() -> dict:
    return json.loads(BADGE_CONFIG.read_text(encoding="utf-8"))


def _workflow_image(repo: str, workflow: str, style: str) -> str:
    return f"https://github.com/{repo}/actions/workflows/{workflow}/badge.svg?style={style}"


def _static_image(label: str, message: str, color: str, style: str) -> str:
    q_label = quote(label, safe="")
    q_message = quote(message, safe="")
    return f"https://img.shields.io/badge/{q_label}-{q_message}-{color}?style={style}"


def _badge_markdown(repo: str, style: str, badge: dict) -> str:
    alt = badge["alt"]
    link = badge["link"]

    kind = badge["kind"]
    if kind == "workflow":
        image = _workflow_image(repo=repo, workflow=badge["workflow"], style=style)
    elif kind == "static":
        image = _static_image(
            label=badge["label"],
            message=badge["message"],
            color=badge["color"],
            style=style,
        )
    elif kind == "dynamic":
        image = badge["image"]
    else:
        raise ValueError(f"unsupported badge kind: {kind}")

    return f"[![{alt}]({image})]({link})"


def _render_block(lines: list[str], start: str, end: str) -> str:
    return "\n".join([start, *lines, end])


def _replace_marked_block(text: str, markers: tuple[str, str], block: str) -> str:
    start, end = markers
    if start not in text or end not in text:
        raise ValueError(f"missing markers: {start} / {end}")

    prefix, remainder = text.split(start, 1)
    _, suffix = remainder.split(end, 1)
    return f"{prefix}{block}{suffix}"


def _find_badge(config: dict, badge_id: str) -> dict:
    for badge in config["readme"]["badges"]:
        if badge["id"] == badge_id:
            return badge
    raise KeyError(f"unknown badge id: {badge_id}")


def _expand_row_entries(config: dict, entries: list) -> list[dict]:
    expanded: list[dict] = []
    for entry in entries:
        if isinstance(entry, str):
            expanded.append(dict(_find_badge(config, entry)))
            continue

        badge = dict(_find_badge(config, entry["id"]))
        if "link" in entry:
            badge["link"] = entry["link"]
        expanded.append(badge)
    return expanded


def _render_rows(config: dict, rows: list[dict], repo: str, style: str) -> list[str]:
    rendered: list[str] = []
    for row in rows:
        if row.get("label"):
            rendered.append(f"**{row['label']}**")
        badges = _expand_row_entries(config, row["badges"])
        rendered.append(" ".join(_badge_markdown(repo, style, badge) for badge in badges))
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write badge rails into README files")
    args = parser.parse_args()

    config = _load_config()
    style = config["style"]
    repo = "MontrealAI/alpha-nova-seeds"

    readme_rows = config["readme"].get("rows")
    if not readme_rows:
        readme_rows = [{"badges": [badge["id"] for badge in config["readme"]["badges"]]}]
    readme_lines = _render_rows(config, readme_rows, repo, style)

    demos_rows = config["demos_readme"].get("rows")
    if not demos_rows:
        demos_rows = [{"badges": config["demos_readme"].get("badges", [])}]
    demos_lines = _render_rows(config, demos_rows, repo, style)

    readme_block = _render_block(readme_lines, *README_MARKERS)
    demos_block = _render_block(demos_lines, *DEMOS_MARKERS)

    if args.write:
        README.write_text(
            _replace_marked_block(README.read_text(encoding="utf-8"), README_MARKERS, readme_block),
            encoding="utf-8",
        )
        DEMOS_README.write_text(
            _replace_marked_block(DEMOS_README.read_text(encoding="utf-8"), DEMOS_MARKERS, demos_block),
            encoding="utf-8",
        )
        print("Updated README.md and demos/README.md badge rails")
    else:
        print("# README badge rail")
        print(readme_block)
        print()
        print("# demos/README badge strip")
        print(demos_block)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
