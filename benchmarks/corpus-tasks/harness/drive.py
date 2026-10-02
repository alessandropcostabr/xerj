#!/usr/bin/env python3
"""Run one corpus's full suite (all tasks x both arms) and write RESULTS.md.

Usage: drive.py <slug> [<slug>...]        (suite must exist in tasks/<slug>.json)
Parallelism: 4 concurrent single runs (matching the pilot's batch shape).
Skips tasks whose runs already have grade lines, so re-invocation resumes.
"""
import json, pathlib, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).resolve().parents[1]

def run_one(args):
    slug, tid, arm = args
    run_dir = HERE / "runs" / slug / f"{tid}-{arm}"
    g = run_dir / "grade.json"
    if g.exists():
        return json.loads(g.read_text())
    r = subprocess.run(["bash", str(HERE / "harness" / "run.sh"), slug, tid, arm],
                       capture_output=True, text=True, timeout=900)
    line = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "{}"
    try:
        grade = json.loads(line)
    except json.JSONDecodeError:
        grade = {"task": tid, "arm": arm, "pass": False, "error": line[:300],
                 "rc": r.returncode, "stderr": r.stderr[-300:]}
    grade["task"] = tid
    g.write_text(json.dumps(grade))
    return grade

def drive(slug):
    suite_p = HERE / "tasks" / f"{slug}.json"
    if not suite_p.exists():
        print(f"{slug}: NO SUITE"); return
    suite = json.loads(suite_p.read_text())
    tasks = suite["tasks"]
    if len(tasks) < 4:
        out = HERE / "runs" / slug / "RESULTS.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(f"# {slug} — suite infeasible (mechanical)\n\n"
                       f"Generator produced {len(tasks)} tasks from the pinned clone "
                       f"(no minable constants in this corpus's file types). "
                       f"Left for hand-written task design; not counted as a run.\n")
        print(f"{slug}: INFEASIBLE ({len(tasks)} tasks)"); return
    jobs = [(slug, t["id"], a) for t in tasks for a in ("p", "x")]
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=4) as ex:
        grades = list(ex.map(run_one, jobs))
    rollup(slug, suite, grades)
    print(f"{slug}: done in {int(time.time()-t0)}s")

def rollup(slug, suite, grades):
    rows = {"p": [], "x": []}
    for g in grades:
        rows.setdefault(g.get("arm"), []).append(g)
    def agg(a):
        rs = rows.get(a, [])
        n = len(rs)
        solved = sum(1 for g in rs if g.get("pass"))
        cost = sum(g.get("cost_usd") or 0 for g in rs)
        secs = sum(g.get("seconds") or 0 for g in rs)
        turns = sum(g.get("turns") or 0 for g in rs)
        calls = sum(g.get("xerj_calls") or 0 for g in rs)
        return solved, n, cost, secs, turns, calls
    p, x = agg("p"), agg("x")
    n_d = sum(1 for t in suite["tasks"] if t["class"] == "drift")
    drift_p = [g["task"] for g in rows["p"] if g.get("pass")]
    drift_ids = {t["id"] for t in suite["tasks"] if t["class"] == "drift"}
    dp = sum(1 for t in drift_p if t in drift_ids); dn = len(drift_ids)
    out = [f"# {slug} — RESULTS ({suite.get('generated','?')})", "",
           f"Suite: `tasks/{slug}.json`, {len(suite['tasks'])} tasks "
           f"({n_d} drift-anchored, {len(suite['tasks'])-n_d} state), "
           f"pin `{suite['pin']}`. Generated + graded from the pinned clone.", "",
           "| arm | solved | cost | wall | turns | corpus calls |",
           "|-----|--------|------|------|-------|--------------|",
           f"| P (bare) | **{p[0]}/{p[1]}** | ${p[2]:.2f} | {p[3]} s | {p[4]} | {p[5]} |",
           f"| X (corpus+XERJ) | **{x[0]}/{x[1]}** | ${x[2]:.2f} | {x[3]} s | {x[4]} | {x[5]} |",
           "", f"Drift-anchored subset: P {dp}/{dn}, X "
               f"{sum(1 for g in rows['x'] if g.get('pass') and g['task'] in drift_ids)}/{dn}.",
           "", "## Per-task", "",
           "| task | class | kind | P | X | X calls |", "|------|-------|------|---|---|---------|"]
    kinds = {t["id"]: (t["class"], t.get("kind", "")) for t in suite["tasks"]}
    TRIVIAL = {0, 1, 2, 4, 8, 16, 32, 64, 100, 128, 256, 512, 1024, 4096, 65536}
    for t in suite["tasks"]:
        gp = next((g for g in rows["p"] if g["task"] == t["id"]), {})
        gx = next((g for g in rows["x"] if g["task"] == t["id"]), {})
        try:
            trivial = int(t["re"][0].split("|")[0], 0) in TRIVIAL
        except ValueError:
            trivial = False
        flag = " ⚠️guessable" if trivial and gp.get("pass") else ""
        out.append(f"| {t['id']} | {kinds[t['id']][0]} | {kinds[t['id']][1]} | "
                   f"{'✅' if gp.get('pass') else '❌'}{flag} | {'✅' if gx.get('pass') else '❌'} | "
                   f"{gx.get('xerj_calls', 0)} |")
    out += ["", "Grades: `runs/%s/grades.jsonl` (one JSON per run in T<n>-<arm>/grade.json)." % slug, ""]
    d = HERE / "runs" / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / "RESULTS.md").write_text("\n".join(out))
    with open(d / "grades.jsonl", "w") as f:
        for g in grades:
            f.write(json.dumps(g) + "\n")

if __name__ == "__main__":
    for slug in sys.argv[1:]:
        drive(slug)
