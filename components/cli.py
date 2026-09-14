"""``components``: the one write path for measured component dimensions.

    components measure <part> <CONST> <value> --by XX [--datasheet URL] [--no-push]
    components render-sheet [--sheet-id ID]
    components lint [--staged] [<path>]

``measure`` works on a local clone of this repo (``COMPONENTS_REPO``, default
``~/projects/components``). It fetches first and refuses (exit 2) unless the
clone is clean and HEAD is exactly ``origin/<branch>``: two people measuring
at once cannot silently overwrite each other. It writes the constant, commits,
tags the immutable ``components-v1.N`` (N from origin's tags), moves the
``components-v1`` tag, and pushes all three atomically. A failed push is
reported as exactly that, never as success.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from . import CONST_RE, iter_constants, parse_module
from .lint_consumer import main as lint_main

DEFAULT_REPO = Path(os.environ.get("COMPONENTS_REPO") or Path.home() / "projects" / "components")
DEFAULT_SHEET_ID = os.environ.get("COMPONENTS_SHEET_ID") or "1-G4-48xwSrVWiIt33I2HpkaiQWnqSUNHsJp5eKKWjxg"
SHEET_TAB = "COMPONENTS (generated)"
MOVING_TAG = "components-v1"
TAG_RE = re.compile(r"^components-v1\.(\d+)$")
PART_RE = re.compile(r"^[a-z][a-z0-9_]*$")
NAME_RE = re.compile(r"^[A-Z_][A-Z0-9_]*$")
BY_RE = re.compile(r"^[A-Z]{2,3}$")
URL_RE = re.compile(r"^https?://\S+$")


def die(msg: str, code: int = 1) -> None:
    print(f"components: {msg}", file=sys.stderr)
    sys.exit(code)


def git(repo: Path, *args: str, check: bool = True, code: int = 1) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        die(f"git {' '.join(args)} failed:\n{r.stderr.strip()}", code)
    return r


# ----------------------------------------------------------------- measure --
def _parse_value(text: str):
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            die(f"value must be a number, got {text!r}")


def _next_tag(repo: Path) -> str:
    """N + 1 where N is the highest components-v1.N that ORIGIN has."""
    r = git(repo, "ls-remote", "--tags", "--refs", "origin", "components-v1.*", code=2)
    n = 0
    for line in r.stdout.splitlines():
        m = TAG_RE.match(line.split("refs/tags/", 1)[-1])
        if m:
            n = max(n, int(m.group(1)))
    return f"components-v1.{n + 1}"


def _write_constant(path: Path, part: str, name: str, value, provenance: str) -> str:
    new_line = f"{name} = {value!r}  # {provenance}"
    if not path.exists():
        header = (f'"""{part}: created by `components measure` on '
                  f'{dt.date.today().isoformat()}. Add a description."""\n'
                  f'UNIT = "mm"\n')
        path.write_text(header + new_line + "\n")
        return "created"
    lines = path.read_text().splitlines()
    for i, raw in enumerate(lines):
        m = CONST_RE.match(raw)
        if m and m.group(1) == name:
            lines[i] = new_line
            path.write_text("\n".join(lines) + "\n")
            return "edited"
    lines.append(new_line)
    path.write_text("\n".join(lines) + "\n")
    return "appended"


def cmd_measure(a: argparse.Namespace) -> int:
    # 1. Validate every argument before touching anything.
    if not PART_RE.match(a.part):
        die(f"part must be a lowercase module name, got {a.part!r}")
    if not NAME_RE.match(a.const):
        die(f"constant must be UPPERCASE, got {a.const!r}")
    if a.const == "UNIT":
        die("UNIT is metadata, edit it by hand in the module")
    if not BY_RE.match(a.by):
        die(f"--by wants 2-3 uppercase initials, got {a.by!r}")
    if a.datasheet and not URL_RE.match(a.datasheet):
        die(f"--datasheet wants an http(s) URL, got {a.datasheet!r}")
    value = _parse_value(a.value)
    today = dt.date.today().isoformat()
    provenance = f"DATASHEET {a.datasheet}" if a.datasheet else f"CALIPER {today} {a.by}"

    # 2. The clone must exist, be on a branch, be clean, and match origin.
    repo = Path(a.repo).expanduser()
    pkg = repo / "components"
    if git(repo, "rev-parse", "--is-inside-work-tree", check=False).returncode != 0:
        die(f"no git clone at {repo} (set COMPONENTS_REPO)", 2)
    if not (pkg / "__init__.py").exists():
        die(f"{pkg} is not the components package; is {repo} a clone of flyinthelyceum/components?", 2)
    branch = git(repo, "symbolic-ref", "-q", "--short", "HEAD", check=False).stdout.strip()
    if not branch:
        die("clone is on a detached HEAD; check out a branch first", 2)
    dirty = git(repo, "status", "--porcelain").stdout.strip()
    if dirty:
        die(f"clone at {repo} is dirty; commit or stash first:\n{dirty}", 2)
    if not a.no_fetch:
        git(repo, "fetch", "--quiet", "origin", code=2)
        head = git(repo, "rev-parse", "HEAD").stdout.strip()
        upstream = git(repo, "rev-parse", f"origin/{branch}", check=False).stdout.strip()
        if not upstream:
            die(f"origin has no branch {branch}; push it first", 2)
        if head != upstream:
            die(f"clone is not at origin/{branch} (HEAD {head[:12]}, origin {upstream[:12]}); "
                f"run `git pull --ff-only` and measure again", 2)

    # 3. Write, verify, commit, tag. Any failure leaves the clone porcelain-clean.
    path = pkg / f"{a.part}.py"
    version_py = pkg / "_version.py"
    tag = _next_tag(repo) if not a.no_fetch else _next_tag_local(repo)
    action = _write_constant(path, a.part, a.const, value, provenance)
    try:
        compile(path.read_text(), str(path), "exec")
        parse_module(path)
    except (SyntaxError, ValueError) as e:
        _undo(repo, path, action)
        die(f"refusing to commit a module that does not parse: {e}")
    version_py.write_text("# Written by `components measure` when it tags. Do not edit by hand.\n"
                          f'TAG = "{tag}"\n')
    subject = f"components: {a.part}.{a.const} = {value!r} ({provenance})"
    git(repo, "add", str(path.relative_to(repo)), str(version_py.relative_to(repo)))
    if git(repo, "commit", "-q", "-m", subject, check=False).returncode != 0:
        git(repo, "reset", "-q", "--hard", "HEAD", check=False)
        _undo(repo, path, action)
        die("git commit failed; clone restored")
    sha = git(repo, "rev-parse", "--short", "HEAD").stdout.strip()
    git(repo, "tag", tag)
    git(repo, "tag", "-f", MOVING_TAG)
    print(f"{action} {path.relative_to(repo)}: {a.const} = {value!r}  # {provenance}")
    print(f"committed {sha}, tagged {tag}, moved {MOVING_TAG}")
    if a.no_push:
        print("push disabled (--no-push); commit and tags are local only")
        return 0
    push = git(repo, "push", "--atomic", "origin", "HEAD", tag, f"+{MOVING_TAG}", check=False)
    if push.returncode != 0:
        print(f"committed and tagged locally, push failed: {push.stderr.strip()}", file=sys.stderr)
        return 2
    print(f"pushed {branch}, {tag} and {MOVING_TAG} to origin")
    return 0


def _next_tag_local(repo: Path) -> str:
    tags = git(repo, "tag", "--list", "components-v1.*").stdout.split()
    n = max((int(m.group(1)) for t in tags if (m := TAG_RE.match(t))), default=0)
    return f"components-v1.{n + 1}"


def _undo(repo: Path, path: Path, action: str) -> None:
    if action == "created":
        path.unlink(missing_ok=True)
    else:
        git(repo, "checkout", "--", str(path.relative_to(repo)), check=False)


# ------------------------------------------------------------ render-sheet --
def _tokens() -> list[str]:
    """Candidate bearer tokens, most likely owner of the sheet first."""
    out: list[str] = []
    env = os.environ.get("COMPONENTS_GOOGLE_TOKEN")
    if env:
        out.append(env)
    script = Path.home() / "labnode-scripts" / "google-auth.mjs"
    if script.exists():
        for account in ("personal", "brophy"):
            r = subprocess.run(["node", str(script), "--token", f"--account={account}"],
                               capture_output=True, text=True)
            if r.returncode == 0 and r.stdout.strip():
                out.append(r.stdout.strip())
    mcp = Path.home() / ".config" / "google-drive-mcp" / "tokens.json"
    if mcp.exists():
        try:
            out.append(json.load(open(mcp))["access_token"])
        except (KeyError, ValueError):
            pass
    if not out:
        die("no Google token: set COMPONENTS_GOOGLE_TOKEN (Sheets scope)")
    return out


def _api(token: str, url: str, body=None, method: str = "GET"):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {token}",
                                          "Content-Type": "application/json"}, method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def _rows() -> list[list]:
    header = ["part", "constant", "value", "unit", "provenance", "source", "module"]
    rows = [header]
    for c in iter_constants():
        rows.append([c.part, c.name, "" if c.value is None else c.value, c.unit,
                     c.kind if c.kind != "NEEDED" else "CALIPER needed", c.source,
                     f"components/{c.file.name}:{c.line}"])
    return rows


def cmd_render_sheet(a: argparse.Namespace) -> int:
    rows = _rows()
    base = f"https://sheets.googleapis.com/v4/spreadsheets/{a.sheet_id}"
    last_err = None
    for token in _tokens():
        try:
            meta = _api(token, f"{base}?fields=sheets.properties")
            titles = [s["properties"]["title"] for s in meta["sheets"]]
            if SHEET_TAB not in titles:
                _api(token, f"{base}:batchUpdate",
                     {"requests": [{"addSheet": {"properties": {"title": SHEET_TAB}}}]}, "POST")
            clear_rng = f"'{SHEET_TAB}'!A:Z"
            write_rng = f"'{SHEET_TAB}'!A1"
            _api(token, f"{base}/values/{urllib.request.quote(clear_rng)}:clear", {}, "POST")
            # The body's range must equal the URL's, or Sheets answers 400.
            _api(token, f"{base}/values/{urllib.request.quote(write_rng)}?valueInputOption=RAW",
                 {"range": write_rng, "majorDimension": "ROWS", "values": rows}, "PUT")
            print(f"wrote {len(rows) - 1} constants to '{SHEET_TAB}' on "
                  f"https://docs.google.com/spreadsheets/d/{a.sheet_id}")
            return 0
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}"
            if e.code not in (401, 403):
                break
    die(f"sheet write failed: {last_err}")
    return 1


# --------------------------------------------------------------------- main --
def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="components", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("measure", help="record a measurement, commit, tag, push")
    m.add_argument("part", help="module name, e.g. ws2812_ring12 (created if new)")
    m.add_argument("const", help="UPPERCASE constant, e.g. THICKNESS")
    m.add_argument("value", help="number, in the module's UNIT (mm unless it says in)")
    m.add_argument("--by", required=True, help="initials of who held the caliper, e.g. JR")
    m.add_argument("--datasheet", metavar="URL", help="provenance is this datasheet, not a caliper")
    m.add_argument("--no-push", action="store_true", help="commit and tag locally only")
    m.add_argument("--no-fetch", action="store_true", help=argparse.SUPPRESS)
    m.add_argument("--repo", default=str(DEFAULT_REPO), help=f"clone to write (default {DEFAULT_REPO})")
    m.set_defaults(fn=cmd_measure)

    r = sub.add_parser("render-sheet", help=f"write every constant to the '{SHEET_TAB}' tab")
    r.add_argument("--sheet-id", default=DEFAULT_SHEET_ID)
    r.set_defaults(fn=cmd_render_sheet)

    l = sub.add_parser("lint", help="refuse measured constants outside the lib")
    l.add_argument("--staged", action="store_true", help="lint the git index, not the working tree")
    l.add_argument("path", nargs="?", default=".")
    l.set_defaults(fn=lambda a: lint_main((["--staged"] if a.staged else []) + [a.path]))

    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
