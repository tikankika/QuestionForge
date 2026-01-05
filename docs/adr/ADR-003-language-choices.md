# ADR-003: Language Choices (TypeScript + Python)

## Status
**Accepted**

## Date
2026-01-02

## Context

QuestionForge has two MCPs with different purposes:
- **MCP 1 (qf-scaffolding)**: Methodology guidance, pedagogical process
- **MCP 2 (qf-pipeline)**: Build, validate, export to QTI

Each MCP needs a language choice. Constraints:
- Existing QTI-Generator-for-Inspera is Python
- Existing assessment-mcp pattern uses TypeScript
- MCP SDK available in both TypeScript and Python

## Options

### Option A: All TypeScript
- Both MCPs in TypeScript
- **Pros**: Single language, consistent tooling
- **Cons**: Must rewrite Python QTI code in TypeScript

### Option B: All Python
- Both MCPs in Python
- **Pros**: Can directly use existing QTI code
- **Cons**: Breaks pattern from assessment-mcp, less familiar for methodology

### Option C: TypeScript + Python (Hybrid)
- MCP 1 (scaffolding): TypeScript
- MCP 2 (pipeline): Python
- **Pros**: Best of both - pattern consistency + code reuse
- **Cons**: Two languages to maintain

## Decision

**Option C: TypeScript + Python (Hybrid)**

| MCP | Language | Rationale |
|-----|----------|-----------|
| qf-scaffolding | TypeScript | Consistent with assessment-mcp pattern, methodology focus |
| qf-pipeline | Python | Wraps existing QTI-Generator-for-Inspera code |

## Rationale

1. **Don't rewrite working code**: QTI-Generator-for-Inspera Python code works and is tested
2. **Pattern consistency**: assessment-mcp (TypeScript) established good methodology patterns
3. **Right tool for job**: Python for data/export, TypeScript for structured methodology
4. **MCP SDK supports both**: No technical barrier to mixed languages
5. **Team familiarity**: Both languages well-understood

## Consequences

### Positive
- Preserve existing Python QTI export code
- Methodology MCP follows established patterns
- No major rewrites needed

### Negative
- Two languages in one project
- Developers need both TypeScript and Python knowledge
- Different build/deploy processes

### Mitigation
- Clear directory separation (`packages/qf-scaffolding/`, `packages/qf-pipeline/`)
- Separate package.json and pyproject.toml
- Document both setup processes

## Validation
- [ ] MCP 1 (TypeScript) builds and runs
- [ ] MCP 2 (Python) builds and runs
- [ ] Both MCPs can communicate via files/tools

---

*ADR-003 | QuestionForge | 2026-01-02*
