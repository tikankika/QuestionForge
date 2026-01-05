# QuestionForge Logging Specification

**Version:** 1.0  
**Status:** Draft  
**Date:** 2026-01-05  
**Purpose:** Spårbarhet + ML-träningsdata

---

## Designprinciper

1. **Lokal först** - PostgreSQL körs lokalt hos varje lärare
2. **Alla loopar spåras** - Guided Build, Validation, Review
3. **Abandonerade sessioner loggas** - Värdefull ML-data
4. **Snapshots vid nyckelsteg** - Inte varje mikroändring
5. **Aktör alltid noterad** - Lärare / AI / Automatisk validering
6. **ML-redo från dag 1** - Strukturerad data för framtida träning

---

## PostgreSQL Schema

### Övergripande struktur

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

### Tabell: sessions

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identifiering
    session_name VARCHAR(255) NOT NULL,
    
    -- Kontext
    course_code VARCHAR(50),
    course_name VARCHAR(255),
    module_name VARCHAR(255),
    assessment_type VARCHAR(50),  -- 'quiz', 'exam', 'formative'
    
    -- Tidsstämplar
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,  -- NULL = pågående eller abandonerad
    abandoned_at TIMESTAMP WITH TIME ZONE,  -- NULL = inte abandonerad
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',  -- 'active', 'completed', 'abandoned'
    
    -- Metadata
    target_question_count INTEGER,
    actual_question_count INTEGER DEFAULT 0,
    
    -- Konfiguration som användes
    config JSONB  -- Blueprint, Bloom's distribution, etc.
);

CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_course ON sessions(course_code);
CREATE INDEX idx_sessions_created ON sessions(created_at);
```

### Tabell: questions

```sql
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    
    -- Identifiering
    question_identifier VARCHAR(100) NOT NULL,  -- 'MC_Q001'
    question_type VARCHAR(50) NOT NULL,         -- 'multiple_choice_single'
    
    -- Aktuell status
    current_stage VARCHAR(30) DEFAULT 'draft',
    -- Stages: 'draft', 'guided_build', 'validating', 'review', 'finalized', 'exported', 'abandoned'
    
    -- Senaste version
    current_version INTEGER DEFAULT 1,
    current_content JSONB,  -- Senaste snapshot
    
    -- Pedagogisk kontext
    learning_objective VARCHAR(255),
    bloom_level VARCHAR(20),
    difficulty VARCHAR(20),
    
    -- Tidsstämplar
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    finalized_at TIMESTAMP WITH TIME ZONE,
    exported_at TIMESTAMP WITH TIME ZONE,
    abandoned_at TIMESTAMP WITH TIME ZONE,
    
    -- Statistik
    total_iterations INTEGER DEFAULT 0,
    validation_attempts INTEGER DEFAULT 0,
    validation_failures INTEGER DEFAULT 0,
    
    -- Kvalitetsbedömning (optional, för ML)
    teacher_quality_score INTEGER,  -- 1-5 om läraren bedömer
    
    UNIQUE(session_id, question_identifier)
);

CREATE INDEX idx_questions_session ON questions(session_id);
CREATE INDEX idx_questions_stage ON questions(current_stage);
CREATE INDEX idx_questions_type ON questions(question_type);
CREATE INDEX idx_questions_bloom ON questions(bloom_level);
```

### Tabell: events

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
    
    -- Tidsstämpel
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Event-typ
    event_type VARCHAR(50) NOT NULL,
    -- Types: se EVENT_TYPES nedan
    
    -- Vem/vad orsakade eventet
    actor_type VARCHAR(30) NOT NULL,  -- 'teacher', 'ai_suggestion', 'auto_validation', 'system'
    actor_detail TEXT,                 -- Beskrivning av vad som hände
    
    -- Stage-förändring
    stage_before VARCHAR(30),
    stage_after VARCHAR(30),
    
    -- Version-förändring
    version_before INTEGER,
    version_after INTEGER,
    
    -- Loop-kontext
    loop_type VARCHAR(30),         -- 'guided_build', 'validation', 'review', NULL
    loop_iteration INTEGER,        -- Vilken iteration i loopen (1, 2, 3...)
    
    -- Ändringsdetaljer
    change_summary JSONB,
    -- Exempel: {"fields_changed": ["options[1].text"], "change_type": "distractor_improvement"}
    
    -- Valideringsresultat (om event_type = validation_*)
    validation_result JSONB,
    -- Exempel: {"passed": false, "errors": [...], "warnings": [...]}
    
    -- För abandoned events
    abandonment_reason TEXT,
    
    -- Referens till snapshots
    snapshot_before_id UUID,
    snapshot_after_id UUID
);

CREATE INDEX idx_events_question ON events(question_id);
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_actor ON events(actor_type);
CREATE INDEX idx_events_loop ON events(loop_type, loop_iteration);
```

### Tabell: snapshots

```sql
CREATE TABLE snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
    
    -- Version
    version INTEGER NOT NULL,
    
    -- Tidsstämpel
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Fullständigt innehåll
    content JSONB NOT NULL,
    -- Innehåller: question_text, options, correct_answer, feedback, metadata, etc.
    
    -- Hashvärde för snabb jämförelse
    content_hash VARCHAR(64),
    
    UNIQUE(question_id, version)
);

CREATE INDEX idx_snapshots_question ON snapshots(question_id);
CREATE INDEX idx_snapshots_version ON snapshots(question_id, version);
```

---

## Event Types

### Lifecycle Events

| Event Type | Beskrivning | Actor Types |
|------------|-------------|-------------|
| `question_created` | Fråga skapades (första draft) | teacher, ai_suggestion |
| `question_modified` | Fråga ändrades | teacher, ai_suggestion |
| `question_finalized` | Markerad som klar | teacher |
| `question_exported` | Exporterad till QTI | system |
| `question_abandoned` | Övergavs (aldrig klar) | teacher, system (timeout) |

### Guided Build Loop Events

| Event Type | Beskrivning | Actor Types |
|------------|-------------|-------------|
| `build_started` | Guided build påbörjades | system |
| `build_field_completed` | Ett fält färdigställt | teacher, ai_suggestion |
| `build_ai_suggestion_offered` | AI föreslog innehåll | ai_suggestion |
| `build_ai_suggestion_accepted` | Lärare accepterade förslag | teacher |
| `build_ai_suggestion_rejected` | Lärare avvisade förslag | teacher |
| `build_ai_suggestion_modified` | Lärare modifierade förslag | teacher |
| `build_iteration_complete` | En iteration klar | system |
| `build_completed` | Guided build avslutad | system |
| `build_abandoned` | Guided build avbruten | teacher |

### Validation Loop Events

| Event Type | Beskrivning | Actor Types |
|------------|-------------|-------------|
| `validation_started` | Validering påbörjades | system |
| `validation_passed` | Alla valideringar passerade | auto_validation |
| `validation_failed` | Validering misslyckades | auto_validation |
| `validation_error_fixed` | Fel korrigerades | teacher, ai_suggestion |
| `validation_warning_acknowledged` | Varning ignorerades medvetet | teacher |
| `validation_abandoned` | Gav upp efter upprepade fel | teacher |

### Review Loop Events

| Event Type | Beskrivning | Actor Types |
|------------|-------------|-------------|
| `review_started` | QA-granskning påbörjades | teacher |
| `review_issue_found` | Problem identifierades | teacher |
| `review_returned_to_build` | Skickades tillbaka till generation | teacher |
| `review_approved` | Godkänd i granskning | teacher |
| `review_abandoned` | Övergavs i granskning | teacher |

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

Pilar:
───► Normal progression
◄─── Loop tillbaka (validation failed, review issue)
- - - Abandonment (kan ske från alla stages)
```

---

## Loop-spårning

### Guided Build Loop

```
iteration 1:
  ├── build_started
  ├── build_ai_suggestion_offered (question_text)
  ├── build_ai_suggestion_accepted
  ├── build_field_completed (question_text)
  ├── build_ai_suggestion_offered (options)
  ├── build_ai_suggestion_rejected  ◄── Läraren vill inte ha detta
  └── [iteration 1 incomplete]

iteration 2:
  ├── build_ai_suggestion_offered (options - ny variant)
  ├── build_ai_suggestion_modified ◄── Läraren editerade
  ├── build_field_completed (options)
  ├── build_field_completed (answer)
  ├── build_field_completed (feedback)
  ├── build_iteration_complete
  └── build_completed ◄── Alla fält klara
```

### Validation Loop

```
attempt 1:
  ├── validation_started
  ├── validation_failed
  │   └── errors: ["Missing correct answer", "Distractor too similar"]
  └── [tillbaka till build eller manuell fix]

attempt 2:
  ├── validation_error_fixed (actor: teacher)
  ├── validation_started
  ├── validation_failed
  │   └── errors: ["Distractor too similar"]
  └── [fortfarande problem]

attempt 3:
  ├── validation_error_fixed (actor: ai_suggestion)
  ├── validation_started
  └── validation_passed ◄── Äntligen!
```

---

## Snapshot Content Schema

```json
{
  "question_text": "Vilken process...",
  "question_type": "multiple_choice_single",
  
  "options": [
    {"letter": "A", "text": "Mitos", "is_correct": false},
    {"letter": "B", "text": "Meios", "is_correct": true},
    {"letter": "C", "text": "Cytokinesis", "is_correct": false},
    {"letter": "D", "text": "Apoptos", "is_correct": false}
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
    "misconception_targeted": "Förväxling mitos/meios"
  }
}
```

---

## Abandonment Tracking

### När registreras abandonment?

1. **Explicit abandonment** - Lärare klickar "Avbryt" eller "Släng fråga"
2. **Session timeout** - Ingen aktivitet på X minuter + session stängd
3. **Session closed without completion** - Browser stängd mitt i arbete

### Vad sparas vid abandonment?

```sql
-- I events-tabellen
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

### ML-värde av abandonment-data

- **Pattern:** "Frågor som överges efter 3+ valideringsfel"
- **Pattern:** "Frågetyper som ofta överges" 
- **Pattern:** "Bloom-nivåer som är svåra att generera"
- **Pattern:** "Vilka AI-förslag leder till abandonment"

---

## ML Export Format

### JSONL för träningsdata

```jsonl
{"type": "question_lifecycle", "question_id": "...", "session_id": "...", "question_type": "multiple_choice_single", "bloom_level": "understand", "outcome": "completed", "iterations": 3, "validation_attempts": 2, "snapshots": [...], "events": [...]}
{"type": "question_lifecycle", "question_id": "...", "session_id": "...", "question_type": "text_entry", "bloom_level": "apply", "outcome": "abandoned", "iterations": 5, "validation_attempts": 4, "abandonment_stage": "validating", "snapshots": [...], "events": [...]}
```

### Export Query

```sql
-- Exportera alla frågor med fullständig historik
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

## MCP-specifik loggning

### qf-scaffolding (Metodologi)

Loggar på **session**-nivå:
- Vilka moduler (M1-M4) genomfördes
- Stage gates som passerades
- Tid per modul
- Beslut som togs

**Behöver INTE PostgreSQL** - kan vara enkel markdown/JSON i projektmappen.

### qf-pipeline (Frågegenerering)

Loggar på **fråga**-nivå (detta dokument):
- Alla events, snapshots, loops
- **KRÄVER PostgreSQL** för ML-träning

### Separationsprincip

```
┌─────────────────────────────────────────────────────────────────┐
│                    Session (qf-scaffolding)                      │
│   Loggas: Markdown i projektmapp                                 │
│   Syfte: Lärarens process-dokumentation                          │
├─────────────────────────────────────────────────────────────────┤
│   ┌─────────────────────────────────────────────────────────┐   │
│   │              Question Pipeline (qf-pipeline)             │   │
│   │   Loggas: PostgreSQL                                     │   │
│   │   Syfte: ML-träningsdata + spårbarhet                    │   │
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
- [ ] Data anonymization (om central server)
- [ ] Training pipeline integration

---

## Beslutade konfigurationer

| Parameter | Beslut | Datum |
|-----------|--------|-------|
| Session timeout | **30 minuter** utan aktivitet = abandoned | 2026-01-05 |
| Snapshot frekvens | **Vid VARJE event** (inte bara stage-byte) | 2026-01-05 |
| qf-scaffolding loggning | **Separat** (markdown i projektmapp, INTE PostgreSQL) | 2026-01-05 |
| Data retention | Permanent lokalt, anonymiserat vid central export | 2026-01-05 |

---

## Relaterad loggning (Andra system)

### Assessment MCP - Dokument-nivå metadata

Assessment-filer (Q-filer) har egen YAML frontmatter för att spåra bedömningsprocessen:

```yaml
---
ASSESSMENT-STATUS:
  File: "Q001_alla_elever.md"
  Question: "Fråga 001: Global Warming Potential (GWP)"
  Max-points: 3
  Total-students: 18
  Last-assessed-student: "NatSur2000"
  Last-assessed-index: 12
  Progress: "13/18 (72.22%)"
  Date: "2026-01-01"
  Rubric-file: null
---
```

**Syfte:** Spåra var läraren är i bedömningsprocessen  
**Hanteras av:** Assessment MCP (separat projekt)  
**Status:** Separat specifikation behövs

---

*Logging Specification v1.0 | QuestionForge | 2026-01-05*
