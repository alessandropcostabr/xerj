# PROGRAM-100 — the workflow that builds the Hub's first 100 corpora

**Status: active (opened 2026-10-02).** This document is the workflow. `backlog/backlog-100.json`
is the work list; `profiler.py` is the intake tool; `validate_hub.py` is the gate; the tracker is
GitHub issue **"Corpus Hub: first 100 corpora"** on xerj-org/xerj. The Hub launched 2026-10-01
with 5 entries (4 reference corpora + the rust-vulns pack); this program takes it to 100 without
lowering the bar the launch set: pinned, licenced, checksummed, signed, and *measured*.

The program exists because of two findings we already published, and it is shaped by both:

- retrieval wins decisively on **un-memorised** material and saves nothing on what the model
  already knows (the reference-coding study's memorised controls);
- the #1111 security A/B **tied** because a corpus nobody queries and whose records cannot match
  the query's shape is decoration — surface and shape beat size.

So "100 corpora" is not a volume target. It is 100 *nameable domains* an agent would actually
query, each shaped so a real question retrieves against it. A wave that ends with 14 good
corpora and 6 killed candidates is a success; one that ends with 20 mediocre ones is a failure.

---

## 1. The unit of work: one corpus, seven gates

Every corpus, regardless of lane, passes the same seven gates. No gate may be waived; a candidate
that cannot pass one is killed or deferred, and the backlog records why.

| # | gate | what satisfies it | who |
|---|------|-------------------|-----|
| G1 | **domain test** | the backlog row finishes *"an agent working on ___ would query this for ___"* in one specific sentence — "code" or "security" is not a domain | intake |
| G2 | **shape test** | the record/file shape matches the queries: function bodies for code questions, clause-level sections for standards questions, advisory records for precedent questions | build |
| G3 | **un-memorisation test** | the answer-bearing content is niche, internal, post-cutoff, or too large/detailed for recall — famous-and-small content is killed as retrieval theatre | intake |
| G4 | **licence review** | a human opened the licence file(s) and wrote the `review` block (`adapt-with-attribution` / `approach-only` / `mixed`); detector + profiler output are hints, never the verdict | reviewer |
| G5 | **pin truth** | manifest SHA = the commit the build actually used; recipes pin source URLs and versions; `format_version` refused when unknown | build |
| G6 | **registry validation** | `validate_hub.py` green (manifest/recipe shape, review blocks, 40-hex SHAs, no paths as slugs, backlog consistency) | CI + local |
| G7 | **retrieval spot-check** | 5 pre-written domain queries against the built corpus, top-5 hits graded manually (relevant / partial / miss); **median ≥ 3 relevant to pass**, else back to G2 with the diagnosis recorded | maintainer |

G7 is the wave's actual quality gate and it is deliberately manual: we have no ground-truth
relevance judgments for these domains, and pretending a script can grade "is this RFC section the
right answer to a sanitisation question" would be a number without a run behind it. Five queries
is small; it catches the failure modes that killed #1111's corpus arm (zero invocations,
prose-vs-code mismatch) at minutes of cost.

## 2. The wave loop

Waves are the batching unit: **one category, ~20 candidates, one PR to `corpus-hub`, one wave
report.** The loop:

```
            backlog row (status: candidate)
                    │  profiler.py <slug>          ── G1 G3 recorded, source pinned,
                    ▼                                 licence evidence gathered
            draft manifest / recipe  (use: UNREVIEWED ── cannot pass G6 until G4)
                    │  build (corpus index | corpus build)
                    ▼
            built corpus  ── G2 shape review
                    │  reviewer opens licence files ── G4
                    ▼
            final manifest / recipe  ── G5 G6
                    │  xerj code <slug> × 5 queries ── G7
                    ▼
        pass ──► status: live, PR to corpus-hub, wave report row
        fail ──► status: killed | deferred (reason recorded in backlog), candidate replaced
```

Per wave, on top of the per-corpus gates:

- **W-A (blind A/B, once per phase, not per wave).** One blinded agent task that is *natural* to
  the wave's domains — a plain arm and a corpus arm, run by the #1111 harness discipline (pinned
  binary, frozen protocol pre-registered before the runs, manual dynamic validation of every
  claimed difference). The pre-registered expectations are inherited from
  `benchmarks/corpus-ab-2026-10/CORPUS-X100.md` §4 (P1 surface / P2 shape / P3 un-memorised-only
  / P4 precision / P5 honest negative). A tie is a publishable outcome; a silent no-test is not.
- **W-B (freshness pass).** `profiler.py --check` over all live manifests; drift beyond the
  corpus's refresh class (below) opens a re-pin PR in the same wave.

## 3. Refresh classes (the 30-day contract at scale)

The engine refuses an index older than 30 days. 100 corpora make that a schedule, not an
accident. Every backlog row carries `refresh`:

| class | content | mechanism |
|---|---|---|
| `pinned` | specs, standards, papers, reference code at a release tag | index is stable; re-index on the 30-day clock; re-pin only when a new release matters to the domain |
| `weekly` | curated packs whose upstream moves (advisory DBs, cheat sheets) | recipe re-run on a weekly timer, signed, dated Release asset like `rust-vulns` |
| `daily` | feeds (KEV, OSV, GHSA) | the existing daily pack pipeline; a second feed joins it only if a consumer names a query it answers |

A `pinned` corpus whose upstream rewrote history (force-push, deleted tag) is **withdrawn**
(`status: withdrawn`), not silently re-pinned — the pin is the promise.

## 4. The categories (and why these)

Seven categories, each answering "what does an agent actually get asked". Counts are the backlog's
current shape; the wave order is by expected value per review hour, which favours public-domain
government data and permissive-spec sources first (cheap G4), and deferred-or-killed heavy
candidates last.

| cat | name | what it gives an agent | lane | target |
|-----|------|------------------------|------|--------|
| SEC | security advisories & identifiers | "does this pattern have CVE/GHSA/KEV precedent; is this CVE exploited in the wild" | B | 15 |
| STD | standards & specifications | "what does RFC 9105 / SP 800-88 / WHATWG-URL actually say about ___" (clause-level) | A | 14 |
| OPS | production & incident knowledge | "how do real teams handle ___ / what caused real outages like ___" | A | 9 |
| GOOD | design guidance & exemplars | "what does a reviewed, idiomatic ___ look like" | A | 9 |
| BAD | failure precedent (mining) | "show me real vulnerable functions and the fix that closed them" (beyond rust-vulns) | B | 6 |
| DATA | reference implementations — data engines | how duckdb/rocksdb/sqlite actually do planner/LSM/B+-tree/… | A | 24 |
| NET | reference implementations — net/crypto/serialisation/compression | how quinn/rustls/zstd/protobuf actually do handshake/… | A | 23 |

Lane B packs that curate *across* sources (KEV, postmortems) are where the Hub's own value-add is
densest — the identity-resolution machinery (`[identity] edges`, union-find) is what upstream
databases do not ship. Lane A reference corpora are the cheapest to stand up and the ones the
reference-coding measurement already validates.

**Memorisation is priced in, not ignored:** famous small libraries are excluded by G3 however
permissive their licence (this is why the DATA/NET rows are engines with real internals, not
"awesome-rust" hits), and every SEC row's *prose* is treated as shape-risk after #1111 — advisory
text alone does not answer code-shaped questions, so SEC packs carry affected-functions/
fix-commit fields the way `rust-vulns` gen-2 is designed to (see `CORPUS-X100.md` §3).

## 5. Licence discipline at batch scale

100 corpora ≈ 150+ source reviews. The rules do not bend; the *process* scales:

1. `profiler.py` gathers the evidence: LICENSE/COPYING files found at the pin, first lines
   quoted, SPDX heuristic, per-source bytes — and writes it into the draft's `review.note`.
2. The reviewer opens the licence file **at the pinned SHA** (not `HEAD`), decides `use`, and
   signs `by`/`at`. `UNREVIEWED` fails G6, so nothing lands unreviewed by accident.
3. Known traps, recorded here so no wave rediscovers them:
   - **license changes mid-history** (Redis → RSAL/SSPL, HashiCorp → BUSL, Sentry → BUSL,
     Elastic → AGPL era, Grafana Loki → AGPL): review the licence *at the pin*, and prefer
     the open fork (valkey, openbao, etc.) over the relicensed origin.
   - **CC variants**: CC-BY fine with attribution; **CC-BY-NC / NC-ND / ND are approach-only
     at best** (non-commercial + no-derivatives terms collide with serving derived snippets);
     SRE books and CIS benchmarks live here — treat as `approach-only` or exclude.
   - **docs ≠ code licence**: many projects dual-license (code MIT, docs CC-BY-SA); review the
     artefact you actually index.
   - **mirror provenance**: RFC/spec mirrors must carry the upstream's own redistribution terms
     (IETF TLP, W3C, WHATWG, ECMA libre, Unicode) — review the upstream terms, note the mirror.
   - **the detector lies both ways** (it read Elasticsearch as Apache-2.0 once): CI checks the
     review block exists and is well-formed; only the opened file makes it true.

## 6. Consume-side contract

Nothing lands as `live` until its three commands are true from a clean machine, and the wave
report paste proves it:

```
xerj corpus add  --from <manifest-or-pack URL at the corpus-hub branch>
xerj corpus index <slug>
xerj code        <slug> "<one of the G7 queries>"
```

Packs additionally: `--verify-sig` green against the published signature (the launch post's
rule — checksums prove integrity, signatures prove authorship).

## 7. Reporting

Each wave appends a section to `WAVES.md` (this directory): corpus, gate outcomes, G7 scores
(the misses included), kills with reasons, drift found by W-B, and the wave's reviewer-hours
estimate. The phase's blind A/B gets the full #1111-style treatment in `benchmarks/` on `main`
with RESULTS and VERDICTS files, pre-registered before the runs. Management view, one line per
wave, rolls into the tracker issue.

## 8. Wave plan

| wave | category | candidates | note |
|------|----------|-----------|------|
| 1 | SEC | backlog rows `cat=SEC`, status candidate | public-domain/CC-heavy: cheapest G4; `cisa-kev` already scoped by #1110 Part A — coordinate, don't duplicate |
| 2 | STD | `cat=STD` | clause-shape G2 is the work; mirrors pinned at release tags |
| 3 | DATA | `cat=DATA` | extends the launch's four; biggest G3 win (real internals, niche paths) |
| 4 | NET | `cat=NET` | same discipline, net/crypto/serialisation/compression |
| 5 | OPS+GOOD | `cat=OPS`,`cat=GOOD` | curation-heavy: packs where the Hub adds identity-resolution value |
| 6 | BAD | `cat=BAD` | depends on the ×100 mining tooling (#61 S1/S3) — scheduled behind it by design |

Wave 6 ordering is deliberate: mining corpora carry per-record provenance and licence obligations
that only exist once the harvester does (advisory-backed vs provisional records must be
distinguishable in the badge, per `CORPUS-X100.md`).

## 9. What "done" means

100 rows at `status: live` — each with its seven gates recorded in `WAVES.md`, its refresh class
honoured by a W-B pass within the last cycle, and at least two phase-level blind A/Bs run and
published (win or tie) in `benchmarks/`. If the program stalls below 100 because domains ran out
of candidates that pass G1–G3, **that is the correct outcome to publish** — a hub of 70 corpora
that pass the domain test beats 100 that don't, and the number in the README stays honest either
way.
