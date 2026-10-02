#!/usr/bin/env bash
# relaunch.sh — clear stuck leftovers and start the wave workers.
set -u
pkill -f 'harness/wave.sh' 2>/dev/null
pkill -f 'xerj corpus index' 2>/dev/null
pkill -f 'claude -p --output-format' 2>/dev/null
pkill -f 'harness/drive.py' 2>/dev/null
sleep 2
B=/workspace/benchmarks/corpus-tasks
for i in 0 1 2 3; do
  nohup bash "$B/harness/wave.sh" $(cat "$B/runs/.rest-0$i") >> "$B/runs/worker-$i.log" 2>&1 &
done
nohup bash "$B/harness/wave.sh" badger caddy dragonboat iceberg etcd-src kafka-src >> "$B/runs/worker-6.log" 2>&1 &
sleep 15
for i in 0 1 2 3 6; do echo "w$i: $(tail -1 "$B/runs/worker-$i.log")"; done
