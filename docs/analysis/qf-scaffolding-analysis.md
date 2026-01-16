# QF-SCAFFOLDING ANALYSIS

**Date:** 2026-01-07
**Purpose:** Sammanfattning av existerande dokumentation och roadmap för qf-scaffolding utveckling

---

## EXISTERANDE DOKUMENTATION

### Huvuddokument

| Dokument | Plats | Innehåll |
|----------|-------|----------|
| CLAUDE.md | `/QuestionForge/CLAUDE.md` | Projektöversikt, arkitektur, quick start |
| ROADMAP.md | `/QuestionForge/ROADMAP.md` | Nuvarande status, fas 1-4 plan |
| CHANGELOG.md | `/QuestionForge/CHANGELOG.md` | Ändringshistorik |
| DISCOVERY_BRIEF.md | `/docs/DISCOVERY_BRIEF.md` | Problemanalys, lösningsriktning |
| qf-scaffolding-spec.md | `/docs/specs/qf-scaffolding-spec.md` | Detaljerad specifikation |

### ADRs (Architecture Decision Records)

| ADR | Relevans för qf-scaffolding |
|-----|----------------------------|
| ADR-001 | Two-MCP Architecture - KRITISK |
| ADR-002 | Module Naming (M1-M4) - KRITISK |
| ADR-003 | Language Choices (TypeScript) - KRITISK |
| ADR-004 | M2+M3 Merge - KRITISK |
| ADR-005 | MCP Integration (pipeline calls scaffolding) - KRITISK |
| ADR-006 | Session Management - Referens |
| ADR-007 | Tool Naming Convention - Referens |

---

## PACKAGES STATUS

```
packages/
├── qf-pipeline/      ✅ KLAR - Python MCP, fungerar
│   ├── src/qf_pipeline/
│   │   ├── server.py     # MCP server
│   │   ├── tools/        # step0_start, step0_status, step2_validate, step4_export
│   │   ├── wrappers/     # parser, validator, packager, generator
│   │   └── utils/        # session management
│   ├── pyproject.toml
│   └── README.md
│
├── qf-scaffolding/   ⬜ TOM - Ska byggas
│   └── (inget innehåll)
│
└── qti-core/         ✅ KLAR - Kopierad från QTI-Generator-for-Inspera
    ├── src/          # Core QTI logic
    ├── templates/    # XML templates
    └── ...
```

---

## QF-SCAFFOLDING SPECIFIKATION (Sammanfattning)

### Syfte
Metodikstyrning för att hjälpa lärare skapa frågor genom en strukturerad, pedagogisk process.

### Moduler

| Modul | Namn | Stages | Syfte |
|-------|------|--------|-------|
| M1 | Content Analysis | 6 | Analysera vad som undervisades |
| M2 | Assessment Planning | 5 | Designa bedömningsstruktur |
| M3 | Question Generation | 4 | Skapa frågor |
| M4 | Quality Assurance | 4 | Validera pedagogiskt |

### Verktyg (8 st)

| Verktyg | Kategori | Syfte |
|---------|----------|-------|
| `get_module_instructions` | Navigation | Hämta metodikguidning |
| `suggest_next_step` | Navigation | Rekommendera nästa steg |
| `get_stage_gate_checklist` | Stage Mgmt | Hämta godkännandechecklista |
| `validate_stage_output` | Stage Mgmt | Kontrollera stage-komplettering |
| `list_available_modules` | Flexible Nav | Visa alla moduler |
| `can_start_module` | Flexible Nav | Kontrollera prerequisites |
| `analyze_distractors` | Analysis | QA för MC-frågor |
| `check_language_consistency` | Analysis | QA för terminologi |

### Teknisk Stack

- **Språk:** TypeScript (Node.js)
- **MCP SDK:** @modelcontextprotocol/sdk
- **Pattern:** NON-LINEAR, flexibla ingångspunkter
- **Output:** Markdown-frågor

### Filstruktur (från spec)

```
packages/qf-scaffolding/
├── src/
│   ├── index.ts               # MCP server entry
│   ├── tools/
│   │   ├── navigation.ts      # get_module_instructions, suggest_next_step
│   │   ├── stage-management.ts # get_stage_gate_checklist, validate_stage_output
│   │   ├── flexible-nav.ts    # list_available_modules, can_start_module
│   │   └── analysis.ts        # analyze_distractors, check_language_consistency
│   ├── modules/
│   │   ├── m1-content-analysis/
│   │   │   ├── stages.ts
│   │   │   └── instructions.md
│   │   ├── m2-assessment-planning/
│   │   │   ├── stages.ts
│   │   │   └── instructions.md
│   │   ├── m3-question-generation/
│   │   │   ├── stages.ts
│   │   │   └── instructions.md
│   │   └── m4-quality-assurance/
│   │       ├── stages.ts
│   │       └── instructions.md
│   └── utils/
│       └── checklist.ts
├── package.json
├── tsconfig.json
└── README.md
```

---

## INTEGRATION MED QF-PIPELINE

### Workflow

```
Teacher med material
        │
        ▼
┌─────────────────────┐
│ QF-SCAFFOLDING      │
│ M1 → M2 → M3 → M4   │
│ (Flexibel ordning)  │
└─────────────────────┘
        │
        │ Markdown-frågor
        ▼
┌─────────────────────┐
│ QF-PIPELINE         │
│ Step 1-4            │
│ (Linjär pipeline)   │
└─────────────────────┘
        │
        │ QTI-paket
        ▼
    Inspera LMS
```

### MCP-integration (Framtid: Step 1.5)

qf-pipeline kommer kunna anropa qf-scaffolding för pedagogisk analys:
- `analyze_distractors` - MC-kvalitetskontroll
- `check_language_consistency` - Terminologigranskning

---

## BEFINTLIGT METODIKMATERIAL

### MQG BB1 Dokumentation

Finns redan i:
```
/AIED_EdTech_Dev_documentation_projects/
  Modular QGen - Modular Question Generation Framework/
    docs/MQG_0.2/
      MQG_bb1a_Introduction_Framework.md      ← Reviderad
      MQG_bb1b_Stage0_Material_Analysis.md    ← Reviderad
      MQG_bb1c_Stage1_Initial_Validation.md   ← Reviderad
      MQG_bb1d_Stage2_Emphasis_Refinement.md
      MQG_bb1e_Stage3_Example_Catalog.md
      MQG_bb1f_Stage4_Misconception_Analysis.md
      MQG_bb1g_Stage5_Scope_Objectives.md
      MQG_bb1h_Facilitation_Best_Practices.md ← Reviderad
```

Denna dokumentation mappar till M1 (Content Analysis) i qf-scaffolding.

---

## NÄSTA STEG

### Prioritet 1: Setup Node.js MCP Project
- [ ] Skapa package.json
- [ ] Skapa tsconfig.json
- [ ] Installera @modelcontextprotocol/sdk
- [ ] Skapa basic server struktur (index.ts)

### Prioritet 2: Implementera Navigation Tools
- [ ] `get_module_instructions`
- [ ] `suggest_next_step`
- [ ] `list_available_modules`
- [ ] `can_start_module`

### Prioritet 3: Implementera Stage Management
- [ ] `get_stage_gate_checklist`
- [ ] `validate_stage_output`

### Prioritet 4: Integrera Metodikinnehåll
- [ ] Migrera BB1 → M1 instructions
- [ ] Skapa M2, M3, M4 instructions

### Prioritet 5: Analysis Tools (Framtid)
- [ ] `analyze_distractors`
- [ ] `check_language_consistency`

---

## FRÅGOR ATT BESLUTA

1. **Var ska instructions.md lagras?**
   - Alternativ A: Inbäddade i qf-scaffolding/src/modules/
   - Alternativ B: Referera till MQG_0.2 dokumentation
   - Alternativ C: Kopiera till qf-specifications/modules/

2. **Session management?**
   - Behöver qf-scaffolding egen session?
   - Eller bara stateless tool calls?

3. **Hur detaljerade ska stage-instruktioner vara?**
   - Full MQG-stil (1500+ rader per modul)?
   - Eller kompakt översikt?

---

*Analys skapad 2026-01-07*
