# ADR-013: QF-Scaffolding Migration Strategy

**Status:** Accepted  
**Date:** 2026-01-14  
**Deciders:** Niklas  
**Related:** ADR-001 (Two MCP Architecture), ADR-002 (Module Naming)

---

## Context

QuestionForge needs a methodology guidance MCP (qf-scaffolding) to help teachers create assessment questions through structured pedagogical processes.

We have existing resources:
1. **MPC_MQG_v3** - Existing TypeScript MCP with BB6 conversion tools
2. **MQG_0.2** - Comprehensive methodology documentation (43 files)
3. **assessment-mcp** - Reference implementation with similar pattern

Questions to decide:
- How to build qf-scaffolding?
- What to reuse from existing code?
- Where to place methodology files?

---

## Decision

### 1. Follow assessment-mcp Pattern

Separate methodology documents from code:

```
qf-scaffolding/
├── methodology/          ← Markdown files (editable without code changes)
│   ├── m1/
│   ├── m2/
│   ├── m3/
│   └── m4/
└── src/
    └── core/
        └── module_loader.ts  ← Reads methodology at runtime
```

**Rationale:**
- Proven pattern in assessment-mcp
- Methodology updates don't require code changes
- Clear separation of concerns

### 2. Migration from MPC_MQG_v3

**Reuse:**
| Component | Action |
|-----------|--------|
| `tsconfig.json` | ✅ Copy and update |
| `package.json` structure | ✅ Copy and update |
| `src/utils/fileOps.ts` | ✅ Copy (generic utilities) |

**Remove (replaced by qf-pipeline):**
| Component | Reason |
|-----------|--------|
| `tools/applyBB6.ts` | → qf-pipeline step1 |
| `tools/validateBB6.ts` | → qf-pipeline step2 |
| `tools/showBBStatus.ts` | → qf-pipeline step0 |
| `tools/createManifest.ts` | → qf-pipeline step0 |
| `utils/bb6Converter.ts` | BB6-specific |
| `utils/manifest.ts` | → qf-pipeline session |

**Archive:** After migration, archive MPC_MQG_v3 as superseded.

### 3. Methodology Source

Copy MQG_0.2 to qf-scaffolding/methodology/:

| Source (MQG_0.2) | Target (qf-scaffolding) |
|------------------|-------------------------|
| bb1a-bb1h | methodology/m1/ |
| bb2a-bb2i | methodology/m2/ |
| bb4a-bb4e | methodology/m3/ |
| bb5a-bb5f | methodology/m4/ |

**Rationale:**
- Centralizes methodology with MCP
- Version controlled together
- Runtime loading allows updates

### 4. Minimal Tool Set

Start with 4 core tools:
1. `init` - Critical instructions
2. `list_modules` - Show modules with requirements
3. `load_stage` - Progressive methodology loading
4. `module_status` - Progress tracking

**Deferred (TBD):**
- `analyze_distractors` - Pending M4 review
- `check_language` - Pending M4 review

**Rationale:** YAGNI - don't build tools until methodology review shows they're needed.

---

## Consequences

### Positive
- Clean architecture following proven pattern
- Methodology editable without code changes
- Minimal initial complexity (4 tools)
- Clear migration path from existing code

### Negative
- Need to maintain methodology copy (vs. reference)
- May need to add tools later if methodology insufficient

### Neutral
- MPC_MQG_v3 will be archived (not deleted)
- Methodology review required before implementation complete

---

## Implementation

1. ~~Update spec to v2.1~~ ✅
2. ~~Create ACDM log~~ ✅
3. ~~Create this ADR~~ ✅
4. Review M1-M4 methodology
5. Copy methodology to qf-scaffolding
6. Create IMPLEMENT_handoff
7. Build qf-scaffolding

---

## Alternatives Considered

### A: Integrate into qf-pipeline (rejected)
- Would create one large MCP
- Mixes methodology guidance with technical processing
- Rejected: Different concerns, different MCPs

### B: Direct file reading without MCP (rejected)
- Claude could read methodology via Filesystem
- No progressive loading, no tracking
- Rejected: MCP provides better control

### C: Build from scratch (rejected)
- Ignore MPC_MQG_v3 entirely
- More work, lose useful utilities
- Rejected: fileOps.ts is valuable

---

*ADR-013 | QuestionForge | 2026-01-14*
