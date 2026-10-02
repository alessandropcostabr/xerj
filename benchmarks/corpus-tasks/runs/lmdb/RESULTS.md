# lmdb suite — RESULTS (2026-10-02)

Suite: `tasks/lmdb.json`, 10 tasks, expected answers derived from the pinned
clone (`700e10f91a`, `libraries/liblmdb/{mdb.c,lmdb.h}`) before the arms ran.
T1 ran as the smoke pair before protocol freeze (both passed); T2–T10 ran after.
Arms per PROTOCOL.md. Node: loopback :9200, corpus indexed 2026-10-02
(977 records).

## Headline

| arm | solved | cost | wall | turns | corpus calls |
|-----|--------|------|------|-------|--------------|
| P (bare) | **10/10** | $1.63 | 755 s | 10 | 0 |
| X (corpus+XERJ) | **10/10** | $2.17 | 680 s | 65 | 31 |

**A tie — and the corpus arm cost 33% more.** Per-task table in
`grades.jsonl`; every X-arm answer carried `file:line` citations from the
retrieved source (e.g. T9: `mdb.c:712-714`, `mdb.c:5659`), every X-arm run
queried the corpus (2–6 calls).

## Why (audited, not assumed)

Every P-arm run is a **single-turn, zero-tool-use answer**: `num_turns=1` on
all ten, no command mentions in outputs, costs $0.05–0.44. The bare model
recalled LMDB cold — including `-30790` (MDB_READERS_FULL), `1048576`
(DEFAULT_MAPSIZE), `0x400000` (MDB_NOLOCK), `me_maxreaders`, `me_pghead`+MIDL,
and the spill mechanism with function names. No transcript can show a lookup
because no lookup happened; there was no turn in which one could have.

This is the reference-coding study's memorised-control finding reproduced at
corpus granularity: **LMDB's source is inside the model.** Retrieval cannot
beat recall on recallable content; it can only add cost (here: +$0.054/run
mean, +5.5 turns).

## What this suite proves and does not

- Proves: the harness runs, grades mechanically, counts invocations, and
  publishes a negative result cleanly. The per-corpus instrument exists.
- Does not prove: "corpora don't help." It proves *this corpus, for this
  model, on general-knowledge questions about famous software, adds cost
  without adding solves*. The protocol's pre-registered expectation (§2.1)
  said exactly this would happen on memorised content — the surprise is only
  how complete the recall is (10/10, not the predicted 2–5/10 on detail
  questions).

## Design consequence for the remaining 70 suites

Task suites separate arms only on **un-memorised** content. Two task classes
qualify, both G3-consistent:

1. **Pin-anchored questions** — about what is true *at this commit* (exact
   current defaults after recent commits, line anchors, behaviour that
   changed in the last N commits). Recall cannot know an arbitrary pin; the
   corpus can. T9 came closest (X cited real line numbers) and still tied
   because the fact is stable across pins.
2. **Genuinely niche/private/post-cutoff corpora** — dragonboat-class
   adoption, the user's own tree (already measured: the autoindex/reference
   studies' 2.7× tokens / 2.1× cost), or post-cutoff pins.

Next suite queued under this protocol: a pin-anchored variant (5 tasks
re-anchored to commit-specific facts) on this same corpus to measure the
 separation directly; then a niche corpus. On famous-repo corpora generally,
 the expected result is parity, and that expectation is now empirically
 grounded.
