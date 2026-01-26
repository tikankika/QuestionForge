# M1 Stage 0: Material Analysis - Teacher Guide

## QUICK START FOR TEACHERS

This is the simplified version. Full details below.

### Step 1: Start Stage 0
Say: "Start M1 Stage 0 material analysis"

### Step 2: For Each Material
Say: "Analyze [filename.pdf]"
[Upload the file when Claude asks]
Claude saves analysis DIRECTLY to file (no chat preview needed)
Say: "Continue to next file"

### Step 3: Complete Stage 0
Say: "Finalize Stage 0"

## Overview
You will guide Claude through analyzing your instructional materials
one file at a time. Each analysis is saved to its OWN file in preparation/.

**Output structure:**
```
preparation/
├── m1_material_01_[name].md    ← Analysis of first material
├── m1_material_02_[name].md    ← Analysis of second material
├── m1_material_03_[name].md    ← ... and so on
└── m1_stage0_summary.md        ← Final summary (after all materials)
```

## Before Starting
- Have all materials in: project/materials/
- Block out 60-90 minutes
- Be ready to provide feedback on Claude's analysis

---

## Step-by-Step Instructions

### STEP 1: Start Stage 0
**You say:** "Start M1 Stage 0 analysis"

**Claude will:**
- Load Stage 0 methodology
- List your materials
- Ask which file to analyze first

---

### STEP 2: Analyze First Material
**You say:** "Analyze [filename.pdf]"
*(Example: "Analyze Lecture_Week1.pdf")*

**Claude will:**
- Read the material
- Analyze and save DIRECTLY to file
- Report: "✅ Saved to preparation/m1_material_01_lecture_week1.md"
- Ask: "Continue to next file?"

**You should:**
- Say "yes" to continue, or
- Say "show me" to review the saved analysis

---

### STEP 3: Continue with Next Material
**You say:** "Yes, continue" or "Next"

**Claude will:**
- Analyze next material
- Save DIRECTLY to file
- Report progress (e.g., "2/10 materials complete")

---

### STEP 4: Repeat for All Materials
Repeat until all materials analyzed.

---

### STEP 5: Complete Stage 0
After all materials analyzed:

**You say:** "Finalize Stage 0"

**Claude will:**
- Create summary: preparation/m1_stage0_summary.md
- Ask if you want to proceed to Stage 1

---

## Common Issues

**Q: Claude shows analysis in chat instead of saving directly**
A: Say: "Don't show in chat. Save DIRECTLY to file."

**Q: Claude tries to analyze multiple files at once**
A: Say: "Stop. Analyze ONLY [filename.pdf] and save to file."

**Q: I want to review an analysis**
A: Say: "Show me m1_material_01.md" or check the file directly

**Q: I need to pause mid-stage**
A: Progress is saved in individual files. Resume anytime with: "Continue Stage 0"

---

#### FOR CLAUDE: Critical Execution Rules

**RULE 1: DIRECT FILE WRITE - NO CHAT PREVIEW**
- Analyze material internally
- Write DIRECTLY to file using write_project_file
- Do NOT show full analysis in chat
- Only show confirmation: "✅ Saved to [filename]"

**RULE 2: ONE FILE PER MATERIAL**
Each material gets its own file:
```
preparation/m1_material_01_[sanitized_name].md
preparation/m1_material_02_[sanitized_name].md
...
```

Filename format:
- `m1_material_` + 2-digit number + `_` + sanitized original name
- Sanitize: lowercase, spaces→underscores, remove special chars
- Example: "Vad är AI?.pdf" → "m1_material_01_vad_ar_ai.md"

**RULE 3: ONE file per turn**
After listing materials:
- Ask user to upload FIRST file ONLY
- STOP - do not proceed until file uploaded

**RULE 4: Save then ask for next**
After analyzing ONE file:
- Save to file immediately
- Report: "✅ Saved to preparation/m1_material_XX_name.md (X/N complete)"
- Ask: "Continue to next file?"
- STOP - wait for user

**CRITICAL: write_project_file Format**

```json
write_project_file({
  project_path: "<project_path>",
  relative_path: "preparation/m1_material_01_vad_ar_ai.md",
  content: "# Material 1: Vad är AI?\n\n**Typ:** Introduktion...\n\n## Topics & Begrepp\n...\n\n## Betoningar\n...\n\n## Instruktionsexempel\n...\n\n## Missuppfattningar\n..."
})
```

**Analysis Template:**
```markdown
# Material N: [Original Filename]

**Typ:** [Document type - lecture, textbook, slides, etc.]
**Källa:** [Source/course]
**Datum:** [Analysis date]

## Topics & Begrepp

**Primära begrepp (definierade):**
- [Term] - [definition as presented]
- ...

**Sekundära begrepp (nämnda):**
- [Term], [Term], ...

## Betoningar & Prioriteringar

1. **HÖGSTA:** [What's emphasized most]
2. **HÖG:** [Secondary emphasis]
3. **MEDEL:** [Moderate coverage]
...

## Instruktionsexempel

- [Concrete example from material]
- [Another example]
...

## Missuppfattningar

- **"[Common misconception]"** ❌ → [Correct understanding]
- ...
```

## TROUBLESHOOTING

**Problem: Claude shows long analysis in chat**
Solution: Say "STOP. Write DIRECTLY to file, don't show in chat."

**Problem: Claude tries to analyze multiple files at once**
Solution: Say "STOP. Analyze ONLY [filename.pdf]. Save to file and wait."

**Problem: Claude overwrites previous analysis**
Solution: Each material has unique filename - this shouldn't happen. Check filenames.

**Problem: Claude uses save_m1_progress instead of write_project_file**
Solution: Say "Use write_project_file to create separate files per material."
