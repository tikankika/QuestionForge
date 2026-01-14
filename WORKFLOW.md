# QuestionForge Workflow

**Version:** 1.0  
**Date:** 2026-01-14  
**Related:** ADR-014 (Shared Session), qf-scaffolding-spec.md, qf-pipeline-spec.md

---

## Overview

QuestionForge är ett AI-assisterat ramverk för att skapa pedagogiskt förankrade quiz-frågor. Det består av två MCP:er som samarbetar:

| MCP | Språk | Syfte |
|-----|-------|-------|
| **qf-pipeline** | Python | Teknisk bearbetning (validering, export till QTI) |
| **qf-scaffolding** | TypeScript | Metodologi-guidning (M1-M4 moduler) |

Båda delar **samma session** för enhetlig användarupplevelse.

---

## Entry Points (Startpunkter)

**Entry point = var du STARTAR, men du kan hoppa fritt mellan moduler!**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           QUESTIONFORGE                                      │
│                                                                              │
│   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌──────────────┐ │
│   │   M1    │   │   M2    │   │   M3    │   │   M4    │   │    Export    │ │
│   │ Analys  │──▶│Blueprint│──▶│ Frågor  │──▶│   QA    │──▶│     QTI      │ │
│   └────▲────┘   └────▲────┘   └────▲────┘   └─────────┘   └──────▲───────┘ │
│        │             │             │                              │          │
│   ┌────┴────┐   ┌────┴────┐   ┌────┴────┐                   ┌────┴────┐    │
│   │ Entry A │   │ Entry B │   │ Entry C │                   │ Entry D │    │
│   │Material │   │  Mål    │   │  Plan   │                   │ Frågor  │    │
│   └─────────┘   └─────────┘   └─────────┘                   └─────────┘    │
│                                                                              │
│          ◀── ── ── KAN HOPPA MELLAN MODULER ── ── ──▶                      │
│                                                                              │
│   M1 = Content Analysis    M3 = Question Generation                         │
│   M2 = Assessment Design   M4 = Quality Assurance                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Entry | Startar på | Rekommenderad väg | Kan hoppa till |
|-------|------------|-------------------|----------------|
| **A** Material | M1 | M1 → M2 → M3 → M4 → Export | Alla moduler |
| **B** Mål | M2 | M2 → M3 → M4 → Export | M1, M3, M4, Export |
| **C** Plan | M3 | M3 → M4 → Export | M1, M2, M4, Export |
| **D** Frågor | Export | Validate → Export | M1, M2, M3, M4 |

---

## Complete Flow Diagram

```
                              ┌──────────────┐
                              │    START     │
                              └──────┬───────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │   init (båda MCP)   │
                          │   "Vad har du?"     │
                          └─────────┬───────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
              ┌─────────┐    ┌─────────┐    ┌─────────┐
              │    A    │    │   B/C   │    │    D    │
              │Material │    │Obj/Plan │    │ Frågor  │
              └────┬────┘    └────┬────┘    └────┬────┘
                   │              │              │
                   └──────────────┼──────────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │    step0_start      │
                       │  (qf-pipeline)      │
                       │  Skapar session     │
                       └─────────┬───────────┘
                                 │
                                 ▼
                       ┌─────────────────────┐
                       │   Session skapad    │
                       │   session.yaml      │
                       └─────────┬───────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
   ┌───────────┐          ┌───────────┐          ┌───────────┐
   │  Val A    │          │  Val B/C  │          │  Val D    │
   │  M1-M4    │          │  M2/M3-M4 │          │ Pipeline  │
   └─────┬─────┘          └─────┬─────┘          └─────┬─────┘
         │                      │                      │
         ▼                      ▼                      │
   ┌───────────┐          ┌───────────┐                │
   │list_modules│         │list_modules│               │
   │(scaffolding)│        │(scaffolding)│              │
   └─────┬─────┘          └─────┬─────┘                │
         │                      │                      │
         ▼                      ▼                      │
   ┌───────────┐          ┌───────────┐                │
   │ M1: Content│         │ M2 or M3  │                │
   │ Analysis   │         │ (skip M1) │                │
   └─────┬─────┘          └─────┬─────┘                │
         │                      │                      │
         ▼                      │                      │
   ┌───────────┐                │                      │
   │ M2: Plan  │◄───────────────┘                      │
   └─────┬─────┘                                       │
         │                                             │
         ▼                                             │
   ┌───────────┐                                       │
   │ M3: Gen   │◄──────────────────────────────────────┤
   └─────┬─────┘                                       │
         │                                             │
         ▼                                             │
   ┌───────────┐                                       │
   │ M4: QA    │                                       │
   └─────┬─────┘                                       │
         │                                             │
         └──────────────────┬──────────────────────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │   step2_validate    │
                 │   (qf-pipeline)     │
                 └─────────┬───────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
        ┌──────────┐             ┌──────────┐
        │  VALID   │             │ INVALID  │
        └────┬─────┘             └────┬─────┘
             │                        │
             ▼                        ▼
      ┌─────────────┐          ┌─────────────┐
      │step4_export │          │  Fixa fel   │
      │  (QTI)      │          │step1_fix_*  │
      └─────────────┘          └──────┬──────┘
                                      │
                                      └──→ (validera igen)
```

---

## Project Structure

När session skapas med `step0_start`:

```
project_name/
├── 00_materials/           ← Input för M1 (föreläsningar, slides)
├── 01_source/              ← Original markdown (från M3 eller extern)
├── 02_working/             ← Working copy för pipeline
├── 03_output/              ← QTI export (.zip)
├── methodology/            ← M1-M4 outputs
│   ├── m1_objectives.md    ← Lärandemål från M1
│   ├── m1_examples.md      ← Exempelkatalog
│   ├── m1_misconceptions.md← Missuppfattningar
│   ├── m2_blueprint.md     ← Blueprint från M2
│   └── m3_questions.md     ← Genererade frågor
├── session.yaml            ← Session state (båda MCP:er)
└── logs/                   ← Action logs
```

---

## Modules (M1-M4)

### M1: Content Analysis
**Syfte:** Analysera vad som faktiskt undervisades  
**Input:** Undervisningsmaterial (föreläsningar, slides, transkriberingar)  
**Output:** Lärandemål, exempelkatalog, missuppfattningar  
**Duration:** 2.5-3.5 timmar  
**Stages:** 8

```
Stage 0: Material Analysis (AI solo, 60-90 min)
Stage 1: Initial Validation (dialog, 20-30 min)
Stage 2: Emphasis Refinement (dialog, 30-45 min)
Stage 3: Example Catalog (dialog, 20-30 min)
Stage 4: Misconception Registry (dialog, 20-30 min)
Stage 5: Scope & Objectives (dialog, 45-60 min)
```

### M2: Assessment Planning
**Syfte:** Designa assessment-strukturen  
**Input:** Lärandemål (från M1 eller egna)  
**Output:** Blueprint med frågefördelning  
**Stages:** 9

```
Stage 1: Objective Validation
Stage 2: Strategy Definition
Stage 3: Question Target
Stage 4: Bloom's Distribution
Stage 5: Question Type Mix
Stage 6: Difficulty Distribution
Stage 7: Blueprint Construction
```

### M3: Question Generation
**Syfte:** Skapa frågorna  
**Input:** Blueprint (från M2 eller egen)  
**Output:** Markdown-frågor  
**Stages:** 5

```
Stage 1: Template Selection
Stage 2: Basic Generation
Stage 3: Distribution Review
Stage 4: Finalization
```

### M4: Quality Assurance
**Syfte:** Validera frågor pedagogiskt  
**Input:** Frågor (från M3 eller befintliga)  
**Output:** Granskade, validerade frågor  
**Stages:** 6

```
Phase 1: Automated Validation
Phase 2: Pedagogical Review
Phase 3: Collective Analysis
Phase 4: Documentation
```

---

## Tool Reference

### qf-pipeline Tools

| Tool | Syfte | När använda |
|------|-------|-------------|
| `init` | Kritiska instruktioner | ALLTID först |
| `step0_start` | Skapa session | Efter init, när sökvägar klara |
| `step0_status` | Visa session | Kontrollera progress |
| `step1_start` | Starta guided build | Om v6.3 format |
| `step1_fix_auto` | Auto-fixa problem | Efter analys |
| `step1_fix_manual` | Manuell fix | Kräver input |
| `step2_validate` | Validera markdown | Innan export |
| `step2_read` | Läs arbetsfil | Felsökning |
| `step4_export` | Exportera QTI | När valid |
| `list_types` | Lista frågetyper | Referens |
| `list_projects` | Lista projekt | Hitta filer |

### qf-scaffolding Tools

| Tool | Syfte | När använda |
|------|-------|-------------|
| `init` | Kritiska instruktioner | ALLTID först (samma som pipeline) |
| `list_modules` | Visa M1-M4 | Efter session skapad |
| `load_stage` | Ladda metodologi | Progressivt per stage |
| `module_status` | Visa progress | Kontrollera var du är |

---

## Common Scenarios

### Scenario A: Lärare har föreläsningsmaterial

```
1. User: "Jag vill skapa quiz från mina föreläsningar"
2. Claude: init → "Vad har du?" → User: "Material"
3. Claude: "Var ligger materialet? Var ska projektet sparas?"
4. User: Anger sökvägar
5. Claude: step0_start → Session skapad
6. Claude: list_modules → "Börja med M1?"
7. User: "Ja"
8. Claude: load_stage(m1, 0) → Visar intro
9. User: "Ok"
10. Claude: load_stage(m1, 1) → Stage 0 (AI analyserar material)
... fortsätter genom M1-M4 ...
11. Claude: step2_validate → Validerar
12. Claude: step4_export → Exporterar QTI
```

### Scenario B: Lärare har lärandemål klara

```
1. User: "Jag har lärandemål, vill skapa quiz"
2. Claude: init → "Vad har du?" → User: "Lärandemål"
3. Claude: step0_start → Session skapad
4. Claude: list_modules → "Du kan hoppa M1. Börja M2?"
5. User: "Ja"
6. Claude: load_stage(m2, 0) → Börjar M2
... fortsätter M2-M4 ...
```

### Scenario C: Lärare har färdig markdown

```
1. User: "Jag har quiz-frågor i markdown, vill exportera"
2. Claude: init → "Vad har du?" → User: "Markdown med frågor"
3. Claude: step0_start → Session skapad
4. Claude: step2_validate → Validerar
5. Om valid: step4_export
6. Om invalid: step1_fix_* eller manuell fix
```

---

## Session State

### session.yaml Structure

```yaml
# ===== QF-PIPELINE =====
session_id: "project_20260114_103000"
created_at: "2026-01-14T10:30:00"
source_file: "/path/to/questions.md"
working_file: "/path/to/02_working/questions.md"
output_folder: "/path/to/03_output"
validation_status: "valid"  # pending | valid | invalid
question_count: 25
exports:
  - path: "questions_QTI.zip"
    timestamp: "2026-01-14T11:45:00"
    question_count: 25

# ===== QF-SCAFFOLDING =====
methodology:
  entry_point: "materials"  # materials | objectives | blueprint | questions
  active_module: "m2"
  
  m1:
    status: "completed"
    loaded_stages: [0, 1, 2, 3, 4, 5, 6, 7]
    outputs:
      objectives: "methodology/m1_objectives.md"
      examples: "methodology/m1_examples.md"
      misconceptions: "methodology/m1_misconceptions.md"
  
  m2:
    status: "in_progress"
    loaded_stages: [0, 1, 2]
    current_stage: 2
    outputs: {}
  
  m3:
    status: "not_started"
    loaded_stages: []
    outputs: {}
  
  m4:
    status: "not_started"
    loaded_stages: []
    outputs: {}
```

---

## Critical Rules

### För Claude

1. **ALLTID börja med init** - returnerar kritiska instruktioner
2. **FRÅGA vad användaren har** - anta aldrig A/B/C/D
3. **VÄNTA på svar** - gissa inte sökvägar
4. **En stage i taget** - progressiv laddning
5. **STOP vid stage gates** - vänta på lärarens godkännande
6. **Validera innan export** - step2_validate ALLTID före step4_export

### Stage Gate Pattern

```
load_stage(m1, 2) returnerar:
{
  document: { content: "..." },
  requires_approval: true,
  approval_prompt: "Stage 1 klar. Fortsätt till Stage 2?"
}

→ Claude MÅSTE fråga läraren
→ Vänta på "ja" / "ok" / bekräftelse
→ SEDAN load_stage(m1, 3)
```

---

## Troubleshooting

### "Ingen aktiv session"
```
Orsak: qf-scaffolding anropades utan session
Lösning: Kör step0_start (qf-pipeline) först
```

### "Filen finns inte"
```
Orsak: Felaktig sökväg
Lösning: Använd list_projects för att hitta rätt mapp
```

### "Ogiltigt format"
```
Orsak: Markdown följer inte v6.5 spec
Lösning: Kör step1_fix_auto eller step1_fix_manual
```

### "Claude hoppar över stages"
```
Orsak: Stage gate inte respekterad
Lösning: load_stage har requires_approval - Claude MÅSTE vänta
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-14 | Initial workflow document |

---

*QuestionForge Workflow v1.0 | 2026-01-14*
