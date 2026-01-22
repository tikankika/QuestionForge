# ADR-010: Step 3 Decision Architecture

**Status:** Proposed  
**Date:** 2026-01-06  
**Deciders:** Niklas  
**Context:** qf-pipeline Step 3 design

---

## Context

qf-pipeline has a linear workflow:

```
step0_start ──▶ step2_validate ──▶ step3_decision ──▶ step4_export
```

Step 3 is the decision point where the teacher chooses HOW to export validated questions. Both paths ultimately produce QTI output, but through different processes.

---

## Decision

### Step 3 has TWO paths, both leading to QTI export:

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: DECISION                                               │
│                                                                  │
│  "How do you want to export your questions?"                    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  PATH A: Direct Export                                      ││
│  │  ────────────────────                                       ││
│  │  • Export ALL validated questions                           ││
│  │  • No filtering, no grouping                                ││
│  │  • Simple QTI package (individual items)                    ││
│  │  • Fast, straightforward                                    ││
│  │                                                              ││
│  │  Tool: step4_export (existing)                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  PATH B: Question Set Builder                               ││
│  │  ────────────────────────────                               ││
│  │  • Filter questions (Bloom, difficulty, tags, points)       ││
│  │  • Group into sections                                      ││
│  │  • Configure shuffle per section                            ││
│  │  • Choose: with labels OR without labels                    ││
│  │  • Preview before export                                    ││
│  │  • QTI assessmentTest package                               ││
│  │                                                              ││
│  │  Tool: step3_question_set (NEW - see ADR-011)               ││
│  │  Then: step4_export                                         ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Both paths ──▶ Step 4: Export ──▶ QTI Package                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Path Comparison

| Aspect | Path A: Direct | Path B: Question Set |
|--------|----------------|----------------------|
| **Use case** | Export all questions | Create dynamic test |
| **Filtering** | None | Bloom, difficulty, tags, points |
| **Grouping** | None | Sections with count |
| **Shuffle** | No | Per section |
| **Labels** | As-is | With OR without |
| **Output** | QTI items | assessmentTest + items |
| **Complexity** | Simple | Complex |
| **Tool** | step4_export | step3_question_set → step4_export |

---

## Implementation

### No new tool needed for Step 3 decision itself

The decision is made by the teacher through dialogue:

```
Claude: "Your 27 questions are validated. How do you want to export?"
        
        A) Direct export - all questions as QTI package
        B) Question Set - filter, group, and configure
        
Teacher: "B - I want to create a Question Set"

Claude: [calls step3_question_set tool - see ADR-011]
```

### Tool flow

**Path A:**
```
step2_validate ──▶ step4_export
```

**Path B:**
```
step2_validate ──▶ step3_question_set ──▶ step4_export
                         │
                         ├── Filtering
                         ├── Sections
                         ├── Shuffle config
                         └── Labels choice
```

---

## Labels: With vs Without

**With labels:**
- Questions keep their ^labels metadata
- Inspera can filter/group by labels
- Useful for question banks

**Without labels:**
- Labels stripped from export
- Cleaner for final exams
- Students don't see categorization

**Note:** Current QTI-Generator Question Set builder does NOT have this choice. This is a NEW feature for qf-pipeline.

---

## Consequences

### Positive
- Clear separation of simple vs complex export
- Teacher has explicit choice
- Both paths produce valid QTI
- Path B enables advanced Inspera features

### Negative
- Path B requires significant new development (ADR-011)
- Two mental models for export

### Neutral
- Path A already works (step4_export exists)
- Path B is optional enhancement

---

## Related ADRs

- **ADR-011:** Question Set Builder (Path B details) - REQUIRED
- **ADR-009:** Resource Handling (applies to both paths)
- **ADR-006:** Session Management

---

*ADR-010 | QuestionForge | 2026-01-06*
