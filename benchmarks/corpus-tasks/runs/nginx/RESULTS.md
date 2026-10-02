# nginx — RESULTS (2026-10-02)

Suite: `tasks/nginx.json`, 10 tasks (10 drift-anchored, 0 state), pin `2b5c2b605b`. Generated + graded from the pinned clone.

| arm | solved | cost | wall | turns | corpus calls |
|-----|--------|------|------|-------|--------------|
| P (bare) | **0/10** | $1.51 | 543 s | 10 | 0 |
| X (corpus+XERJ) | **10/10** | $1.60 | 315 s | 56 | 25 |

Drift-anchored subset: P 0/10, X 10/10.

## Per-task

| task | class | kind | P | X | X calls |
|------|-------|------|---|---|---------|
| T1 | drift | added | ❌ | ✅ | 2 |
| T2 | drift | added | ❌ | ✅ | 1 |
| T3 | drift | added | ❌ | ✅ | 1 |
| T4 | drift | added | ❌ | ✅ | 2 |
| T5 | drift | added | ❌ | ✅ | 2 |
| T6 | drift | added | ❌ | ✅ | 2 |
| T7 | drift | added | ❌ | ✅ | 7 |
| T8 | drift | added | ❌ | ✅ | 2 |
| T9 | drift | added | ❌ | ✅ | 2 |
| T10 | drift | added | ❌ | ✅ | 4 |

Grades: `runs/nginx/grades.jsonl` (one JSON per run in T<n>-<arm>/grade.json).
