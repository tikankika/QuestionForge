# ADR-015: Flexible Project Initialization

**Status:** Implemented ✅
**Date:** 2026-01-30
**Deciders:** Niklas Karlsson, Claude
**Related:** RFC-017 (Existing Questions Entry Point)

---

## Context

Current `step0_start` requires both `entry_point` and source files at project creation:

```python
# Current - must know everything at start
step0_start(
    entry_point="m3",           # Must choose
    source_file="blueprint.md", # Must have file
    output_folder="..."
)
```

**Problem:**
- Teachers must know "entry point" terminology
- File must exist and be accessible at project creation
- Cannot create project first, add materials later
- No flexibility for iterative work

---

## Decision

**Separate project creation from file handling and entry point selection.**

New flow:

```
1. step0_start()      → Create empty project
2. step0_add_file()   → Add file(s), can be called multiple times
3. step0_analyze()    → System suggests appropriate flow
```

---

## New Tools

### step0_start (updated)

```python
step0_start(
    output_folder: str,
    project_name: str = None,      # Auto-generated if not provided
    # entry_point: OPTIONAL now (can be set later)
    # source_file: OPTIONAL now (use step0_add_file instead)
)
```

Returns: Project path, ready for files

### step0_add_file (new)

```python
step0_add_file(
    project_path: str,
    file: str,                     # Path or URL
    file_type: str = "auto",       # auto | questions | materials | blueprint | resources
    convert: bool = True,          # Convert via MarkItDown if needed
)
```

Behavior:
- `file_type="auto"` → Detect based on content/extension
- docx/xlsx/pdf → Convert to markdown via MarkItDown MCP
- Images/audio → Copy to `questions/resources/`
- Can be called multiple times

### step0_analyze (new)

```python
step0_analyze(
    project_path: str
)
```

Returns:
```yaml
files_found:
  - questions/source.md (20 questions detected)
  - questions/resources/ (5 images)

recommended_flow: "M5 → Pipeline"
alternatives:
  - "M4 → M5 → Pipeline (review first)"
  - "M2 → M5 → Pipeline (add taxonomy)"

next_step: "Run m5_start() to begin format conversion"
```

---

## Consequences

### Positive
- Teachers don't need to understand "entry points"
- Projects can be created before materials exist
- Iterative work possible (add more files later)
- System guides based on what actually exists

### Negative
- More tool calls (3 instead of 1)
- Existing flow must be updated

### Neutral
- Backwards compatibility: `step0_start(entry_point=..., source_file=...)` still works

---

## Implementation

1. ✅ Update `step0_start` to make `entry_point` and `source_file` optional
2. ✅ Add `step0_add_file` tool with MarkItDown integration
3. ✅ Add `step0_analyze` tool with content detection
4. ✅ Update session.yaml to track added files
5. ✅ Update `init` tool documentation

---

## UX: Guided File Collection

After `step0_start(entry_point="setup")`, the system prompts:

```
═══════════════════════════════════════════════════════
ASK TEACHER: Which files should be added?
═══════════════════════════════════════════════════════

📝 EXAMS/QUESTIONS to convert?
   (Word, Excel, PDF with existing questions)

📚 TEACHING MATERIALS?
   (Lectures, slides, transcripts)

🖼️  RESOURCES (images, audio, video)?
   (Figures, diagrams, audio clips for questions)
```

After each `step0_add_file()`, the system asks:

```
MORE FILES TO ADD?

📚 Teaching materials? (slides, lectures)
🖼️  Resources? (images, audio, video for questions)
📝 More exams/questions?

If YES: Use step0_add_file again
If NO: Run step0_analyze to continue
```

---

*ADR-015 created 2026-01-30, implemented 2026-01-30*
