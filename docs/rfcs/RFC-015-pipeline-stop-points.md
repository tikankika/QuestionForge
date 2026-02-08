# RFC-015: Pipeline Stop Points - Teacher Verification Gates

**Status:** Draft
**Date:** 2026-01-28
**Author:** Claude Code
**Problem:** Workflow runs too fast, doesn't stop for teacher verification

---

## Problem

Current behavior:
```
M3 → M5 → Step2 → Step3 → Step4   (runs continuously, no stops)
```

Teacher sees final result but has no chance to verify/correct at each step.

When something fails (like "0 questions found"), the whole chain has already run.

---

## Solution: Mandatory Stop Points

Each phase MUST stop and present results before continuing.

```
M3 output ready
    │
    ▼
┌──────────────────────────────────────────┐
│ STOP 1: "Here are N questions from M3"   │
│ - Show summary                            │
│ - Wait for: approve / change / cancel     │
└──────────────────────────────────────────┘
    │
    ▼
M5 (one question at a time)
    │
    ▼
┌──────────────────────────────────────────┐
│ STOP 2a: "Question 1 of 5 (essay)"       │
│ - Show interpreted QFMD                   │
│ - Wait for: approve / change / skip       │
└──────────────────────────────────────────┘
    │
    ▼
(repeat for each question...)
    │
    ▼
┌──────────────────────────────────────────┐
│ STOP 2b: "M5 complete - all N questions" │
│ - Show summary                            │
│ - Wait for: continue to validation        │
└──────────────────────────────────────────┘
    │
    ▼
Step 2 Validator
    │
    ▼
┌──────────────────────────────────────────┐
│ STOP 3: "Validation complete"            │
│ - N questions validated                   │
│ - X errors found (show list)              │
│ - Wait for: continue / fix errors         │
└──────────────────────────────────────────┘
    │
    ▼
Step 3 Router
    │
    ▼
┌──────────────────────────────────────────┐
│ STOP 4: "Router recommends..."           │
│ - Question Set (N questions)              │
│ - OR Individual Questions                 │
│ - Wait for: approve / change selection    │
└──────────────────────────────────────────┘
    │
    ▼
Step 4 Export
    │
    ▼
┌──────────────────────────────────────────┐
│ STOP 5: "Export complete"                │
│ - Show: filename.zip                      │
│ - Show: number of exported questions      │
│ - Done!                                   │
└──────────────────────────────────────────┘
```

---

## Stop Point Specifications

### STOP 1: M3 Output Review

**Trigger:** After M3 generates questions
**Display:**
```
══════════════════════════════════════════
M3 COMPLETE - Review before M5
══════════════════════════════════════════

Generated questions: 5
Question types:
  - essay: 3
  - multiple_choice_single: 2

File: questions/m3_output.md

What do you want to do?
  [1] Approve → Continue to M5
  [2] Show questions first
  [3] Edit file manually
  [4] Cancel
══════════════════════════════════════════
```

**Wait for:** Teacher choice (1-4)

---

### STOP 2a: M5 Per-Question Review

**Trigger:** M5 presents each question
**Display:**
```
══════════════════════════════════════════
M5 - QUESTION 1 of 5 (essay)
══════════════════════════════════════════

INTERPRETED FROM M3:
  Title: Basic concepts in AI
  Type: essay
  Points: 3
  Tags: #understand #easy #elements_of_AI_chapter1

QUESTION TEXT:
  The material introduces several important concepts...

CONVERTED TO QFMD:
  ^type essay
  ^identifier Q001
  ^points 3
  ^labels #understand #easy #elements_of_AI_chapter1

  @field: question_text
  The material introduces...
  @end_field

What do you want to do?
  [1] Approve → Save & next question
  [2] Edit something (opens editor)
  [3] Skip this question
  [4] Delete this question
══════════════════════════════════════════
```

**Wait for:** Teacher choice (1-4)
**After choice:** Update document, show next question

---

### STOP 2b: M5 Session Complete

**Trigger:** All questions processed
**Display:**
```
══════════════════════════════════════════
M5 COMPLETE - Summary
══════════════════════════════════════════

Processed: 5 questions
  - Approved: 4
  - Skipped: 1
  - Deleted: 0

File saved: questions/m5_output.md

What do you want to do?
  [1] Continue → Run Step 2 (validation)
  [2] Review file first
  [3] Cancel
══════════════════════════════════════════
```

---

### STOP 3: Step 2 Validation Complete

**Trigger:** Validation finished
**Display:**
```
══════════════════════════════════════════
STEP 2 COMPLETE - Validation Results
══════════════════════════════════════════

Validated questions: 4
Status: ✅ READY FOR EXPORT

No errors found.

What do you want to do?
  [1] Continue → Step 3 Router
  [2] Review file
  [3] Cancel
══════════════════════════════════════════
```

OR if errors:
```
══════════════════════════════════════════
STEP 2 COMPLETE - Validation Results
══════════════════════════════════════════

Validated questions: 4
Status: ⚠️ ERRORS FOUND

Errors:
  Q002: Missing ^identifier
  Q004: Unknown question type "essai"

What do you want to do?
  [1] Fix errors (opens Step 1)
  [2] Export anyway (skip invalid)
  [3] Review file
  [4] Cancel
══════════════════════════════════════════
```

---

### STOP 4: Step 3 Router Decision

**Trigger:** Router analysis complete
**Display:**
```
══════════════════════════════════════════
STEP 3 - ROUTER DECISION
══════════════════════════════════════════

Analysed questions: 4

RECOMMENDATION: Question Set
  Reason: More than 3 questions of same type

Options:
  [1] Question Set (recommended)
      → 1 QTI file with all 4 questions

  [2] Individual Questions
      → 4 separate QTI files

Select export format:
══════════════════════════════════════════
```

---

### STOP 5: Step 4 Export Complete

**Trigger:** Export finished
**Display:**
```
══════════════════════════════════════════
STEP 4 COMPLETE - Export finished!
══════════════════════════════════════════

✅ Exported: 4 questions
   Format: Question Set
   File: output/entry_check_2026-01-28.zip

The file can now be imported into Inspera.

══════════════════════════════════════════
```

---

## Implementation

### Option A: Prompt Engineering

Add to system prompt / CLAUDE.md:
```
IMPORTANT: After each pipeline step, STOP and present results.
Do NOT automatically continue to next step.
Wait for explicit teacher approval before proceeding.
```

**Pros:** No code changes
**Cons:** LLM might ignore, inconsistent

### Option B: MCP Tool Returns

Each tool returns `requires_approval: true`:
```typescript
return {
  success: true,
  requires_approval: true,
  approval_message: "M5 complete - 5 questions processed. Continue?",
  next_step: "step2_validate"
};
```

**Pros:** Enforced by tool design
**Cons:** Requires code changes

### Option C: Workflow State Machine

New tool: `pipeline_controller`
```typescript
// States: m3_review, m5_question, m5_complete, step2_review, step3_decision, step4_done
// Each state has required_action: "teacher_approval"
```

**Pros:** Full control
**Cons:** Complex implementation

---

## Recommendation

**Start with Option A** (prompt engineering) immediately.

Add to CLAUDE.md:
```markdown
## Pipeline Workflow - MANDATORY STOPS

IMPORTANT: The pipeline has mandatory teacher verification gates.

After EACH step, you MUST:
1. Present a clear summary
2. Show the specific options available
3. WAIT for teacher to choose
4. Do NOT automatically proceed to next step

Stop points:
- After M3: Show generated questions, wait for approval
- During M5: Show EACH question, wait for approval
- After M5: Show summary, wait for "continue to Step 2"
- After Step 2: Show validation results, wait
- After Step 3: Show router recommendation, wait
- After Step 4: Show export result, done

If teacher says "kör" or "continue" - proceed to next step only.
If teacher says "visa" or "show" - display details.
If teacher says "ändra" or "change" - allow edits.
```

**Then implement Option B** as tools are updated.

---

## Related Issues

### M5 Format Recognition

Current M5 flexible_parser recognizes:
- `### Q1`
- `## Question 1`
- `## Fråga 1`

Does NOT recognize:
- `**Title:** ...` / `**Stem:** ...` format

This needs separate fix - see M5 parser update.

---

## Open Questions

1. Should STOP be skippable with "kör allt" command?
2. How verbose should the summaries be?
3. Should we save state to allow resume after disconnect?

---

## Document Metadata

**Created:** 2026-01-28
**Status:** Draft
**Priority:** HIGH - Immediate usability issue
