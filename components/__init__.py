"""Physical component dimensions: the one place they are written.

One module per part. Flat UPPERCASE constants. Every constant carries a
provenance comment that is exactly one of

    # CALIPER YYYY-MM-DD XX      measured on the part in hand, by XX
    # DATASHEET <url>            read from the maker's drawing or table
    # CALIPER needed             value is None; nobody has measured it

CHOICE and DERIVED values never live here. They belong to the design that makes
the choice or the derivation, next to the reasoning.

Units are millimetres unless the module says ``UNIT = "in"``; a part measured in
inches stays in inches so the reading in the file is the reading on the caliper.

Write with ``components measure <part> <CONST> <value> --by XX``; never by hand.
Consumers import (``from components import ws2812_ring12 as ring``) and never
restate a number. ``components lint <repo>`` refuses one that does.
"""
from __future__ import annotations

import ast
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ._version import TAG

__version__ = TAG

ROOT = Path(__file__).resolve().parent
_NOT_PARTS = {"__init__", "__main__", "_version", "cli", "lint_consumer"}

CONST_RE = re.compile(r"^([A-Z_][A-Z0-9_]*)\s*=\s*(.+?)\s*(?:#\s*(.*?))?\s*$")
PROVENANCE_RE = re.compile(
    r"^(?:CALIPER (\d{4}-\d{2}-\d{2}) ([A-Z]{2,3})|DATASHEET (\S+)|CALIPER needed)$"
)


@dataclass(frozen=True)
class Constant:
    part: str
    name: str
    value: object
    unit: str
    kind: str      # CALIPER | DATASHEET | NEEDED
    source: str    # "YYYY-MM-DD XX" | url | ""
    file: Path
    line: int


def part_modules() -> list[str]:
    return sorted(p.stem for p in ROOT.glob("*.py")
                  if p.stem not in _NOT_PARTS and not p.stem.startswith("_"))


def parse_module(path: Path) -> list[Constant]:
    """Read a part module textually, so None and provenance survive."""
    part = path.stem
    unit = "mm"
    out: list[Constant] = []
    lines = path.read_text().splitlines()
    for i, raw in enumerate(lines, 1):
        m = CONST_RE.match(raw)
        if not m:
            continue
        name, expr, comment = m.group(1), m.group(2), (m.group(3) or "")
        if name == "UNIT":
            unit = ast.literal_eval(expr)
            continue
        pm = PROVENANCE_RE.match(comment)
        if not pm:
            raise ValueError(f"{path}:{i}: {name} has no valid provenance comment: {comment!r}")
        try:
            value = ast.literal_eval(expr)
        except (ValueError, SyntaxError) as e:
            raise ValueError(f"{path}:{i}: {name} is not a literal: {expr!r}") from e
        if pm.group(1):
            kind, source = "CALIPER", f"{pm.group(1)} {pm.group(2)}"
        elif pm.group(3):
            kind, source = "DATASHEET", pm.group(3)
        else:
            kind, source = "NEEDED", ""
        if kind == "NEEDED" and value is not None:
            raise ValueError(f"{path}:{i}: {name} says CALIPER needed but has a value")
        if kind != "NEEDED" and value is None:
            raise ValueError(f"{path}:{i}: {name} is None but claims a source")
        out.append(Constant(part, name, value, unit, kind, source, path, i))
    return out


def iter_constants() -> list[Constant]:
    out: list[Constant] = []
    for part in part_modules():
        out.extend(parse_module(ROOT / f"{part}.py"))
    return out


def validate() -> int:
    """Every module parses and every constant carries a provenance. Returns the count."""
    return len(iter_constants())


def version() -> str:
    """The installed tag, plus the resolved commit when pip recorded one.

    Stamp this into any cut artifact (a DXF, a cut list, a print) so the
    numbers it was cut from can be found again: ``components-v1.3+a1b2c3d``.
    """
    sha = ""
    try:
        from importlib.metadata import distribution
        text = distribution("components").read_text("direct_url.json")
        if text:
            sha = json.loads(text).get("vcs_info", {}).get("commit_id", "")[:12]
    except Exception:  # not installed via pip, or no direct_url
        pass
    if not sha:
        r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short=12", "HEAD"],
                           capture_output=True, text=True)
        if r.returncode == 0:
            sha = r.stdout.strip()
    return f"{TAG}+{sha}" if sha else TAG
