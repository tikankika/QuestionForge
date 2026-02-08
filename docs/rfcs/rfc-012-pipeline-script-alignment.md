# RFC-012: Pipeline-Script Alignment

**Status:** Phase 1 IMPLEMENTED
**Created:** 2026-01-22
**Updated:** 2026-01-25
**Author:** Niklas + Claude Code + Claude Sonnet
**Related:** WORKFLOW.md Appendix A.1.2, ADR-008 (qti-core)

---

## Executive Summary

**DECISION: Hybrid Approach**

- **Phase 1 (NOW):** Subprocess - Fix critical bugs with minimal risk (1 day)
- **Phase 2 (LATER):** Refactor - Clean architecture for long-term maintenance (3-5 days)

---

## Problem Statement

### Identified Bugs (2026-01-22)

| Step | Problem | Severity |
|------|---------|--------------|
| 1 | Validation skipped in step4_export | ⚠️ Medium |
| 6 | `apply_resource_mapping()` missing entirely | 🔴 Critical |

### Root Cause

Wrappers **re-implement** the logic instead of **reusing** scripts.

---

## Proposal: Script-First Architecture

### Princip

> **MCP pipeline ska anropa EXAKT samma kod som manuella scripts.**

---

## PHASE 1: Subprocess (IMPLEMENTERA NU)

### step2_validate implementation

```python
async def handle_step2_validate(arguments: dict):
    """Run step1_validate.py via subprocess."""
    import subprocess
    
    session = get_current_session()
    file_path = session.working_file if session else arguments.get("file_path")
    
    # Path to qti-core
    qti_core_path = Path("./packages/qti-core")
    
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
    """Run ALL 5 scripts sequentially."""
    import subprocess
    
    session = get_current_session()
    file_path = session.working_file
    language = arguments.get("language", "sv")
    
    qti_core_path = Path("./packages/qti-core")
    
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
        all_output.append(f"STEP {i}/5: {script['name']}")
        all_output.append(f"{'='*70}\n")
        
        result = subprocess.run(
            ['python', f"scripts/{script['name']}"] + script['args'],
            cwd=qti_core_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            all_output.append(f"\n❌ ERROR in {script['name']}!")
            all_output.append(result.stderr)
            return [TextContent(type="text", text="\n".join(all_output))]
        
        all_output.append(result.stdout)
    
    return [TextContent(type="text", text="\n".join(all_output))]
```

---

## Migration Plan

### ✅ Phase 1: Subprocess (COMPLETE - 2026-01-24)

- [x] Implement subprocess in server.py
- [x] Test all 5 steps (syntax + import + simulated calls)
- [x] Verify that images work (see rfc-012-image-path-verification.md)
- [x] Document in WORKFLOW.md (Appendix A.1.2)
- [x] Commit: `ac866ab` - feat(rfc-012): Replace wrappers with subprocess calls

### 🔄 Phase 2: Refactor (LATER - 3-5 days)

- [ ] Refactor scripts → importable functions
- [ ] Update server.py
- [ ] Unit tests
- [ ] Remove subprocess

---

## Appendix A: Parser Consistency (2026-01-25)

### Problem: Validator vs Parser Mismatch

After RFC-012 Phase 1 was implemented, a second alignment issue was discovered:

| Component | Regex Pattern | Accepts Colons? |
|-----------|---------------|-----------------|
| `validate_mqg_format.py` | `\^type:?\s+(\S+)` | Yes |
| `markdown_parser.py` | `^\^type\s+(.+)` | No |

**Symptom:** `step1_validate.py` reported 40 valid questions, but `step4_generate_xml.py` found 0.

### Solution: Single Source of Truth

The same "script-first" philosophy applies to the validator:

> **The parser (`markdown_parser.py`) is the single source of truth for format rules.**

**Implementation:**
1. Added `validate()` method to `markdown_parser.py` (~100 lines)
2. Simplified `validate_mqg_format.py` from 554 → 185 lines
3. `validate_mqg_format.py` now calls `parser.validate()` instead of own parsing

**Guarantee:** If `validate()` passes, `parse()` will work (same code, same rules).

### Key Code Change

```python
# validate_mqg_format.py - NOW A THIN WRAPPER
from src.parser.markdown_parser import MarkdownQuizParser

def validate_markdown_file(file_path: Path) -> ValidationReport:
    parser = MarkdownQuizParser(content)
    result = parser.validate()  # Single source of truth!
    # ... convert result to ValidationReport
```

### Verification

| Test | Validate | Export | Status |
|------|----------|--------|--------|
| v1 (with colons) | ❌ 0 valid, 120 errors | 0 questions | ✅ Consistent |
| v2 (correct format) | ✅ 40 valid | 40 questions | ✅ Consistent |

---

*RFC-012 | Pipeline-Script Alignment | 2026-01-22 | Updated 2026-01-25*
