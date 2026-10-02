#!/usr/bin/env python3
"""Corpus intake profiler — gate G1/G3/G4 evidence gathering (PROGRAM-100.md §2).

Turns backlog rows into DRAFT manifests with the pin pinned, the size counted
and the licence evidence the reviewer must open quoted into the note. Deliberately
stdlib + `git` subprocess only (plus `gh api` opportunistically, for the size
estimate when authenticated): nothing to supply-chain.

  python3 tools/xerj-code/hub/profiler.py <slug>...        # profile rows
  python3 tools/xerj-code/hub/profiler.py --all [--cats DATA,NET]
  python3 tools/xerj-code/hub/profiler.py --check          # drift report

Bulk mode (--all) is trees-only: `git clone --depth 1 --filter=blob:none
--no-checkout` fetches commit+trees (a few MB even for llvm-scale repos), file
counts come from `git ls-tree -r`, the licence file is read via a single lazy
`git show HEAD:<file>` blob fetch, and the byte count is the GitHub API's repo
size estimate (labelled as an estimate in the manifest — it is the pack size,
not a checkout du). Working-tree checkouts of 70+ engines would be tens of GB
and hours; trees-only is minutes.

Design rule: drafts land in hub/drafts/<slug>.json, NEVER hub/<slug>.json.
A draft carries review.use = "UNREVIEWED", which validate_hub.py rejects — so a
draft cannot reach the registry unreviewed by accident. After the human opens
the licence file(s) at the pin and fills the review block, the draft moves to
hub/<slug>.json and goes out in the wave PR.

What the profiler does NOT do: decide anything. Licence heuristics are hints
for the reviewer (our detector has been wrong in both directions — it once read
Elasticsearch as Apache-2.0); the GitHub API's licence detection is a second
hint, not a verdict; the domain test (G1) and un-memorisation test (G3) stay
human judgements recorded in the backlog.
"""
from __future__ import annotations

import concurrent.futures as cf
import datetime as _dt
import json
import pathlib
import re
import shutil
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[3]
HUB = ROOT / "tools" / "xerj-code" / "hub"
BACKLOG = HUB / "backlog" / "backlog-100.json"
DRAFTS = HUB / "drafts"
CACHE = pathlib.Path.home() / ".xerj-code" / "hub-profiling"

LICENSE_NAMES = ("LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "LICENCE.md",
                 "LICENSE-MIT", "LICENSE-APACHE", "COPYING", "COPYING.txt",
                 "COPYING.LESSER", "COPYRIGHT", "NOTICE", "license.txt")
# SPDX hints, longest-first so "Apache-2.0" beats "Apache". Evidence, not verdicts.
_SPDX_HINTS = [
    ("Apache-2.0", r"apache license\s*(version)?\s*2"),
    ("Apache-1.1", r"apache license\s*(version)?\s*1\.1"),
    ("GPL-3.0", r"gnu general public license.*version 3|gplv3"),
    ("GPL-2.0", r"gnu general public license.*version 2|gplv2"),
    ("LGPL-2.1", r"gnu lesser general public license"),
    ("LGPL-3.0", r"lesser general public.*version 3"),
    ("MPL-2.0", r"mozilla public license\s*(version)?\s*2"),
    ("AGPL-3.0", r"gnu affero general public license|affero gpl"),
    ("SSPL-1.0", r"server side public license"),
    ("BUSL-1.1", r"business source license"),
    ("RSALv2", r"redis source available license"),
    ("Elastic-2.0", r"elastic license\s*2"),
    ("MIT", r"permission is hereby granted, free of charge"),
    ("BSD-3", r"redistribution and use in source and binary forms.*neither the name"),
    ("BSD-2", r"redistribution and use in source and binary forms"),
    ("ISC", r"isc license|permission to use, copy, modify"),
    ("CC-BY-4.0", r"creative commons attribution 4\.0"),
    ("CC-BY-SA-4.0", r"creative commons attribution-sharealike 4\.0"),
    ("CC-BY-SA-3.0", r"creative commons attribution-sharealike 3"),
    ("Unlicense", r"this is free and unencumbered software released into the public domain"),
    ("PostgreSQL", r"postgresql database management system"),
    ("zlib", r"zlib license"),
    ("Boost-BSL-1.0", r"boost software license"),
    ("Curl", r"curl licence|curl license"),
    ("Unicode-3.0", r"unicode license v3|unicode, inc\. license"),
    ("OpenLDAP", r"openldap public license"),
    ("MPL-1.1", r"mozilla public license\s*(version)?\s*1\.1"),
]
# Verdicts the G4 reviewer must NOT wave through as adapt-with-attribution.
_RESTRICTED = {"AGPL-3.0", "SSPL-1.0", "BUSL-1.1", "RSALv2", "Elastic-2.0",
               "GPL-2.0", "GPL-3.0", "LGPL-2.1", "LGPL-3.0", "CC-BY-SA-4.0",
               "CC-BY-SA-3.0"}


def run(cmd: list[str], cwd: pathlib.Path | None = None,
        timeout: int = 300) -> str:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                       timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)}\n{p.stderr.strip()[:400]}")
    return p.stdout.strip()


def gh_api(repo: str) -> dict:
    """repo = 'owner/name' → {size_kb, license_spdx, default_branch} via gh."""
    try:
        out = subprocess.run(["gh", "api", f"repos/{repo}", "--cache", "1h"],
                             capture_output=True, text=True, timeout=30)
        if out.returncode == 0:
            d = json.loads(out.stdout)
            lic = (d.get("license") or {}).get("spdx_id") or "None"
            return {"size_kb": d.get("size", 0), "license_spdx": lic,
                    "default_branch": d.get("default_branch", "")}
    except Exception:
        pass
    return {"size_kb": 0, "license_spdx": "unknown", "default_branch": ""}


def github_repo_of(url: str) -> str | None:
    m = re.match(r"https://github\.com/([\w.-]+/[\w.-]+?)(?:\.git)?/?$", url)
    return m.group(1) if m else None


def spdx_hint(text: str) -> str:
    low = text.lower()
    for spdx, pat in _SPDX_HINTS:
        if re.search(pat, low):
            return spdx
    return "UNKNOWN"


def profile_git(url: str, slug: str) -> dict:
    """Trees-only profile of one source: pin, file count, licence text."""
    work = CACHE / f"{slug}-{re.sub(r'[^a-z0-9]', '', url[-12:].lower())}"
    if work.exists():
        shutil.rmtree(work)
    work.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "clone", "--depth", "1", "--filter=blob:none", "--no-checkout",
         "--no-tags", url, str(work)], timeout=600)
    sha = run(["git", "rev-parse", "HEAD"], cwd=work)
    files = run(["git", "ls-tree", "-r", "--name-only", "HEAD"], cwd=work,
                timeout=300).splitlines()
    top = {f for f in files if "/" not in f}
    lic_paths = sorted(top.intersection(LICENSE_NAMES))
    # a couple of common subdirectory licences for monorepos, best effort
    if not lic_paths:
        for d in ("LICENSES/", "docs/"):
            cand = [f for f in files if f.startswith(d)
                    and pathlib.Path(f).name.upper() in LICENSE_NAMES]
            if cand:
                lic_paths = cand[:3]
                break
    evidence = []
    for f in lic_paths[:4]:
        try:
            text = run(["git", "show", f"HEAD:{f}"], cwd=work, timeout=120)
        except Exception:
            continue
        evidence.append({"file": f, "spdx_hint": spdx_hint(text[:4000]),
                         "head": "\n".join(ln for ln in text.splitlines()
                                           if ln.strip())[:2]})
    return {"sha": sha, "files": len(files), "top_files": sorted(top)[:25],
            "licence_evidence": evidence
            or "NO TOP-LEVEL LICENCE FILE FOUND — investigate before review"}


def manifest_draft(slug: str, row: dict, now: str) -> tuple[str, str]:
    """Profile all git sources of a row; write the draft. → (status_line, 'ok'|'fail')."""
    git_rows = [s for s in row["sources"]
                if s["url"].startswith(("https://github.com/", "https://git.",
                                        "https://gitlab.com/"))]
    if not git_rows:
        return (f"{slug}: no git source (recipe/intake row — hand-draft per "
                f"CONTRIBUTING.md lane picker)", "skip")
    repos = []
    facts_summary = []
    for i, s in enumerate(git_rows):
        src_slug = f"{slug}" if len(git_rows) == 1 else f"{slug}-{i + 1}"
        try:
            facts = profile_git(s["url"], src_slug)
        except Exception as e:
            return (f"{slug}: PROFILE FAILED {s['url']}: {str(e)[:200]}", "fail")
        api = gh_api(github_repo_of(s["url"]) or "")
        bytes_est = api["size_kb"] * 1024 if api["size_kb"] else 0
        ev = facts["licence_evidence"]
        if isinstance(ev, str):
            ev_s, ev_list = ev, []
        else:
            ev_list = ev
            ev_s = "; ".join(f"{e['file']}→{e['spdx_hint']}" for e in ev)
        hint = s.get("licence_hint", "")
        note = (f"PROFILER {now} trees-only — files={facts['files']}"
                f"{f' bytes≈{bytes_est:,} (GitHub pack-size ESTIMATE)' if bytes_est else ''}; "
                f"backlog hint: {hint}; api licence: {api['license_spdx']}; "
                f"evidence: {ev_s}")
        if api.get("license_spdx") not in ("None", "unknown", None):
            note += f"; GH-API-DETECTED: {api['license_spdx']}"
        repos.append({
            "repo": src_slug,
            "url": s["url"],
            "licence": f"hint only: {hint}",
            "sha": facts["sha"],
            "files": facts["files"],
            "bytes": bytes_est,
            "review": {"spdx": "UNREVIEWED", "use": "UNREVIEWED",
                       "by": "", "at": "", "note": note[:2000]},
        })
        facts_summary.append(f"{src_slug} {facts['sha'][:10]} "
                             f"{facts['files']}f {ev_s[:60]}")
        shutil.rmtree(CACHE / src_slug, ignore_errors=True)
    draft = {"corpus": slug, "cloned_at": now, "repos": repos}
    out = DRAFTS / f"{slug}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(draft, indent=2) + "\n")
    return (f"{slug}: {' | '.join(facts_summary)} → draft {out.relative_to(ROOT)}",
            "ok")


def check_drift() -> int:
    """W-B freshness pass: every live manifest vs its remote HEAD."""
    drifted = 0
    for path in sorted(HUB.glob("*.json")):
        if path.name in ("TEMPLATE.json",):
            continue
        data = json.loads(path.read_text())
        for r in data.get("repos", []):
            url, pinned = r["url"], r.get("sha", "")
            if not pinned:
                continue
            try:
                head = run(["git", "ls-remote", url, "HEAD"]).split()[0]
            except Exception as e:
                print(f"{path.stem}: ls-remote FAILED for {url}: {e}")
                drifted += 1
                continue
            if head != pinned:
                print(f"{path.stem}: DRIFT {url} pinned {pinned[:12]} head {head[:12]}")
                drifted += 1
    print(f"drift check: {drifted} source(s) moved or unreachable")
    return 0 if drifted == 0 else 1


def main(argv: list[str]) -> int:
    args = list(argv)
    if not args:
        print(__doc__)
        return 2
    if args[0] == "--check":
        return check_drift()

    backlog = json.loads(BACKLOG.read_text())
    rows = {r["slug"]: r for r in backlog["corpora"]}
    cats = None
    if args[0] == "--all":
        cats = None
        if len(args) > 1 and args[1].startswith("--cats="):
            cats = set(args[1].split("=", 1)[1].split(","))
        targets = [r for r in backlog["corpora"]
                   if r["status"] in ("candidate", "planned")
                   and r["lane"] == "A"
                   and (cats is None or r["cat"] in cats)]
    else:
        missing = [s for s in args if s not in rows]
        if missing:
            print(f"not in backlog: {missing}")
            return 1
        targets = [rows[s] for s in args]

    now = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    results, rc = [], 0
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(manifest_draft, r["slug"], r, now): r["slug"]
                for r in targets}
        for fut in cf.as_completed(futs):
            try:
                line, status = fut.result()
            except Exception as e:
                line, status = f"{futs[fut]}: UNEXPECTED {e}", "fail"
            results.append((futs[fut], status, line))

    for slug, status, line in sorted(results):
        print(("  FAIL " if status == "fail" else "  skip " if status == "skip"
                else "  ok   ") + line)
        if status == "fail":
            rc = 1
    ok = sum(1 for _, s, _ in results if s == "ok")
    print(f"\nprofiled {ok} ok, "
          f"{sum(1 for _, s, _ in results if s == 'fail')} failed, "
          f"{sum(1 for _, s, _ in results if s == 'skip')} skipped "
          f"(no git source) of {len(targets)} targets")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
