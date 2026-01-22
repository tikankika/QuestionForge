# RFC-010 Complement: Lessons Learned

**Companion to:** RFC-010 Parser Alignment & QFMD Canonicalization  
**Type:** Post-Mortem & Learning Document  
**Author:** Claude + Niklas Karlsson  
**Created:** 2026-01-21  
**Session:** 2026-01-21 QuestionForge QFMD Parser Debugging

---

## Executive Summary

This document captures the lessons learned from discovering and diagnosing the "validation passes, export fails" bug in QuestionForge. It's a meta-analysis of the debugging process, architectural insights gained, and principles that emerged. **This is NOT about the bug itself** (that's in RFC-010) - **this is about HOW we found it and WHAT we learned.**

**Key Insight:** The gap between validation and export wasn't a parser bug - it was a **missing architectural layer**. We discovered this by methodically tracing the code path from user-facing symptoms back to root causes.

---

## Timeline: How We Got Here

### Session Context (Pre-Discovery)

**Starting Point:**
- User (Niklas) has 40 QFMD questions for Entry Check Module 2
- Previously fixed systematic formatting errors → `Entry check modul2 FIXED.md`
- QuestionForge parser was "broken" (reported all fields missing)
- User frustrated: "Why doesn't validation catch export errors?"

**Previous Session Breakthrough:**
- Parser behavior changed - now reads fields but reports specific format mismatches
- 42 validation errors identified across 18+8+5 questions
- step2_validate WORKS (reads file, reports errors)
- step4_export FAILS (reports 0 questions found)

**Critical Question That Started This Session:**
> "Validatorn ger ju vad vi behöver ändra i filen - är detta ett nytt step3 istället för att försöka använda step1 igen eller är detta något som kan fixas inom step1?"

This question revealed the core insight: **There's a missing step in the pipeline.**

---

## Discovery Process: Methodical Investigation

### Phase 1: Understanding the Symptom (15 min)

**Observation:**
```
step2_validate: 42 specific, actionable errors
step4_export:   "Inga fragor hittades i filen" (0 questions)
```

**First Hypothesis:** "Maybe the errors are too severe for export?"

**Test:** Look at error messages from step2
```
Question 2 (Q002):
  Invalid question type: "multiple_choice" (check spelling and underscores)
```

**Insight:** The error messages are INCREDIBLY specific. They tell us EXACTLY what to change (`multiple_choice` → `multiple_choice_single`). This isn't a "file is corrupt" error - this is a "file uses variant format" error.

**Question that emerged:** If step2 can parse the file well enough to give detailed errors, why can't step4 parse it at all?

### Phase 2: Code Archaeology (30 min)

**Investigation:** Trace the code paths for step2 vs step4

**Finding 1: Different Parsers**
```python
# step2 (validator.py)
from validate_mqg_format import validate_content

# step4 (parser.py)
from src.parser.markdown_parser import MarkdownQuizParser
```

**Insight:** They use DIFFERENT libraries from QTI-Generator-for-Inspera!

**Finding 2: Different Behaviors**
- `validate_content()` - Liberal parser, returns detailed issues
- `MarkdownQuizParser.parse()` - Strict parser, returns `{'questions': []}`

**Aha Moment #1:** "This isn't a bug - it's a design gap. The validator is MORE permissive than the export parser."

### Phase 3: Understanding step1 (45 min)

**Question:** "Can we use step1_transform to fix these errors?"

**Investigation:** Read `step1/transformer.py`

**Finding 1: Has Relevant Transforms**
```python
'normalize_type_names': ...,      # ✅ We need this!
'extract_correct_answers': ...,   # ✅ We need this!
'restructure_text_entry': ...,    # ✅ We need this!
```

**Initial thought:** "Great! step1 already has these transforms!"

**Finding 2: But Wrong Syntax**
```python
def _transform_normalize_type_names(self, content: str):
    # Only checks small alias list
    type_aliases = {
        'multiple_choice': 'multiple_choice_single',
        'mc': 'multiple_choice_single',
    }
```

**Finding 3: Works on Legacy Format**
```python
def _transform_extract_correct_answers(self, content: str):
    # Looks for ### Options section (Legacy)
    options_match = re.search(
        r'(###\s*Options.*?)(?=###|\Z)',
        content,
        re.DOTALL | re.IGNORECASE
    )
```

**Aha Moment #2:** "step1 transforms work on Legacy Syntax (### headers), not QFMD v6.5 (@field: syntax)!"

**Finding 4: Creates New Bugs**

From user's previous session:
```
Before step1: {{dropdown1}}
After step1:  {{dropdown_1}}         # Fixed!
              @field: dropdown1_options  # NOT fixed!
```

Result: Mismatched placeholders.

**Aha Moment #3:** "step1 is for Legacy → QFMD, not QFMD → Canonical QFMD. Using it here would be forcing a square peg into a round hole."

### Phase 4: Architectural Insight (20 min)

**Realization:** We have TWO separate transformation problems:

**Transformation A: Legacy → QFMD** (step1's job)
- Input: Semi-structured markdown (## headers, @key: metadata)
- Output: Basic QFMD (@field: syntax, ^metadata)
- Tools: step1_transform

**Transformation B: QFMD → Canonical QFMD** (missing step!)
- Input: Valid but variant QFMD (@field: with wrong types, missing fields)
- Output: Strict v6.5 canonical QFMD
- Tools: **DOES NOT EXIST**

**Aha Moment #4:** "We need a NEW step, not to extend step1. These are fundamentally different transformations."

### Phase 5: Source Code Deep Dive (60 min)

**Goal:** Understand exactly what v6.5 canonical format requires

**Approach:** Read the actual parser code
```bash
QuestionForge/packages/qti-core/src/parser/markdown_parser.py
```

**Finding 1: Strict Metadata Parsing**
```python
def _extract_metadata_fields(self, block):
    # Looks for: ^type VALUE (no colon!)
    type_match = re.match(r'\^type\s+(\w+)', line)
```

**Insight:** Parser expects `^type multiple_choice_single` (no colon), but accepts `^type: multiple_choice_single`. However, it does NOT normalize `multiple_choice` → `multiple_choice_single`.

**Finding 2: Type Recognition**
```python
SUPPORTED_TYPES = [
    'multiple_choice_single',  # ✅ Recognized
    'multiple_response',       # ✅ Recognized
    'text_entry',              # ✅ Recognized
    # ... but NOT:
    'multiple_choice',         # ❌ Unknown type → skip question
]
```

**Aha Moment #5:** "If the type isn't in the SUPPORTED_TYPES list, the parser SKIPS the entire question. That's why we get 0 questions - 18 questions have unrecognized types!"

**Finding 3: Field Parsing**
```python
def _parse_field_sections(self, block):
    # Looks for @field: name ... @end_field
    # Nested fields use @@field: ... @@end_field
```

**Insight:** The parser is actually quite flexible with field syntax, BUT:
- Must have `@end_field` markers
- Nested fields MUST use `@@field:` (not `@subfield:`)

**Finding 4: Text Entry Special Case**
```python
if question_type == 'text_entry':
    # Must have {{blank_N}} in question_text
    # Must have @field: blanks with @@field: blank_N
    if not self._has_blank_placeholders(question_text):
        return None  # Skip question
```

**Aha Moment #6:** "text_entry is ULTRA strict. Must have exact format or question is skipped."

---

## Key Learnings

### Learning 1: Symptoms vs Root Causes

**Symptom:** "Export fails with 0 questions"

**What we thought:** "Parser is broken"

**What we learned:** Parser works perfectly - it's just strict. The real problem is we're feeding it non-canonical input.

**Principle:** When debugging, distinguish between:
- **Symptoms** (what the user sees)
- **Proximate causes** (immediate code that fails)
- **Root causes** (architectural gaps)

In this case:
- Symptom: Export fails
- Proximate cause: Parser returns empty list
- Root cause: Missing canonicalization step

### Learning 2: The Validation Paradox

**Paradox:** "Our validator is TOO GOOD"

**What we mean:**
- step2 validator is liberal and helpful
- It parses variant formats and gives detailed errors
- Users think: "If validator can read it, why can't export?"

**What we learned:** There's a tension between:
- **Liberal validation** (helpful, educational)
- **Strict parsing** (reliable, predictable)

**Solution:** Add a transformation layer that bridges them:
```
Liberal Validator → Canonical Transform → Strict Parser
```

**Principle:** When you have mismatched strictness levels, don't try to make them the same - add a layer that transforms between them.

### Learning 3: Don't Force-Fit Solutions

**Temptation:** "step1 has 90% of the transforms we need - let's just extend it!"

**Why we resisted:**
- Conceptually wrong (Legacy→QFMD vs QFMD→Canonical are different problems)
- Would create maintenance nightmare (two code paths in one module)
- Would introduce bugs (transforms designed for different syntax)

**What we learned:** Sometimes the right answer is "create a new thing" even if it seems like duplication.

**Principle:** Respect separation of concerns. If two transformations solve fundamentally different problems, don't merge them just to avoid code duplication.

### Learning 4: Parser Alignment is a Pattern

**Realization:** This isn't a QuestionForge-specific problem!

**Pattern we discovered:**
```
Input Format → Liberal Validator → [GAP] → Strict Processor → Output
```

This appears in many systems:
- HTML: Browsers parse messy HTML, validators are strict
- JSON: Parsers accept trailing commas, spec is strict
- Markdown: Renderers are permissive, linters are strict

**Solution Pattern:**
```
Input → Validate → Normalize → Process → Output
         ↑         ↑           ↑
       Liberal   Transform   Strict
```

**Principle:** Whenever you have different strictness levels at different pipeline stages, you need a normalization step.

### Learning 5: Error Messages as Transformation Specs

**Insight:** step2's error messages are PERFECT transformation specifications!

Example:
```
Error: Invalid question type: "multiple_choice"
       (check spelling and underscores)

Transform: type_normalization
  Pattern: multiple_choice
  Replacement: multiple_choice_single
```

**What we learned:** Good error messages should be:
1. **Specific** (exact location, exact problem)
2. **Actionable** (what to change)
3. **Automatable** (can be parsed into transformations)

**Principle:** Design error messages to be machine-readable. They should serve double duty:
- Human-readable (help users understand)
- Machine-parseable (enable automated fixes)

### Learning 6: Code Archaeology Techniques

**What worked:**
1. **Follow the data flow** (validation report → export failure)
2. **Read actual source code** (not just documentation)
3. **Look for version history** (PARSER_UPDATE_SUMMARY.md gave context)
4. **Test hypotheses incrementally** (don't assume, verify)

**Example:** When we thought "maybe step1 can fix this", we:
- Read step1/transformer.py (found transforms)
- Read transforms in detail (found syntax mismatch)
- Tested hypothesis (transforms work on Legacy, not QFMD)
- Rejected approach (wrong tool for job)

**Principle:** Methodical investigation beats intuition. Read code, test assumptions, verify behavior.

### Learning 7: The Missing Step Pattern

**Pattern we discovered:**
```
step0 → [works]
step1 → [works]
step2 → [works]
step3 → [MISSING!]
step4 → [fails]
```

**Red flags that indicate a missing step:**
- Gap in numbering (step0, step1, step2, step4 - no step3!)
- Error messages that can't be acted on programmatically
- Manual work required between automated steps
- "If X works, why doesn't Y work?"

**Principle:** Pipeline gaps often show up as missing numbers. If you have step1, step2, step4 - ask "where's step3?"

### Learning 8: Transformation Order Matters

**Discovery:** step1 has transforms in specific order:
```python
transform_order = [
    'metadata_syntax',      # First: Fix metadata
    'placeholder_syntax',
    'upgrade_headers',
    'normalize_type_names', # Then: Normalize types
    'extract_correct_answers',
    'restructure_text_entry',
    'nested_field_syntax',  # Last: Fix structure
    'add_end_fields',
]
```

**Why order matters:**
- Can't extract correct_answers until options are in right format
- Can't add end_fields until nested_field_syntax is fixed
- Type normalization must happen before type-specific transforms

**Principle:** Transformations have dependencies. Order them carefully:
1. Format fixes (syntax, structure)
2. Type normalization (canonical names)
3. Type-specific transforms (use normalized types)
4. Cleanup (markers, formatting)

### Learning 9: Dry-Run is Essential

**Insight:** User said "skriv en rfc" not "fix my file"

**Why?** Because automated transformations are SCARY:
- Might misinterpret intent
- Might introduce new bugs
- User loses control

**Solution:** Always provide dry-run mode:
```python
step3_canonicalize(dry_run=True)  # Preview only
```

**Principle:** For destructive operations, always provide:
1. Dry-run (preview changes)
2. Backup (preserve original)
3. Undo (revert if needed)
4. Detailed log (what changed and why)

### Learning 10: Documentation Reveals Design Intent

**Discovery:** Found `PARSER_UPDATE_SUMMARY.md` in QTI-Generator

```markdown
Parser recently updated for flexibility (v6.5):
- Optional YAML frontmatter (can extract from markdown)
- Alternative inline_choice dropdown formats supported
- Flexible blank header levels (## or ###)
```

**Insight:** The parser WAS made flexible, but in PARSING, not VALIDATION. It can READ multiple formats but only EXPORTS one canonical format.

**What this tells us:**
- Design intent: "Liberal in what you accept, strict in what you produce"
- But implementation: Missing normalization layer

**Principle:** Read update logs and version history. They reveal design intent and evolution.

---

## Mistakes We Almost Made

### Almost-Mistake 1: Blaming the Parser

**Initial thought:** "The parser is broken - it should accept these formats!"

**Why wrong:** Parser is doing its job (strict validation for reliable export). The problem is we're not giving it canonical input.

**What we learned:** Don't blame tools for doing their job correctly. Question your assumptions instead.

### Almost-Mistake 2: Making step4 More Liberal

**Tempting fix:** "Just make MarkdownQuizParser accept `multiple_choice`!"

**Why wrong:**
- Hides format inconsistencies
- Makes QFMD spec unclear
- Loses benefits of canonical format

**What we learned:** Weakening constraints often creates more problems than it solves.

### Almost-Mistake 3: Extending step1

**Tempting fix:** "Add `--mode=canonicalize` to step1!"

**Why wrong:**
- Conceptually confusing (mixing two transformations)
- Would make step1 complex and fragile
- Doesn't respect separation of concerns

**What we learned:** Don't add features to existing tools just to avoid creating new ones.

### Almost-Mistake 4: Manual Fix Instructions

**Tempting fix:** "Just tell user to manually change all `multiple_choice` to `multiple_choice_single`"

**Why wrong:**
- Doesn't scale (40 questions, 42 errors)
- Error-prone (humans make mistakes)
- Doesn't solve the architectural problem

**What we learned:** If you're writing manual instructions for something that could be automated, you're solving the wrong problem.

---

## Debugging Principles That Emerged

### Principle 1: Trace the Happy Path

**Method:**
1. Start with working input
2. Trace it through the pipeline
3. Find where it breaks
4. Compare with non-working input

**Example:**
```
Working: ^type multiple_choice_single → Parser recognizes → Question exported
Broken:  ^type multiple_choice         → Parser skips → 0 questions
         ↑
         Divergence point!
```

### Principle 2: Read Code, Not Documentation

**Why:** Documentation describes intent, code describes reality.

**Example:** Documentation says "parser is flexible" but code shows it only recognizes specific type names.

### Principle 3: Test Hypotheses Incrementally

**Method:**
1. Form hypothesis ("step1 can fix this")
2. Find minimal test case
3. Test hypothesis
4. Accept or reject based on evidence

**Don't:** Jump to implementation without testing assumptions

### Principle 4: Follow the Data

**Method:**
1. Input file → step2 → validation report → [what happens?]
2. Input file → step4 → parser → `{'questions': []}` → [why empty?]
3. Compare data at each step

**Key insight:** The data tells the story. Follow it.

### Principle 5: Respect Architectural Layers

**Method:**
1. Identify what each layer is SUPPOSED to do
2. Don't force a layer to do another layer's job
3. Add missing layers rather than overloading existing ones

**Example:** step1 is for Legacy→QFMD. Don't make it also do QFMD→Canonical.

---

## Pattern Recognition: Similar Problems

### Pattern 1: The Validation-Processing Gap

**Where else this appears:**
- **HTML:** W3C validator vs browser rendering
- **SQL:** Linters vs database engines
- **TypeScript:** tsc --noEmit vs tsc

**Common solution:** Formatter/Normalizer layer (Prettier, SQL formatters, etc.)

### Pattern 2: The Strict-Liberal Mismatch

**Where else this appears:**
- **HTTP:** Browsers send messy headers, servers parse strictly
- **JSON:** APIs accept loose JSON, databases require strict schema
- **Markdown:** Editors allow any syntax, renderers expect specific formats

**Common solution:** Schema validation + normalization before processing

### Pattern 3: The Missing Transformation Step

**Where else this appears:**
- **Build pipelines:** Code → Lint → [missing: Format] → Build → Deploy
- **Data pipelines:** Extract → Validate → [missing: Transform] → Load
- **CI/CD:** Test → [missing: Staging] → Deploy

**Common solution:** Add explicit transformation/normalization stage

---

## Meta-Learning: How to Learn from Debugging

### 1. Document the Journey

**What we did:** Kept transcript of entire debugging session

**Why valuable:**
- Shows thought process, not just solution
- Captures dead ends and why they were rejected
- Reveals insights that emerged along the way

**Lesson:** The journey is as valuable as the destination.

### 2. Ask "Why?" Five Times

**Example:**
1. **Why does export fail?** → Parser returns 0 questions
2. **Why 0 questions?** → Parser doesn't recognize question types
3. **Why doesn't it recognize?** → Type is `multiple_choice` not `multiple_choice_single`
4. **Why is type wrong?** → User wrote variant format
5. **Why doesn't validation catch this?** → Validation is liberal, export is strict

**Result:** Found root cause (missing normalization layer)

### 3. Build Mental Models

**Model we built:**
```
QuestionForge Pipeline:
  Input → Validation → [GAP] → Export
          ↑             ↑       ↑
        Liberal      Missing   Strict
```

**Why useful:** Mental models help predict behavior and design solutions.

### 4. Extract Principles

**From specific bug:**
- "Parser returns 0 questions if type is wrong"

**To general principle:**
- "When strictness levels mismatch, add normalization layer"

**Why valuable:** Principles transfer to new problems.

### 5. Share Learnings

**What we're doing now:** Writing this RFC Complement

**Why important:**
- Future developers avoid same pitfalls
- Team builds shared understanding
- Knowledge compounds over time

---

## Recommendations for Future Work

### Short-term (This Week)

1. **Implement step3 MVP** based on RFC-010
   - Focus on Entry Check Modul 2 use case
   - Core transformations only
   - Extensive testing

2. **Extract reusable patterns** from step1/transformer.py
   - Transformation registry pattern
   - Batch processing pattern
   - Iterative refinement pattern

3. **Document v6.5 canonical format** (RFC-011)
   - Exact syntax specification
   - Required vs optional fields
   - Nesting rules

### Medium-term (This Month)

1. **Unify error reporting** between step2 and step3
   - Machine-readable error format
   - Consistent terminology
   - Actionable messages

2. **Add dry-run mode** to all destructive operations
   - step1_transform --dry-run
   - step3_canonicalize --dry-run
   - Preview changes before applying

3. **Create test corpus** of QFMD variants
   - Legacy syntax examples
   - v6.3, v6.4, v6.5 variants
   - Common errors and fixes

### Long-term (Next Quarter)

1. **Consider LLM-based fallback** for complex cases
   - When rule-based transforms fail
   - For ambiguous error types
   - With user approval required

2. **Build QFMD linter** separate from validator
   - Style guide enforcement
   - Best practices recommendations
   - Format consistency checks

3. **Create migration tools** for version upgrades
   - v6.5 → v7.0 when it arrives
   - Automated changelog generation
   - Backward compatibility testing

---

## Conclusion: What We Learned

### The Bug

- **Surface:** Export fails with 0 questions
- **Cause:** Parser strictness mismatch
- **Solution:** Add normalization step (step3)

### The Process

- **Method:** Methodical investigation, code archaeology
- **Key skill:** Following data through the pipeline
- **Critical insight:** Distinguish symptoms from root causes

### The Architecture

- **Pattern:** Validation-Processing Gap
- **Anti-pattern:** Forcing wrong tool for the job
- **Solution pattern:** Liberal validate → Normalize → Strict process

### The Principles

1. Respect architectural layers
2. Add missing steps rather than overload existing ones
3. Error messages should enable automation
4. Transformation order matters
5. Dry-run is essential for destructive operations

### The Impact

This wasn't just fixing a bug - it was:
- Discovering a missing architectural layer
- Learning how to debug pipeline problems
- Extracting reusable patterns
- Building team knowledge

**Most importantly:** We learned that the right solution often isn't to fix what's broken, but to add what's missing.

---

## Appendix: Session Artifacts

### Code Read

- `packages/qf-pipeline/src/qf_pipeline/wrappers/validator.py` (52 lines)
- `packages/qf-pipeline/src/qf_pipeline/wrappers/parser.py` (73 lines)
- `packages/qf-pipeline/src/qf_pipeline/step1/transformer.py` (600+ lines)
- `packages/qti-core/src/parser/markdown_parser.py` (referenced but not fully read)
- `packages/qti-core/PARSER_UPDATE_SUMMARY.md` (version history)

### Insights Captured

- 10 major "Aha Moments"
- 5 transformation rules identified
- 4 architectural patterns recognized
- 10 debugging principles extracted

### Decisions Made

- ✅ Create step3 (not extend step1)
- ✅ Keep parsers separate (not unify)
- ✅ Rule-based transforms (not LLM)
- ✅ Dry-run mode essential
- ✅ Iterative refinement (max 3 iterations)

### Time Investment

- Discovery: ~2 hours
- Analysis: ~2 hours
- RFC writing: ~2 hours
- **Total: ~6 hours**
- **Value: Permanent fix + team knowledge**

---

**Document Status:** Complete  
**Next Action:** Review with team, approve RFC-010, begin implementation

**Final Thought:** The best debugging sessions teach you not just how to fix the problem, but how to think about similar problems in the future. This was one of those sessions.

---

*"We don't just fix bugs. We learn from them."*
