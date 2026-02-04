# RFC-016: M5 Self-Learning Format Recognition

**Status:** Implemented
**Date:** 2026-01-28
**Updated:** 2026-01-29 (Option B: Data-Driven Field Aliases)
**Author:** Claude Code
**Related:** RFC-015 (Pipeline Stop Points), RFC-011 (Self-Learning Transformations)

---

## Problem

M5 flexible_parser has hardcoded patterns:
- `### Q1`
- `## Question 1`
- `## Fråga 1`

When teachers use a different format (e.g., M3 output with `**Title:**/**Stem:**`):
```
**Title:** Basic AI concepts
**Type:** essay
**Bloom:** understand
**Stem:** The material introduces...
```

Result: "0 questions found" → Dead end.

**This is the WRONG approach!**

---

## Philosophy: Teacher-Led, AI-Assisted

QuestionForge is built on:
- **Teacher leads** - AI assists
- **Dialogue** - not automation
- **Learning** - not hardcoding

M5 should NOT try to parse everything automatically.
M5 should ASK the teacher when it doesn't understand.

---

## Solution: Self-Learning Format Recognition

### Principle

```
┌─────────────────────────────────────────────────────┐
│  1. M5 sees new format                              │
│     → Asks teacher for help                         │
├─────────────────────────────────────────────────────┤
│  2. Teacher explains the mapping                    │
│     → "Title means title, Stem is the question text"│
├─────────────────────────────────────────────────────┤
│  3. M5 saves the pattern                            │
│     → format_patterns.json                          │
├─────────────────────────────────────────────────────┤
│  4. Next time same format                           │
│     → M5 recognises it automatically               │
└─────────────────────────────────────────────────────┘
```

### Similar to Step 3 fix_rules

Step 3 has `fix_rules.json` for transformations:
```json
{
  "STEP3_001": {
    "issue_type": "missing_identifier",
    "auto_fix": "Generate from question number",
    "confidence": 0.95
  }
}
```

M5 gets `format_patterns.json` for format recognition:
```json
{
  "patterns": [
    {
      "pattern_id": "M5_FMT_001",
      "name": "M3 Bold Headers",
      "learned_from": "teacher_session_2026-01-28",
      "confidence": 0.9,
      "mappings": {
        "**Title:**": { "field": "title", "type": "single_line" },
        "**Type:**": { "field": "type", "type": "single_line" },
        "**Bloom:**": { "field": "label", "type": "tag" },
        "**Difficulty:**": { "field": "label", "type": "tag" },
        "**Points:**": { "field": "points", "type": "number" },
        "**Tags:**": { "field": "labels", "type": "tags" },
        "**Learning Objective:**": { "field": "skip", "type": "ignore" },
        "**Stem:**": { "field": "question_text", "type": "multiline_until_next" },
        "**Answer:**": { "field": "answer", "type": "multiline_until_next" },
        "**Feedback:**": { "field": "feedback", "type": "multiline_until_next" }
      },
      "question_separator": "---",
      "times_used": 0,
      "teacher_approved": true
    }
  ]
}
```

---

## Workflow: First Time (unknown format)

### Step 1: M5 discovers unknown format

```
══════════════════════════════════════════════════════
M5 - NEEDS HELP
══════════════════════════════════════════════════════

I found a file but don't recognise the format.

File's first 30 lines:
┌────────────────────────────────────────────────────┐
│ **Title:** Basic AI concepts                       │
│ **Type:** essay                                    │
│ **Bloom:** understand                              │
│ **Difficulty:** easy                               │
│ **Points:** 3                                      │
│ **Tags:** #elements_of_AI_chapter1 #basic_concepts │
│ **Learning Objective:** ARTI1000X - Knowledge...   │
│ **Stem:**                                          │
│ The material introduces several important concepts │
│                                                    │
│ ---                                                │
│                                                    │
│ **Title:** The role of machine learning            │
│ ...                                                │
└────────────────────────────────────────────────────┘

I see patterns with **Header:** but don't know what they mean.

Can you help me understand the format?

══════════════════════════════════════════════════════
```

### Step 2: Teacher explains

Teacher responds (natural language):
```
Title is the question title
Type is question type (essay, multiple_choice_single, etc)
Bloom should become a tag
Difficulty should also become a tag
Points is points
Tags are tags (keep as they are)
Learning Objective - skip, don't include
Stem is where the question text begins
--- separates questions
```

### Step 3: M5 confirms understanding

```
══════════════════════════════════════════════════════
M5 - CONFIRMING MAPPING
══════════════════════════════════════════════════════

OK, I understand the format like this:

  **Title:**      → Question title (title)
  **Type:**       → Question type (type)
  **Bloom:**      → Add as tag (#understand)
  **Difficulty:** → Add as tag (#easy)
  **Points:**     → Points (points)
  **Tags:**       → Tags (labels) - keep as they are
  **Learning Objective:** → SKIP
  **Stem:**       → Question text (question_text)
  ---             → Question separator

Is this correct?
  [1] Yes, save this pattern
  [2] No, let me correct

══════════════════════════════════════════════════════
```

### Step 4: Save pattern

Teacher says "Yes" → M5 saves to `format_patterns.json`

```
══════════════════════════════════════════════════════
M5 - PATTERN SAVED
══════════════════════════════════════════════════════

✅ Saved pattern "M3 Bold Headers"
   File: logs/m5_format_patterns.json

Next time I see this format I will recognise it.

Now we can start processing the questions!

Found: 5 questions

Show question 1?
  [1] Yes, continue
  [2] Show all first

══════════════════════════════════════════════════════
```

---

## Workflow: Second Time (known format)

```
══════════════════════════════════════════════════════
M5 - FORMAT RECOGNISED
══════════════════════════════════════════════════════

I recognise this format!

Format: "M3 Bold Headers" (learned 2026-01-28)
Confidence: 90%
Used: 3 times previously

Found: 8 questions

  - essay: 5
  - multiple_choice_single: 3

Do you want to start processing the questions?
  [1] Yes, start with question 1
  [2] Show all questions first
  [3] This looks wrong, let me correct the mapping

══════════════════════════════════════════════════════
```

---

## Data Structure

### format_patterns.json

```json
{
  "version": "1.0",
  "patterns": [
    {
      "pattern_id": "M5_FMT_001",
      "name": "M3 Bold Headers",
      "description": "M3 output with **Header:** format",
      "learned_from": {
        "session_id": "abc123",
        "date": "2026-01-28T12:35:00Z",
        "teacher_confirmed": true
      },
      "detection": {
        "required_markers": ["**Title:**", "**Stem:**"],
        "optional_markers": ["**Type:**", "**Points:**"],
        "question_separator": "---"
      },
      "mappings": {
        "**Title:**": {
          "qfmd_field": "title",
          "extraction": "single_line"
        },
        "**Type:**": {
          "qfmd_field": "type",
          "extraction": "single_line"
        },
        "**Bloom:**": {
          "qfmd_field": "labels",
          "extraction": "single_line",
          "transform": "prepend_hash"
        },
        "**Difficulty:**": {
          "qfmd_field": "labels",
          "extraction": "single_line",
          "transform": "prepend_hash"
        },
        "**Points:**": {
          "qfmd_field": "points",
          "extraction": "number"
        },
        "**Tags:**": {
          "qfmd_field": "labels",
          "extraction": "single_line",
          "transform": "keep_as_is"
        },
        "**Learning Objective:**": {
          "qfmd_field": null,
          "extraction": "skip"
        },
        "**Stem:**": {
          "qfmd_field": "question_text",
          "extraction": "multiline_until_next_marker"
        },
        "**Answer:**": {
          "qfmd_field": "answer",
          "extraction": "multiline_until_next_marker"
        },
        "**Feedback:**": {
          "qfmd_field": "feedback",
          "extraction": "multiline_until_next_marker"
        }
      },
      "statistics": {
        "times_used": 5,
        "questions_processed": 23,
        "last_used": "2026-01-28T14:20:00Z",
        "teacher_corrections": 1
      }
    },
    {
      "pattern_id": "M5_FMT_002",
      "name": "QFMD v6.5 Native",
      "description": "Already in QFMD format",
      "detection": {
        "required_markers": ["^type", "^identifier", "@field:"]
      },
      "mappings": "passthrough",
      "statistics": {
        "times_used": 12
      }
    },
    {
      "pattern_id": "M5_FMT_003",
      "name": "Markdown Headers",
      "description": "### Q1 format",
      "detection": {
        "required_markers": ["### Q"],
        "question_separator": "---"
      },
      "mappings": {
        "### Q(\\d+)": {
          "qfmd_field": "question_number",
          "extraction": "regex_group_1"
        }
      }
    }
  ]
}
```

### Pattern Matching Priority

1. Check for exact QFMD v6.5 format (passthrough)
2. Check learned patterns by `required_markers`
3. If no match → Ask teacher for help

---

## Implementation

### Phase 1: Ask-for-Help Mode

```typescript
// m5_start checks format
async function m5Start(projectPath: string, sourceFile: string) {
  const content = readFile(sourceFile);

  // Try to detect format
  const knownPatterns = loadPatterns(projectPath);
  const detected = detectFormat(content, knownPatterns);

  if (detected.confidence > 0.8) {
    // Known format - proceed
    return {
      success: true,
      format: detected.pattern.name,
      questions: parseWithPattern(content, detected.pattern)
    };
  } else {
    // Unknown format - ask teacher
    return {
      success: true,
      needs_teacher_help: true,
      reason: "unknown_format",
      file_preview: getFirstNLines(content, 30),
      detected_markers: findPotentialMarkers(content),
      question: "I don't recognise this format. Can you help me understand what each header means?"
    };
  }
}
```

### Phase 2: Learn-from-Teacher

```typescript
// New tool: m5_teach_format
async function m5TeachFormat(
  projectPath: string,
  mappings: Record<string, FieldMapping>,
  questionSeparator: string,
  patternName: string
) {
  const pattern: FormatPattern = {
    pattern_id: generatePatternId(),
    name: patternName,
    learned_from: {
      session_id: getCurrentSessionId(),
      date: new Date().toISOString(),
      teacher_confirmed: true
    },
    detection: {
      required_markers: Object.keys(mappings).filter(m => mappings[m].required),
      question_separator: questionSeparator
    },
    mappings: mappings,
    statistics: {
      times_used: 0,
      questions_processed: 0,
      teacher_corrections: 0
    }
  };

  savePattern(projectPath, pattern);

  return {
    success: true,
    message: `Pattern "${patternName}" saved!`,
    pattern_id: pattern.pattern_id
  };
}
```

### Phase 3: Use Learned Pattern

```typescript
// m5_start now uses learned patterns
function parseWithPattern(content: string, pattern: FormatPattern): Question[] {
  const questions: Question[] = [];

  // Split by question separator
  const blocks = content.split(pattern.detection.question_separator);

  for (const block of blocks) {
    const question: Question = {};

    for (const [marker, mapping] of Object.entries(pattern.mappings)) {
      const value = extractValue(block, marker, mapping);

      if (value && mapping.qfmd_field) {
        if (mapping.transform === 'prepend_hash') {
          question[mapping.qfmd_field] = `#${value}`;
        } else if (mapping.qfmd_field === 'labels') {
          // Append to existing labels
          question.labels = (question.labels || '') + ' ' + value;
        } else {
          question[mapping.qfmd_field] = value;
        }
      }
    }

    if (Object.keys(question).length > 0) {
      questions.push(question);
    }
  }

  // Update statistics
  pattern.statistics.times_used++;
  pattern.statistics.questions_processed += questions.length;
  pattern.statistics.last_used = new Date().toISOString();
  savePattern(projectPath, pattern);

  return questions;
}
```

---

## New MCP Tools

| Tool | Purpose |
|------|---------|
| `m5_start` | (Updated) Now asks for help if format unknown |
| `m5_teach_format` | Teacher defines format mapping |
| `m5_list_formats` | Show all learned formats |
| `m5_edit_format` | Modify existing format pattern |
| `m5_delete_format` | Remove format pattern |

---

## Confidence Building

Like Step 3's fix_rules, confidence increases with use:

```
Initial confidence: 0.8 (teacher just taught)
After 5 uses without corrections: 0.9
After 10 uses without corrections: 0.95
If teacher corrects: confidence -= 0.1
```

---

## Benefits

1. **No hardcoded parsers** - System learns from teacher
2. **Handles any format** - Just needs one teaching session
3. **Gets smarter over time** - Confidence builds with use
4. **Teacher stays in control** - Can correct/edit patterns
5. **Transparent** - All learned patterns visible in JSON
6. **Reusable** - Patterns persist across sessions

---

## Migration Path

### Current flexible_parser.ts patterns → format_patterns.json

Move hardcoded patterns to JSON:
```json
{
  "pattern_id": "M5_FMT_BUILTIN_001",
  "name": "Markdown Headers (###)",
  "builtin": true,
  "detection": {
    "required_markers": ["### Q"]
  }
}
```

This way:
- Existing patterns still work
- New patterns learned from teacher
- All patterns in one system

---

## Open Questions

1. Should patterns be per-project or global?
2. How to handle conflicting patterns?
3. Export/import patterns between projects?

---

## Related RFCs

- RFC-011: Self-Learning Transformations (Step 3 fix_rules)
- RFC-015: Pipeline Stop Points (mandatory teacher verification)
- RFC-013: QuestionForge Pipeline Architecture v2

---

---

## Appendix A: Option B - Data-Driven Field Aliases (2026-01-29)

### Problem

Pattern mappings use field names like `"stem"`, but internal code expects `"question_text"`.
Originally solved with hardcoded mapping - not flexible.

### Solution: field_aliases in patterns file

```json
{
  "version": "1.0",
  "field_aliases": {
    "stem": "question_text",
    "frågans_text": "question_text",
    "svar": "answer",
    "pregunta": "question_text"
  },
  "patterns": [...]
}
```

### Default Aliases (built-in)

```typescript
const DEFAULT_FIELD_ALIASES = {
  // Stem variants → question_text
  "stem": "question_text",
  "question": "question_text",
  "fråga": "question_text",
  "frågetext": "question_text",
  // Answer variants
  "svar": "answer",
  // Tags/Labels
  "tags": "labels",
  "etiketter": "labels",
  // Swedish variants
  "poäng": "points",
  "svårighetsgrad": "difficulty",
  "lärandemål": "learning_objective",
  "titel": "title",
  "typ": "type",
  // ...
};
```

### New MCP Tools

```typescript
// Add alias
m5_add_field_alias({
  project_path: "/path/to/project",
  alias: "frågans_text",
  maps_to: "question_text"
})

// Remove alias
m5_remove_field_alias({
  project_path: "/path/to/project",
  alias: "frågans_text"
})

// List all aliases
m5_list_field_aliases({
  project_path: "/path/to/project"
})
// Returns: { defaults: {...}, custom: {...}, merged: {...} }
```

### Implementation

- `format_learner.ts`: `getMergedAliases()`, `addFieldAlias()`, `removeFieldAlias()`, `listFieldAliases()`
- `m5_interactive_tools.ts`: MCP tool wrappers
- `parseWithPattern()` accepts optional `customAliases` parameter

---

## Document Metadata

**Created:** 2026-01-28
**Updated:** 2026-01-29
**Status:** Implemented
**Priority:** HIGH - Core M5 functionality
