# Assessment MCP - Loggningsspecifikation (Framtida ACDM)

**Status:** PARKERAD - Fullständigt dokumenterad för framtida implementation  
**Prioritet:** Efter QuestionForge qf-pipeline  
**Dokumenterad:** 2026-01-05  
**Baserat på:** QuestionForge loggningsdiskussion

---

## Sammanfattning

Detta dokument innehåller den kompletta designen för Assessment MCP-loggning, baserat på samma principer som utvecklades för QuestionForge. Dokumentet är redo att användas som utgångspunkt för en ACDM-cykel när Assessment MCP-loggning ska implementeras.

---

## Del 1: Nuvarande Implementation

### Q-fil YAML Frontmatter

Assessment MCP använder redan YAML frontmatter i Q-filer för grundläggande process-spårning:

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

### Vad detta spårar idag

| Fält | Syfte |
|------|-------|
| File | Identifierar Q-filen |
| Question | Frågans rubrik |
| Max-points | Maxpoäng för frågan |
| Total-students | Antal elever att bedöma |
| Last-assessed-student | Senast bedömda eleven |
| Last-assessed-index | Position i listan |
| Progress | Procent färdigt |
| Date | Senaste bedömningsdatum |
| Rubric-file | Referens till bedömningsanvisningar |

### Begränsningar med nuvarande implementation

1. **Ingen historik** - Bara senaste status, inte hur vi kom dit
2. **Ingen aktörsspårning** - Vem gjorde vad?
3. **Ingen ML-data** - Kan inte träna modeller på bedömningsmönster
4. **Ingen loop-spårning** - Om läraren ändrar en bedömning, syns inte det
5. **Ingen abandonment-data** - Vet inte vilka bedömningar som övergavs

---

## Del 2: Föreslagen PostgreSQL-implementation

### Designprinciper (samma som QuestionForge)

1. **Lokal först** - PostgreSQL körs lokalt hos varje lärare
2. **Snapshot vid VARJE event** - Full spårbarhet
3. **Aktör alltid noterad** - Lärare / AI-förslag / System
4. **Abandonment spåras** - Värdefull data för analys
5. **ML-redo** - Strukturerad data för framtida träning
6. **30 minuters timeout** - Inaktivitet = session abandoned

### Databasschema

#### Tabell: assessment_sessions

```sql
CREATE TABLE assessment_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identifiering
    session_name VARCHAR(255) NOT NULL,
    q_file_path VARCHAR(500) NOT NULL,
    
    -- Kontext
    course_code VARCHAR(50),
    course_name VARCHAR(255),
    question_identifier VARCHAR(100),  -- 'Q001'
    question_title VARCHAR(500),
    max_points DECIMAL(5,2),
    
    -- Elev-information
    total_students INTEGER NOT NULL,
    assessed_count INTEGER DEFAULT 0,
    
    -- Tidsstämplar
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,  -- NULL = pågående/abandoned
    abandoned_at TIMESTAMP WITH TIME ZONE,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',  -- 'active', 'completed', 'abandoned'
    
    -- Rubrik-referens
    rubric_file VARCHAR(500),
    rubric_version VARCHAR(50)
);

CREATE INDEX idx_asess_sessions_status ON assessment_sessions(status);
CREATE INDEX idx_asess_sessions_course ON assessment_sessions(course_code);
CREATE INDEX idx_asess_sessions_created ON assessment_sessions(created_at);
```

#### Tabell: student_assessments

```sql
CREATE TABLE student_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES assessment_sessions(id) ON DELETE CASCADE,
    
    -- Elev-identifiering
    student_id VARCHAR(100) NOT NULL,  -- 'AbdDua2002'
    student_index INTEGER NOT NULL,     -- Position i listan
    
    -- Elevsvar
    word_count INTEGER,
    answer_text TEXT,
    
    -- Bedömning
    current_version INTEGER DEFAULT 0,  -- 0 = ej bedömd ännu
    total_points DECIMAL(5,2),
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending',  
    -- 'pending', 'in_progress', 'completed', 'skipped', 'flagged'
    
    -- Tidsstämplar
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Flaggor
    is_flagged BOOLEAN DEFAULT FALSE,
    flag_reason TEXT,
    
    UNIQUE(session_id, student_id)
);

CREATE INDEX idx_student_asess_session ON student_assessments(session_id);
CREATE INDEX idx_student_asess_status ON student_assessments(status);
```

#### Tabell: assessment_events

```sql
CREATE TABLE assessment_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_assessment_id UUID REFERENCES student_assessments(id) ON DELETE CASCADE,
    
    -- Tidsstämpel
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Event-typ
    event_type VARCHAR(50) NOT NULL,
    
    -- Aktör
    actor_type VARCHAR(30) NOT NULL,  -- 'teacher', 'ai_suggestion', 'system'
    actor_detail TEXT,
    
    -- Bedömningsförändring
    points_before DECIMAL(5,2),
    points_after DECIMAL(5,2),
    
    -- Version
    version_before INTEGER,
    version_after INTEGER,
    
    -- Ändringsdetaljer
    change_summary JSONB,
    
    -- Referens till snapshots
    snapshot_before_id UUID,
    snapshot_after_id UUID
);

CREATE INDEX idx_asess_events_student ON assessment_events(student_assessment_id);
CREATE INDEX idx_asess_events_timestamp ON assessment_events(timestamp);
CREATE INDEX idx_asess_events_type ON assessment_events(event_type);
```

#### Tabell: assessment_snapshots

```sql
CREATE TABLE assessment_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_assessment_id UUID REFERENCES student_assessments(id) ON DELETE CASCADE,
    
    -- Version
    version INTEGER NOT NULL,
    
    -- Tidsstämpel
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Fullständig bedömning
    content JSONB NOT NULL,
    
    -- Hash för snabb jämförelse
    content_hash VARCHAR(64),
    
    UNIQUE(student_assessment_id, version)
);

CREATE INDEX idx_asess_snapshots_student ON assessment_snapshots(student_assessment_id);
```

### Snapshot Content Schema

```json
{
  "student_id": "AbdDua2002",
  "word_count": 59,
  
  "aspects": [
    {
      "name": "1a GWP-värden",
      "max_points": 1.0,
      "awarded_points": 1.0,
      "symbol": "✓",
      "requirement": "CO₂=1, CH₄≈28-30, N₂O=260-300",
      "student_performance": "✓ CO₂=1 ✓ CH₄=26-30 ✓ N₂O=260-300",
      "comment": null
    },
    {
      "name": "1b Tidshorisont",
      "max_points": 1.0,
      "awarded_points": 1.0,
      "symbol": "✓✓",
      "requirement": "Förklara 100-årsperspektiv",
      "student_performance": "compares green house gases over 100 yers of time",
      "comment": null
    },
    {
      "name": "1c Jämförelsesyfte",
      "max_points": 1.0,
      "awarded_points": 1.0,
      "symbol": "✓✓✓",
      "requirement": "Förklara varför GWP behövs",
      "student_performance": "enable consistent evaluation across fuel options...",
      "comment": null
    }
  ],
  
  "total_points": 3.0,
  "max_points": 3.0,
  
  "next_step": "Öva på att tillämpa GWP-värden i specifika bränslejämförelser.",
  
  "metadata": {
    "assessed_at": "2026-01-01T14:32:00Z",
    "time_spent_seconds": 45,
    "rubric_version": "v1.0"
  }
}
```

---

## Del 3: Event Types

### Session Events

| Event Type | Beskrivning | Actor Types |
|------------|-------------|-------------|
| `session_started` | Bedömningssession påbörjades | teacher |
| `session_completed` | Alla elever bedömda | system |
| `session_abandoned` | Session övergavs | teacher, system |
| `session_resumed` | Session återupptogs | teacher |

### Student Assessment Events

| Event Type | Beskrivning | Actor Types |
|------------|-------------|-------------|
| `assessment_started` | Började bedöma elev | teacher |
| `assessment_completed` | Bedömning färdig | teacher |
| `assessment_modified` | Bedömning ändrades | teacher |
| `assessment_skipped` | Eleven hoppades över | teacher |
| `assessment_flagged` | Markerad för granskning | teacher |
| `assessment_unflagged` | Flagga borttagen | teacher |

### AI-assisterad bedömning (framtida)

| Event Type | Beskrivning | Actor Types |
|------------|-------------|-------------|
| `ai_suggestion_offered` | AI föreslog bedömning | ai_suggestion |
| `ai_suggestion_accepted` | Lärare accepterade AI-förslag | teacher |
| `ai_suggestion_rejected` | Lärare avvisade AI-förslag | teacher |
| `ai_suggestion_modified` | Lärare modifierade AI-förslag | teacher |

---

## Del 4: State Machine

### Student Assessment Lifecycle

```
┌─────────┐     ┌─────────────┐     ┌───────────┐
│ PENDING │────►│ IN_PROGRESS │────►│ COMPLETED │
└─────────┘     └─────────────┘     └───────────┘
     │                │                    │
     │                │                    │
     ▼                ▼                    ▼
┌─────────┐     ┌───────────┐        ┌─────────┐
│ SKIPPED │     │  FLAGGED  │◄───────│(modify) │
└─────────┘     └───────────┘        └─────────┘
```

### Session Lifecycle

```
┌────────┐     ┌─────────────┐     ┌───────────┐
│ ACTIVE │────►│  COMPLETED  │     │ ABANDONED │
└────────┘     └─────────────┘     └───────────┘
     │                                    ▲
     │                                    │
     └────────────────────────────────────┘
              (30 min timeout)
```

---

## Del 5: ML-träningsdata

### Värdefulla mönster att samla

1. **Bedömningstid per aspekt** - Vilka aspekter tar längst tid?
2. **Ändringsfrevens** - Hur ofta ändras bedömningar?
3. **AI-acceptansgrad** - Hur ofta accepteras AI-förslag?
4. **Skip-mönster** - Vilka elever/svar hoppas över?
5. **Flaggmönster** - Vad triggar flaggning?
6. **Abandonment-mönster** - Var i processen ger lärare upp?

### Export-format (JSONL)

```jsonl
{"type": "student_assessment", "student_id": "...", "question_id": "Q001", "outcome": "completed", "total_points": 3.0, "max_points": 3.0, "time_spent": 45, "versions": 1, "ai_suggestions_offered": 0, "snapshots": [...], "events": [...]}
{"type": "student_assessment", "student_id": "...", "question_id": "Q001", "outcome": "flagged", "total_points": 2.0, "max_points": 3.0, "flag_reason": "Osäker på aspekt 1c", "snapshots": [...], "events": [...]}
```

---

## Del 6: Integration med Q-filer

### Synkronisering

PostgreSQL är "source of truth", men Q-filens YAML frontmatter uppdateras för bakåtkompatibilitet:

```python
def sync_to_qfile(session_id: UUID, q_file_path: str):
    """Synka PostgreSQL-status till Q-filens YAML frontmatter."""
    session = get_session(session_id)
    
    frontmatter = {
        'ASSESSMENT-STATUS': {
            'File': os.path.basename(q_file_path),
            'Question': session.question_title,
            'Max-points': float(session.max_points),
            'Total-students': session.total_students,
            'Last-assessed-student': get_last_assessed_student(session_id),
            'Last-assessed-index': get_last_assessed_index(session_id),
            'Progress': f"{session.assessed_count}/{session.total_students} ({100*session.assessed_count/session.total_students:.2f}%)",
            'Date': session.updated_at.strftime('%Y-%m-%d'),
            'Rubric-file': session.rubric_file
        }
    }
    
    update_qfile_frontmatter(q_file_path, frontmatter)
```

### När synkroniseras?

- Efter varje `assessment_completed` event
- Vid session start/resume
- Vid manuell "Spara"-action

---

## Del 7: Implementation Roadmap

### Fas 1: Databas Setup
- [ ] Skapa PostgreSQL schema
- [ ] Migrations-system
- [ ] Seed-data för testning

### Fas 2: Grundläggande Events
- [ ] Session-events (start, complete, abandon)
- [ ] Student assessment-events (start, complete, modify)
- [ ] Snapshot-skapande

### Fas 3: Q-fil Integration
- [ ] Läs befintlig frontmatter
- [ ] Synka till PostgreSQL vid session-start
- [ ] Synka tillbaka vid ändringar

### Fas 4: Avancerad Spårning
- [ ] Tidsmätning per aspekt
- [ ] Skip/flagg-hantering
- [ ] Abandonment-detektion (30 min timeout)

### Fas 5: ML Export
- [ ] JSONL export-funktion
- [ ] Aggregeringsqueries
- [ ] Anonymiseringslager

---

## Del 8: Konfiguration

### Beslutade parametrar (från QuestionForge-diskussion)

| Parameter | Värde | Motivering |
|-----------|-------|------------|
| Session timeout | 30 minuter | Balans mellan flexibilitet och datakvalitet |
| Snapshot frekvens | Vid VARJE event | Full spårbarhet för ML-träning |
| Databas | PostgreSQL (lokal) | Skalbart, ML-redo, JSON-stöd |
| Q-fil sync | Ja, bakåtkompatibel | Behåll befintlig workflow |

---

## Del 9: ACDM Checklista

När du startar ACDM-cykeln för Assessment MCP-loggning:

### DISCOVER
- [ ] Verifiera att detta dokument fortfarande är aktuellt
- [ ] Kartlägg eventuella ändringar i Assessment MCP sedan 2026-01-05
- [ ] Identifiera nya behov som tillkommit

### SHAPE
- [ ] Validera PostgreSQL-schemat mot aktuella behov
- [ ] Definiera exakta event-typer som behövs
- [ ] Besluta om AI-assisterad bedömning ska inkluderas

### DECIDE
- [ ] Bekräfta eller uppdatera konfigurationsparametrar
- [ ] Välj implementation approach (vertikal slice vs horisontell)
- [ ] Prioritera fas 1-5

### COORDINATE
- [ ] Planera integration med befintlig Assessment MCP-kod
- [ ] Identifiera beroenden till QuestionForge
- [ ] Tidplan

### EXPLORE
- [ ] Detaljspecificera API:er
- [ ] Designa migrationsväg för befintliga Q-filer

### IMPLEMENT
- [ ] Följ roadmap i Del 7
- [ ] Testa varje fas innan nästa

### DELIVER
- [ ] Migrera befintliga bedömningar (om önskat)
- [ ] Dokumentation för lärare
- [ ] ML-export verifierad

---

## Relaterade dokument

| Dokument | Plats | Relation |
|----------|-------|----------|
| QuestionForge Logging Spec | `QuestionForge/docs/specs/qf-logging-specification.md` | Samma principer |
| Assessment MCP kod | `assessment-mcp/` | Befintlig implementation |
| Q-fil exempel | Nextcloud | Format-referens |

---

*Fullständigt dokumenterad 2026-01-05*  
*Redo för framtida ACDM-cykel*  
*Nästa steg: Implementera efter QuestionForge qf-pipeline är klar*
