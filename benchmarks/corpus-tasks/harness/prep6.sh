#!/usr/bin/env bash
# prep6.sh — clone+unshallow the manifest corpora prep never reached, then
# drive them (5th worker; shares the global index lock with workers 0-3).
set -u
HUB=/root/hub-branch/tools/xerj-code/hub
CORPORA=/root/.xerj-code/corpora
X=/tmp/xtarget/release/xerj
for slug in zalando-restful-api-guidelines zlib-ng zstd xerj-vector xerj-storage xerj-search; do
  [ -d "$CORPORA/$slug" ] && { echo "$slug exists"; continue; }
  echo "── add $slug $(date -u +%H:%M:%S)"
  timeout 1800 "$X" corpus add --from "$HUB/$slug.json" 2>&1 | tail -2
  gitdir=$(find "$CORPORA/$slug" -maxdepth 2 -name .git -type d 2>/dev/null | head -1)
  [ -z "$gitdir" ] && { echo "$slug NOGIT"; continue; }
  w=$(dirname "$gitdir")
  for r in $(find "$CORPORA/$slug" -maxdepth 2 -name .git -type d | xargs -n1 dirname); do
    timeout 600 git -C "$r" fetch --unshallow -q 2>/dev/null || timeout 600 git -C "$r" fetch -q --depth=200000 2>/dev/null
    echo "  $r depth=$(git -C "$r" rev-list --count HEAD 2>/dev/null)"
  done
done
mkdir -p /workspace/benchmarks/corpus-tasks/runs/school-of-sre
printf '# school-of-sre — not measured (demoted at G7)\n\nDemoted to candidate at wave-0 G7 (median 2.5/5: query suite presumed absent\nchapters; rescope-then-rerun, no query-shopping). No manifest on the hub branch\n— excluded from the 71 live.\n' > /workspace/benchmarks/corpus-tasks/runs/school-of-sre/RESULTS.md
exec bash /workspace/benchmarks/corpus-tasks/harness/wave.sh \
  zalando-restful-api-guidelines zlib-ng zstd xerj-vector xerj-storage xerj-search
