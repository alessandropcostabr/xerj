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

LOCK_SMALL=/tmp/corpus-tasks-index-small.lock
index_corpus() {  # big corpora take the exclusive lock; small ones may pair
  # (2026-10-02 OOM was postgres-src x duckdb — two BIG indexes. One big + one
  # small, or two small, stayed within memory on this 119G box.)
  local sl=/root/.xerj-code/corpora/$1
  local lock="$LOCK"
  if [ "$(du -sm "$sl" 2>/dev/null | cut -f1)" -lt 200 ]; then
    if flock -n 8 true 8>"$LOCK_SMALL" 2>/dev/null; then lock="$LOCK_SMALL"; fi
  fi
  (
    flock 9
    for try in 1 2; do
      s=$(curl -s -m 3 "$URL/_cluster/health" | jq -r .status 2>/dev/null)
      [ "$s" = "green" ] && break
      sleep 20
    done
    timeout 900 "$X" corpus index "$1" --url "$URL" >/dev/null 2>&1 && exit 0
    sleep 20
    timeout 900 "$X" corpus index "$1" --url "$URL" >/dev/null 2>&1 && exit 0
    exit 1
  ) 9>"$lock"
}

for slug in "$@"; do
  [ -d "runs/$slug" ] && [ -f "runs/$slug/RESULTS.md" ] && { echo "$slug already driven"; continue; }
  [ -d "/root/.xerj-code/corpora/$slug" ] || { echo "$slug NOT CLONED"; continue; }
  # G2 guard: a single non-git file >4MB means binary/asset bloat the indexer
  # grinds on (kafka-protocol: 898M, 28k files, 6MB JPGs — 2026-10-02 17:19Z).
  big=$(find "/root/.xerj-code/corpora/$slug" -type f -size +4M ! -path "*/.git/*" | head -1)
  if [ -n "$big" ]; then
    sz=$(du -sh "/root/.xerj-code/corpora/$slug" | cut -f1); n=$(find "/root/.xerj-code/corpora/$slug" -type f ! -path "*/.git/*" | wc -l)
    mkdir -p "runs/$slug"
    printf '# %s — index-pathological (shape)\n\nThe clone contains non-git files over 4 MB (e.g. %s). Clone: %s in %s files.\nThe indexer grinds asset bloat (kafka-protocol class: 23+ min and counting for a\ndocs-sized corpus); suite not run. Hub action: rescope the corpus (strip static\nassets / split giant files) before G7 — same remedy as the ecma262 finding.\n' \
      "$slug" "$(basename "$big")" "$sz" "$n" > "runs/$slug/RESULTS.md"
    echo "$slug INDEX-PATHOLOGICAL (giant file: $(basename "$big"))"; continue
  fi
  echo "── $slug: index $(date -u +%H:%M:%S)"
  index_corpus "$slug" || { echo "$slug INDEX-FAILED"; continue; }
  python3 harness/gen_tasks.py "$slug" || { echo "$slug GEN-FAILED"; continue; }
  n=$(jq '.tasks | length' "tasks/$slug.json")
  echo "── $slug: $n tasks, drive $(date -u +%H:%M:%S)"
  python3 harness/drive.py "$slug"
done
