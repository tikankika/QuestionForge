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
│   └────▲────┘   └────▲────┘   └────▲────┘   └────▲────┘   └──────▲───────┘ │
│        │             │             │              │               │          │
│   ┌────┴────┐   ┌────┴────┐   ┌────┴────┐   ┌────┴────┐    ┌────┴────┐    │
│   │   m1    │   │   m2    │   │   m3    │   │   m4    │    │pipeline │    │
│   │Material │   │  Mål    │   │  Plan   │   │Frågor QA│    │ Direkt  │    │
│   └─────────┘   └─────────┘   └─────────┘   └─────────┘    └─────────┘    │
│                                                                              │
│          ◀── ── ── KAN HOPPA MELLAN MODULER ── ── ──▶                      │
│                                                                              │
│   M1 = Content Analysis    M3 = Question Generation                         │
│   M2 = Assessment Design   M4 = Quality Assurance                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Entry | Startar på | Rekommenderad väg | Kan hoppa till |
|-------|------------|-------------------|----------------|
| **m1** Material | M1 | M1 → M2 → M3 → M4 → Pipeline | Alla moduler |
| **m2** Mål | M2 | M2 → M3 → M4 → Pipeline | M1, M3, M4, Pipeline |
| **m3** Plan | M3 | M3 → M4 → Pipeline | M1, M2, M4, Pipeline |
| **m4** QA | M4 | M4 → Pipeline | M1, M2, M3, Pipeline |
| **pipeline** Direkt | Pipeline | Step1 → Step2 → Step4 | M1, M2, M3, M4 |

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
            ┌───────────┬───────────┼───────────┬───────────┐
            │           │           │           │           │
            ▼           ▼           ▼           ▼           ▼
      ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
      │   m1    │ │   m2    │ │   m3    │ │   m4    │ │pipeline │
      │Material │ │  Mål    │ │  Plan   │ │   QA    │ │ Direkt  │
      └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
           │           │           │           │           │
           └───────────┴───────────┴───────────┴───────────┘
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
    ┌────────────┬───────────────┼───────────────┬────────────┐
    │            │               │               │            │
    ▼            ▼               ▼               ▼            ▼
┌───────┐   ┌───────┐       ┌───────┐       ┌───────┐   ┌─────────┐
│  m1   │   │  m2   │       │  m3   │       │  m4   │   │pipeline │
│ M1-M4 │   │ M2-M4 │       │ M3-M4 │       │M4 only│   │  direct │
└───┬───┘   └───┬───┘       └───┬───┘       └───┬───┘   └────┬────┘
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
  entry_point: "m1"  # m1 | m2 | m3 | m4 | pipeline
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
2. **FRÅGA vad användaren har** - anta aldrig m1/m2/m3/m4/pipeline
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
| 1.1 | 2026-01-22 | Added Appendix A: QTI Export Technical Details |

---

## Appendix A: QTI Export Technical Details

### Två sätt att exportera QTI

QuestionForge har två metoder för QTI-export som använder **samma underliggande logik**:

| Metod | Var | Användning |
|-------|-----|------------|
| **Manuella scripts** | `qti-core/scripts/` | Terminal, utveckling |
| **MCP Pipeline** | `qf-pipeline/step4_export` | Claude Desktop |

---

### A.1 Manuella Scripts (5 steg)

```
qti-core/scripts/
├── step1_validate.py      ── Validera markdown-format
├── step2_create_folder.py ── Skapa output-struktur
├── step3_copy_resources.py── Kopiera bilder/media
├── step4_generate_xml.py  ── Generera QTI XML per fråga
└── step5_create_zip.py    ── Paketera till importbar ZIP
```

**Körning:**
```bash
cd packages/qti-core
python scripts/step1_validate.py input.md
python scripts/step2_create_folder.py input.md
python scripts/step3_copy_resources.py input.md
python scripts/step4_generate_xml.py input.md
python scripts/step5_create_zip.py input.md
```

**Eller allt-i-ett:**
```bash
python main.py input.md output.zip
```

---

### A.1.2 Steg-för-steg jämförelse

| Steg | Manuellt Script | MCP Pipeline (step4_export) | Skillnad |
|------|-----------------|----------------------------|----------|
| **1. Validera** | `step1_validate.py` → `validate_markdown_file()` | `step2_validate` (separat) eller inget | ⚠️ Pipeline skippar validering i step4! |
| **2. Skapa mappar** | `step2_create_folder.py` → mkdir quiz/, resources/, .workflow/ | `QTIPackager.create_package()` skapar mappar | ⚠️ Skapas vid packaging (senare) |
| **3. Parsa markdown** | `step4_generate_xml.py` → `MarkdownQuizParser` | `parse_file()` → `MarkdownQuizParser` | ✅ Samma parser |
| **4. Validera resurser** | `step3_copy_resources.py` → `ResourceManager.validate_resources()` | `validate_resources()` | ✅ Samma logik |
| **5. Kopiera resurser** | `step3_copy_resources.py` → `ResourceManager.copy_resources()` | `copy_resources()` | ✅ Samma logik |
| **6. Uppdatera paths** | `step4_generate_xml.py` → `apply_resource_mapping()` | ❌ **SAKNAS HELT** | 🔴 **KRITISK BUG: Ingen path mapping!** |
| **7. Generera XML** | `step4_generate_xml.py` → `XMLGenerator.generate_question()` per fråga | `generate_all_xml()` → `XMLGenerator` | ✅ Samma generator |
| **8. Skapa manifest** | `step5_create_zip.py` → `QTIPackager` | `create_qti_package()` → `QTIPackager` | ✅ Samma packager |
| **9. Skapa ZIP** | `step5_create_zip.py` → zipfile | `create_qti_package()` | ✅ Samma logik |

**🔴 KRITISK BUG - Steg 6 (VERIFIERAD 2026-01-22):**

```
cli.py (main.py) rad 425-471:
────────────────────────────────
resource_mapping = copy_resources(questions, quiz_dir)
for question in questions:
    question['image']['path'] = resource_mapping[original]  # ✅ UPPDATERAR
    question['question_text'] = update_image_paths_in_text(...)  # ✅ UPPDATERAR
xml_generator.generate_question(question)  # Får KORREKTA paths

server.py (pipeline) rad 1242-1256:
────────────────────────────────
copy_result = copy_resources(...)
resource_count = copy_result.get("count", 0)  # ❌ Ignorerar "copied" mapping!
# SAKNAS: ~45 rader som uppdaterar question paths
xml_list = generate_all_xml(questions, language)  # Får ORIGINAL paths ❌
```

**Resultat:**
- Manuell: `image.png` → kopieras som `Q001_image.png` → XML: `resources/Q001_image.png` ✅
- Pipeline: `image.png` → kopieras som `Q001_image.png` → XML: `image.png` ❌ (fil saknas!)

---

### A.1.3 Detaljerad Script-beskrivning

**step1_validate.py**
```
Input:  markdown_file
Output: Validation report (exit code 0/1)
Calls:  validate_mqg_format.validate_markdown_file()
Data:   Sparar INGET (endast stdout)
```

**step2_create_folder.py**
```
Input:  markdown_file, --output-name, --output-dir
Output: output/quiz_name/, output/quiz_name/resources/, output/quiz_name/.workflow/
Calls:  mkdir, json.dump
Data:   Sparar .workflow/metadata.json
        {input_file, quiz_name, quiz_dir, resources_dir, output_base}
```

**step3_copy_resources.py**
```
Input:  Läser .workflow/metadata.json
Output: Kopierar bilder till resources/
Calls:  MarkdownQuizParser, ResourceManager
Data:   Sparar .workflow/resource_mapping.json
        {original_filename: renamed_filename}
```

**step4_generate_xml.py**
```
Input:  Läser .workflow/metadata.json + resource_mapping.json
Output: XML-filer i quiz_dir (en per fråga)
Calls:  MarkdownQuizParser, apply_resource_mapping(), XMLGenerator
Data:   Sparar .workflow/xml_files.json
        {xml_count, xml_files[], quiz_metadata}
```

**step5_create_zip.py**
```
Input:  Läser .workflow/xml_files.json
Output: quiz_name.zip + imsmanifest.xml
Calls:  QTIPackager
Data:   Sparar .workflow/package_info.json
```

---

### A.2 MCP Pipeline (`step4_export`)

Pipeline kombinerar alla steg i ETT MCP-anrop:

```
step4_export
    │
    ├── 1. parse_file()           ← wrappers/parser.py
    │       └── MarkdownQuizParser ← qti-core/src/parser/markdown_parser.py
    │
    ├── 2. validate_resources()   ← wrappers/resources.py
    │       └── ResourceManager    ← qti-core/src/generator/resource_manager.py
    │
    ├── 3. copy_resources()       ← wrappers/resources.py
    │       └── ResourceManager
    │
    ├── 4. generate_all_xml()     ← wrappers/generator.py
    │       └── XMLGenerator       ← qti-core/src/generator/
    │
    └── 5. create_qti_package()   ← wrappers/packager.py
            └── QTIPackager        ← qti-core/src/packager.py
```

---

### A.3 Modulernas ansvarsområden

```
┌─────────────────────────────────────────────────────────────────────────┐
│  qf-pipeline (MCP Server)                                                │
│  ├── server.py           ← handle_step4_export()                        │
│  └── wrappers/           ← Tunna adapters till qti-core                 │
│      ├── parser.py       ← parse_file(), parse_markdown()              │
│      ├── validator.py    ← validate_file()                              │
│      ├── generator.py    ← generate_all_xml()                           │
│      ├── packager.py     ← create_qti_package()                         │
│      └── resources.py    ← validate_resources(), copy_resources()       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ importerar
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  qti-core (Standalone Logic)                                            │
│  ├── validate_mqg_format.py  ← Validering av markdown-format           │
│  ├── main.py / src/cli.py    ← CLI entry point                         │
│  └── src/                                                               │
│      ├── parser/                                                        │
│      │   └── markdown_parser.py  ← MarkdownQuizParser                  │
│      ├── generator/                                                     │
│      │   ├── xml_generator.py    ← XMLGenerator                        │
│      │   ├── resource_manager.py ← ResourceManager                     │
│      │   └── qti_templates/      ← XML-mallar per frågetyp             │
│      └── packager.py             ← QTIPackager (ZIP-skapande)          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### A.4 Förväntad input-format (v6.5)

**Parser (markdown_parser.py) kräver exakt detta format:**

```markdown
# Q001 Titel här
^type multiple_choice_single
^identifier MC_Q001
^points 1
^labels #label1 #label2

@field: question_text
Frågetext här...
@end_field

@field: options
^Shuffle Yes
A. Alternativ 1
B. Alternativ 2*
C. Alternativ 3
D. Alternativ 4
@end_field

@field: answer
B
@end_field

@field: feedback

@@field: general_feedback
Generell feedback...
@@end_field

@@field: correct_feedback
Rätt svar feedback...
@@end_field

@@field: incorrect_feedback
Fel svar feedback...
@@end_field

@end_field
```

**Kritiska krav:**
- `# Q001 ` - MÅSTE ha mellanslag och titel efter numret
- `^type value` - INGEN kolon, värde på samma rad
- `^identifier value` - INGEN kolon
- `^points value` - INGEN kolon
- `*` efter rätt alternativ i options

---

### A.5 VARNING: Validator vs Parser Mismatch

**Nuvarande problem (2026-01-22):**

| Komponent | `^type: value` | `^type value` |
|-----------|----------------|---------------|
| **Validator** (validate_mqg_format.py) | ✅ Accepterar | ✅ Accepterar |
| **Parser** (markdown_parser.py) | ❌ Misslyckas | ✅ Fungerar |

**Konsekvens:** En fil kan passera `step2_validate` men misslyckas på `step4_export`!

**Lösning:** Validator ska ENDAST acceptera det format som parser kan hantera.
Validator-regex bör ändras från `r'\^type:?\s+'` till `r'^\^type\s+'`.

---

### A.6 Felsökning

**"Inga frågor hittades"**
```
Orsak: Parser-regex matchar inte frågeheaders
Kontrollera:
  - # Q001 måste ha mellanslag + titel (inte bara # Q001\n)
  - ^type måste vara på egen rad utan kolon
```

**"Failed to generate question X"**
```
Orsak: Saknar required field för frågetypen
Kontrollera:
  - multiple_choice_single: @field: options, @field: answer
  - text_entry: {{blank_N}} placeholder, @field: blanks
  - inline_choice: {{dropdown_N}} placeholder, @field: dropdown_N
```

**"Resource validation failed"**
```
Orsak: Bild refererad men finns inte
Kontrollera:
  - Bildfilerna finns i samma mapp som markdown-filen
  - Filnamn matchar exakt (case-sensitive)
```

---

### A.7 Testa export manuellt

```bash
# Aktivera venv
cd packages/qf-pipeline
source .venv/bin/activate

# Testa parser direkt
python -c "
from qf_pipeline.wrappers import parse_file
result = parse_file('/path/to/questions.md')
print(f'Questions: {len(result[\"questions\"])}')
for q in result['questions']:
    print(f'  - {q.get(\"identifier\")}: {q.get(\"question_type\")}')
"

# Testa full export
cd ../qti-core
python main.py /path/to/questions.md /path/to/output.zip --verbose
```

---

*QuestionForge Workflow v1.1 | 2026-01-22*
