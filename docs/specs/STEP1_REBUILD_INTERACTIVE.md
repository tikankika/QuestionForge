# STEP 1 REBUILD: Interactive Guide

**Problem:** Step 1 became auto-batch, not interactive guide  
**Solution:** Change flow to question-by-question with teacher decisions  
**Date:** 2026-01-08

---

## CURRENT FLOW (WRONG)

```
step1_start → step1_transform (all questions at once) → done
                    ↑
                    No teacher involvement!
```

## NEW FLOW (CORRECT)

```
step1_start
    ↓
┌─────────────────────────────────────────────────────────────┐
│                    QUESTION LOOP                             │
│                                                              │
│  step1_analyze (show issues for THIS question)              │
│       ↓                                                      │
│  CLAUDE PRESENTS:                                            │
│  "Q001 has 3 problems:                                       │
│   1. [AUTO] Old syntax @question: → ^question               │
│   2. [AUTO] Missing @end_field                              │
│   3. [ASK] Missing Bloom level in labels"                   │
│       ↓                                                      │
│  CLAUDE ASKS:                                                │
│  "Which Bloom level? [Remember] [Understand] [Apply]..."    │
│       ↓                                                      │
│  TEACHER ANSWERS: "Remember"                                │
│       ↓                                                      │
│  step1_fix_auto + step1_fix_manual                          │
│       ↓                                                      │
│  step1_next → next question                                 │
│       ↓                                                      │
│  (repeat until all questions done)                          │
└─────────────────────────────────────────────────────────────┘
    ↓
step1_finish → report
```

---

## CHANGED MCP TOOLS

### 1. step1_transform → REMOVE or CHANGE

```python
# OLD (wrong):
def step1_transform(question_id=None):
    """Transform all questions automatically"""
    # Run all transforms on all questions
    # No interaction
    
# NEW (correct):
def step1_transform(question_id=None):
    """
    Transform ONLY syntax fixes that are 100% safe.
    Returns list of what COULD NOT be fixed automatically.
    """
    # ONLY syntax transforms:
    # - @question: → ^question
    # - {{BLANK-1}} → {{blank_1}}
    # - Add @end_field
    
    # RETURN issues that require input:
    return {
        "auto_fixed": ["Syntax converted", "Added @end_field"],
        "needs_input": [
            {"field": "^labels", "prompt": "select_bloom"},
            {"field": "partial_feedback", "prompt": "suggest_feedback"}
        ]
    }
```

### 2. step1_analyze → KEEP but IMPROVE

```python
def step1_analyze(question_id=None):
    """
    Analyse ONE question and return issues CATEGORISED.
    """
    return {
        "question_id": "Q001",
        "question_type": "text_entry",
        
        # Categorise issues
        "auto_fixable": [
            {"id": 1, "message": "Old syntax @question:"},
            {"id": 2, "message": "Missing @end_field"}
        ],
        "needs_input": [
            {
                "id": 3, 
                "field": "^labels",
                "message": "Missing Bloom level",
                "prompt_type": "select_bloom",
                "options": ["Remember", "Understand", "Apply", "Analyze"]
            },
            {
                "id": 4,
                "field": "partial_feedback", 
                "message": "Missing partial_feedback",
                "prompt_type": "suggest_feedback",
                "suggestion": "Copy from correct_feedback?"
            }
        ],
        
        # Instruction to Claude
        "instruction": "Fix auto_fixable, ask user about needs_input"
    }
```

### 3. step1_fix → SEPARATE auto and manual

```python
def step1_fix_auto(question_id=None):
    """
    Apply ONLY automatic fixes.
    Return what was fixed and what remains.
    """
    return {
        "fixed": ["Syntax converted", "Added @end_field"],
        "remaining": [
            {"field": "^labels", "prompt": "select_bloom"},
            {"field": "partial_feedback", "prompt": "suggest_feedback"}
        ]
    }

def step1_fix_manual(question_id: str, field: str, value: str):
    """
    Apply ONE manual fix based on teacher input.
    """
    # Example: field="^labels", value="^labels #EXAMPLE_COURSE #Remember #Easy"
    return {
        "fixed": True,
        "field": field,
        "new_value": value
    }
```

### 4. NEW: step1_suggest

```python
def step1_suggest(question_id: str, field: str):
    """
    Generate suggestion for a field based on context.
    User can accept, modify, or write their own.
    """
    if field == "partial_feedback":
        # Copy from correct_feedback
        correct = get_field(question_id, "correct_feedback")
        return {
            "field": field,
            "suggestion": correct,
            "options": [
                ("accept", "Accept suggestion"),
                ("modify", "Modify"),
                ("custom", "Write own"),
                ("skip", "Skip")
            ]
        }
    
    if field == "^labels":
        # Generate based on question type and content
        return {
            "field": field,
            "suggestion": "^labels #EXAMPLE_COURSE #Digestion #Remember #Easy",
            "needs_confirmation": True
        }
```

---

## HOW CLAUDE USES TOOLS

### Current (wrong):
```
User: "Run Step 1 on the file"
Claude: 
  1. step1_start() 
  2. step1_transform()  ← Everything at once!
  3. "Done, 19 errors remaining"
```

### New (correct):
```
User: "Run Step 1 on the file"

Claude:
  1. step1_start()
  → "27 questions found in v6.3 format"
  
  2. step1_analyze()
  → "Q001 has 4 issues: 2 auto-fixable, 2 need input"
  
  3. step1_fix_auto()
  → "Fixed syntax. Remaining: Bloom level, partial_feedback"
  
  4. Claude to user:
  "Q001 is missing Bloom level. Which cognitive level does the question test?
   [Remember] [Understand] [Apply] [Analyze]"
  
  5. User: "Remember"
  
  6. step1_fix_manual(field="bloom", value="Remember")
  
  7. Claude to user:
  "Q001 is missing partial_feedback. Should I copy from correct_feedback?
   [Yes] [No, I'll write] [Skip]"
  
  8. User: "Yes"
  
  9. step1_fix_manual(field="partial_feedback", value=<copied>)
  
  10. step1_next()
  → "Q002 (2 of 27)"
  
  ... repeat for each question ...
  
  27. step1_finish()
  → Report
```

---

## BATCH-APPLY (IMPORTANT!)

When the same issue exists in multiple questions:

```python
def step1_batch_preview(issue_type: str):
    """
    Show all questions with the same issue.
    """
    return {
        "issue": "Missing partial_feedback",
        "affected_questions": ["Q001", "Q005", "Q006", "Q007", "Q009", ...],
        "count": 11,
        "preview": {
            "Q001": "Peristalsis is the wave movements...",
            "Q005": "Enzymes are proteins that...",
            # ... first 3 as preview
        }
    }

def step1_batch_apply(issue_type: str, fix_type: str, questions: list = None):
    """
    Apply the same fix to multiple questions.
    
    Args:
        issue_type: "missing_partial_feedback"
        fix_type: "copy_from_correct" or "custom"
        questions: List of questions, or None for all
    """
    return {
        "applied_to": ["Q001", "Q005", "Q006", ...],
        "success": 11,
        "failed": 0
    }
```

### Claude uses batch:
```
Claude: "11 questions are missing partial_feedback:
Q001, Q005, Q006, Q007, Q009, Q017, Q018, Q020, Q023, Q025

Do you want to:
1. Copy from correct_feedback for all 11
2. Go through one by one
3. Skip all"

User: "1"

Claude: step1_batch_apply("missing_partial_feedback", "copy_from_correct")
→ "Fixed 11 questions"
```

---

## IMPLEMENTATION PRIORITY

```
1. CHANGE step1_transform
   - Only syntax fixes
   - Return "needs_input" list
   
2. IMPROVE step1_analyze  
   - Categorise: auto_fixable vs needs_input
   - Include prompt_type and options
   
3. ADD step1_suggest
   - Generate suggestions for missing fields
   
4. ADD step1_batch_preview + step1_batch_apply
   - Streamline repetitive fixes
   
5. UPDATE prompts.py
   - Actually use PROMPTS dictionary
   - Format for Claude to present
```

---

## FLOW DIAGRAM

```
                    ┌─────────────────┐
                    │  step1_start    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
            ┌──────►│  step1_analyze  │◄──────┐
            │       └────────┬────────┘       │
            │                │                │
            │       ┌────────▼────────┐       │
            │       │  step1_fix_auto │       │
            │       └────────┬────────┘       │
            │                │                │
            │     ┌──────────▼──────────┐     │
            │     │  needs_input?       │     │
            │     └──────────┬──────────┘     │
            │                │                │
            │         ┌──────┴──────┐         │
            │         │             │         │
            │    ┌────▼────┐   ┌────▼────┐    │
            │    │ PROMPT  │   │  BATCH  │    │
            │    │ USER    │   │ PREVIEW │    │
            │    └────┬────┘   └────┬────┘    │
            │         │             │         │
            │    ┌────▼────┐   ┌────▼────┐    │
            │    │  USER   │   │  USER   │    │
            │    │ DECIDES │   │ DECIDES │    │
            │    └────┬────┘   └────┬────┘    │
            │         │             │         │
            │    ┌────▼────────────▼────┐     │
            │    │  step1_fix_manual    │     │
            │    │  OR step1_batch_apply│     │
            │    └──────────┬───────────┘     │
            │               │                 │
            │      ┌────────▼────────┐        │
            │      │  step1_next     │        │
            │      └────────┬────────┘        │
            │               │                 │
            │      ┌────────▼────────┐        │
            │      │  more questions?│────────┘
            │      └────────┬────────┘
            │               │ no
            │      ┌────────▼────────┐
            └──────│  step1_finish   │
                   └─────────────────┘
```

---

## EXAMPLE: Complete Session

```
USER: Run Step 1 on EXAMPLE_COURSE_Fys_v63.md

CLAUDE: [step1_start]
📁 Session started!
- File: EXAMPLE_COURSE_Fys_v63.md
- Format: v6.3 (needs upgrade to v6.5)
- Questions: 27

Shall I start with Q001?

USER: Yes

CLAUDE: [step1_analyze(Q001)]
**Q001: Muscle movement in the gastrointestinal tract**
Type: text_entry

Found 4 issues:
✅ AUTO: Convert @question: → ^question
✅ AUTO: Convert @tags: → ^labels  
✅ AUTO: Add @end_field
❓ INPUT: Missing partial_feedback

[step1_fix_auto]
Fixed 3 syntax issues.

Remaining: Q001 is missing partial_feedback.

Do you want to:
1. Copy from correct_feedback
2. Write your own
3. Skip

USER: 1

CLAUDE: [step1_fix_manual(field="partial_feedback", value=<copied>)]
✅ Q001 done!

[step1_next]
**Q002: Where is bile produced** (2 of 27)
...

--- AFTER 5 QUESTIONS ---

CLAUDE: I see that 9 more questions are missing partial_feedback.
Do you want to apply the same fix (copy from correct) to all?

[step1_batch_preview("missing_partial_feedback")]
Affected questions: Q005, Q006, Q007, Q009, Q017, Q018, Q020, Q023, Q025

1. Yes, fix all 9
2. No, go through one by one
3. Skip all

USER: 1

CLAUDE: [step1_batch_apply(...)]
✅ Fixed partial_feedback for 9 questions

--- CONTINUES ---

CLAUDE: [step1_finish]
📊 Step 1 Complete!

Results:
- 27 questions processed
- 24 fully complete
- 3 with warnings (Q013, Q021, Q023 - match format)
- 0 skipped

Ready for Step 2 validate?
```

---

## SUMMARY

| Old | New |
|-----|-----|
| Auto-batch everything | Question-by-question |
| No interaction | Claude asks, teacher answers |
| 19 errors left for Claude to fix | All errors handled in the loop |
| prompts.py unused | prompts.py actively used |

---

*Step 1 Rebuild Spec | 2026-01-08*
