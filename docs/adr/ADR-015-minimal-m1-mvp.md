# ADR-015: Minimal M1 MVP Implementation

**Status:** Accepted  
**Date:** 2026-01-14  
**Deciders:** Niklas  
**Related:** ADR-014 (Shared Session), qf-scaffolding-spec.md v2.2

---

## Context

qf-scaffolding exists only as documentation (spec, methodology files). Entry point A (materials) requires M1 but no implementation exists yet.

**Current state:**
- ✅ Spec complete (qf-scaffolding-spec.md v2.2, 508 lines)
- ✅ Methodology exists (bb1a-bb1h in MQG_0.2, 8 files)
- ✅ Session architecture ready (ADR-014)
- ❌ 0% implementation (packages/qf-scaffolding/ is empty)

**User need:**
- User wants entry point A (materials → M1 → M2 → M3)
- Cannot wait for full qf-scaffolding (estimated 2-4 days)
- Needs M1 working TODAY (4-6 hours)

---

## Decision

Build **Minimal M1 MVP** with ONLY `load_stage` tool.

### What's IN (MVP Scope)

1. **Single tool: `load_stage`**
   - Reads bb1a-bb1h methodology files
   - Returns markdown content
   - Module: "m1" only (hardcoded)
   - Stages: 0-7 (bb1a through bb1h)

2. **Basic TypeScript MCP**
   - @modelcontextprotocol/sdk
   - Minimal error handling
   - No logging, no tests

3. **Methodology integration**
   - Copy bb1a-bb1h from MQG_0.2 to QuestionForge
   - Place in `packages/qf-scaffolding/methodology/m1/`
   - Simple file reader (fs/promises)

### What's OUT (Post-MVP)

- ❌ `init` tool (use qf-pipeline's init instead)
- ❌ `list_modules` tool
- ❌ `module_status` tool  
- ❌ Session tracking (no writes to session.yaml)
- ❌ M2, M3, M4 modules
- ❌ Progress persistence
- ❌ Comprehensive error handling
- ❌ Testing suite
- ❌ Logging

---

## Implementation

### Architecture (Minimal)

```
packages/qf-scaffolding/
├── package.json              ← Basic dependencies
├── tsconfig.json             ← Standard TypeScript config
├── src/
│   ├── index.ts             ← MCP server entry point
│   └── tools/
│       └── load_stage.ts    ← File reader
└── methodology/
    └── m1/                  ← Copied bb1a-bb1h
        ├── bb1a_Introduction_Framework.md
        ├── bb1b_Stage0_Material_Analysis.md
        ├── bb1c_Stage1_Initial_Validation.md
        ├── bb1d_Stage2_Emphasis_Refinement.md
        ├── bb1e_Stage3_Example_Catalog.md
        ├── bb1f_Stage4_Misconception_Analysis.md
        ├── bb1g_Stage5_Scope_Objectives.md
        └── bb1h_Facilitation_Best_Practices.md
```

### Tool: load_stage

**Input:**
```typescript
{
  module: "m1",           // Only M1 in MVP
  stage: 0-7              // 0=bb1a, 1=bb1b, ..., 7=bb1h
}
```

**Output:**
```typescript
{
  success: true,
  content: "# MQG_bb1a_Introduction_Framework\n\n..."
}
```

**Mapping:**
- Stage 0 → bb1a_Introduction_Framework.md
- Stage 1 → bb1b_Stage0_Material_Analysis.md
- Stage 2 → bb1c_Stage1_Initial_Validation.md
- Stage 3 → bb1d_Stage2_Emphasis_Refinement.md
- Stage 4 → bb1e_Stage3_Example_Catalog.md
- Stage 5 → bb1f_Stage4_Misconception_Analysis.md
- Stage 6 → bb1g_Stage5_Scope_Objectives.md
- Stage 7 → bb1h_Facilitation_Best_Practices.md

### Usage Example

```
User: "Jag vill analysera mitt kursmaterial"
Claude (qf-pipeline): init → visar A/B/C/D → user väljer A
Claude (qf-pipeline): step0_start(entry_point="materials")
Claude (qf-scaffolding): load_stage(module="m1", stage=0)
   ↳ Returns bb1a content
Claude: Visar Introduction, ber om bekräftelse
User: "Ok, fortsätt"
Claude: load_stage(module="m1", stage=1)
   ↳ Returns bb1b Stage 0 content
Claude: Faciliterar Stage 0 dialog enligt bb1b instruktioner
... fortsätter genom alla stages ...
```

---

## Consequences

### Positive

- ✅ M1 fungerar idag (4-6 timmar)
- ✅ Entry point A blir användbar
- ✅ User kan köra material analysis
- ✅ Liten kodbas = lätt att underhålla
- ✅ Kan utökas inkrementellt (M2-M4 senare)

### Negative

- ❌ Ingen progress tracking (måste köras i en session)
- ❌ Claude måste själv hålla reda på vilket stage user är på
- ❌ Ingen automatisk guidance mellan stages
- ❌ User kan inte "fortsätta senare" (ingen state saved)

### Mitigations

**Workaround för progress tracking:**
- Claude Desktop conversation = session state
- User säger "fortsätt där vi slutade"
- Claude kollar chat history för senaste stage

**När expandera till Full Version:**
- Efter Step 3 (Decision) klar i qf-pipeline
- Lägg till session tracking
- Lägg till init, list_modules, module_status
- Lägg till M2-M4

---

## Alternatives Considered

### A: Full qf-scaffolding nu (rejected)

**Scope:** All 4 tools, all 4 modules, full session tracking

**Time:** 2-4 days

**Rejected because:**
- User needs M1 TODAY
- Full implementation can wait
- MVP proves concept first

### B: Manual workflow (rejected)

**Approach:** User runs bb1a-bb1h manually in Claude Desktop without MCP

**Rejected because:**
- Less structured
- No tool integration
- Harder to maintain state
- User wanted MCP approach

### C: Hardcoded M1 responses (rejected)

**Approach:** Hardcode bb1 content in qf-pipeline init

**Rejected because:**
- Mixing concerns (pipeline vs methodology)
- Harder to update methodology
- Doesn't scale to M2-M4

---

## Implementation Timeline

| Task | Time | Status |
|------|------|--------|
| Copy bb1a-bb1h files | 5 min | ⬜ TODO |
| package.json setup | 10 min | ⬜ TODO |
| tsconfig.json | 5 min | ⬜ TODO |
| load_stage.ts | 2-3 hours | ⬜ TODO |
| index.ts (MCP server) | 1-2 hours | ⬜ TODO |
| Local testing | 30 min | ⬜ TODO |
| Claude Desktop config | 15 min | ⬜ TODO |

**TOTAL:** 4-6 hours

---

## Acceptance Criteria

MVP is complete when:

- [ ] bb1a-bb1h copied to `methodology/m1/`
- [ ] TypeScript compiles without errors
- [ ] `load_stage(module="m1", stage=0)` returns bb1a content
- [ ] Claude Desktop can call load_stage
- [ ] Claude can facilitate M1 Stage 0 dialogue
- [ ] User can complete full M1 workflow (stages 0-7)

---

## Post-MVP Roadmap

**Phase 2: Session Tracking**
- Add writes to session.yaml
- Track current_stage, loaded_stages
- Update methodology.m1.status

**Phase 3: Full Tools**
- Add `init` (return A/B/C/D routing)
- Add `list_modules` (return M1-M4)
- Add `module_status` (return progress)

**Phase 4: Additional Modules**
- M2 (Assessment Design)
- M3 (Question Generation)
- M4 (Quality Assurance)

---

*ADR-015 | QuestionForge | 2026-01-14*
