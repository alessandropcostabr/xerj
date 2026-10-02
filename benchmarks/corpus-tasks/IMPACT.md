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

## Status

- [x] Pilot (hand-built memorised suite, tie honestly published)
- [x] Wave 1: 4 code corpora, 80 runs
- [ ] Waves 2+: remaining live lane-A corpora as prep completes
      (`runs/PREP.log`); markdown corpora recorded `suite-infeasible`
