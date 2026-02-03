# ADR-006: Session Management för qf-pipeline

## Status
**Proposed** → Pending implementation

## Datum
2026-01-05

## Kontext

qf-pipeline (QuestionForge pipeline MCP) byggdes initialt med fokus på export-funktionalitet. Vid testning upptäcktes att:

1. **Filåtkomst saknas** - MCP-servern kunde inte läsa filer från användarens lokala filsystem
2. **Ingen arbetskopia** - Användaren kunde inte redigera filer utan att påverka originalet
3. **Ingen projektstruktur** - Export skedde utan organiserad mappstruktur

### Referensimplementation

Assessment_suite/pre-assessment-mcp har ett beprövat mönster:
- `phase1_explore` - Skannar och identifierar filer
- `phase1_setup` - Skapar projektstruktur, kopierar filer

Se: `/path/to/assessment-suite/packages/pre-assessment-mcp/src/pre_assessment_mcp/tools/`

## Beslut

Implementera session management i qf-pipeline med följande komponenter:

### Nytt verktyg: `start_session`

```python
start_session(
    source_file: str,      # Sökväg till markdown-fil
    output_folder: str,    # Var projektet ska skapas
    project_name: str = None  # Valfritt, auto-generera från filnamn
) -> dict
```

**Returnerar:**
```json
{
  "success": true,
  "project_path": "/path/to/project",
  "working_file": "/path/to/project/02_working/file.md",
  "session_id": "uuid",
  "message": "Session startad. Arbetar med: file.md"
}
```

### Projektmappstruktur

```
project_name/
├── 01_source/          ← Original (ALDRIG modifierad)
│   └── original_file.md
├── 02_working/         ← Arbetskopia (kan redigeras)
│   └── original_file.md
├── 03_output/          ← Exporterade filer
│   └── (QTI-paket, ZIP-filer)
└── session.yaml        ← Metadata och state
```

### session.yaml schema

```yaml
session:
  id: "uuid"
  created: "2026-01-05T23:30:00Z"
  updated: "2026-01-05T23:45:00Z"
  
source:
  original_path: "/Users/.../EXAMPLE_COURSE_Fys_v65_5.md"
  filename: "EXAMPLE_COURSE_Fys_v65_5.md"
  copied_to: "01_source/EXAMPLE_COURSE_Fys_v65_5.md"
  
working:
  path: "02_working/EXAMPLE_COURSE_Fys_v65_5.md"
  last_validated: "2026-01-05T23:35:00Z"
  validation_status: "valid"
  question_count: 27
  
exports:
  - timestamp: "2026-01-05T23:45:00Z"
    output_file: "03_output/EXAMPLE_COURSE_Fys_QTI.zip"
    questions_exported: 27
```

### Uppdatering av befintliga verktyg

| Verktyg | Förändring |
|---------|------------|
| `validate_file` | Accepterar absolut sökväg ELLER relativ inom session |
| `export_questions` | Skriver till 03_output/ om session aktiv |
| `parse_markdown` | Oförändrad (fungerar redan) |

## Konsekvenser

### Positiva
- Användaren kan arbeta med lokala filer
- Original bevaras alltid (01_source)
- Arbetskopia kan redigeras fritt
- Tydlig separation: input → arbete → output
- Metadata spårar sessionen

### Negativa
- Extra steg: måste starta session innan arbete
- Mer kod att underhålla
- Projektmappar skapas (tar diskutrymme)

### Neutrala
- Följer etablerat mönster från pre-assessment-mcp
- Konsekvent med Assessment_suite arkitektur

## Alternativ som övervägdes

### A: Endast filläsning (ingen session)
- Enklare implementation
- Men: ingen arbetskopia, ingen struktur
- **Avvisat:** För begränsat för produktionsanvändning

### B: In-memory arbete
- Läs fil → arbeta i minnet → exportera
- Men: förlorar arbete vid krasch
- **Avvisat:** Riskabelt för större projekt

### C: Session management (valt)
- Inspirerat av pre-assessment-mcp
- Beprövat mönster
- **Valt:** Bäst balans mellan enkelhet och funktion

## Implementation

### Filer att skapa/uppdatera

```
packages/qf-pipeline/src/qf_pipeline/
├── tools/
│   └── session.py          ← NY: start_session, get_session_status
├── utils/
│   └── session_manager.py  ← NY: SessionManager klass
└── server.py               ← UPPDATERA: registrera nya verktyg
```

### Prioritet

Del av Fas 1.5 (efter grundläggande MCP fungerar, före PostgreSQL-loggning)

## Relaterade dokument

- [ADR-005: MCP Integration](ADR-005-mcp-integration.md)
- [qf-pipeline-spec.md](../specs/qf-pipeline-spec.md)
- [qf-logging-specification.md](../specs/qf-logging-specification.md) - Session-loggning integreras här senare

---

*Dokumenterat 2026-01-05 som del av ACDM IMPLEMENT-fasen*
