# RFC-016: M5 Self-Learning Format Recognition

**Status:** Implemented
**Date:** 2026-01-28
**Updated:** 2026-01-29 (Option B: Data-Driven Field Aliases)
**Author:** Claude Code
**Related:** RFC-015 (Pipeline Stop Points), RFC-011 (Self-Learning Transformations)

---

## Problem

M5 flexible_parser har hårdkodade mönster:
- `### Q1`
- `## Question 1`
- `## Fråga 1`

När lärare använder annat format (t.ex. M3-output med `**Title:**/**Stem:**`):
```
**Title:** Grundbegrepp inom AI
**Type:** essay
**Bloom:** understand
**Stem:** I materialet introduceras...
```

Resultat: "0 frågor hittades" → Dead end.

**Detta är FEL approach!**

---

## Filosofi: Teacher-Led, AI-Assisted

QuestionForge bygger på:
- **Läraren leder** - AI assisterar
- **Dialog** - inte automatik
- **Lärande** - inte hårdkodning

M5 ska INTE försöka parsa allt automatiskt.
M5 ska FRÅGA läraren när den inte förstår.

---

## Lösning: Self-Learning Format Recognition

### Princip

```
┌─────────────────────────────────────────────────────┐
│  1. M5 ser nytt format                              │
│     → Frågar läraren om hjälp                       │
├─────────────────────────────────────────────────────┤
│  2. Läraren förklarar mappningen                    │
│     → "Title betyder titel, Stem är frågetexten"   │
├─────────────────────────────────────────────────────┤
│  3. M5 sparar mönstret                              │
│     → format_patterns.json                          │
├─────────────────────────────────────────────────────┤
│  4. Nästa gång samma format                         │
│     → M5 känner igen det automatiskt               │
└─────────────────────────────────────────────────────┘
```

### Liknar Step 3 fix_rules

Step 3 har `fix_rules.json` för transformationer:
```json
{
  "STEP3_001": {
    "issue_type": "missing_identifier",
    "auto_fix": "Generate from question number",
    "confidence": 0.95
  }
}
```

M5 får `format_patterns.json` för format-igenkänning:
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

## Workflow: Första gången (okänt format)

### Steg 1: M5 upptäcker okänt format

```
══════════════════════════════════════════════════════
M5 - BEHÖVER HJÄLP
══════════════════════════════════════════════════════

Jag hittade en fil men känner inte igen formatet.

Filens första 30 rader:
┌────────────────────────────────────────────────────┐
│ **Title:** Grundbegrepp inom AI                    │
│ **Type:** essay                                    │
│ **Bloom:** understand                              │
│ **Difficulty:** easy                               │
│ **Points:** 3                                      │
│ **Tags:** #elements_of_AI_chapter1 #grundbegrepp   │
│ **Learning Objective:** ARTI1000X - Kunskaper...   │
│ **Stem:**                                          │
│ I materialet introduceras flera viktiga begrepp... │
│                                                    │
│ ---                                                │
│                                                    │
│ **Title:** Maskininlärningens roll                 │
│ ...                                                │
└────────────────────────────────────────────────────┘

Jag ser mönster med **Rubrik:** men vet inte vad de betyder.

Kan du hjälpa mig förstå formatet?

══════════════════════════════════════════════════════
```

### Steg 2: Läraren förklarar

Läraren svarar (naturligt språk):
```
Title är frågetiteln
Type är frågetyp (essay, multiple_choice_single, etc)
Bloom ska bli en tagg
Difficulty ska också bli en tagg
Points är poäng
Tags är taggar (behåll som de är)
Learning Objective - hoppa över, ta inte med
Stem är där frågetexten börjar
--- separerar frågorna
```

### Steg 3: M5 bekräftar förståelse

```
══════════════════════════════════════════════════════
M5 - BEKRÄFTAR MAPPNING
══════════════════════════════════════════════════════

Okej, jag förstår formatet så här:

  **Title:**      → Frågetitel (title)
  **Type:**       → Frågetyp (type)
  **Bloom:**      → Lägg till som tagg (#understand)
  **Difficulty:** → Lägg till som tagg (#easy)
  **Points:**     → Poäng (points)
  **Tags:**       → Taggar (labels) - behåll som de är
  **Learning Objective:** → HOPPA ÖVER
  **Stem:**       → Frågetext (question_text)
  ---             → Fråga-separator

Stämmer detta?
  [1] Ja, spara detta mönster
  [2] Nej, låt mig korrigera

══════════════════════════════════════════════════════
```

### Steg 4: Spara mönster

Läraren säger "Ja" → M5 sparar till `format_patterns.json`

```
══════════════════════════════════════════════════════
M5 - MÖNSTER SPARAT
══════════════════════════════════════════════════════

✅ Sparade mönstret "M3 Bold Headers"
   Fil: logs/m5_format_patterns.json

Nästa gång jag ser detta format kommer jag känna igen det.

Nu kan vi börja bearbeta frågorna!

Hittade: 5 frågor

Visa fråga 1?
  [1] Ja, fortsätt
  [2] Visa alla först

══════════════════════════════════════════════════════
```

---

## Workflow: Andra gången (känt format)

```
══════════════════════════════════════════════════════
M5 - FORMAT IGENKÄNT
══════════════════════════════════════════════════════

Jag känner igen detta format!

Format: "M3 Bold Headers" (lärt 2026-01-28)
Confidence: 90%
Använt: 3 gånger tidigare

Hittade: 8 frågor

  - essay: 5 st
  - multiple_choice_single: 3 st

Vill du börja bearbeta frågorna?
  [1] Ja, börja med fråga 1
  [2] Visa alla frågor först
  [3] Detta ser fel ut, låt mig korrigera mappningen

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
      question: "Jag känner inte igen detta format. Kan du hjälpa mig förstå vad varje rubrik betyder?"
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
    message: `Mönster "${patternName}" sparat!`,
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
