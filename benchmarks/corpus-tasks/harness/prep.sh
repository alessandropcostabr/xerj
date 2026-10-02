#!/usr/bin/env bash
# prep.sh — clone + unshallow every live hub manifest not already on disk.
# Indexing is a separate pass (index_all.sh) so drive waves can own the server.
# Resumable: skips corpora whose clone dir exists. Logs to runs/PREP.log.
set -u
HUB=/root/hub-branch/tools/xerj-code/hub
CORPORA=/root/.xerj-code/corpora
X=/tmp/xtarget/release/xerj
LOG=/workspace/benchmarks/corpus-tasks/runs/PREP.log
mkdir -p "$(dirname "$LOG")"

for m in "$HUB"/*.json; do
  slug=$(basename "$m" .json)
  [ "$slug" = "corpus-schema" ] && continue
  [ -d "$CORPORA/$slug" ] && { echo "$(date -u +%FT%TZ) $slug CLONE-EXISTS" >> "$LOG"; continue; }
  echo "$(date -u +%FT%TZ) $slug ADD-START" >> "$LOG"
  if timeout 900 "$X" corpus add --from "$m" >> "$LOG" 2>&1; then
    gitdir=$(find "$CORPORA/$slug" -maxdepth 2 -name .git -type d 2>/dev/null | head -1)
    if [ -n "$gitdir" ]; then
      w=$(dirname "$gitdir")
      if timeout 420 git -C "$w" fetch --unshallow -q 2>/dev/null || timeout 420 git -C "$w" fetch -q --depth=200000 2>/dev/null; then
        echo "$(date -u +%FT%TZ) $slug OK depth=$(git -C "$w" rev-list --count HEAD 2>/dev/null)" >> "$LOG"
      else
        echo "$(date -u +%FT%TZ) $slug UNSHALLOW-FAILED depth=$(git -C "$w" rev-list --count HEAD 2>/dev/null)" >> "$LOG"
      fi
    else
      echo "$(date -u +%FT%TZ) $slug ADD-NOGIT" >> "$LOG"
    fi
  else
    echo "$(date -u +%FT%TZ) $slug ADD-FAILED" >> "$LOG"
  fi
done
echo "$(date -u +%FT%TZ) PREP-DONE" >> "$LOG"
