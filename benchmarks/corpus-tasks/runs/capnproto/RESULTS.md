# capnproto — RESULTS (2026-10-02)

Suite: `tasks/capnproto.json`, 10 tasks (4 drift-anchored, 6 state), pin `e866bdbaa3`. Generated + graded from the pinned clone.

| arm | solved | cost | wall | turns | corpus calls |
|-----|--------|------|------|-------|--------------|
| P (bare) | **1/10** | $0.96 | 327 s | 15 | 0 |
| X (corpus+XERJ) | **10/10** | $1.05 | 221 s | 37 | 19 |

Drift-anchored subset: P 0/4, X 4/4.

## Per-task

| task | class | kind | P | X | X calls |
|------|-------|------|---|---|---------|
| T1 | drift | added | ❌ | ✅ | 3 |
| T2 | drift | added | ❌ | ✅ | 2 |
| T3 | drift | added | ❌ | ✅ | 2 |
| T4 | drift | added | ❌ | ✅ | 2 |
| T5 | state |  | ❌ | ✅ | 2 |
| T6 | state |  | ❌ | ✅ | 1 |
| T7 | state |  | ❌ | ✅ | 1 |
| T8 | state |  | ✅ ⚠️guessable | ✅ | 1 |
| T9 | state |  | ❌ | ✅ | 2 |
| T10 | state |  | ❌ | ✅ | 3 |

Grades: `runs/capnproto/grades.jsonl` (one JSON per run in T<n>-<arm>/grade.json).
