#!/usr/bin/env bash
# run.sh <corpus> <task-id> <arm:p|x>  — one task, one arm, one run dir
set -u
CORPUS=$1; TID=$2; ARM=$3
HERE=$(cd "$(dirname "$0")/.." && pwd)
X=/tmp/xtarget/release/xerj
RUN="$HERE/runs/$CORPUS/$TID-$ARM"
rm -rf "$RUN"; mkdir -p "$RUN/scratch"
Q=$(jq -r --arg t "$TID" '.tasks[] | select(.id==$t) .q' "$HERE/tasks/$CORPUS.json")

SUBJ=$(jq -r '.subject // .corpus' "$HERE/tasks/$CORPUS.json")
COMMON="You are answering one technical question about the $SUBJ source tree. Be precise and brief. You MUST end your reply with a single line of the form 'ANSWER: <your answer>'."
if [ "$ARM" = "p" ]; then
  PROMPT="$COMMON You are offline: no network access, and its source code is not available to you. Answer from your own knowledge; if you do not know, say 'unknown' in the ANSWER line — do not guess a fabricated constant. The question: $Q"
else
  PROMPT="$COMMON A local retrieval node holds the corpus (the real source at a pinned commit). Query it from bash like: xerj code '$CORPUS' \"<your search query>\" --url http://localhost:9200 . Use it as much as helps; cite what you found. The question: $Q"
fi
printf '%s\n' "$PROMPT" > "$RUN/prompt.txt"

cd "$RUN/scratch"
export PATH="$HERE/harness/xerjshim:$PATH"
export XERJ_CALL_LOG="$RUN/xerj-calls.log"; : > "$XERJ_CALL_LOG"
S=$(date +%s)
timeout 420 claude -p --output-format json --dangerously-skip-permissions --max-turns 10 "$PROMPT" > out.json 2> err.txt
RC=$?
E=$(date +%s)
cp "$RUN/scratch/out.json" "$RUN/out.json" 2>/dev/null || true
echo $RC > "$RUN/.rc"; echo $((E-S)) > "$RUN/.seconds"
python3 - "$RUN" <<'PY'
import json, sys, pathlib
run = pathlib.Path(sys.argv[1])
try: d = json.loads((run/"out.json").read_text())
except Exception: d = {"_raw": (run/"out.json").read_text(errors="replace")[:2000], "result": ""}
meta = {"rc": int((run/".rc").read_text()) if (run/".rc").exists() else 0,
        "seconds": int((run/".seconds").read_text()) if (run/".seconds").exists() else 0,
        "cost_usd": d.get("total_cost_usd"), "num_turns": d.get("num_turns"),
        "usage": d.get("usage"), "xerj_calls": len((run/"xerj-calls.log").read_text().splitlines())}
(run/"meta.json").write_text(json.dumps(meta, indent=1))
PY
python3 - "$HERE" "$RUN" "$TID" <<'PY'
import json, sys, pathlib, subprocess
here, run, tid = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
tasks = json.loads((here/f"tasks/{pathlib.Path(run).parent.name}.json").read_text())["tasks"]
task = next(t for t in tasks if t["id"] == tid)
out = subprocess.run(["python3", str(here/"harness/check.py"), "/dev/stdin", str(run/"out.json")],
                     input=json.dumps(task), capture_output=True, text=True).stdout
grade = json.loads(out); grade["seconds"] = int((run/".seconds").read_text()); grade["arm"] = run.name.split("-")[-1]
grade["xerj_calls"] = len((run/"xerj-calls.log").read_text().splitlines())
import json as j; m = j.loads((run/"meta.json").read_text()) if (run/"meta.json").exists() else {}
grade["cost_usd"] = m.get("cost_usd"); grade["turns"] = m.get("num_turns")
print(j.dumps(grade))
PY
