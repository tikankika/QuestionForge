
DEL 1: Header och Översikt
markdown# M1 Material Analysis - Detaljerat Flöde

## Översikt
Detta dokument beskriver det exakta flödet för M1 Material Analysis, inklusive:
- Användarinteraktioner
- Tool calls
- Beslutspunkter
- Dataflöden

---

## STARTPUNKT
```
┌─────────────────────────────────────┐
│  Användare har material (10 PDFer)  │
│  Vill skapa entry check-frågor      │
└─────────────────┬───────────────────┘
                  │
                  ↓
```

---

## STEG 0: Projekt Initiering
```
┌──────────────────────────────────────────────┐
│  USER: "Skapa entry check från 10 PDFer"    │
└──────────────────┬───────────────────────────┘
                   │
                   ↓
         ┌─────────────────────┐
         │  step0_start        │
         │  entry_point: "m1"  │
         └─────────┬───────────┘
                   │
                   ↓
         ┌─────────────────────────────────┐
         │  Skapar projektstruktur:        │
         │  ├─ 00_materials/ (10 PDFer)    │
         │  ├─ 01_methodology/             │
         │  ├─ 02_working/                 │
         │  ├─ 03_output/                  │
         │  ├─ session.yaml                │
         │  └─ logs/session.jsonl          │
         └─────────┬───────────────────────┘
                   │
                   ↓
         ┌─────────────────────┐
         │  Projekt redo!      │
         │  SESSION CREATED    │
         └─────────────────────┘
```

DEL 2: M1 Start
markdown## STEG 1: M1 Material Analysis Start

### 1.1 Load Stage 0 (Introduction)
```
┌──────────────────────────┐
│  USER: "Börja M1"        │
└──────────┬───────────────┘
           │
           ↓
   ┌───────────────────┐
   │  load_stage       │
   │  module: m1       │
   │  stage: 0         │
   └───────┬───────────┘
           │
           ↓
   ┌────────────────────────────┐
   │  Läser m1_0_intro.md       │
   │  Uppdaterar session.yaml   │
   └───────┬────────────────────┘
           │
           ↓
   ┌────────────────────────────┐
   │  CLAUDE: Visar intro       │
   │  "M1: Material Analysis"   │
   │  "Låt oss börja..."        │
   └────────────────────────────┘
```

### 1.2 Load Stage 1 (Material Analysis)
```
┌───────────────────────────────┐
│  USER: "Fortsätt till Stage 1" │
└───────────┬───────────────────┘
            │
            ↓
    ┌───────────────────┐
    │  load_stage       │
    │  module: m1       │
    │  stage: 1         │
    └───────┬───────────┘
            │
            ↓
    ┌──────────────────────────────────┐
    │  Läser m1_1_stage0_material      │
    │  _analysis.md                    │
    │  Returnerar instruktioner        │
    └───────┬──────────────────────────┘
            │
            ↓
    ┌──────────────────────────────────┐
    │  CLAUDE: Förstår att ska:        │
    │  1. Lista PDFer                  │
    │  2. Läsa en i taget              │
    │  3. Fråga efter varje            │
    │  4. Notera viktigt i minnet      │
    └──────────────────────────────────┘
```
Vill du att jag fortsätter med resten? Det blir cirka 5-6 delar till.ja12:44DEL 3: PDF-läsning Process
markdown## STEG 2: Interaktiv PDF-läsning

### 2.1 Lista Tillgängliga PDFer
```
┌─────────────────────────────────────┐
│  CLAUDE: Anropar read_materials     │
│  (utan filename = list mode)        │
└────────────┬────────────────────────┘
             │
             ↓
     ┌───────────────────┐
     │  read_materials   │
     │  project_path: XX │
     │  filename: null   │
     └────────┬──────────┘
              │
              ↓
     ┌────────────────────────────┐
     │  Listar filer i            │
     │  00_materials/*.pdf        │
     │  Returns: {files: [...]}   │
     └────────┬───────────────────┘
              │
              ↓
     ┌────────────────────────────────────┐
     │  CLAUDE: "Jag ser 9 PDFer:         │
     │  1. Vad är AI.pdf                  │
     │  2. Bias.pdf                       │
     │  ... osv                           │
     │  Börja med 'Vad är AI.pdf'?"       │
     └────────┬───────────────────────────┘
              │
              ↓
     ┌────────────────┐
     │  USER: "Ja"    │
     └────────┬───────┘
              │
              ↓
```

### 2.2 Läs Första PDFen
```
┌─────────────────────────────────────┐
│  CLAUDE: Anropar read_materials     │
│  med filename                       │
└────────────┬────────────────────────┘
             │
             ↓
     ┌─────────────────────────┐
     │  read_materials         │
     │  filename: "Vad är AI"  │
     │  extract_text: true     │
     └────────┬────────────────┘
              │
              ↓
     ┌────────────────────────────┐
     │  Läser PDF                 │
     │  Extraherar text           │
     │  Returns: {                │
     │    filename: "...",        │
     │    text: "...",            │
     │    pages: 5                │
     │  }                         │
     └────────┬───────────────────┘
              │
              ↓
```

### 2.3 Claude Analyserar (I Minnet)
```
     ┌────────────────────────────────────┐
     │  CLAUDE WORKING MEMORY:            │
     │  ┌──────────────────────────────┐  │
     │  │ current_pdf: "Vad är AI"     │  │
     │  │ topics_found:                │  │
     │  │   - AI definition            │  │
     │  │   - Maskininlärning          │  │
     │  │   - Djupinlärning            │  │
     │  │ tier_suggestions:            │  │
     │  │   tier1: [AI def, ML]        │  │
     │  │   tier2: [Snäv vs AGI]       │  │
     │  │ examples_noted:              │  │
     │  │   - Hundbilder (ML)          │  │
     │  └──────────────────────────────┘  │
     └────────┬───────────────────────────┘
              │
              ↓
```

### 2.4 Claude Frågar Läraren
```
     ┌─────────────────────────────────────┐
     │  CLAUDE: "Jag har läst 'Vad är AI'  │
     │  Huvudtopics:                        │
     │  - AI definition                     │
     │  - Maskininlärning                   │
     │  Förslag:                            │
     │  - Tier 1: AI def, ML                │
     │  - Tier 2: Snäv vs AGI               │
     │  Stämmer? Nästa PDF?"                │
     └────────┬────────────────────────────┘
              │
              ↓
     ┌─────────────────────────────────────┐
     │  USER: "Ja bra, men snäv AI vs AGI  │
     │  är också Tier 1.                   │
     │  Nästa: Bias.pdf - KRITISKT"        │
     └────────┬────────────────────────────┘
              │
              ↓
```

### 2.5 Claude Uppdaterar Minnet
```
     ┌────────────────────────────────────┐
     │  CLAUDE WORKING MEMORY UPDATE:     │
     │  ┌──────────────────────────────┐  │
     │  │ tier1: [AI def, ML,          │  │
     │  │         Snäv vs AGI]  ←NEW   │  │
     │  │ tier2: []  ←CLEARED          │  │
     │  │ teacher_flags:               │  │
     │  │   "Bias.pdf": "KRITISKT"     │  │
     │  └──────────────────────────────┘  │
     └────────┬───────────────────────────┘
              │
              ↓
```

### 2.6 Repeat för Nästa PDF
```
     ┌─────────────────────────┐
     │  read_materials         │
     │  filename: "Bias.pdf"   │
     └────────┬────────────────┘
              │
              ↓
     [Samma process som 2.2-2.5]
              │
              ↓
     ┌────────────────────────────────┐
     │  WORKING MEMORY VÄXER:         │
     │  - Fler topics i tiers         │
     │  - Fler examples noterade      │
     │  - Fler misconceptions         │
     └────────┬───────────────────────┘
              │
              ↓
```

---

## LOOP: Remaining PDFs (3-9)
```
┌─────────────────────────────────────┐
│  FOR varje PDF (totalt 9 st):      │
│  ┌───────────────────────────────┐ │
│  │ 1. read_materials(filename)   │ │
│  │      ↓                        │ │
│  │ 2. Claude analyserar          │ │
│  │      ↓                        │ │
│  │ 3. Claude frågar läraren      │ │
│  │      ↓                        │ │
│  │ 4. Läraren svarar             │ │
│  │      ↓                        │ │
│  │ 5. Claude uppdaterar minnet   │ │
│  │      ↓                        │ │
│  │ 6. Nästa PDF                  │ │
│  └───────────────────────────────┘ │
└────────────┬────────────────────────┘
             │
             ↓ (Efter alla 9 PDFer)
```

DEL 4: Sammanfattning och Output Generation
markdown## STEG 3: Sammanfattning
```
┌─────────────────────────────────────────┐
│  CLAUDE WORKING MEMORY (FINAL):         │
│  ┌───────────────────────────────────┐  │
│  │ tier1: [8 topics]                 │  │
│  │ tier2: [5 topics]                 │  │
│  │ tier3: [2 topics]                 │  │
│  │ tier4_excluded: [1 topic]         │  │
│  │ examples: [8 key examples]        │  │
│  │ misconceptions: [10 found]        │  │
│  │ materials_analyzed: [9 files]     │  │
│  └───────────────────────────────────┘  │
└────────────┬────────────────────────────┘
             │
             ↓
     ┌───────────────────────────────────┐
     │  CLAUDE: "Klart! Sammanfattning:  │
     │  TIER 1: 8 topics                 │
     │  TIER 2: 5 topics                 │
     │  Examples: 8 st                   │
     │  Misconceptions: 10 st            │
     │  Stämmer? Generera filer?"        │
     └───────────┬───────────────────────┘
                 │
                 ↓
     ┌──────────────────┐
     │  USER: "Ja!"     │
     └───────┬──────────┘
             │
             ↓
```

---

## STEG 4: Generera Output-filer (5 filer)

### 4.1 File 1: Learning Objectives
```
┌─────────────────────────────────────┐
│  complete_stage                     │
│  module: m1                         │
│  stage: 5                           │
│  output: {                          │
│    type: "learning_objectives"      │
│    data: {                          │
│      tier1: [...8 LOs...]           │
│      tier2: [...5 LOs...]           │
│      tier3: [...2 LOs...]           │
│    }                                │
│  }                                  │
└────────────┬────────────────────────┘
             │
             ↓
     ┌───────────────────────────┐
     │  VALIDATES data           │
     │  GENERATES YAML + MD      │
     │  WRITES FILE              │
     │  UPDATES session.yaml     │
     │  LOGS event               │
     └───────┬───────────────────┘
             │
             ↓
     ┌───────────────────────────────────┐
     │  CREATED:                         │
     │  01_methodology/                  │
     │    m1_learning_objectives.md      │
     │  (~200 lines)                     │
     └───────┬───────────────────────────┘
             │
             ↓
```

### 4.2 Files 2-5: Samma Mönster
```
┌────────────────────────────────────────┐
│  FOR varje output type:                │
│  ┌──────────────────────────────────┐ │
│  │ 1. complete_stage(output_type)   │ │
│  │      ↓                           │ │
│  │ 2. Validate data                 │ │
│  │      ↓                           │ │
│  │ 3. Generate YAML + Markdown      │ │
│  │      ↓                           │ │
│  │ 4. Write file                    │ │
│  │      ↓                           │ │
│  │ 5. Update session.yaml           │ │
│  │      ↓                           │ │
│  │ 6. Log event                     │ │
│  └──────────────────────────────────┘ │
└────────────┬───────────────────────────┘
             │
             ↓
     ┌───────────────────────────────┐
     │  CREATED (5 files total):     │
     │  1. m1_learning_objectives    │
     │  2. m1_misconceptions         │
     │  3. m1_examples               │
     │  4. m1_emphasis_patterns      │
     │  5. m1_material_analysis      │
     │  Total: ~950 lines            │
     └───────┬───────────────────────┘
             │
             ↓
```

---

## STEG 5: M1 Complete
```
┌─────────────────────────────────────┐
│  session.yaml UPDATED:              │
│  methodology:                       │
│    m1:                              │
│      status: complete               │
│      outputs:                       │
│        learning_objectives: path    │
│        misconceptions: path         │
│        examples: path               │
│        emphasis_patterns: path      │
│        material_analysis: path      │
└────────────┬────────────────────────┘
             │
             ↓
     ┌───────────────────────────┐
     │  CLAUDE: "M1 COMPLETE! ✅  │
     │  5 filer skapade          │
     │  Nästa: M2?"              │
     └───────┬───────────────────┘
             │
             ↓
     ┌──────────────────────┐
     │  REDO FÖR M2         │
     └──────────────────────┘
```
Fortsätter med DEL 5...ja12:45DEL 5: Data-flöden och Beslutspunkter
markdown---

## DATA-FLÖDEN

### Materials → Memory → Files
```
┌────────────────┐
│  00_materials/ │
│  (10 PDFer)    │
└───────┬────────┘
        │
        │ read_materials (10x)
        ↓
┌────────────────────┐
│  CLAUDE MEMORY     │
│  ┌──────────────┐  │
│  │ Tiers        │  │
│  │ Examples     │  │
│  │ Misconcept.  │  │
│  │ Analysis     │  │
│  └──────────────┘  │
└───────┬────────────┘
        │
        │ complete_stage (5x)
        ↓
┌─────────────────────┐
│  01_methodology/    │
│  (5 output files)   │
└─────────────────────┘
```

### State Tracking
```
┌──────────────┐
│ session.yaml │
│ Tracks:      │
│ - Stages     │
│ - Outputs    │
│ - Progress   │
└──────┬───────┘
       │
       │ Updated by:
       ↓
┌──────────────────┐
│ - step0_start    │
│ - load_stage     │
│ - complete_stage │
└──────────────────┘
```

---

## KRITISKA BESLUTSPUNKTER

### Decision Point 1: Efter varje PDF
```
┌─────────────────────────┐
│  Claude har läst PDF    │
└──────────┬──────────────┘
           │
           ↓
     ┌─────────────────────┐
     │  Fråga läraren:     │
     │  "Stämmer detta?"   │
     └─────┬───────────────┘
           │
           ├─► JA: Fortsätt nästa PDF
           │
           └─► NEJ: Justera tier-klassificering
```

### Decision Point 2: Efter alla PDFer
```
┌────────────────────────┐
│  Alla PDFer lästa      │
└──────────┬─────────────┘
           │
           ↓
     ┌─────────────────────────┐
     │  Visa sammanfattning    │
     │  "Stämmer analysen?"    │
     └─────┬───────────────────┘
           │
           ├─► JA: Generera filer (complete_stage 5x)
           │
           └─► NEJ: Korrigera analysen
```

---

## TIDSESTIMERING
```
┌─────────────────────────────────────┐
│  M1 TOTAL: 60-90 min                │
│  ┌───────────────────────────────┐  │
│  │ Stage 0-1 Load:      5 min    │  │
│  │ PDF Reading:        50-70 min │  │
│  │   - 9 PDFs × 5-8 min each     │  │
│  │ Final Generation:    5-10 min │  │
│  │   - 5× complete_stage calls   │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

---

## TOOL ANVÄNDNING SAMMANFATTNING

### M1 Tools (17 total calls)
```
┌──────────────────────────┐
│  load_stage:       2     │
│  read_materials:  10     │
│  complete_stage:   5     │
│  ────────────────────    │
│  TOTAL:           17     │
└──────────────────────────┘
```

### Breakdown
```
load_stage (2):
  - Stage 0 (intro)
  - Stage 1 (material analysis)

read_materials (10):
  - 1× list mode (get all files)
  - 9× extract mode (one per PDF)

complete_stage (5):
  - learning_objectives
  - misconceptions
  - examples
  - emphasis_patterns
  - material_analysis
```

---

## NÄSTA STEG
```
┌─────────────────┐
│  M1 COMPLETE    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  M2 START       │
│  (Blueprint)    │
└─────────────────┘
```

DEL 6: Kritiska Insikter och Design Principer
markdown---

# KRITISKA INSIKTER

## 1. Interaktiv Process
- **INTE** bulk autonomous (Claude läser allt själv)
- **UTAN** collaborative (dialog efter varje PDF)
- Teacher guidance är ESSENTIAL

## 2. Memory Management
- Claude håller working memory UNDER hela M1
- Växer med varje PDF (tiers, examples, misconceptions)
- Transformeras till 5 filer vid slutet

## 3. State Tracking
- session.yaml uppdateras kontinuerligt
- Logs i session.jsonl för varje händelse
- Möjliggör resume om avbrott

## 4. Quality Gates
- Efter varje PDF: Validation med läraren
- Efter alla PDFer: Final approval innan file generation

---

# DESIGN PRINCIPER

## Separation of Concerns
- **Tools**: Technical operations (read, write, validate)
- **Methodology**: Pedagogical guidance (when, what, why)
- **Claude**: Orchestration (use tools according to methodology)

## Progressive Enhancement
- Start with minimum (list files)
- Build incrementally (read one at a time)
- Synthesize at end (create outputs)

## Teacher in Control
- Claude ASKS, never ASSUMES
- Teacher validates after each step
- Final approval before file generation

---

# POTENTIAL ISSUES & SOLUTIONS

## Issue 1: PDF Reading Fails
**Problem**: pdf-parse can't extract text
**Solution**: Return error → Claude asks teacher to provide text manually

## Issue 2: Memory Overflow
**Problem**: Too many PDFs → too much in memory
**Solution**: Implement progressive saves to temp file

## Issue 3: Teacher Changes Mind
**Problem**: "Actually, move X from Tier 1 to Tier 2"
**Solution**: Allow re-running complete_stage with overwrite flag

## Issue 4: Ambiguous Materials
**Problem**: No clear emphasis signals
**Solution**: Methodology instructs Claude to ask teacher explicitly

---

# EXEMPEL: COMPLETE M1 SESSION

## Input
```
Materials: 9 PDFer (34 sidor)
Entry point: m1
Goal: Entry check questions
```

## Process
```
1. step0_start → Projekt skapat
2. load_stage(m1, 0) → Intro
3. load_stage(m1, 1) → Material Analysis
4. read_materials() → Lista 9 PDFer
5. För varje PDF:
   - read_materials(filename)
   - Claude analyserar
   - Dialog med läraren
   - Uppdatera working memory
6. Sammanfattning → Läraren godkänner
7. complete_stage × 5 → Skapa alla filer
8. M1 complete → Redo för M2
```

## Output
```
01_methodology/
├── m1_learning_objectives.md (203 lines)
├── m1_misconceptions.md (258 lines)
├── m1_examples.md (195 lines)
├── m1_emphasis_patterns.md (212 lines)
└── m1_material_analysis.md (108 lines)

Total: 976 lines, 5 filer
```

## Tid
```
Total: 85 minuter
- PDF reading: 70 min (9 PDFs × ~8 min)
- Final generation: 10 min
- Loading stages: 5 min
```

---

# TEKNISK IMPLEMENTATION

## Tool Signatures

### step0_start
```typescript
step0_start({
  entry_point: "m1" | "m2" | "m3" | "m4" | "pipeline",
  materials_folder?: string,  // Required for m1
  source_file?: string,       // Required for m2/m3/m4/pipeline
  output_folder: string,
  project_name?: string
})
→ { project_path, session_id, materials_copied }
```

### load_stage
```typescript
load_stage({
  module: "m1" | "m2" | "m3" | "m4",
  stage: number,
  project_path: string
})
→ { content, metadata, tools_for_stage, next_action }
```

### read_materials
```typescript
read_materials({
  project_path: string,
  filename?: string,          // If omitted: list mode
  extract_text?: boolean      // Default: true
})
→ { 
  files?: string[],           // List mode
  filename?: string,          // Extract mode
  text?: string,              // Extract mode
  pages?: number              // Extract mode
}
```

### complete_stage
```typescript
complete_stage({
  project_path: string,
  module: "m1" | "m2" | "m3" | "m4",
  stage: number,
  output?: {
    type: string,             // "learning_objectives", "misconceptions", etc.
    data: object              // Structured data (validated)
  },
  overwrite?: boolean         // Default: false
})
→ { 
  success: boolean,
  filepath?: string,
  lines?: number
}
```

---

# SESSION STATE STRUKTUR

## session.yaml Format
```yaml
session:
  id: uuid
  created: timestamp
  entry_point: m1|m2|m3|m4|pipeline

materials:
  folder: 00_materials/
  count: number
  files: [...]

methodology:
  m1:
    status: not_started|in_progress|complete
    current_stage: number
    completed_stages: [...]
    outputs:
      learning_objectives: filepath
      misconceptions: filepath
      examples: filepath
      emphasis_patterns: filepath
      material_analysis: filepath
  m2:
    status: ...
    outputs: ...
  m3:
    status: ...
    outputs: ...
  m4:
    status: ...
    outputs: ...

working:
  questions_file: filepath
  question_count: number

output:
  exports: [...]
```

---

*Dokumentet uppdaterat: 2026-01-18*
*Version: 1.0*
*Total längd: ~800 rader*

