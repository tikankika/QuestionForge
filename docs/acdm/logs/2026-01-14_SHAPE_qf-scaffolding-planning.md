# ACDM Log: QF-Scaffolding Planning

**Date:** 2026-01-14  
**Phase:** SHAPE  
**Topic:** qf-scaffolding architecture, tool design, shared session  
**Participants:** Niklas + Claude

---

## Summary

Planning session for qf-scaffolding MCP - the methodology guidance component of QuestionForge. Established architecture, tool set, shared session with qf-pipeline, and M1 methodology review.

---

## Key Decisions

### 1. Architecture Pattern
**Decision:** Follow assessment-mcp pattern  
**Rationale:** Proven pattern with methodology/ separate from src/

### 2. Tool Set Reduced
**Decision:** 4 core tools (from original 8)

| Tool | Purpose |
|------|---------|
| `init` | Critical instructions (same as qf-pipeline) |
| `list_modules` | Show modules with requirements |
| `load_stage` | Progressive methodology loading |
| `module_status` | Progress tracking |

**TBD:** analyze_distractors, check_language (pending M4 review)

### 3. Flexible Entry Points
**Decision:** Modules are independent - teacher chooses start point  

| Entry Point | Description | Route |
|-------------|-------------|-------|
| A) Material | Har föreläsningar/slides | M1 → M2 → M3 → M4 → Pipeline |
| B) Objectives | Har lärandemål | M2 → M3 → M4 → Pipeline |
| C) Blueprint | Har plan | M3 → M4 → Pipeline |
| D) Questions | Har markdown | Pipeline direkt |

### 4. SHARED SESSION (Critical Decision)
**Decision:** qf-scaffolding och qf-pipeline delar session  
**Rationale:** Enhetlig UX, gemensam projektstruktur

**Implementation:**
- Båda MCP:er har SAMMA init output
- qf-pipeline `step0_start` skapar session
- qf-scaffolding läser och utökar session.yaml
- Gemensam projektstruktur

**Project Structure:**
```
project_name/
├── 00_materials/           ← INPUT för M1
├── 01_source/              ← Markdown frågor
├── 02_working/             ← Working copy
├── 03_output/              ← QTI export
├── methodology/            ← M1-M4 outputs
└── session.yaml            ← Utökad med methodology
```

### 5. Progressive Loading with Stage Gates
**Decision:** load_stage returnerar `requires_approval: boolean`  
**Rationale:** Tvingar Claude att vänta på lärarens godkännande mellan stages

---

## M1 Methodology Review

### Structure Analysis

| File | Purpose | Lines |
|------|---------|-------|
| bb1a | Introduction, principles, framework | ~200 |
| bb1b | Stage 0: Material Analysis (AI solo) | ~250 |
| bb1c | Stage 1: Initial Validation | ~180 |
| bb1d | Stage 2: Emphasis Refinement | ~280 |
| bb1e | Stage 3: Example Catalog | ~200 |
| bb1f | Stage 4: Misconception Analysis | ~200 |
| bb1g | Stage 5: Scope & Objectives | ~400 |
| bb1h | Facilitation Best Practices | ~150 |

**Total:** ~1860 lines, 8 files

### Key Findings

1. **Bra struktur:** Tydlig "FOR CLAUDE" / "FOR TEACHERS" separation
2. **Stage gates:** Redan inbyggda STOP checkpoints i markdown
3. **Progressive building:** Varje stage bygger på föregående
4. **Adaptive inquiry:** "Adapt based on responses" - inte rigid checklista

### Stage Mapping for qf-scaffolding

| Index | File | Original |
|-------|------|----------|
| 0 | intro.md | bb1a |
| 1 | stage0.md | bb1b |
| 2 | stage1.md | bb1c |
| 3 | stage2.md | bb1d |
| 4 | stage3.md | bb1e |
| 5 | stage4.md | bb1f |
| 6 | stage5.md | bb1g |
| 7 | best_practices.md | bb1h |

---

## User Flow Design

### Init → Choice → Session → Route

```
User: "Jag vill skapa quiz-frågor"

Claude: init
        ↓
        "Vad har du?"
        A) Material → M1-M4
        B) Lärandemål → M2-M4
        C) Blueprint → M3-M4
        D) Frågor → Pipeline

User: "A - jag har föreläsningar"

Claude: step0_start (qf-pipeline)
        ↓
        Session skapad!
        
Claude: list_modules (qf-scaffolding)
        ↓
        "Börja med M1?"

User: "Ja"

Claude: load_stage(m1, 0) → intro
        ... progressiv laddning ...
```

---

## Open Questions (Resolved)

| Question | Resolution |
|----------|------------|
| Progressiv vs alla filer | ✅ Progressiv laddning |
| Init i vilken MCP? | ✅ Båda har samma init output |
| Vem skapar session? | ✅ qf-pipeline step0_start |
| Stage gate implementation | ✅ requires_approval i load_stage |

---

## Artifacts Created

| File | Version | Location |
|------|---------|----------|
| Spec | v2.2 | `docs/specs/qf-scaffolding-spec.md` |
| This log | - | `docs/acdm/logs/2026-01-14_SHAPE_qf-scaffolding-planning.md` |
| ADR-013 | - | `docs/adr/ADR-013-qf-scaffolding-migration.md` |

---

## Implementation Plan

### Phase 1: Preparation ✅ COMPLETE
- [x] Update spec to 4 core tools (v2.1)
- [x] Create ACDM log
- [x] Create ADR-013
- [x] Design shared session architecture (v2.2)
- [x] Review M1 methodology

### Phase 2: Remaining Methodology Review
- [x] Review M1 (bb1a-bb1h) - 8 files ✅
- [x] Review M2 (bb2a-bb2i) - 9 files ✅
- [x] Review M3 (bb4a-bb4e) - 5 files ✅
- [x] Review M4 (bb5a-bb5f) - 6 files ✅
- [x] Document stage patterns ✅
- [x] Decision: analyze_distractors NOT needed ✅

### Phase 3: Preparation for Implementation
- [x] Create ADR-014 (shared session) ✅
- [x] Copy methodology to QuestionForge ✅ (redan fanns!)
- [x] Document M2-M4 analysis ✅
- [ ] Create IMPLEMENT_handoff for M2-M4

### Phase 4: Implementation (Code)
- [ ] Create qf-scaffolding structure
- [ ] Implement session_reader.ts
- [ ] Implement 4 core tools
- [ ] Test with M1

---

## PENDING IMPLEMENTATION

Beslut fattade - status uppdaterad 2026-01-15:

| ID | Beslut | Fil att ändra | Prioritet | Status |
|----|--------|---------------|-----------|--------|
| P1 | `step0_start` behöver `materials_folder` param | qf-pipeline/server.py | HIGH | READY (handoff created) |
| P2 | `step0_start` behöver `entry_point` param | qf-pipeline/server.py | HIGH | ✅ DONE |
| P3 | `init` output ska inkludera A/B/C/D routing | qf-pipeline/server.py | HIGH | ✅ DONE |
| P4 | Projektstruktur ska inkludera `00_materials/` | qf-pipeline/session_manager.py | MEDIUM | ✅ DONE |
| P5 | Projektstruktur ska inkludera `methodology/` | qf-pipeline/session_manager.py | MEDIUM | ✅ DONE |
| P6 | Kopiera metodologi bb* → methodology/m*/ | qf-scaffolding | MEDIUM | ✅ DONE (redan fanns!) |
| P7 | Skapa `session_reader.ts` i qf-scaffolding | qf-scaffolding | MEDIUM | TODO |

**STATUS:** 6 av 7 items KLARA ✅  
**Se:** `docs/METHODOLOGY_STATUS.md` för fullständig uppdatering  
**Nästa:** P7 (session_reader.ts) efter M2-M4 granskning

---

## Next Steps

1. ~~Create ADR-014 for shared session decision~~ ✅
2. Review M2 methodology (when ready)
3. Review M3 methodology
4. Review M4 methodology (critical for tool decision)
5. Implement P1-P5 (qf-pipeline changes)
6. Copy and rename methodology files (P6)
7. Create IMPLEMENT_handoff for qf-scaffolding

---

*Log updated: 2026-01-14*
