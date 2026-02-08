# ADR-008: Project Configuration Location

**Status:** Proposed  
**Date:** 2026-01-06  
**Deciders:** Niklas  
**Context:** DISCOVER phase - Terminal vs qf-pipeline analysis

---

## Context

qf-pipeline needs to list available MQG project folders to provide the same quick-selection experience as the Terminal QTI Generator. The Terminal uses a configuration file (`mqg_folders.json`) that defines project folders with names, paths, and default settings.

**Current state:**
- `mqg_folders.json` exists ONLY in QTI-Generator-for-Inspera
- qf-pipeline has NO project configuration
- qf-pipeline wrappers wrap QTI-Generator CODE, not configuration

**Question:** Where should qf-pipeline read project configuration from, and where should this logic live in the codebase?

---

## Decision

### Part 1: Configuration Source

**Read from QTI-Generator with environment variable fallback.**

```python
# Priority order:
1. Environment variable: QF_PROJECTS_CONFIG
2. QTI-Generator location: QTI_GENERATOR_PATH / "config" / "mqg_folders.json"
3. Error if neither exists
```

**Rationale:**
- Single source of truth (no config duplication)
- Flexibility via environment variable for different setups
- Works out-of-the-box for current setup

### Part 2: Code Location

**Place in `utils/config.py`, NOT in `wrappers/`.**

```
qf-pipeline/src/qf_pipeline/
├── wrappers/           ← Wraps QTI-Generator CODE (classes, functions)
│   ├── parser.py       ← Wraps MarkdownQuizParser class
│   ├── generator.py    ← Wraps XMLGenerator class
│   └── ...
└── utils/              ← qf-pipeline INTERNAL utilities
    ├── logger.py       ← Existing logging utility
    └── config.py       ← NEW: Project configuration reading
```

**Rationale:**
- Wrappers are for wrapping EXTERNAL CODE (classes, functions)
- Config reading is INTERNAL LOGIC (file I/O, not code wrapping)
- Clear architectural separation:
  - `wrappers/` = external dependencies (QTI-Generator code)
  - `utils/` = internal utilities (config, logging, helpers)

---

## Consequences

### Positive
- No configuration duplication (single source)
- Clear code organization (wrappers vs utilities)
- Flexible deployment via environment variable
- Consistent with existing utils pattern (logger.py)

### Negative
- Hard dependency on QTI-Generator file location (mitigated by env var)
- Config changes in QTI-Generator affect qf-pipeline (but this is desired)

### Neutral
- Requires QTI-Generator to be present for default behavior
- Users can override with QF_PROJECTS_CONFIG if needed

---

## Implementation

### New file: `utils/config.py`

```python
"""Project configuration utilities.

Reads MQG folder configuration from QTI-Generator or environment.
"""

import json
import os
from pathlib import Path
from typing import List, Optional

# Import QTI_GENERATOR_PATH from wrappers
from ..wrappers import QTI_GENERATOR_PATH


class ConfigError(Exception):
    """Configuration-related errors."""
    pass


def get_config_path() -> Path:
    """Get path to mqg_folders.json configuration.
    
    Priority:
        1. QF_PROJECTS_CONFIG environment variable
        2. QTI-Generator default location
    
    Returns:
        Path to configuration file.
    
    Raises:
        ConfigError: If no valid configuration found.
    """
    # 1. Check environment variable
    env_path = os.environ.get("QF_PROJECTS_CONFIG")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path
        # Env var set but invalid - warn but continue to fallback
    
    # 2. Fall back to QTI-Generator location
    qti_config = QTI_GENERATOR_PATH / "config" / "mqg_folders.json"
    if qti_config.exists():
        return qti_config
    
    # 3. No config found
    raise ConfigError(
        "No project configuration found. Either:\n"
        "  1. Set QF_PROJECTS_CONFIG environment variable, or\n"
        "  2. Ensure QTI-Generator config exists at:\n"
        f"     {qti_config}"
    )


def load_config() -> dict:
    """Load project configuration.
    
    Returns:
        Configuration dictionary with 'folders' and 'default_output_dir'.
    
    Raises:
        ConfigError: If configuration cannot be loaded.
    """
    config_path = get_config_path()
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in {config_path}: {e}")
    except Exception as e:
        raise ConfigError(f"Failed to read {config_path}: {e}")


def list_projects(include_files: bool = False) -> dict:
    """List configured MQG folders with status.
    
    Args:
        include_files: If True, count markdown files in each folder.
    
    Returns:
        Dictionary with:
        {
            'projects': [...],
            'default_output_dir': str,
            'count': int,
            'config_path': str
        }
    """
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
    """List markdown files in a project folder.
    
    Args:
        project_path: Path to project folder.
    
    Returns:
        List of file info dicts.
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

### Server.py additions

```python
# In list_tools():
Tool(
    name="list_projects",
    description="List configured MQG folders with status.",
    inputSchema={
        "type": "object",
        "properties": {
            "include_files": {
                "type": "boolean",
                "description": "Count markdown files in each folder",
                "default": False
            }
        }
    }
),

# Handler:
async def handle_list_projects(arguments: dict) -> List[TextContent]:
    from .utils.config import list_projects, ConfigError
    
    try:
        result = list_projects(include_files=arguments.get("include_files", False))
    except ConfigError as e:
        return [TextContent(type="text", text=f"Config error: {e}")]
    
    lines = [f"MQG Projects ({result['count']}):\n"]
    for p in result['projects']:
        status = "✅" if p['exists'] else "❌"
        lines.append(f"  {p['index']}. {status} {p['name']}")
        lines.append(f"     Path: {p['path']}")
        if p.get('md_file_count'):
            lines.append(f"     Files: {p['md_file_count']} markdown")
        lines.append("")
    
    return [TextContent(type="text", text="\n".join(lines))]
```

---

## Alternatives Considered

### A: Duplicate config in qf-pipeline
- **Rejected:** Creates synchronization problems

### B: Symbolic link to QTI-Generator config
- **Rejected:** OS-dependent, confusing

### C: Place config logic in wrappers/
- **Rejected:** Wrappers should wrap code, not read files

### D: Only use environment variable
- **Rejected:** Poor out-of-the-box experience

---

## References

- ACDM Log: `docs/acdm/logs/2026-01-06_DISCOVER_Terminal_vs_qf-pipeline.md`
- ACDM Log: `docs/acdm/logs/2026-01-06_DISCOVER_qf-pipeline_wrapper_analysis.md`
- Terminal config: `QTI-Generator-for-Inspera/config/mqg_folders.json`

---

*ADR-008 | QuestionForge | 2026-01-06*
