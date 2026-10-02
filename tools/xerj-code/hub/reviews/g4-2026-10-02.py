#!/usr/bin/env python3
"""One-shot G4 application: hand-review verdicts -> hub/<slug>.json, drafts consumed.
Verdict method: the profiler's git-show licence read at the pin for the common
permissive families (evidence retained in each review.note), PLUS hand opens for
every UNKNOWN / restricted-suspect / hint-conflict (21 repos, /tmp/g4read.py run
2026-10-02, output quoted in notes). Two detector false-positives found and
recorded: mozilla-ssl-configs and openbao both hinted GPL-2.0, both are MPL-2.0.
"""
import json, pathlib

HUB = pathlib.Path(__file__).parent
DRAFTS, BACKLOG = HUB / "drafts", HUB / "backlog" / "backlog-100.json"
BY, AT = "xerj-org", "2026-10-02"
A = "adapt-with-attribution"

# slug -> {repo: (spdx, use, note)}
V = {
# ---- DATA
"duckdb": {"duckdb": ("MIT", A, "LICENSE at pin: MIT (DuckDB Labs/Zeteo).")},
"rocksdb": {"rocksdb": ("GPL-2.0 OR Apache-2.0 (Apache selected)", A, "README License section at pin: dual GPLv2/Apache-2.0 choose-one; COPYING is the GPLv2 text, Apache-2.0 selected for corpus use.")},
"leveldb": {"leveldb": ("BSD-3-Clause", A, "LICENSE at pin: 3-clause BSD, LevelDB Authors 2011.")},
"badger": {"badger": ("Apache-2.0", A, "LICENSE at pin: Apache-2.0 — backlog hint said MIT, evidence over hint (dgraph-era relicence did reach badger).")},
"lmdb": {"lmdb": ("OpenLDAP-2.8", A, "no top-level file; opened libraries/liblmdb/LICENSE (OpenLDAP Public License 2.8) + COPYRIGHT (Howard Chu/Symas). Code lives in libraries/liblmdb/ on the default branch.")},
"faiss": {"faiss": ("MIT", A, "LICENSE at pin: MIT.")},
"annoy": {"annoy": ("Apache-2.0", A, "LICENSE at pin: Apache-2.0 (hint was unsure).")},
"sqlite-src": {"sqlite-src": ("Public-Domain (SQLite blessing)", A, "LICENSE.md at pin: 'SQLite Is Public Domain', affidavit statement; whole repo public domain per sqlite.org/copyright.html.")},
"postgres-src": {"postgres-src": ("PostgreSQL", A, "COPYRIGHT at pin: PostgreSQL Licence (BSD-family).")},
"parquet-format": {"parquet-format": ("Apache-2.0", A, "LICENSE at pin: Apache-2.0.")},
"arrow-rs": {"arrow-rs": ("Apache-2.0", A, "LICENSE.txt at pin: Apache-2.0.")},
"iceberg": {"iceberg": ("Apache-2.0", A, "LICENSE at pin: Apache-2.0.")},
"kafka-src": {"kafka-src": ("Apache-2.0", A, "LICENSE at pin: Apache-2.0.")},
"rabbitmq": {"rabbitmq": ("MPL-2.0 (core) AND Apache-2.0 (OCF parts)", A, "LICENSE at pin: core MPL 2.0 (LICENSE-MPL-RabbitMQ), some OCF files Apache-2.0. File-level copyleft only; snippet use with attribution fine.")},
"nats-server": {"nats-server": ("Apache-2.0", A, "LICENSE at pin: Apache-2.0.")},
"etcd-src": {"etcd-src": ("Apache-2.0", A, "LICENSE at pin: Apache-2.0.")},
"raft-rs": {"raft-rs": ("Apache-2.0", A, "LICENSE at pin: Apache-2.0 (hint BSD-2 wrong).")},
"dragonboat": {"dragonboat": ("Apache-2.0", A, "LICENSE at pin: Apache-2.0 (hint BSD-2 wrong).")},
"influxdb": {"influxdb": ("Apache-2.0 OR MIT", A, "LICENSE-APACHE + LICENSE-MIT both at pin: dual.")},
"prometheus-src": {"prometheus-src": ("Apache-2.0", A, "LICENSE at pin: Apache-2.0.")},
"valkey-src": {"valkey-src": ("BSD-3-Clause", A, "COPYING at pin: redis-derived 3-clause BSD (valkey fork).")},
# ---- STD
"whatwg-specs": {"whatwg-specs-1": ("CC-BY-4.0", A, "LICENSE at pin (whatwg/html): CC-BY-4.0."),
                 "whatwg-specs-2": ("CC-BY-4.0", A, "LICENSE at pin (whatwg/url): CC-BY-4.0.")},
"w3c-css": {"w3c-css": ("W3C-Software-And-Document", A, "LICENSE.md at pin: all documents under W3C Software and Document License (BSD-style with notice).")},
"ecma262": {"ecma262": ("Ecma-text-policy AND Ecma-MIT-software-policy", A, "LICENSE.md at pin: text under Ecma text copyright policy (alternative notice), code under Ecma MIT-style software policy.")},
"unicode-cldr": {"unicode-cldr": ("Unicode-ToU (UTS#35 notice at pin)", A, "LICENSE at pin is the pre-v3 UTS#35 copyright-and-permission notice (internal-copy language for the doc). CLDR data files are redistributed industry-wide under the Unicode ToU/Licence v3; Lane A pointer + attribution OK. Do NOT emit as a Lane B pack without re-review.")},
"openapi-spec": {"openapi-spec": ("Apache-2.0", A, "LICENSE at pin: Apache-2.0.")},
"json-schema-spec": {"json-schema-spec": ("BSD-2-Clause", A, "LICENSE at pin: BSD-family redistribution text (2-clause shape).")},
"graphql-spec": {"graphql-spec": ("JDF-charter (spec text (c) Facebook 2015-2018 + JDF)", A, "LICENSE.md appendix at pin defers to the JDF technical charter (technical-charter.graphql.org); open-spec terms with attribution. Re-check before any Lane B redistribution.")},
"nats-protocol": {"nats-protocol": ("Apache-2.0", A, "LICENSE at pin: Apache-2.0.")},
"kafka-protocol": {"kafka-protocol": ("Apache-2.0", A, "LICENSE at pin: Apache-2.0 (kafka-site, protocol guide included in tree).")},
"valkey-docs": {"valkey-docs": ("CC-BY-SA-4.0", "approach-only", "LICENSE+COPYRIGHT at pin: CC-BY-SA-4.0 (redis-doc lineage, Sanfilippo). ShareAlike term collides with serving derived snippets — approach-only; Lane A pointer only.")},
# ---- OPS
"gitlab-runbooks": {"gitlab-runbooks": ("MIT", A, "LICENSE at pin caae442685: MIT (GitLab); hosted on gitlab.com, cloned from there.")},
"otel-proto": {"otel-proto-1": ("Apache-2.0", A, "LICENSE at pin (opentelemetry-proto): Apache-2.0."),
               "otel-proto-2": ("Apache-2.0", A, "LICENSE at pin (semantic-conventions): Apache-2.0.")},
"etcd-docs": {"etcd-docs": ("CC-BY-4.0", A, "LICENSE at pin (etcd-io/website): CC-BY-4.0 for docs content.")},
"freebsd-handbook": {"freebsd-handbook": ("FreeBSD-Doc", A, "COPYRIGHT at pin: FreeBSD Project 1994-2026, 2-clause-style documentation licence (source+compiled forms).")},
"openbsd-faq": {"openbsd-faq": ("OpenBSD per-page copyright", A, "no LICENSE at pin cab1d91061; www module pages carry (c) OpenBSD notices, redistributable with notice retained. Corpus core is faq/ (98 pages) incl. the pf FAQ (faq6).")},
"tldr-pages": {"tldr-pages": ("MIT", A, "LICENSE.md at pin: MIT.")},
"school-of-sre": {"school-of-sre": ("CC-BY-4.0", A, "LICENSE at pin: CC-BY-4.0 (LinkedIn).")},
# ---- GOOD
"rust-api-guidelines": {"rust-api-guidelines": ("MIT OR Apache-2.0", A, "LICENSE-APACHE + LICENSE-MIT at pin: dual.")},
"google-eng-practices": {"google-eng-practices": ("CC-BY-3.0", A, "LICENSE at pin: CC Attribution 3.0 Unported — backlog hint said 4.0, evidence over hint.")},
"msft-api-guidelines": {"msft-api-guidelines": ("CC-BY-4.0", A, "license.txt (lowercase) at pin: CC-BY-4.0; the profiler's uppercase-only name list missed it — name list fixed.")},
"zalando-restful-api-guidelines": {"zalando-restful-api-guidelines": ("CC-BY-4.0", A, "LICENSE at pin: CC-BY-4.0.")},
"github-api-description": {"github-api-description": ("MIT", A, "LICENSE.md at pin: MIT.")},
"mozilla-ssl-configs": {"mozilla-ssl-configs": ("MPL-2.0", A, "DETECTOR FALSE POSITIVE: hinted GPL-2.0 (MPL text mentions GPL); opened LICENSE at pin: Mozilla Public License 2.0.")},
"osquery-config-examples": {"osquery-config-examples": ("MIT", A, "LICENSE.md at pin: MIT (Palantir).")},
"govuk-design-system": {"govuk-design-system": ("MIT", A, "LICENSE.txt at pin: MIT.")},
"twelve-factor": {"twelve-factor": ("MIT", A, "LICENSE at pin: MIT (site code + content).")},
# ---- NET
"rustls": {"rustls": ("Apache-2.0 OR MIT", A, "LICENSE-APACHE + LICENSE-MIT at pin: dual.")},
"openssl": {"openssl": ("Apache-2.0", A, "LICENSE.txt at pin: Apache-2.0 (3.x era).")},
"s2n-tls": {"s2n-tls": ("Apache-2.0", A, "LICENSE at pin: Apache-2.0.")},
"boringtun": {"boringtun": ("BSD-3-Clause", A, "LICENSE.md at pin: 3-clause BSD, Cloudflare 2019 (hint said Apache/BSD variants).")},
"quinn": {"quinn": ("Apache-2.0 OR MIT", A, "LICENSE-APACHE + LICENSE-MIT at pin: dual.")},
"nghttp2": {"nghttp2": ("MIT", A, "COPYING at pin: MIT (LICENSE is a pointer 'See COPYING').")},
"curl-src": {"curl-src": ("curl", A, "COPYING at pin: the curl licence (MIT-derived, SPDX: curl).")},
"libuv": {"libuv": ("MIT", A, "LICENSE at pin: MIT.")},
"zstd": {"zstd": ("mixed: BSD-3 (lib) / GPL-2.0 (cli)", "mixed", "LICENSE at pin: BSD (Meta) for lib/; COPYING: GPLv2 for programs — snippets outside lib/ are approach-only.")},
"lz4": {"lz4": ("mixed: BSD-2 (lib) / GPL-2.0+ (rest)", "mixed", "LICENSE at pin states the split explicitly: lib/ BSD 2-Clause, all other dirs GPL-2.0-or-later; snippets outside lib/ are approach-only.")},
"brotli": {"brotli": ("MIT", A, "LICENSE at pin: MIT.")},
"zlib-ng": {"zlib-ng": ("Zlib", A, "LICENSE.md at pin: zlib licence (Gailly/Adler).")},
"snappy": {"snappy": ("BSD-3-Clause", A, "COPYING at pin: Google 2011, 3-clause BSD.")},
"protobuf": {"protobuf": ("BSD-3-Clause", A, "LICENSE at pin: Google 2008 3-clause BSD.")},
"flatbuffers": {"flatbuffers": ("Apache-2.0", A, "LICENSE at pin: Apache-2.0.")},
"capnproto": {"capnproto": ("MIT", A, "LICENSE at pin: MIT.")},
"msgpack-c": {"msgpack-c": ("BSL-1.0", A, "COPYING + NOTICE at pin: Boost Software License 1.0.")},
"openbao": {"openbao": ("MPL-2.0", A, "DETECTOR FALSE POSITIVE: hinted GPL-2.0 (MPL 2.0 section 3.3 mentions GPL); opened LICENSE at pin: MPL-2.0 (HashiCorp 2015 lineage, MPL fork).")},
"caddy": {"caddy": ("Apache-2.0", A, "LICENSE at pin: Apache-2.0.")},
"envoy": {"envoy": ("Apache-2.0", A, "LICENSE at pin: Apache-2.0.")},
"nginx": {"nginx": ("BSD-2-Clause", A, "LICENSE at pin: 2-clause BSD.")},
}

written, dropped = [], []
for slug, verdicts in V.items():
    src = DRAFTS / f"{slug}.json"
    d = json.loads(src.read_text())
    for r in d["repos"]:
        spdx, use, note = verdicts[r["repo"]]
        prof_note = r["review"]["note"]
        r["review"] = {"spdx": spdx, "use": use, "by": BY, "at": AT,
                       "note": f"{note} | profiler evidence: {prof_note[:600]}"}
    (HUB / f"{slug}.json").write_text(json.dumps(d, indent=2) + "\n")
    src.unlink()
    written.append(slug)

# drafts whose rows are deferred/killed — discard, not review
for slug in ("mqtt-spec", "postmortems"):
    p = DRAFTS / f"{slug}.json"
    if p.exists():
        p.unlink(); dropped.append(slug)

# backlog: flip reviewed rows live; postmortems deferred
bl = json.loads(BACKLOG.read_text())
lived = set(written)
for r in bl["corpora"]:
    if r["slug"] in lived:
        r["status"] = "live"
    elif r["slug"] == "postmortems":
        r["status"] = "deferred"
        r["sources"] = [{"url": "https://github.com/danluu/post-mortems",
                         "licence_hint": "DEFERRED 2026-10-02: NO licence at pin 630562e5 (verified) AND the repo is a curated link index (7 files), not the postmortem text — real content sits on ~1k linked sites each with its own terms. Needs a Lane B curation with per-post licence review."}]
BACKLOG.write_text(json.dumps(bl, indent=1) + "\n")

import collections
print(f"{len(written)} manifests written, drafts dropped: {dropped}")
print("backlog:", dict(collections.Counter(r['status'] for r in bl['corpora'])))
left = sorted(p.stem for p in DRAFTS.glob('*.json'))
print("drafts remaining:", left or "none")
