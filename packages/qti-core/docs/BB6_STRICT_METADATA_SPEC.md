# BB6 Strict Metadata Specification

**Version:** 3.0
**Last Updated:** 2025-11-10
**Status:** MANDATORY

---

## REQUIRED Metadata Format

Every question MUST use this exact format:

```markdown
**Type**: question_type
**Identifier**: UNIQUE_ID
**Points**: number
**Tags**: CourseCode, LearningContentWords, BloomLevel, Difficulty
**Language**: language_code
```

---

## Tags Field Specification

### Format
**Comma-separated list** containing (in order):

1. **Course Code** - Course identifier (e.g., EXAMPLE_COURSE, TRA265)
2. **Learning Content Words** - Descriptive keywords for the learning content (e.g., Celltyper, Prokaryot, Eukaryot, Mitokondrier)
3. **Bloom's Taxonomy Level** - ONE of: Remember, Understand, Apply, Analyze, Evaluate, Create
4. **Difficulty Level** - ONE of: Easy, Medium, Hard
5. **(Optional)** Additional keywords, metadata tags

### Valid Example
```markdown
**Tags**: EXAMPLE_COURSE, Celltyper, Prokaryot, Eukaryot, Cellkärna, Understand, Easy
```

### Bloom's Taxonomy Levels (Required)
Choose exactly ONE:
- **Remember** - Recall facts and basic concepts
- **Understand** - Explain ideas or concepts
- **Apply** - Use information in new situations
- **Analyze** - Draw connections among ideas
- **Evaluate** - Justify a decision or course of action
- **Create** - Produce new or original work

### Difficulty Levels (Required)
Choose exactly ONE:
- **Easy** - Basic recall or simple application
- **Medium** - Requires understanding and some analysis
- **Hard** - Complex analysis or synthesis required

---

## INCORRECT Formats

### ❌ DO NOT USE Separate Fields

These formats will cause **VALIDATION ERROR**:

```markdown
❌ **Learning Objectives**: LO1, LO2
❌ **Bloom's Level**: Understand
❌ **Difficulty**: Easy
```

**Why?** Separate fields are NOT converted to Inspera labels. Only the **Tags** field creates searchable labels in Inspera.

### ❌ DO NOT USE Space-Separated Tags

```markdown
❌ **Tags**: EXAMPLE_COURSE Celltyper Prokaryot Understand Easy
```

**Use comma-separated instead.**

---

## Complete Question Example

```markdown
# Question 1: Prokaryot vs Eukaryot grundskillnad

**Type**: multiple_choice_single
**Identifier**: MC_Q001
**Points**: 1
**Tags**: EXAMPLE_COURSE, Celltyper, Prokaryot, Eukaryot, Cellkärna, Understand, Easy
**Language**: sv

## Question Text
Vad är den viktigaste skillnaden mellan prokaryota och eukaryota celler?

## Options
A. Eukaryota celler har membranomslutna organeller
B. Eukaryota celler har cellkärna där DNA förvaras ✓
C. Eukaryota celler har linjärt DNA
D. Eukaryota celler har större ribosomer

## Correct Answer
B

## Feedback

### General Feedback
Cellkärnan är den fundamentala skillnaden mellan dessa två stora celltyper.

---
```

---

## Validation Rules

The validator will **ERROR** if:

1. ❌ **Tags** field is missing
2. ❌ **Tags** field is empty
3. ❌ **Tags** field does not contain a Bloom's level keyword (Remember, Understand, Apply, Analyze, Evaluate, Create)
4. ❌ **Tags** field does not contain a difficulty keyword (Easy, Medium, Hard)
5. ❌ Question uses separate **Learning Objectives**: field
6. ❌ Question uses separate **Bloom's Level**: field
7. ❌ Question uses separate **Difficulty**: field

The validator will **PASS** if:

1. ✅ **Tags** field is present
2. ✅ **Tags** field is comma-separated
3. ✅ **Tags** contains at least one Bloom's level
4. ✅ **Tags** contains at least one difficulty level
5. ✅ No separate Learning Objectives, Bloom's Level, or Difficulty fields

---

## Why This Format?

### Inspera Label Generation
The QTI Generator creates Inspera searchable labels ONLY from the **Tags** field. Each comma-separated item becomes a searchable label in Inspera's question bank.

**Example:** This Tags field:
```markdown
**Tags**: EXAMPLE_COURSE, Celltyper, Prokaryot, Understand, Easy
```

Creates these Inspera labels:
- EXAMPLE_COURSE
- Celltyper
- Prokaryot
- Understand
- Easy

### Single Source of Truth
Having all metadata in ONE field eliminates confusion and ensures Inspera labels match the question's learning objectives, cognitive level, and difficulty.

---

## Migration from Old Format

If you have questions using the OLD format with separate fields:

### Old Format (INCORRECT)
```markdown
**Type**: multiple_choice_single
**Identifier**: Q001
**Points**: 1
**Learning Objectives**: LO1, LO2, Prokaryot, Eukaryot
**Bloom's Level**: Understand
**Difficulty**: Easy
**Language**: sv
```

### New Format (CORRECT)
```markdown
**Type**: multiple_choice_single
**Identifier**: Q001
**Points**: 1
**Tags**: EXAMPLE_COURSE, LO1, LO2, Prokaryot, Eukaryot, Understand, Easy
**Language**: sv
```

**Action Required:** Combine Learning Objectives, Bloom's Level, and Difficulty into the Tags field, comma-separated.

---

## Summary

✅ **USE:** `**Tags**: CourseCode, ContentWords, BloomLevel, Difficulty`
❌ **DO NOT USE:** Separate `**Learning Objectives**:`, `**Bloom's Level**:`, or `**Difficulty**:` fields

This is the ONLY accepted format for BB6 v3.0 compliance.
