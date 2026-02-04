# RFC-013 Updates for Desktop

**Date:** 2026-01-25
**Updated:** 2026-01-25 (validation responsibilities)
**From:** Code session review + Desktop discussion

---

## Part A: Technical Fixes (4 items)

## Part B: Validation Responsibilities (6 decisions)

---

# PART A: TECHNICAL FIXES

## 4 Changes to Make in RFC-013

### 1. Question Type Names - FIX
**Wrong:** `multiple_choice_question`
**Correct:** `multiple_choice_single` (one correct) and `multiple_response` (multiple correct)

All correct type names:
```
multiple_choice_single    text_entry              match
multiple_response         text_entry_numeric      hotspot
true_false                text_entry_math         graphicgapmatch_v2
inline_choice             text_area               text_entry_graphic
essay                     audio_record            composite_editor
nativehtml
```

### 2. Remove Line Numbering - REMOVE
**Decision:** Line numbers are over-engineering. Question IDs are sufficient.

Remove:
- Section about "Line Numbering System"
- `001`, `002` prefix in all examples
- "strip line numbers before export" logic

Question ID (`Q001`, `Q002`) + YAML frontmatter provides all tracking we need.

### 3. Add RFC-012 Reference - ADD
In Introduction, add:

```markdown
### Related RFCs
- **RFC-012:** Subprocess architecture, unified validator, single source of truth for parsing
```

### 4. Step 2 Already Implemented - NOTE
In Step 2 section, add note:

```markdown
**Note:** Validator implemented in RFC-012. Uses `markdown_parser.validate()` -
same parser as Step 4. Guarantees: validate pass → export works.
```

---

## Summary

| Issue | Action |
|-------|--------|
| Question type names | Change `multiple_choice_question` → `multiple_choice_single` |
| Line numbering | Remove entirely - use Question IDs instead |
| RFC-012 reference | Add in Introduction |
| Step 2 validator | Note that it's already implemented |

---

# PART B: VALIDATION RESPONSIBILITIES

From discussion about overlap between M5, Step 1, Step 2, Step 3.

---

## Decision 5: M5 Responsibility - STRUCTURALLY CORRECT OUTPUT

M5 should generate markdown with correct structure from the start:

```
M5's responsibility:
├── Separators between questions (---)
├── Correct field syntax (@field: / @end_field)
├── Complete structure for each question type
└── Valid MQG format

OUTPUT: Structurally valid markdown
(May have content issues, but structure = OK)
```

**Update in RFC-013:** M5 section should clearly specify that output must be structurally correct.

---

## Decision 6: Step 1 Responsibility - SAFETY NET

Step 1 fixes "unexpected" structural problems that SHOULD NOT exist:

```
Step 1's responsibility:
├── M5 bugs (generated wrong syntax)
├── File corruption (user edited manually)
├── Import from older format
└── Unexpected edge cases

If M5 is perfect → Step 1 finds 0 issues ✅
```

**Update in RFC-013:** Step 1 is a safety net, not a mandatory fix station.

---

## Decision 7: "Structural" Definition - RELATIVE, NOT FIXED

**Key insight:** "Structural" means "Step 3 cannot auto-fix this RIGHT NOW"

```
Same error can be:
├── "Structural" → When Step 3 lacks pattern
└── "Auto-fixable" → When Step 3 has learned pattern

Over time: Fewer things are "structural" (Step 3 learns)
```

**Starting list for "structural" (always route to Step 1 in iteration 0):**
- Missing separator between questions
- Unclosed fields (@field without @end_field)
- Unknown field types

**Update in RFC-013:** Explain that "structural" is a relative category.

---

## Decision 8: Pattern Separation - TWO SEPARATE SYSTEMS

Step 1 and Step 3 have SEPARATE pattern databases:

```
Step 1 patterns:
├── Used ONLY in Step 1
├── Helps AI suggest fix to teacher
└── "Based on 15 previous files, separator is usually here"

Step 3 patterns:
├── Used ONLY in Step 3
├── Auto-applied without teacher
└── "This error has been auto-fixed 47 times successfully"

NO SHARING between systems (simpler, no edge cases)
```

**Update in RFC-013:** Specify that pattern databases are separate.

---

## Decision 9: Step 3 Routing - TRY AUTO-FIX EVEN "STRUCTURAL"

In iteration > 0, Step 3 tries to auto-fix even "structural" errors:

```python
# Step 3 logic (pseudocode)
for error in errors:
    pattern = find_pattern(error, min_confidence=0.9)

    if pattern:
        # Learned pattern with high confidence
        apply_pattern(error)  # Auto-fix
    else:
        if iteration == 0:
            route_to_step1(error)  # First time: teacher
        else:
            mark_unfixable(error)  # Already tried: give up
```

**Update in RFC-013:** Step 3 always tries to auto-fix if pattern exists.

---

## Decision 10: Skip Tracking - NO SHARING

```
Step 1: Teacher skips issue
    ↓ (no tracking to Step 3)
Step 2: Validation fails (same issue)
    ↓
Step 3: Tries to auto-fix
    ├── Has pattern? → Auto-fix → Success
    └── No pattern? → Route to Step 1 OR fail
```

**Result:** Teacher gets new chance in Step 1, or file fails.

**Update in RFC-013:** Step 3 does NOT know what was skipped in Step 1.

---

# SUMMARY OF ALL DECISIONS

| # | Decision | Brief |
|---|----------|-------|
| 1 | Question type names | `multiple_choice_single`, not `multiple_choice_question` |
| 2 | Line numbering | Remove - Question IDs are sufficient |
| 3 | RFC-012 reference | Add in Introduction |
| 4 | Step 2 validator | Already implemented (RFC-012) |
| 5 | M5 responsibility | Generate structurally correct output |
| 6 | Step 1 responsibility | Safety net for unexpected problems |
| 7 | "Structural" definition | Relative - "cannot be auto-fixed right now" |
| 8 | Pattern separation | Two separate databases (Step 1 / Step 3) |
| 9 | Step 3 routing | Try auto-fix even structural if pattern exists |
| 10 | Skip tracking | No sharing - skipped items fail in Step 2 |

---

## Flowchart to Add to RFC-013

```
M5: Generate markdown
  ↓ (should be structurally perfect)

Step 1: Review for unexpected issues
  ├─ 0 issues? → Step 2
  ├─ Issues? → Teacher fixes → Step 2
  └─ Skip? → Step 2 (will fail)

Step 2: Validate
  ├─ Valid? → Step 4 Export
  └─ Invalid? → Step 3

Step 3: Auto-fix iteration
  ├─ Auto-fixable? → Apply → Step 2 (loop)
  ├─ Missing content? → Route to M5
  ├─ Structural (no pattern)? → Route to Step 1
  └─ Max iterations? → Report failure
```
