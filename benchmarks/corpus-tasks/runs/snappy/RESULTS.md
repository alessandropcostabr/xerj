# snappy — RESULTS (2026-10-02)

Suite: `tasks/snappy.json`, 10 tasks (5 drift-anchored, 5 state), pin `9c28114a38`. Generated + graded from the pinned clone.

| arm | solved | cost | wall | turns | corpus calls |
|-----|--------|------|------|-------|--------------|
| P (bare) | **3/10** | $1.21 | 450 s | 10 | 0 |
| X (corpus+XERJ) | **10/10** | $1.58 | 304 s | 52 | 24 |

Drift-anchored subset: P 1/5, X 5/5.

## Per-task

| task | class | kind | P | X | X calls |
|------|-------|------|---|---|---------|
| T1 | drift | added | ❌ | ✅ | 1 |
| T2 | drift | added | ❌ | ✅ | 1 |
| T3 | drift | changed | ❌ | ✅ | 5 |
| T4 | drift | added | ✅ | ✅ | 2 |
| T5 | drift | changed | ❌ | ✅ | 2 |
| T6 | state |  | ❌ | ✅ | 2 |
| T7 | state |  | ❌ | ✅ | 3 |
| T8 | state |  | ❌ | ✅ | 2 |
| T9 | state |  | ✅ ⚠️guessable | ✅ | 2 |
| T10 | state |  | ✅ | ✅ | 4 |

Grades: `runs/snappy/grades.jsonl` (one JSON per run in T<n>-<arm>/grade.json).
