# ADR-009: Resource Handling in Export

**Status:** Proposed  
**Date:** 2026-01-06  
**Deciders:** Niklas  
**Priority:** 🔴 CRITICAL

---

## Context

Claude Code's deep analysis revealed a **critical bug**: `resources.py` wrapper exists in qf-pipeline but is **never called** during export. This means:

- Images referenced in questions are NOT copied to the QTI package
- QTI packages with images **do not work in Inspera**
- The wrapper code exists and is functional, just unused

### Current flow (broken)

```python
# server.py:handle_step4_export()
async def handle_step4_export(arguments: dict):
    # ...
    data = parse_file(file_path)           # ✅ Parse markdown
    questions = data.get("questions", [])
    xml_list = generate_all_xml(questions) # ✅ Generate XML
    result = create_qti_package(xml_list)  # ✅ Create ZIP
    # 🔴 MISSING: copy_resources() never called!
```

### QTI-Generator flow (correct)

```
Step 1: Validate markdown
Step 2: Create output folder
Step 3: Copy resources     ← THIS IS MISSING
Step 4: Generate XML
Step 5: Create ZIP
```

---

## Decision

### Option A: Integrate into step4_export (RECOMMENDED)

Add resource handling directly into the existing export flow.

```python
async def handle_step4_export(arguments: dict):
    # ... existing code ...
    
    # NEW: Validate and copy resources BEFORE XML generation
    from .wrappers import validate_resources, copy_resources
    
    # 1. Validate resources exist
    resource_validation = validate_resources(
        input_file=file_path,
        questions=questions,
        strict=False
    )
    
    if not resource_validation["valid"]:
        issues = resource_validation["issues"]
        return [TextContent(
            type="text",
            text=f"Resource validation failed:\n" + 
                 "\n".join(f"  - {i['message']}" for i in issues)
        )]
    
    # 2. Copy resources to output directory
    copy_result = copy_resources(
        input_file=file_path,
        output_dir=str(output_folder),
        questions=questions
    )
    
    # 3. Generate XML (existing code)
    xml_list = generate_all_xml(questions, language)
    
    # 4. Create package (existing code)
    result = create_qti_package(xml_list, metadata, output_path)
    
    # Include resource info in response
    return [TextContent(
        type="text",
        text=f"QTI package created!\n"
             f"  ZIP: {result.get('zip_path')}\n"
             f"  Questions: {len(questions)}\n"
             f"  Resources: {copy_result.get('count', 0)} files copied"
    )]
```

**Pros:**
- Minimal changes
- Maintains simple workflow
- Resources always included

**Cons:**
- No separate resource validation step
- Can't skip resources if not needed

### Option B: Add step3_resources tool

Create separate tool for resource handling.

```python
Tool(
    name="step3_resources",
    description="Validate and copy resources (images, media) for QTI export.",
    inputSchema={
        "type": "object",
        "properties": {
            "validate_only": {
                "type": "boolean",
                "description": "Only validate, don't copy",
                "default": False
            }
        }
    }
)
```

**Pros:**
- Explicit step, matches QTI-Generator
- Can validate before committing
- More control

**Cons:**
- Extra step for users
- Risk of forgetting to run it

### Decision: Option A with validation warning

Integrate into step4_export but log warnings for missing resources rather than failing completely (unless strict mode).

---

## Implementation

### Files to modify

| File | Change |
|------|--------|
| `server.py:handle_step4_export()` | Add resource validation and copying |
| `wrappers/__init__.py` | Already exports `copy_resources`, `validate_resources` ✅ |

### Code changes

```python
# In server.py, add at top:
from .wrappers import (
    # ... existing imports ...
    validate_resources,
    copy_resources,
)

# In handle_step4_export(), BEFORE xml_list = generate_all_xml():

# Validate resources
resource_result = validate_resources(
    input_file=file_path,
    questions=questions,
    media_dir=None,  # Auto-detect
    strict=False
)

# Log warnings but continue
if resource_result["warning_count"] > 0:
    for issue in resource_result["issues"]:
        if issue["level"] == "WARNING":
            log_action(session.project_path, "step4_export", 
                      f"Resource warning: {issue['message']}")

# Fail on errors
if resource_result["error_count"] > 0:
    error_msgs = [i["message"] for i in resource_result["issues"] 
                  if i["level"] == "ERROR"]
    return [TextContent(
        type="text",
        text=f"Resource errors:\n" + "\n".join(f"  - {m}" for m in error_msgs)
    )]

# Copy resources to output
copy_result = copy_resources(
    input_file=file_path,
    output_dir=str(output_folder),
    questions=questions
)

resource_count = copy_result.get("count", 0)

# Continue with existing XML generation...
```

---

## Consequences

### Positive
- QTI packages with images will work in Inspera
- Uses existing, tested wrapper code
- Minimal workflow change for users

### Negative
- Export may fail if images missing (but this is correct behavior)
- Slightly slower export (file copying)

### Neutral
- Existing packages without images unaffected

---

## Testing

```python
def test_export_with_images():
    """Export with images should include resources."""
    # Create test markdown with image
    # Run step4_export
    # Verify ZIP contains image files
    
def test_export_missing_image_fails():
    """Export should fail if referenced image missing."""
    # Create markdown referencing non-existent image
    # Run step4_export
    # Verify error returned

def test_export_no_images_works():
    """Export without images should work as before."""
    # Create markdown without images
    # Run step4_export
    # Verify success
```

---

## References

- Claude Code analysis: 2026-01-06
- QTI-Generator step3: `scripts/step3_copy_resources.py`
- Wrapper: `wrappers/resources.py`
- Consolidated analysis: `acdm/logs/2026-01-06_DISCOVER_consolidated_analysis.md`

---

*ADR-009 | QuestionForge | 2026-01-06 | CRITICAL*
