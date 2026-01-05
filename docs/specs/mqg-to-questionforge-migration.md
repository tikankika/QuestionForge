# MQG → QuestionForge Migration Mapping

**Version:** 1.0  
**Status:** Draft  
**Date:** 2026-01-05  
**Purpose:** Map Modular Question Generation (MQG) Building Blocks to QuestionForge Modules

---

## Overview

This document maps the existing MQG Building Block structure (BB1-BB6) to the new QuestionForge Module architecture (M1-M4). The goal is to migrate proven methodology documentation while consolidating into a cleaner, more maintainable structure.

---

## Architecture Comparison

### MQG Structure (Current)

```
MQG Building Blocks
├── BB1: Content Analysis (8 files)
│   ├── bb1a: Introduction & Framework
│   ├── bb1b: Stage 0 - Material Analysis
│   ├── bb1c: Stage 1 - Initial Validation
│   ├── bb1d: Stage 2 - Emphasis Refinement
│   ├── bb1e: Stage 3 - Example Catalog
│   ├── bb1f: Stage 4 - Misconception Analysis
│   ├── bb1g: Stage 5 - Scope & Objectives
│   └── bb1h: Facilitation Best Practices
│
├── BB2: Assessment Design (9 files)
│   ├── bb2a: Introduction & Foundations
│   ├── bb2b: Stage 1 - Objective Validation
│   ├── bb2c: Stage 2 - Strategy Definition
│   ├── bb2d: Stage 3 - Question Target
│   ├── bb2e: Stage 4 - Bloom's Distribution
│   ├── bb2f: Stage 5 - Question Type Mix
│   ├── bb2g: Stage 6 - Difficulty Distribution
│   ├── bb2h: Stage 7 - Blueprint Construction
│   └── bb2i: Facilitation Best Practices
│
├── BB3: Technical Setup (7 files)
│   ├── bb3a: Introduction & Foundations
│   ├── bb3b: Stage 1 - Platform Orientation
│   ├── bb3c: Stage 2 - Metadata Configuration
│   ├── bb3d: Stage 3 - Label System Design
│   ├── bb3e: Stage 4 - Question Type Mapping
│   ├── bb3f: Stage 5 - Technical Validation
│   └── bb3g: Output & Implementation
│
├── BB4: Question Generation (5 files)
│   ├── bb4a: Introduction & Principles
│   ├── bb4b: Stage 4A - Basic Generation
│   ├── bb4c: Stage 4B - Distribution Review
│   ├── bb4d: Stage 4C - Finalization
│   └── bb4e: Process Guidelines
│
├── BB4.5: Assembly (5 files)
│   ├── bb4.5a: Introduction & Assembly
│   ├── bb4.5b: Stage 1 - Collection Validation
│   ├── bb4.5c: Stage 2 - Dashboard Construction
│   ├── bb4.5d: Stage 3 - Assembly Formatting
│   └── bb4.5e: Output Specification
│
├── BB5: Quality Assurance (6 files)
│   ├── bb5a: Introduction & Foundations
│   ├── bb5b: Phase 1 - Automated Validation
│   ├── bb5c: Phase 2 - Pedagogical Review
│   ├── bb5d: Phase 3 - Collective Analysis
│   ├── bb5e: Phase 4 - Documentation
│   └── bb5f: Output & Transition
│
└── BB6: Field Requirements (5 files)
    ├── bb6_Field_Requirements_v04.md
    ├── bb6_Field_Requirements_v05.md
    ├── bb6_Field_Requirements_v06.md
    ├── bb6_Output_Validation_v04.md
    └── bb6_Output_Validation_v05.md

Total: 45 files
```

### QuestionForge Structure (Target)

```
QuestionForge Modules
├── M1: Content Analysis
│   ├── overview.md
│   ├── stage-0-material-analysis.md
│   ├── stage-1-validation.md
│   ├── stage-2-emphasis.md
│   ├── stage-3-examples.md
│   ├── stage-4-misconceptions.md
│   └── stage-5-objectives.md
│
├── M2: Assessment Planning
│   ├── overview.md
│   ├── stage-1-metadata-schema.md
│   ├── stage-2-label-taxonomy.md
│   ├── stage-3-question-types.md
│   ├── stage-4-distribution.md
│   └── stage-5-platform-requirements.md
│
├── M3: Question Generation
│   ├── overview.md
│   ├── stage-1-templates.md
│   ├── stage-2-drafts.md
│   ├── stage-3-review.md
│   └── stage-4-iteration.md
│
└── M4: Quality Assurance
    ├── overview.md
    ├── stage-1-distractor-analysis.md
    ├── stage-2-cognitive-verification.md
    ├── stage-3-language-review.md
    └── stage-4-alignment-check.md

Total: 22 files (51% reduction)
```

---

## Detailed Mapping

### M1: Content Analysis ← BB1

| QuestionForge | MQG Source | Notes |
|---------------|------------|-------|
| `m1/overview.md` | bb1a + bb1h | Combine intro + best practices |
| `m1/stage-0-material-analysis.md` | bb1b | Direct migration |
| `m1/stage-1-validation.md` | bb1c | Direct migration |
| `m1/stage-2-emphasis.md` | bb1d | Direct migration |
| `m1/stage-3-examples.md` | bb1e | Direct migration |
| `m1/stage-4-misconceptions.md` | bb1f | Direct migration |
| `m1/stage-5-objectives.md` | bb1g | Direct migration |

**Migration Notes:**
- BB1 maps cleanly to M1 (1:1 stage correspondence)
- Combine bb1a (intro) and bb1h (best practices) into overview.md
- Preserve stage gate controls from revised bb1b-bb1g
- Remove redundant version info between files

---

### M2: Assessment Planning ← BB2 + BB3

| QuestionForge | MQG Source | Notes |
|---------------|------------|-------|
| `m2/overview.md` | bb2a + bb2i + bb3a | Combine foundations |
| `m2/stage-1-metadata-schema.md` | bb3c | Metadata configuration |
| `m2/stage-2-label-taxonomy.md` | bb3d | Label system design |
| `m2/stage-3-question-types.md` | bb2f + bb3e | Combine type selection + mapping |
| `m2/stage-4-distribution.md` | bb2e + bb2g + bb2h | Combine Bloom's + difficulty + blueprint |
| `m2/stage-5-platform-requirements.md` | bb3b + bb3f + bb3g | Platform orientation + validation |

**Migration Notes:**
- BB2 (pedagogical design) + BB3 (technical setup) = M2 (assessment planning)
- This consolidation recognizes that assessment planning includes BOTH pedagogical AND technical decisions
- bb2b (Objective Validation) moves to M1 stage-5 (they're related to content objectives)
- bb2c (Strategy Definition) merges with overview
- bb2d (Question Target) merges with stage-4-distribution

---

### M3: Question Generation ← BB4 + BB4.5

| QuestionForge | MQG Source | Notes |
|---------------|------------|-------|
| `m3/overview.md` | bb4a + bb4e + bb4.5a | Combine principles + guidelines + assembly intro |
| `m3/stage-1-templates.md` | NEW | Template selection (from BB6 knowledge) |
| `m3/stage-2-drafts.md` | bb4b | Basic generation |
| `m3/stage-3-review.md` | bb4c + bb4.5b + bb4.5c | Distribution review + collection validation + dashboard |
| `m3/stage-4-iteration.md` | bb4d + bb4.5d + bb4.5e | Finalization + assembly formatting + output spec |

**Migration Notes:**
- BB4 (generation) + BB4.5 (assembly) = M3 (complete generation workflow)
- Assembly is part of generation, not separate
- Add stage-1-templates.md to guide template selection (pulls from qf-specifications)
- Dashboard construction (bb4.5c) is a review tool, not a separate process

---

### M4: Quality Assurance ← BB5

| QuestionForge | MQG Source | Notes |
|---------------|------------|-------|
| `m4/overview.md` | bb5a + bb5f | Combine intro + transition |
| `m4/stage-1-distractor-analysis.md` | bb5c (partial) | Extract distractor review |
| `m4/stage-2-cognitive-verification.md` | bb5c (partial) | Extract Bloom's verification |
| `m4/stage-3-language-review.md` | bb5c (partial) | Extract language/terminology |
| `m4/stage-4-alignment-check.md` | bb5d + bb5e | Collective analysis + documentation |

**Migration Notes:**
- bb5b (Automated Validation) → moves to qf-pipeline (Step 2: Validator)
- bb5c (Pedagogical Review) splits into three focused stages
- This separation allows independent execution of QA checks
- Phase 4 (Documentation) merges with alignment check

---

### qf-specifications ← BB6

| QuestionForge | MQG Source | Notes |
|---------------|------------|-------|
| `question-format-v7.md` | bb6_Field_Requirements_v06 | Evolve to v7 format |
| `question-types/*.md` | bb6 (split) | One file per type |
| `metadata-schema.json` | bb6 (extract) | JSON Schema for validation |
| `label-taxonomy.yaml` | bb3d (extract) | YAML taxonomy |
| `platforms/inspera/` | bb3b, bb3e (extract) | Platform-specific docs |

**Migration Notes:**
- BB6 becomes shared specifications (not a module)
- Split monolithic field requirements into per-type specs
- Extract machine-readable schemas (JSON, YAML)
- Platform-specific content moves to platforms/ subdirectory

---

## Consolidation Benefits

### Reduced File Count

| Category | MQG | QuestionForge | Reduction |
|----------|-----|---------------|-----------|
| Modules | 45 files | 22 files | 51% |
| BB6 → Specs | 5 files | ~20 files | (expanded for clarity) |
| Total Methodology | 45 files | 22 module files | 51% |

### Improved Organization

1. **Clear Module Boundaries**
   - M1 = Content Analysis (what was taught)
   - M2 = Assessment Planning (how to assess)
   - M3 = Question Generation (create questions)
   - M4 = Quality Assurance (verify quality)

2. **Eliminated Redundancy**
   - Best practices merged into overviews
   - Facilitation guidance consolidated
   - Duplicate stage gates unified

3. **Cleaner Naming**
   - `stage-N-purpose.md` instead of `bbXx_StageN_Description.md`
   - Descriptive filenames
   - Consistent hierarchy

---

## Migration Execution Plan

### Phase 1: Prepare Structure
```bash
# Create qf-specifications directories
mkdir -p qf-specifications/question-types
mkdir -p qf-specifications/platforms/inspera
mkdir -p qf-specifications/modules/m1-content-analysis
mkdir -p qf-specifications/modules/m2-assessment-planning
mkdir -p qf-specifications/modules/m3-question-generation
mkdir -p qf-specifications/modules/m4-quality-assurance
```

### Phase 2: Migrate M1 (Content Analysis)
1. Copy bb1b-bb1g → m1/stage-*.md
2. Combine bb1a + bb1h → m1/overview.md
3. Update cross-references
4. Verify stage gates preserved

### Phase 3: Migrate M2 (Assessment Planning)
1. Extract metadata content from bb3c → m2/stage-1-metadata-schema.md
2. Extract label content from bb3d → m2/stage-2-label-taxonomy.md
3. Combine bb2f + bb3e → m2/stage-3-question-types.md
4. Combine bb2e + bb2g + bb2h → m2/stage-4-distribution.md
5. Combine bb3b + bb3f + bb3g → m2/stage-5-platform-requirements.md
6. Create overview from bb2a + bb2i + bb3a

### Phase 4: Migrate M3 (Question Generation)
1. Create m3/stage-1-templates.md (new)
2. Copy bb4b → m3/stage-2-drafts.md
3. Combine bb4c + bb4.5b + bb4.5c → m3/stage-3-review.md
4. Combine bb4d + bb4.5d + bb4.5e → m3/stage-4-iteration.md
5. Create overview from bb4a + bb4e + bb4.5a

### Phase 5: Migrate M4 (Quality Assurance)
1. Split bb5c into three stage files
2. Combine bb5d + bb5e → m4/stage-4-alignment-check.md
3. Create overview from bb5a + bb5f
4. Move automated validation logic to qf-pipeline spec

### Phase 6: Create qf-specifications
1. Evolve bb6_v06 → question-format-v7.md
2. Split into question-types/*.md (15+ files)
3. Create metadata-schema.json
4. Create label-taxonomy.yaml
5. Extract platform-specific docs to platforms/inspera/

### Phase 7: Validation
1. Review all cross-references
2. Verify no content lost
3. Test documentation completeness
4. Update QuestionForge README

---

## File-Level Migration Checklist

### BB1 → M1
- [ ] bb1a → m1/overview.md (partial)
- [ ] bb1b → m1/stage-0-material-analysis.md
- [ ] bb1c → m1/stage-1-validation.md
- [ ] bb1d → m1/stage-2-emphasis.md
- [ ] bb1e → m1/stage-3-examples.md
- [ ] bb1f → m1/stage-4-misconceptions.md
- [ ] bb1g → m1/stage-5-objectives.md
- [ ] bb1h → m1/overview.md (merge)

### BB2 + BB3 → M2
- [ ] bb2a → m2/overview.md (partial)
- [ ] bb2b → m1/stage-5-objectives.md (merge - objective validation)
- [ ] bb2c → m2/overview.md (merge - strategy)
- [ ] bb2d → m2/stage-4-distribution.md (merge)
- [ ] bb2e → m2/stage-4-distribution.md (Bloom's)
- [ ] bb2f → m2/stage-3-question-types.md (partial)
- [ ] bb2g → m2/stage-4-distribution.md (difficulty)
- [ ] bb2h → m2/stage-4-distribution.md (blueprint)
- [ ] bb2i → m2/overview.md (merge)
- [ ] bb3a → m2/overview.md (merge)
- [ ] bb3b → m2/stage-5-platform-requirements.md (partial)
- [ ] bb3c → m2/stage-1-metadata-schema.md
- [ ] bb3d → m2/stage-2-label-taxonomy.md
- [ ] bb3e → m2/stage-3-question-types.md (partial)
- [ ] bb3f → m2/stage-5-platform-requirements.md (partial)
- [ ] bb3g → m2/stage-5-platform-requirements.md (merge)

### BB4 + BB4.5 → M3
- [ ] bb4a → m3/overview.md (partial)
- [ ] bb4b → m3/stage-2-drafts.md
- [ ] bb4c → m3/stage-3-review.md (partial)
- [ ] bb4d → m3/stage-4-iteration.md (partial)
- [ ] bb4e → m3/overview.md (merge)
- [ ] bb4.5a → m3/overview.md (merge)
- [ ] bb4.5b → m3/stage-3-review.md (merge)
- [ ] bb4.5c → m3/stage-3-review.md (merge)
- [ ] bb4.5d → m3/stage-4-iteration.md (merge)
- [ ] bb4.5e → m3/stage-4-iteration.md (merge)
- [ ] NEW → m3/stage-1-templates.md

### BB5 → M4
- [ ] bb5a → m4/overview.md (partial)
- [ ] bb5b → qf-pipeline (automated validation)
- [ ] bb5c (distractor) → m4/stage-1-distractor-analysis.md
- [ ] bb5c (cognitive) → m4/stage-2-cognitive-verification.md
- [ ] bb5c (language) → m4/stage-3-language-review.md
- [ ] bb5d → m4/stage-4-alignment-check.md (partial)
- [ ] bb5e → m4/stage-4-alignment-check.md (merge)
- [ ] bb5f → m4/overview.md (merge)

### BB6 → qf-specifications
- [ ] bb6_v06 → question-format-v7.md
- [ ] bb6_v06 → question-types/*.md (split)
- [ ] bb6_v06 → metadata-schema.json (extract)
- [ ] bb3d → label-taxonomy.yaml (extract)
- [ ] bb3b,bb3e → platforms/inspera/*.md (extract)

---

## Decision Log

| Decision | Rationale |
|----------|-----------|
| Merge BB2 + BB3 into M2 | Assessment planning includes both pedagogical design AND technical setup |
| Merge BB4 + BB4.5 into M3 | Assembly is part of generation, not separate |
| Split bb5c into 3 stages | Independent QA checks enable flexible execution |
| Move BB6 to qf-specifications | Format specs are shared infrastructure, not a methodology module |
| Move bb5b to qf-pipeline | Automated validation belongs in the tool, not methodology |

---

*Migration Mapping v1.0 | QuestionForge | 2026-01-05*
