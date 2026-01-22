SEPARATION: Methodology vs MCP
METHODOLOGY = "VAD & VARFÖR"
Location: {project_path}/methodology/m1/
Innehåll:

Pedagogiska instruktioner för Claude
Förklaringar av varför vi gör något
Exempel på bra vs dåligt
Dialogue strategies
Quality criteria

Filer:
methodology/m1/
├── m1_0_stage0_material_analysis.md  ← Pedagogiska instruktioner
├── m1_1_stage1_validation.md         ← Dialogue strategies
├── m1_2_stage2_emphasis.md
├── m1_3_stage3_examples.md
├── m1_4_stage4_misconceptions.md
├── m1_5_stage5_objectives.md
└── m1_6_best_practices.md
Exempel från m1_0_stage0_material_analysis.md:
markdown## FOR CLAUDE: Pre-Dialogue Analysis Strategy

You will analyze instructional materials to identify:
- Content emphasis patterns
- Learning priorities (Tiers 1-4)
- Instructional examples
- Common misconceptions

### Emphasis Signals to Look For:
1. **Repetition** - Topics mentioned 3+ times
2. **Time allocation** - Topics with substantial coverage
3. **Explicit priority** - Teacher states "viktigt för tentan"

### Tier Definitions:
TIER 1 - Essential:
  Multiple emphasis signals (2+)
  Foundation for other concepts
  Explicitly stated as critical

TIER 2 - Important:
  Single emphasis signal
  Substantial coverage (2+ pages)
  Supporting concepts

MCP = "HUR tekniskt"
Location: qf-scaffolding TypeScript kod
Ansvar:

Läsa filer från disk
Extrahera text (pdf-parse)
Returnera content till Claude Desktop
Spara data till working docs
Uppdatera YAML frontmatter
Logga events

Kod (förenklat):
typescriptasync function load_stage(module: string, stage: number, project_path: string) {
  // 1. READ methodology file
  const content = fs.readFileSync(
    `${project_path}/methodology/${module}/m${module}_${stage}_*.md`
  );
  
  // 2. RETURN to Claude Desktop
  return {
    content: content.toString(),
    metadata: { module, stage },
    tools_for_stage: ["read_materials", "update_stage0_working"]
  };
}

async function read_materials(project_path: string, filename?: string) {
  if (!filename) {
    // LIST mode
    return { files: fs.readdirSync(`${project_path}/00_materials/`) };
  }
  
  // EXTRACT mode
  const pdfBuffer = fs.readFileSync(`${project_path}/00_materials/${filename}`);
  const pdfData = await pdfParse(pdfBuffer);
  
  return {
    filename,
    text: pdfData.text,
    pages: pdfData.numpages
  };
}

KONKRET EXEMPEL: Stage 0 Material Analysis
Methodology säger (PEDAGOGISKT):
markdown## STAGE 0: MATERIAL ANALYSIS

**FOR CLAUDE:**
This is an INTERACTIVE process with the teacher.

Process:
1. List all materials
2. FOR EACH PDF:
   - Read the PDF text
   - Identify topics mentioned
   - Look for emphasis signals:
     * Repetition (how many times mentioned?)
     * Time allocation (how many pages?)
     * Explicit priority (does teacher say "viktigt"?)
   - Suggest tier classification
   - Note examples used in instruction
   - Note misconceptions addressed
   - DISCUSS with teacher
   - SAVE progress after teacher validates

Quality criteria for tier classification:
- Tier 1 requires 2+ emphasis signals
- Teacher's explicit priority statements override analysis
- When uncertain, ASK teacher rather than assume

**FOR TEACHERS:**
You will validate Claude's analysis of each PDF.
- Confirm tier classifications are accurate
- Correct misunderstandings
- Add pedagogical context Claude might miss
- Flag topics that are more/less important than text suggests
MCP gör (TEKNISKT):
typescript// 1. PROVIDE methodology content to Claude
load_stage("m1", 0, project_path)
  → Returns the markdown content above

// 2. PROVIDE PDF list to Claude
read_materials(project_path, null)
  → Returns: ["Vad är AI.pdf", "Bias.pdf", ...]

// 3. PROVIDE PDF text to Claude
read_materials(project_path, "Vad är AI.pdf")
  → Returns: { text: "AI är ett samlingsbegrepp...", pages: 5 }

// 4. SAVE Claude's analysis
update_stage0_working(project_path, "add_pdf_analysis", {
  pdf_name: "Vad är AI.pdf",
  topics: [...],
  tiers: {...}
})
  → Writes to 01_methodology/m1_stage0_working_notes.md
```

---

## FLÖDE MED TYDLIG SEPARATION
```
┌─────────────────────────────────────┐
│  Claude Desktop anropar MCP         │
│  load_stage(m1, 0, project_path)    │
└───────┬─────────────────────────────┘
        │
        ↓
┌────────────────────────────────────┐
│  MCP LÄSER (tekniskt):             │
│  {project_path}/methodology/m1/    │
│  m1_0_stage0_material_analysis.md  │
│                                    │
│  MCP RETURNERAR content            │
└───────┬────────────────────────────┘
        │
        ↓
┌─────────────────────────────────────────┐
│  Claude Desktop LÄSER methodology:      │
│  "STAGE 0: MATERIAL ANALYSIS            │
│   Process: List materials, read each,   │
│   identify emphasis signals, discuss    │
│   with teacher, save progress..."       │
│                                         │
│  Claude FÖRSTÅR pedagogiken:            │
│  "Jag ska leta efter repetition,        │
│   time allocation, explicit priority.   │
│   Tier 1 kräver 2+ signals.             │
│   När osäker, FRÅGA teacher."           │
└─────────────────────────────────────────┘
        │
        ↓
┌─────────────────────────────────────┐
│  Claude anropar MCP:                │
│  read_materials(project, null)      │
│  (teknisk operation: lista filer)   │
└───────┬─────────────────────────────┘
        │
        ↓
┌────────────────────────────────────┐
│  MCP HÄMTAR tekniskt:              │
│  fs.readdir("00_materials/")       │
│  Returns lista                     │
└───────┬────────────────────────────┘
        │
        ↓
┌─────────────────────────────────────┐
│  Claude ANVÄNDER pedagogiken:       │
│  "Methodology sa: List materials    │
│   först. MCP gav mig listan.        │
│   Nu ska jag visa den för teacher." │
│                                     │
│  Claude: "Jag ser 9 PDFer:          │
│  1. Vad är AI.pdf..."               │
└─────────────────────────────────────┘
        │
        ↓
┌─────────────────────────────────────┐
│  Claude anropar MCP:                │
│  read_materials(project, "Vad...")  │
│  (teknisk: hämta PDF text)          │
└───────┬─────────────────────────────┘
        │
        ↓
┌────────────────────────────────────┐
│  MCP EXTRAHERAR tekniskt:          │
│  pdfParse(buffer)                  │
│  Returns text                      │
└───────┬────────────────────────────┘
        │
        ↓
┌─────────────────────────────────────┐
│  Claude ANVÄNDER pedagogiken:       │
│  "Methodology sa: Leta efter        │
│   - Repetition (3+ mentions)        │
│   - Time allocation (2+ pages)      │
│   - Explicit priority               │
│                                     │
│  Jag läser texten... AI nämns 3×    │
│  ML får 2 sidor... Tier 1!          │
│                                     │
│  Methodology sa: Discuss with       │
│  teacher before saving."            │
│                                     │
│  Claude: "Topics: AI, ML...         │
│  Tier 1: AI def, ML                 │
│  Stämmer?"                          │
└─────────────────────────────────────┘

VARFÖR DENNA SEPARATION?
Fördelar:

Pedagog kan uppdatera methodology utan att ändra kod

Ändra tier-kriterier
Lägga till fler emphasis signals
Förbättra dialogue strategies


Utvecklare kan förbättra MCP utan att påverka pedagogik

Bättre PDF-parsing
Snabbare filhantering
Ny logging-struktur


Olika versioner för olika kurser

methodology/m1/ kan vara olika för gymnasiet vs högskola
MCP-koden är samma


Tydligare ansvar

Pedagog äger: VAD & VARFÖR
Utvecklare äger: HUR (tekniskt)
Claude kombinerar båda




SAMMANFATTNING
VadVarÄgs avÄndras närPedagogiska instruktionermethodology/*.mdPedagogPedagogiken ändrasTier definitionsmethodology/*.mdPedagogKriterier ändrasDialogue strategiesmethodology/*.mdPedagogProcessen förbättrasFilhanteringMCP TypeScriptUtvecklareTekniken förbättrasPDF parsingMCP TypeScriptUtvecklareNya featuresData savingMCP TypeScriptUtvecklareFormat ändras
Claude Desktop:

Läser methodology (pedagogik)
Anropar MCP (teknik)
Kombinerar båda för att utföra processen

Stämmer denna förståelse? 🎯