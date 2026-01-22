# RFC-012: Pipeline-Script Alignment

**Status:** Proposed (Hybrid Approach)
**Created:** 2026-01-22
**Updated:** 2026-01-22
**Author:** Niklas + Claude Code + Claude Sonnet
**Related:** WORKFLOW.md Appendix A.1.2, ADR-008 (qti-core)

---

## Executive Summary

**BESLUT: Hybrid Approach**

- **Phase 1 (NU):** Subprocess - Fixa kritiska buggar med minimal risk (1 dag)
- **Phase 2 (SENARE):** Refactor - Ren arkitektur för långsiktig underhåll (3-5 dagar)

---

## Problem Statement

### Identifierade buggar (2026-01-22)

| Steg | Problem | Allvarlighet |
|------|---------|--------------|
| 1 | Validering skippad i step4_export | ⚠️ Medium |
| 6 | `apply_resource_mapping()` saknas helt | 🔴 Kritisk |

### Grundorsak

Wrappers **reimplementerar** logiken istället för att **återanvända** scripts.

---

## Proposal: Script-First Architecture

### Princip

> **MCP pipeline ska anropa EXAKT samma kod som manuella scripts.**

---

## PHASE 1: Subprocess (IMPLEMENTERA NU)

### step2_validate implementation

```python
async def handle_step2_validate(arguments: dict):
    """Kör step1_validate.py via subprocess."""
    import subprocess
    
    session = get_current_session()
    file_path = session.working_file if session else arguments.get("file_path")
    
    # Path to qti-core
    qti_core_path = Path("/Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/packages/qti-core")
    
    # Run step1_validate.py
    result = subprocess.run(
        ['python', 'scripts/step1_validate.py', str(file_path), '--verbose'],
        cwd=qti_core_path,
        capture_output=True,
        text=True,
        timeout=60
    )
    
    # Update session
    is_valid = (result.returncode == 0)
    if session:
        session.update_validation(is_valid, 0)
    
    return [TextContent(type="text", text=result.stdout)]
```

### step4_export implementation

```python
async def handle_step4_export(arguments: dict):
    """Kör ALLA 5 scripts sekventiellt."""
    import subprocess
    
    session = get_current_session()
    file_path = session.working_file
    language = arguments.get("language", "sv")
    
    qti_core_path = Path("/Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/packages/qti-core")
    
    scripts = [
        {'name': 'step1_validate.py', 'args': [str(file_path), '--verbose']},
        {'name': 'step2_create_folder.py', 'args': [str(file_path)]},
        {'name': 'step3_copy_resources.py', 'args': []},
        {'name': 'step4_generate_xml.py', 'args': ['--language', language]},
        {'name': 'step5_create_zip.py', 'args': []},
    ]
    
    all_output = []
    
    for i, script in enumerate(scripts, 1):
        all_output.append(f"\n{'='*70}")
        all_output.append(f"STEG {i}/5: {script['name']}")
        all_output.append(f"{'='*70}\n")
        
        result = subprocess.run(
            ['python', f"scripts/{script['name']}"] + script['args'],
            cwd=qti_core_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            all_output.append(f"\n❌ FEL i {script['name']}!")
            all_output.append(result.stderr)
            return [TextContent(type="text", text="\n".join(all_output))]
        
        all_output.append(result.stdout)
    
    return [TextContent(type="text", text="\n".join(all_output))]
```

---

## Migration Plan

### ✅ Phase 1: Subprocess (NU - 1 dag)

- [ ] Implementera subprocess i server.py
- [ ] Testa alla 5 steg
- [ ] Verifiera att bilder fungerar
- [ ] Dokumentera i WORKFLOW.md

### 🔄 Phase 2: Refactor (SENARE - 3-5 dagar)

- [ ] Refactor scripts → importerbara funktioner
- [ ] Uppdatera server.py
- [ ] Unit tests
- [ ] Ta bort subprocess

---

*RFC-012 | Pipeline-Script Alignment | 2026-01-22*
