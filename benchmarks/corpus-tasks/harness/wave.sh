#!/usr/bin/env bash
# wave.sh <slug>... — for each cloned corpus: index into :9200, generate suite,
# drive both arms, write RESULTS.md. Skips corpora already driven (RESULTS.md)
# and records mechanically-infeasible suites without running them.
#
# Indexing is serialized across workers with flock (2026-10-02: two concurrent
# big-corpus indexes OOM-killed the node — postgres-src × duckdb at 17:09Z);
# each index waits for cluster green first and retries once after 20 s.
set -u
HERE=/workspace/benchmarks/corpus-tasks
X=/tmp/xtarget/release/xerj
URL=http://localhost:9200
LOCK=/tmp/corpus-tasks-index.lock
cd "$HERE"

index_corpus() {  # holds the global lock; exits 0 on success
  (
    flock 9
    for try in 1 2; do
      s=$(curl -s -m 3 "$URL/_cluster/health" | jq -r .status 2>/dev/null)
      [ "$s" = "green" ] && break
      sleep 20
    done
    timeout 1800 "$X" corpus index "$1" --url "$URL" >/dev/null 2>&1 && exit 0
    sleep 20
    timeout 1800 "$X" corpus index "$1" --url "$URL" >/dev/null 2>&1 && exit 0
    exit 1
  ) 9>"$LOCK"
}

for slug in "$@"; do
  [ -d "runs/$slug" ] && [ -f "runs/$slug/RESULTS.md" ] && { echo "$slug already driven"; continue; }
  [ -d "/root/.xerj-code/corpora/$slug" ] || { echo "$slug NOT CLONED"; continue; }
  echo "── $slug: index $(date -u +%H:%M:%S)"
  index_corpus "$slug" || { echo "$slug INDEX-FAILED"; continue; }
  python3 harness/gen_tasks.py "$slug" || { echo "$slug GEN-FAILED"; continue; }
  n=$(jq '.tasks | length' "tasks/$slug.json")
  echo "── $slug: $n tasks, drive $(date -u +%H:%M:%S)"
  python3 harness/drive.py "$slug"
done
