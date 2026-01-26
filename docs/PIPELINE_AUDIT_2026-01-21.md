# QuestionForge Pipeline Audit - Deep Dive

**Date:** 2026-01-21  
**Purpose:** Complete revision of QuestionForge pipeline (step1 → step4)  
**Method:** Backward analysis (M4 → step1) to understand root causes

---

## Executive Summary

**Critical Finding:** QuestionForge pipeline has a **THREE-WAY MISMATCH**:
1. **step1 (Guided Build)** produces format A
2. **step2 (Validator)** checks for format B
3. **step4 (Export)** requires format C

This audit investigates:
- ✅ How M4/QTI-core actually works
- ⚠️ Whether validator updates created problems
- ❌ Why step1 output quality is poor
- 💡 Whether step3 (RFC-010) is the right solution

---

## PART 1: M4 (QTI-Core) Deep Dive

### Architecture Discovery

**Location:** `/Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/packages/qti-core/`

**What is qti-core?**
- Locally embedded copy of QTI-Generator-for-Inspera
- Used by QuestionForge step4 for QTI export
- **NOT** the same as Assessment_suite (which is for exam grading)

**Key Components:**
```
qti-core/
├── src/
│   ├── parser/
│   │   └── markdown_parser.py     ← step4 uses THIS
│   ├── generator/                  ← Creates QTI XML
│   └── packager/                   ← Creates ZIP
├── validate_mqg_format.py          ← step2 uses THIS
└── PARSER_UPDATE_SUMMARY.md        ← Recent changes (v6.5)
```

### Critical Discovery: TWO PARSERS!

#### Parser 1: `validate_mqg_format.py` (step2 uses)
**Purpose:** Pre-flight validation before QTI generation  
**Behavior:** STRICT format checking  

**What it checks:**
```python
VALID_TYPES = {
    'multiple_choice_single',  # ✅ Recognized
    'multiple_response',
    'text_entry',
    # NOT:
    'multiple_choice',          # ❌ Invalid
    'mc',                       # ❌ Invalid
}

REQUIRES_OPTIONS = {'multiple_choice_single', 'multiple_response', 'true_false'}
REQUIRES_ANSWER = {'multiple_choice_single', 'true_false'}
REQUIRES_CORRECT_ANSWERS = {'multiple_response'}
REQUIRES_BLANKS = {'text_entry', 'text_entry_math', 'text_entry_numeric'}
REQUIRES_DROPDOWNS = {'inline_choice'}
REQUIRES_SCORING = {'multiple_response', 'text_entry', 'inline_choice', ...}
```

**Validation strictness:**
- ERROR: Missing required fields (blocks export)
- WARNING: Recommended but optional fields
- INFO: Style suggestions

**Returns:** `ValidationReport` with errors/warnings

#### Parser 2: `src/parser/markdown_parser.py` (step4 uses)
**Purpose:** Extract questions for QTI XML generation  
**Behavior:** LIBERAL parsing with fallbacks  

**Key differences from validator:**
- Accepts some format variations (based on PARSER_UPDATE_SUMMARY.md)
- Has fallbacks for missing fields
- Can extract metadata from markdown if YAML missing
- Supports alternative formats (Evolution format, etc.)

**Returns:** `{'questions': [...]}` or `{'questions': []}`

### The Mismatch Problem

**Current flow:**
```
User file → step2 (validate_mqg_format) → reports errors
         → step4 (markdown_parser) → tries to parse anyway
```

**What we discovered:**
```
step2: "8 errors - missing scoring for inline_choice"
step4: SUCCESS - exports 40 questions anyway!
```

**Why?** `@field: scoring` is **OPTIONAL** in markdown_parser but validator **recommends** it.

### Parser Feature Matrix

| Feature | validate_mqg_format (step2) | markdown_parser (step4) |
|---------|----------------------------|------------------------|
| Type aliases (mc → multiple_choice_single) | ❌ Rejects | ⚠️ Unknown (needs testing) |
| Optional scoring field | ⚠️ Warns if missing | ✅ Accepts missing |
| @subfield: vs @@field: | ❌ Requires @@field: | ✅ Accepts both? (needs testing) |
| Placeholder format (dropdown_1 vs dropdown1) | ❌ Strict matching | ✅ Flexible? (needs testing) |
| Multiple @end_field | ❌ Validation issue | ✅ Parses anyway? (needs testing) |

**CRITICAL UNKNOWN:** We need to TEST markdown_parser's actual tolerance!

---

## PART 2: Validator Update Analysis

### What We Changed

**Original validator:** *(Need to check git history)*

**Current validator:** `validate_mqg_format.py` (v6.5)

**Questions to investigate:**
1. Did WE update the validator or was it from upstream?
2. If we updated it, what did we change?
3. Did our changes make it STRICTER or more LIBERAL?
4. Are validator errors aligned with parser requirements?

### Git History Investigation Needed

```bash
cd /Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/packages/qti-core
git log --oneline validate_mqg_format.py
git diff HEAD~5 validate_mqg_format.py
```

### Hypothesis to Test

**Hypothesis A:** Validator is TOO STRICT
- Reports errors that export parser ignores
- Creates false sense of "file is broken"
- Solution: Make validator match parser tolerance

**Hypothesis B:** Validator is CORRECTLY STRICT
- Reports real issues that WILL cause export problems
- Parser is too lenient (accepts broken files)
- Solution: Keep validator strict, fix files properly

**Test plan:**
1. Create file with validation errors
2. Try to export with step4
3. Check if export succeeds or fails
4. If succeeds: validator is too strict
5. If fails: validator is correct

---

## PART 3: step1 Forensics

### What step1 Does

**Location:** `/Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/packages/qf-pipeline/src/qf_pipeline/step1/`

**Components:**
```
step1/
├── transformer.py       ← Transformation rules
├── analyzer.py          ← Detect issues
├── detector.py          ← Find question patterns
├── parser.py            ← Parse semi-structured input
├── prompts.py           ← AI prompts for guidance
└── session.py           ← Session management
```

**Purpose:** Transform Legacy/semi-structured markdown → QFMD

### step1 Transformation Registry

From `transformer.py`:
```python
self._transforms = {
    # Legacy syntax transforms
    'metadata_syntax': ...,           # @key: → ^key
    'placeholder_syntax': ...,        # {{BLANK-1}} → {{blank_1}}
    'upgrade_headers': ...,           # ## → ###
    'add_end_fields': ...,            # Add missing @end_field
    'nested_field_syntax': ...,       # @field: → @@field:
    
    # Format normalization transforms
    'normalize_type_names': ...,      # multiple_choice → multiple_choice_single
    'extract_correct_answers': ...,   # [correct] → @field: correct_answers
    'restructure_text_entry': ...,    # old format → blanks format
}
```

### Problems We Observed

**From our session:**
1. ❌ Type not normalized (`multiple_choice` unchanged)
2. ❌ Placeholder mismatch (`{{dropdown_1}}` but `dropdown1_options`)
3. ❌ Too many `@end_field` markers
4. ❌ Feedback nesting not converted (`@subfield:` not → `@@field:`)

### Root Cause Analysis

**Why does step1 fail?**

**Theory 1: Wrong Input Assumptions**
- step1 expects Legacy Syntax (## headers, @key:)
- Users give it QFMD-ish input (already has @field:)
- Transforms don't trigger properly

**Theory 2: Incomplete Transforms**
- Transforms exist but have bugs
- Example: `normalize_type_names` only checks small alias list
- Example: `extract_correct_answers` looks for `### Options` not `@field: options`

**Theory 3: Transform Order Issues**
- Transforms applied in wrong order
- Example: Add @end_field before fixing nested fields → creates duplicates

**Theory 4: Regex Brittleness**
- Transforms use regex that's too specific
- Breaks on minor format variations

### Test Cases Needed

We need to test step1 with:
1. Pure Legacy Syntax (## headers, no @field:)
2. Pure QFMD v6.5 (correct format)
3. Mixed format (our actual use case)
4. QFMD with minor errors (what we're trying to fix)

**Expected:**
- Case 1: Should work ✅
- Case 2: Should pass through unchanged ✅
- Case 3: Should intelligently handle both ⚠️
- Case 4: Should fix errors ❌ (currently fails)

---

## PART 4: step3 RFC Critical Review

### RFC-010 Proposal Recap

**Proposed solution:** Create step3 (Canonicalization)
- Reads step2 validation errors
- Applies targeted fixes
- Iterates until valid

### Critical Questions

#### Q1: Is step3 the right solution?

**Pro step3:**
- ✅ Clean separation: step1 = Legacy→QFMD, step3 = QFMD→Canonical
- ✅ Targeted fixes based on actual errors
- ✅ Doesn't break existing step1 users
- ✅ Extensible (easy to add new transforms)

**Against step3:**
- ❌ Adds another step (complexity)
- ❌ step1 should already do this
- ❌ Might hide underlying problems

#### Q2: Can we fix step1 instead?

**Option:** Make step1 handle QFMD→Canonical transformations

**Pros:**
- ✅ No new step needed
- ✅ Users already know step1

**Cons:**
- ❌ Conceptual confusion (Legacy vs QFMD)
- ❌ step1 already complex
- ❌ Risk breaking existing workflows

#### Q3: Should validator be more lenient?

**Option:** Make validator match parser's tolerance

**Pros:**
- ✅ No "false positive" errors
- ✅ If parser accepts it, validator should too

**Cons:**
- ❌ Hides potential export issues
- ❌ Validator serves as quality gate
- ❌ Better to have strict validator + automated fix

#### Q4: Should we align parsers instead?

**Option:** Make markdown_parser stricter to match validator

**Pros:**
- ✅ Single source of truth
- ✅ No mismatch possible

**Cons:**
- ❌ Breaking change for existing users
- ❌ Loses flexibility
- ❌ Users might have legacy files that work now

### Recommendation

After analysis, RFC-010 (step3) is CORRECT approach because:

1. **Clear purpose:** QFMD→Canonical (not Legacy→QFMD like step1)
2. **Preserves validator strictness:** Good to catch issues early
3. **Automated fixes:** Saves user time
4. **Extensible:** Easy to add transforms as patterns emerge
5. **Non-breaking:** Doesn't change step1 or parser behavior

**BUT:** We need to update RFC-010 based on discoveries:

**Discovery 1:** Parser is MORE tolerant than we thought
- Some "errors" from validator don't block export
- step3 should prioritize BLOCKING errors

**Discovery 2:** Parser tolerance is unknown
- We need to TEST what markdown_parser actually accepts
- Update transform priorities based on real failures

**Discovery 3:** step1 has bugs that need fixing
- Separate issue from step3
- Fix step1 for Legacy→QFMD
- Create step3 for QFMD→Canonical

---

## PART 5: Action Plan

### Immediate Actions (This Week)

#### 1. Parser Tolerance Testing
**Goal:** Understand what markdown_parser ACTUALLY accepts

**Test matrix:**
```markdown
Test 1: Type aliases
- File with ^type: multiple_choice
- Does export succeed or fail?

Test 2: Feedback nesting
- File with @subfield: correct
- Does export succeed or fail?

Test 3: Placeholder mismatch
- File with {{dropdown_1}} and dropdown1_options
- Does export succeed or fail?

Test 4: Missing scoring
- inline_choice without @field: scoring
- Does export succeed or fail? (Already tested: SUCCEEDS)

Test 5: Multiple @end_field
- File with extra @end_field markers
- Does export succeed or fail?
```

**Method:**
1. Create test files in `/03_output/parser_tests/`
2. Run step4_export on each
3. Document results

#### 2. Validator History Analysis
**Goal:** Understand if WE changed validator or upstream did

```bash
cd qti-core
git log --all --follow validate_mqg_format.py
git diff <previous_version> validate_mqg_format.py
```

#### 3. step1 Minimal Test
**Goal:** Understand when step1 works vs fails

**Test cases:**
```markdown
# Test A: Pure Legacy
## Question Text
Question here

## Options
- A) Option 1 [correct]
- B) Option 2

# Test B: Pure QFMD v6.5
@field: question_text
Question here
@end_field

# Test C: QFMD with errors
^type: multiple_choice  ← Wrong type
@field: question_text
@end_field
```

Run step1_transform on each, check output quality.

### Medium-term Actions (This Month)

#### 1. Implement step3 MVP
- Based on RFC-010
- Priority: blocking errors only
- Test with Entry Check Modul 2

#### 2. Fix step1 Bugs
- Update `normalize_type_names` to work with @field: format
- Fix placeholder consistency
- Improve feedback nesting conversion

#### 3. Document Parser Behavior
- Create parser_tolerance_matrix.md
- Helps users understand validation vs export

### Long-term Actions (Next Quarter)

#### 1. Parser Unification Discussion
- Should we unify validate_mqg_format and markdown_parser?
- Or keep separate with clear documentation?

#### 2. RFC-011 (Self-Learning)
- Implement after step3 MVP stabilizes
- Learn from actual user corrections

---

## Key Findings Summary

### ✅ **CONFIRMED:**
1. qti-core has TWO parsers (validator + export)
2. Parsers have different tolerance levels
3. Some validation "errors" don't block export
4. step1 has bugs in transformation logic

### ⚠️ **NEEDS INVESTIGATION:**
1. Exact tolerance of markdown_parser (export parser)
2. Validator update history (did we make it stricter?)
3. step1 success rate on different input types

### 💡 **RECOMMENDATIONS:**
1. **Implement step3** per RFC-010 (correct solution)
2. **Test parser tolerance** to update transform priorities
3. **Fix step1 bugs** as separate effort
4. **Document** parser differences clearly

### 🚫 **DO NOT:**
1. Make validator more lenient (lose quality gate)
2. Force step1 to do QFMD→Canonical (wrong purpose)
3. Unify parsers without understanding impact

---

## Next Steps for This Session

**User (Niklas) should decide:**

**Option A:** Continue parser tolerance testing
- Create test files, run exports, document results
- This tells us what transforms are CRITICAL vs NICE-TO-HAVE

**Option B:** Implement step3 MVP now
- Fix Entry Check Modul 2 automatically
- Learn from real-world use

**Option C:** Deep-dive step1 bugs
- Understand why transforms fail
- Fix step1 for its intended purpose

**Option D:** Git history analysis
- Understand validator evolution
- Check if our changes created problems

**Which path?** 🤔

---

**Document Status:** DRAFT - Awaiting user decision on investigation direction

**Created:** 2026-01-21  
**Author:** Claude + Niklas Karlsson  
**Next Review:** After parser tolerance testing complete
