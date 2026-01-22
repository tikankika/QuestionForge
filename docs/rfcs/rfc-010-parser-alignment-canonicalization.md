# RFC-010: Parser Alignment & QFMD Canonicalization

**Status:** Draft  
**Author:** Claude + Niklas Karlsson  
**Created:** 2026-01-21  
**Updated:** 2026-01-21  
**Type:** Bug Fix + Architecture Decision

---

## Executive Summary

**TL;DR:** step2 (validator) and step4 (export) use different parsers with different strictness levels, creating a "validation passes but export fails" scenario. Users get actionable error reports from step2 but no automated way to fix them. **Proposed solution:** Create step3 (QFMD Canonicalization) to transform validated-but-non-canonical QFMD into the strict v6.5 format required by step4.

**The Gap:**
```
step2_validate: ✅ "42 errors - here's what to fix"
step3:          ❌ DOES NOT EXIST
step4_export:   ❌ "Inga fragor hittades" (0 questions)
```

**Impact:** This affects EVERY user who writes QFMD by hand or uses AI-generated questions. Real example: 40-question Entry Check Modul 2 file - step2 reports 42 fixable errors, step4 silently fails with 0 questions found.

---

## Problem Statement

### The Bug

QuestionForge has a **parser alignment problem**:

**step2 (Validation):**
- Uses: `validate_mqg_format.validate_content()` from QTI-Generator
- Behavior: Liberal parser that identifies deviations from v6.5
- Output: Detailed, actionable error reports

**step4 (Export):**
- Uses: `src.parser.markdown_parser.MarkdownQuizParser` from QTI-Generator  
- Behavior: Strict v6.5-only parser
- Output: Silently returns `{'questions': []}` if format doesn't match exactly

**Result:** Users get a perfect bug report from step2 but export still fails because step4 uses a different parser.

### Real-World Example

**File:** `Entry check modul2 FIXED.md` (40 QFMD questions)

**step2_validate output:**
```
Question 2 (Q002):
  Invalid question type: "multiple_choice" (check spelling and underscores)

Question 7 (Q007):
  Missing "correct_answers" section (required for multiple_response)

Question 3 (Q003):
  text_entry requires {{blank_N}} placeholder(s) in question text
  Missing "blanks" section or blank_N subsections

[... 39 more errors across 31 questions ...]

Summary: 42 errors, 0 warnings
STATUS: ❌ NOT READY
```

**step4_export output:**
```
Inga fragor hittades i filen
```

**What the validator tells us to fix:**
1. 18 questions: `^type: multiple_choice` → should be `^type: multiple_choice_single`
2. 8 questions: `multiple_response` missing `@field: correct_answers` section
3. 5 questions: `text_entry` missing `{{blank_N}}` placeholders and `@field: blanks`
4. Various: Missing `@end_field` markers, incorrect feedback nesting (`@subfield:` vs `@@field:`)

**Why export fails:** step4's parser expects EXACT v6.5 format. If type says `multiple_choice` instead of `multiple_choice_single`, parser doesn't recognize it as a question at all.

### Root Cause Analysis

Digging into the codebase:

**File:** `packages/qf-pipeline/src/qf_pipeline/wrappers/validator.py`
```python
from validate_mqg_format import validate_content

def validate_markdown(content: str) -> dict:
    is_valid, issues = validate_content(content)
    # Returns detailed issues with line numbers, messages
```

**File:** `packages/qf-pipeline/src/qf_pipeline/wrappers/parser.py`
```python
from src.parser.markdown_parser import MarkdownQuizParser

def parse_markdown(content: str) -> dict:
    parser = MarkdownQuizParser(content)
    return parser.parse()  # Returns {'questions': []} if format wrong
```

**The mismatch:** Both import from QTI-Generator-for-Inspera but use DIFFERENT parsers:
- Validator: `validate_mqg_format` (liberal, helpful)
- Export: `MarkdownQuizParser` (strict, silent)

**Design intent vs reality:**
- **Intent:** validator should catch issues before export
- **Reality:** validator is MORE permissive than export parser (catches issues but doesn't prevent export failure)

### Why step1 Doesn't Solve This

step1 (Guided Build) has transformers that are ALMOST right:

**File:** `packages/qf-pipeline/src/qf_pipeline/step1/transformer.py`
```python
class Transformer:
    def _register_all(self):
        self._transforms = {
            'normalize_type_names': ...,      # ✅ Has this!
            'extract_correct_answers': ...,   # ✅ Has this!
            'restructure_text_entry': ...,    # ✅ Has this!
            # But missing:
            # - Feedback nesting (@subfield: → @@field:)
            # - Placeholder consistency (dropdown_1 vs dropdown1_)
        }
```

**Problems with using step1:**

1. **Conceptual mismatch:** step1 is for **Legacy → QFMD** transformation (headers ##→###, @key:→^key), not **QFMD → Canonical QFMD**

2. **Incomplete transformations:**
   - Has `normalize_type_names` but only checks a small alias list
   - Has `extract_correct_answers` but looks for old `### Options` format, not `@field: options`
   - Missing feedback nesting conversion entirely

3. **Creates new bugs:** Example from our session:
   ```
   Before step1: ^type: multiple_choice ^identifier: Q001
   After step1:  ^type: multiple_choice ^identifier: Q001  # Type NOT fixed!
                 {{dropdown_1}}                            # Fixed placeholder
                 @field: dropdown1_options                 # But NOT field name!
   ```
   Now we have MISMATCHED placeholders: `{{dropdown_1}}` vs `dropdown1_options`

4. **Wrong input assumptions:** step1 expects semi-structured or legacy markdown, not well-formed QFMD with minor format issues

**Conclusion:** step1 transforms are **90% of what we need** but in the **wrong architectural layer**. They need to be:
- Moved to a new normalization step
- Updated to work with v6.5 @field: syntax (not legacy ### headers)
- Extended with missing transformations

---

## Proposed Solution

### Option A: New Step 3 - QFMD Canonicalization (RECOMMENDED)

Create a dedicated normalization step between validation and export:

```
┌─────────────────────────────────────────────────────────────┐
│                  Step 3: Canonicalization                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Input: Valid QFMD (any variant)                           │
│      ↓                                                      │
│  [1] Parse step2 validation errors                         │
│      ↓                                                      │
│  [2] Build transformation plan                             │
│      ↓                                                      │
│  [3] Apply rule-based fixes                                │
│      │                                                      │
│      ├─→ Type normalization (multiple_choice → _single)    │
│      ├─→ Generate correct_answers fields                   │
│      ├─→ Restructure text_entry to blanks format           │
│      ├─→ Convert feedback nesting (@subfield: → @@field:)  │
│      └─→ Ensure all @end_field markers present             │
│      ↓                                                      │
│  [4] Validate again (step2)                                │
│      ↓                                                      │
│  [5] If errors remain → iterate (max 3 times)              │
│      ↓                                                      │
│  Output: Canonical v6.5 QFMD ✅                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Key Features:**

1. **Error-driven transformations:**
   - Parse step2 validation output
   - Extract question ID + error type
   - Apply targeted fix for each error pattern

2. **Batch processing:**
   - Group errors by type (all "Invalid question type" together)
   - Apply transformations efficiently
   - Report progress

3. **Iterative refinement:**
   - Apply fixes → re-validate → apply more fixes
   - Maximum iterations: 3 (prevent infinite loops)
   - Report what was fixed vs what remains

4. **Safety features:**
   - Dry-run mode (preview changes)
   - Detailed change log (before/after)
   - User approval for ambiguous cases

**Implementation:**

```python
# packages/qf-pipeline/src/qf_pipeline/step3/

canonicalizer.py:
    class QFMDCanonicalizer:
        def canonicalize(self, content: str) -> (str, Report):
            """Transform QFMD to canonical v6.5 format."""

error_parser.py:
    class ValidationErrorParser:
        def parse(self, validation_report: str) -> List[Fix]:
            """Extract fixable issues from step2 output."""

transformations.py:
    # Reuse from step1/transformer.py but adapt for v6.5:
    - normalize_type_names()
    - generate_correct_answers()
    - restructure_text_entry()
    
    # New transformations:
    - convert_feedback_nesting()  # @subfield: → @@field:
    - normalize_placeholders()     # dropdown1 → dropdown_1
    - ensure_end_markers()         # Add missing @end_field
```

**MCP Tool:**

```python
@server.tool()
async def step3_canonicalize(
    file_path: Optional[str] = None,
    dry_run: bool = False,
    max_iterations: int = 3
) -> dict:
    """
    Canonicalize QFMD to strict v6.5 format.
    
    Uses step2 validation errors as transformation guide.
    Iteratively fixes until valid or max iterations reached.
    
    Returns:
        {
            'status': 'success' | 'partial' | 'failed',
            'iterations': 2,
            'fixes_applied': 42,
            'errors_remaining': 0,
            'change_log': [...] if not dry_run else None,
            'preview': [...] if dry_run else None
        }
    """
```

**User Experience:**

```bash
$ qf-pipeline step3_canonicalize

Step 3: QFMD Canonicalization
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 File: entry_check_modul2.md
📊 Initial: 42 errors

Iteration 1:
  ├─ Type normalization (18 questions)
  ├─ correct_answers generation (8 questions)
  ├─ Feedback nesting (40 questions)
  └─ Text entry restructure (5 questions)
  
✓ Applied 42 fixes in 2.1s

🔄 Re-validating...
📊 Result: 0 errors

✅ Canonical QFMD ready for export!
```

### Option B: Extend step1 with Canonicalization Mode

Add a `--mode=canonicalize` flag to step1:

```python
@server.tool()
async def step1_transform(
    question_id: Optional[str] = None,
    mode: str = "legacy"  # "legacy" | "canonicalize"
) -> dict:
    """
    Apply transformations.
    
    mode="legacy": Legacy → QFMD (current behavior)
    mode="canonicalize": QFMD → Canonical QFMD (new)
    """
```

**Pros:**
- Reuses existing infrastructure
- No new step number

**Cons:**
- Conceptually confusing (mixing two different transformation types)
- step1 Session state assumes semi-structured input
- Harder to maintain (two codepaths in same module)

**Recommendation:** ❌ Don't do this. step1 and step3 serve fundamentally different purposes.

### Option C: Make step4 Parser More Liberal

Modify `MarkdownQuizParser` to accept variant formats:

```python
TYPE_ALIASES = {
    'multiple_choice': 'multiple_choice_single',
    'mc': 'multiple_choice_single',
    # ... etc
}

def _extract_metadata_fields(self, block: str):
    original_type = self._get_type(block)
    normalized_type = TYPE_ALIASES.get(original_type, original_type)
    # ... use normalized_type
```

**Pros:**
- No new step needed
- "Liberal in what you accept, strict in what you output"

**Cons:**
- Hides format inconsistencies
- Makes QFMD spec unclear ("anything goes")
- Harder to maintain parser (complex normalization logic scattered)
- Loses benefits of canonical format (tooling, predictability)
- Doesn't solve feedback nesting, blanks format, etc.

**Recommendation:** ❌ Canonical format is valuable. Don't weaken the parser.

---

## Detailed Design: Step 3 Transformation Rules

### Rule 1: Type Normalization

```python
TYPE_ALIASES = {
    'multiple_choice': 'multiple_choice_single',
    'mc': 'multiple_choice_single',
    'mcq': 'multiple_choice_single',
    'single_choice': 'multiple_choice_single',
    'multi_response': 'multiple_response',
    'mr': 'multiple_response',
    'mcq_multi': 'multiple_response',
    'select_multiple': 'multiple_response',
    'tf': 'true_false',
    'true_false_single': 'true_false',
    'fill_blank': 'text_entry',
    'fill_in': 'text_entry',
    'cloze': 'text_entry',
    'dropdown': 'inline_choice',
    'select': 'inline_choice',
}

def normalize_type(content: str, question_id: str, original_type: str) -> str:
    """Normalize question type to canonical name."""
    canonical = TYPE_ALIASES.get(original_type.lower(), original_type)
    
    # Find and replace in question block
    pattern = rf'(# {question_id}.*?\^type:?\s+){re.escape(original_type)}'
    replacement = rf'\g<1>{canonical}'
    
    return re.sub(pattern, replacement, content, flags=re.DOTALL | re.IGNORECASE)
```

**Test Case:**
```
Before: ^type: multiple_choice
After:  ^type: multiple_choice_single
```

### Rule 2: Generate correct_answers Field

```python
def generate_correct_answers(content: str, question_id: str) -> str:
    """Extract [correct] markers and create @field: correct_answers."""
    
    # Find question block
    q_match = re.search(
        rf'(# {question_id}.*?)(?=# Q\d{{3}}|\Z)',
        content,
        re.DOTALL
    )
    if not q_match:
        return content
    
    q_block = q_match.group(1)
    
    # Extract options with [correct] markers
    correct_options = []
    options_match = re.search(
        r'@field:\s*options\s*\n(.*?)@end_field',
        q_block,
        re.DOTALL
    )
    if options_match:
        options_text = options_match.group(1)
        for match in re.finditer(r'([A-Z])\).*?\[correct\]', options_text):
            correct_options.append(match.group(1))
    
    if not correct_options:
        return content
    
    # Create correct_answers field
    correct_field = f"""
@field: correct_answers
{', '.join(correct_options)}
@end_field
"""
    
    # Insert after options field
    insertion_point = options_match.end()
    new_block = q_block[:insertion_point] + correct_field + q_block[insertion_point:]
    
    # Replace in content
    return content[:q_match.start()] + new_block + content[q_match.end():]
```

**Test Case:**
```
Before:
@field: options
A) Option 1 [correct]
B) Option 2
C) Option 3 [correct]
@end_field

After:
@field: options
A) Option 1 [correct]
B) Option 2
C) Option 3 [correct]
@end_field

@field: correct_answers
A, C
@end_field
```

### Rule 3: Restructure Text Entry

```python
def restructure_text_entry(content: str, question_id: str) -> str:
    """Convert text_entry to {{blank_N}} format with @field: blanks."""
    
    q_match = re.search(rf'(# {question_id}.*?)(?=# Q\d{{3}}|\Z)', content, re.DOTALL)
    if not q_match:
        return content
    
    q_block = q_match.group(1)
    
    # Extract correct_answer and alternatives
    correct_match = re.search(
        r'@field:\s*correct_answer\s*\n(.*?)@end_field',
        q_block,
        re.DOTALL
    )
    alternatives_match = re.search(
        r'@field:\s*accept_alternatives\s*\n(.*?)@end_field',
        q_block,
        re.DOTALL
    )
    
    if not correct_match:
        return content
    
    correct = correct_match.group(1).strip()
    alternatives = alternatives_match.group(1).strip().split('\n') if alternatives_match else []
    
    # Update question_text to include {{blank_1}}
    qt_match = re.search(
        r'(@field:\s*question_text\s*\n)(.*?)(@end_field)',
        q_block,
        re.DOTALL
    )
    if qt_match and '{{blank_1}}' not in qt_match.group(2):
        new_qt = f"{qt_match.group(1)}{qt_match.group(2).rstrip()}\n\nSvar: {{{{blank_1}}}}\n{qt_match.group(3)}"
        q_block = q_block[:qt_match.start()] + new_qt + q_block[qt_match.end():]
    
    # Create blanks field
    blanks_field = f"""
@field: blanks
@@field: blank_1
^Correct_Answers
- {correct}
{chr(10).join(f'- {alt.strip()}' for alt in alternatives if alt.strip())}
^Case_Sensitive No
@@end_field
@end_field
"""
    
    # Remove old correct_answer and accept_alternatives fields
    q_block = re.sub(
        r'@field:\s*correct_answer\s*\n.*?@end_field\s*',
        '',
        q_block,
        flags=re.DOTALL
    )
    q_block = re.sub(
        r'@field:\s*accept_alternatives\s*\n.*?@end_field\s*',
        '',
        q_block,
        flags=re.DOTALL
    )
    
    # Insert blanks field before feedback
    feedback_pos = re.search(r'@field:\s*feedback', q_block)
    if feedback_pos:
        q_block = q_block[:feedback_pos.start()] + blanks_field + "\n" + q_block[feedback_pos.start():]
    else:
        q_block += "\n" + blanks_field
    
    return content[:q_match.start()] + q_block + content[q_match.end():]
```

**Test Case:**
```
Before:
@field: question_text
Namnge de tre typerna av ML.
@end_field

@field: correct_answer
övervakad, oövervakad, förstärkt
@end_field

@field: accept_alternatives
supervised, unsupervised, reinforcement
@end_field

After:
@field: question_text
Namnge de tre typerna av ML.

Svar: {{blank_1}}
@end_field

@field: blanks
@@field: blank_1
^Correct_Answers
- övervakad, oövervakad, förstärkt
- supervised, unsupervised, reinforcement
^Case_Sensitive No
@@end_field
@end_field
```

### Rule 4: Convert Feedback Nesting

```python
def convert_feedback_nesting(content: str) -> str:
    """Convert @subfield: → @@field: in feedback sections."""
    
    # Find all feedback sections
    feedback_pattern = r'(@field:\s*feedback\s*\n)(.*?)(@end_field)'
    
    def convert_section(match):
        opening = match.group(1)
        feedback_content = match.group(2)
        closing = match.group(3)
        
        # Convert @subfield: correct → @@field: correct_feedback
        subfield_mapping = {
            'correct': 'correct_feedback',
            'incorrect': 'incorrect_feedback',
            'partial': 'partial_feedback',
            'unanswered': 'unanswered_feedback',
        }
        
        for old, new in subfield_mapping.items():
            # Replace @subfield: name with @@field: name_feedback
            feedback_content = re.sub(
                rf'@subfield:\s*{old}\s*\n',
                f'@@field: {new}\n',
                feedback_content
            )
            # Ensure proper nesting markers
            # Find content between @@field: and next marker
            feedback_content = re.sub(
                rf'(@@field:\s*{new}\s*\n.*?)(?=@@field:|@end_field|\Z)',
                r'\1@@end_field\n',
                feedback_content,
                flags=re.DOTALL
            )
        
        return opening + feedback_content + closing
    
    return re.sub(feedback_pattern, convert_section, content, flags=re.DOTALL)
```

**Test Case:**
```
Before:
@field: feedback
@subfield: correct
Korrekt!
@subfield: incorrect
Nej.
@end_field

After:
@field: feedback
@@field: correct_feedback
Korrekt!
@@end_field
@@field: incorrect_feedback
Nej.
@@end_field
@end_field
```

### Rule 5: Placeholder Consistency

```python
def normalize_placeholders(content: str) -> str:
    """Ensure placeholder {{dropdown_N}} matches field dropdown_N_options."""
    
    # Find all questions
    questions = re.findall(r'(# Q\d{3}.*?)(?=# Q\d{3}|\Z)', content, re.DOTALL)
    
    for q_block in questions:
        # Extract all {{dropdown_N}} placeholders
        placeholders = set(re.findall(r'\{\{dropdown_(\d+)\}\}', q_block))
        
        for num in placeholders:
            # Check if field uses dropdown1_options or dropdown_1_options
            has_underscore = bool(re.search(rf'@field:\s*dropdown_{num}_options', q_block))
            has_no_underscore = bool(re.search(rf'@field:\s*dropdown{num}_options', q_block))
            
            if has_no_underscore and not has_underscore:
                # Normalize field name to use underscore
                q_block = re.sub(
                    rf'(@field:\s*)dropdown{num}_options',
                    rf'\g<1>dropdown_{num}_options',
                    q_block
                )
        
        content = content.replace(q_block, q_block)
    
    return content
```

---

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1)

**Deliverables:**
- [ ] Create `packages/qf-pipeline/src/qf_pipeline/step3/` module
- [ ] Implement `ValidationErrorParser` (parses step2 output)
- [ ] Implement `QFMDCanonicalizer` (applies transformations)
- [ ] Add `step3_canonicalize` MCP tool
- [ ] Write unit tests for error parser

**Files:**
```
packages/qf-pipeline/src/qf_pipeline/step3/
├── __init__.py
├── canonicalizer.py      # Main orchestrator
├── error_parser.py       # Parse step2 validation output
├── transformations.py    # Individual transformation rules
└── tests/
    ├── test_error_parser.py
    ├── test_transformations.py
    └── test_canonicalizer.py
```

### Phase 2: Transformation Rules (Week 2)

**Deliverables:**
- [ ] Implement type normalization
- [ ] Implement correct_answers generation
- [ ] Implement text_entry restructuring
- [ ] Implement feedback nesting conversion
- [ ] Implement placeholder consistency
- [ ] Add comprehensive test cases for each rule

**Test Files:**
- `test_type_normalization.md` (18 questions with various type aliases)
- `test_correct_answers.md` (8 multiple_response questions)
- `test_text_entry.md` (5 text_entry questions with different patterns)
- `test_feedback_nesting.md` (feedback with @subfield:)

### Phase 3: Iteration & Safety (Week 3)

**Deliverables:**
- [ ] Implement iterative refinement loop
- [ ] Add dry-run mode (preview changes)
- [ ] Add detailed change logging
- [ ] Implement max iterations limit (prevent infinite loops)
- [ ] Add progress reporting

**Features:**
```python
canonicalize(
    content,
    dry_run=True,        # Preview only
    max_iterations=3,    # Safety limit
    report_progress=True # Show real-time progress
)
```

### Phase 4: Integration & Documentation (Week 4)

**Deliverables:**
- [ ] Connect to existing step0/step2/step4 workflow
- [ ] Update QuestionForge documentation
- [ ] Create user guide for step3
- [ ] Add examples to README
- [ ] Integration tests with real-world files

**Documentation:**
- `docs/pipeline/step3-canonicalization.md`
- `docs/qfmd/v6.5-canonical-format.md`
- `examples/canonicalization-examples.md`

---

## Success Metrics

### Phase 1 (MVP)
- [ ] Handles Entry Check Modul 2 (40 questions, 42 errors) → 0 errors
- [ ] Processing time <10 seconds
- [ ] 100% questions exportable after canonicalization

### Phase 2 (Production)
- [ ] Handles 95% of real-world QFMD files automatically
- [ ] <1% false positive fix rate
- [ ] User satisfaction >4/5

### Phase 3 (Ecosystem)
- [ ] Adopted by 50% of QuestionForge users
- [ ] 80% reduction in "export fails" support tickets
- [ ] Community-contributed transformation rules

---

## Alternative Considered: Unify Parsers

**Idea:** Make step2 and step4 use the SAME parser

**Approach:**
```python
# Both use MarkdownQuizParser
step2_validate: parse + validate structure
step4_export: parse + generate QTI
```

**Pros:**
- Guaranteed alignment (by definition)
- Simpler architecture (one parser, not two)

**Cons:**
- Loses step2's helpful error messages (validate_mqg_format is better at this)
- step4 parser is designed for extraction, not validation
- Would require significant refactoring of both wrappers
- Doesn't solve the "how to fix errors" problem

**Decision:** ❌ Rejected. Keep two parsers but add canonicalization step to bridge them.

---

## Open Questions

### Q1: Should step3 be mandatory or optional?

**Option A:** Always run automatically: `step2 → step3 → step4`  
**Option B:** User explicitly calls step3  
**Option C:** Auto-run if step2 detects errors

**Recommendation:** Start with B (explicit), move to C later (automatic with opt-out)

### Q2: How to handle ambiguous cases?

Example: `@field: answer` - is this `correct_answer` or `correct_answers`?

**Options:**
- Ask user (interactive prompt)
- Use question type heuristic (multiple_response → plural)
- Log warning and skip

**Recommendation:** Use question type heuristic + log decision

### Q3: Version targeting?

Should step3 support multiple QFMD versions?

```
step3_canonicalize --target=v6.5  # Default
step3_canonicalize --target=v7.0  # Future
```

**Recommendation:** v6.5 only for MVP, add version param in Phase 2

### Q4: Should step3 preserve comments?

Example: `# TODO: Improve this question`

**Recommendation:** Yes, preserve all non-QFMD content

---

## Impact Analysis

### For Users

**Positive:**
- ✅ Automated fixes (minutes instead of hours)
- ✅ Reliable export (no more silent failures)
- ✅ Educational (learn v6.5 format from fixes)
- ✅ Fast iteration (fix → validate → fix loop)

**Negative:**
- ⚠️ One more step to learn
- ⚠️ Might introduce unexpected changes (mitigated by dry-run)

**Net:** **Highly positive** - solves critical pain point

### For QuestionForge

**Positive:**
- ✅ Completes pipeline (fills the gap)
- ✅ Better UX (clear workflow)
- ✅ Format flexibility (accept variants, output canonical)
- ✅ Extensible (easy to add new rules)

**Negative:**
- ⚠️ Maintenance burden (new codebase)
- ⚠️ Testing complexity (many edge cases)

**Net:** **Positive** - improves product quality significantly

### For Ecosystem

**Positive:**
- ✅ Canonical format adoption (encourages consistency)
- ✅ Tool interoperability (other tools can target v6.5)
- ✅ Version migration path (future QFMD versions)

**Negative:**
- ⚠️ Might discourage liberal parsers in other tools

**Net:** **Positive** - raises ecosystem standards

---

## Risks & Mitigations

### Risk 1: Transformation Errors

**Risk:** Auto-fixes might misinterpret user intent

**Mitigation:**
- Dry-run mode (preview changes)
- Detailed change log (show before/after)
- User approval gates for ambiguous cases
- Comprehensive test suite

**Severity:** Medium  
**Likelihood:** Low (with good tests)

### Risk 2: Performance

**Risk:** Iterative normalization might be slow

**Mitigation:**
- Batch processing (group by error type)
- Optimize regex patterns
- Progress reporting (user sees it's working)
- Benchmark with large files (>100 questions)

**Severity:** Low  
**Likelihood:** Low

### Risk 3: False Positives

**Risk:** Fixing something that wasn't broken

**Mitigation:**
- Only apply fixes for errors reported by step2
- Don't modify questions with 0 errors
- Preserve original in .backup file

**Severity:** Medium  
**Likelihood:** Low

### Risk 4: Version Incompatibility

**Risk:** Future QFMD v7 might require different canonicalization

**Mitigation:**
- Version-aware transformations
- Target format parameter (`--target=v6.5`)
- Separate rule sets per version

**Severity:** Low  
**Likelihood:** Medium (future problem)

---

## Decision

**APPROVED:** Implement **Option A - New Step 3: QFMD Canonicalization**

**Rationale:**
1. Solves real user pain (Entry Check Modul 2 example)
2. Clean architectural layer (separation of concerns)
3. Extensible (easy to add new transformation rules)
4. Reuses existing transformations from step1 where possible
5. Provides educational value (users learn canonical format)

**Next Steps:**
1. Create RFC-011: QFMD v6.5 Canonical Format Specification
2. Implement Phase 1 (Core Infrastructure)
3. Test with Entry Check Modul 2 file
4. Iterate based on feedback

---

## Appendix A: Example Transformation Session

```
$ qf-pipeline step3_canonicalize --dry-run

Step 3: QFMD Canonicalization (DRY RUN)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 File: entry_check_modul2.md
📊 Initial validation: 42 errors in 31 questions

Preview of transformations:

┌─────────────────────────────────────────────────┐
│ Type Normalization (18 questions)              │
├─────────────────────────────────────────────────┤
│ Q002, Q004, Q006, Q008, Q010, Q014, Q018,      │
│ Q020, Q022, Q025, Q026, Q029, Q031, Q032,      │
│ Q033, Q034, Q038, Q039, Q040                   │
│                                                 │
│ Before: ^type: multiple_choice                 │
│ After:  ^type: multiple_choice_single          │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Generate correct_answers (8 questions)         │
├─────────────────────────────────────────────────┤
│ Q007, Q011, Q015, Q019, Q023, Q027, Q030, Q037 │
│                                                 │
│ Before: (missing)                              │
│ After:  @field: correct_answers                │
│         A, B, D                                 │
│         @end_field                              │
└─────────────────────────────────────────────────┘

[... more transformation previews ...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary:
  • Total transformations: 42
  • Questions affected: 31/40
  • Estimated time: 2.5 seconds

To apply these changes:
  qf-pipeline step3_canonicalize
```

---

## Appendix B: Error Pattern Registry

```python
ERROR_PATTERNS = {
    'invalid_type': {
        'pattern': r'Invalid question type: "([^"]+)"',
        'handler': normalize_type,
        'extract': ['type_name'],
        'batch': True,
    },
    
    'missing_correct_answers': {
        'pattern': r'Missing "correct_answers" section',
        'handler': generate_correct_answers,
        'extract': [],
        'batch': True,
    },
    
    'text_entry_format': {
        'pattern': r'text_entry requires {{blank_N}}',
        'handler': restructure_text_entry,
        'extract': [],
        'batch': False,  # Complex per-question logic
    },
    
    'missing_end_field': {
        'pattern': r'Missing @end_field',
        'handler': add_end_markers,
        'extract': ['field_name'],
        'batch': True,
    },
    
    # Future patterns:
    'missing_identifier': {...},
    'missing_points': {...},
    'invalid_feedback_structure': {...},
}
```

---

## References

- **QTI-Generator-for-Inspera:** External package providing parsers
- **Current validators:** `packages/qf-pipeline/src/qf_pipeline/wrappers/validator.py`
- **Current parsers:** `packages/qf-pipeline/src/qf_pipeline/wrappers/parser.py`
- **step1 transformers:** `packages/qf-pipeline/src/qf_pipeline/step1/transformer.py`
- **Entry Check Modul 2:** Real-world test case (40 questions, 42 errors)

---

**RFC Status:** Draft → Review → Approved → Implementation

**Implementation Timeline:** 4 weeks (Jan 22 - Feb 19, 2026)