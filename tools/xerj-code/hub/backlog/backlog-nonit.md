# Non-IT corpus expansion — proposal (2026-10-02)

Beyond PROGRAM-100's engineering lanes. Selection bar is unchanged: G1 domain
coherence, G2 indexable shape, G3 un-memorisation (these domains drift
constantly — statutes amend, codes re-issue, guidance rewrites — so the
drift-anchored task instrument applies directly), G4 licence **verified at the
source, not assumed**, G5 pin truth, G6 validation, G7 retrieval spot-check.

The one structural difference from the IT lanes: most of these sources are not
git-hosted. Lane A entries therefore need a pinned mirror strategy (versioned
bulk XML/API snapshot committed to a repo, or a third-party git mirror whose
pin we record); Lane B entries become record-pack recipes like
`pattern-rust-vulns`.

Licence shorthand used below: PD = public domain / government edict (US) or
official-work exemption (DE §5 UrhG); OGL = UK Open Government Licence v3;
CC-* = Creative Commons; VERIFY = promising but the hub's verify-before-live
rule applies (sources are checked at fetch time, as G4 requires).

## A. Law & regulation (best drift in the whole proposal)

| slug | source | licence | lane | why people want it |
|------|--------|---------|------|--------------------|
| `uk-legislation` ✅ **LIVE (2026-10-02)** — [mirror](https://github.com/xerj-org/corpus-uk-legislation): all 418 ukpga 2015–2026, current version, 21k per-section files | legislation.gov.uk (RDF/XML API, every act + amendments since 1267) | OGL / PD | A | the only major legal system publishing full versioned XML openly; amendment drift is built in |
| `uscode` ⏸ deferred 2026-10-02: OLRC download centre is serving "Under Maintenance" and returns 403 on the zips; the community git mirrors are 2014–2022 stale (useless for current-law lookup); govinfo COMPS is per-act compilations, not per-code-title. Retry OLRC, then mirror per-title XML | Office of Law Revision Counsel US Code XML; community git mirrors exist | PD | A | title-level files, amended per public law |
| `ecfr-title-12` / `-26` / `-29` ✅ **LIVE (2026-10-02)** — mirrors [t12](https://github.com/xerj-org/corpus-ecfr-title-12) [t26](https://github.com/xerj-org/corpus-ecfr-title-26) [t29](https://github.com/xerj-org/corpus-ecfr-title-29): GPO bulk XML split per § section (12: 7.2k, 26: 6.2k, 29: 7.3k files), picked by demand rank (consumer-finance 71 / employment 57 / tax 40) | eCFR daily bulk XML — one corpus per high-traffic title (29 labor/OSHA, 21 food, 40 env, 49 transport); other titles follow demand | PD | A | "what does the regulation actually say" is the canonical look-it-up task |
| `eurlex` | EUR-Lex directives/regulations (CELEX-id chunking) | reuse w/ acknowledgement | A | EU-wide; multilingual variants possible later |
| `de-gesetze` | gesetze-im-internet.de federal laws XML | official works, free | A | German federal statutes, amend-drift |
| `nz-legislation` | legislation.govt.nz | CC BY 4.0 | A | clean licence, versioned |
| `scotus` | CourtListener bulk opinions | PD (opinions) | A | new opinions are permanently post-cutoff |
| `us-case-law` (per jurisdiction) | Harvard Caselaw Access Project, CC0 bulk | CC0 | B | millions of state/federal cases → record packs, query-built |
| `irs-pubs` | IRS publications + form instructions, yearly | PD | A | tax season is the highest-traffic "current value" lookup civilians do |
| `fatf-recs` | FATF recommendations | VERIFY | A | AML/compliance professionals |

Known-closed (documented so we stop re-litigating): ICC I-codes (© ICC —
free-view portal forbids redistribution), Eurocodes (CEN/national bodies sell),
NEC/ASTM/ASCE/ISO/DIN (all sold). The legal-adjacent world is where
"incorporated by reference but privately copyrighted" lives; that is exactly
why the open set above is worth curating.

## B. Construction & built environment

| slug | source | licence | lane | notes |
|------|--------|---------|------|-------|
| `uk-building-regs` | Approved Documents A–R | OGL | A | per-document shape; homeowners + pros |
| `mutcd` | FHWA Manual on Uniform Traffic Control Devices | PD | A | municipal crews, engineers; edition drift |
| `ufc` | DoD Unified Facilities Criteria (wholebuildingdesign.com) | PD (US gov) | A | **G2 risk: PDFs** — needs text extraction pass, the ecma262 single-giant-file lesson applies |
| `fema-p-series` | FEMA P-695/P-58/P-807 engineering methodology | PD | A | edition-based drift |
| `ada-2010` | DOJ ADA Standards + Access Board guides | PD | A | accessibility compliance |
| `hud-mps` | HUD Minimum Property Standards | PD | A | housing inspection |
| `nist-hb44` | NIST Handbook 44 (weights & measures) | PD | A | inspection professionals; yearly editions |
| `canada-nbc`, `ncc-au`, `eurocodes`, `icc` | — | **closed** | — | excluded on licence; recorded here deliberately |

## C. Health, food & safety

| slug | source | licence | lane | notes |
|------|--------|---------|------|-------|
| `fda-food-code` | FDA Food Code (4-year editions) | PD | A | edition drift is textbook drift-anchoring |
| `dailymed` | NLM DailyMed drug labels API | PD | B | labels revise constantly — record pack |
| `cdc-clinical` | CDC clinical guidance (STI, measles, immunization) | PD | A | rewritten post-cutoff |
| `usda-canning` | Complete Guide to Home Canning | PD | A | genuinely beloved civilian reference |
| `extension-ag` | land-grant university extension pubs | mostly PD/CC — VERIFY per source | A | gardening, food safety, 4-H |
| `mesh` / `rxnorm` | NLM vocabularies | PD | A/B | reference lookup |
| `nice-guidelines` | UK NICE | VERIFY (© NICE, free access) | A | clinical guidance with update versions |
| `icd-11`, `snomed` | WHO / SNOMED Intl | VERIFY / **closed** (SNOMOT licence is national-member gated) | — | ICD-11 browser terms need checking |

## D. Transport & aviation

| slug | source | licence | lane | notes |
|------|--------|---------|------|-------|
| `far-14cfr` | 14 CFR (FARs) | PD | A | pilots' daily lookup |
| `faa-advisory-circulars` | AC library | PD | A | constant revisions = drift |
| `navrules` | USCG navigation rules | PD | A | boaters |
| `fmcsa-49cfr` | 49 CFR motor carrier regs | PD | A | drivers/compliance |

## E. Money, work & consumer

| slug | source | licence | lane | notes |
|------|--------|---------|------|-------|
| `cfpb-12cfr` | CFPB regulations (Reg Z etc.) | PD | A | consumer-finance compliance |
| `ssa-poms` | SSA Program Operations Manual | PD | A | niche-loved, constantly revised |
| `cpsc-recalls` | recalls.gov | PD | B | record pack, keeps fresh |

## Instrument note

These domains fit the existing measurement unchanged: the drift-anchored
generator mines *any* versioned text for changed/added facts — statute section
values (amounts, thresholds, dates), code numeric requirements (stair rise,
loads), guidance dosages — and grades mechanically against the pin. The
"current value of X after the 2025 amendment" task is exactly the shape where
bare models serve stale memorised values; it is the lmdb/quinn finding applied
to law instead of code.

## Proposed first wave (12, licence-first order)

uk-legislation, uscode, ecfr-title-29, irs-pubs, scotus, eurlex, de-gesetze,
uk-building-regs, mutcd, far-14cfr, fda-food-code, usda-canning — then the
Lane B recipes (us-case-law, dailymed) which reuse the
pattern-rust-vulns pack builder.
