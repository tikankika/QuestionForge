# QuestionForge qf-pipeline - Implementation Handoff v6

**Datum:** 2026-01-06  
**Syfte:** Handoff till Claude Code för implementation  
**ACDM Status:** IMPLEMENT pågår

---

## UPPGIFT 1: Lägg till `init`-verktyg

### Problem som upptäcktes

Vid testning hoppade Claude över att fråga användaren om fil och mapp innan `step0_start` kördes. Detta bröt hela workflow:en.

### Lösning

Samma mönster som Assessment_suite: ett `init`-verktyg som Claude MÅSTE kalla först och som returnerar instruktioner.

**Referens:** `/Users/niklaskarlsson/AIED_EdTech_projects/Assessment_suite/packages/assessment-mcp/src/tools/init.ts`

### Tool Definition (server.py)

```python
Tool(
    name="init",
    description=(
        "CALL THIS FIRST! Returns critical instructions for using qf-pipeline. "
        "You MUST follow these instructions. "
        "ALWAYS ask user for source_file and output_folder BEFORE calling step0_start. "
        "NEVER use bash/cat/ls - MCP has full file access."
    ),
    inputSchema={
        "type": "object",
        "properties": {},
        "required": [],
    },
)
```

### Handler (server.py)

```python
async def handle_init() -> List[TextContent]:
    """Handle init tool call - return critical instructions."""
    
    instructions = """# QF-Pipeline - Kritiska Instruktioner

## REGLER (MÅSTE FÖLJAS)

1. **FRÅGA ALLTID användaren INNAN du kör step0_start:**
   - "Vilken markdown-fil vill du arbeta med?" (source_file)
   - "Var ska projektet sparas?" (output_folder)
   - Vänta på svar innan du fortsätter!

2. **ANVÄND INTE bash/cat/ls** - qf-pipeline har full filåtkomst

3. **SÄG ALDRIG "ladda upp filen"** - MCP kan läsa filer direkt

4. **FÖLJ PIPELINE-ORDNINGEN:**
   - step0_start → step2_validate → step4_export
   - Validera ALLTID innan export!

5. **OM VALIDERING MISSLYCKAS:**
   - Använd step2_read för att läsa filen
   - Hjälp användaren förstå och fixa felen
   - Validera igen efter fix

## STANDARD WORKFLOW

1. User: "Använd qf-pipeline" / "Exportera till QTI"
2. Claude: "Vilken markdown-fil vill du arbeta med?"
3. User: anger sökväg
4. Claude: "Var ska projektet sparas?"
5. User: anger output-mapp
6. Claude: [step0_start] → Skapar session
7. Claude: [step2_validate] → Validerar
8. Om valid: [step4_export] → Exporterar
   Om invalid: [step2_read] → Visa fel, hjälp fixa

## TILLGÄNGLIGA VERKTYG

- init: CALL THIS FIRST (denna instruktion)
- step0_start: Starta ny session eller ladda befintlig
- step0_status: Visa sessionstatus
- step2_validate: Validera markdown-fil
- step2_validate_content: Validera markdown-innehåll
- step2_read: Läs arbetsfilen för felsökning
- step4_export: Exportera till QTI-paket
- list_types: Lista stödda frågetyper (16 st)
"""
    
    return [TextContent(
        type="text",
        text=instructions
    )]
```

---

## UPPGIFT 2: Lägg till `step2_read`-verktyg

### Problem som upptäcktes

Vid testning kunde Claude validera filen men inte LÄSA den för att hjälpa fixa felen. Claude (Desktop) har inte filsystemåtkomst men MCP-verktygen har det.

### Lösning

Lägg till `step2_read` som läser arbetsfilen från aktiv session och returnerar innehållet.

### Tool Definition (server.py)

```python
Tool(
    name="step2_read",
    description=(
        "Read the working file content for inspection/fixing. "
        "Use when validation fails and you need to see the file to help fix errors. "
        "Requires active session."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "max_lines": {
                "type": "integer",
                "description": "Maximum number of lines to return (default: all)",
            },
            "start_line": {
                "type": "integer",
                "description": "Start reading from this line (1-indexed, default: 1)",
            },
        },
    },
)
```

### Handler (server.py)

```python
async def handle_step2_read(arguments: dict) -> List[TextContent]:
    """Handle step2_read tool call - read working file content."""
    session = get_current_session()
    
    if not session or not session.working_file:
        return [TextContent(
            type="text",
            text="Error: Ingen aktiv session. Kör step0_start först."
        )]
    
    working_file = Path(session.working_file)
    
    if not working_file.exists():
        return [TextContent(
            type="text",
            text=f"Error: Arbetsfilen finns inte: {working_file}"
        )]
    
    try:
        with open(working_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        start_line = arguments.get('start_line', 1) - 1  # Convert to 0-indexed
        max_lines = arguments.get('max_lines')
        
        if start_line < 0:
            start_line = 0
        
        if max_lines:
            selected_lines = lines[start_line:start_line + max_lines]
        else:
            selected_lines = lines[start_line:]
        
        content = ''.join(selected_lines)
        line_count = len(selected_lines)
        total_lines = len(lines)
        
        header = f"Fil: {working_file.name}\n"
        header += f"Visar rad {start_line + 1}-{start_line + line_count} av {total_lines}\n"
        header += "-" * 40 + "\n"
        
        return [TextContent(
            type="text",
            text=header + content
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: Kunde inte läsa filen: {e}"
        )]
```

### Registrera i call_tool

```python
elif name == "step2_read":
    return await handle_step2_read(arguments)
```

---

## Komplett verktygslista efter implementation

```
System:
  init                    # CALL THIS FIRST!

Step 0 (Session):
  step0_start             # Ny eller ladda session
  step0_status            # Visa status

Step 2 (Validator):
  step2_validate          # Validera fil
  step2_validate_content  # Validera innehåll
  step2_read              # Läs fil för felsökning

Step 4 (Export):
  step4_export            # Skapa QTI-paket

Cross-Step:
  list_types              # Frågetyper
```

**Totalt:** 9 verktyg

---

## Implementation steg

### För `init`:

1. Lägg till Tool i list_tools
2. Lägg till handler `handle_init()`
3. Registrera i call_tool

### För `step2_read`:

1. Lägg till Tool i list_tools
2. Lägg till handler `handle_step2_read(arguments)`
3. Registrera i call_tool

### Testa

```bash
# Starta MCP-server och verifiera:
# 1. init returnerar instruktioner inkl. step2_read
# 2. step2_read returnerar filinnehåll efter step0_start
```

---

## Förväntat beteende efter implementation

```
User: "Använd qf-pipeline"

Claude: [init] → Läser instruktioner

Claude: "Vilken markdown-fil vill du arbeta med?"

User: "/Users/.../BIOG001X_Fys_v65_5.md"

Claude: "Var ska projektet sparas?"

User: "/Users/.../test_projects/"

Claude: [step0_start] → "Session startad!"

Claude: [step2_validate] → "27 frågor, 22 fel (saknar ^labels)..."

Claude: [step2_read] → Läser filen

Claude: "Jag ser problemet. På rad 45 saknas ^labels. 
         Lägg till: ^labels: A, B, C, D
         Vill du att jag visar hur hela frågan ska se ut?"
```

---

## Filplacering

```
qf-pipeline/src/qf_pipeline/
├── tools/
│   ├── session.py      ← step0_start, step0_status (befintlig)
│   └── read.py         ← step2_read (NY FIL)
└── server.py           ← init handler + registrera tools
```

Alternativt kan `step2_read` läggas direkt i `server.py` tillsammans med `init` om det är enklare.

---

## Relaterade dokument

- `docs/adr/ADR-007-tool-naming-convention.md` - Verktygsnamn
- Assessment_suite referens: `/Assessment_suite/packages/assessment-mcp/src/tools/init.ts`

---

---

## UPPGIFT 3: Lägg till loggning

### Problem

Ingen spårbarhet av vad som händer i pipeline:n. Svårt att debugga och följa upp.

### Lösning

Enkel filbaserad loggning per projekt. Både human-readable och JSON-format.

### Filplacering

```
project_folder/
├── 01_source/
├── 02_working/
├── 03_output/
├── session.yaml
├── pipeline.log          ← Human-readable logg
└── pipeline.jsonl         ← Strukturerad logg (JSON Lines)
```

### Logger utility (`utils/logger.py`)

```python
import json
from pathlib import Path
from datetime import datetime, timezone


def log_action(
    project_path: Path,
    step: str,
    message: str,
    data: dict = None
):
    """
    Log action to both pipeline.log (human) and pipeline.jsonl (structured).
    
    Args:
        project_path: Project directory containing log files
        step: Tool/step name (e.g., "step0_start", "step2_validate")
        message: Human-readable message
        data: Optional structured data for JSON log
    """
    timestamp = datetime.now(timezone.utc)
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    timestamp_iso = timestamp.isoformat()
    
    # Human-readable log
    log_file = project_path / "pipeline.log"
    entry = f"{timestamp_str} [{step}] {message}\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)
    
    # Structured JSON log (JSON Lines format)
    jsonl_file = project_path / "pipeline.jsonl"
    json_entry = {
        "timestamp": timestamp_iso,
        "step": step,
        "message": message,
    }
    if data:
        json_entry["data"] = data
    
    with open(jsonl_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(json_entry, ensure_ascii=False) + "\n")
```

### Användning i handlers

```python
from ..utils.logger import log_action

async def handle_step0_start(arguments: dict):
    # ... skapa session ...
    
    log_action(
        project_path,
        "step0_start",
        f"Session created: {session_id}",
        data={
            "session_id": session_id,
            "source_file": str(source_file),
            "project_path": str(project_path),
        }
    )

async def handle_step2_validate(arguments: dict):
    # ... validera ...
    
    log_action(
        project_path,
        "step2_validate",
        f"Validated: {question_count} questions, {error_count} errors",
        data={
            "question_count": question_count,
            "error_count": error_count,
            "warning_count": warning_count,
            "valid": is_valid,
        }
    )

async def handle_step4_export(arguments: dict):
    # ... exportera ...
    
    log_action(
        project_path,
        "step4_export",
        f"Exported {question_count} questions to {zip_name}",
        data={
            "question_count": question_count,
            "output_file": str(zip_path),
            "file_size_bytes": zip_path.stat().st_size,
        }
    )
```

### Exempel: pipeline.log (human-readable)

```
2026-01-06 09:18:01 [init] Pipeline initialized
2026-01-06 09:18:05 [step0_start] Session created: b1c108d2-a78c-479a-ac36-604b86817f93
2026-01-06 09:18:10 [step2_validate] Validated: 27 questions, 22 errors
2026-01-06 09:18:15 [step2_read] Read lines 1-500
2026-01-06 09:20:30 [step4_export] Exported 27 questions to BIOG001X_Fys_v65_5_QTI.zip
```

### Exempel: pipeline.jsonl (structured)

```json
{"timestamp": "2026-01-06T09:18:01Z", "step": "init", "message": "Pipeline initialized"}
{"timestamp": "2026-01-06T09:18:05Z", "step": "step0_start", "message": "Session created", "data": {"session_id": "b1c108d2-...", "source_file": "/path/to/file.md"}}
{"timestamp": "2026-01-06T09:18:10Z", "step": "step2_validate", "message": "Validated", "data": {"question_count": 27, "error_count": 22, "valid": false}}
{"timestamp": "2026-01-06T09:20:30Z", "step": "step4_export", "message": "Exported", "data": {"question_count": 27, "output_file": "03_output/..._QTI.zip"}}
```

### Vilka steg ska loggas

| Steg | Vad loggas |
|------|------------|
| `init` | Pipeline initialized |
| `step0_start` | Session ID, source, project path |
| `step0_status` | (ingen logg - bara läsning) |
| `step2_validate` | Question count, errors, warnings, valid |
| `step2_read` | Lines read |
| `step4_export` | Question count, output file, size |

---

## Komplett verktygslista efter implementation

```
System:
  init                    # CALL THIS FIRST!

Step 0 (Session):
  step0_start             # Ny eller ladda session
  step0_status            # Visa status

Step 2 (Validator):
  step2_validate          # Validera fil
  step2_validate_content  # Validera innehåll
  step2_read              # Läs fil för felsökning

Step 4 (Export):
  step4_export            # Skapa QTI-paket

Cross-Step:
  list_types              # Frågetyper
```

**Totalt:** 9 verktyg + loggning

---

## Sammanfattning: 3 uppgifter

| # | Uppgift | Filer |
|---|---------|-------|
| 1 | `init` verktyg | `server.py` |
| 2 | `step2_read` verktyg | `server.py` eller `tools/read.py` |
| 3 | Loggning | `utils/logger.py` + uppdatera handlers |

---

## Relaterade dokument

- `docs/adr/ADR-007-tool-naming-convention.md` - Verktygsnamn
- Assessment_suite referens: `/Assessment_suite/packages/assessment-mcp/src/tools/init.ts`

---

*Handoff v7 - 2026-01-06*  
*Fokus: init + step2_read + loggning*
