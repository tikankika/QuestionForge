# M1 Stage 0: Material Analysis - Teacher Guide

## QUICK START FOR TEACHERS

This is the simplified version. Full details below.

### Step 1: Start Stage 0
Say: "Start M1 Stage 0 material analysis"

### Step 2: For Each Material
Say: "Analyze [filename.pdf]" 
[Upload the file when Claude asks]
Review Claude's analysis
Say: "Save and continue to next file"

### Step 3: Complete Stage 0  
Say: "Finalize Stage 0"

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

#### FOR CLAUDE: Critical Execution Rules

**RULE 1: ONE file per turn**
After listing materials:
- Ask user to upload FIRST file ONLY
- STOP - do not proceed until file uploaded

**RULE 2: Present before proceeding**
After user uploads ONE file:
- Analyze ONLY that ONE file
- Present findings
- Ask: "Ready to save this analysis?"
- STOP - do not analyze more files

**RULE 3: Save then ask for next**
After user confirms "save":
- Call save_m1_progress(action="add_material")
- Report progress: "X/N materials complete"
- Ask: "Upload next file: [filename.pdf]"
- STOP - do not proceed to next file

## TROUBLESHOOTING

**Problem: Claude tries to analyze multiple files at once**
Solution: Say "STOP. Analyze ONLY [filename.pdf]. Present findings and wait for my feedback."

**Problem: Claude proceeds to next file without my approval**
Solution: Say "STOP. Wait for my confirmation to save and continue."

**Problem: Claude skips to Stage 1 before all materials analyzed**
Solution: Say "STOP. Return to Stage 0. We have N materials remaining to analyze."

**Problem: Claude doesn't wait for file upload**
Solution: Say "STOP. I need to upload the file first. Ask me to upload [filename.pdf]."