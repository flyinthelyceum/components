#!/usr/bin/env python3
"""Refuse measured constants outside the components package.

A consumer repo imports its measurements from ``components``; it never
restates one. This scan finds a number whose comment, element comment,
following docstring, or data-file line says caliper or datasheet (any case),
and exits 1 with the file:line and the ``components measure`` command to run
instead. Exit 0 when clean.

Trailing and element comments are matched case-insensitively (``caliper``,
``calipered``, ``datasheet``). A docstring right after an assignment, and a
line in a ``.toml``/``.json``/``.csv`` file, is matched on the uppercase tags
``CALIPER``/``CALIPERED``/``DATASHEET`` only: prose such as "CONFIDENCE:
datasheet" describes a source without restating a measurement tag.

What passes on purpose:
  * a comment led by a design word (CHOICE, DERIVED, ESTIMATE, ASSUMPTION,
    LIB) that merely mentions the caliper in prose;
  * a line carrying ``# lint: not-a-measurement``;
  * docs (``docs/``, ``*.md``), ``.claude/``, virtualenvs, build output, and
    the components package's own tree.

``--staged`` lints the git index (what the commit would contain) instead of the
working tree; the pre-commit hook uses that.

Standalone on purpose: the hook runs it as a script from any clone, with no
package installed. Also reachable as ``components lint [--staged] <path>``.
"""
from __future__ import annotations

import io
import re
import subprocess
import sys
import tokenize
from dataclasses import dataclass
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "env", "node_modules", "__pycache__", ".pio",
             "build", "dist", "vendor", "out", "export", ".claude", ".pytest_cache",
             ".eggs", "site-packages", "docs"}
SKIP_SUFFIXES = {".md"}
DATA_SUFFIXES = {".toml", ".json", ".csv"}
ALLOW = "lint: not-a-measurement"

MEASURE_WORD = re.compile(r"caliper|datasheet", re.I)          # trailing and element comments
TAG_WORD = re.compile(r"\b(CALIPER|CALIPERED|DATASHEET)\b")     # docstrings and data files
DESIGN_LED = re.compile(r"^\s*(CHOICE|DERIVED|ESTIMATE|ASSUMPTION|LIB)\b")
HAS_NUMBER = re.compile(r"(?<![\w.])-?\d+(\.\d+)?(?![\w])")
NUMBER_ONLY = re.compile(r"^-?\d+(\.\d+)?$")
DATA_LINE = re.compile(r"[=:]")
GENERIC_STEMS = {"params", "config", "constants", "settings", "model", "__init__"}


@dataclass(frozen=True)
class Finding:
    file: Path
    line: int
    name: str
    value: str
    comment: str

    def command(self) -> str:
        part = re.sub(r"[^a-z0-9_]", "_", self.file.stem.lower())
        if part in GENERIC_STEMS:
            part = "<part>"
        value = self.value if NUMBER_ONLY.match(self.value) else "<value>"
        flag = " --datasheet <url>" if "datasheet" in self.comment.lower() else ""
        return f"components measure {part} {self.name.upper()} {value} --by XX{flag}"


def _is_lib_dir(d: Path) -> bool:
    return d.name == "components" and (d / "lint_consumer.py").exists()


def _skip_path(rel: Path) -> bool:
    if any(part in SKIP_DIRS or part.startswith(".venv") for part in rel.parts[:-1]):
        return True
    return rel.suffix in SKIP_SUFFIXES


def _files(root: Path):
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix not in {".py", *DATA_SUFFIXES}:
            continue
        rel = p.relative_to(root)
        if _skip_path(rel) or any(_is_lib_dir(root / Path(*rel.parts[:i + 1]))
                                  for i in range(len(rel.parts) - 1)):
            continue
        yield p, rel


def _suspect(comment: str) -> bool:
    body = comment.lstrip("#")
    if ALLOW in body or DESIGN_LED.match(body):
        return False
    return bool(MEASURE_WORD.search(body))


def scan_python(text: str, path: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, SyntaxError, IndentationError):
        return _scan_python_fallback(text, path)

    lines = text.splitlines()
    statements: list[dict] = []   # {name, value, start, numbers, comments, allow, string_only}
    cur: dict | None = None
    depth = 0
    for tok in toks:
        tt, s, (row, _), _, _ = tok
        if tt in (tokenize.ENCODING, tokenize.INDENT, tokenize.DEDENT, tokenize.NL):
            continue
        if tt == tokenize.ENDMARKER:
            break
        if cur is None:
            if tt == tokenize.COMMENT:
                # An indented comment right after a statement continues that
                # statement's comment (a dataclass field's wrapped note).
                if statements and tok[2][1] > 0:
                    statements[-1]["comments"].append((row, s, False))
                    if ALLOW in s:
                        statements[-1]["allow"] = True
                continue
            cur = {"name": None, "value": "", "start": row, "numbers": False,
                   "comments": [], "allow": False, "string_only": tt == tokenize.STRING,
                   "text": "", "toks": [], "seen_eq": False}
        if tt == tokenize.NEWLINE:
            statements.append(cur)
            cur = None
            depth = 0
            continue
        if tt == tokenize.COMMENT:
            on_code_line = any(t[2][0] == row for t in cur["toks"])
            cur["comments"].append((row, s, on_code_line))
            if ALLOW in s:
                cur["allow"] = True
            continue
        if tt != tokenize.STRING:
            cur["string_only"] = False
        cur["toks"].append(tok)
        if tt == tokenize.OP and s in "([{":
            depth += 1
        elif tt == tokenize.OP and s in ")]}":
            depth -= 1
        if tt == tokenize.NUMBER and cur["seen_eq"]:
            cur["numbers"] = True
        if tt == tokenize.OP and s == "=" and depth == 0 and not cur["seen_eq"]:
            cur["seen_eq"] = True
            first = cur["toks"][0]
            if first[0] == tokenize.NAME:
                cur["name"] = first[1]
                eq_end = tok[3]
                cur["value"] = lines[eq_end[0] - 1][eq_end[1]:].split("#")[0].strip()

    for i, st in enumerate(statements):
        if st["name"] is None or not st["numbers"] or st["allow"]:
            continue
        led = False   # a comment-only line continues the comment above it
        for row, c, on_code in st["comments"]:
            body = c.lstrip("#")
            if on_code or not led:
                led = bool(DESIGN_LED.match(body))
            if not led and _suspect(c):
                findings.append(Finding(path, row, st["name"], st["value"], body.strip()))
        nxt = statements[i + 1] if i + 1 < len(statements) else None
        if nxt and nxt["string_only"] and nxt["toks"]:
            doc = nxt["toks"][0][1]
            if TAG_WORD.search(doc) and ALLOW not in doc:
                findings.append(Finding(path, nxt["toks"][0][2][0], st["name"], st["value"],
                                        "docstring: " + TAG_WORD.search(doc).group(0)))
    return findings


_ASSIGN_LINE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?::[^=]*)?=(?!=)\s*(.*?)\s*#(.*)$")


def _scan_python_fallback(text: str, path: Path) -> list[Finding]:
    out = []
    for i, raw in enumerate(text.splitlines(), 1):
        m = _ASSIGN_LINE.match(raw)
        if m and HAS_NUMBER.search(m.group(2)) and _suspect(m.group(3)):
            out.append(Finding(path, i, m.group(1), m.group(2), m.group(3).strip()))
    return out


def scan_data(text: str, path: Path) -> list[Finding]:
    out = []
    for i, raw in enumerate(text.splitlines(), 1):
        if ALLOW in raw or not TAG_WORD.search(raw) or not HAS_NUMBER.search(raw):
            continue
        if path.suffix != ".csv" and not DATA_LINE.search(raw):
            continue
        key = raw.split("=")[0].split(":")[0].strip().strip('"') or path.stem
        out.append(Finding(path, i, key, "<value>", raw.strip()[:80]))
    return out


def scan_text(text: str, path: Path) -> list[Finding]:
    return scan_python(text, path) if path.suffix == ".py" else scan_data(text, path)


def scan(root: Path) -> list[Finding]:
    root = root.resolve()
    findings: list[Finding] = []
    for p, rel in _files(root):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        findings.extend(scan_text(text, rel))
    return findings


def scan_staged(root: Path) -> list[Finding]:
    root = root.resolve()
    r = subprocess.run(["git", "-C", str(root), "diff", "--cached", "--name-only",
                        "--diff-filter=ACMR", "-z"], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"components lint: git diff --cached failed: {r.stderr.strip()}", file=sys.stderr)
        return []
    findings: list[Finding] = []
    for name in filter(None, r.stdout.split("\0")):
        rel = Path(name)
        if rel.suffix not in {".py", *DATA_SUFFIXES} or _skip_path(rel):
            continue
        if any(_is_lib_dir(root / Path(*rel.parts[:i + 1])) for i in range(len(rel.parts) - 1)):
            continue
        show = subprocess.run(["git", "-C", str(root), "show", f":{name}"],
                              capture_output=True, text=True, errors="replace")
        if show.returncode == 0:
            findings.extend(scan_text(show.stdout, rel))
    return findings


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    staged = "--staged" in argv
    argv = [a for a in argv if a != "--staged"]
    root = Path(argv[0]) if argv else Path(".")
    if not root.is_dir():
        print(f"components lint: not a directory: {root}", file=sys.stderr)
        return 2
    findings = scan_staged(root) if staged else scan(root)
    if not findings:
        return 0
    print("components lint: measured values live in the components package, not here.")
    for f in findings:
        print(f"{f.file}:{f.line}: {f.name} = {f.value}  # {f.comment}")
        print(f"    run instead:  {f.command()}")
        print("    then import it from the components package"
              f" (or mark it `# {ALLOW}` if it is not one).")
    print(f"{len(findings)} measured constant(s) outside the lib. Commit refused.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
