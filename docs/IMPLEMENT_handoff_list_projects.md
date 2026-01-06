# IMPLEMENT HANDOFF: list_projects Tool

**Status:** Ready for implementation  
**Date:** 2026-01-06  
**Target:** Claude Code  
**ADR:** ADR-008-project-configuration-location.md

---

## TASK SUMMARY

Implement `list_projects` tool in qf-pipeline MCP server.

---

## FILES TO CREATE

### 1. `src/qf_pipeline/utils/config.py`

```python
"""Project configuration utilities.

Reads MQG folder configuration from QTI-Generator or environment.
"""

import json
import os
from pathlib import Path
from typing import List

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
    """Load project configuration."""
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
        Dictionary with projects, default_output_dir, count, config_path.
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

---

## FILES TO MODIFY

### 2. `src/qf_pipeline/utils/__init__.py`

Add export:
```python
from .config import list_projects, get_project_files, ConfigError
```

### 3. `src/qf_pipeline/server.py`

Add to `list_tools()`:
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

Add to `call_tool()`:
```python
elif name == "list_projects":
    return await handle_list_projects(arguments)
```

Add handler:
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

## TESTS TO ADD

### 4. `tests/test_config.py`

```python
"""Tests for utils/config.py"""

import pytest
from qf_pipeline.utils.config import list_projects, get_project_files, ConfigError


def test_list_projects_returns_dict():
    """list_projects should return dict with expected keys."""
    result = list_projects()
    assert 'projects' in result
    assert 'count' in result
    assert 'config_path' in result


def test_list_projects_includes_status():
    """Each project should have exists status."""
    result = list_projects()
    for p in result['projects']:
        assert 'exists' in p
        assert isinstance(p['exists'], bool)


def test_list_projects_with_files():
    """include_files should add md_file_count."""
    result = list_projects(include_files=True)
    for p in result['projects']:
        if p['exists']:
            assert 'md_file_count' in p
```

---

## EXPECTED OUTPUT

After implementation, `qf-pipeline:list_projects` should return:

```
MQG Projekt (5 st):

  1. ✅ Biologi BIOG001X (Autumn 2025)
     Path: /Users/niklaskarlsson/Nextcloud/Courses/Biologi/...
     Biologifrågor för BIOG001X hösten 2025
     
  2. ❌ TRA265 LP2 2025
     Path: /Users/niklaskarlsson/Nextcloud/Chalmers/TRA265/...
     
  3. ✅ Mate2b001x Autmn 2025
     Path: /Users/niklaskarlsson/Nextcloud/Courses/Matematik/...

Default output: /Users/niklaskarlsson/Nextcloud/Inspera/QTI_export_INSPERA

Config: /Users/niklaskarlsson/QTI-Generator-for-Inspera/config/mqg_folders.json

Tips: Använd step0_start med source_file från önskad mapp.
```

---

## VERIFICATION

1. Run tests: `pytest tests/test_config.py -v`
2. Start MCP server and test with Claude
3. Verify output matches expected format

---

## REFERENCES

- ADR-008: `docs/adr/ADR-008-project-configuration-location.md`
- Analysis: `docs/acdm/logs/2026-01-06_DISCOVER_qf-pipeline_wrapper_analysis.md`
- Terminal reference: `QTI-Generator-for-Inspera/scripts/interactive_qti.py`

---

*Handoff created: 2026-01-06*
