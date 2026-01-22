# ACDM DISCOVER: qf-pipeline Wrapper Analysis

**Fas:** DISCOVER (fortsättning)  
**Datum:** 2026-01-06  
**Kontext:** Hur qf-pipeline wrappar QTI-Generator-for-Inspera

---

## 1. WRAPPER-ARKITEKTUR

### 1.1 Kärnmekanism

```python
# I wrappers/__init__.py
QTI_GENERATOR_PATH = Path("/Users/niklaskarlsson/QTI-Generator-for-Inspera")
sys.path.insert(0, str(QTI_GENERATOR_PATH))
```

**Kritisk observation:** Hårdkodad sökväg gör qf-pipeline beroende av att QTI-Generator finns på exakt denna plats.

### 1.2 Wrapper → QTI-Generator mappning

| qf-pipeline Wrapper | QTI-Generator Modul | Klass/Funktion |
|---------------------|---------------------|----------------|
| `parser.py` | `src/parser/markdown_parser.py` | `MarkdownQuizParser` |
| `generator.py` | `src/generator/xml_generator.py` | `XMLGenerator` |
| `validator.py` | `validate_mqg_format.py` | `validate_content()` |
| `packager.py` | `src/packager/qti_packager.py` | `QTIPackager` |
| `resources.py` | `src/generator/resource_manager.py` | `ResourceManager` |

### 1.3 Import-struktur

```
qf-pipeline/src/qf_pipeline/
├── server.py                    ← MCP server (tool definitions)
├── tools/                       ← Tool implementations
│   └── ...
├── wrappers/
│   ├── __init__.py              ← Sätter sys.path + exporterar
│   ├── parser.py                ← Wrappar MarkdownQuizParser
│   ├── generator.py             ← Wrappar XMLGenerator
│   ├── validator.py             ← Wrappar validate_content
│   ├── packager.py              ← Wrappar QTIPackager
│   ├── resources.py             ← Wrappar ResourceManager
│   └── errors.py                ← Egna exception-klasser
└── utils/
    └── ...

QTI-Generator-for-Inspera/
├── src/
│   ├── parser/
│   │   └── markdown_parser.py   ← MarkdownQuizParser
│   ├── generator/
│   │   ├── xml_generator.py     ← XMLGenerator
│   │   └── resource_manager.py  ← ResourceManager
│   └── packager/
│       └── qti_packager.py      ← QTIPackager
├── validate_mqg_format.py       ← validate_content()
└── config/
    └── mqg_folders.json         ← Projektkonfiguration
```

---

## 2. BEROENDEGRAF

```
┌─────────────────────────────────────────────────────────────────┐
│                        Claude (User)                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ MCP Protocol
┌─────────────────────────────────────────────────────────────────┐
│  qf-pipeline MCP Server                                         │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  server.py                                                  ││
│  │  - init, step0_start, step2_validate, step4_export...      ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                   │
│                              ▼ Python calls                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  wrappers/                                                  ││
│  │  - parser.py, generator.py, validator.py, packager.py      ││
│  └─────────────────────────────────────────────────────────────┘│
└───────────────────────────────┼─────────────────────────────────┘
                                │ 
                                ▼ sys.path import
┌─────────────────────────────────────────────────────────────────┐
│  QTI-Generator-for-Inspera                                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ markdown_    │ │ xml_         │ │ qti_         │            │
│  │ parser.py    │ │ generator.py │ │ packager.py  │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐          │
│  │ config/mqg_folders.json  ← PROJEKTKONFIGURATION │          │
│  └──────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. KONFIGURATIONSDELNING

### 3.1 Nuläge

`mqg_folders.json` finns ENDAST i QTI-Generator:
```
/Users/niklaskarlsson/QTI-Generator-for-Inspera/config/mqg_folders.json
```

qf-pipeline har INGEN egen konfiguration för projekt.

### 3.2 Alternativ för `list_projects`

| Alternativ | Implementation | Fördelar | Nackdelar |
|------------|----------------|----------|-----------|
| **A) Läs från QTI-Gen** | `QTI_GENERATOR_PATH / "config" / "mqg_folders.json"` | Delad källa, ingen duplicering | Hårdkodat beroende |
| **B) Miljövariabel** | `os.environ.get("QF_CONFIG_PATH")` | Konfigurerbart | Kräver setup |
| **C) Egen kopia** | `qf-pipeline/config/mqg_folders.json` | Oberoende | Kan bli osynkad |
| **D) Symlink** | `qf-pipeline/config → QTI-Gen/config` | Delad, transparent | OS-beroende |

### 3.3 Rekommendation

**Alternativ A med fallback till B:**

```python
from pathlib import Path
import os

def get_config_path() -> Path:
    """Get path to mqg_folders.json configuration."""
    
    # 1. Check environment variable first
    env_path = os.environ.get("QF_PROJECTS_CONFIG")
    if env_path and Path(env_path).exists():
        return Path(env_path)
    
    # 2. Fall back to QTI-Generator location
    from . import QTI_GENERATOR_PATH
    qti_config = QTI_GENERATOR_PATH / "config" / "mqg_folders.json"
    if qti_config.exists():
        return qti_config
    
    # 3. No config found
    raise FileNotFoundError(
        "No project configuration found. "
        "Set QF_PROJECTS_CONFIG env var or ensure QTI-Generator config exists."
    )
```

---

## 4. WRAPPER-MÖNSTER ANALYS

### 4.1 Vad wrappers gör

1. **Felhantering** - Konverterar exceptions till egna typer (ParsingError, etc.)
2. **Förenkling** - Exponerar bara nödvändiga funktioner
3. **Dokumentation** - Tydliga docstrings med typer
4. **Isolering** - Kapslar in QTI-Generator-detaljer

### 4.2 Vad wrappers INTE gör

1. **Ingen caching** - Varje anrop skapar ny instans
2. **Ingen konfiguration** - Läser inte mqg_folders.json
3. **Ingen projektöversikt** - Vet inte vilka projekt som finns
4. **Ingen historik** - Sparar inte filval

### 4.3 Gap att fylla med `list_projects`

```python
# Saknas i wrappers:
def list_projects() -> dict:
    """List configured MQG folders with status."""
    ...

def get_project_files(project_path: str) -> list:
    """List markdown files in a project."""
    ...

def get_recent_files() -> list:
    """Get recently used files from history."""
    ...
```

---

## 5. IMPLEMENTATION: `list_projects`

### 5.1 Placering

```
qf-pipeline/src/qf_pipeline/
├── wrappers/
│   ├── __init__.py          ← Lägg till export
│   ├── projects.py          ← NY FIL
│   └── ...
└── server.py                ← Lägg till tool
```

### 5.2 Ny fil: `projects.py`

```python
"""Project configuration wrapper.

Reads MQG folder configuration from QTI-Generator-for-Inspera.
"""

import json
import os
from pathlib import Path
from typing import List, Optional

from . import QTI_GENERATOR_PATH


def get_config_path() -> Path:
    """Get path to mqg_folders.json configuration."""
    env_path = os.environ.get("QF_PROJECTS_CONFIG")
    if env_path and Path(env_path).exists():
        return Path(env_path)
    
    qti_config = QTI_GENERATOR_PATH / "config" / "mqg_folders.json"
    if qti_config.exists():
        return qti_config
    
    raise FileNotFoundError("No project configuration found")


def list_projects(include_files: bool = False) -> dict:
    """List configured MQG folders with status.
    
    Args:
        include_files: If True, also count markdown files in each folder.
    
    Returns:
        {
            'projects': [
                {
                    'index': 1,
                    'name': str,
                    'path': str,
                    'exists': bool,
                    'language': str,
                    'description': str,
                    'md_file_count': int  # Only if include_files=True
                },
                ...
            ],
            'default_output_dir': str,
            'count': int,
            'config_path': str
        }
    """
    config_path = get_config_path()
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
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
            md_files = list(path.rglob("*.md"))
            md_files = [f for f in md_files if not f.name.startswith('.') 
                       and 'README' not in f.name
                       and '_archive' not in str(f)]
            project['md_file_count'] = len(md_files)
        
        projects.append(project)
    
    return {
        'projects': projects,
        'default_output_dir': config.get('default_output_dir'),
        'count': len(projects),
        'config_path': str(config_path)
    }


def get_project_files(project_path: str) -> List[dict]:
    """List markdown files in a project folder.
    
    Args:
        project_path: Path to project folder.
    
    Returns:
        List of file info dicts with path, name, mtime.
    """
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

### 5.3 Server.py tillägg

```python
# I list_tools():
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

# I call_tool():
elif name == "list_projects":
    return await handle_list_projects(arguments)

# Ny handler:
async def handle_list_projects(arguments: dict) -> List[TextContent]:
    """Handle list_projects - list configured MQG folders."""
    from .wrappers.projects import list_projects
    
    include_files = arguments.get("include_files", False)
    
    try:
        result = list_projects(include_files=include_files)
    except FileNotFoundError as e:
        return [TextContent(type="text", text=f"Konfiguration saknas: {e}")]
    
    # Format output
    lines = [f"MQG Projekt ({result['count']} st):\n"]
    
    for p in result['projects']:
        status = "✅" if p['exists'] else "❌"
        lines.append(f"  {p['index']}. {status} {p['name']}")
        lines.append(f"     Path: {p['path']}")
        if p['description']:
            lines.append(f"     {p['description']}")
        if include_files and p['exists']:
            lines.append(f"     Filer: {p.get('md_file_count', '?')} markdown")
        lines.append("")
    
    if result['default_output_dir']:
        lines.append(f"Default output: {result['default_output_dir']}")
    
    lines.append("\nTips: Använd step0_start med source_file från önskad mapp.")
    
    return [TextContent(type="text", text="\n".join(lines))]
```

---

## 6. TESTPLAN

### 6.1 Manuell test
```
1. qf-pipeline:list_projects
   → Ska visa 5 projekt med ✅/❌ status

2. qf-pipeline:list_projects include_files=true
   → Ska visa antal .md-filer per projekt

3. Ändra env QF_PROJECTS_CONFIG till ogiltig path
   → Ska falla tillbaka till QTI-Generator config
```

### 6.2 Enhetstest
```python
def test_list_projects_returns_dict():
    result = list_projects()
    assert 'projects' in result
    assert 'count' in result

def test_list_projects_includes_status():
    result = list_projects()
    for p in result['projects']:
        assert 'exists' in p
        assert isinstance(p['exists'], bool)

def test_get_project_files_excludes_archive():
    files = get_project_files("/path/with/_archive/")
    for f in files:
        assert '_archive' not in f['path']
```

---

## 7. NÄSTA STEG

### 7.1 SHAPE-fas
- [x] Wrapper-relation analyserad
- [x] `list_projects` specifikation skapad
- [x] Beslut: Config i `utils/config.py`, INTE i `wrappers/`

### 7.2 DECIDE-fas
- [x] ADR-008: Project Configuration Location ✅

### 7.3 COORDINATE-fas
- [ ] Implementera `utils/config.py`
- [ ] Uppdatera `server.py` med `list_projects` tool
- [ ] Testa med Claude

---

## 8. UPPDATERING: Wrapper vs Utility

**Ursprungligt förslag:** Skapa `wrappers/projects.py`

**Reviderat beslut:** Skapa `utils/config.py` istället

**Anledning:**
- Wrappers ska wrappa EXTERN KOD (klasser, funktioner från QTI-Generator)
- Config-läsning är INTERN LOGIK (filläsning, inte kod-wrapping)
- Tydligare arkitektur:
  - `wrappers/` = externa beroenden
  - `utils/` = interna utilities

Se ADR-008 för fullständig motivering.

---

*ACDM DISCOVER Steg 2 slutförd: 2026-01-06*
*ADR-008 skapad: 2026-01-06*
