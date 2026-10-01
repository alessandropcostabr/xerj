#!/usr/bin/env python3
"""Registry validation for the corpus-hub branch (§5 of CONTRIBUTING.md).

Checks every tools/xerj-code/hub/*.json manifest and every
tools/packs/*/recipe.toml against the registry's format rules. Deliberately
stdlib-only and engine-free: this is the fast gate a PR runs; the real
untrusted-input gate consumers use is `cargo test -p xerj-common
xccode::manifest`, which CI on main also runs over these files.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parents[3]
HUB = ROOT / "tools" / "xerj-code" / "hub"
PACKS = ROOT / "tools" / "packs"

LEGAL_USE = {"adapt-with-attribution", "approach-only", "mixed"}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")

errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


# ── Lane A: reference-corpus manifests ────────────────────────────────────
manifests = sorted(p for p in HUB.glob("*.json") if p.name != "TEMPLATE.json")
if not manifests:
    err("no hub manifests found — did the tree change shape?")

for path in manifests:
    rel = path.relative_to(ROOT)
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        err(f"{rel}: not valid JSON ({e})")
        continue

    name = data.get("corpus")
    if name != path.stem:
        err(f"{rel}: corpus field {name!r} must equal the filename {path.stem!r}")

    repos = data.get("repos")
    if not isinstance(repos, list) or not repos:
        err(f"{rel}: repos must be a non-empty list")
        continue
    for i, r in enumerate(repos):
        where = f"{rel}: repos[{i}] ({r.get('repo', '?')})"
        for field in ("repo", "url", "licence", "sha"):
            if not r.get(field):
                err(f"{where}: missing {field}")
        if r.get("sha") and not SHA_RE.match(r["sha"]):
            err(f"{where}: sha must be full 40-hex, got {r['sha']!r}")
        review = r.get("review")
        if not isinstance(review, dict):
            err(f"{where}: missing human licence review block (see CONTRIBUTING.md §3)")
            continue
        for field in ("spdx", "use", "by", "at"):
            if not review.get(field):
                err(f"{where}: review missing {field}")
        if review.get("use") not in LEGAL_USE:
            err(f"{where}: review.use must be one of {sorted(LEGAL_USE)}, "
                f"got {review.get('use')!r}")
        if review.get("at") and not re.match(r"^\d{4}-\d{2}-\d{2}$", review["at"]):
            err(f"{where}: review.at must be YYYY-MM-DD")

# ── Lane B: pack recipes ──────────────────────────────────────────────────
recipes = sorted(p for p in PACKS.glob("*/recipe.toml")
                 if p.parent.name != "TEMPLATE-recipe")
if not recipes:
    err("no pack recipes found — did the tree change shape?")

for path in recipes:
    rel = path.relative_to(ROOT)
    try:
        recipe = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as e:
        err(f"{rel}: not valid TOML ({e})")
        continue

    meta = recipe.get("recipe", {})
    if meta.get("name") != path.parent.name:
        err(f"{rel}: recipe.name {meta.get('name')!r} must equal the directory "
            f"{path.parent.name!r}")
    if meta.get("format") != 1:
        err(f"{rel}: recipe.format must be 1 (unknown formats are refused by "
            "the tool — do not invent one)")
    sources = recipe.get("sources")
    if not isinstance(sources, list) or not sources:
        err(f"{rel}: at least one [[sources]] block is required")
        continue
    for i, s in enumerate(sources):
        where = f"{rel}: sources[{i}]"
        for field in ("slug", "kind", "url", "licence"):
            if not s.get(field):
                err(f"{where}: missing {field}")
        if s.get("kind") not in ("git", "http-zip", "dir"):
            err(f"{where}: kind must be git | http-zip | dir, got {s.get('kind')!r}")
        if "/" in s.get("slug", "") or ".." in s.get("slug", ""):
            err(f"{where}: slug must be a plain name, never a path "
                "(it is joined into filesystem paths)")

if errors:
    print("corpus-hub validation FAILED:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(f"corpus-hub validation OK: {len(manifests)} manifests, "
      f"{len(recipes)} recipes")
