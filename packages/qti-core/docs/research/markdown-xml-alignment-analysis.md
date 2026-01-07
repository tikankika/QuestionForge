# Markdown-XML Alignment Analysis

**Purpose**: Identify misalignments between markdown specifications and actual XML templates to ensure perfect mapping during code generation.

**Date**: 2025-10-30
**Status**: Initial Analysis
**Templates Analyzed**: 4 Priority 1 types

---

## Executive Summary

### Critical Issues Found: 10

1. **Question type code mismatches** - Type names differ between markdown and XML
2. **Missing question type** - Text area not in markdown spec
3. **Missing configuration fields** - XML templates need fields not in markdown
4. **Incomplete feedback coverage** - Partially correct feedback inconsistent
5. **Scoring field mismatches** - Multiple response scoring needs precise mapping

### Coverage Status

| XML Template | Markdown Spec Type | Status | Issues |
|--------------|-------------------|--------|--------|
| extended_text.xml | `essay` | ⚠️ Misaligned | Type name, missing config fields |
| multiple_choice_single.xml | `multiple_choice_single` | ✅ Aligned | Minor: partially_correct feedback |
| text_area.xml | (missing) | ❌ Missing | No markdown spec |
| multiple_response.xml | `multiple_choice_multiple` | ⚠️ Misaligned | Type name, scoring fields |

---

## Issue 1: Question Type Code Mismatches

### Problem

Markdown type codes must match XML template identifiers exactly, but currently don't.

### Discrepancies

| Markdown Spec Type | XML Template Name | inspera:objectType | Correct Code |
|-------------------|-------------------|-------------------|--------------|
| `essay` | extended_text.xml | content_question_qti2_extendedtext | Should be `extended_text` |
| `multiple_choice_multiple` | multiple_response.xml | content_question_qti2_multiple_response | Should be `multiple_response` |
| `multiple_choice_single` | multiple_choice_single.xml | content_question_qti2_multiple_choice | ✅ Correct |

### Impact

- **Critical**: Parser won't be able to map markdown types to XML templates
- Code generator will fail or produce incorrect XML

### Recommendation

Update markdown specification to use these exact type codes:
- `extended_text` (not `essay`)
- `multiple_response` (not `multiple_choice_multiple`)
- `multiple_choice_single` (keep as-is)
- `text_area` (add new type)

---

## Issue 2: Missing Text Area Type

### Problem

XML template `text_area.xml` exists but has no corresponding markdown specification.

### Difference from Extended Text

| Feature | extended_text.xml | text_area.xml |
|---------|------------------|---------------|
| **Rich formatting** | Yes (bold, italic, lists) | No (plain text only) |
| **Editor type** | Rich text editor | Plain textarea |
| **Use case** | Long essays, analysis | Short answers, definitions |
| **inspera:variant** | (not set) | `textarea` |
| **usePlainText** | `false` | `true` |

### XML Placeholders for Text Area

```
{{IDENTIFIER}}
{{TITLE}}
{{LANGUAGE}}
{{MAX_SCORE}}
{{QUESTION_TEXT}}
{{QUESTION_IMAGES}}
{{INITIAL_LINES}}
{{FIELD_WIDTH}}
{{SHOW_WORD_COUNT}}
{{EDITOR_PROMPT}}
{{FEEDBACK_UNANSWERED}}
{{FEEDBACK_ANSWERED}}
```

### Recommendation

Add new section to markdown specification for `text_area` type.

---

## Issue 3: Extended Text Configuration Fields Missing

### Problem

`extended_text.xml` requires configuration fields not present in markdown spec.

### XML Placeholders

```
{{INITIAL_LINES}} - Number of lines in editor (e.g., 10, 20)
{{FIELD_WIDTH}} - Width of editor (e.g., "100%")
{{SHOW_WORD_COUNT}} - Display word counter (true/false)
{{MAX_WORDS}} - Word limit (number or empty)
{{EDITOR_PROMPT}} - Placeholder text in editor
```

### Current Markdown Spec

```markdown
## Expected Response Length

**Minimum words**: 300
**Maximum words**: 600
```

### Gap Analysis

| XML Placeholder | Markdown Field | Status |
|----------------|----------------|--------|
| {{MAX_WORDS}} | Maximum words | ✅ Exists |
| {{INITIAL_LINES}} | (missing) | ❌ Need to add |
| {{FIELD_WIDTH}} | (missing) | ❌ Need to add |
| {{SHOW_WORD_COUNT}} | (missing) | ❌ Need to add |
| {{EDITOR_PROMPT}} | (missing) | ❌ Need to add |

### Recommendation

Add new section to essay/extended_text markdown specification:

```markdown
## Editor Configuration

**Initial lines**: 15
**Field width**: 100%
**Show word count**: true
**Editor prompt**: "Enter your response here..."
```

---

## Issue 4: Multiple Response Scoring Field Mapping

### Problem

Markdown spec has generic "Scoring" section that doesn't map precisely to XML placeholders.

### XML Template Placeholders

```
{{POINTS_EACH_CORRECT}} - Points per correct selection
{{POINTS_EACH_WRONG}} - Points per incorrect selection (often negative)
{{POINTS_ALL_CORRECT}} - Bonus for all correct (maximum score)
{{POINTS_MINIMUM}} - Score floor (typically 0)
{{CORRECT_CHOICES}} - List of correct answer IDs
{{MAPPING_ENTRIES}} - mapEntry elements for each correct choice
{{PROMPT_TEXT}} - Instruction text (e.g., "Select all that apply")
```

### Current Markdown Spec

```markdown
## Scoring

**Type**: partial_credit
**Correct choices**: 1 point each
**Incorrect choices**: -0.5 points each
**Minimum score**: 0
```

### Gap Analysis

| XML Placeholder | Markdown Field | Mapping |
|----------------|----------------|---------|
| {{POINTS_EACH_CORRECT}} | Correct choices | ✅ Maps to "1 point each" |
| {{POINTS_EACH_WRONG}} | Incorrect choices | ✅ Maps to "-0.5 points each" |
| {{POINTS_MINIMUM}} | Minimum score | ✅ Maps to "0" |
| {{POINTS_ALL_CORRECT}} | (missing) | ❌ Need to add "Maximum score" |
| {{PROMPT_TEXT}} | (missing) | ❌ Need to add |

### Recommendation

Update scoring section:

```markdown
## Scoring

**Points per correct choice**: 1
**Points per incorrect choice**: -0.5
**Maximum score**: 3
**Minimum score**: 0

## Prompt

Select all that apply.
```

---

## Issue 5: Partially Correct Feedback

### Problem

XML templates include `{{FEEDBACK_PARTIALLY_CORRECT}}` but markdown spec is inconsistent.

### XML Templates with Partially Correct Feedback

1. **multiple_response.xml** - Has partially_correct feedback modal
2. **multiple_choice_single.xml** - Has partially_correct feedback modal (though rarely used)

### Current Markdown Coverage

| Question Type | Markdown Spec Has Partially Correct | XML Template Needs It |
|---------------|-----------------------------------|---------------------|
| multiple_choice_single | ❌ No | ✅ Yes (line 198-200) |
| multiple_response | ✅ Yes (line 235) | ✅ Yes |

### Recommendation

Add partially correct feedback section to ALL question types that have it in XML:

```markdown
### Partially Correct Feedback (optional)
[Feedback shown when answer is partially correct]
```

---

## Issue 6: Question Images Separation

### Problem

XML templates have dedicated `{{QUESTION_IMAGES}}` placeholder in a separate div, but markdown spec embeds images in question text.

### XML Structure

```xml
<div class="question-main-illustration">
    {{QUESTION_IMAGES}}
</div>

{{QUESTION_TEXT}}
```

### Current Markdown Approach

Images are embedded directly in question text:

```markdown
## Question Text

Examine the graph below:

![Scatterplot](images/scatter.png)

What type of correlation is displayed?
```

### Consideration

**Should we separate images from text?**

**Option A**: Keep images in text, parser extracts them
- Pros: Simpler markdown syntax, natural flow
- Cons: Parser must extract and reformat images

**Option B**: Add dedicated Images section
- Pros: Cleaner mapping to XML, easier parsing
- Cons: More verbose markdown

### Recommendation

**Keep current approach** (Option A) but document parser behavior:
- Parser should extract images from question text
- Place them in `<div class="question-main-illustration">` if they appear before first paragraph
- Otherwise embed in question text

---

## Issue 7: Feedback Unanswered vs Answered

### Problem

Manual grading questions (extended_text, text_area) have different feedback structure.

### XML Feedback for Manual Questions

```xml
<modalFeedback identifier="feedback_unanswered">{{FEEDBACK_UNANSWERED}}</modalFeedback>
<modalFeedback identifier="feedback_answered">{{FEEDBACK_ANSWERED}}</modalFeedback>
```

### XML Feedback for Auto-Graded Questions

```xml
<modalFeedback identifier="feedback_unanswered">{{FEEDBACK_UNANSWERED}}</modalFeedback>
<modalFeedback identifier="feedback_correct">{{FEEDBACK_CORRECT}}</modalFeedback>
<modalFeedback identifier="feedback_wrong">{{FEEDBACK_INCORRECT}}</modalFeedback>
<modalFeedback identifier="feedback_partially_correct">{{FEEDBACK_PARTIALLY_CORRECT}}</modalFeedback>
```

### Current Markdown Spec

All question types use same feedback structure:
- General Feedback
- Correct Response Feedback
- Incorrect Response Feedback
- Option-Specific Feedback

### Gap for Manual Grading

Manual grading questions (essay/extended_text, text_area) don't have "correct" or "incorrect" - just "answered" or "unanswered".

### Recommendation

Add alternative feedback structure for manual grading types:

```markdown
## Feedback

### General Feedback
[Context about what question assesses]

### Answered Feedback
[Acknowledgment shown when student submits response]

### Unanswered Feedback
[Reminder shown when question is skipped]
```

---

## Issue 8: Shuffle Configuration

### Problem

`shuffle` attribute in XML can be at question level or global level.

### XML Templates

All auto-graded questions have:

```xml
<choiceInteraction shuffle="{{SHUFFLE}}">
```

### Current Markdown Spec

Global configuration in YAML:

```yaml
assessment_configuration:
  shuffle_choices: true
```

### Question

Should shuffle be:
- **Global only** (all questions use same setting)
- **Per-question** (each question specifies shuffle)
- **Both** (global default, per-question override)

### Recommendation

Support both with per-question override:

```markdown
**Type**: multiple_choice_single
**Identifier**: Q001
**Points**: 1
**Shuffle options**: false  # Optional: overrides global setting
```

---

## Issue 9: Missing Inspera Attributes

### Problem

XML templates use Inspera-specific attributes not captured in markdown.

### XML Attributes in `<itemBody>`

```xml
<itemBody inspera:defaultLanguage="{{LANGUAGE}}" inspera:supportedLanguages="{{LANGUAGE}}">
```

### Current Markdown Coverage

- ✅ Language is in YAML frontmatter
- ❌ Supported languages (multi-language support) not in spec

### Recommendation

Add to YAML frontmatter:

```yaml
test_metadata:
  language: "en"  # Default language
  supported_languages: ["en", "sv"]  # Optional: for multi-language tests
```

---

## Issue 10: Response Processing Logic Placeholders

### Problem

`multiple_response.xml` has placeholders for response processing logic that are dynamically generated.

### XML Placeholders

```
{{CORRECT_MATCH_LOGIC}} - AND conditions checking all correct choices
{{PARTIAL_MATCH_LOGIC}} - OR conditions checking any correct choice
```

### Analysis

These are **not** user-configurable fields - they're **generated** by the Python code based on the correct answers.

### Example Generation

If correct answers are A, C, E:

```xml
<!-- CORRECT_MATCH_LOGIC -->
<and>
    <member><baseValue>choice_A</baseValue><variable identifier="RESPONSE"/></member>
    <member><baseValue>choice_C</baseValue><variable identifier="RESPONSE"/></member>
    <member><baseValue>choice_E</baseValue><variable identifier="RESPONSE"/></member>
    <not>
        <member><baseValue>choice_B</baseValue><variable identifier="RESPONSE"/></member>
    </not>
    <not>
        <member><baseValue>choice_D</baseValue><variable identifier="RESPONSE"/></member>
    </not>
</and>
```

### Recommendation

**No markdown changes needed** - document in generator implementation notes that these placeholders are programmatically generated.

---

## Complete Field Mapping Tables

### Extended Text / Essay

| XML Placeholder | Markdown Field | Location | Status |
|----------------|----------------|----------|--------|
| {{IDENTIFIER}} | Identifier | Question metadata | ✅ |
| {{TITLE}} | Question title | Header | ✅ |
| {{LANGUAGE}} | language | YAML frontmatter | ✅ |
| {{MAX_SCORE}} | Points | Question metadata | ✅ |
| {{QUESTION_TEXT}} | Question Text section | Question body | ✅ |
| {{QUESTION_IMAGES}} | Images in text | (extracted) | ⚠️ |
| {{INITIAL_LINES}} | (missing) | - | ❌ ADD |
| {{FIELD_WIDTH}} | (missing) | - | ❌ ADD |
| {{SHOW_WORD_COUNT}} | (missing) | - | ❌ ADD |
| {{MAX_WORDS}} | Maximum words | Expected Response Length | ✅ |
| {{EDITOR_PROMPT}} | (missing) | - | ❌ ADD |
| {{FEEDBACK_UNANSWERED}} | (missing) | - | ❌ ADD |
| {{FEEDBACK_ANSWERED}} | (missing) | - | ❌ ADD |

### Multiple Choice Single

| XML Placeholder | Markdown Field | Location | Status |
|----------------|----------------|----------|--------|
| {{IDENTIFIER}} | Identifier | Question metadata | ✅ |
| {{TITLE}} | Question title | Header | ✅ |
| {{LANGUAGE}} | language | YAML | ✅ |
| {{MAX_SCORE}} | Points | Question metadata | ✅ |
| {{CORRECT_CHOICE_ID}} | Answer | Answer section | ✅ |
| {{SHUFFLE}} | shuffle_choices | YAML / per-question | ⚠️ |
| {{QUESTION_TEXT}} | Question Text | Question body | ✅ |
| {{CHOICES}} | Options | Options section | ✅ |
| {{FEEDBACK_CORRECT}} | Correct Response Feedback | Feedback section | ✅ |
| {{FEEDBACK_INCORRECT}} | Incorrect Response Feedback | Feedback section | ✅ |
| {{FEEDBACK_PARTIALLY_CORRECT}} | (missing) | - | ❌ ADD |
| {{FEEDBACK_UNANSWERED}} | (missing) | - | ❌ ADD |

### Multiple Response

| XML Placeholder | Markdown Field | Location | Status |
|----------------|----------------|----------|--------|
| {{IDENTIFIER}} | Identifier | Question metadata | ✅ |
| {{TITLE}} | Question title | Header | ✅ |
| {{LANGUAGE}} | language | YAML | ✅ |
| {{POINTS_EACH_CORRECT}} | Points per correct | Scoring section | ✅ |
| {{POINTS_EACH_WRONG}} | Points per incorrect | Scoring section | ✅ |
| {{POINTS_ALL_CORRECT}} | (missing "Maximum score") | - | ❌ ADD |
| {{POINTS_MINIMUM}} | Minimum score | Scoring section | ✅ |
| {{CORRECT_CHOICES}} | Answer | Answer section | ✅ |
| {{MAPPING_ENTRIES}} | (generated from answer) | - | ✅ |
| {{SHUFFLE}} | shuffle_choices | YAML | ⚠️ |
| {{QUESTION_TEXT}} | Question Text | Question body | ✅ |
| {{QUESTION_IMAGES}} | (in text) | - | ⚠️ |
| {{CHOICES}} | Options | Options section | ✅ |
| {{PROMPT_TEXT}} | (missing) | - | ❌ ADD |
| {{FEEDBACK_CORRECT}} | Correct Response Feedback | Feedback | ✅ |
| {{FEEDBACK_INCORRECT}} | Incorrect Response Feedback | Feedback | ✅ |
| {{FEEDBACK_PARTIALLY_CORRECT}} | Partially Correct Feedback | Feedback | ✅ |
| {{FEEDBACK_UNANSWERED}} | (missing) | - | ❌ ADD |
| {{CORRECT_MATCH_LOGIC}} | (generated) | - | ✅ |
| {{PARTIAL_MATCH_LOGIC}} | (generated) | - | ✅ |

### Text Area

| XML Placeholder | Markdown Field | Location | Status |
|----------------|----------------|----------|--------|
| {{IDENTIFIER}} | (no spec yet) | - | ❌ ADD TYPE |
| {{TITLE}} | (no spec yet) | - | ❌ ADD TYPE |
| {{LANGUAGE}} | language | YAML | ✅ |
| {{MAX_SCORE}} | (no spec yet) | - | ❌ ADD TYPE |
| {{QUESTION_TEXT}} | (no spec yet) | - | ❌ ADD TYPE |
| {{QUESTION_IMAGES}} | (no spec yet) | - | ❌ ADD TYPE |
| {{INITIAL_LINES}} | (no spec yet) | - | ❌ ADD TYPE |
| {{FIELD_WIDTH}} | (no spec yet) | - | ❌ ADD TYPE |
| {{SHOW_WORD_COUNT}} | (no spec yet) | - | ❌ ADD TYPE |
| {{EDITOR_PROMPT}} | (no spec yet) | - | ❌ ADD TYPE |
| {{FEEDBACK_UNANSWERED}} | (no spec yet) | - | ❌ ADD TYPE |
| {{FEEDBACK_ANSWERED}} | (no spec yet) | - | ❌ ADD TYPE |

---

## Recommended Actions

### Priority 1: Critical Fixes (Required for Generator)

1. ✅ **Update question type codes** in markdown_specification.md:
   - Change `essay` → `extended_text`
   - Change `multiple_choice_multiple` → `multiple_response`

2. ✅ **Add text_area question type** specification

3. ✅ **Add missing configuration fields** for extended_text:
   - Initial lines
   - Field width
   - Show word count
   - Editor prompt

4. ✅ **Add feedback_answered and feedback_unanswered** for manual grading types

5. ✅ **Add PROMPT_TEXT field** for multiple_response

6. ✅ **Add maximum score** to multiple_response scoring

### Priority 2: Enhancements (Improve Usability)

7. ⚠️ **Add per-question shuffle override** (optional feature)

8. ⚠️ **Add partially_correct feedback** to all applicable types

9. ⚠️ **Add supported_languages** to YAML frontmatter

### Priority 3: Documentation (Clarify Behavior)

10. 📄 **Document image extraction** logic in spec

11. 📄 **Document auto-generated placeholders** (CORRECT_MATCH_LOGIC, etc.)

12. 📄 **Update question_generation_template.md** with new types and fields

---

## Impact Assessment

### Code Generation Impact

**High Impact Issues** (will cause generation failures):
- Issue 1: Type code mismatches → Parser can't find templates
- Issue 2: Missing text_area type → Can't generate 9.3% of questions
- Issue 4: Scoring field gaps → Incorrect score calculations

**Medium Impact Issues** (will cause incomplete/incorrect output):
- Issue 3: Missing config fields → Questions missing UI settings
- Issue 5: Feedback gaps → Missing feedback messages
- Issue 7: Manual feedback structure → Wrong feedback shown

**Low Impact Issues** (cosmetic or optional):
- Issue 6: Image separation → Affects HTML structure, not function
- Issue 8: Shuffle configuration → Can use global default

### User Experience Impact

**Breaking Changes** (require markdown updates):
- Type code changes: Users must update `essay` → `extended_text`
- New required fields: Users must add configuration sections

**Backward Compatibility**:
- Can provide defaults for missing optional fields
- Can map old type names to new ones (with deprecation warning)

---

## Next Steps

1. **Update markdown_specification.md** with all Priority 1 fixes
2. **Update question_generation_template.md** to match
3. **Update metadata_reference.md** with new fields
4. **Create migration guide** for any existing markdown files
5. **Implement parser** with field mapping documented here

---

## Document Metadata

**Created**: 2025-10-30
**Author**: QTI Generator Analysis
**Version**: 1.0
**Status**: Complete Analysis
**Next Review**: After markdown spec updates
