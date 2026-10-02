# influxdb — RESULTS (2026-10-02)

Suite: `tasks/influxdb.json`, 10 tasks (10 drift-anchored, 0 state), pin `06200ef96b`. Generated + graded from the pinned clone.

| arm | solved | cost | wall | turns | corpus calls |
|-----|--------|------|------|-------|--------------|
| P (bare) | **0/10** | $0.70 | 188 s | 10 | 0 |
| X (corpus+XERJ) | **10/10** | $1.16 | 357 s | 44 | 21 |

Drift-anchored subset: P 0/10, X 10/10.

## Per-task

| task | class | kind | P | X | X calls |
|------|-------|------|---|---|---------|
| T1 | drift | added | ❌ | ✅ | 1 |
| T2 | drift | added | ❌ | ✅ | 1 |
| T3 | drift | added | ❌ | ✅ | 1 |
| T4 | drift | added | ❌ | ✅ | 2 |
| T5 | drift | added | ❌ | ✅ | 4 |
| T6 | drift | added | ❌ | ✅ | 1 |
| T7 | drift | added | ❌ | ✅ | 4 |
| T8 | drift | added | ❌ | ✅ | 2 |
| T9 | drift | added | ❌ | ✅ | 2 |
| T10 | drift | changed | ❌ | ✅ | 3 |

Grades: `runs/influxdb/grades.jsonl` (one JSON per run in T<n>-<arm>/grade.json).
