# ADR-001: Two-MCP Architecture

## Status
**Accepted**

## Date
2026-01-02

## Context

The Modular Question Generation (MQG) ecosystem had grown into a fragmented collection of overlapping tools:

- **QTI-Generator-for-Inspera_MPC**: 18 tools mixing validation, editing, conversion, analysis, export
- **MPC_MQG_v3**: 5 tools with duplicate validation functionality
- **Modular QGen Framework**: 46 documentation files (BB1-BB6)
- **QTI-Generator-for-Inspera** (GitHub): Python export code

Problems included:
- Functional duplication (validate_bb6 in multiple places)
- Unclear boundaries between tools
- No clear workflow connecting creation → validation → export
- Mixed pedagogical and technical concerns

We needed to decide how to restructure these tools into a coherent architecture.

## Options

### Option A: Single Monolithic MCP
- One MCP with all functionality
- **Pros**: Simple deployment, single context
- **Cons**: Violates separation of concerns, hard to maintain, mixed languages

### Option B: Five-Layer Architecture
- Five separate MCPs (Analyzer, Validator, Exporter, Builder, Scaffolding)
- **Pros**: Maximum separation
- **Cons**: Too complex, over-engineered, coordination overhead

### Option C: Two Focused MCPs
- MCP 1: Pedagogical scaffolding (methodology guidance)
- MCP 2: Technical pipeline (build, validate, export)
- **Pros**: Clear separation of concerns, manageable complexity, reusable
- **Cons**: Requires inter-MCP communication for some features

## Decision

**Option C: Two Focused MCPs**

```
MCP 1: qf-scaffolding (TypeScript)
├── M1: Content Analysis
├── M2: Assessment Planning
├── M3: Question Generation
└── M4: Quality Assurance
OUTPUT: Markdown questions

MCP 2: qf-pipeline (Python)
├── Step 1: Guided Build
├── Step 1.5: Summary Analysis (FUTURE)
├── Step 2: Validator
├── Step 3: Decision
└── Step 4: Export
OUTPUT: QTI package
```

## Rationale

1. **Clear responsibility split**: Pedagogy (MCP 1) vs Technical (MCP 2)
2. **Language alignment**: TypeScript for methodology (like assessment-mcp), Python to wrap existing QTI code
3. **Manageable complexity**: Two MCPs is simpler than five, more organized than one
4. **Reusability**: Each MCP can be used independently or together
5. **Future integration**: MCP 2 can call MCP 1 for pedagogical analysis (Step 1.5)

## Consequences

### Positive
- Clear workflow: scaffolding → pipeline → export
- Each MCP has single responsibility
- Easier to test and maintain independently
- Can upgrade/replace one without affecting other

### Negative
- Inter-MCP communication adds complexity (Step 1.5)
- Two deployment units instead of one
- Need shared specifications folder

### Mitigation
- Shared `qf-specifications/` folder for common definitions
- Clear interface between MCPs (markdown files)
- Step 1.5 (MCP integration) is future development

## Validation
- [ ] Both MCPs deployed and functional
- [ ] Full workflow tested end-to-end
- [ ] MCP 1 → MCP 2 handoff works via markdown files

---

*ADR-001 | QuestionForge | 2026-01-02*
