# QuestionForge Logging Specification

**Version:** 1.0  
**Status:** Draft  
**Date:** 2026-01-05  
**Purpose:** Traceability + ML training data

---

## Design Principles

1. **Local first** - PostgreSQL runs locally for each teacher
2. **All loops tracked** - Guided Build, Validation, Review
3. **Abandoned sessions logged** - Valuable ML data
4. **Snapshots at key steps** - Not every micro-change
5. **Actor always noted** - Teacher / AI / Automatic validation
6. **ML-ready from day 1** - Structured data for future training

---

## PostgreSQL Schema

### Overall Structure

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    sessions     │────<│    questions    │────<│     events      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │
                              │
                        ┌─────┴─────┐
                        │ snapshots │
                        └───────────┘
```

### Table: sessions

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identification
    session_name VARCHAR(255) NOT NULL,
    
    -- Context
    course_code VARCHAR(50),
    course_name VARCHAR(255),
    module_name VARCHAR(255),
    assessment_type VARCHAR(50),  -- 'quiz', 'exam', 'formative'
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,  -- NULL = in progress or abandoned
    abandoned_at TIMESTAMP WITH TIME ZONE,  -- NULL = not abandoned
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',  -- 'active', 'completed', 'abandoned'
    
    -- Metadata
    target_question_count INTEGER,
    actual_question_count INTEGER DEFAULT 0,
    
    -- Configuration used
    config JSONB  -- Blueprint, Bloom's distribution, etc.
);

CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_course ON sessions(course_code);
CREATE INDEX idx_sessions_created ON sessions(created_at);
```

### Table: questions

```sql
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    
    -- Identification
    question_identifier VARCHAR(100) NOT NULL,  -- 'MC_Q001'
    question_type VARCHAR(50) NOT NULL,         -- 'multiple_choice_single'
    
    -- Current status
    current_stage VARCHAR(30) DEFAULT 'draft',
    -- Stages: 'draft', 'guided_build', 'validating', 'review', 'finalized', 'exported', 'abandoned'
    
    -- Latest version
    current_version INTEGER DEFAULT 1,
    current_content JSONB,  -- Latest snapshot
    
    -- Pedagogical context
    learning_objective VARCHAR(255),
    bloom_level VARCHAR(20),
    difficulty VARCHAR(20),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    finalized_at TIMESTAMP WITH TIME ZONE,
    exported_at TIMESTAMP WITH TIME ZONE,
    abandoned_at TIMESTAMP WITH TIME ZONE,
    
    -- Statistics
    total_iterations INTEGER DEFAULT 0,
    validation_attempts INTEGER DEFAULT 0,
    validation_failures INTEGER DEFAULT 0,
    
    -- Quality assessment (optional, for ML)
    teacher_quality_score INTEGER,  -- 1-5 if teacher rates
    
    UNIQUE(session_id, question_identifier)
);

CREATE INDEX idx_questions_session ON questions(session_id);
CREATE INDEX idx_questions_stage ON questions(current_stage);
CREATE INDEX idx_questions_type ON questions(question_type);
CREATE INDEX idx_questions_bloom ON questions(bloom_level);
```

### Table: events

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
    
    -- Timestamp
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Event type
    event_type VARCHAR(50) NOT NULL,
    -- Types: see EVENT_TYPES below
    
    -- Who/what caused the event
    actor_type VARCHAR(30) NOT NULL,  -- 'teacher', 'ai_suggestion', 'auto_validation', 'system'
    actor_detail TEXT,                 -- Description of what happened
    
    -- Stage change
    stage_before VARCHAR(30),
    stage_after VARCHAR(30),
    
    -- Version change
    version_before INTEGER,
    version_after INTEGER,
    
    -- Loop context
    loop_type VARCHAR(30),         -- 'guided_build', 'validation', 'review', NULL
    loop_iteration INTEGER,        -- Which iteration in the loop (1, 2, 3...)
    
    -- Change details
    change_summary JSONB,
    -- Example: {"fields_changed": ["options[1].text"], "change_type": "distractor_improvement"}
    
    -- Validation result (if event_type = validation_*)
    validation_result JSONB,
    -- Example: {"passed": false, "errors": [...], "warnings": [...]}
    
    -- For abandoned events
    abandonment_reason TEXT,
    
    -- Reference to snapshots
    snapshot_before_id UUID,
    snapshot_after_id UUID
);

CREATE INDEX idx_events_question ON events(question_id);
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_actor ON events(actor_type);
CREATE INDEX idx_events_loop ON events(loop_type, loop_iteration);
```

### Table: snapshots

```sql
CREATE TABLE snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
    
    -- Version
    version INTEGER NOT NULL,
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Complete content
    content JSONB NOT NULL,
    -- Contains: question_text, options, correct_answer, feedback, metadata, etc.
    
    -- Hash value for quick comparison
    content_hash VARCHAR(64),
    
    UNIQUE(question_id, version)
);

CREATE INDEX idx_snapshots_question ON snapshots(question_id);
CREATE INDEX idx_snapshots_version ON snapshots(question_id, version);
```

---

## Event Types

### Lifecycle Events

| Event Type | Description | Actor Types |
|------------|-------------|-------------|
| `question_created` | Question created (first draft) | teacher, ai_suggestion |
| `question_modified` | Question modified | teacher, ai_suggestion |
| `question_finalized` | Marked as complete | teacher |
| `question_exported` | Exported to QTI | system |
| `question_abandoned` | Abandoned (never completed) | teacher, system (timeout) |

### Guided Build Loop Events

| Event Type | Description | Actor Types |
|------------|-------------|-------------|
| `build_started` | Guided build started | system |
| `build_field_completed` | A field completed | teacher, ai_suggestion |
| `build_ai_suggestion_offered` | AI suggested content | ai_suggestion |
| `build_ai_suggestion_accepted` | Teacher accepted suggestion | teacher |
| `build_ai_suggestion_rejected` | Teacher rejected suggestion | teacher |
| `build_ai_suggestion_modified` | Teacher modified suggestion | teacher |
| `build_iteration_complete` | An iteration complete | system |
| `build_completed` | Guided build finished | system |
| `build_abandoned` | Guided build cancelled | teacher |

### Validation Loop Events

| Event Type | Description | Actor Types |
|------------|-------------|-------------|
| `validation_started` | Validation started | system |
| `validation_passed` | All validations passed | auto_validation |
| `validation_failed` | Validation failed | auto_validation |
| `validation_error_fixed` | Error corrected | teacher, ai_suggestion |
| `validation_warning_acknowledged` | Warning deliberately ignored | teacher |
| `validation_abandoned` | Gave up after repeated errors | teacher |

### Review Loop Events

| Event Type | Description | Actor Types |
|------------|-------------|-------------|
| `review_started` | QA review started | teacher |
| `review_issue_found` | Problem identified | teacher |
| `review_returned_to_build` | Sent back to generation | teacher |
| `review_approved` | Approved in review | teacher |
| `review_abandoned` | Abandoned in review | teacher |

---

## State Machine: Question Lifecycle

```
                                    ┌─────────────┐
                                    │  ABANDONED  │
                                    └─────────────┘
                                          ▲
                    ┌─────────────────────┼─────────────────────┐
                    │                     │                     │
                    │                     │                     │
┌───────┐     ┌─────┴─────┐     ┌────────┴────────┐     ┌──────┴──────┐
│ DRAFT │────►│  GUIDED   │────►│   VALIDATING    │────►│   REVIEW    │
└───────┘     │   BUILD   │◄────│                 │◄────│             │
              └───────────┘     └─────────────────┘     └─────────────┘
                    │                                         │
                    │         ┌─────────────┐                 │
                    │         │  FINALIZED  │◄────────────────┘
                    │         └─────────────┘
                    │               │
                    │               ▼
                    │         ┌─────────────┐
                    └────────►│  EXPORTED   │
                              └─────────────┘

Arrows:
───► Normal progression
◄─── Loop back (validation failed, review issue)
- - - Abandonment (can occur from all stages)
```

---

## Loop Tracking

### Guided Build Loop

```
iteration 1:
  ├── build_started
  ├── build_ai_suggestion_offered (question_text)
  ├── build_ai_suggestion_accepted
  ├── build_field_completed (question_text)
  ├── build_ai_suggestion_offered (options)
  ├── build_ai_suggestion_rejected  ◄── Teacher doesn't want this
  └── [iteration 1 incomplete]

iteration 2:
  ├── build_ai_suggestion_offered (options - new variant)
  ├── build_ai_suggestion_modified ◄── Teacher edited
  ├── build_field_completed (options)
  ├── build_field_completed (answer)
  ├── build_field_completed (feedback)
  ├── build_iteration_complete
  └── build_completed ◄── All fields complete
```

### Validation Loop

```
attempt 1:
  ├── validation_started
  ├── validation_failed
  │   └── errors: ["Missing correct answer", "Distractor too similar"]
  └── [back to build or manual fix]

attempt 2:
  ├── validation_error_fixed (actor: teacher)
  ├── validation_started
  ├── validation_failed
  │   └── errors: ["Distractor too similar"]
  └── [still problems]

attempt 3:
  ├── validation_error_fixed (actor: ai_suggestion)
  ├── validation_started
  └── validation_passed ◄── Finally!
```

---

## Snapshot Content Schema

```json
{
  "question_text": "Which process...",
  "question_type": "multiple_choice_single",
  
  "options": [
    {"letter": "A", "text": "Mitosis", "is_correct": false},
    {"letter": "B", "text": "Meiosis", "is_correct": true},
    {"letter": "C", "text": "Cytokinesis", "is_correct": false},
    {"letter": "D", "text": "Apoptosis", "is_correct": false}
  ],
  
  "correct_answer": "B",
  
  "feedback": {
    "general": "...",
    "correct": "...",
    "incorrect": "..."
  },
  
  "metadata": {
    "points": 1,
    "language": "sv",
    "labels": ["#genetics", "#cell-division"],
    "custom_metadata": {}
  },
  
  "pedagogical": {
    "learning_objective": "LO_3.2",
    "bloom_level": "understand",
    "difficulty": "medium",
    "misconception_targeted": "Confusion between mitosis/meiosis"
  }
}
```

---

## Abandonment Tracking

### When is abandonment registered?

1. **Explicit abandonment** - Teacher clicks "Cancel" or "Discard question"
2. **Session timeout** - No activity for X minutes + session closed
3. **Session closed without completion** - Browser closed mid-work

### What is saved on abandonment?

```sql
-- In events table
INSERT INTO events (
    question_id,
    event_type,
    actor_type,
    stage_before,
    abandonment_reason,
    loop_type,
    loop_iteration,
    snapshot_before_id
) VALUES (
    '...',
    'question_abandoned',
    'teacher',
    'validating',
    'Repeated validation failures - gave up after 4 attempts',
    'validation',
    4,
    '...'
);
```

### ML Value of Abandonment Data

- **Pattern:** "Questions abandoned after 3+ validation failures"
- **Pattern:** "Question types that are often abandoned" 
- **Pattern:** "Bloom levels that are difficult to generate"
- **Pattern:** "Which AI suggestions lead to abandonment"

---

## ML Export Format

### JSONL for Training Data

```jsonl
{"type": "question_lifecycle", "question_id": "...", "session_id": "...", "question_type": "multiple_choice_single", "bloom_level": "understand", "outcome": "completed", "iterations": 3, "validation_attempts": 2, "snapshots": [...], "events": [...]}
{"type": "question_lifecycle", "question_id": "...", "session_id": "...", "question_type": "text_entry", "bloom_level": "apply", "outcome": "abandoned", "iterations": 5, "validation_attempts": 4, "abandonment_stage": "validating", "snapshots": [...], "events": [...]}
```

### Export Query

```sql
-- Export all questions with complete history
SELECT 
    q.id,
    q.question_type,
    q.bloom_level,
    q.current_stage,
    q.total_iterations,
    q.validation_attempts,
    q.validation_failures,
    q.abandoned_at IS NOT NULL as was_abandoned,
    s.course_code,
    s.assessment_type,
    json_agg(DISTINCT e.*) as events,
    json_agg(DISTINCT sn.*) as snapshots
FROM questions q
JOIN sessions s ON q.session_id = s.id
LEFT JOIN events e ON e.question_id = q.id
LEFT JOIN snapshots sn ON sn.question_id = q.id
GROUP BY q.id, s.course_code, s.assessment_type;
```

---

## MCP-Specific Logging

### qf-scaffolding (Methodology)

Logs at **session** level:
- Which modules (M1-M4) were completed
- Stage gates that were passed
- Time per module
- Decisions that were made

**Does NOT need PostgreSQL** - can be simple markdown/JSON in project folder.

### qf-pipeline (Question Generation)

Logs at **question** level (this document):
- All events, snapshots, loops
- **REQUIRES PostgreSQL** for ML training

### Separation Principle

```
┌─────────────────────────────────────────────────────────────────┐
│                    Session (qf-scaffolding)                      │
│   Logged: Markdown in project folder                             │
│   Purpose: Teacher's process documentation                       │
├─────────────────────────────────────────────────────────────────┤
│   ┌─────────────────────────────────────────────────────────┐   │
│   │              Question Pipeline (qf-pipeline)             │   │
│   │   Logged: PostgreSQL                                     │   │
│   │   Purpose: ML training data + traceability               │   │
│   │                                                          │   │
│   │   question_1: [events...] [snapshots...]                 │   │
│   │   question_2: [events...] [snapshots...]                 │   │
│   │   question_3: [events...] [snapshots...]                 │   │
│   └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Roadmap

### Phase 1: Basic Logging (Now)
- [ ] PostgreSQL schema setup
- [ ] Basic event logging (create, modify, finalize)
- [ ] Snapshot creation
- [ ] Session tracking

### Phase 2: Loop Tracking (Soon)
- [ ] Guided Build loop events
- [ ] Validation loop events
- [ ] Loop iteration counting
- [ ] Actor differentiation

### Phase 3: Abandonment (Next)
- [ ] Explicit abandonment capture
- [ ] Session timeout detection
- [ ] Abandonment reason logging

### Phase 4: ML Export (Future)
- [ ] JSONL export functionality
- [ ] Aggregation queries
- [ ] Data anonymisation (if central server)
- [ ] Training pipeline integration

---

## Decided Configurations

| Parameter | Decision | Date |
|-----------|----------|------|
| Session timeout | **30 minutes** without activity = abandoned | 2026-01-05 |
| Snapshot frequency | **At EVERY event** (not just stage change) | 2026-01-05 |
| qf-scaffolding logging | **Separate** (markdown in project folder, NOT PostgreSQL) | 2026-01-05 |
| Data retention | Permanent locally, anonymised on central export | 2026-01-05 |

---

## Related Logging (Other Systems)

### Assessment MCP - Document-level Metadata

Assessment files (Q-files) have their own YAML frontmatter to track the assessment process:

```yaml
---
ASSESSMENT-STATUS:
  File: "Q001_all_students.md"
  Question: "Question 001: Global Warming Potential (GWP)"
  Max-points: 3
  Total-students: 18
  Last-assessed-student: "NatSur2000"
  Last-assessed-index: 12
  Progress: "13/18 (72.22%)"
  Date: "2026-01-01"
  Rubric-file: null
---
```

**Purpose:** Track where the teacher is in the assessment process  
**Handled by:** Assessment MCP (separate project)  
**Status:** Separate specification needed

---

*Logging Specification v1.0 | QuestionForge | 2026-01-05*
