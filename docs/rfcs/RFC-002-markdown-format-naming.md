# RFC-002: QuestionForge Markdown Format Naming and Versioning

| Field | Value |
|-------|-------|
| **Status** | Implemented |
| **Created** | 2026-01-17 |
| **Updated** | 2026-01-17 |
| **Author** | Niklas Karlsson |
| **Relates to** | qf-pipeline (step1), documentation, WORKFLOW.md |

## Summary

This RFC proposes replacing ambiguous version numbers ("v6.3", "v6.5") with descriptive, stable format names for QuestionForge markdown question files. The current naming creates confusion about what formats are supported and implies a versioning scheme that doesn't exist.

## Problem Statement

### Current Terminology Issues

**1. "v6.5" is misleading**
- Implies this is version 6.5 of something
- What happened to v1-v5? v6.0-v6.4?
- What happens when we update the format - v6.6? v7.0?
- Not descriptive of what the format actually IS

**2. "v6.3" doesn't exist in code**
- Term appears in WORKFLOW.md: "(v6.3 → v6.5)"
- Actually refers to "Level 3 / OLD_SYNTAX" format from `step1_guided_build_spec.md`
- Users will be confused searching for "v6.3" documentation

**3. step1 handles MORE than just "v6.3"**

From `step1_guided_build_spec.md`, step1 actually handles:

```python
FormatLevel.RAW (Level 1)           # **FRÅGA:** format
FormatLevel.SEMI_STRUCTURED (Level 2)  # **Type**: format  
FormatLevel.OLD_SYNTAX (Level 3)    # @question: format
FormatLevel.VALID_V65 (Level 4)     # ^question format (current target)
```

**Step1 is NOT just "v6.3 → v6.5"** - it's:
- RAW → QFMD
- SEMI → QFMD
- OLD_SYNTAX → QFMD
- User-generated text → QFMD
- AI-generated questions → QFMD
- Exported from other tools → QFMD

### Real-World Scenarios

Users will arrive at step1 with:
- ✅ Questions from M3 (Question Generation module)
- ✅ Manually written questions in various formats
- ✅ AI-generated questions (ChatGPT, Claude, etc.)
- ✅ Questions exported from other quiz tools
- ✅ Old MQG questions from previous projects
- ✅ Questions from collaborators with their own conventions

**None of these are "v6.3"** - that term is meaningless to users.

## Proposed Solution

### New Naming System

Replace version numbers with descriptive format names:

| Old Term | New Term | Description |
|----------|----------|-------------|
| "v6.5" | **QFMD** | QuestionForge Markdown (canonical format) |
| "v6.3" | **Legacy Syntax** | Old @question:/@type: syntax |
| "Level 1" | **Unstructured** | Plain text with minimal markup |
| "Level 2" | **Semi-Structured** | Has headers but not full metadata |
| "Level 3" | **Legacy Syntax** | @field notation |
| "Level 4" | **QFMD** | Current canonical format |

### QFMD Definition

**QFMD (QuestionForge Markdown)** is:
- The canonical markdown format for QuestionForge
- What step2_validate checks against
- What step4_export converts to QTI
- Defined by question type specifications in `/specs/`
- Uses `^metadata` and `@field/@end_field` notation

**Characteristics:**
```markdown
# Q001 Question Title
^question Q001
^type multiple_choice_single
^identifier COURSE_Q001
^points 1
^labels #Topic #Bloom #Difficulty

@field question_text
Question content here
@end_field

@field options
A. Option 1
B. Option 2
@end_field
```

**NOT versioned** because:
- Format is defined by question type specs (which CAN version)
- Specs can evolve independently (e.g., `multiple_choice_single_v2.yaml`)
- QFMD itself is just the container syntax

### Updated Terminology

**In code:**
```python
class FormatLevel(Enum):
    UNSTRUCTURED = "unstructured"      # Was: RAW / Level 1
    SEMI_STRUCTURED = "semi_structured"  # Was: Level 2
    LEGACY_SYNTAX = "legacy_syntax"    # Was: OLD_SYNTAX / Level 3
    QFMD = "qfmd"                      # Was: VALID_V65 / Level 4
```

**In documentation:**
- "Convert questions to QFMD format"
- "step1: Guided conversion to QFMD"
- "Input: Any format → Output: QFMD"

**In user-facing messages:**
```
"This file uses legacy syntax. Let me convert it to QFMD format."
"Your questions are already in QFMD format - ready for validation!"
"I'll help you structure these questions into QFMD format."
```

## Migration Plan

### Phase 1: Code Updates

**File:** `packages/qf-pipeline/src/qf_pipeline/step1/detector.py`
```python
# BEFORE
class FormatLevel(Enum):
    RAW = 1
    SEMI_STRUCTURED = 2
    OLD_SYNTAX = 3
    VALID_V65 = 4

# AFTER
class FormatLevel(Enum):
    UNSTRUCTURED = "unstructured"
    SEMI_STRUCTURED = "semi_structured"
    LEGACY_SYNTAX = "legacy_syntax"
    QFMD = "qfmd"
```

**File:** `step1_guided_build_spec.md`
- Replace "Level 1-4" with descriptive names
- Remove "v6.5" references
- Add QFMD definition section

### Phase 2: Documentation Updates

**WORKFLOW.md:**
```markdown
# BEFORE
│ step1 (OPTIONAL)     │
│ Guided Build         │
│ (v6.3 → v6.5)        │

# AFTER
│ step1 (OPTIONAL)     │
│ Guided Build         │
│ Convert to QFMD      │
```

**Tool descriptions:**
```markdown
# BEFORE
step1_start: Starta guided build session | När du har v6.3 format frågor

# AFTER  
step1_start: Starta guided build session | När du har questions that need conversion to QFMD
```

### Phase 3: User Communication

**If user has QFMD already:**
```
✅ Your questions are already in QFMD format!
   You can skip step1 and go directly to step2_validate.
```

**If user has legacy format:**
```
📝 I see your questions use legacy syntax (@question:, @type:).
   Let me convert them to QFMD format using step1.
```

**If user has unstructured text:**
```
📝 These questions need to be structured into QFMD format.
   I recommend using M3 (Question Generation) module for this.
   Alternatively, I can help structure them in step1 if they're close.
```

## Benefits

### 1. Clarity
- "QFMD" clearly describes WHAT it is (QuestionForge Markdown)
- Not tied to arbitrary version numbers
- Self-documenting in code and conversation

### 2. Flexibility
- Question type specs can version independently
- New question types don't require "bumping the version"
- Format can evolve without confusion

### 3. User Experience
- Users understand "convert to QFMD" better than "v6.3 → v6.5"
- Clear what format they should aim for
- Easier to search documentation

### 4. Future-Proof
- No version number collisions
- Can introduce new input formats without renumbering
- Aligns with industry practice (e.g., "GFM" = GitHub Flavored Markdown)

## Open Questions

### Q1: Should we keep "Level 1-4" internally?
**Options:**
A. Remove entirely, use descriptive names everywhere
B. Keep for internal detection logic but don't expose to users
C. Document as "detection levels" separate from "format names"

**Recommendation:** Option A - remove entirely for consistency

### Q2: What about old YAML specs that say "v6.5"?
**Example:** Some specs might reference "v6.5" in comments

**Solution:** Global find/replace in specs directory

### Q3: Do we need a "format version" field in QFMD?
**Proposal:** Add optional metadata
```markdown
^format_version 1.0
^question Q001
...
```

**Recommendation:** NO - question type specs handle versioning

### Q4: How to handle user confusion during transition?
**Example:** User says "I have v6.3 questions"

**Solution:** Claude recognizes old terms and translates:
```
I understand you have questions in the legacy syntax format 
(what we used to call "v6.3"). Let me convert them to QFMD 
format for you.
```

## Implementation Checklist

- [x] Update `FormatLevel` enum in detector.py
- [x] Update step1_guided_build_spec.md
- [x] Update WORKFLOW.md (empty file, no changes needed)
- [x] Update tool descriptions in qf-pipeline MCP
- [x] Search/replace "v6.5" in all specs
- [x] Search/replace "v6.3" in documentation
- [ ] Add QFMD definition to main README
- [x] Update error messages in step1 tools
- [x] Update step2_validate messages
- [x] Test that old terminology doesn't leak in user-facing output

## Success Criteria

1. ✅ No references to "v6.3" or "v6.5" in user-facing documentation
2. ✅ QFMD term used consistently across all packages
3. ✅ Users can find "QFMD" definition easily
4. ✅ Code enum values are descriptive, not numeric
5. ✅ Old terminology handled gracefully in conversation

## Related Work

- ADR-014: Shared Session (mentions format detection)
- step1_guided_build_spec.md (defines current format levels)
- WORKFLOW.md (will need updates)

## References

- Industry examples: GFM (GitHub Flavored Markdown), CommonMark
- Question type specs: `/packages/qf-pipeline/src/qf_pipeline/specs/`

---

**Status:** Ready for review and approval
**Next Steps:** Gather feedback, then implement Phase 1
