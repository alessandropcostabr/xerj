# quinn — RESULTS (2026-10-02)

Suite: `tasks/quinn.json`, 10 tasks (10 drift-anchored, 0 state), pin `7f1c6b5508`. Generated + graded from the pinned clone.

| arm | solved | cost | wall | turns | corpus calls |
|-----|--------|------|------|-------|--------------|
| P (bare) | **0/10** | $0.86 | 281 s | 10 | 0 |
| X (corpus+XERJ) | **10/10** | $0.94 | 195 s | 32 | 14 |

Drift-anchored subset: P 0/10, X 10/10.

## Per-task

| task | class | kind | P | X | X calls |
|------|-------|------|---|---|---------|
| T1 | drift | added | ❌ | ✅ | 1 |
| T2 | drift | added | ❌ | ✅ | 1 |
| T3 | drift | added | ❌ | ✅ | 1 |
| T4 | drift | added | ❌ | ✅ | 2 |
| T5 | drift | added | ❌ | ✅ | 1 |
| T6 | drift | changed | ❌ | ✅ | 1 |
| T7 | drift | added | ❌ | ✅ | 2 |
| T8 | drift | added | ❌ | ✅ | 1 |
| T9 | drift | added | ❌ | ✅ | 2 |
| T10 | drift | changed | ❌ | ✅ | 2 |

Grades: `runs/quinn/grades.jsonl` (one JSON per run in T<n>-<arm>/grade.json).
