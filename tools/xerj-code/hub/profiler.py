#!/usr/bin/env python3
"""Corpus intake profiler — gate G1/G3/G4 evidence gathering (PROGRAM-100.md §2).

Turns a backlog row into a DRAFT manifest with the pin pinned, the size counted
and the licence evidence the reviewer must open quoted into the note. Deliberately
stdlib + `git` subprocess only, like validate_hub.py: nothing to supply-chain.

  python3 tools/xerj-code/hub/profiler.py <slug>...     # profile backlog rows
  python3 tools/xerj-code/hub/profiler.py --check       # drift report, live manifests

Design rule: drafts land in hub/drafts/<slug>.json, NEVER hub/<slug>.json.
A draft carries review.use = "UNREVIEWED", which validate_hub.py rejects — so a
draft cannot reach the registry unreviewed by accident. After the human opens the
licence file(s) at the pin and fills the review block, the draft moves to
hub/<slug>.json and goes out in the wave PR.

What the profiler does NOT do: decide anything. Licence heuristics are hints for
the reviewer (our detector has been wrong in both directions — it once read
Elasticsearch as Apache-2.0); size and file counts are facts; the domain test
(G1) and the un-memorisation test (G3) stay human judgements recorded in the
backlog.
"""
from __future__ import annotations

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
                 "COPYING", "COPYING.txt", "COPYRIGHT", "NOTICE")
# SPDX hints, longest-first so "Apache-2.0" beats "Apache". Evidence, not verdicts.
_SPDX_HINTS = [
    ("Apache-2.0", r"apache license\s*(version)?\s*2"),
    ("Apache-1.1", r"apache license\s*(version)?\s*1\.1"),
    ("GPL-3.0", r"gnu general public license.*version 3"),
    ("GPL-2.0", r"gnu general public license.*version 2"),
    ("LGPL-2.1", r"gnu lesser general public license"),
    ("LGPL-3.0", r"lesser general public.*version 3"),
    ("MPL-2.0", r"mozilla public license\s*(version)?\s*2"),
    ("AGPL-3.0", r"gnu affero general public license"),
    ("SSPL-1.0", r"server side public license"),
    ("BUSL-1.1", r"business source license"),
    ("RSALv2", r"redis source available license"),
    ("MIT", r"permission is hereby granted, free of charge"),
    ("BSD-3", r"redistribution and use in source and binary forms.*neither the name"),
    ("BSD-2", r"redistribution and use in source and binary forms"),
    ("ISC", r"isc license|permission to use, copy, modify"),
    ("CC-BY-4.0", r"creative commons attribution 4\.0"),
    ("CC-BY-SA-4.0", r"creative commons attribution-sharealike 4\.0"),
    ("Unlicense", r"this is free and unencumbered software released into the public domain"),
    ("PostgreSQL", r"postgresql database management system"),
    ("zlib", r"zlib license"),
    ("Boost-BSL-1.0", r"boost software license"),
    ("Curl", r"curl licence|curl license"),
    ("MPL-1.1", r"mozilla public license\s*(version)?\s*1\.1"),
]


def run(cmd: list[str], cwd: pathlib.Path | None = None) -> str:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)}\n{p.stderr.strip()}")
    return p.stdout.strip()


def http_head_ok(url: str) -> bool:
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=15) as r:
            return 200 <= r.status < 400
    except Exception:
        return False


def spdx_hint(text: str) -> str:
    low = text.lower()
    for spdx, pat in _SPDX_HINTS:
        if re.search(pat, low):
            return spdx
    return "UNKNOWN"


def profile_git(url: str, slug: str) -> dict:
    """Shallow-clone the source, return pin/size/licence-evidence facts."""
    work = CACHE / slug
    if work.exists():
        shutil.rmtree(work)
    work.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "clone", "--depth", "1", "--filter=blob:none", "--no-tags",
         url, str(work)])
    sha = run(["git", "rev-parse", "HEAD"], cwd=work)
    files = run(["git", "ls-files"], cwd=work).splitlines()
    total = 0
    for f in files:
        try:
            total += (work / f).stat().st_size
        except OSError:
            pass
    lic_files = [f for f in files
                 if f.count("/") == 0 and f.upper() in LICENSE_NAMES]
    evidence = []
    for f in lic_files:
        text = (work / f).read_text(errors="replace")[:4000]
        evidence.append({"file": f, "spdx_hint": spdx_hint(text),
                         "first_lines": "\n".join(
                             ln for ln in text.splitlines()
                             if ln.strip())[:3]})
    return {"sha": sha, "files": len(files), "bytes": total,
            "licence_evidence": evidence or "NO TOP-LEVEL LICENCE FILE FOUND — investigate before review"}


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "--check":
        return check_drift()

    backlog = json.loads(BACKLOG.read_text())
    rows = {r["slug"]: r for r in backlog["corpora"]}
    now = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rc = 0
    for slug in argv:
        row = rows.get(slug)
        if row is None:
            print(f"{slug}: not in {BACKLOG}"); rc = 1; continue
        git_rows = [s for s in row["sources"]
                    if s["url"].startswith("https://github.com/")
                    or s["url"].startswith("https://git.")]
        if not git_rows:
            print(f"{slug}: no git source to profile (recipe/intake row — "
                  "hand-write the draft per CONTRIBUTING.md lane picker)"); rc = 1; continue
        facts = profile_git(git_rows[0]["url"], slug)
        hint = git_rows[0].get("licence_hint", "")
        note = (f"PROFILER {now} — files={facts['files']} bytes={facts['bytes']}; "
                f"backlog hint: {hint}; evidence: ")
        if isinstance(facts["licence_evidence"], str):
            note += facts["licence_evidence"]
        else:
            note += "; ".join(f"{e['file']} looks like {e['spdx_hint']}"
                              for e in facts["licence_evidence"])
        draft = {
            "corpus": slug,
            "cloned_at": now,
            "repos": [{
                "repo": slug,
                "url": git_rows[0]["url"],
                "licence": f"hint only: {hint}",
                "sha": facts["sha"],
                "files": facts["files"],
                "bytes": facts["bytes"],
                "review": {
                    "spdx": "UNREVIEWED",
                    "use": "UNREVIEWED",
                    "by": "", "at": "",
                    "note": note[:2000],
                },
            }],
        }
        out = DRAFTS / f"{slug}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(draft, indent=2) + "\n")
        ev = facts["licence_evidence"]
        ev_s = ("NO LICENCE FILE" if isinstance(ev, str)
                else ", ".join(f"{e['file']}→{e['spdx_hint']}" for e in ev))
        print(f"{slug}: pinned {facts['sha'][:12]} · {facts['files']} files · "
              f"{facts['bytes']:,} B · {ev_s}\n  draft → {out.relative_to(ROOT)}")
        shutil.rmtree(CACHE / slug, ignore_errors=True)
    return rc


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


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
