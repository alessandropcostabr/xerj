# The XERJ Corpus Hub — this branch is the registry

You are on the **`corpus-hub` branch** of [xerj-org/xerj](https://github.com/xerj-org/xerj).
This branch is the public contribution surface for the Corpus Hub: **open a pull request
targeting `corpus-hub`** to add or update a corpus. The project README lives on
[`main`](https://github.com/xerj-org/xerj/tree/main#readme). The walkthrough with the
measured use case and the A/B we published as a tie is
[the launch post](https://xerj.org/blog/the-corpus-hub); the reader-facing guide is
[xerj.org/docs/corpus-hub](https://xerj.org/docs/corpus-hub).

A **corpus** is a body of knowledge an AI agent retrieves from — peer-engine source code,
vulnerability advisories, internal documents, datasets — indexed into [XERJ](https://xerj.org)
and queried with `xerj code <name> "<what you need>"`. The Hub is the discipline around
that: every corpus is **pinned** (two people retrieve the same bytes), **licenced** (each
source reviewed by a human, not a detector), **checksummed** (packs carry per-file SHA-256),
and — for published packs — **signed** (detached ed25519 a consumer verifies before trusting).

## The two lanes

| lane | what you contribute | where it lands | what it becomes |
|---|---|---|---|
| **Reference corpora** (source code) | a `corpus.json` definition: pinned repo SHAs + per-source licence review | [`tools/xerj-code/hub/`](./tools/xerj-code/hub/) | a rebuild-anywhere reference corpus behind `xerj corpus add --from <file>` |
| **Record packs** (structured data) | a recipe TOML + provenance notes | [`tools/packs/<name>/`](./tools/packs/) | a checksummed, signed pack published as a GitHub Release asset |

Both lanes are one PR each. **Read
[`tools/xerj-code/hub/CONTRIBUTING.md`](./tools/xerj-code/hub/CONTRIBUTING.md) before
opening one** — it has the templates, the licence rules (which sources are
adapt-freely, which are read-the-design-write-your-own, and why the difference is not a
technicality), and the review checklist that decides how fast your PR merges.

## Consume, in three commands

```sh
xerj corpus add --from https://raw.githubusercontent.com/xerj-org/xerj/corpus-hub/tools/xerj-code/hub/xerj-storage.json
xerj corpus index xerj-storage
xerj code xerj-storage "flush epoch crash recovery"
```

Or install a published, signed pack (the [`rust-vulns`](./tools/packs/rust-vulns/) daily
advisory pack) — exact lines in [`docs/CORPUS_PACKS.md`](./docs/CORPUS_PACKS.md).

## What is here today

| corpus | lane | contents | use it for |
|---|---|---|---|
| [`xerj-search`](./tools/xerj-code/hub/xerj-search.json) | reference | lucene, tantivy, quickwit, meilisearch, sonic, elasticsearch | FTS, BM25, merge policy, ES wire semantics |
| [`xerj-vector`](./tools/xerj-code/hub/xerj-vector.json) | reference | qdrant, usearch, instant-distance, hnswlib | HNSW construction, quantisation, filtered kNN |
| [`xerj-storage`](./tools/xerj-code/hub/xerj-storage.json) | reference | sled, fjall, redb | WAL, crash recovery, compaction |
| [`xerj-columnar`](./tools/xerj-code/hub/xerj-columnar.json) | reference | clickhouse | columnar layout, codecs, vectorised scans |
| [`rust-vulns`](./tools/packs/rust-vulns/) | pack | 1,950 identity-resolved Rust advisories | vulnerability precedent, affected-function lookup |

## Ground rules, short form

1. **A corpus is for a domain a reviewer can name.** "Everything" retrieves like a search
   engine with no query. Say what the corpus is *for*.
2. **Licences are reviewed by a human, per source.** The detector has been wrong in both
   directions (it once read Elasticsearch's triple licence as Apache-2.0 because the AGPL
   text contains the phrase «an "Apache License 2.0" compatible license»). Your PR fills
   a `review` block per source; CI checks it exists, not that you were right.
3. **Pins are frozen on purpose.** A shared SHA is what makes two people's retrieval
   results comparable. Moving one is its own PR with a reason.
4. **No pack binaries in git.** Recipes and definitions only; built packs are signed
   Release assets attached by maintainers after review.

Validation runs on every PR to this branch
([`.github/workflows/corpus-hub-validate.yml`](./.github/workflows/corpus-hub-validate.yml)).
The general engineering bar is [`CONTRIBUTING.md` on `main`](https://github.com/xerj-org/xerj/blob/main/CONTRIBUTING.md);
the corpus-specific rules live in the hub guide.
