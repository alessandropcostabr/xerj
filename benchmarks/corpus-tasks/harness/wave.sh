#!/usr/bin/env bash
# wave.sh <slug>... — for each cloned corpus: index into :9200, generate suite,
# drive both arms, write RESULTS.md. Skips corpora already driven (RESULTS.md)
# and records mechanically-infeasible suites without running them.
set -u
HERE=/workspace/benchmarks/corpus-tasks
X=/tmp/xtarget/release/xerj
URL=http://localhost:9200
cd "$HERE"

for slug in "$@"; do
  [ -d "runs/$slug" ] && [ -f "runs/$slug/RESULTS.md" ] && { echo "$slug already driven"; continue; }
  [ -d "/root/.xerj-code/corpora/$slug" ] || { echo "$slug NOT CLONED"; continue; }
  echo "── $slug: index $(date -u +%H:%M:%S)"
  timeout 1200 "$X" corpus index "$slug" --url "$URL" >/dev/null 2>&1 || { echo "$slug INDEX-FAILED"; continue; }
  python3 harness/gen_tasks.py "$slug" || { echo "$slug GEN-FAILED"; continue; }
  n=$(jq '.tasks | length' "tasks/$slug.json")
  echo "── $slug: $n tasks, drive"
  python3 harness/drive.py "$slug"
done
