# libuv — RESULTS (2026-10-02)

Suite: `tasks/libuv.json`, 10 tasks (10 drift-anchored, 0 state), pin `49b1c06471`. Generated + graded from the pinned clone.

| arm | solved | cost | wall | turns | corpus calls |
|-----|--------|------|------|-------|--------------|
| P (bare) | **5/10** | $1.30 | 487 s | 10 | 0 |
| X (corpus+XERJ) | **10/10** | $1.18 | 228 s | 36 | 14 |

Drift-anchored subset: P 5/10, X 10/10.

## Per-task

| task | class | kind | P | X | X calls |
|------|-------|------|---|---|---------|
| T1 | drift | changed | ❌ | ✅ | 1 |
| T2 | drift | changed | ✅ ⚠️guessable | ✅ | 1 |
| T3 | drift | added | ✅ | ✅ | 2 |
| T4 | drift | changed | ❌ | ✅ | 1 |
| T5 | drift | added | ✅ | ✅ | 1 |
| T6 | drift | added | ✅ | ✅ | 1 |
| T7 | drift | added | ❌ | ✅ | 1 |
| T8 | drift | added | ❌ | ✅ | 2 |
| T9 | drift | added | ❌ | ✅ | 3 |
| T10 | drift | added | ✅ | ✅ | 1 |

Grades: `runs/libuv/grades.jsonl` (one JSON per run in T<n>-<arm>/grade.json).
