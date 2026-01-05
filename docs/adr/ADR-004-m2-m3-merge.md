# ADR-004: M2+M3 Merge (Assessment Planning)

## Status
**Accepted**

## Date
2026-01-02

## Context

Original Building Block structure had:
- **BB2: Assessment Design** - Question types, distribution, cognitive levels
- **BB3: Technical Setup** - Inspera configuration, metadata, labels

During SHAPE phase, we questioned whether these should be separate modules.

Key observations:
- BB3 was too Inspera-specific
- When teachers select question types (BB2), they need to know technical requirements
- Metadata and labels are part of assessment planning, not separate "setup"
- Teachers don't naturally separate "what types" from "how to label"

## Options

### Option A: Keep Separate (M2 + M3)
- M2: Assessment Design
- M3: Technical Setup
- **Pros**: Finer granularity
- **Cons**: Artificial separation, Inspera-specific

### Option B: Merge into Assessment Planning (M2 only)
- M2: Assessment Planning (types + distribution + metadata + labels)
- Remove M3 as separate module
- **Pros**: Natural grouping, platform-agnostic
- **Cons**: Larger module, more stages

### Option C: Keep Separate but Rename
- M2: Assessment Design
- M3: Metadata Design (not "Technical Setup")
- **Pros**: Less Inspera-specific naming
- **Cons**: Still artificial separation

## Decision

**Option B: Merge into Assessment Planning**

New M2 structure:
```
M2: Assessment Planning
├── Stage 1: Metadata Schema Definition
│   └── What to track? (topic, difficulty, bloom, etc.)
├── Stage 2: Label Taxonomy Design
│   └── Hierarchical label system
├── Stage 3: Question Type Selection
│   └── Which types? (shows technical requirements)
└── Stage 4: Platform Requirements (optional)
    └── Inspera-specific needs if known
```

## Rationale

1. **Natural grouping**: Teachers think of this as one planning activity
2. **Platform-agnostic**: Not called "Technical Setup" or "Inspera Config"
3. **Question types + metadata belong together**: Selecting MC means knowing MC requires options, feedback, etc.
4. **Reduces cognitive load**: 4 modules easier than 5
5. **Teacher feedback**: "Technical Setup" sounded intimidating

## Consequences

### Positive
- More intuitive for teachers
- Platform-agnostic design
- One fewer module to maintain
- Question type technical requirements shown in context

### Negative
- M2 is now larger (4 stages)
- Must migrate BB2 and BB3 docs into single M2

### Mitigation
- Clear stage structure within M2
- Stage 4 (Platform Requirements) is optional
- Documentation clearly separates stages

## Validation
- [ ] M2 documentation covers all former BB2+BB3 content
- [ ] Teachers can complete M2 without Inspera-specific knowledge
- [ ] Question type selection shows technical implications clearly

---

*ADR-004 | QuestionForge | 2026-01-02*
