# QuestionForge Roadmap

**Senast uppdaterad:** 2026-01-14

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

---

## Fas 4: Logging ⬜ PARKERAD

**Status:** Parkerad (filbaserad loggning redan implementerad i Step 1)

| Uppgift | Status |
|---------|--------|
| Filbaserad loggning (pipeline.log, pipeline.jsonl) | ✅ Klar |
| PostgreSQL logging | ⬜ Parkerad |

---

## Fas 5: qf-scaffolding ⬜ FRAMTIDA

**Beskrivning:** TypeScript MCP för pedagogisk scaffolding (M1-M4)

| Uppgift | Status |
|---------|--------|
| M1: Content Analysis | ⬜ Planerad |
| M2: Assessment Planning | ⬜ Planerad |
| M3: Question Generation | ⬜ Planerad |
| M4: Quality Assurance | ⬜ Planerad |

---

## Fas 2.5: Shared Session (ADR-014) ✅ KLAR

**Beskrivning:** Delad session mellan qf-pipeline och qf-scaffolding

| Uppgift | Status | Datum |
|---------|--------|-------|
| ADR-014: Shared Session arkitektur | ✅ Klar | 2026-01-14 |
| 4 Entry Points (A/B/C/D) | ✅ Klar | 2026-01-14 |
| source_file Optional för entry A | ✅ Klar | 2026-01-14 |
| Nya mappar: 00_materials/, methodology/ | ✅ Klar | 2026-01-14 |
| methodology sektion i session.yaml | ✅ Klar | 2026-01-14 |

**Entry Points:**
| ID | Entry Point | source_file | Nästa Modul |
|----|-------------|-------------|-------------|
| A | materials | ❌ Valfri | M1 (scaffolding) |
| B | objectives | ✅ Krävs | M2 (scaffolding) |
| C | blueprint | ✅ Krävs | M3 (scaffolding) |
| D | questions | ✅ Krävs | Pipeline direkt |

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

## Prioritetsordning

1. **Step 3: Decision Tool** - Välj export-path (enkel vs Question Set)
2. **Testa hela pipelinen** - End-to-end test
3. **qf-scaffolding** - När pipeline är stabil

---

## Relaterade dokument

| Dokument | Beskrivning |
|----------|-------------|
| `WORKFLOW.md` | Komplett workflow-diagram |
| `CHANGELOG.md` | Detaljerad ändringslogg |
| `docs/acdm/` | ACDM sessionsloggar och reflektioner |
| `docs/adr/ADR-010-step3-decision-architecture.md` | Step 3 arkitektur |
| `docs/adr/ADR-011-question-set-builder.md` | Question Set spec |
| `docs/adr/ADR-014-shared-session.md` | Shared Session arkitektur |
| `docs/specs/STEP1_REBUILD_INTERACTIVE.md` | Step 1 spec |
| `docs/DISCOVERY_BRIEF.md` | Ursprunglig vision |

---

*Roadmap uppdaterad 2026-01-14*
