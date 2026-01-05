# QuestionForge qf-pipeline - Implementation Handoff

**Datum:** 2026-01-05  
**Syfte:** Handoff till Claude Code för implementation  
**ACDM Status:** EXPLORE ✅ → IMPLEMENT ⬜

---

## Vad som är klart (EXPLORE)

Alla specifikationer finns i `QuestionForge/docs/specs/`:

| Fil | Innehåll |
|-----|----------|
| `qf-pipeline-spec.md` | MCP-verktyg, 4-stegs pipeline |
| `qf-pipeline-wrapper-spec.md` | Hur wrappers kopplar till QTI-Generator |
| `qf-logging-specification.md` | PostgreSQL schema, events, loops |
| `qf-specifications-structure.md` | Delad specs-mapp struktur |
| `mqg-to-questionforge-migration.md` | MQG → QuestionForge mappning |

---

## Implementation Prioritering

### Fas 1: Step 4 Export (BÖRJA HÄR)

**Varför först?** Enklast, wrappar direkt befintlig kod, ger omedelbart värde.

**Att implementera:**

1. **Projektstruktur**
   ```
   qf-pipeline/
   ├── pyproject.toml
   ├── src/
   │   └── qf_pipeline/
   │       ├── __init__.py
   │       ├── server.py          # MCP server
   │       ├── wrappers/
   │       │   ├── __init__.py    # Python path config
   │       │   ├── parser.py      # Wrap MarkdownQuizParser
   │       │   ├── generator.py   # Wrap XMLGenerator
   │       │   ├── packager.py    # Wrap QTIPackager
   │       │   └── validator.py   # Wrap validate_content
   │       └── tools/
   │           └── export.py      # MCP tool: export_questions
   └── tests/
   ```

2. **Wrappers** (se `qf-pipeline-wrapper-spec.md` för detaljer)
   - `parser.py`: `parse_markdown(content) -> dict`
   - `generator.py`: `generate_xml(question, language) -> str`
   - `packager.py`: `create_qti_package(xml_list, metadata, output) -> dict`

3. **MCP Tool: export_questions**
   ```python
   # Input: markdown_path, output_path, language
   # Output: {zip_path, folder_path, question_count}
   ```

### Fas 2: PostgreSQL + Loggning

**Att implementera:**

1. **Schema setup** (se `qf-logging-specification.md`)
   - `sessions` tabell
   - `questions` tabell
   - `events` tabell
   - `snapshots` tabell

2. **Loggningsfunktioner**
   - `log_event(question_id, event_type, actor, ...)`
   - `create_snapshot(question_id, content)`
   - `get_question_history(question_id)`

### Fas 3: Step 2 Validator

**Att implementera:**

1. **Wrapper** för `validate_mqg_format.py`
2. **MCP Tools:**
   - `validate_file(path) -> {valid, issues}`
   - `validate_question(content) -> {valid, issues}`
3. **Loggning:** `validation_started`, `validation_passed`, `validation_failed`

### Fas 4: Step 1 Guided Build (SIST - mest komplex)

**Att implementera:**

1. **Session-hantering**
2. **Interaktiv loop**
3. **AI-förslag integration**
4. **Full loggning med alla event-typer**

---

## Beroenden

### QTI-Generator-for-Inspera

**Plats:** `/Users/niklaskarlsson/QTI-Generator-for-Inspera`

**Klasser att wrappa:**
- `src/parser/markdown_parser.py` → `MarkdownQuizParser`
- `src/generator/xml_generator.py` → `XMLGenerator`
- `src/packager/qti_packager.py` → `QTIPackager`
- `validate_mqg_format.py` → `validate_content()`

**Python path setup:**
```python
import sys
from pathlib import Path
QTI_GENERATOR_PATH = '/Users/niklaskarlsson/QTI-Generator-for-Inspera'
if QTI_GENERATOR_PATH not in sys.path:
    sys.path.insert(0, QTI_GENERATOR_PATH)
```

### PostgreSQL

**Lokal installation krävs.**

```bash
# macOS
brew install postgresql
brew services start postgresql
createdb questionforge
```

---

## Beslutade konfigurationer

| Parameter | Värde |
|-----------|-------|
| Session timeout | 30 minuter |
| Snapshot frekvens | Vid VARJE event |
| Default language | `sv` |
| Database | PostgreSQL (lokal) |

---

## Testa implementation

### Minimal test för Fas 1

```python
# test_export.py
from qf_pipeline.wrappers.parser import parse_markdown
from qf_pipeline.wrappers.generator import generate_all_xml
from qf_pipeline.wrappers.packager import create_qti_package

# 1. Parse
with open('test_quiz.md') as f:
    data = parse_markdown(f.read())

# 2. Generate
xml_list = generate_all_xml(data['questions'], language='sv')

# 3. Package
result = create_qti_package(xml_list, data['metadata'], 'test_output.zip')
print(f"Created: {result['zip_path']}")
```

---

## Filer att skapa i Claude Code

### Första sessionen (Fas 1)

1. `qf-pipeline/pyproject.toml`
2. `qf-pipeline/src/qf_pipeline/__init__.py`
3. `qf-pipeline/src/qf_pipeline/wrappers/__init__.py`
4. `qf-pipeline/src/qf_pipeline/wrappers/parser.py`
5. `qf-pipeline/src/qf_pipeline/wrappers/generator.py`
6. `qf-pipeline/src/qf_pipeline/wrappers/packager.py`
7. `qf-pipeline/src/qf_pipeline/server.py` (MCP server stub)
8. `qf-pipeline/tests/test_wrappers.py`

### Andra sessionen (Fas 2)

1. `qf-pipeline/db/schema.sql`
2. `qf-pipeline/src/qf_pipeline/db/__init__.py`
3. `qf-pipeline/src/qf_pipeline/db/models.py`
4. `qf-pipeline/src/qf_pipeline/db/logging.py`

---

## Relaterade dokument (läs vid behov)

| Dokument | Läs för |
|----------|---------|
| `qf-pipeline-wrapper-spec.md` | Detaljerad wrapper-design |
| `qf-logging-specification.md` | PostgreSQL schema + events |
| `PARKED_assessment_mcp_logging.md` | Assessment MCP (framtida) |

---

*Handoff skapad 2026-01-05*  
*Klar för Claude Code implementation*
