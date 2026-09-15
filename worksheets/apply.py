"""Apply a filled measurement worksheet: one `components measure` per row with a value.

    python worksheets/apply.py worksheets/bourns_3590s/sheet.csv --by JR [--dry]

Rows with an empty `measured_mm` are skipped and listed. A row whose `note`
starts with `DATASHEET <url>` is recorded with that provenance instead of a
caliper. Each successful row is one commit, one tag; the CLI's own guards
(clean clone, fetch, fast-forward) apply per row.
"""
from __future__ import annotations
import argparse, csv, subprocess, sys

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sheet"); ap.add_argument("--by", required=True); ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    done, skipped, failed = [], [], []
    with open(a.sheet, newline="") as f:
        for r in csv.DictReader(f):
            v = (r.get("measured_mm") or "").strip()
            if not v:
                skipped.append(f"{r['letter']} {r['part']}.{r['const']}"); continue
            cmd = [sys.executable, "-m", "components", "measure", r["part"], r["const"], v, "--by", a.by]
            note = (r.get("note") or "").strip()
            if note.upper().startswith("DATASHEET "):
                cmd += ["--datasheet", note.split(None, 1)[1]]
            print("+", " ".join(cmd[2:]))
            if a.dry: continue
            p = subprocess.run(cmd, text=True, capture_output=True)
            (done if p.returncode == 0 else failed).append(f"{r['letter']} {r['part']}.{r['const']} = {v}"
                                                            + ("" if p.returncode == 0 else f"  <- {p.stderr.strip() or p.stdout.strip()}"))
            if p.returncode != 0:
                print("  stop: fix the row above and rerun; rows already applied are committed", file=sys.stderr); break
    print(f"\napplied {len(done)}, skipped {len(skipped)} (no value), failed {len(failed)}")
    for s in skipped: print("  blank:", s)
    for s in failed: print("  FAILED:", s)
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
