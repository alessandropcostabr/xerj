#!/usr/bin/env bash
# build_uk.sh — download all enumerated ukpga acts 2015-2026 (current revised
# version via /data.xml), split per-section, build the pinned mirror repo.
set -u
W=/tmp/nonit/uk
SP=/root/hub-branch/tools/xerj-code/hub/nonit/split_uk.py
LOG=/tmp/nonit/uk-build.log
mkdir -p "$W/xml"
echo "download start $(date -u +%H:%M:%S)" >> "$LOG"

download() {
  y=$1; c=$2
  f="$W/xml/$y-$c.xml"
  [ -s "$f" ] && return 0
  curl -sS --retry 3 -o "$f" "https://www.legislation.gov.uk/ukpga/$y/$c/data.xml" --max-time 240 \
    || { rm -f "$f"; echo "$y-$c DL-FAIL" >> "$LOG"; return 1; }
  # 4xx/5xx come back as error pages; keep only real XML
  head -c 200 "$f" | grep -q '<?xml\|<Legislation' || { rm -f "$f"; echo "$y-$c NOTXML" >> "$LOG"; return 1; }
}
export -f download
export W LOG

awk '{print $1, $2}' /tmp/nonit/uk-list.txt | xargs -P 6 -n2 bash -c 'download "$@"' _
echo "download done $(date -u +%H:%M:%S): $(ls "$W"/xml | wc -l) files" >> "$LOG"

mkdir -p "$W/repo"
ok=0
for f in "$W"/xml/*.xml; do
  base=$(basename "$f" .xml); y=${base%-*}; c=${base#*-}
  python3 "$SP" "$y" "$c" "$f" "$W/repo" >> "$LOG" 2>&1 && ok=$((ok+1)) \
    || echo "$base SPLIT-FAIL" >> "$LOG"
done
echo "split done $(date -u +%H:%M:%S): $ok acts, files=$(find "$W/repo" -name '*.txt' | wc -l)" >> "$LOG"
