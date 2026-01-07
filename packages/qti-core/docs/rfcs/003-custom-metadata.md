# RFC 003: Inspera Custom Metadata Support

**Status:** Implemented
**Date:** 2025-12-18
**Author:** Claude Code

---

## Summary

Add support for Inspera's new Custom Metadata feature, allowing structured metadata fields to be applied to both Questions and Question Sets via QTI import.

---

## Inspera Terminology

| Term | Description | XML Element |
|------|-------------|-------------|
| **Label** | Free-form text tag (existing) | `<imsmd:taxon>` with only `<imsmd:entry>` |
| **Custom Metadata** | Structured field + value (new) | `<imsmd:taxon>` with `<imsmd:id>` + `<imsmd:entry>` |
| **Field name** | The metadata field identifier | `<imsmd:id>Bloom</imsmd:id>` |
| **Value** | The selected/entered value | `<imsmd:entry><imsmd:langstring>Understand</imsmd:langstring></imsmd:entry>` |

---

## Background

### Labels (Existing)
- Free-form text tags applied to questions and question sets
- Stored in `imsmanifest.xml` as `<imsmd:taxon>` with only `<imsmd:entry>` (NO `<imsmd:id>`)
- Any text value, searchable if 3+ characters
- Currently supported via `^labels` in MQG format

### Custom Metadata (New Feature)
- Structured fields with predefined values
- Created at tenant level by Custom Metadata Manager
- Made available per Item Bank by Item Bank Manager
- Can apply to **Questions AND Question Sets**

### Custom Metadata Field Types
| Type | Description | QTI Format |
|------|-------------|------------|
| Single-select | One value from predefined list | `<imsmd:id>Field name</imsmd:id><imsmd:entry>Value</imsmd:entry>` |
| Multi-select | Multiple values from list | Multiple `<imsmd:taxon>` with same `<imsmd:id>` |
| Numbers | Integer value (no decimals) | `<imsmd:entry>` contains number |
| Dates | Date value | `<imsmd:entry>` contains date string |

---

## QTI Structure Analysis

### Labels (NO `<imsmd:id>`)
```xml
<imsmd:taxon>
  <imsmd:entry>
    <imsmd:langstring>Easy</imsmd:langstring>
  </imsmd:entry>
</imsmd:taxon>
```

### Custom Metadata (WITH `<imsmd:id>`)
```xml
<imsmd:taxon>
  <imsmd:id>Bloom</imsmd:id>                           <!-- Field name -->
  <imsmd:entry>
    <imsmd:langstring>Understand</imsmd:langstring>    <!-- Value -->
  </imsmd:entry>
</imsmd:taxon>
```

### Multi-select Metadata (multiple `<imsmd:taxon>` with same Field name)
```xml
<imsmd:taxon>
  <imsmd:id>Område Biologi</imsmd:id>
  <imsmd:entry>
    <imsmd:langstring>cellbiologi</imsmd:langstring>
  </imsmd:entry>
</imsmd:taxon>
<imsmd:taxon>
  <imsmd:id>Område Biologi</imsmd:id>
  <imsmd:entry>
    <imsmd:langstring>fysiologi</imsmd:langstring>
  </imsmd:entry>
</imsmd:taxon>
```

### Applies to Both Questions AND Question Sets

| Level | Resource Type | Can have Labels? | Can have Custom Metadata? |
|-------|--------------|------------------|---------------------------|
| **Question Set** | `imsqti_test_xmlv2p2` | ✅ Yes | ✅ Yes |
| **Question** | `imsqti_item_xmlv2p2` | ✅ Yes | ✅ Yes |

---

## Decided MQG Format

### Question Level: `^custom_metadata`
```markdown
# Q001 Prokaryot vs Eukaryot
^question Q001
^type multiple_choice_single
^identifier MC_Q001
^points 1
^labels #Easy #BIOG001X #Prokaryot                          # Labels (free-form)
^custom_metadata Nivåer: nivå 1                             # Single-select
^custom_metadata Område Biologi: cellbiologi, fysiologi     # Multi-select (comma-separated)
```

**Format:** `^custom_metadata Field name: value` or `^custom_metadata Field name: value1, value2, value3`

### Question Set Level: YAML Frontmatter
```yaml
---
title: "Biology Quiz"
language: sv
custom_metadata:
  Nivåer: nivå 1
  Område Biologi: cellbiologi, fysiologi, genetik
---
```

### Summary

| Level | Labels | Custom Metadata |
|-------|--------|-----------------|
| **Question** | `^labels #Easy #Topic` | `^custom_metadata Field: value` |
| **Question Set** | YAML `labels:` | YAML `custom_metadata:` |

---

## Design Decisions

1. **Field name** - Use `^custom_metadata` (matches Inspera terminology, distinct from `^type`, `^labels`)
2. **Multi-select** - Comma-separated values on single line
3. **Validation** - No validation against predefined fields (Inspera handles this on import)
4. **Question Set** - Use YAML frontmatter (already used for quiz-level metadata)

---

## Files to Modify

### Parser
- `src/parser/markdown_parser.py` - Parse new metadata format

### Generator
- `src/generator/manifest_generator.py` - Generate `<imsmd:taxon>` with `<imsmd:id>`
- Possibly new template for metadata structure

### Validator
- `validate_mqg_format.py` - Validate metadata format

---

## Implementation Status

1. [x] Decide on MQG format - `^custom_metadata Field: value`
2. [x] Parser support - `src/parser/markdown_parser.py` (lines 336-351)
3. [x] Manifest generator - `src/packager/qti_packager.py` (lines 474-485)
4. [x] Validation support - `validate_mqg_format.py` (lines 333-334, 462-466)
5. [x] Test fixture - `tests/fixtures/v65/custom_metadata.md`
6. [ ] Test with Inspera import (pending user validation)

---

## References

- Inspera Help: "Create and manage Custom Metadata"
- Inspera Help: "Tagging content with Custom Metadata"
- Inspera Help: "Add labels to questions"
- Sample QTI: `251218_ItemBanking_metadata_questionset/imsmanifest.xml`
