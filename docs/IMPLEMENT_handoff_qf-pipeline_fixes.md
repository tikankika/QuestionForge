# IMPLEMENT HANDOFF: qf-pipeline Fixes

**Status:** ✅ COMPLETED (Resource handling already implemented)
**Date:** 2026-01-06
**Updated:** 2026-01-16
**Target:** Claude Code
**Priority Order:** ADR-009 (CRITICAL) → ADR-008 (Medium)

> **NOTE:** Resource handling (ADR-009) was found to be ALREADY IMPLEMENTED in server.py lines 1051-1134. The handoff was outdated.

---

## PRIORITET 1: ✅ Resource Handling (REDAN KLART)

**ADR:** ADR-009-resource-handling.md

### ~~Problem~~ LÖST

~~`resources.py` wrapper finns men anropas ALDRIG i `step4_export`. Bilder kopieras inte till QTI-paketet.~~

**Status:** REDAN IMPLEMENTERAT i `server.py` lines 1051-1134:
- `validate_resources()` kallas och loggar varningar
- `copy_resources()` kopierar bilder till output
- Return message inkluderar `{resource_count} filer kopierade`

### Fix: Modifiera `server.py`

```python
# I server.py, lägg till import högst upp (om inte redan finns):
from .wrappers import (
    # ... existing imports ...
    validate_resources,
    copy_resources,
)
```

```python
# I handle_step4_export(), FÖRE "xml_list = generate_all_xml()":

# === NEW: Resource handling ===

# 1. Validate resources exist
resource_result = validate_resources(
    input_file=file_path,
    questions=questions,
    media_dir=None,  # Auto-detect
    strict=False
)

# Log warnings but continue
if resource_result.get("warning_count", 0) > 0:
    for issue in resource_result.get("issues", []):
        if issue.get("level") == "WARNING":
            if session:
                log_action(session.project_path, "step4_export", 
                          f"Resource warning: {issue.get('message')}")

# Fail on errors
if resource_result.get("error_count", 0) > 0:
    error_msgs = [i.get("message") for i in resource_result.get("issues", []) 
                  if i.get("level") == "ERROR"]
    return [TextContent(
        type="text",
        text=f"Resource-fel:\n" + "\n".join(f"  - {m}" for m in error_msgs) +
             "\n\nFixa bilderna och kör igen."
    )]

# 2. Prepare output structure
output_folder = session.output_folder if session else Path(output_path).parent

# 3. Copy resources to output
copy_result = copy_resources(
    input_file=file_path,
    output_dir=str(output_folder),
    questions=questions
)

resource_count = copy_result.get("count", 0)

# === END NEW ===

# Continue with existing XML generation...
xml_list = generate_all_xml(questions, language)
```

```python
# Uppdatera return-meddelandet för att inkludera resource-info:

return [TextContent(
    type="text",
    text=f"QTI-paket skapat!\n"
         f"  ZIP: {result.get('zip_path')}\n"
         f"  Mapp: {result.get('folder_path')}\n"
         f"  Frågor: {len(questions)}\n"
         f"  Resurser: {resource_count} filer kopierade"  # NEW
)]
```

### Test

```bash
# Skapa test-markdown med bild:
echo '---
title: Test med bild
---

## Q1
ID: TEST_IMG_001
Type: multiple_choice_single
Points: 1

![Test](test_image.png)

Vad visar bilden?

- [x] Rätt svar
- [ ] Fel svar
' > /tmp/test_with_image.md

# Skapa dummy-bild
touch /tmp/test_image.png

# Testa export via MCP
```

### Verifiering

1. Kör `step4_export` på fil med bilder
2. Öppna skapad ZIP
3. Verifiera att bildfilerna finns i paketet
4. Importera till Inspera och verifiera att bilder visas

---

## PRIORITET 2: 🟡 list_projects Tool

**ADR:** ADR-008-project-configuration-location.md

### Skapa ny fil: `src/qf_pipeline/utils/config.py`

```python
"""Project configuration utilities.

Reads MQG folder configuration from QTI-Generator or environment.
"""

import json
import os
from pathlib import Path
from typing import List

from ..wrappers import QTI_GENERATOR_PATH


class ConfigError(Exception):
    """Configuration-related errors."""
    pass


def get_config_path() -> Path:
    """Get path to mqg_folders.json configuration."""
    # 1. Check environment variable
    env_path = os.environ.get("QF_PROJECTS_CONFIG")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path
    
    # 2. Fall back to QTI-Generator location
    qti_config = QTI_GENERATOR_PATH / "config" / "mqg_folders.json"
    if qti_config.exists():
        return qti_config
    
    raise ConfigError(
        "Ingen projektkonfiguration hittad. Antingen:\n"
        "  1. Sätt QF_PROJECTS_CONFIG miljövariabel, eller\n"
        "  2. Se till att QTI-Generator config finns på:\n"
        f"     {qti_config}"
    )


def load_config() -> dict:
    """Load project configuration."""
    config_path = get_config_path()
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"Ogiltig JSON i {config_path}: {e}")
    except Exception as e:
        raise ConfigError(f"Kunde inte läsa {config_path}: {e}")


def list_projects(include_files: bool = False) -> dict:
    """List configured MQG folders with status."""
    config_path = get_config_path()
    config = load_config()
    
    projects = []
    for i, folder in enumerate(config.get('folders', []), 1):
        path = Path(folder['path']).expanduser()
        exists = path.exists()
        
        project = {
            'index': i,
            'name': folder['name'],
            'path': str(path),
            'exists': exists,
            'language': folder.get('default_language', 'sv'),
            'description': folder.get('description', ''),
        }
        
        if include_files and exists:
            md_files = [
                f for f in path.rglob("*.md")
                if not f.name.startswith('.')
                and 'README' not in f.name
                and '_archive' not in str(f)
            ]
            project['md_file_count'] = len(md_files)
        
        projects.append(project)
    
    return {
        'projects': projects,
        'default_output_dir': config.get('default_output_dir'),
        'count': len(projects),
        'config_path': str(config_path)
    }


def get_project_files(project_path: str) -> List[dict]:
    """List markdown files in a project folder."""
    path = Path(project_path).expanduser()
    if not path.exists():
        return []
    
    files = []
    for md_file in path.rglob("*.md"):
        if md_file.name.startswith('.'):
            continue
        if 'README' in md_file.name:
            continue
        if '_archive' in str(md_file):
            continue
        
        files.append({
            'path': str(md_file),
            'relative_path': str(md_file.relative_to(path)),
            'name': md_file.name,
            'mtime': md_file.stat().st_mtime
        })
    
    files.sort(key=lambda x: x['relative_path'])
    return files
```

### Uppdatera `src/qf_pipeline/utils/__init__.py`

```python
from .config import list_projects, get_project_files, ConfigError, get_config_path
```

### Lägg till i `server.py`

**I `list_tools()`:**
```python
Tool(
    name="list_projects",
    description="List configured MQG folders with status. Shows available projects for quick selection.",
    inputSchema={
        "type": "object",
        "properties": {
            "include_files": {
                "type": "boolean",
                "description": "Also count markdown files in each folder",
                "default": False
            }
        }
    }
),
```

**I `call_tool()`:**
```python
elif name == "list_projects":
    return await handle_list_projects(arguments)
```

**Ny handler:**
```python
async def handle_list_projects(arguments: dict) -> List[TextContent]:
    """Handle list_projects - list configured MQG folders."""
    from .utils.config import list_projects, ConfigError
    
    include_files = arguments.get("include_files", False)
    
    try:
        result = list_projects(include_files=include_files)
    except ConfigError as e:
        return [TextContent(type="text", text=f"Konfigurationsfel: {e}")]
    
    lines = [f"MQG Projekt ({result['count']} st):\n"]
    
    for p in result['projects']:
        status = "✅" if p['exists'] else "❌"
        lines.append(f"  {p['index']}. {status} {p['name']}")
        lines.append(f"     Path: {p['path']}")
        if p['description']:
            lines.append(f"     {p['description']}")
        if include_files and p.get('md_file_count') is not None:
            lines.append(f"     Filer: {p['md_file_count']} markdown")
        lines.append("")
    
    if result['default_output_dir']:
        lines.append(f"Default output: {result['default_output_dir']}")
    
    lines.append(f"\nConfig: {result['config_path']}")
    lines.append("\nTips: Använd step0_start med source_file från önskad mapp.")
    
    return [TextContent(type="text", text="\n".join(lines))]
```

---

## SAMMANFATTNING

| Prioritet | Task | Fil | Status |
|-----------|------|-----|--------|
| ✅ 1 | Resource handling | `server.py` | DONE (already implemented) |
| 🟡 2 | Config utility | `utils/config.py` | TODO |
| 🟡 2 | list_projects tool | `server.py` | TODO |

---

## KÖRORDNING I CLAUDE CODE

```
1. Läs ADR-009 och fixa resources i step4_export
2. Testa med fil som har bilder
3. Läs ADR-008 och skapa utils/config.py
4. Lägg till list_projects tool
5. Testa list_projects
```

---

## REFERENSER

- ADR-008: `docs/adr/ADR-008-project-configuration-location.md`
- ADR-009: `docs/adr/ADR-009-resource-handling.md`
- Konsoliderad analys: `docs/acdm/logs/2026-01-06_DISCOVER_consolidated_analysis.md`
- QTI-Generator resources: `scripts/step3_copy_resources.py`
- qf-pipeline wrappers: `src/qf_pipeline/wrappers/resources.py`

---

*Handoff updated: 2026-01-06*
*Critical fix: ADR-009 resources*
