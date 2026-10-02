#!/usr/bin/env python3
"""Generate a 10-task drift-anchored suite for one hub corpus.

Task classes:
  drift — a literal (constant/define/const) whose VALUE changed in the repo's
          recent history (default window: 2024-01-01..pin). The bare arm can
          only answer from memory; if the change postdates the model's
          training data it serves the OLD value and fails. The corpus arm
          retrieves the value at the pin.
  state — a literal's current value at HEAD (fallback when the window yields
          fewer than 10 drift facts). May tie on memorised content — that is
          measured, not hidden; each task carries its class.

Ground truth is mechanical: the value in the working tree at the pin.
"""
import json, pathlib, re, subprocess, sys

HUB = pathlib.Path("/root/hub-branch/tools/xerj-code/hub")
CORPORA = pathlib.Path.home() / ".xerj-code" / "corpora"
HERE = pathlib.Path(__file__).resolve().parents[1]

ASSIGN = re.compile(
    r'^[-+]\s*(?:#\s*define\s+|pub\s+const\s+|const\s+|public\s+const\s+|static\s+const\s+)'
    r'([A-Z][A-Z0-9_]{4,})\b[^=]*=\s*([^,;\s]+)[,;\s]|'
    r'^[-+]\s*(?:#\s*define\s+)([A-Z][A-Z0-9_]{4,})\s+(-?0x[0-9a-fA-F]+|-?\d+|"[^"]*")'
    r'\s*$')

def run(cmd, cwd=None, timeout=300):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return ""  # drift is best-effort; state tasks still fill the suite
    return p.stdout if p.returncode == 0 else ""

def repo_dirs(slug):
    base = CORPORA / slug
    if not base.exists():
        return []
    out = []
    for d in sorted(base.iterdir()):
        if d.is_dir() and (d / ".git").exists():
            out.append(d)
        else:  # nested one level (manifest repo-name dirs)
            for dd in sorted(d.iterdir()) if d.is_dir() else []:
                if dd.is_dir() and (dd / ".git").exists():
                    out.append(dd)
    return out


DEF_RE = re.compile(
    r'^\s*#\s*define\s+([A-Z][A-Z0-9_]{4,})\s+\(?\s*(-?0x[0-9a-fA-F]+[ULul]*|-?\d[\d_]*[ULul]*|"[^"]{1,60}")\s*\)?\s*(?:/\*.*\*/)?\s*$')
RS_RE = re.compile(
    r'^\s*(?:pub\s+)?(?:const|static)\s+([A-Z][A-Z0-9_]{4,})\s*:[^=]+?=\s*(-?0x[0-9a-fA-F]+|-?\d[\d_]*|"[^"]{1,60}")\s*;')
CPP_RE = re.compile(  # Google style: static const int kNumShardBits = 4;
    r'^\s*(?:static\s+)?(?:const|constexpr)\s+[A-Za-z_][\w:<>,\s]*?\s(k[A-Z][A-Za-z0-9]{2,})\s*=\s*(-?0x[0-9a-fA-F]+|-?\d[\d_]*|"[^"]{1,60}")\s*;')

JAVA_RE = re.compile(  # static final int MAX_FOO = 3;
    r'^\s*(?:public\s+|private\s+|protected\s+)?static\s+final\s+[A-Za-z_][\w<>\[\],.]*\s+([A-Z][A-Z0-9_]{3,})\s*=\s*(-?0x[0-9a-fA-F]+L?|-?\d+L?|"[^"]{1,60}")\s*;')
GO_VAL = r'(-?0x[0-9a-fA-F]+|-?\d+(?:\.\d+)?|"[^"]{1,60}")'
GO_LINE = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_]{5,})\s*=\s*' + GO_VAL + r'\s*$')
GO_CONST = re.compile(r'^\s*const\s+([A-Za-z_][A-Za-z0-9_]{5,})(?:\s+\w+)?\s*=\s*' + GO_VAL + r'\s*$')

def match_const(line, go_block=False):
    m = DEF_RE.match(line) or RS_RE.match(line) or CPP_RE.match(line) or JAVA_RE.match(line)
    if m:
        return m
    if go_block:
        return GO_LINE.match(line)
    return GO_CONST.match(line)

SKIP_DIRS = {"vendor", "third_party", "thirdparty", "node_modules", ".git", "test-data"}

def iter_files(work):
    n = 0
    for f in work.rglob("*"):
        if n > 6000:
            return
        if f.is_file() and f.suffix in (".c", ".h", ".cc", ".cpp", ".hpp", ".rs", ".go", ".java"):
            rel = f.relative_to(work).parts
            if not any(p.lower() in SKIP_DIRS for p in rel[:-1]):
                n += 1
                yield f

def parse_consts(work):
    cur = {}
    for f in iter_files(work):
        try:
            go = f.suffix == ".go"
            in_block = False
            for line in f.read_text(errors="ignore").splitlines()[:200000]:
                if go:
                    if re.match(r'^\s*const\s*\(', line):
                        in_block = True; continue
                    if in_block and re.match(r'^\)', line):
                        in_block = False; continue
                m = match_const(line, go_block=in_block)
                if m and not m.group(1).endswith(("import", "package", "return")):
                    cur.setdefault(m.group(1), (m.group(2), str(f.relative_to(work))))
        except OSError:
            pass
    return cur

def literals_at_head(work):
    return {k: v[0] for k, v in parse_consts(work).items()}

def drift_facts(work, since="2024-01-01", max_commits=400, consts=None):
    consts = consts if consts is not None else parse_consts(work)
    if not consts:
        return []
    names = re.compile("\\b(" + "|".join(re.escape(n) for n in list(consts)[:1500]) + ")\\b")
    log = run(["git", "log", "-E", f"--since={since}", f"--max-count={max_commits}",
               "--unified=0", "-G", r"#define|const |constexpr", "--format=COMMIT %cd",
               "--date=short", "-p"], cwd=work, timeout=600)
    facts, date = {}, None
    for line in log.splitlines():  # newest-first
        if line.startswith("COMMIT "):
            date = line.split()[-1]
            continue
        if line[:1] not in ("+", "-") or line.startswith(("+++", "---")):
            continue
        m = match_const(line[1:], go_block=True)
        if not m:
            continue
        name, val = m.group(1), m.group(2)
        if not names.search(line):
            continue
        f = facts.setdefault(name, [])
        if not f or f[-1][0] != val:
            f.append((val, date, line[0] == "+"))
    out = []
    for name, seq in facts.items():
        plus = [s for s in seq if s[2]]
        if not plus or name not in consts:
            continue
        cur, curdate = consts[name][0], plus[0][1]
        if consts[name][0] != plus[0][0]:
            continue  # HEAD value differs from window's newest: skip
        olds = {s[0] for s in seq if not s[2]} - {cur}
        if olds:
            out.append({"name": name, "cur": cur, "date": curdate,
                        "olds": sorted(olds)[:3], "kind": "changed"})
        elif all(s[2] for s in seq) and len(seq) == 1:
            # appears once, added, never removed: likely NEW in the window
            out.append({"name": name, "cur": cur, "date": curdate,
                        "olds": [], "kind": "added"})
    out.sort(key=lambda f: f["date"] or "", reverse=True)
    return out


def val_regex(v):
    if v.startswith('"'):
        return re.escape(v.strip('"'))[:60]
    esc = re.escape(v)
    try:
        n = int(v, 0)
        alts = {esc, re.escape(hex(n)), re.escape(str(n))}
        if n > 1024:
            alts.add(re.escape(f"{n//1024} ?[kK]")[0:40])  # rough, rarely used
        return "|".join(sorted(alts))
    except ValueError:
        return esc

def gen(slug):
    man = json.loads((HUB / f"{slug}.json").read_text())
    works = repo_dirs(slug)
    if not works:
        return None
    drift, state_pool = [], {}
    for w in works:
        consts = parse_consts(w)
        drift += [(w, f) for f in drift_facts(w, consts=consts)]
        state_pool.update({k: v[0] for k, v in consts.items()})
    tasks, seen = [], set()
    for w, f in drift[:10]:
        if f["name"] in seen:
            continue
        seen.add(f["name"])
        proj = man["repos"][0]["repo"] if len(man["repos"]) == 1 else w.name
        tasks.append({"id": f"T{len(tasks)+1}", "class": "drift", "name": f["name"],
                      "kind": f["kind"], "changed": f["date"], "olds": f["olds"],
                      "q": f"In the current development source of {proj}, what is the exact value of {f['name']}? Answer with the value only.",
                      "re": [val_regex(f["cur"])], "need": 1})
    if len(tasks) < 10:  # fill with state facts (current values, may memorise-tie)
        recent = {f["name"] for w, f in drift}
        pool = sorted(state_pool.items(),
                      key=lambda kv: (kv[0] not in recent, -len(kv[0])))
        for name, val in pool:
            if len(tasks) >= 10:
                break
            if name in seen or not re.match(r'^-?0x[0-9a-fA-F]+$|^-?\d+$|^"[^"]*"$', val):
                continue
            seen.add(name)
            proj = man["repos"][0]["repo"] if len(man["repos"]) == 1 else works[0].name
            tasks.append({"id": f"T{len(tasks)+1}", "class": "state", "name": name,
                          "q": f"In the current development source of {proj}, what is the exact value of {name}? Answer with the value only.",
                          "re": [val_regex(val)], "need": 1})
    suite = {"corpus": slug, "subject": man["repos"][0]["repo"] if man["repos"] else slug,
             "pin": man["repos"][0]["sha"][:10],
             "generated": "2026-10-02", "tasks": tasks[:10]}
    out = HERE / "tasks" / f"{slug}.json"
    out.write_text(json.dumps(suite, indent=1) + "\n")
    return suite

if __name__ == "__main__":
    for slug in sys.argv[1:]:
        s = gen(slug)
        if s:
            n_drift = sum(1 for t in s["tasks"] if t["class"] == "drift")
            print(f"{slug}: {len(s['tasks'])} tasks ({n_drift} drift, {len(s['tasks'])-n_drift} state)")
        else:
            print(f"{slug}: NO CLONE — run corpus add first")
