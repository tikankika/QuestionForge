# ADR-002: Module Naming (BB → M1-M4)

## Status
**Accepted**

## Date
2026-01-02

## Context

The existing Modular QGen Framework used "Building Block" (BB) naming:
- BB1: Content Analysis
- BB2: Assessment Design
- BB3: Technical Setup
- BB4: Question Generation
- BB5: Quality Assurance
- BB6: Export & Validation

Problems with "BB" naming:
- Internal jargon that users don't understand
- "BB6" doesn't communicate "export and validation"
- Six blocks when some could be merged
- BB3 (Technical Setup) was Inspera-specific

## Options

### Option A: Keep BB Naming
- BB1 through BB6
- **Pros**: Existing documentation uses it
- **Cons**: Confusing, jargon-heavy

### Option B: Rename to Modules (M1-M6)
- M1 through M6
- **Pros**: Cleaner, "Module" is clearer than "Building Block"
- **Cons**: Still 6 when some overlap

### Option C: Rename to Modules AND Merge (M1-M4)
- Reduce from 6 to 4 modules
- Merge BB2+BB3 into Assessment Planning
- Move BB6 to separate MCP (pipeline)
- **Pros**: Clearer, leaner, better separation
- **Cons**: Migration effort from existing docs

## Decision

**Option C: Rename to Modules AND Merge (M1-M4)**

| Old | New | Name | Change |
|-----|-----|------|--------|
| BB1 | M1 | Content Analysis | Renamed only |
| BB2+BB3 | M2 | Assessment Planning | Merged |
| BB4 | M3 | Question Generation | Renamed only |
| BB5 | M4 | Quality Assurance | Renamed only |
| BB6 | MCP 2 | Pipeline | Moved to separate MCP |

## Rationale

1. **"Module" is clearer**: More intuitive than "Building Block"
2. **BB2+BB3 natural merge**: Assessment design and metadata/labels are one planning activity
3. **BB3 was too Inspera-specific**: Absorbing into M2 makes it platform-agnostic
4. **BB6 is technical, not pedagogical**: Belongs in pipeline MCP, not scaffolding
5. **4 is easier than 6**: Less cognitive load for teachers

## Consequences

### Positive
- Clearer naming for users
- Logical grouping of related activities
- Platform-agnostic design (M2 not Inspera-specific)
- Technical concerns separated to MCP 2

### Negative
- Existing BB1-BB6 documentation needs migration
- Some internal references will break

### Mitigation
- Document migration plan in DISCOVERY_BRIEF
- Archive old docs, don't delete
- Update all references systematically

## Validation
- [ ] All documentation updated to M1-M4 naming
- [ ] No remaining BB references in active docs
- [ ] Teachers find new naming intuitive

---

*ADR-002 | QuestionForge | 2026-01-02*
