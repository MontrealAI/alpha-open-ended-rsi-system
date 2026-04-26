from __future__ import annotations
from pathlib import Path
import re

FUNCTION_RE = re.compile(r"function\s+([A-Za-z0-9_]+)\s*\([^)]*\)[^{]*\{", re.MULTILINE)


def read_contracts(folder: Path):
    return {path.name: path.read_text() for path in sorted(folder.glob("*.sol"))}


def function_bodies(source: str):
    out = []
    for m in FUNCTION_RE.finditer(source):
        name = m.group(1)
        i = m.end()
        depth = 1
        while i < len(source) and depth > 0:
            if source[i] == "{":
                depth += 1
            elif source[i] == "}":
                depth -= 1
            i += 1
        out.append((name, source[m.end(): i - 1]))
    return out


def line_for_function(source: str, function_name: str) -> int:
    marker = f"function {function_name}"
    idx = source.find(marker)
    return 1 if idx < 0 else source[:idx].count("\n") + 1
