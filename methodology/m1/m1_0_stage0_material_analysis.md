# M1 Stage 0: Material Analysis - Teacher Guide

## Overview
You will guide Claude through analyzing your instructional materials 
one file at a time. This takes 60-90 minutes and requires your 
feedback after each material.

## Before Starting
- Have all materials in: project/00_materials/
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
- Identify topics, emphasis patterns, examples
- Present findings (3-5 minutes)
- Ask: "Does this look correct?"

**You should:**
- Review Claude's analysis
- Correct any misunderstandings
- Confirm: "Yes, this looks good" or provide corrections

---

### STEP 3: Save and Continue
**You say:** "Save this analysis and continue"

**Claude will:**
- Save the material analysis
- Report progress (e.g., "1/10 materials complete")
- Ask: "Which file should I analyze next?"

**You say:** "Analyze [next_filename.pdf]"

---

### STEP 4: Repeat for All Materials
Repeat Steps 2-3 for each material file.

---

### STEP 5: Complete Stage 0
After all materials analyzed:

**You say:** "Finalize Stage 0"

**Claude will:**
- Create Stage 0 summary document
- Ask if you want to proceed to Stage 1

---

## Common Issues

**Q: Claude tries to analyze multiple files at once**
A: Say: "Stop. Analyze ONLY [filename.pdf], present findings, and wait."

**Q: Claude skips to next file without my feedback**
A: Say: "Stop. Present your analysis of [current file] and wait for my feedback."

**Q: I need to pause mid-stage**
A: Say: "Save progress and pause." You can resume later with: "Continue Stage 0"

---

## For Claude: Stage 0 Instructions

*(This section is what Claude reads - minimal, focused)*

When teacher says "Analyze [filename.pdf]":
1. Read the material
2. Identify: topics, emphasis, examples, misconceptions
3. Present findings in structured format
4. Ask: "Does this look correct?"
5. STOP and wait for teacher response

When teacher says "Save and continue":
1. Call save_m1_progress(action="add_material", data={...})
2. Report progress
3. Ask: "Which file next?"
4. STOP and wait for teacher response

Do NOT:
- Analyze multiple files in one response
- Proceed without teacher confirmation
- Skip to Stage 1 without teacher approval