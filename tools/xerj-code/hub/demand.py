#!/usr/bin/env python3
"""demand.py — mine real Ask-HN questions for corpus demand signals.

Two measurements per domain:
  1. nbHits for domain keywords in Ask HN (all time, points>=3) — volume.
  2. a year-sample of Ask HN titles regex-matched to the domain — freshness
     and example questions (short quotes, links preserved in demand-raw.json).
Output: JSON to stdout (see backlog/demand-2026-10.md for the analysis).
"""
import json, re, time, urllib.request, urllib.parse

API = "https://hn.algolia.com/api/v1"

def get(path, **params):
    u = f"{API}/{path}?" + urllib.parse.urlencode(params)
    for _ in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "hub-demand-research/1.0"}), timeout=15) as r:
                return json.loads(r.read())
        except Exception:
            time.sleep(2)
    return {}

DOMAINS = {
  # existing hub corpora / adjacent
  "databases-sql":       r"\b(sql|sqlite|postgres|mysql|database index|query plan)\b",
  "key-value-storage":   r"\b(redis|valkey|lmdb|rocksdb|leveldb|badger|key[- ]value)\b",
  "web-servers-proxy":   r"\b(nginx|caddy|reverse proxy|envoy|haproxy)\b",
  "tls-crypto":          r"\b(tls|ssl certificate|openssl|certificate autokat|https cert)\b",
  "data-formats":        r"\b(parquet|arrow|protobuf|avro|flatbuffer|json schema|msgpack|csv format)\b",
  "messaging":           r"\b(kafka|rabbitmq|nats|message queue|mqtt)\b",
  "search-engines":      r"\b(elasticsearch|opensearch|full[- ]text search|meilisearch|typesense)\b",
  "vector-db":           r"\b(vector database|qdrant|hnsw|embedding search|rag)\b",
  "columnar-olap":       r"\b(clickhouse|duckdb|olap|columnar|analytics database)\b",
  "api-design":          r"\b(rest api design|openapi|graphql|api versioning|api guidelines)\b",
  "observability":       r"\b(prometheus|opentelemetry|grafana|metrics|tracing)\b",
  "os-sysprog":          r"\b(system programming|kernel|epoll|io_uring|memory allocator)\b",
  # non-IT proposal domains
  "building-construction": r"\b(building code|construction|contractor|stair|egress|zoning|renovat(e|ion)|permit)\b",
  "legal-courts":          r"\b(lawsuit|court case|statute|regulation|small claims|immigration|custody|lease agreement|copyright law)\b",
  "tax":                   r"\b(tax filing|IRS|1099|taxes|tax deductible|W-?2|capital gains tax)\b",
  "employment-hr":         r"\b(overtime|salary|fired|resign|FMLA|non[- ]compete|workplace rights)\b",
  "aviation":              r"\b(private pilot|part 107|drone license|PPL|aviation|flight rules)\b",
  "health-medical":        r"\b(diagnos(is|ed)|medication|drug interaction|side effects|clinical|treatment)\b",
  "food-safety":           r"\b(canning|food safety|food poisoning|expiration|pasteuriz)\b",
  "home-diY":              r"\b(plumb(ing)?|electrical wiring|drywall|HVAC|roof(ing)?)\b",
  "consumer-finance":      r"\b(credit score|mortgage|refinance|insurance claim|debt collect)\b",
  "radio-ham":             r"\b(ham radio|amateur radio|FCC license|antenna tuner)\b",
}

def sample_year():
    since = int(time.time()) - 365 * 86400
    titles = []
    for page in range(10):
        d = get("search_by_date", tags="ask_hn", numericFilters=f"created_at_i>{since},points>=2",
                hitsPerPage=100, page=page)
        hs = d.get("hits", [])
        if not hs:
            break
        titles += [((h.get("title") or "").strip(), h.get("points", 0), h.get("objectID")) for h in hs]
        time.sleep(0.6)
    return titles

def domain_volume():
    out = {}
    for dom, pat in DOMAINS.items():
        vol = {}
        queries = {
            "databases-sql": ["sqlite", "postgres"], "key-value-storage": ["redis", "lmdb"],
            "web-servers-proxy": ["nginx", "reverse proxy"], "tls-crypto": ["tls certificate", "openssl"],
            "data-formats": ["parquet", "protobuf"], "messaging": ["kafka", "rabbitmq"],
            "search-engines": ["elasticsearch", "full-text search"], "vector-db": ["vector database", "qdrant"],
            "columnar-olap": ["clickhouse", "duckdb"], "api-design": ["REST API design", "openapi"],
            "observability": ["prometheus", "opentelemetry"], "os-sysprog": ["io_uring", "memory allocator"],
            "building-construction": ["building code", "contractor"], "legal-courts": ["lawsuit", "small claims court"],
            "tax": ["tax filing", "IRS"], "employment-hr": ["overtime", "non-compete"],
            "aviation": ["private pilot", "part 107"], "health-medical": ["medication", "diagnosis"],
            "food-safety": ["food safety", "canning"], "home-diY": ["plumbing", "electrical wiring"],
            "consumer-finance": ["credit score", "mortgage"], "radio-ham": ["ham radio", "amateur radio"],
        }[dom]
        for q in queries:
            d = get("search", query=f'"{q}"', tags="ask_hn", numericFilters="points>=10", hitsPerPage=5)
            vol[q] = {"nbHits": d.get("nbHits", 0),
                      "examples": [(h.get("title"), h.get("points"),
                                    f"https://news.ycombinator.com/item?id={h.get('objectID')}")
                                   for h in d.get("hits", [])[:3] if h.get("title", "").startswith("Ask HN")] or
                                  [(h.get("title"), h.get("points"),
                                    f"https://news.ycombinator.com/item?id={h.get('objectID')}")
                                   for h in d.get("hits", [])[:2]]}
            time.sleep(0.5)
        out[dom] = vol
    return out

if __name__ == "__main__":
    titles = sample_year()
    rx = {d: re.compile(p, re.I) for d, p in DOMAINS.items()}
    matched = {d: [] for d in DOMAINS}
    for t, pts, oid in titles:
        for d, r in rx.items():
            if r.search(t):
                matched[d].append((t, pts, f"https://news.ycombinator.com/item?id={oid}"))
    vol = domain_volume()
    print(json.dumps({"sampled": len(titles),
                      "volume": vol,
                      "matched": {d: sorted(v, key=lambda x: -x[1])[:12] for d, v in matched.items()}},
                     indent=1))
