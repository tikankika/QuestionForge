# PLAN Phase (Implementation Layer)

You are in the PLAN phase of ACDM implementation.

## Prerequisites

- EXPLORE phase complete
- Codebase understood
- No blocking questions

## Your Task

Create a concrete implementation plan before coding.

## Steps

1. **Break Down the Work**
   - List specific changes needed
   - Order by dependency (what must come first?)
   - Estimate complexity of each step

2. **Define Test Strategy**
   - What unit tests?
   - What integration tests?
   - How to verify each step?

3. **Use Extended Thinking (if complex)**
   - Standard: just plan
   - Complex algorithm: "think"
   - Multiple systems: "think hard"
   - Architecture: "ultrathink"

4. **Create Plan Document (optional)**
   For complex tasks, write plan to file:
   `docs/tasks/[task]-plan.md`

## Plan Format

```markdown
## Implementation Plan: [Task]

### Step 1: [Name]
- Files: [files to touch]
- Changes: [what to do]
- Tests: [how to verify]

### Step 2: [Name]
...

### Risks
- [potential issue]: [mitigation]

### Order of Operations
1. [first thing]
2. [second thing]
...
```

## Rules

- ❌ Do NOT start coding yet
- ✅ Think through edge cases
- ✅ Consider test strategy
- ✅ Identify risks
- ✅ Plan for TDD (test first)

## Extended Thinking Guide

| Complexity | Command | When |
|------------|---------|------|
| Simple | (none) | Straightforward changes |
| Medium | "think" | Algorithm design |
| High | "think hard" | Multiple components |
| Critical | "ultrathink" | Architecture decisions |

## Output

Before moving to CODE:
- [ ] Steps defined
- [ ] Order clear
- [ ] Test strategy clear
- [ ] Risks identified
- [ ] Plan shared with human (for complex tasks)

## Next Phase

When plan is clear → `/impl-code` to start TDD implementation.

---

*ACDM v1.0 - Implementation Layer*
