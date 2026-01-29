# QuestionForge Roadmap

**Senast uppdaterad:** 2026-01-29

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

## Fas 2: Guided Build ✅ REFAKTORERAD

### Step 1: Minimal Safety Net (Vision A) ✅ (2026-01-28)

**Refaktorering:** Step 1 omdesignat från "Interactive Guided Build" (3700 rader) till "Minimal Safety Net" (~289 rader).

| Uppgift | Status | Datum |
|---------|--------|-------|
| RFC-013 v2.5: Step 1 Vision A spec | ✅ Klar | 2026-01-28 |
| Arkivera gamla moduler (7 filer → `_archived/`) | ✅ Klar | 2026-01-28 |
| `step1_review` - visa fråga + issues | ✅ Klar | 2026-01-28 |
| `step1_manual_fix` - manuell fix | ✅ Klar | 2026-01-28 |
| `step1_delete` - radera fråga | ✅ Klar | 2026-01-28 |
| `step1_skip` - skippa fråga | ✅ Klar | 2026-01-28 |
| Old tools → deprecation stubs | ✅ Klar | 2026-01-28 |

**Vision A Principer:**
- Step 1 används ENDAST när Step 3 auto-fix misslyckas
- Normal flow: M5 → Step 2 → Step 3 → Step 4 (Step 1 skippas)
- Step 1 hanterar: okända fel, Step 3-misslyckanden, strukturella issues

**Arkiverade moduler (3200+ rader):**
- `analyzer.py` → Ersatt av Step 2 validator
- `transformer.py` → Ersatt av Step 3 auto-fix
- `structural_issues.py` → Ersatt av pipeline_router
- `detector.py`, `patterns.py`, `prompts.py`, `session.py`

**Behållna moduler (~520 rader):**
- `frontmatter.py` - YAML progress tracking
- `parser.py` - Fråge-parsning
- `decision_logger.py` - Beslutsloggning

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

### Step 4: Export ✅ KLAR (RFC-012 Löst)
| Uppgift | Status | Datum |
|---------|--------|-------|
| `step4_export` - generera QTI-paket | ✅ Klar | 2026-01 |
| Tags → Labels mapping | ✅ Klar | 2026-01 |
| Resource handling (bilder etc) | ✅ Fixad | 2026-01-28 |
| Auto-load session från projektmapp | ✅ Klar | 2026-01-28 |

**RFC-012 LÖST:**
- Subprocess-approach: Pipeline anropar `scripts/` för validering + export
- `apply_resource_mapping()` körs nu korrekt via `generate_qti_package.py`
- Session auto-laddas från projekt om input är i `pipeline/` eller `questions/`

### Pipeline Router ✅ NY (2026-01-28)

| Uppgift | Status | Datum |
|---------|--------|-------|
| `pipeline_route` tool | ✅ Klar | 2026-01-28 |
| Felkategorisering (MECHANICAL/STRUCTURAL/PEDAGOGICAL) | ✅ Klar | 2026-01-28 |
| Routing till rätt handler | ✅ Klar | 2026-01-28 |

**Routing-logik:**
| Kategori | Handler | Beskrivning |
|----------|---------|-------------|
| MECHANICAL | Step 3 | Syntax-fel som kan auto-fixas |
| STRUCTURAL | Step 1 | Kräver lärar-beslut |
| PEDAGOGICAL | M5 | Innehållsproblem, tillbaka till M5 |
| NONE | Step 4 | Allt validerat, redo för export |

**Fil:** `tools/pipeline_router.py`

### RFC-014: Resource Handling 📋 DRAFT

**Beskrivning:** Hantering av resurser för komplexa frågetyper (bilder, audio, koordinater)

| Uppgift | Status | Datum |
|---------|--------|-------|
| RFC-014 placeholder skapad | ✅ Klar | 2026-01-28 |
| Implementation | ⬜ Planerad | - |

**Frågetyper som kräver resource handling:**
- `hotspot` - Bild + koordinater
- `graphicgapmatch_v2` - Bild + drop zones
- `audio_record` - Ljudfil
- `text_entry_graphic` - Bild + textfält

**Funktioner (planerade):**
- Resource discovery (hitta refererade filer)
- Koordinat-editor (visualisera zoner)
- Fil-path management (normalisera, kopiera)
- Preview i terminal eller GUI

**Prioritet:** Låg - väntar på pipeline-stabilisering

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

### RFC-016: M5 Self-Learning Format Recognition ✅ KLAR (2026-01-29)

**Beskrivning:** M5 (Content Completeness & QFMD Generation) med självlärande formatigenkänning.

| Uppgift | Status | Datum |
|---------|--------|-------|
| RFC-016 specifikation | ✅ Klar | 2026-01-26 |
| Format learner implementation | ✅ Klar | 2026-01-27 |
| BUG 1-2: Separator regex + format detection | ✅ Fixad | 2026-01-28 |
| BUG 3: Parse validation | ✅ Fixad | 2026-01-29 |
| BUG 4: Field normalization | ✅ Fixad | 2026-01-29 |
| BUG 6: STOP points (teacher gates) | ✅ Fixad | 2026-01-29 |
| BUG 7: Missing field warnings | ✅ Fixad | 2026-01-29 |
| Option B: Data-driven field aliases | ✅ Klar | 2026-01-29 |

**M5 Tools (komplett):**
| Tool | Beskrivning |
|------|-------------|
| `m5_start` | Starta M5-session, ladda format patterns |
| `m5_detect_format` | Detektera/bekräfta frågeformat |
| `m5_analyze` | Parsea frågor, visa validering |
| `m5_approve` | Godkänn fråga (med STOP points) |
| `m5_manual_fix` | Manuell korrigering |
| `m5_finish` | Avsluta session, spara patterns |
| `m5_add_field_alias` | **NY** Lägg till fältalias |
| `m5_remove_field_alias` | **NY** Ta bort fältalias |
| `m5_list_field_aliases` | **NY** Lista alla fältaliaser |

**Option B - Data-Driven Field Aliases:**
- Default-aliaser för svenska/engelska varianter (30+)
- Anpassningsbara per projekt via `logs/m5_format_patterns.json`
- Self-learning: nya alias sparas automatiskt
- Exempel: `stem → question_text`, `svårighetsgrad → difficulty`

**Filer:**
- `packages/qf-scaffolding/src/m5/format_learner.ts`
- `packages/qf-scaffolding/src/tools/m5_interactive_tools.ts`
- `docs/rfcs/RFC-016-m5-self-learning-format-recognition.md`

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

| Step | Namn | Status | Uppdaterad |
|------|------|--------|------------|
| Step 0 | Session + Entry Points | ✅ Klar | 2026-01 |
| Step 1 | Minimal Safety Net (Vision A) | ✅ Refaktorerad | 2026-01-28 |
| Step 2 | Validator | ✅ Klar | 2026-01 |
| Router | Pipeline Router | ✅ NY | 2026-01-28 |
| Step 3 | Auto-fix | ✅ Klar | 2026-01-22 |
| Step 4 | Export | ✅ Klar (RFC-012 löst) | 2026-01-28 |

**Ny Pipeline Flow (2026-01-28):**
```
M5 output → Step 2 (validate) → Router → Step 3 (auto-fix) → Step 4 (export)
                                   ↓
                              [om STRUCTURAL → Step 1 teacher fix]
                              [om PEDAGOGICAL → M5 redo]
```

---

## Bugfixar (2026-01-16)

| Bugg | Status |
|------|--------|
| markdownify strip/convert conflict | ✅ Fixad |
| Duplicate folder creation | ✅ Fixad |
| log_event() argument error | ✅ Fixad |

---

## Fas 6: MarkItDown MCP Integration 🔶 NÄSTA

**Beskrivning:** Microsoft's officiella MCP-server för filkonvertering (29+ format → Markdown)

**Beslut (2026-01-21):** Använder MarkItDown MCP istället för egen `course-extractor-mcp`.
- ✅ Officiellt underhållen av Microsoft
- ✅ 29+ format (inte bara PDF)
- ✅ MIT-licens (ingen AGPL-komplikation)
- ✅ Production-ready

### Stödda Format
| Kategori | Format |
|----------|--------|
| Office | PDF, DOCX, PPTX, XLSX |
| Media | JPG, PNG, MP3, WAV (med OCR/transkription) |
| Webb | HTML, RSS, Wikipedia |
| Data | CSV, JSON, XML, ZIP |
| Publicering | EPUB, Jupyter notebooks |

### Roadmap

| Uppgift | Status | Datum |
|---------|--------|-------|
| Dokumentation klar | ✅ Klar | 2026-01-20 |
| Beslut: Använd MarkItDown (ej egen MCP) | ✅ Klar | 2026-01-21 |
| Installation (~30-45 min) | ⬜ Nästa | - |
| Testa med kursmaterial (PDF) | ⬜ Planerad | - |
| Konfigurera för QuestionForge workflow | ⬜ Planerad | - |

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

### Deprecated: course-extractor-mcp
- Flyttad till separat repo (AGPL-isolation)
- **Status:** Arkiverad - använd MarkItDown istället
- **Anledning:** Microsoft's lösning är bättre underhållen och har fler format

---

## Prioritetsordning

1. ~~**qf-scaffolding logging** - TypeScript logger per RFC-001~~ ✅ Klar
2. ~~**RFC-004 Phase 2** - M1 progressive saving tools~~ ✅ Klar
3. ~~**RFC-007** - LLM Workflow Control Patterns + Option A~~ ✅ Klar
4. ~~**RFC-012** - Pipeline-Script Alignment~~ ✅ Klar (2026-01-28)
5. ~~**RFC-013 v2.5** - Step 1 Vision A refactor~~ ✅ Klar (2026-01-28)
6. **MarkItDown MCP** - Installation och konfiguration ⬅️ **NÄSTA**
7. **Testa M1 med MarkItDown** - End-to-end test med PDF-extraktion
8. **M2-M4 Tools** - Implementera tools för övriga moduler
9. **RFC-001 TIER 3** - user_decision logging (efter M1-M4 körts)
10. **RFC-014** - Resource handling (bilder, audio, koordinater) - LÅG PRIORITET

---

## Teknisk Skuld / Framtida Förbättringar

### RFC-XXX: qti-core Refaktorering ⬜ Planerad

**Beskrivning:** Städa intern struktur i `packages/qti-core/`

**Bakgrund:**
- qti-core är ursprungligen `QTI-Generator-for-Inspera` (standalone projekt)
- Importerades till QuestionForge som lokal package (ADR-008)
- Fungerar utmärkt men har rörig intern struktur
- Mycket arbete har lagts på validering och QTI-generering - får INTE förloras!

**Nuvarande struktur (rörig):**
```
qti-core/
├── validate_mqg_format.py   ← Löst i roten
├── main.py                   ← Löst i roten
├── src/parser/               ← Organiserat
├── src/generators/           ← Organiserat
└── scripts/                  ← CLI-verktyg
```

**Föreslaget (städat):**
```
qti-core/
└── src/
    ├── parser/          # MarkdownQuizParser (finns)
    ├── validator/       # Flytta validate_mqg_format.py hit
    ├── generator/       # QTI XML-generering (finns)
    └── packager/        # ZIP-paketering
```

**Krav:**
- [ ] Skapa RFC med migrationsplan
- [ ] Ingen funktionalitet får försvinna
- [ ] Wrappers i qf-pipeline måste uppdateras
- [ ] Alla tester måste passera efter flytt
- [ ] Dokumentera nya import-paths

**Prioritet:** Låg (fungerar nu, städa senare)
**Estimat:** 2-4 timmar

---

## Relaterade dokument

| Dokument | Beskrivning |
|----------|-------------|
| `WORKFLOW.md` | Komplett workflow-diagram |
| `CHANGELOG.md` | Detaljerad ändringslogg |
| `docs/rfcs/RFC-001-unified-logging.md` | Unified Logging RFC |
| `docs/rfcs/RFC-004-m1-methodology-tools.md` | M1 Tools RFC |
| `docs/rfcs/RFC-007-llm-workflow-control-patterns.md` | LLM Workflow Control |
| `docs/rfcs/RFC-009-m3-conversation-capture.md` | M3 Conversation Capture |
| `docs/rfcs/rfc-012-pipeline-script-alignment.md` | Pipeline-Script Alignment (LÖST) |
| `docs/rfcs/RFC-013-Questionforge pipeline architecture v2.md` | Pipeline arkitektur v2.5 |
| `docs/rfcs/RFC-014-resource-handling.md` | Resource Handling (DRAFT) |
| `docs/rfcs/RFC-016-m5-self-learning-format-recognition.md` | **NEW** M5 Self-Learning Format (KLAR) |
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

*Roadmap uppdaterad 2026-01-29 (RFC-016 M5 implementerad med Option B field aliases, BUG 3/4/6/7 fixade)*
