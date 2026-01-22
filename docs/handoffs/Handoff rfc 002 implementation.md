# IMPLEMENTATION HANDOFF: RFC-002 - QFMD Naming [CORRECTED]

**För:** Claude Code (Windsurf)  
**Från:** Claude Desktop  
**Datum:** 2026-01-17  
**RFC:** RFC-002-markdown-format-naming.md  
**Status:** CORRECTED after code review

---

## VIKTIGT: Kod-analys genomförd

Code har analyserat faktisk kod och hittat diskrepanser i ursprunglig handoff.
Denna version är KORRIGERAD baserat på `/packages/qf-pipeline/src/qf_pipeline/step1/detector.py`.

---

## FAKTISK KOD-STRUKTUR

### Nuvarande FormatLevel (detector.py, line 9-14)

```python
class FormatLevel(Enum):
    """Input format levels."""
    VALID_V65 = 'v65'           # Already valid, skip Step 1
    OLD_SYNTAX_V63 = 'v63'      # Has @field: but old syntax
    SEMI_STRUCTURED = 'semi'    # Has ## headers, **Type**: etc
    RAW = 'raw'                 # Unstructured, needs scaffolding
    UNKNOWN = 'unknown'
```

**Observationer:**
- ✅ Redan string-värden (inte numeriska som ursprunglig handoff antog)
- ✅ OLD_SYNTAX_V63 (INTE "OLD_SYNTAX" som handoff skrev)
- ✅ UNKNOWN finns (saknades i ursprunglig handoff)

---

## KORRIGERAD ENUM-MAPPING

| Nuvarande Namn | Nuvarande Värde | Nytt Namn | Nytt Värde | Notering |
|----------------|-----------------|-----------|------------|----------|
| VALID_V65 | 'v65' | QFMD | 'qfmd' | Canonical format |
| OLD_SYNTAX_V63 | 'v63' | LEGACY_SYNTAX | 'legacy' | Old @ syntax |
| SEMI_STRUCTURED | 'semi' | SEMI_STRUCTURED | 'semi' | Oförändrad |
| RAW | 'raw' | UNSTRUCTURED | 'unstructured' | Mer beskrivande |
| UNKNOWN | 'unknown' | UNKNOWN | 'unknown' | Oförändrad |

---

## PHASE 1: CODE UPDATES

### 1.1 Update FormatLevel Enum

**Fil:** `packages/qf-pipeline/src/qf_pipeline/step1/detector.py`

**Rad 9-14, BEFORE:**
```python
class FormatLevel(Enum):
    """Input format levels."""
    VALID_V65 = 'v65'           # Already valid, skip Step 1
    OLD_SYNTAX_V63 = 'v63'      # Has @field: but old syntax
    SEMI_STRUCTURED = 'semi'    # Has ## headers, **Type**: etc
    RAW = 'raw'                 # Unstructured, needs scaffolding
    UNKNOWN = 'unknown'
```

**AFTER:**
```python
class FormatLevel(Enum):
    """Input format levels."""
    QFMD = 'qfmd'                    # QuestionForge Markdown (canonical)
    LEGACY_SYNTAX = 'legacy'         # Old @question:/@type: syntax
    SEMI_STRUCTURED = 'semi'         # Has ## headers, **Type**: etc
    UNSTRUCTURED = 'unstructured'    # Unstructured, needs scaffolding
    UNKNOWN = 'unknown'              # Cannot determine format
```

### 1.2 Update get_format_description()

**Fil:** `packages/qf-pipeline/src/qf_pipeline/step1/detector.py`

**Rad 54-61, BEFORE:**
```python
def get_format_description(level: FormatLevel) -> str:
    """Get human-readable description of format level."""
    descriptions = {
        FormatLevel.VALID_V65: "Valid v6.5 format - redo för Step 2",
        FormatLevel.OLD_SYNTAX_V63: "Gammal syntax (v6.3) - behöver syntax-uppgradering",
        FormatLevel.SEMI_STRUCTURED: "Semi-strukturerat - behöver omformatering",
        FormatLevel.RAW: "Ostrukturerat - behöver qf-scaffolding först",
        FormatLevel.UNKNOWN: "Okänt format - behöver manuell granskning"
    }
    return descriptions.get(level, "Okänt")
```

**AFTER:**
```python
def get_format_description(level: FormatLevel) -> str:
    """Get human-readable description of format level."""
    descriptions = {
        FormatLevel.QFMD: "QFMD format - ready for validation",
        FormatLevel.LEGACY_SYNTAX: "Legacy syntax - needs conversion to QFMD",
        FormatLevel.SEMI_STRUCTURED: "Semi-structured - needs formatting",
        FormatLevel.UNSTRUCTURED: "Unstructured - recommend M3 (Question Generation)",
        FormatLevel.UNKNOWN: "Unknown format - needs manual review"
    }
    return descriptions.get(level, "Unknown format")
```

### 1.3 Update is_transformable()

**Fil:** `packages/qf-pipeline/src/qf_pipeline/step1/detector.py`

**Rad 66-68, BEFORE:**
```python
def is_transformable(level: FormatLevel) -> bool:
    """Check if format can be transformed by Step 1."""
    return level == FormatLevel.OLD_SYNTAX_V63
```

**AFTER:**
```python
def is_transformable(level: FormatLevel) -> bool:
    """Check if format can be transformed by Step 1."""
    return level == FormatLevel.LEGACY_SYNTAX
```

### 1.4 Update Comments in detect_format()

**Fil:** `packages/qf-pipeline/src/qf_pipeline/step1/detector.py`

**Rad 24-26, BEFORE:**
```python
    # Check for v6.5 markers (caret metadata + @end_field)
```

**AFTER:**
```python
    # Check for QFMD markers (caret metadata + @end_field)
```

**Rad 32-33, BEFORE:**
```python
    # Check for v6.3 markers (old @ syntax with colon)
```

**AFTER:**
```python
    # Check for legacy syntax markers (old @ syntax with colon)
```

**Rad 29-30, BEFORE:**
```python
    if has_caret_metadata and has_field_markers and has_end_field:
        return FormatLevel.VALID_V65
```

**AFTER:**
```python
    if has_caret_metadata and has_field_markers and has_end_field:
        return FormatLevel.QFMD
```

**Rad 36-37, BEFORE:**
```python
    if has_at_metadata and has_field_markers:
        return FormatLevel.OLD_SYNTAX_V63
```

**AFTER:**
```python
    if has_at_metadata and has_field_markers:
        return FormatLevel.LEGACY_SYNTAX
```

**Rad 47-48, BEFORE:**
```python
    if has_raw_swedish:
        return FormatLevel.RAW
```

**AFTER:**
```python
    if has_raw_swedish:
        return FormatLevel.UNSTRUCTURED
```

### 1.5 Search All Other Files Referencing FormatLevel

**Command:**
```bash
cd packages/qf-pipeline
grep -r "FormatLevel\." --include="*.py" src/
```

**Action:** Update ALLA references från:
- `FormatLevel.VALID_V65` → `FormatLevel.QFMD`
- `FormatLevel.OLD_SYNTAX_V63` → `FormatLevel.LEGACY_SYNTAX`
- `FormatLevel.RAW` → `FormatLevel.UNSTRUCTURED`

---

## PHASE 2: DOCUMENTATION UPDATES

### 2.1 WORKFLOW.md

**Same as original handoff - no changes needed to these instructions**

### 2.2 step1_guided_build_spec.md

**Global search/replace in this file:**
- "v6.5" → "QFMD"
- "v6.3" → "Legacy Syntax"
- "Level 1" → "Unstructured"
- "Level 2" → "Semi-Structured"
- "Level 3" / "OLD_SYNTAX" → "Legacy Syntax"
- "Level 4" / "VALID_V65" → "QFMD"

**Special attention:**
Replace all code examples showing enum values:
```python
# BEFORE
FormatLevel.VALID_V65
FormatLevel.OLD_SYNTAX
FormatLevel.RAW

# AFTER
FormatLevel.QFMD
FormatLevel.LEGACY_SYNTAX
FormatLevel.UNSTRUCTURED
```

---

## PHASE 3: USER-FACING MESSAGES

**Same guidance as original, but ensure you search for actual enum names:**
- Search for `.VALID_V65` not just "v6.5"
- Search for `.OLD_SYNTAX_V63` not just "v6.3"
- Search for `.RAW` references

---

## FILES TO CHANGE vs NOT CHANGE

### ✅ SHOULD CHANGE:

**Code:**
- `packages/qf-pipeline/src/qf_pipeline/step1/detector.py` ⭐ PRIMARY
- All files in `packages/qf-pipeline/src/` that reference FormatLevel
- Tool files with user-facing messages

**Documentation:**
- `WORKFLOW.md`
- `docs/specs/step1_guided_build_spec.md`
- Any other specs mentioning "v6.3" or "v6.5"

### ❌ SHOULD NOT CHANGE:

**Test Data:**
- `test_projects/*` - These are test fixtures, leave as-is

**Historical Documents:**
- `docs/rfcs/RFC-*.md` (except RFC-002) - These are historical
- `qti-core/docs/*` - Separate package, may have own versioning

**Git History:**
- Don't rewrite commit messages

---

## TESTING CHECKLIST

After implementation:

- [ ] `FormatLevel` enum has correct names (QFMD, LEGACY_SYNTAX, UNSTRUCTURED, SEMI_STRUCTURED, UNKNOWN)
- [ ] `FormatLevel` enum has correct values ('qfmd', 'legacy', 'unstructured', 'semi', 'unknown')
- [ ] `get_format_description()` returns QFMD-terminology
- [ ] `is_transformable()` checks LEGACY_SYNTAX
- [ ] All `detect_format()` returns use new enum names
- [ ] Comments in detector.py use new terminology
- [ ] All other files referencing FormatLevel updated
- [ ] WORKFLOW.md updated (no "v6.3 → v6.5")
- [ ] step1_guided_build_spec.md uses new terms
- [ ] No "v6.3" or "v6.5" in user-facing messages

---

## VALIDATION COMMANDS

**Find remaining v6 references (should be ~0 in source code):**
```bash
cd packages/qf-pipeline
grep -r "v6\." --include="*.py" src/ | grep -v "# QFMD was v6.5"
```

**Find FormatLevel references:**
```bash
cd packages/qf-pipeline
grep -r "FormatLevel\." --include="*.py" src/
```

**Expected counts AFTER implementation:**
- FormatLevel.QFMD: ~5-10 occurrences
- FormatLevel.LEGACY_SYNTAX: ~5-10 occurrences
- FormatLevel.VALID_V65: 0 occurrences
- FormatLevel.OLD_SYNTAX_V63: 0 occurrences

---

## EXPECTED TERMINAL OUTPUT EXAMPLES

**Format detection messages:**
```python
# When file is already QFMD:
"✅ File is already in QFMD format - ready for validation!"

# When file is legacy:
"📝 File uses Legacy Syntax - converting to QFMD format..."

# When file is unstructured:
"⚠️ File is unstructured - recommend using M3 (Question Generation) instead"
```

---

## MIGRATION NOTES

**Breaking changes:**
- Enum names changed - any code comparing enum names will break
- Enum values changed - any code comparing enum values will break

**Backwards compatibility:**
- Test data in test_projects/ uses old format - don't change
- Tests may need updating if they assert on enum names/values

**Communication:**
- Users should see "QFMD" and "Legacy Syntax" in all messages
- Old terms ("v6.3", "v6.5") only in backward-compat scenarios

---

## QUESTIONS DURING IMPLEMENTATION

If you encounter:

1. **More than 170 "v6" references** - Document where they are, some may be legitimate
2. **Files not mentioned here** - Ask before changing
3. **Tests failing** - May need to update test assertions
4. **Unclear whether to change** - Default to NO CHANGE, ask first

---

**This handoff is CORRECTED and ready for implementation.**
**Original handoff had wrong assumptions about enum structure.**
**This version is based on actual code review.**