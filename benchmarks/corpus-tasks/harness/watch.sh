#!/usr/bin/env bash
# watch.sh — block until no corpus is queued/running, then print the final table.
B=/workspace/benchmarks/corpus-tasks
while :; do
  n=$(python3 "$B/harness/report.py" 2>/dev/null | tail -1 | grep -o 'queued=[0-9]*' | cut -d= -f2)
  [ -z "$n" ] && n=99
  [ "$n" = "0" ] && break
  w=$(ps -eo args | grep -c 'harness/wave[.]sh')
  [ "$n" != "0" ] && [ "$w" = "0" ] && { echo "WORKERS DEAD with $n queued — restart needed"; exit 42; }
  sleep 60
done
echo "ALL RESOLVED $(date -u +%FT%TZ)"
python3 "$B/harness/report.py"
