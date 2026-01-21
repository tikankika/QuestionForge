# QuestionForge Roadmap

**Senast uppdaterad:** 2026-01-21

---

## Projektöversikt

QuestionForge är ett MCP-baserat verktyg för att skapa, validera och exportera quiz-frågor till QTI-format för Inspera.

---

## Fas 1: Grundläggande Pipeline ✅ KLAR

| Uppgift | Status | Datum |
|---------|--------|-------|
| Export wrappers (parser, generator, packager) | ✅ Klar | 2025-12 |
| MCP-server setup | ✅ Klar | 2025-12 |
| Validator wrapper | ✅ Klar | 2025-12 |
| Session management (step0_start, step0_status) | ✅ Klar | 2026-01-05 |
| GitHub repo skapat | ✅ Klar | 2026-01-05 |

---

## Fas 1.5: Refaktorering ✅ KLAR

### 1.5.1 Tool Naming Convention (ADR-007) ✅ KLAR
| Uppgift | Status | Datum |
|---------|--------|-------|
| Beslut: `stepN_` prefix | ✅ Klar | 2026-01-06 |
| Dokumenterat i ADR-007 | ✅ Klar | 2026-01-06 |
| Implementerat i server.py | ✅ Klar | 2026-01-07 |

### 1.5.2 Standalone Migration (ADR-008) ✅ KLAR
| Uppgift | Status | Datum |
|---------|--------|-------|
| DISCOVER-fas | ✅ Klar | 2026-01-06 |
| Beslut: Alternativ A (full kopia) | ✅ Klar | 2026-01-06 |
| Implementation: qti-core kopierad | ✅ Klar | 2026-01-07 |

**Resultat:**
- QTI-Generator-for-Inspera kopierad som `packages/qti-core/`
- 114 filer (exkl. .git, .venv, __pycache__, output)
- Wrapper-paths uppdaterade från absoluta till relativa
- QuestionForge är nu helt standalone

---

## Fas 2: Guided Build ✅ KLAR

### Step 1: Interactive Guided Build (Rebuild)
| Uppgift | Status | Datum |
|---------|--------|-------|
| Specifikation (STEP1_REBUILD_INTERACTIVE.md) | ✅ Klar | 2026-01-08 |
| `step1_analyze` - kategorisera issues | ✅ Klar | 2026-01-08 |
| `step1_fix_auto` - auto-fixable syntax | ✅ Klar | 2026-01-08 |
| `step1_fix_manual` - user input handling | ✅ Klar | 2026-01-08 |
| `step1_suggest` - generera förslag | ✅ Klar | 2026-01-08 |
| `step1_batch_preview` - batch preview | ✅ Klar | 2026-01-08 |
| `step1_batch_apply` - batch apply | ✅ Klar | 2026-01-08 |
| `step1_skip` - skippa fråga/issue | ✅ Klar | 2026-01-08 |

### Step 2: Validator ✅ KLAR
| Uppgift | Status | Datum |
|---------|--------|-------|
| Validation output improvement (ADR-012) | ✅ Klar | 2026-01-06 |
| `^tags` som alternativ till `^labels` | ✅ Klar | 2026-01-07 |
| step2_complete signal | ✅ Klar | 2026-01-08 |

---

## Fas 2.5: Shared Session (ADR-014) ✅ KLAR

**Beskrivning:** Delad session mellan qf-pipeline och qf-scaffolding

| Uppgift | Status | Datum |
|---------|--------|-------|
| ADR-014: Shared Session arkitektur | ✅ Klar | 2026-01-14 |
| 5 Entry Points (m1/m2/m3/m4/pipeline) | ✅ Klar | 2026-01-14 |
| source_file Optional för m1 | ✅ Klar | 2026-01-14 |
| Nya mappar: 00_materials/, methodology/ | ✅ Klar | 2026-01-14 |
| methodology sektion i session.yaml | ✅ Klar | 2026-01-14 |
| URL auto-fetch för source_file | ✅ Klar | 2026-01-14 |
| materials_folder parameter (m1) | ✅ Klar | 2026-01-16 |
| sources.yaml tracking | ✅ Klar | 2026-01-15 |
| Methodology copy till projekt | ✅ Klar | 2026-01-15 |

**Entry Points:**
| Entry Point | source_file | Nästa Modul |
|-------------|-------------|-------------|
| m1 | ❌ Valfri | M1 (scaffolding) |
| m2 | ✅ Krävs | M2 (scaffolding) |
| m3 | ✅ Krävs | M3 (scaffolding) |
| m4 | ✅ Krävs | M4 (scaffolding) |
| pipeline | ✅ Krävs | Pipeline direkt |

---

## Fas 3: Decision & Export ⏳ NÄSTA

### Step 3: Decision Tool (ADR-010, ADR-011)
| Uppgift | Status |
|---------|--------|
| ADR-010: Step 3 architecture | ✅ Föreslaget |
| ADR-011: Question Set Builder | ✅ Föreslaget |
| `step3_question_set` implementation | ⬜ Planerad |

**Två exportvägar:**
- **Path A:** Direkt export (enkla frågor → QTI)
- **Path B:** Question Set Builder (filtrering, sektioner, random selection)

### Step 4: Export ✅ KLAR
| Uppgift | Status |
|---------|--------|
| `step4_export` - generera QTI-paket | ✅ Klar |
| Tags → Labels mapping | ✅ Klar |
| Resource handling (bilder etc) | ✅ Klar |

---

## Fas 4: Unified Logging (RFC-001) ✅ KLAR

**Status:** TIER 1-2 Complete, TIER 3-4 planerade

### TIER 1-2: Implementerat ✅

| Uppgift | Status | Datum |
|---------|--------|-------|
| RFC-001 specifikation | ✅ Klar | 2026-01-16 |
| JSON Schema (qf-specifications/logging/) | ✅ Klar | 2026-01-16 |
| Python logger (RFC-001 compliant) | ✅ Klar | 2026-01-16 |
| TypeScript logger (qf-scaffolding) | ✅ Klar | 2026-01-17 |
| **TIER 1:** tool_start/end/error | ✅ Klar | 2026-01-17 |
| **TIER 2:** session_start/resume/end | ✅ Klar | 2026-01-17 |
| **TIER 2:** stage_start/complete | ✅ Klar | 2026-01-17 |
| **TIER 2:** validation_complete, export_complete | ✅ Klar | 2026-01-17 |

**TIER 1-2 events:**
| Event | Fil | Beskrivning |
|-------|-----|-------------|
| tool_start/end/error | server.py, load_stage.ts | Alla tool calls |
| session_start | session_manager.py | Ny session |
| session_resume | server.py | Återuppta session |
| session_end | session_manager.py | Avsluta session |
| stage_start/complete | load_stage.ts | M1-M4 stages |
| validation_complete | server.py | Validering lyckad |
| export_complete | server.py | Export klar |

### TIER 3: Audit Trail 🔄 Delvis

| Uppgift | Status | Beroende |
|---------|--------|----------|
| format_detected | ✅ Klar | - |
| format_converted | ✅ Klar | - |
| user_decision | ⬜ Planerad | M1-M4 implementation |

**Väntar på:** M1-M4 scaffolding implementation för att definiera user_decision events.

### TIER 4: ML Training ⏸️ Parkerad

| Uppgift | Status | Timeline |
|---------|--------|----------|
| user_decision (full context) | ⏸️ Parkerad | Q2-Q3 2026 |
| ai_suggestion | ⏸️ Parkerad | Q2-Q3 2026 |
| correction_made | ⏸️ Parkerad | Q2-Q3 2026 |

**Krav:** TIER 1-3 complete + >100 sessions insamlade. Se RFC-003.

**Filer:**
- `docs/rfcs/RFC-001-unified-logging.md`
- `docs/rfcs/RFC-003-ml-training-placeholder.md`
- `qf-specifications/logging/schema.json`

---

## Fas 5: qf-scaffolding 🔶 M1 IMPLEMENTATION KLAR

**Beskrivning:** TypeScript MCP för pedagogisk scaffolding (M1-M4)

### Grundläggande Setup ✅
| Uppgift | Status | Datum |
|---------|--------|-------|
| MVP: `load_stage` tool | ✅ Klar | 2026-01-14 |
| M1-M4 stage loading | ✅ Klar | 2026-01-16 |
| `requiresApproval` field | ✅ Klar | 2026-01-16 |
| Methodology files imported (28 filer) | ✅ Klar | 2026-01-14 |
| TypeScript logger (RFC-001) | ✅ Klar | 2026-01-17 |
| TIER 1-2 logging | ✅ Klar | 2026-01-17 |

### RFC-004: M1 Methodology Tools ✅
| Uppgift | Status | Datum |
|---------|--------|-------|
| Phase 0: `load_stage` path fix | ✅ Klar | 2026-01-17 |
| Phase 1: `read_materials`, `read_reference` | ✅ Klar | 2026-01-17 |
| Phase 2: `save_m1_progress` tool | ✅ Klar | 2026-01-19 |
| Phase 2: `read_materials` filename param | ✅ Klar | 2026-01-19 |
| Phase 2: `load_stage` stage numbering fix | ✅ Klar | 2026-01-19 |
| Workflow dokumentation (v3.0) | ✅ Klar | 2026-01-19 |

**RFC-004 Key Decisions:**
- Single document strategy: `m1_analysis.md`
- 6 stages (0-5) instead of 8
- Progressive saving during Stage 0 (after each PDF)
- Stage-completion saves for dialogue stages (1-5)

### M1 Tools (komplett) ✅
| Tool | Beskrivning |
|------|-------------|
| `load_stage` | Ladda metodologi för stage 0-5 |
| `read_materials` | Lista filer (list mode) eller läs EN fil (read mode) |
| `read_reference` | Läs kursplan etc. |
| `save_m1_progress` | Progressiv sparning till `m1_analysis.md` |
| `write_m1_stage` | **NEW** Direkt filskrivning per stage (separata filer) |

### write_m1_stage Tool ✅ (2026-01-21)
| Uppgift | Status | Datum |
|---------|--------|-------|
| Tool implementation | ✅ Klar | 2026-01-21 |
| Separate files per stage (0-5) | ✅ Klar | 2026-01-21 |
| m1_progress.yaml tracking | ✅ Klar | 2026-01-21 |
| Overwrite protection | ✅ Klar | 2026-01-21 |

**Princip:** "What Claude writes = what gets saved"
- Varje stage får egen fil: `m1_stage0_materials.md`, `m1_stage1_validation.md`, etc.
- Automatisk progress-tracking i `m1_progress.yaml`
- Säkerhet: Skriver inte över utan explicit `overwrite=true`

### RFC-007: LLM Workflow Control Patterns ✅
| Uppgift | Status | Datum |
|---------|--------|-------|
| Problem analysis (M1 session failures) | ✅ Klar | 2026-01-19 |
| Core principles documented | ✅ Klar | 2026-01-19 |
| Patterns that work (A/B/C) | ✅ Klar | 2026-01-19 |
| Reality Check section | ✅ Klar | 2026-01-19 |
| Final Recommendation: Option A | ✅ Klar | 2026-01-19 |
| Teacher-facing methodology | ✅ Klar | 2026-01-19 |

**RFC-007 Key Findings:**
- MCP cannot "control" Claude - only provide tools and guidance
- User-driven workflows (Option A): ~95% reliable
- Tool constraints (Option B/C): ~70% reliable
- "One-at-a-time with feedback" requires user to drive each step

**Decision:** Option A (User-Driven) för M1 Stage 0
- Teacher says: "Analyze [file]" → Claude analyzes → "Save and continue"
- Methodology rewritten as teacher guide

### RFC-009: M3 Conversation Capture 📋 DRAFT
| Uppgift | Status | Datum |
|---------|--------|-------|
| Problem analysis (M3 vs M1/M2 patterns) | ✅ Klar | 2026-01-21 |
| RFC-009 draft created | ✅ Klar | 2026-01-21 |
| `append_m3_question` tool design | 📋 Draft | - |
| Implementation | ⬜ Planerad | - |

**RFC-009 Key Insight:**
- M1/M2: Stage-based → save complete document at once
- M3: Iterative conversation → accumulate questions incrementally
- M3 needs different tooling than `write_m1_stage`

### Återstående arbete
| Uppgift | Status |
|---------|--------|
| Testa M1 med Option A workflow | ⬜ Nästa |
| Update M1 methodology for `write_m1_stage` | ⬜ Nästa |
| User decision logging (TIER 3) | ⬜ Planerad |
| M2 tools (kan använda write_m1_stage) | ⬜ Planerad |
| M3 tools (RFC-009: append_m3_question) | ⬜ Planerad |
| M4 tools implementation | ⬜ Planerad |

**Methodology struktur:**
```
methodology/
├── m1/  (6 filer) - Material Analysis (Stage 0-5)
├── m2/  (9 filer) - Assessment Design
├── m3/  (5 filer) - Question Generation
└── m4/  (6 filer) - Quality Assurance
```

---

## Pipeline Status

| Step | Namn | Status |
|------|------|--------|
| Step 0 | Session + Entry Points | ✅ Klar |
| Step 1 | Guided Build | ✅ Klar |
| Step 2 | Validator | ✅ Klar |
| Step 3 | Decision | ⬜ Nästa |
| Step 4 | Export | ✅ Klar |

---

## Bugfixar (2026-01-16)

| Bugg | Status |
|------|--------|
| markdownify strip/convert conflict | ✅ Fixad |
| Duplicate folder creation | ✅ Fixad |
| log_event() argument error | ✅ Fixad |

---

## Fas 6: MarkItDown MCP Integration ⏳ FRAMTIDA

**Beskrivning:** Microsoft's officiella MCP-server för filkonvertering (29+ format → Markdown)

**Syfte:**
- Backup-lösning om egen PDF-läsning behöver kompletteras
- Stöd för fler filformat (DOCX, PPTX, XLSX, EPUB, etc.)
- Learning opportunity för att jämföra med egen implementation

### Stödda Format
| Kategori | Format |
|----------|--------|
| Office | PDF, DOCX, PPTX, XLSX |
| Media | JPG, PNG, MP3, WAV (med OCR/transkription) |
| Webb | HTML, RSS, Wikipedia |
| Data | CSV, JSON, XML, ZIP |
| Publicering | EPUB, Jupyter notebooks |

### Roadmap

| Fas | Uppgift | Status | Timeline |
|-----|---------|--------|----------|
| **Kort-sikt** | Dokumentation klar | ✅ Klar | 2026-01-20 |
| | Installation (~30-45 min) | ⏳ Pending | Q1 2026 |
| | Initial testning med kursmaterial | ⏳ Pending | Q1 2026 |
| **Mellan-sikt** | Jämför med egen MCP | ⏳ Pending | Q2 2026 |
| | Utvärdera: Vilken lösning för vilka use cases? | ⏳ Pending | Q2 2026 |
| | Dokumentera best practices | ⏳ Pending | Q2 2026 |
| **Lång-sikt** | Hybrid-lösning (egen MCP + MarkItDown) | ⏳ Pending | Q3-Q4 2026 |
| | Bidra till MarkItDown vid förbättringar | ⏳ Pending | Q3-Q4 2026 |

### Installationsmetoder
1. **Standard Python** (enklast) - uv + virtuell miljö
2. **Docker** (säkrast) - isolerad körning med read-only mounts

### Säkerhetskrav
- `:ro` (read-only) volume mounts obligatoriskt
- Begränsa folder access till specifika mappar
- Endast localhost binding (`127.0.0.1`)
- Disable plugins om osäker

### Resurser
- GitHub: https://github.com/microsoft/markitdown
- MCP Package: https://github.com/microsoft/markitdown/tree/main/packages/markitdown-mcp
- Komplett installationsguide: `docs/guides/markitdown-mcp-installation.md`

---

## Prioritetsordning

1. ~~**qf-scaffolding logging** - TypeScript logger per RFC-001~~ ✅ Klar
2. ~~**RFC-004 Phase 2** - M1 progressive saving tools~~ ✅ Klar
3. ~~**RFC-007** - LLM Workflow Control Patterns + Option A~~ ✅ Klar
4. **Testa M1 Option A** - End-to-end test med teacher-driven workflow
5. **Step 3: Decision Tool** - Välj export-path (enkel vs Question Set)
6. **M2-M4 Tools** - Implementera tools för övriga moduler
7. **RFC-001 TIER 3** - user_decision logging (efter M1-M4 körts)
8. **MarkItDown MCP** - Installation och testning (Q1 2026)

---

## Relaterade dokument

| Dokument | Beskrivning |
|----------|-------------|
| `WORKFLOW.md` | Komplett workflow-diagram |
| `CHANGELOG.md` | Detaljerad ändringslogg |
| `docs/rfcs/RFC-001-unified-logging.md` | Unified Logging RFC |
| `docs/rfcs/RFC-004-m1-methodology-tools.md` | M1 Tools RFC |
| `docs/rfcs/RFC-007-llm-workflow-control-patterns.md` | LLM Workflow Control |
| `docs/rfcs/RFC-009-m3-conversation-capture.md` | **NEW** M3 Conversation Capture |
| `docs/workflows/m1_complete_workflow.md` | M1 Workflow (v3.1) |
| `methodology/m1/m1_0_stage0_material_analysis.md` | **NEW** Teacher Guide for Stage 0 |
| `docs/acdm/` | ACDM sessionsloggar och reflektioner |
| `docs/adr/ADR-010-step3-decision-architecture.md` | Step 3 arkitektur |
| `docs/adr/ADR-011-question-set-builder.md` | Question Set spec |
| `docs/adr/ADR-014-shared-session.md` | Shared Session arkitektur |
| `docs/specs/STEP1_REBUILD_INTERACTIVE.md` | Step 1 spec |
| `docs/DISCOVERY_BRIEF.md` | Ursprunglig vision |
| `docs/guides/markitdown-mcp-installation.md` | **NEW** MarkItDown MCP installationsguide |

---

*Roadmap uppdaterad 2026-01-21 (write_m1_stage tool, RFC-009 M3 Conversation Capture)*
