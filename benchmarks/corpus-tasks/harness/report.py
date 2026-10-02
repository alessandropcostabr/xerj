#!/usr/bin/env python3
"""71-row status+results table from runs/ state. Refresh any time.

Row source: tasks/<slug>.json + runs/<slug>/grades.jsonl when measured;
runs/<slug>/RESULTS.md first heading for non-run outcomes (infeasible,
pathological, demoted, cited); 'queued' otherwise.
"""
import json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parents[1]
RUNS, TASKS = HERE / "runs", HERE / "tasks"

# The 71-row universe is FIXED (snapshot at benchmark start, 2026-10-02):
# the 70 manifest stems present then + rust-vulns. Later hub additions (e.g.
# the non-IT lane) must not grow the denominator of an in-flight measurement.
UNIVERSE = sorted((HERE / "runs" / "universe-71.txt").read_text().split())
assert len(UNIVERSE) == 71, len(UNIVERSE)

def slug_row(slug):
    d = RUNS / slug
    if not (d / "RESULTS.md").exists():
        return None
    head = (d / "RESULTS.md").read_text().splitlines()[0]
    if "infeasible" in head:
        n = re.search(r"\d+", head.split("(")[-1])
        return {"status": f"infeasible({n.group(0) if n else '?'})"}
    if "pathological" in head:
        return {"status": "index-pathological"}
    if "not measured" in head or "demoted" in head:
        return {"status": "demoted-candidate"}
    gpath = d / "grades.jsonl"
    tpath = TASKS / f"{slug}.json"
    if not gpath.exists() or not tpath.exists():
        return {"status": "results-pending"}
    grades = [json.loads(l) for l in gpath.read_text().splitlines()]
    suite = json.loads(tpath.read_text())
    nd = sum(1 for t in suite["tasks"] if t["class"] == "drift")
    def agg(a):
        rs = [g for g in grades if g.get("arm") == a]
        return (sum(1 for g in rs if g.get("pass")), len(rs),
                sum(g.get("cost_usd") or 0 for g in rs),
                sum(g.get("xerj_calls") or 0 for g in rs))
    p, x = agg("p"), agg("x")
    drift_ids = {t["id"] for t in suite["tasks"] if t["class"] == "drift"}
    dp = sum(1 for g in grades if g.get("arm") == "p" and g.get("pass") and g["task"] in drift_ids)
    dx = sum(1 for g in grades if g.get("arm") == "x" and g.get("pass") and g["task"] in drift_ids)
    return {"status": "measured", "n": len(suite["tasks"]), "drift": nd,
            "p": f"{p[0]}/{p[1]}", "x": f"{x[0]}/{x[1]}", "pc": p[2], "xc": x[2],
            "calls": x[3], "dp": f"{dp}/{nd}" if nd else "-", "dx": f"{dx}/{nd}" if nd else "-"}

rows = []
for slug in UNIVERSE:
    if slug == "rust-vulns":
        rows.append((slug, {"status": "cited-#1111"})); continue
    rows.append((slug, slug_row(slug) or {"status": "queued"}))

states = {}
for _, r in rows:
    states[r["status"]] = states.get(r["status"], 0) + 1
w = max(len(s) for s, _ in rows)
print(f"{'corpus'.ljust(w)} | {'status'.ljust(18)} | suite      | drift P    | X          | P$     | X$     | Xcalls")
print("-" * 110)
for slug, r in rows:
    if r["status"] == "measured":
        print(f"{slug.ljust(w)} | {'MEASURED'.ljust(18)} | {str(r['n']).rjust(2)}t/{r['drift']:>2}d | {r['dp'].ljust(10)} | {r['x'].ljust(10)} | {r['pc']:>5.2f} | {r['xc']:>5.2f} | {r['calls']}")
    else:
        print(f"{slug.ljust(w)} | {r['status']}")
print("-" * 110)
print("states:", ", ".join(f"{k}={v}" for k, v in sorted(states.items())), f"| total={len(rows)}")
