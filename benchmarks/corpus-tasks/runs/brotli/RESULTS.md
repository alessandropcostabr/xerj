# brotli — RESULTS (2026-10-02)

Suite: `tasks/brotli.json`, 10 tasks (10 drift-anchored, 0 state), pin `42a2ed4355`. Generated + graded from the pinned clone.

| arm | solved | cost | wall | turns | corpus calls |
|-----|--------|------|------|-------|--------------|
| P (bare) | **1/10** | $1.10 | 411 s | 13 | 0 |
| X (corpus+XERJ) | **9/10** | $1.09 | 226 s | 40 | 18 |

Drift-anchored subset: P 1/10, X 9/10.

## Per-task

| task | class | kind | P | X | X calls |
|------|-------|------|---|---|---------|
| T1 | drift | added | ❌ | ✅ | 1 |
| T2 | drift | added | ❌ | ✅ | 1 |
| T3 | drift | added | ❌ | ❌ | 2 |
| T4 | drift | changed | ❌ | ✅ | 3 |
| T5 | drift | added | ❌ | ✅ | 2 |
| T6 | drift | added | ❌ | ✅ | 1 |
| T7 | drift | added | ✅ ⚠️guessable | ✅ | 4 |
| T8 | drift | changed | ❌ | ✅ | 2 |
| T9 | drift | changed | ❌ | ✅ | 1 |
| T10 | drift | changed | ❌ | ✅ | 1 |

Grades: `runs/brotli/grades.jsonl` (one JSON per run in T<n>-<arm>/grade.json).
