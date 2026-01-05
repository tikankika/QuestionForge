# CODE Phase (Implementation Layer)

You are in the CODE phase of ACDM implementation.

## Prerequisites

- PLAN phase complete
- Implementation steps defined
- Test strategy clear

## Your Task

Implement the solution using TDD (Test-Driven Development).

## TDD Workflow

```
┌─────────────────────────────────────────┐
│  1. Write test for expected behavior    │
│            ↓                            │
│  2. Run test → Confirm it FAILS         │
│            ↓                            │
│  3. Write MINIMAL code to pass          │
│            ↓                            │
│  4. Run test → Confirm it PASSES        │
│            ↓                            │
│  5. Refactor if needed                  │
│            ↓                            │
│  6. Repeat for next behavior            │
└─────────────────────────────────────────┘
```

## Steps

For each step in your plan:

1. **Write Test First**
   - Test the expected behavior
   - Test should FAIL initially

2. **Run Test**
   - Confirm it fails (red)
   - If it passes, test might be wrong

3. **Write Minimal Code**
   - Only enough to pass the test
   - Don't over-engineer

4. **Run Test Again**
   - Confirm it passes (green)
   - If fails, fix code

5. **Refactor**
   - Clean up code
   - Tests should still pass

6. **Commit Checkpoint**
   - Small, working increment
   - Clear commit message

## Rules

- ✅ Test first, then code
- ✅ Small increments
- ✅ Run tests frequently
- ✅ Commit working states
- ❌ Don't write code without test
- ❌ Don't skip failing test step
- ❌ Don't refactor while test is red

## Commit Checkpoints

Good checkpoint:
- Tests pass
- Feature increment complete
- Code is clean

Commit message format:
```
feat(component): add [feature]

- [what was added]
- [tests added]
```

## When to Escalate

Stop and ask human if:
- Spec is ambiguous
- Unexpected complexity found
- Tests reveal spec gap
- Blocked by external dependency

## Output

After CODE phase:
- [ ] All planned tests written
- [ ] All tests passing
- [ ] Code reviewed (self)
- [ ] Ready for COMMIT

## Next Phase

When implementation complete → `/impl-commit` to finalize.

---

*ACDM v1.0 - Implementation Layer*
