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

When something fails (like "0 frågor hittades"), the whole chain has already run.

---

## Solution: Mandatory Stop Points

Each phase MUST stop and present results before continuing.

```
M3 output ready
    │
    ▼
┌──────────────────────────────────────────┐
│ STOP 1: "Här är N frågor från M3"        │
│ - Visa sammanfattning                     │
│ - Vänta på: godkänn / ändra / avbryt     │
└──────────────────────────────────────────┘
    │
    ▼
M5 (en fråga i taget)
    │
    ▼
┌──────────────────────────────────────────┐
│ STOP 2a: "Fråga 1 av 5 (essay)"          │
│ - Visa tolkad QFMD                        │
│ - Vänta på: godkänn / ändra / hoppa      │
└──────────────────────────────────────────┘
    │
    ▼
(repeat för varje fråga...)
    │
    ▼
┌──────────────────────────────────────────┐
│ STOP 2b: "M5 klar - alla N frågor"       │
│ - Visa sammanfattning                     │
│ - Vänta på: fortsätt till validering     │
└──────────────────────────────────────────┘
    │
    ▼
Step 2 Validator
    │
    ▼
┌──────────────────────────────────────────┐
│ STOP 3: "Validering klar"                │
│ - N frågor validerade                     │
│ - X fel hittade (visa lista)             │
│ - Vänta på: fortsätt / fixa fel          │
└──────────────────────────────────────────┘
    │
    ▼
Step 3 Router
    │
    ▼
┌──────────────────────────────────────────┐
│ STOP 4: "Router rekommenderar..."        │
│ - Question Set (N frågor)                 │
│ - ELLER Individual Questions              │
│ - Vänta på: godkänn / ändra val          │
└──────────────────────────────────────────┘
    │
    ▼
Step 4 Export
    │
    ▼
┌──────────────────────────────────────────┐
│ STOP 5: "Export klar"                    │
│ - Visa: filename.zip                      │
│ - Visa: antal frågor exporterade          │
│ - Klart!                                  │
└──────────────────────────────────────────┘
```

---

## Stop Point Specifications

### STOP 1: M3 Output Review

**Trigger:** After M3 generates questions
**Display:**
```
══════════════════════════════════════════
M3 KLAR - Granskning innan M5
══════════════════════════════════════════

Genererade frågor: 5
Frågetyper:
  - essay: 3 st
  - multiple_choice_single: 2 st

Fil: questions/m3_output.md

Vad vill du göra?
  [1] Godkänn → Fortsätt till M5
  [2] Visa frågorna först
  [3] Ändra i filen manuellt
  [4] Avbryt
══════════════════════════════════════════
```

**Wait for:** Teacher choice (1-4)

---

### STOP 2a: M5 Per-Question Review

**Trigger:** M5 presents each question
**Display:**
```
══════════════════════════════════════════
M5 - FRÅGA 1 av 5 (essay)
══════════════════════════════════════════

TOLKAT FRÅN M3:
  Title: Grundbegrepp inom AI
  Type: essay
  Points: 3
  Tags: #understand #easy #elements_of_AI_chapter1

FRÅGETEXT:
  I materialet introduceras flera viktiga begrepp...

KONVERTERAD TILL QFMD:
  ^type essay
  ^identifier Q001
  ^points 3
  ^labels #understand #easy #elements_of_AI_chapter1

  @field: question_text
  I materialet introduceras...
  @end_field

Vad vill du göra?
  [1] Godkänn → Spara & nästa fråga
  [2] Ändra något (öppnar editor)
  [3] Hoppa över denna fråga
  [4] Radera denna fråga
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
M5 KLAR - Sammanfattning
══════════════════════════════════════════

Bearbetade: 5 frågor
  - Godkända: 4
  - Hoppade: 1
  - Raderade: 0

Fil sparad: questions/m5_output.md

Vad vill du göra?
  [1] Fortsätt → Kör Step 2 (validering)
  [2] Granska filen först
  [3] Avbryt
══════════════════════════════════════════
```

---

### STOP 3: Step 2 Validation Complete

**Trigger:** Validation finished
**Display:**
```
══════════════════════════════════════════
STEP 2 KLAR - Valideringsresultat
══════════════════════════════════════════

Validerade frågor: 4
Status: ✅ REDO FÖR EXPORT

Inga fel hittades.

Vad vill du göra?
  [1] Fortsätt → Step 3 Router
  [2] Granska filen
  [3] Avbryt
══════════════════════════════════════════
```

OR if errors:
```
══════════════════════════════════════════
STEP 2 KLAR - Valideringsresultat
══════════════════════════════════════════

Validerade frågor: 4
Status: ⚠️ FEL HITTADE

Fel:
  Q002: Missing ^identifier
  Q004: Unknown question type "essai"

Vad vill du göra?
  [1] Fixa felen (öppnar Step 1)
  [2] Exportera ändå (hoppa över felaktiga)
  [3] Granska filen
  [4] Avbryt
══════════════════════════════════════════
```

---

### STOP 4: Step 3 Router Decision

**Trigger:** Router analysis complete
**Display:**
```
══════════════════════════════════════════
STEP 3 - ROUTER BESLUT
══════════════════════════════════════════

Analyserade frågor: 4

REKOMMENDATION: Question Set
  Anledning: Fler än 3 frågor av samma typ

Alternativ:
  [1] Question Set (rekommenderat)
      → 1 QTI-fil med alla 4 frågorna

  [2] Individual Questions
      → 4 separata QTI-filer

Välj exportformat:
══════════════════════════════════════════
```

---

### STOP 5: Step 4 Export Complete

**Trigger:** Export finished
**Display:**
```
══════════════════════════════════════════
STEP 4 KLAR - Export färdig!
══════════════════════════════════════════

✅ Exporterat: 4 frågor
   Format: Question Set
   Fil: output/entry_check_2026-01-28.zip

Filen kan nu importeras till Inspera.

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
  approval_message: "M5 klar - 5 frågor bearbetade. Fortsätt?",
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
