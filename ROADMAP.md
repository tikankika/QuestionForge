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

## Pipeline Status

| Step | Namn | Status |
|------|------|--------|
| Step 0 | Session | ✅ Klar |
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
| `CHANGELOG.md` | Detaljerad ändringslogg |
| `docs/acdm/` | ACDM sessionsloggar och reflektioner |
| `docs/adr/ADR-010-step3-decision-architecture.md` | Step 3 arkitektur |
| `docs/adr/ADR-011-question-set-builder.md` | Question Set spec |
| `docs/specs/STEP1_REBUILD_INTERACTIVE.md` | Step 1 spec |
| `docs/DISCOVERY_BRIEF.md` | Ursprunglig vision |

---

*Roadmap uppdaterad 2026-01-14*
