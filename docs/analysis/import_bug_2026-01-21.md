# QuestionForge Import Bug Analysis

## Problem Summary

**Symptom:** QFMD-validation misslyckas alltid med "alla fält saknas" trots att filen är korrekt formaterad.

**Root Cause:** Import-fel när qf-pipeline körs som MCP-server.

## Technical Details

### 1. Current Import Strategy

**File:** `packages/qf-pipeline/src/qf_pipeline/wrappers/__init__.py`

```python
import sys
from pathlib import Path

# QTI-Generator-for-Inspera location (now local as qti-core)
QTI_GENERATOR_PATH = Path(__file__).parent.parent.parent.parent.parent / "qti-core"

# Add to Python path if not already present
if str(QTI_GENERATOR_PATH) not in sys.path:
    sys.path.insert(0, str(QTI_GENERATOR_PATH))
```

**Intended path:** `/packages/qti-core/`

**Problem:** Detta fungerar när qf-pipeline körs direkt, men INTE när den körs som MCP-server via Claude Desktop.

### 2. Affected Files

**File:** `packages/qf-pipeline/src/qf_pipeline/wrappers/parser.py`
```python
from src.parser.markdown_parser import MarkdownQuizParser
```

**File:** `packages/qf-pipeline/src/qf_pipeline/wrappers/validator.py`
```python
from validate_mqg_format import validate_content
```

**Problem:** Dessa imports förutsätter att qti-core finns i sys.path, vilket misslyckas när MCP körs via Claude Desktop.

## Why MCP Server Context Matters

När Claude Desktop startar en MCP-server:

1. **Working directory** kan vara annorlunda än `/packages/qf-pipeline/`
2. **Python path** manipulering via `sys.path.insert()` kanske inte fungerar
3. **Relative paths** räknas från MCP-serverns startpunkt, inte från `__init__.py`

## Evidence from User Sessions

### Session Transcript Analysis

**From:** Chat transcript (2026-01-21)

```
User: step2_validate
Result: "All questions missing required fields: ^type, ^identifier, ^points"

User: step2_read (check working file)
Result: File contents CORRECT - all fields present:
  ^type: inline_choice
  ^identifier: Q001
  ^points: 1
  ^labels: bloom: understand difficulty: easy
  
Conclusion: Parser cannot read file → Import failure
```

### Validation Behavior

**Expected:** Parse metadata fields, validate structure
**Actual:** Cannot parse at all → reports all fields missing
**Diagnosis:** `MarkdownQuizParser` import fails silently → uses fallback/broken parser

## Solution Options

### Option A: Fix Import Path (Quick Fix) ⭐ RECOMMENDED

**Change:** Make imports relative to package structure

**Before:**
```python
from src.parser.markdown_parser import MarkdownQuizParser
from validate_mqg_format import validate_content
```

**After:**
```python
# In packages/qf-pipeline/pyproject.toml, add:
[tool.setuptools.packages.find]
where = ["packages"]

# Then install qti-core as editable package:
# cd packages/qti-core && pip install -e .

# Update imports to:
from qti_core.parser.markdown_parser import MarkdownQuizParser
from qti_core.validate_mqg_format import validate_content
```

**Benefits:**
- Proper Python packaging
- Works in all contexts (direct run, MCP, testing)
- No sys.path manipulation needed

**Effort:** ~2 hours

---

### Option B: Embed QTI Core (Medium Fix)

**Change:** Copy critical files directly into qf-pipeline

**Structure:**
```
packages/qf-pipeline/
├── src/
│   └── qf_pipeline/
│       ├── qti_embedded/
│       │   ├── __init__.py
│       │   ├── parser.py          (from qti-core)
│       │   └── validator.py        (from qti-core)
│       └── wrappers/
│           ├── parser.py           (import from qti_embedded)
│           └── validator.py        (import from qti_embedded)
```

**Benefits:**
- No external dependency
- Simple imports
- Guaranteed to work

**Drawbacks:**
- Code duplication
- Must sync changes manually
- Increases package size

**Effort:** ~4 hours

---

### Option C: Dynamic Import (Current Attempt - BROKEN)

**Status:** This is what's currently attempted but failing

**Why it fails:**
```python
# __init__.py tries this:
sys.path.insert(0, str(QTI_GENERATOR_PATH))

# But when MCP runs from Claude Desktop:
# - Working dir is ~/Library/Application Support/Claude/...
# - Relative path calculations break
# - sys.path manipulation doesn't propagate to submodules
```

**Conclusion:** Not reliable for MCP context

---

## Testing the Fix

### Test 1: Direct Python
```bash
cd packages/qf-pipeline
python -c "from qf_pipeline.wrappers import parse_markdown; print('OK')"
```

**Expected:** No errors
**Current:** ImportError (qti-core not found)

### Test 2: MCP Server
```bash
# Start MCP server
cd packages/qf-pipeline
python -m qf_pipeline.server

# From Claude: call step2_validate
# Expected: Validation works
# Current: "All fields missing"
```

### Test 3: Validation Test
```python
from qf_pipeline.wrappers import validate_markdown

content = """
^type: inline_choice
^identifier: Q001
^points: 1

@field: question_text
Test question
"""

result = validate_markdown(content)
print(result)  # Should show valid=True
```

## Recommended Action Plan

### Phase 1: Quick Fix (Option A) ⭐

1. **Add qti-core to Python packages** (~30 min)
   ```bash
   cd packages/qti-core
   pip install -e .
   ```

2. **Update imports in wrappers/** (~30 min)
   - Change all `from src.parser...` → `from qti_core.src.parser...`
   - Change all `from validate_mqg_format` → `from qti_core.validate_mqg_format`

3. **Test thoroughly** (~1 hour)
   - Direct Python import
   - MCP server startup
   - Full validation workflow

### Phase 2: Documentation (~30 min)

1. **Update docs/adr/** with decision
2. **Update README.md** with installation instructions
3. **Document in CHANGELOG.md**

### Total Effort: ~2.5 hours

## Expected Outcomes

**After Fix:**
- ✅ Validation works correctly
- ✅ Parser can read QFMD files
- ✅ Export to QTI succeeds
- ✅ No more "all fields missing" errors

## Verification Checklist

- [ ] Direct import test passes
- [ ] MCP server starts without errors
- [ ] step2_validate correctly identifies fields
- [ ] step4_export generates valid QTI package
- [ ] User's 40-question file validates successfully

---

**Analysis Date:** 2026-01-21
**Analyst:** Claude (Sonnet 4.5)
**Priority:** HIGH (blocking core functionality)
**Estimated Fix Time:** 2.5 hours
