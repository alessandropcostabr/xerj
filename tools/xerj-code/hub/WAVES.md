# Wave reports — PROGRAM-100

One section per wave, appended in order. The template below is the contract: the
misses are part of the report, a kill is a normal outcome, and reviewer-hours
keep the program honest about what 100 corpora actually costs.

```
## Wave N — <category>, <date opened>..<date closed>

| corpus | G1..G6 | G7 (relevant/5 queries) | status | notes |
|--------|--------|--------------------------|--------|-------|

- kills: <slug> — <gate that failed, one line of evidence>
- W-B drift: <manifests re-pinned / withdrawn, from profiler.py --check>
- reviewer-hours: <estimate>
- consume proof: <one xerj code line per live corpus, pasted>
```

## Wave 0 (bulk, all categories) — 2026-10-02

The program's first land is a bulk intake rather than a per-category wave: 73
backlog rows entered G1–G3 already judged (task #63), the profiler v2
(trees-only clones) pinned and gathered licence evidence for 70 of them, and
one session applied G4 across all of them. Recorded here because the amendment
in PROGRAM-100.md §1 was written for exactly this session and its conditions
were met in order: the stratified sample (2 per category, 50 pre-registered
queries in /root/g7/queries.json, graded manually) ran BEFORE any status
flipped to live.

**In: 68 manifests reviewed (G4) + 5 launch entries. Out: 71 live, 18 candidate,
7 deferred, 3 killed, 1 planned.**

Stratified G7 sample (10 corpora, 5 queries each, pre-registered, top-5 graded):

| corpus | G7 median | verdict |
|--------|-----------|---------|
| etcd-docs | 5.0 | pass |
| leveldb | 4.0 | pass |
| quinn | 4.0 | pass |
| google-eng-practices | 4.0 | pass |
| osquery-config-examples | 4.0 | pass |
| lmdb | 3.5 | pass |
| json-schema-spec | 3.5 | pass |
| boringtun | 3.0 | pass |
| ecma262 | 0.0 | **FAIL → demoted** |
| school-of-sre | 2.5 | **FAIL → demoted** |

Sample lessons (systemic, applied to the pending list's priorities):

- **Single-file giant HTML specs fail G2 outright.** ecma262's entire spec text
  is one 3MB spec.html; the indexer skips it and retrieval surfaces FAQ and
  CONTRIBUTING instead. Risk class on the pending list: whatwg-specs (html
  source), kafka-protocol (single-page protocol.html) — try those FIRST next
  cycle; the fix is section-split intake, not re-indexing.
- **Query vocabulary must be the corpus's vocabulary.** leveldb Q5 asked about
  "tombstones" — leveldb calls them deletions (1/5); school-of-sre queries that
  presumed an on-call chapter retrieved nothing because there is none. Rescope
  G1 domain sentences to actual content before re-running G7 — no query-shopping.
- **Whole-file md chunking is fine for spec repos** (json-schema-spec, etcd-docs
  medians 3.5–5): clause-level questions hit the right file every time.
- Duplicate-passage hits (same file ×5, e.g. school-of-sre replication.md) are
  redundant but not wrong; a dedup-by-file knob would improve precision margins.

G4 (licence review, 72 repos): all permissive families verified from the
licence text at the pin (profiler's git-show evidence retained in each
manifest's review.note; 21 ambiguous/restricted-suspect files hand-opened,
g4read.py output quoted). **Two detector false-positives found — both hinted
GPL-2.0, both actually MPL-2.0** (mozilla-ssl-configs, openbao: the MPL 2.0
text discusses GPL compatibility and the regex bit). Three hint corrections
where evidence over hint: badger is Apache-2.0 not MIT, google-eng-practices
is CC-BY-3.0 not 4.0, raft-rs/dragonboat Apache-2.0 not BSD. Verdicts:
66 adapt-with-attribution, 1 approach-only (valkey-docs CC-BY-SA-4.0),
2 mixed (lz4, zstd — BSD lib / GPL-2.0 programs; snippets outside lib/ are
approach-only).

Kills and defers this wave:

- killed: postgres-docs, sqlite-docs, prometheus-docs — same repository as
  their -src row; a second corpus over one repo is padding.
- deferred: ietf-rfc (no maintained full-text git mirror; needs an http
  tar.gz recipe), mqtt-spec (mqtt/mqtt.org is site chrome — the repo does NOT
  contain the spec text, verified at pin faab2e8a05; OASIS hosts it),
  postmortems (no licence at pin 630562e5 AND it is a link index, not the
  postmortem text — Lane B curation with per-post licence review).

W-B drift: profiler --check not re-run post-land (pins are hours old); first
scheduled pass with the next wave.

Pending G7s (58, the amendment's open list — deadline 2026-10-09, after which
each demotes to candidate automatically). Order: STD single-file-HTML risk
class first, then DATA/NET reference code, then OPS/GOOD prose. By category:
DATA 19, GOOD 7, NET 19, OPS 5, STD 8.

| corpus | cat | refresh | G7 due |
|--------|-----|---------|--------|
| whatwg-specs | STD | pinned | 2026-10-09 |
| w3c-css | STD | pinned | 2026-10-09 |
| unicode-cldr | STD | pinned | 2026-10-09 |
| openapi-spec | STD | pinned | 2026-10-09 |
| graphql-spec | STD | pinned | 2026-10-09 |
| nats-protocol | STD | pinned | 2026-10-09 |
| kafka-protocol | STD | pinned | 2026-10-09 |
| valkey-docs | STD | pinned | 2026-10-09 |
| gitlab-runbooks | OPS | pinned | 2026-10-09 |
| otel-proto | OPS | pinned | 2026-10-09 |
| freebsd-handbook | OPS | pinned | 2026-10-09 |
| openbsd-faq | OPS | pinned | 2026-10-09 |
| tldr-pages | OPS | weekly | 2026-10-09 |
| rust-api-guidelines | GOOD | pinned | 2026-10-09 |
| msft-api-guidelines | GOOD | pinned | 2026-10-09 |
| zalando-restful-api-guidelines | GOOD | pinned | 2026-10-09 |
| github-api-description | GOOD | weekly | 2026-10-09 |
| mozilla-ssl-configs | GOOD | pinned | 2026-10-09 |
| govuk-design-system | GOOD | pinned | 2026-10-09 |
| twelve-factor | GOOD | pinned | 2026-10-09 |
| duckdb | DATA | pinned | 2026-10-09 |
| rocksdb | DATA | pinned | 2026-10-09 |
| badger | DATA | pinned | 2026-10-09 |
| faiss | DATA | pinned | 2026-10-09 |
| annoy | DATA | pinned | 2026-10-09 |
| sqlite-src | DATA | pinned | 2026-10-09 |
| postgres-src | DATA | pinned | 2026-10-09 |
| parquet-format | DATA | pinned | 2026-10-09 |
| arrow-rs | DATA | pinned | 2026-10-09 |
| iceberg | DATA | pinned | 2026-10-09 |
| kafka-src | DATA | pinned | 2026-10-09 |
| rabbitmq | DATA | pinned | 2026-10-09 |
| nats-server | DATA | pinned | 2026-10-09 |
| etcd-src | DATA | pinned | 2026-10-09 |
| raft-rs | DATA | pinned | 2026-10-09 |
| dragonboat | DATA | pinned | 2026-10-09 |
| influxdb | DATA | pinned | 2026-10-09 |
| prometheus-src | DATA | pinned | 2026-10-09 |
| valkey-src | DATA | pinned | 2026-10-09 |
| rustls | NET | pinned | 2026-10-09 |
| openssl | NET | pinned | 2026-10-09 |
| s2n-tls | NET | pinned | 2026-10-09 |
| nghttp2 | NET | pinned | 2026-10-09 |
| curl-src | NET | pinned | 2026-10-09 |
| libuv | NET | pinned | 2026-10-09 |
| zstd | NET | pinned | 2026-10-09 |
| lz4 | NET | pinned | 2026-10-09 |
| brotli | NET | pinned | 2026-10-09 |
| zlib-ng | NET | pinned | 2026-10-09 |
| snappy | NET | pinned | 2026-10-09 |
| protobuf | NET | pinned | 2026-10-09 |
| flatbuffers | NET | pinned | 2026-10-09 |
| capnproto | NET | pinned | 2026-10-09 |
| msgpack-c | NET | pinned | 2026-10-09 |
| openbao | NET | pinned | 2026-10-09 |
| caddy | NET | pinned | 2026-10-09 |
| envoy | NET | pinned | 2026-10-09 |
| nginx | NET | pinned | 2026-10-09 |

Reviewer-hours: ~6 (bulk profiling 0.5, G4 pass 2, sample G7 incl. grading 2,
diagnoses and report 1.5).

Consume proof (sampled corpora, pasted from the run):

```
$ xerj corpus add --from tools/xerj-code/hub/leveldb.json && xerj corpus index leveldb --url http://localhost:9200
corpus 'leveldb' searchable: 2047 records
$ xerj code leveldb "where is the manifest file written and what does a version edit contain" --meatl
@ok f=leveldb/db/version_set.cc score=24.18 why=BSD
$ xerj code lmdb "how does the reader lock table let readers avoid blocking the writer" --meatl
@ok f=lmdb/libraries/liblmdb/mdb.c score=54.23 why=NONE-FOUND
$ xerj code etcd-docs "how do you defragment and compact etcd to reclaim database space" --meatl
@ok f=etcd-docs/content/en/blog/2023/how_to_debug_large_db_size_issue.md score=24.57 why=Apache-2.0
$ xerj code google-eng-practices "what should a reviewer look for in the first pass of a changelist" --meatl
@ok f=google-eng-practices/review/reviewer/looking-for.md score=8.93 why=UNKNOWN
```

The `why=NONE-FOUND` / `why=UNKNOWN` lines are the engine's licence detector,
not the G4 verdict — lmdb's licence lives in libraries/liblmdb/LICENSE and
google-eng-practices' is CC-BY-3.0, both recorded in the manifests' review
blocks. The detector disagreeing with the reviewed manifest is expected; the
manifest is the record.
