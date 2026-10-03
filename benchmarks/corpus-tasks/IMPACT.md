# IMPACT — per-corpus task-level measurement roll-up

Every row: same agent, same protocol (PROTOCOL.md), two arms — **P** bare vs
**X** with the XERJ node holding that corpus. Suites generated from the pinned
clone (`harness/gen_tasks.py`); grading mechanical (regex alternates over the
final `ANSWER:` line). `drift` = constant introduced/changed inside
2024-01-01→pin (post-training-cutoff for the model); `state` = current value
(fame-dependent recall). Unknown-honesty and guessable-value flags are audited
per suite in `runs/<slug>/RESULTS.md`.

## Wave 1 (2026-10-02, model default, node :9200)

| corpus | tasks | P solved | X solved | P cost | X cost | P wall | X wall | X calls |
|--------|-------|----------|----------|--------|--------|--------|--------|---------|
| lmdb | 10 drift | 0/10 (9 honest-unknown) | **9/10** | $1.61 | $1.31 | 616 s | 309 s | 17 |
| quinn | 10 drift | 0/10 (9 honest-unknown) | **10/10** | $0.86 | $0.94 | 281 s | 195 s | 14 |
| leveldb | 10 state | 5/10 (2 guessable) | **10/10** | $0.93 | $1.04 | 378 s | 236 s | 16 |
| boringtun | 10 state | 6/10 (1 guessable) | **10/10** | $1.16 | $0.68 | 467 s | 103 s | 10 |

**Same corpus, both ways (lmdb):** the hand-built memorised suite
(`runs/lmdb/RESULTS.md`, pilot) tied 10/10 vs 10/10 at +33% X cost; the
drift-anchored suite on the *same corpus and pin* separates 0/10 vs 9/10 with X
*cheaper and 2× faster*. Content memorisation, not corpus quality, decides
whether retrieval pays — now shown within one corpus under one protocol.

Reading notes (pre-registered in PROTOCOL.md §2, kept here for the roll-up):

- The P arm's failures are honest: 9/10 answers per drift corpus are the word
  `unknown`, not fabricated constants. The bare prompt forbids guessing.
- Guessable-value passes (trivial constants like `0x2`) are flagged and
  discounted in each suite's audit line.
- X cost is *lower* than P on 3/4 corpora here — on un-memorised content the
  bare arm burns turns reasoning toward a refusal while retrieval answers in
  ~2 turns.

## Wave 3 close — the full 71-corpus universe, terminal (2026-10-03)

All 71 universe corpora (`runs/universe-71.txt`) reached a terminal state.
Full 71-row table: `python3 harness/report.py`; snapshot consumed by
hub.xerj.org: `../hub/backlog/impact-snapshot-2026-10-03.json` (71 rows).

| state | count | meaning |
|-------|-------|---------|
| measured | 33 | both arms driven, 10 tasks each (328 runs/arm) |
| index-pathological | 18 | corpus shape defeats the indexer (single >4MB files) — recorded mechanically, not run |
| infeasible | 19 | suite generator finds no drift/state content (markdown/spec corpora) |
| cited-#1111 | 1 | rust-vulns measured under the #1111 protocol and cited from it |

**Headline (33 measured corpora, 328 tasks):** bare-P solved **66/328 (20%)**
vs with-corpus-X **321/327 (98%)** at near-equal mean cost per run
(**$1.02 vs $1.09**). On the drift-bearing subset — 22 corpora, 196 tasks
whose answers changed inside 2024-01-01→pin — P solved **19/196 (10%)** vs X
**190/196 (97%)**. The X arm's 7 misses concentrate in suites whose answers
sit in giant single files the indexer skips (the same shape class as the
index-pathological rows) — corpus shape, not retrieval, is the residual
failure mode, which is why the hub's intakes split section-per-file.

The 18 index-pathological and 19 infeasible rows are findings, not holes:
they are the measured boundary of what whole-file indexing and
constant-drift suites respectively support, and both classes feed the
Corpus Hub's shape rules (section-split intake, G2 >4MB guard).

## Status

- [x] Pilot (hand-built memorised suite, tie honestly published)
- [x] Wave 1: 4 code corpora, 80 runs
- [x] Waves 2–3: full 71-corpus universe terminal (33 measured, 18
      index-pathological, 19 infeasible, 1 cited-#1111)
- Ops notes: two server deaths mid-wave (index-time memory exhaustion,
  #1122) marked corpora INDEX-FAILED with no RESULTS.md — both re-run to
  terminal after the server returned green (postgres-src measured;
  tldr-pages infeasible).
