# CORPUS-TASKS — per-corpus task-level impact measurement

**Status: protocol frozen 2026-10-02 after the T1 smoke pair, before the remaining
18 runs.** Suite + runner live here; results land in `runs/<corpus>/RESULTS.md`.

## 1. The question

For one hub corpus: does an agent **with** the XERJ node holding that corpus solve
the corpus's own domain tasks better/cheaper/faster than the **same agent without
it**? This is the per-corpus version of what `measure/`'s reference-coding study
measured for the launch corpora and #1111 measured (and tied) for `rust-vulns`.

## 2. Pre-registered expectations (so ties/losses cannot be reframed)

Our own published findings constrain what any honest run can show:

1. **Memorised content does not separate arms** (the reference-coding study's
   memorised controls were neutral-to-harmful). Tasks whose answers the model
   recalls — like T1's memorable `0xBEEFC0DE`, which the bare arm answered
   correctly in the smoke pair — will tie. That is a property of the content,
   not a harness failure.
2. **A corpus only pays when it is queried** (#1111's corpus arm invoked the
   corpus zero times and tied). The X arm's prompt names the retrieval command;
   `xerj_calls` is recorded per run via a PATH shim. A run with 0 calls that
   passes is a recall, not a corpus win — reported as such.
3. Therefore the realistic best case is **bare ≈ 2–5/10 and corpus ≈ 7–10/10 on
   un-memorised detail**, NOT 0/10 vs 10/10. A 0/10 bare arm would mean the task
   suite is unanswerable trivia rather than working knowledge — and would be
   scrutinised as task-design bias before being celebrated.

**"Best case 0/10 without, 10/10 with" is explicitly NOT the success criterion.**
The success criterion is: every task graded by a checker derived from the pinned
source, both arms identical except for the retrieval node, and the delta (or
absence of one) published.

## 3. Task suite (10 per corpus)

**Amended 2026-10-02 (post-pilot, pre-scale): suites are generator-derived.**
The pilot's hand-built lmdb suite measured memorised content (10/10 vs 10/10,
documented in `runs/lmdb/RESULTS.md`). Its pre-registered design consequence —
pin-anchored questions — is implemented as `harness/gen_tasks.py`, which mines
the pinned clone and writes `tasks/<slug>.json`:

- **drift** tasks: constants whose introducing change lies inside the window
  2024-01-01 → pin (committer dates; `git log HEAD` at the pin, so facts are
  ancestors of the pin by construction). Kinds: `added` (name first appears in
  the window — the model has plausibly never seen the name) and `changed`
  (value changed; `olds` recorded so a bare arm serving the memorised old value
  is gradable as a *specific wrong answer*, not just a miss).
- **state** tasks (filler to 10): current constant values at the pin. On famous
  repos these are expected to tie — that is the null-control behavior, measured
  not hidden; each task carries its class and per-class scores are reported.
- Ground truth is mechanical: the value in the working tree at the pin;
  checkers are regex alternates (hex/dec) over the final `ANSWER:` line — no
  LLM judging, no partial credit negotiation after the fact.
- Corpora whose file types yield <4 minable facts (markdown/doc corpora) are
  recorded as `suite-infeasible (mechanical)` with their count, not run.

The clones used for mining are unshallowed (`git fetch --unshallow`) with the
working tree left at the pin, so history is complete but facts stay pin-anchored.

## 4. Arms

| | P (plain) | X (corpus + XERJ) |
|---|---|---|
| Agent | `claude -p` CLI 2.1.197, default model, `--dangerously-skip-permissions --max-turns 10`, `--output-format json` | identical |
| cwd | scratch dir (no CLAUDE.md, no project memory) | identical |
| Knowledge | own parameters only; told source is unavailable and to answer `unknown` rather than fabricate | identical **plus** `xerj code lmdb "<q>" --url http://localhost:9200` |
| Network | offline | offline (loopback node only) |
| xerj binary | not on PATH, not mentioned | on PATH via logging shim (counts invocations) |

Metrics per run: pass/fail (checker), `total_cost_usd`, `usage.output_tokens`,
wall seconds, turns, `xerj_calls`. Suite report: solved/10 per arm, mean cost,
mean time, total corpus invocations.

## 5. Contamination controls

- Arms run from a scratch cwd so no project CLAUDE.md/memory leaks in.
- The pinned clone exists on this machine (the node serves it); a bare arm that
  went looking for it would show in its transcript — audits happen before a
  surprising P-arm failure is believed.
- Checkers were written from the source before the runs; grades are mechanical.

## 6. Scale and order of play

71 corpora × 10 tasks × 2 arms = 1,420 runs ≈ $180–450 at the observed Q&A run
cost (~$0.13–0.15) and ~6–10 h wall clock — batched, not attempted at once.
Order: pilot `lmdb` (this freeze), then one famous-repo corpus (nginx or
protobuf) as a **null-control suite** where parity is the expected result, then
the remainder in wave order. A corpus earns the hub's `impact-measured` note from
a completed suite, whatever the delta is.
