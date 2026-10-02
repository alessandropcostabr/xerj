# s2n-tls — RESULTS (2026-10-02)

Suite: `tasks/s2n-tls.json`, 10 tasks (10 drift-anchored, 0 state), pin `b170000016`. Generated + graded from the pinned clone.

| arm | solved | cost | wall | turns | corpus calls |
|-----|--------|------|------|-------|--------------|
| P (bare) | **1/10** | $0.86 | 263 s | 10 | 0 |
| X (corpus+XERJ) | **10/10** | $1.18 | 254 s | 37 | 25 |

Drift-anchored subset: P 1/10, X 10/10.

## Per-task

| task | class | kind | P | X | X calls |
|------|-------|------|---|---|---------|
| T1 | drift | added | ❌ | ✅ | 2 |
| T2 | drift | added | ✅ ⚠️guessable | ✅ | 1 |
| T3 | drift | added | ❌ | ✅ | 7 |
| T4 | drift | added | ❌ | ✅ | 5 |
| T5 | drift | added | ❌ | ✅ | 2 |
| T6 | drift | added | ❌ | ✅ | 2 |
| T7 | drift | added | ❌ | ✅ | 2 |
| T8 | drift | added | ❌ | ✅ | 2 |
| T9 | drift | added | ❌ | ✅ | 1 |
| T10 | drift | added | ❌ | ✅ | 1 |

Grades: `runs/s2n-tls/grades.jsonl` (one JSON per run in T<n>-<arm>/grade.json).
