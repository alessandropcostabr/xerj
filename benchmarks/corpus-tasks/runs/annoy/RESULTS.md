# annoy — RESULTS (2026-10-02)

Suite: `tasks/annoy.json`, 10 tasks (0 drift-anchored, 10 state), pin `379f744667`. Generated + graded from the pinned clone.

| arm | solved | cost | wall | turns | corpus calls |
|-----|--------|------|------|-------|--------------|
| P (bare) | **5/10** | $1.14 | 472 s | 11 | 0 |
| X (corpus+XERJ) | **10/10** | $0.95 | 222 s | 33 | 16 |

Drift-anchored subset: P 0/0, X 0/0.

## Per-task

| task | class | kind | P | X | X calls |
|------|-------|------|---|---|---------|
| T1 | state |  | ❌ | ✅ | 1 |
| T2 | state |  | ✅ ⚠️guessable | ✅ | 3 |
| T3 | state |  | ❌ | ✅ | 1 |
| T4 | state |  | ❌ | ✅ | 1 |
| T5 | state |  | ❌ | ✅ | 1 |
| T6 | state |  | ❌ | ✅ | 1 |
| T7 | state |  | ✅ ⚠️guessable | ✅ | 2 |
| T8 | state |  | ✅ ⚠️guessable | ✅ | 2 |
| T9 | state |  | ✅ ⚠️guessable | ✅ | 1 |
| T10 | state |  | ✅ ⚠️guessable | ✅ | 3 |

Grades: `runs/annoy/grades.jsonl` (one JSON per run in T<n>-<arm>/grade.json).
