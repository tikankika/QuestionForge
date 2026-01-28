# RFC 004: QFMD Template Alignment Audit

**Status:** Draft
**Date:** 2026-01-28
**Author:** Claude Code

---

## Summary

This RFC documents the audit of QFMD v6.5 format (RFC-002) against the actual XML templates in `templates/xml/`. The goal is to identify gaps where QFMD cannot express all the data that templates require.

---

## Background

### Source of Truth Hierarchy

```
templates/xml/                    ← ULTIMATE source of truth
    │                               (what Inspera requires)
    │
    ▼
RFC-002 (QFMD spec)              ← DOCUMENTS what templates need
    │                               (should be derived from templates)
    │
    ▼
markdown_parser.py               ← IMPLEMENTS RFC-002
    │
    ▼
Step 4 (Export)                  ← USES templates + parsed data
```

**Key insight:** Templates define what placeholders are needed → QFMD format must be able to express all that data.

---

## Audit Methodology

1. Extracted all `{{PLACEHOLDER}}` patterns from templates
2. Compared with RFC-002 QFMD syntax
3. Categorized as: ✅ Covered, ⚠️ Partial, ❌ Missing

---

## Audit Results

### Template Placeholder Inventory

Total unique placeholders found: **87**
Templates analyzed: **17** (16 question types + 1 manifest)

### Category: Basic Metadata

| Placeholder | Uses | RFC-002 Status | QFMD Syntax |
|-------------|------|----------------|-------------|
| `{{IDENTIFIER}}` | 36 | ✅ Covered | `^identifier Q001` |
| `{{TITLE}}` | 36 | ✅ Covered | `^title Rubrik` |
| `{{LANGUAGE}}` | 54 | ✅ Covered | `^language sv` |
| `{{MAX_SCORE}}` | 41 | ✅ Covered | `^points 1` |
| `{{TYPE}}` | 4 | ✅ Covered | `^type essay` |

### Category: Question Content

| Placeholder | Uses | RFC-002 Status | QFMD Syntax |
|-------------|------|----------------|-------------|
| `{{QUESTION_TEXT}}` | 26 | ✅ Covered | `@field: question_text` |
| `{{QUESTION_IMAGES}}` | 18 | ⚠️ Partial | Images in markdown (no explicit field) |
| `{{QUESTION_TEXT_WITH_FIELDS}}` | 4 | ⚠️ Implicit | `{{BLANK-1}}` placeholders in text |
| `{{QUESTION_TEXT_WITH_DROPDOWNS}}` | 2 | ⚠️ Implicit | `{{DROPDOWN-1}}` placeholders in text |
| `{{HTML_CONTENT}}` | 2 | ❌ Missing | For nativehtml type |

### Category: Scoring

| Placeholder | Uses | RFC-002 Status | QFMD Syntax | Notes |
|-------------|------|----------------|-------------|-------|
| `{{POINTS_EACH_CORRECT}}` | 20 | ✅ Covered | `^Points_per_correct_field` | |
| `{{POINTS_EACH_WRONG}}` | 22 | ❌ Missing | - | Negative points per wrong answer |
| `{{POINTS_ALL_CORRECT}}` | 28 | ❌ Missing | - | Bonus for all correct |
| `{{POINTS_MINIMUM}}` | 14 | ✅ Covered | `^Points_minimum` | Score floor |
| `{{POINTS_UNANSWERED}}` | 14 | ❌ Missing | - | Points if unanswered |
| `{{PARTIAL_CREDIT}}` | - | ✅ Covered | `^Partial_credit Yes` | |

### Category: Feedback

| Placeholder | Uses | RFC-002 Status | QFMD Syntax |
|-------------|------|----------------|-------------|
| `{{FEEDBACK_CORRECT}}` | 18 | ✅ Covered | `@@field: correct_feedback` |
| `{{FEEDBACK_INCORRECT}}` | 18 | ✅ Covered | `@@field: incorrect_feedback` |
| `{{FEEDBACK_UNANSWERED}}` | 20 | ❌ Missing | - |
| `{{FEEDBACK_PARTIALLY_CORRECT}}` | 15 | ❌ Missing | - |
| `{{FEEDBACK_ANSWERED}}` | 2 | ❌ Missing | For essay confirmation |

### Category: Multiple Choice

| Placeholder | Uses | RFC-002 Status | QFMD Syntax |
|-------------|------|----------------|-------------|
| `{{SHUFFLE}}` | 8 | ✅ Covered | `^Shuffle Yes` |
| `{{CHOICES}}` | 4 | ✅ Covered | `@field: options` with `A. B. C.` |
| `{{CORRECT_CHOICE_ID}}` | 9 | ✅ Covered | `@field: answer` |
| `{{CORRECT_CHOICES}}` | 2 | ✅ Covered | Multiple items in answer field |
| `{{MAPPING_ENTRIES}}` | 7 | ⚠️ Implicit | Derived from choices + answer |
| `{{PROMPT_TEXT}}` | 9 | ❌ Missing | Instruction above options |

### Category: True/False

| Placeholder | Uses | RFC-002 Status | QFMD Syntax |
|-------------|------|----------------|-------------|
| `{{TRUE_LABEL}}` | 3 | ❌ Missing | Default "True" |
| `{{FALSE_LABEL}}` | 3 | ❌ Missing | Default "False" |
| `{{CORRECT_CHOICE_ID}}` | - | ✅ Covered | `@field: answer` with T/F |

### Category: Text Entry / Blanks

| Placeholder | Uses | RFC-002 Status | QFMD Syntax |
|-------------|------|----------------|-------------|
| `{{INITIAL_LINES}}` | 6 | ❌ Missing | Editor height |
| `{{FIELD_WIDTH}}` | 4 | ❌ Missing | Input field width |
| `{{MAX_WORDS}}` | 2 | ❌ Missing | Word limit |
| `{{SHOW_WORD_COUNT}}` | 4 | ❌ Missing | Display counter |
| `{{EDITOR_PROMPT}}` | 5 | ❌ Missing | Placeholder text |
| `{{GAP_TEXTS}}` | 3 | ⚠️ Implicit | `@@field: blank_1` content |
| `{{GAP_SIZE}}` | 2 | ❌ Missing | Visual gap width |

### Category: Match

| Placeholder | Uses | RFC-002 Status | QFMD Syntax |
|-------------|------|----------------|-------------|
| `{{CORRECT_PAIRS}}` | 6 | ✅ Covered | `@field: pairs` with `->` |
| `{{LEFT_COLUMN_ITEMS}}` | 2 | ⚠️ Implicit | Derived from pairs |
| `{{RIGHT_COLUMN_ITEMS}}` | 2 | ⚠️ Implicit | Derived from pairs |
| `{{MAX_ASSOCIATIONS}}` | 2 | ❌ Missing | Max matches per item |
| `{{RANDOMIZE}}` | 2 | ⚠️ Partial | `^Shuffle` exists but unclear scope |

### Category: Graphics / Hotspot

| Placeholder | Uses | RFC-002 Status | QFMD Syntax |
|-------------|------|----------------|-------------|
| `{{BACKGROUND_IMAGE}}` | 6 | ❌ Missing | Image for hotspot/graphic questions |
| `{{IMAGE_TITLE}}` | 4 | ❌ Missing | Image accessibility |
| `{{IMAGE_LOGICAL_NAME}}` | 4 | ❌ Missing | Internal reference |
| `{{HOTSPOTS}}` | 4 | ❌ Missing | Clickable areas |
| `{{CORRECT_HOTSPOT_ID}}` | 4 | ❌ Missing | Correct area |
| `{{COORDS}}` | 2 | ❌ Missing | Shape coordinates |
| `{{SHAPE}}` | 2 | ❌ Missing | circle/rect/poly |
| `{{SHAPE_COLOR}}` | 2 | ❌ Missing | Visual feedback color |
| `{{SHAPE_OPACITY}}` | 2 | ❌ Missing | Visual feedback opacity |
| `{{CANVAS_HEIGHT}}` | 2 | ❌ Missing | Image container size |

### Category: Inline Choice (Dropdowns)

| Placeholder | Uses | RFC-002 Status | QFMD Syntax |
|-------------|------|----------------|-------------|
| `{{INTERACTIONS}}` | 2 | ⚠️ Implicit | `@field: dropdown_N` |
| `{{NUM_DROPDOWNS}}` | 1 | ⚠️ Implicit | Count of dropdown fields |

### Category: Composite Editor

| Placeholder | Uses | RFC-002 Status | QFMD Syntax |
|-------------|------|----------------|-------------|
| `{{RESPONSE_DECLARATIONS}}` | 10 | ⚠️ Auto-generated | From subfields |
| `{{OUTCOME_DECLARATIONS}}` | 8 | ⚠️ Auto-generated | From scoring |
| `{{NUM_FIELDS}}` | 2 | ⚠️ Implicit | Count of blanks |
| `{{NUM_RESPONSES}}` | 1 | ⚠️ Implicit | Count of responses |
| `{{INDIVIDUAL_SCORING}}` | 2 | ❌ Missing | Per-field scoring toggle |

### Category: Audio Record

| Placeholder | Uses | RFC-002 Status | QFMD Syntax |
|-------------|------|----------------|-------------|
| `{{UPLOAD_PROMPT}}` | 2 | ❌ Missing | Recording instruction |

### Category: Package/Manifest

| Placeholder | Uses | RFC-002 Status | QFMD Syntax |
|-------------|------|----------------|-------------|
| `{{RESOURCES}}` | 2 | N/A | Generated by export |
| `{{SECTIONS}}` | 2 | N/A | Generated by export |
| `{{TEST_PART_ID}}` | 2 | N/A | Generated by export |

---

## Summary Statistics

| Category | Covered | Partial | Missing | Total |
|----------|---------|---------|---------|-------|
| Basic Metadata | 5 | 0 | 0 | 5 |
| Question Content | 1 | 3 | 1 | 5 |
| Scoring | 2 | 0 | 4 | 6 |
| Feedback | 2 | 0 | 3 | 5 |
| Multiple Choice | 4 | 1 | 1 | 6 |
| True/False | 1 | 0 | 2 | 3 |
| Text Entry | 1 | 1 | 6 | 8 |
| Match | 1 | 3 | 1 | 5 |
| Graphics/Hotspot | 0 | 0 | 10 | 10 |
| Inline Choice | 0 | 2 | 0 | 2 |
| Composite | 0 | 4 | 1 | 5 |
| Audio | 0 | 0 | 1 | 1 |
| **TOTAL** | **17** | **14** | **30** | **61** |

**Coverage:** 17 fully covered (28%), 14 partial (23%), 30 missing (49%)

---

## Gap Analysis by Priority

### Priority 1: High Impact (affects common question types)

These gaps affect essay, multiple choice, and text entry - the most used types.

| Gap | Affects | Proposed QFMD Syntax |
|-----|---------|---------------------|
| `POINTS_EACH_WRONG` | multiple_response | `^Points_per_wrong -1` |
| `POINTS_ALL_CORRECT` | multiple_response | `^Points_all_correct 2` |
| `FEEDBACK_UNANSWERED` | all types | `@@field: unanswered_feedback` |
| `INITIAL_LINES` | essay, text_area | `^Initial_lines 10` |
| `MAX_WORDS` | essay | `^Max_words 500` |
| `SHOW_WORD_COUNT` | essay, text_area | `^Show_word_count Yes` |

### Priority 2: Medium Impact (affects specific types)

| Gap | Affects | Proposed QFMD Syntax |
|-----|---------|---------------------|
| `FEEDBACK_PARTIALLY_CORRECT` | multiple_response, match | `@@field: partial_feedback` |
| `PROMPT_TEXT` | multiple_choice | `^Prompt "Select one:"` |
| `TRUE_LABEL` / `FALSE_LABEL` | true_false | `^True_label "Correct"` |
| `EDITOR_PROMPT` | essay, text_area | `^Placeholder "Enter answer..."` |

### Priority 3: Low Impact (affects rare types)

| Gap | Affects | Notes |
|-----|---------|-------|
| All hotspot/graphic placeholders | hotspot, graphicgapmatch, text_entry_graphic | Complex types, may need separate RFC |
| `UPLOAD_PROMPT` | audio_record | Rare type |
| `INDIVIDUAL_SCORING` | composite_editor | Complex type |

---

## Current Workarounds

The parser and export likely handle missing QFMD syntax through:

1. **Defaults:** Missing values get sensible defaults
   - `INITIAL_LINES` → 10
   - `SHOW_WORD_COUNT` → false
   - `POINTS_EACH_WRONG` → 0

2. **Derivation:** Values calculated from other fields
   - `MAPPING_ENTRIES` derived from choices + answer
   - `LEFT_COLUMN_ITEMS` derived from pairs

3. **Hardcoded:** Some values are template constants
   - `TRUE_LABEL` → "True"
   - `FALSE_LABEL` → "False"

---

## Recommendations

### Short Term (no QFMD changes)

1. Document the defaults used by parser/export
2. Verify defaults match Inspera expectations
3. Add comments to templates showing default values

### Medium Term (extend QFMD v6.5)

1. Add Priority 1 gaps to RFC-002 as optional metadata
2. Update parser to handle new metadata
3. Update export to use new metadata (fall back to defaults)

### Long Term (QFMD v7.0)

1. Address graphics/hotspot types with proper syntax
2. Consider structured approach for complex types
3. Full alignment audit with updated templates

---

## Open Questions

1. Should missing features be added to v6.5 or wait for v7.0?
2. Are current defaults acceptable for production use?
3. Which graphic question types are actually used in practice?

---

## References

- RFC-002: QFMD v6.5 Format Specification
- `templates/xml/README.md`: Template documentation
- `templates/xml/*.xml`: Actual template files

---

## Appendix: Full Placeholder List

```
54 {{LANGUAGE}}
41 {{MAX_SCORE}}
36 {{TITLE}}
36 {{IDENTIFIER}}
28 {{POINTS_ALL_CORRECT}}
26 {{QUESTION_TEXT}}
22 {{POINTS_EACH_WRONG}}
20 {{POINTS_EACH_CORRECT}}
20 {{FEEDBACK_UNANSWERED}}
18 {{QUESTION_IMAGES}}
18 {{FEEDBACK_INCORRECT}}
18 {{FEEDBACK_CORRECT}}
15 {{FEEDBACK_PARTIALLY_CORRECT}}
14 {{UNANSWERED_CHECKS}}
14 {{POINTS_UNANSWERED}}
14 {{POINTS_MINIMUM}}
10 {{RESPONSE_DECLARATIONS}}
 9 {{PROMPT_TEXT}}
 9 {{CORRECT_CHOICE_ID}}
 8 {{SHUFFLE}}
 8 {{OUTCOME_DECLARATIONS}}
 8 {{ANY_CORRECT_CHECKS}}
 8 {{ALL_CORRECT_CHECKS}}
 7 {{MAPPING_ENTRIES}}
 6 {{INITIAL_LINES}}
 6 {{FIELD_SCORING_LOGIC}}
 6 {{CORRECT_PAIRS}}
 6 {{BACKGROUND_IMAGE}}
 5 {{EDITOR_PROMPT}}
 4 {{TYPE}}
 4 {{TOKEN_SIZE}}
 4 {{TOKEN_POSITION}}
 4 {{TOKEN_ORDER}}
 4 {{SHOW_WORD_COUNT}}
 4 {{REUSE_ALTERNATIVES}}
 4 {{QUESTION_TEXT_WITH_FIELDS}}
 4 {{INCORRECT_CHOICES_CHECK}}
 4 {{IMAGE_TITLE}}
 4 {{IMAGE_LOGICAL_NAME}}
 4 {{HOTSPOTS}}
 4 {{FIELD_WIDTH}}
 4 {{CORRECT_PAIR_CHECKS}}
 4 {{CORRECT_HOTSPOT_ID}}
 4 {{CHOICES}}
 4 {{ANY_CORRECT_PAIR_CHECKS}}
 3 {{TRUE_LABEL}}
 3 {{SCORE_WRONG}}
 3 {{RESPONSE_ID}}
 3 {{PREMISE_ID}}
 3 {{GAP_TEXTS}}
 3 {{FALSE_LABEL}}
 2 {{UPLOAD_PROMPT}}
 2 {{TEST_PART_ID}}
 2 {{SHAPE}}
 2 {{SHAPE_OPACITY}}
 2 {{SHAPE_COLOR}}
 2 {{SECTIONS}}
 2 {{SCORE_UNANSWERED}}
 2 {{RIGHT_COLUMN_ITEMS}}
 2 {{RESOURCES}}
 2 {{RANDOMIZE}}
 2 {{QUESTION_TEXT_WITH_DROPDOWNS}}
 2 {{PARTIAL_MATCH_LOGIC}}
 2 {{NUM_FIELDS}}
 2 {{MAX_WORDS}}
 2 {{MAX_ASSOCIATIONS}}
 2 {{LEFT_COLUMN_ITEMS}}
 2 {{INTERACTIONS}}
 2 {{INDIVIDUAL_SCORING}}
 2 {{INCORRECT_CHOICE_ID}}
 2 {{IMAGE_METADATA}}
 2 {{HTML_CONTENT}}
 2 {{HOTSPOT_ID}}
 2 {{GAP_SIZE}}
 2 {{FIELDS_HTML}}
 2 {{FEEDBACK_ANSWERED}}
 2 {{ENABLE_COLORING}}
 2 {{CORRECT_MATCH_LOGIC}}
 2 {{CORRECT_CHOICE_ID_N}}
 2 {{CORRECT_CHOICES}}
 2 {{COORDS}}
 2 {{CONTENT_WITH_GAPS}}
 2 {{CHOICE_MAP_RESPONSES}}
 2 {{CANVAS_HEIGHT}}
 1 {{RESPONSE_TEXT}}
 1 {{PREMISE_TEXT}}
 1 {{NUM_RESPONSES}}
 1 {{NUM_DROPDOWNS}}
 1 {{MAX_MATCHES}}
 1 {{MAP_RESPONSES}}
 1 {{LENGTH}}
 1 {{GAP_ITEMS}}
 1 {{GAP_IMAGES}}
 1 {{FIELD_FEEDBACK_LOGIC}}
 1 {{CORRECT_ANSWER_N}}
```

---

## Document Metadata

**Created:** 2026-01-28
**Last Updated:** 2026-01-28
**Status:** Draft - pending review
