# Historical Documentation

This folder contains archived documentation from earlier project phases. These documents are preserved for historical context but are **no longer actively maintained**.

---

## Archived Documents

### development_plan_legacy.md
**Archived**: 2025-11-01
**Original Date**: 2025-10-30
**Reason**: Superseded by [VISION.md](../../VISION.md) and [ROADMAP.md](../../ROADMAP.md)

**Historical Context**:
- Original project plan based on Excel-to-QTI workflow
- Competition analysis of existing QTI tools (qti-package-maker, text2qti, qti2txt)
- Early architecture decisions and rationale
- Project scope definition before Markdown transition
- Platform uniqueness analysis (first open-source Inspera QTI generator)

**Note**: This document references Excel templates which were replaced with Markdown format in v0.2.0-alpha (2025-10-31). The Excel-based workflow was found to be less flexible than structured Markdown for question authoring.

**What Changed**:
- **Then**: Excel spreadsheets for question input
- **Now**: Markdown files with YAML frontmatter
- **Why**: Markdown is more flexible, version-control friendly, human-readable, and enables Claude Desktop AI assistance

---

## Why Archive Instead of Delete?

Archived documents provide:
- **Historical context** for design decisions ("why did we choose this?")
- **Reference** for evolution of project vision
- **Institutional knowledge** preservation for future contributors
- **Comparison** of original vs. current approaches

These documents are kept in version control (Git) so the complete project history remains accessible.

---

## For Current Project Planning

If you're looking for **active project documentation**, see the root directory:

- **[VISION.md](../../VISION.md)** - Long-term vision and impact goals (1-3 years)
- **[ROADMAP.md](../../ROADMAP.md)** - Feature development roadmap (6-12 months, v0.3.0 → v1.0.0)
- **[IDEAS.md](../../IDEAS.md)** - Feature wishlist and community suggestions
- **[CHANGELOG.md](../../CHANGELOG.md)** - Detailed version history with daily progress

For technical documentation:
- **[docs/markdown_specification.md](../markdown_specification.md)** - Current markdown format specification
- **[templates/markdown/](../../templates/markdown/)** - Active templates for question generation

---

## Document Lifecycle

Documents move to this archive when:
1. They describe approaches that have been replaced
2. They reference deprecated features or workflows
3. They duplicate information now in authoritative documents
4. They are >6 months old and no longer reflect current practices

Documents are **never deleted** to preserve institutional knowledge and decision rationale.

---

**Last Updated**: 2025-11-01
