# ADR 001: Use Markdown for Question Input Format

## Status

Accepted

## Date

2025-10-30

## Context

The QTI Generator requires an input format for defining assessment questions before conversion to QTI 2.2 XML. The tool targets educators who will use Claude Desktop for question generation, requiring a format that is:

1. Human-readable and easy to write
2. Compatible with AI-assisted generation workflows
3. Capable of representing rich content (images, mathematical notation, formatting)
4. Version-control friendly for collaboration
5. Structurally validatable

### Alternatives Considered

**Option A: Excel/CSV**
- ✅ Familiar to educators
- ❌ Poor for rich content (images, math, formatting)
- ❌ Not version-control friendly
- ❌ Difficult for AI to generate reliably
- ❌ No structural validation

**Option B: JSON**
- ✅ Highly structured
- ✅ Easy to validate
- ❌ Not human-readable
- ❌ Difficult to write manually
- ❌ Poor fit for AI-generated content

**Option C: YAML**
- ✅ Structured and validatable
- ✅ Human-readable
- ❌ Limited support for rich content
- ❌ Indentation-sensitive (error-prone)

**Option D: Markdown with YAML frontmatter** (Selected)
- ✅ Human-readable and writable
- ✅ Excellent for rich content (images, math via LaTeX, code blocks)
- ✅ Natural fit for AI-assisted generation (Claude excels at markdown)
- ✅ Version-control friendly (plain text, line-based diffs)
- ✅ YAML frontmatter provides structure and metadata
- ✅ Widely supported tools and libraries (Python: `markdown2`, `pyyaml`)
- ❌ Requires parsing (minor complexity)

## Decision

We will use **Markdown with YAML frontmatter** as the input format for question definitions.

### Structure

```markdown
---
test_metadata:
  title: "Test Title"
  identifier: "UNIQUE_ID"
  language: "en"

learning_objectives:
  - id: "LO1"
    description: "Students will be able to..."
---

# Question 1: Title

**Type**: multiple_choice_single
**Identifier**: Q001
**Points**: 1
**Learning Objectives**: LO1
**Bloom's Level**: Remember

## Question Text

What is the capital of Sweden?

## Options

A. Oslo
B. Stockholm
C. Copenhagen
D. Helsinki

## Answer

B

## Feedback
...
```

### Rationale

1. **Pedagogical Alignment**: Markdown's natural structure mirrors how educators think about questions (prompt → options → answer → feedback)

2. **AI Integration**: Claude Desktop natively generates high-quality markdown, making the two-phase workflow seamless:
   - Phase 1: Claude generates questions in markdown
   - Phase 2: Python converts markdown → QTI XML

3. **Rich Content Support**: Native support for:
   - Images: `![alt](path.png)`
   - Math: `$x^2$` or `$$\frac{a}{b}$$`
   - Code: ` ```python ... ``` `
   - Formatting: **bold**, *italic*, lists

4. **Version Control**: Plain text format enables:
   - Git-based collaboration
   - Meaningful diffs
   - Easy conflict resolution

5. **Validation**: YAML frontmatter provides structured metadata while markdown body allows flexible content

## Consequences

### Positive

- Educators can read/write questions without specialized tools
- Claude Desktop workflow is natural and efficient
- Rich pedagogical content (images, equations) is natively supported
- Version control enables collaboration and history tracking
- Python parsing is straightforward (`pyyaml` + `markdown2`)

### Negative

- Requires parser implementation (moderate complexity)
- Less rigidly structured than JSON (more validation needed)
- Markdown parsing has edge cases (mitigated by well-defined spec)

### Neutral

- Team must learn markdown syntax (low barrier, widely known)
- Need to define and document markdown specification precisely

## Implementation Notes

- Use `pyyaml` for YAML frontmatter parsing
- Use `markdown2` or `mistune` for markdown → HTML conversion
- Define strict validation schema for required fields
- Document markdown specification comprehensively
- Provide examples for all question types

## References

- Markdown specification: https://commonmark.org/
- YAML specification: https://yaml.org/spec/
- Python libraries: `pyyaml`, `markdown2`, `python-frontmatter`
- CommonMark Python: https://github.com/readthedocs/commonmark.py

## Superseded By

None

## Related Decisions

- ADR 002: XML Template Strategy
- ADR 003: Pedagogical Framework Integration
