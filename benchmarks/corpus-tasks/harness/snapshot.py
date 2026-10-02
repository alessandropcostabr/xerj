#!/usr/bin/env python3
"""Emit the hub-site impact snapshot JSON from runs/ state.

Usage: snapshot.py OUT.json
Reuses report.py's slug_row (single source of truth for statuses/scores).
The snapshot is dated + commit-stamped so the site can cite it honestly.
"""
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "harness"))
import report  # noqa: E402  (slug_row, UNIVERSE)

prov = {
    "date": "2026-10-02",
    "repo": "benchmarks/corpus-tasks",
    "branch": "bench/corpus-tasks",
    "protocol": "benchmarks/corpus-tasks/PROTOCOL.md",
    "commit": subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=HERE,
                             capture_output=True, text=True).stdout.strip(),
    "note": "P = bare offline arm (instructed to answer honestly, not fabricate); "
            "X = same agent with this corpus served via xerj code. Ties are recorded, not hidden.",
}
rows = []
for slug in report.UNIVERSE:
    if slug == "rust-vulns":
        rows.append({"corpus": slug, "status": "cited-#1111"})
    else:
        rows.append({"corpus": slug, **(report.slug_row(slug) or {"status": "queued"})})
pathlib.Path(sys.argv[1]).write_text(json.dumps({"provenance": prov, "rows": rows}, indent=1) + "\n")
states = {}
for r in rows:
    states[r["status"]] = states.get(r["status"], 0) + 1
print(f"wrote {sys.argv[1]}: {len(rows)} rows; " + ", ".join(f"{k}={v}" for k, v in sorted(states.items())))
