# QuestionForge Roadmap

**Senast uppdaterad:** 2026-01-06

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

## Fas 1.5: Refaktorering ⏳ PÅGÅR

### 1.5.1 Tool Naming Convention (ADR-007)
| Uppgift | Status |
|---------|--------|
| Beslut: `stepN_` prefix | ✅ Beslutad |
| Dokumenterat i ADR-007 | ✅ Klar |
| Implementera i server.py | ⬜ Ej påbörjad |

**Verktyg att byta namn:**
- `start_session` → `step0_start`
- `get_session_status` → `step0_status`
- `validate_file` → `step2_validate`
- `export_questions` → `step4_export`
- `list_question_types` → `list_types`

**Verktyg att ta bort:**
- `end_session` (onödig)
- `parse_markdown` (intern utility)

**Verktyg att lägga till:**
- `init` (CALL THIS FIRST!)

### 1.5.2 Standalone Migration (ADR-008) 🔴 KRITISK
| Uppgift | Status |
|---------|--------|
| DISCOVER-fas | ✅ Klar |
| Beslut: Alternativ A (full kopia) | ✅ Beslutad |
| SHAPE-fas | ⬜ Nästa |
| Implementation | ⬜ Ej påbörjad |

**Mål:** Göra qf-pipeline helt självständigt utan beroende på `/Users/niklaskarlsson/QTI-Generator-for-Inspera`

**Ny struktur:**
```
qf-pipeline/src/qf_pipeline/
├── core/              ← Migrerad QTI-logik
│   ├── parser.py
│   ├── generator.py
│   ├── packager.py
│   ├── validator.py
│   └── resource_manager.py
├── templates/xml/     ← 21 XML-mallar
├── wrappers/          ← Tunna wrappers
├── tools/             ← MCP-verktyg
└── utils/             ← Session management
```

**Konsekvens:** QTI-Generator-for-Inspera arkiveras efter migration.

**Uppskattad tid:** 5-7 timmar

---

## Fas 2: Guided Build ⬜ PLANERAD

**Beskrivning:** Interaktiv fråga-för-fråga genomgång med "fix once, apply to all similar"

| Uppgift | Status |
|---------|--------|
| Specifikation | ⬜ Ej påbörjad |
| `step1_build` | ⬜ Planerad |
| `step1_fix` | ⬜ Planerad |
| `step1_skip` | ⬜ Planerad |
| `step1_done` | ⬜ Planerad |

**Kärnfunktion från DISCOVERY_BRIEF:**
```
For each question:
  1. READ question
  2. IDENTIFY type, LOAD spec
  3. COMPARE to spec
  4. SUGGEST corrections
  5. TEACHER decides: accept/modify/skip
  6. APPLY fix to this question
  7. APPLY same fix to ALL similar types  ← KEY FEATURE
```

---

## Fas 3: PostgreSQL Logging ⬜ PARKERAD

**Status:** Parkerad (se PARKED_assessment_mcp_logging.md)

| Uppgift | Status |
|---------|--------|
| Schema design | ✅ Specificerat |
| Implementation | ⬜ Parkerad |

---

## Fas 4: Avancerade funktioner ⬜ FRAMTIDA

- Question Sets (assessmentTest)
- Step 3: Decision tool (`step3_choose`)
- Statistik och rapporter
- Integration med Assessment_suite

---

## Prioritetsordning

1. **🔴 Fas 1.5.2: Standalone Migration** - Kritisk för distribution
2. **Fas 1.5.1: Tool Naming** - Kan göras parallellt
3. **Fas 2: Guided Build** - Huvudfunktionen
4. **Fas 3-4:** Efter Fas 2 är stabil

---

## Relaterade dokument

| Dokument | Beskrivning |
|----------|-------------|
| `docs/DISCOVER_standalone_migration.md` | Analys av migration |
| `docs/adr/ADR-007-tool-naming-convention.md` | Namnkonvention |
| `docs/adr/ADR-006-session-management.md` | Session-arkitektur |
| `docs/IMPLEMENT_handoff_claude_code.md` | Handoff för implementation |
| `docs/DISCOVERY_BRIEF.md` | Ursprunglig vision |

---

*Roadmap skapad 2026-01-06*
