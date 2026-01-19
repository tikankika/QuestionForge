Document Information
Version: 2.0
Last Updated: 2026-01-19
Purpose: Complete workflow documentation for M1 (all 8 stages)
Audience: Developers implementing qf-scaffolding MCP

Table of Contents

Overview
Methodology vs Workflow Separation
M1 Complete Process Flow
Stage-by-Stage Workflows
Session Management
Common Patterns
Troubleshooting


Overview
What is M1?
M1: Material Analysis is the first module in the QuestionForge framework. It transforms instructional materials (lectures, slides, transcripts) into pedagogically grounded content architecture through systematic teacher-AI dialogue.
Duration
Total: 160-240 minutes (2.5-4 hours)

Can be completed in one session
Can be paused/resumed between stages
Progressive saving ensures no data loss

Key Principles

Teacher Authority - Teacher makes all pedagogical decisions
AI Execution - Claude handles systematic analysis and documentation
Progressive Building - Each stage builds on previous outputs
Validation Gates - Teacher approves before advancing
One Output Per Stage - Clear file structure, no overwhelming docs


Methodology vs Workflow Separation
Critical Distinction
┌─────────────────────────────────────────────────────────┐
│                    ARCHITECTURE                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────┐      ┌──────────────────┐   │
│  │   METHODOLOGY        │      │    WORKFLOW      │   │
│  │   (What to do)       │      │  (How it works)  │   │
│  ├──────────────────────┤      ├──────────────────┤   │
│  │                      │      │                  │   │
│  │ Location:            │      │ Location:        │   │
│  │ /methodology/m1/     │      │ /docs/workflows/ │   │
│  │                      │      │                  │   │
│  │ Contains:            │      │ Contains:        │   │
│  │ • FOR CLAUDE         │      │ • Process flow   │   │
│  │ • FOR TEACHERS       │      │ • MCP tools      │   │
│  │ • Dialogue patterns  │      │ • File outputs   │   │
│  │ • Quality criteria   │      │ • Logs           │   │
│  │ • Pedagogical guide  │      │ • Resume logic   │   │
│  │                      │      │                  │   │
│  │ Purpose:             │      │ Purpose:         │   │
│  │ Instructs HOW to     │      │ Documents        │   │
│  │ analyze, facilitate, │      │ MECHANICS of     │   │
│  │ validate content     │      │ execution        │   │
│  │                      │      │                  │   │
│  │ Loaded BY:           │      │ Used BY:         │   │
│  │ Workflow process     │      │ Developers       │   │
│  │ (via load_stage)     │      │ implementing MCP │   │
│  └──────────────────────┘      └──────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
File Mapping
Methodology Files (loaded at runtime):
/methodology/m1/
├── m1_0_stage0_introduction.md          → Stage 0
├── m1_1_stage1_material_analysis.md     → Stage 1
├── m1_2_stage2_validation.md            → Stage 2
├── m1_3_stage3_emphasis_refinement.md   → Stage 3
├── m1_4_stage4_example_cataloging.md    → Stage 4
├── m1_5_stage5_misconception_analysis.md→ Stage 5
├── m1_6_stage6_scope_boundaries.md      → Stage 6
└── m1_7_stage7_learning_objectives.md   → Stage 7
Workflow Files (this document):
/docs/workflows/
└── m1_complete_workflow.md              → All stages

M1 Complete Process Flow
Linear Progression
START
  │
  ├─→ Stage 0: Introduction (5 min)
  │     │
  │     ├─→ Stage 1: Material Analysis (60-90 min) ✓ LONGEST
  │     │     │
  │     │     ├─→ Stage 2: Validation (15-20 min)
  │     │     │     │
  │     │     │     ├─→ Stage 3: Emphasis Refinement (20-30 min)
  │     │     │     │     │
  │     │     │     │     ├─→ Stage 4: Example Cataloging (15-25 min)
  │     │     │     │     │     │
  │     │     │     │     │     ├─→ Stage 5: Misconception Analysis (15-25 min)
  │     │     │     │     │     │     │
  │     │     │     │     │     │     ├─→ Stage 6: Scope Boundaries (10-15 min)
  │     │     │     │     │     │     │     │
  │     │     │     │     │     │     │     └─→ Stage 7: Learning Objectives (20-30 min)
  │     │     │     │     │     │     │           │
  └─────┴─────┴─────┴─────┴─────┴─────┴───────────┘
                                                  │
                                                END
                                           (M1 Complete)
                                                  │
                                                  └─→ Ready for M2
Cumulative Outputs
Stage 0 → (Expectations set)
Stage 1 → m1_stage1_working_notes.md
Stage 2 → m1_stage2_validation.md
Stage 3 → m1_stage3_emphasis_patterns.md
Stage 4 → m1_stage4_examples.md
Stage 5 → m1_stage5_misconceptions.md
Stage 6 → m1_stage6_scope.md
Stage 7 → m1_stage7_learning_objectives.md ← FINAL OUTPUT
Each stage:

Reads previous stage outputs
Produces ONE new output document
Updates session state
Logs progress
Can be resumed if interrupted


Stage-by-Stage Workflows
Stage 0: Introduction
Duration: 5 minutes
Purpose: Set expectations, explain process
Pattern: Load → Present → Confirm
Workflow
┌──────────────────────────┐
│  USER: "Börja M1"        │
└──────────┬───────────────┘
           │
           ↓
┌─────────────────────────────────────┐
│  Claude anropar:                    │
│  TOOL: load_stage                   │
│    module: "m1"                     │
│    stage: 0                         │
│    project_path: "..."              │
└───────┬─────────────────────────────┘
        │
        ↓
┌────────────────────────────────────┐
│  MCP läser:                        │
│  methodology/m1/                   │
│  m1_0_stage0_introduction.md       │
│                                    │
│  Returnerar till Claude            │
└───────┬────────────────────────────┘
        │
        ↓
┌─────────────────────────────────────┐
│  Claude läser och presenterar:     │
│  "Välkommen till M1!                │
│                                     │
│   M1 består av 8 stages:            │
│   0. Introduction (detta)           │
│   1. Material Analysis (längst)     │
│   2. Validation                     │
│   3. Emphasis Refinement            │
│   4. Example Cataloging             │
│   5. Misconception Analysis         │
│   6. Scope Boundaries               │
│   7. Learning Objectives            │
│                                     │
│   Total tid: 2.5-4 timmar           │
│   Kan pausas mellan stages          │
│                                     │
│   Redo att börja?"                  │
└───────┬─────────────────────────────┘
        │
        ↓
┌──────────────────┐
│  USER: "Ja"      │
└───────┬──────────┘
        │
        ↓
Logs:
jsonl{"event": "m1_start", "timestamp": "08:00:00"}
{"event": "stage_load", "module": "m1", "stage": 0}
{"event": "stage_complete", "module": "m1", "stage": 0}
Session State:
yamlmethodology:
  m1:
    status: in_progress
    current_stage: 0
    stage0:
      status: complete
Output: None (expectations set verbally)

Stage 1: Material Analysis
Duration: 60-90 minutes (LONGEST stage)
Purpose: Interactive analysis of all instructional materials
Pattern: Load → List → [Loop: Read → Analyze → Discuss → Save] → Finalize
Workflow Overview
Load instructions
    │
List materials (read_materials with filename: null)
    │
FOR EACH material:
    │
    ├─→ Read text (read_materials with filename: "X")
    ├─→ Analyze content (Claude internal process)
    ├─→ Present findings to teacher
    ├─→ Teacher validates/corrects
    ├─→ Save progress (update_stage1_working)
    └─→ Confirm & continue
    │
Finalize (update_stage1_working with action: "finalize")
Detailed Flow
Part A: Initialize
load_stage(module: "m1", stage: 1, project_path: "...")
  ↓
MCP returns methodology content
  ↓
Claude reads instructions:
  - Emphasis signals (repetition, time, explicit priority)
  - Tier definitions (1-4)
  - Analysis framework
  - Dialogue patterns
Part B: List Materials
read_materials(project_path: "...", filename: null)
  ↓
MCP returns: {files: ["file1.pdf", "file2.pdf", ...]}
  ↓
Claude presents: "Jag ser N materials. Börjar med första?"
Part C: Analysis Loop (FOR EACH material)
C.1: read_materials(filename: "X.pdf")
     ↓
     MCP extracts text → Claude receives content
     
C.2: Claude analyzes (3-8 min, internal):
     - Identifies topics
     - Detects emphasis signals
     - Suggests tier classifications
     - Notes examples
     - Spots misconceptions
     
C.3: Claude presents findings (30 sec):
     "Topics: [...], Tiers: [...], Examples: [...]"
     
C.4: Teacher validates (1-2 min):
     "Correct / Move X from Tier 2 → Tier 1"
     
C.5: Claude updates working memory (10 sec)

C.6: update_stage1_working(
       action: "add_material",
       data: {
         material_name: "X.pdf",
         topics: [...],
         tiers: {...},
         examples: [...],
         misconceptions: [...],
         teacher_feedback: "..."
       }
     )
     ↓
     MCP appends to working_notes.md
     Updates YAML frontmatter
     Updates running synthesis
     Logs progress
     
C.7: Claude confirms: "✅ Material N/M analyzed. Nästa?"
Part D: Finalize
After all materials analyzed:
  ↓
Claude summarizes totals
  ↓
Teacher confirms
  ↓
update_stage1_working(action: "finalize")
  ↓
MCP adds FINAL SYNTHESIS section
Updates status: complete
MCP Tools Used
ToolCallsPurposeload_stage1×Load methodologyread_materialsN+1×List (1×) + Extract each material (N×)update_stage1_workingN+1×Save after each (N×) + Finalize (1×)
Total tool calls: ~(2N + 3) where N = number of materials
Output
File: 01_methodology/m1_stage1_working_notes.md
Structure:
markdown---
stage: 1
module: m1
session_id: xxx
started: [timestamp]
last_updated: [timestamp]
status: complete

materials:
  total: N
  analyzed: N
  completed: [list]

outputs:
  topics: X
  examples: Y
  misconceptions: Z
  tiers: {tier1: A, tier2: B, tier3: C, tier4: D}
---

# Stage 1: Material Analysis Working Notes

## Material 1/N: [filename] ✅
[Full analysis]

## Material 2/N: [filename] ✅
[Full analysis]

...

---

## RUNNING SYNTHESIS
[Updated after each material]

---

## FINAL SYNTHESIS
[Complete breakdown added at finalization]
Size: ~800-1200 lines (depends on material count and analysis depth)
Logs
jsonl{"event": "stage_load", "module": "m1", "stage": 1}
{"event": "materials_list", "count": N, "files": [...]}
{"event": "material_analyzed", "filename": "X.pdf", "duration_min": Y}
{"event": "progress_saved", "materials_analyzed": M, "total": N}
...
{"event": "stage_finalized", "module": "m1", "stage": 1}
{"event": "stage_complete", "module": "m1", "stage": 1, "duration_min": Z}
Session State
yamlmethodology:
  m1:
    current_stage: 1
    stage1:
      status: complete
      completed_at: [timestamp]
      materials_analyzed: N
      duration_min: Z
      output: "01_methodology/m1_stage1_working_notes.md"
    stage2:
      status: not_started
Common Issues
Issue: Material text extraction fails

Cause: Encrypted PDF, image-based, non-standard encoding
Solution: Teacher provides text manually (copy-paste)
Document: Note in working_notes: "Text provided manually"

Issue: Session interrupted mid-analysis

Check: working_notes.md YAML: materials.analyzed: M
Resume: Claude reads working notes, continues from material M+1
Prevention: Progressive saving ensures no data loss

Issue: Teacher changes mind about tiers later

Normal: Expected part of iterative process
Solution: Claude updates working memory, re-saves section
Document: Change noted in teacher feedback


Stage 2: Validation
Duration: 15-20 minutes
Purpose: Teacher reviews and validates entire tier structure
Pattern: Load → Present → Validate → Save
Workflow
load_stage(module: "m1", stage: 2)
  ↓
Claude reads Stage 1 output (working_notes.md)
  ↓
Claude presents complete tier structure for review
  ↓
Teacher validates or requests changes
  ↓
Claude documents validated structure
  ↓
Save validation output
Output
File: 01_methodology/m1_stage2_validation.md
Contains:

Validated tier structure (Tier 1-4)
Any corrections from teacher
Approval timestamp


Stage 3: Emphasis Refinement
Duration: 20-30 minutes
Purpose: Deep dive into WHY certain topics are prioritized
Pattern: Load → Question → Document → Save
Workflow
load_stage(module: "m1", stage: 3)
  ↓
Claude reads Stage 2 validated tiers
  ↓
FOR EACH Tier 1 topic:
  Claude asks: "Why is this Tier 1?"
  Teacher explains pedagogical rationale
  Claude documents reasoning
  ↓
Save emphasis patterns
Output
File: 01_methodology/m1_stage3_emphasis_patterns.md
Contains:

Tier 1 topics with rationale
Pedagogical reasoning
Priority patterns identified


Stage 4: Example Cataloging
Duration: 15-25 minutes
Purpose: Document effective instructional examples
Pattern: Load → Review → Catalog → Save
Workflow
load_stage(module: "m1", stage: 4)
  ↓
Claude presents examples from Stage 1
  ↓
Teacher selects most effective examples
  ↓
Claude catalogs with effectiveness notes
  ↓
Save example catalog
Output
File: 01_methodology/m1_stage4_examples.md
Contains:

Example ID, title, topic
Context of use
Effectiveness notes
Usage recommendations


Stage 5: Misconception Analysis
Duration: 15-25 minutes
Purpose: Identify common student errors and confusions
Pattern: Load → Review → Classify → Save
Workflow
load_stage(module: "m1", stage: 5)
  ↓
Claude presents misconceptions from Stage 1
  ↓
Teacher classifies by severity (critical/moderate/minor)
  ↓
Teacher provides correction strategies
  ↓
Save misconception registry
Output
File: 01_methodology/m1_stage5_misconceptions.md
Contains:

Misconception description
Severity level
Correction strategy
Persistence notes


Stage 6: Scope Boundaries
Duration: 10-15 minutes
Purpose: Define clear IN/OUT boundaries
Pattern: Load → Define → Document → Save
Workflow
load_stage(module: "m1", stage: 6)
  ↓
Claude reviews all topics (Tier 1-4)
  ↓
Teacher explicitly states:
  - What IS in scope (Tier 1-3)
  - What is OUT of scope (Tier 4)
  - Boundary cases
  ↓
Save scope document
Output
File: 01_methodology/m1_stage6_scope.md
Contains:

IN SCOPE (explicit list)
OUT OF SCOPE (explicit list)
Boundary notes
Rationale for exclusions


Stage 7: Learning Objectives
Duration: 20-30 minutes
Purpose: Synthesize validated learning objectives
Pattern: Load → Synthesize → Validate → Finalize
Workflow
load_stage(module: "m1", stage: 7)
  ↓
Claude reads ALL previous stage outputs
  ↓
Claude synthesizes learning objectives:
  - Based on Tier 1 topics (foundational)
  - Informed by emphasis patterns
  - Grounded in examples
  - Aware of misconceptions
  - Within defined scope
  ↓
Teacher validates objectives
  ↓
Claude creates final M1 output
  ↓
M1 COMPLETE
Output
File: 01_methodology/m1_stage7_learning_objectives.md ← FINAL M1 OUTPUT
Contains:

Validated learning objectives
Cognitive levels (Bloom's)
Assessment recommendations
References to supporting materials


Session Management
Session State (session.yaml)
yamlproject:
  name: "AI Course 2026"
  created: "2026-01-18T08:00:00Z"
  last_updated: "2026-01-18T12:00:00Z"

methodology:
  m1:
    status: in_progress  # not_started | in_progress | complete
    current_stage: 3
    started_at: "2026-01-18T08:00:00Z"
    
    stage0:
      status: complete
      completed_at: "2026-01-18T08:05:00Z"
    
    stage1:
      status: complete
      completed_at: "2026-01-18T09:30:00Z"
      materials_analyzed: 9
      duration_min: 70
      output: "01_methodology/m1_stage1_working_notes.md"
    
    stage2:
      status: complete
      completed_at: "2026-01-18T09:50:00Z"
      output: "01_methodology/m1_stage2_validation.md"
    
    stage3:
      status: in_progress
      started_at: "2026-01-18T09:55:00Z"
    
    stage4:
      status: not_started
    
    stage5:
      status: not_started
    
    stage6:
      status: not_started
    
    stage7:
      status: not_started
Session Logs (logs/session.jsonl)
Purpose:

Track exact progress within M1
Enable resume if interrupted
Document duration per stage
Audit trail of all events

Format: One JSON object per line
Example:
jsonl{"event": "m1_start", "timestamp": "2026-01-18T08:00:00Z"}
{"event": "stage_load", "module": "m1", "stage": 0, "timestamp": "08:00:15"}
{"event": "stage_complete", "module": "m1", "stage": 0, "timestamp": "08:05:00"}
{"event": "stage_load", "module": "m1", "stage": 1, "timestamp": "08:05:30"}
{"event": "materials_list", "count": 9, "files": [...], "timestamp": "08:06:00"}
{"event": "material_analyzed", "filename": "Vad är AI.pdf", "duration_min": 8, "timestamp": "08:14:00"}
{"event": "progress_saved", "materials_analyzed": 1, "total": 9, "timestamp": "08:14:05"}
...
{"event": "stage_finalized", "module": "m1", "stage": 1, "timestamp": "09:30:00"}
{"event": "stage_complete", "module": "m1", "stage": 1, "duration_min": 85, "timestamp": "09:30:05"}
Resume Capability
Scenario: Session interrupted at Stage 1, material 5/9
Resume Process:

Read session.yaml:

yaml   stage1:
     status: in_progress
     materials_analyzed: 5

Read logs/session.jsonl (last events):

jsonl   {"event": "material_analyzed", "filename": "Hallucinationer.pdf", ...}
   {"event": "progress_saved", "materials_analyzed": 5, "total": 9}

Read m1_stage1_working_notes.md YAML:

yaml   materials:
     analyzed: 5
     completed: ["Vad är AI.pdf", "Bias.pdf", ...]
     pending: ["Hållbarhet.pdf", "AI-ordbok.pdf", ...]

Claude continues from material 6/9
No data loss (progressive saving)


Common Patterns
Pattern 1: Load → Process → Save
All stages follow:
1. load_stage(module, stage, project_path)
2. Claude reads methodology instructions
3. Claude processes (reads previous outputs, dialogues with teacher)
4. Claude saves output
5. Session state updated
6. Logs written
Pattern 2: Progressive Outputs
Stage 1 output → Stage 2 input
Stage 2 output → Stage 3 input
Stage 3 output → Stage 4 input
...
All outputs → Stage 7 synthesis
Pattern 3: Teacher Validation Gates
Every stage:

Claude presents findings/proposals
Teacher validates or corrects
Claude saves approved version
No automatic progression without approval

Pattern 4: One Output Per Stage
Principle: Each stage produces EXACTLY ONE output document
Why:

Avoids overwhelming documentation
Clear file structure
Easy to track progress
Simple to reference

Exception: Stage 0 (no output, just orientation)

Troubleshooting
Issue: "Claude can't find methodology files"
Symptom: load_stage returns error
Cause: Methodology files not in expected location
Solution:

Check: /methodology/m1/m1_X_stageX_*.md exists
Verify qf-scaffolding MCP configured correctly
Check project_path is absolute

Issue: "Session state out of sync"
Symptom: session.yaml says stage 3, but outputs only exist for stage 1
Cause: Manual file deletion or editing
Solution:

Check which output files actually exist in 01_methodology/
Update session.yaml to match reality
Resume from last existing output

Issue: "Can't resume after interruption"
Symptom: Claude doesn't know where to continue
Solution:

Read session.yaml: methodology.m1.current_stage
Read logs: Last stage_complete event
Read working_notes.md YAML: status field
Resume from last completed stage + 1

Issue: "Working memory overflow in long stages"
Symptom: Claude loses track in Stage 1 with 15+ materials
Cause: Too much data accumulated
Solution:

Progressive saving mitigates this (after each material)
Claude can re-read working_notes.md if needed
Running Synthesis provides quick reference
Consider splitting materials into smaller batches


Next Steps After M1 Complete
When Stage 7 finishes:
M1 Status: complete
Output: m1_stage7_learning_objectives.md

Ready for → M2: Assessment Design
M2 will use:

M1 Stage 7: Learning objectives
M1 Stage 3: Emphasis patterns
M1 Stage 4: Examples
M1 Stage 5: Misconceptions
M1 Stage 6: Scope boundaries

M1 provides the pedagogical foundation for all subsequent modules.

Summary
M1 Essence:

8 stages, 2.5-4 hours total
Progressive building, each stage builds on previous
Teacher validation at every step
One output document per stage
Resumable via logs and session state
Methodology guides WHAT to do, workflow documents HOW it executes

Critical Success Factors:
✅ Teacher actively engaged throughout
✅ Progressive saving after each material (Stage 1)
✅ Claude presents findings, teacher validates
✅ Logs track progress for resume capability
✅ Methodology and workflow clearly separated
✅ One output per stage prevents overwhelm
Total Outputs: 7 files in 01_methodology/
m1_stage1_working_notes.md           (~1000 lines)
m1_stage2_validation.md              (~100 lines)
m1_stage3_emphasis_patterns.md       (~150 lines)
m1_stage4_examples.md                (~200 lines)
m1_stage5_misconceptions.md          (~200 lines)
m1_stage6_scope.md                   (~100 lines)
m1_stage7_learning_objectives.md     (~300 lines) ← FINAL
