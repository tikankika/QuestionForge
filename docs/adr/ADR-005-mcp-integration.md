# ADR-005: MCP Integration (Pipeline Calls Scaffolding)

## Status
**Accepted**

## Date
2026-01-02

## Context

With two MCPs:
- **MCP 1 (qf-scaffolding)**: Pedagogical methodology (M1-M4)
- **MCP 2 (qf-pipeline)**: Technical pipeline (Steps 1-4)

Original requirement stated:
> "a new mcp that scaffolds the generations of questions but **can be used in the other mcp** - for example to check if distractors are ok"

Question: Should MCP 2 be able to call MCP 1 for analysis tasks?

## Options

### Option A: Fully Separate MCPs
- MCP 1 and MCP 2 never call each other
- Teacher uses MCP 1, then separately uses MCP 2
- **Pros**: Simple, no inter-MCP complexity
- **Cons**: Duplicate analysis logic, or no pedagogical analysis in pipeline

### Option B: MCP 2 Calls MCP 1
- MCP 2 can call MCP 1 M4 (QA) for pedagogical analysis
- Specifically in Step 1.5 (Summary Analysis)
- **Pros**: Reuse analysis logic, better quality checking
- **Cons**: More complex, inter-MCP communication

### Option C: Shared Library
- Extract analysis into shared library used by both
- **Pros**: Clean reuse
- **Cons**: Third component to maintain, extraction effort

## Decision

**Option B: MCP 2 Calls MCP 1 (in Step 1.5)**

```
MCP 2: qf-pipeline
│
├── Step 1: Guided Build
│   └── Question-by-question FORMAT validation (MCP 2 only)
│
├── Step 1.5: Summary Analysis (FUTURE)
│   ├── Variation of questions check
│   ├── Final distractor analysis        ← CALLS MCP 1 M4
│   ├── Language consistency check        ← CALLS MCP 1 M4
│   └── Pedagogical quality review        ← CALLS MCP 1 M4
│
├── Step 2: Validator
├── Step 3: Decision
└── Step 4: Export
```

**Key constraint:** Integration happens in Step 1.5 (FUTURE), NOT in Step 1.

## Rationale

1. **Clear separation maintained**: Step 1 = FORMAT only, Step 1.5 = PEDAGOGY
2. **Single source of truth**: Pedagogical analysis lives in MCP 1 only
3. **No duplication**: Don't reimplement distractor analysis in MCP 2
4. **Future development**: Step 1.5 is planned, not immediate
5. **Flexibility**: Can build and use Step 1 before Step 1.5 exists

## Consequences

### Positive
- Pedagogical logic not duplicated
- MCP 1 M4 (QA) is reusable
- Clear separation: format (MCP 2) vs pedagogy (MCP 1)
- Phased development possible

### Negative
- MCP 2 has dependency on MCP 1 (for Step 1.5)
- Inter-MCP communication complexity
- Both MCPs must be available for full functionality

### Mitigation
- Step 1.5 is optional/future - Step 1-4 work without it
- Clear interface definition between MCPs
- Document dependency in deployment instructions

## Future Development (Step 1.5)

When implemented, Step 1.5 will provide:
- Summary check of all questions together
- Variation analysis across question bank
- Final distractor quality check
- Language/terminology consistency
- All delegating pedagogical analysis to MCP 1 M4

## Validation
- [ ] Step 1-4 work without MCP 1 (basic functionality)
- [ ] Step 1.5 successfully calls MCP 1 M4 (when implemented)
- [ ] Analysis results returned correctly to MCP 2

---

*ADR-005 | QuestionForge | 2026-01-02*
