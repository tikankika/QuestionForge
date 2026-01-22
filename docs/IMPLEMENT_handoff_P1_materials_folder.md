# IMPLEMENT_handoff: P1 - materials_folder Parameter

**Date:** 2026-01-15
**Updated:** 2026-01-16
**For:** Claude Code
**Priority:** HIGH
**Status:** ✅ COMPLETED (2026-01-16)
**Related:** HANDOFF_STATUS_ANALYSIS.md, ADR-014, qf-scaffolding-spec.md v2.2

---

## Overview

Implement `materials_folder` parameter for entry point `m1` to enable automatic copying of instructional materials into project structure.

**Problem:**
- Entry point `m1` (Content Analysis) requires materials (PDFs, slides, transcripts)
- Currently: User must MANUALLY copy files to `00_materials/` (bad UX)
- Other entry points (m2/m3/m4/pipeline) automatically copy source_file
- Inconsistent architecture

**Solution:**
- Add `materials_folder` parameter to `step0_start`
- Copy ALL files AND subdirectories from `materials_folder` to `project/00_materials/`
- Filter out junk files (.DS_Store, Thumbs.db, etc.)
- Same pattern as existing source_file copying

---

## Architecture Decision

**WHY copy at session start (step0_start)?**

✅ **Self-contained projects** - everything in one place  
✅ **Shareable** - can send entire project to colleague  
✅ **Protects originals** - M1 can't accidentally modify source files  
✅ **Consistent** - same logic as source_file for other entry points  
✅ **Reproducible** - project works even if Nextcloud folder moves  

**Alternative rejected:** M1 reading directly from Nextcloud
- ❌ Not self-contained
- ❌ Can't share projects
- ❌ Breaks if source folder moves
- ❌ Inconsistent with other entry points

---

## Implementation Plan

### Files to Modify

| File | Changes | Lines |
|------|---------|-------|
| `server.py` | Add parameter to tool definition | ~10 |
| `server.py` | Add validation in handler | ~15 |
| `session_manager.py` | Add parameter to create_session() | ~5 |
| `session_manager.py` | Implement copying logic | ~25 |
| `tools/session.py` | Update start_session_tool() signature | ~5 |

**Total:** ~60 lines of new code

---

## STEP 1: Update server.py Tool Definition

**File:** `packages/qf-pipeline/src/qf_pipeline/server.py`

**Location:** In `list_tools()` function, find `step0_start` Tool definition (around line 82)

**Add new parameter in inputSchema.properties:**

```python
Tool(
    name="step0_start",
    description=(
        "Start a new session OR load existing. "
        "For new: provide output_folder + entry_point (+ source_file for m2/m3/m4/pipeline OR materials_folder for m1). "
        "source_file can be a local path OR a URL (auto-fetched as .md). "
        "For existing: provide project_path."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "output_folder": {
                "type": "string",
                "description": "NEW SESSION: Directory where project will be created",
            },
            "source_file": {
                "type": "string",
                "description": "NEW SESSION: Path OR URL to source (required for m2/m3/m4/pipeline). URLs auto-fetched to .md",
            },
            "project_name": {
                "type": "string",
                "description": "NEW SESSION: Optional project name (auto-generated if not provided)",
            },
            "entry_point": {
                "type": "string",
                "description": (
                    "NEW SESSION: Entry point - "
                    "'m1' (material), 'm2' (lärandemål), 'm3' (blueprint), 'm4' (QA), 'pipeline' (direkt). "
                    "Default: 'pipeline'"
                ),
                "enum": ["m1", "m2", "m3", "m4", "pipeline"],
            },
            # NEW PARAMETER (P1)
            "materials_folder": {
                "type": "string",
                "description": "NEW SESSION: Path to folder containing instructional materials (required for entry_point m1). Entire folder structure copied to 00_materials/ (junk files filtered).",
            },
            "project_path": {
                "type": "string",
                "description": "LOAD SESSION: Path to existing project directory",
            },
        },
    },
),
```

---

## STEP 2: Update server.py Handler

**File:** `packages/qf-pipeline/src/qf_pipeline/server.py`

**Location:** In `handle_step0_start()` function (around line 515)

**Add validation AFTER entry_point validation, BEFORE calling start_session_tool:**

```python
async def handle_step0_start(arguments: dict) -> List[TextContent]:
    """Handle step0_start - create new session OR load existing."""

    # Load existing session (unchanged)
    if arguments.get("project_path"):
        result = await load_session_tool(arguments["project_path"])
        # ... existing code ...

    # Create new session - requires output_folder (unchanged)
    if not arguments.get("output_folder"):
        return [TextContent(
            type="text",
            text=(
                "Error: output_folder krävs för ny session.\n\n"
                "Användning:\n"
                "  - Ny session: output_folder + entry_point (+ source_file för m2/m3/m4/pipeline)\n"
                "  - Ladda befintlig: project_path\n\n"
                "Entry points:\n"
                "  - m1: Börja från undervisningsmaterial (Content Analysis)\n"
                "  - m2: Börja från lärandemål (Assessment Design)\n"
                "  - m3: Börja från blueprint (Question Generation)\n"
                "  - m4: Börja från frågor för QA (Quality Assurance)\n"
                "  - pipeline: Validera och exportera direkt [default]"
            )
        )]

    # Get entry_point (default to "pipeline") - unchanged
    entry_point = arguments.get("entry_point", "pipeline")

    # === NEW: Validate materials_folder for m1 entry point ===
    materials_folder = arguments.get("materials_folder")
    
    if entry_point == "m1":
        if not materials_folder:
            return [TextContent(
                type="text",
                text=(
                    "Error: materials_folder krävs för entry point 'm1'.\n\n"
                    "Entry point m1 (Content Analysis) startar från undervisningsmaterial.\n"
                    "Ange sökväg till mapp med:\n"
                    "  - Presentationer (PDF, PPTX)\n"
                    "  - Föreläsningsanteckningar\n"
                    "  - Transkriptioner\n"
                    "  - Läroböcker/artiklar\n\n"
                    "Exempel:\n"
                    "  materials_folder='/Users/niklas/Nextcloud/Biologi_VT2025/Föreläsningar'"
                )
            )]
        
        # Validate materials_folder exists and is directory
        materials_path = Path(materials_folder)
        if not materials_path.exists():
            return [TextContent(
                type="text",
                text=f"Error: materials_folder finns inte: {materials_folder}"
            )]
        
        if not materials_path.is_dir():
            return [TextContent(
                type="text",
                text=f"Error: materials_folder är inte en mapp: {materials_folder}"
            )]
    
    # If materials_folder provided for non-m1 entry point, warn but continue
    if materials_folder and entry_point != "m1":
        logger.warning(
            f"materials_folder provided for '{entry_point}' entry point - "
            f"will be ignored. This parameter is only used for 'm1'."
        )
        materials_folder = None  # Clear it
    # === END NEW ===

    # Call start_session_tool WITH materials_folder
    result = await start_session_tool(
        output_folder=arguments["output_folder"],
        source_file=arguments.get("source_file"),
        project_name=arguments.get("project_name"),
        entry_point=entry_point,
        materials_folder=materials_folder  # NEW
    )

    # Rest of function unchanged...
```

---

## STEP 3: Update tools/session.py

**File:** `packages/qf-pipeline/src/qf_pipeline/tools/session.py`

**Location:** Find `start_session_tool()` function

**Update signature to include materials_folder:**

```python
async def start_session_tool(
    output_folder: str,
    source_file: Optional[str] = None,
    project_name: Optional[str] = None,
    entry_point: str = "pipeline",
    materials_folder: Optional[str] = None,  # NEW
    initial_sources: Optional[List[Dict[str, Any]]] = None
) -> dict:
    """Start a new session with project structure.
    
    Args:
        output_folder: Directory where project will be created
        source_file: Path to source file (required for m2/m3/m4/pipeline)
        project_name: Optional project name (auto-generated if not provided)
        entry_point: One of "m1", "m2", "m3", "m4", "pipeline"
        materials_folder: Path to folder with materials (required for m1)
        initial_sources: Optional list of initial sources for sources.yaml
    
    Returns:
        dict with success status, paths, and next_module
    """
    session_manager = SessionManager()
    return session_manager.create_session(
        output_folder=output_folder,
        source_file=source_file,
        project_name=project_name,
        entry_point=entry_point,
        materials_folder=materials_folder,  # NEW
        initial_sources=initial_sources
    )
```

---

## STEP 4: Update session_manager.py create_session()

**File:** `packages/qf-pipeline/src/qf_pipeline/utils/session_manager.py`

**Location:** In `create_session()` method (around line 205)

### 4a. Update method signature:

```python
def create_session(
    self,
    output_folder: str,
    source_file: Optional[str] = None,
    project_name: Optional[str] = None,
    entry_point: str = "pipeline",
    materials_folder: Optional[str] = None,  # NEW
    initial_sources: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Create a new session with project structure.

    Args:
        output_folder: Directory where project will be created
        source_file: Path to source file (required for m2/m3/m4/pipeline)
        project_name: Optional project name (auto-generated if not provided)
        entry_point: One of "m1", "m2", "m3", "m4", "pipeline"
        materials_folder: Path to folder with instructional materials (required for m1)
        initial_sources: Optional list of initial sources for sources.yaml
            Each source should have: path, type (optional), location (optional)

    Returns:
        dict with success status, paths, and next_module
    """
```

### 4b. Add materials copying logic:

**Location:** AFTER the folder creation loop (after line 278), BEFORE source_file copying

**IMPORTANT CHANGES from v1:**
- ✅ Uses `shutil.copytree` instead of manual loop (handles subdirectories)
- ✅ Filters junk files (.DS_Store, Thumbs.db, ~$*, .*)
- ✅ README.md only created if NO materials_folder provided
- ✅ Counts files recursively for accurate reporting

```python
            # Create directories (existing code)
            project_path.mkdir(parents=True, exist_ok=True)
            for folder in self.FOLDERS:
                folder_path = project_path / folder
                folder_path.mkdir(exist_ok=True)

                # MODIFIED: Only add README if materials_folder NOT provided
                # (otherwise README would be overwritten or cause confusion)
                if folder == "00_materials" and not materials_folder:
                    readme_path = folder_path / "README.md"
                    readme_path.write_text(
                        "# Undervisningsmaterial\n\n"
                        "Ladda upp allt material från din undervisning här:\n"
                        "- Presentationer (PDF, PPTX)\n"
                        "- Föreläsningsanteckningar\n"
                        "- Transkriptioner från inspelningar\n"
                        "- Läroböcker/artiklar som använts\n",
                        encoding="utf-8"
                    )

            # === NEW: Copy materials if provided (for m1 entry point) ===
            materials_copied = 0
            if materials_folder:
                materials_src = Path(materials_folder)
                materials_dest = project_path / "00_materials"

                logger.info(f"Copying materials from {materials_src} to {materials_dest}")

                # Define junk files to ignore
                def ignore_junk(directory, files):
                    """Ignore junk files and hidden files."""
                    ignored = []
                    for f in files:
                        # Ignore hidden files (except .md files which might be intentional)
                        if f.startswith('.') and not f.endswith('.md'):
                            ignored.append(f)
                        # Ignore OS junk
                        elif f in ('Thumbs.db', 'desktop.ini', 'ehthumbs.db'):
                            ignored.append(f)
                        # Ignore Office temp files
                        elif f.startswith('~$'):
                            ignored.append(f)
                        # Ignore Python cache
                        elif f == '__pycache__' or f.endswith('.pyc'):
                            ignored.append(f)
                    return ignored

                # Copy entire tree (including subdirectories)
                shutil.copytree(
                    materials_src,
                    materials_dest,
                    dirs_exist_ok=True,  # Merge with existing (00_materials already exists)
                    ignore=ignore_junk
                )

                # Count files recursively for reporting
                for item in materials_dest.rglob('*'):
                    if item.is_file():
                        materials_copied += 1

                logger.info(f"Copied {materials_copied} files to 00_materials/")
            # === END NEW ===

            # Copy methodology from QuestionForge (existing code continues...)
            methodology_result = copy_methodology(project_path)
```

### 4c. Update response to include materials info:

**Location:** At the end of create_session(), in the response dict (around line 355)

```python
            # Build response
            response = {
                "success": True,
                "session_id": session_id,
                "project_path": str(project_path),
                "output_folder": str(project_path / "03_output"),
                "entry_point": entry_point,
                "next_module": ep_config["next_module"],
                "pipeline_ready": entry_point == "pipeline",
                "methodology_copied": methodology_result.get("files_copied", 0),
                "sources_initialized": len(initial_sources) if initial_sources else 0,
                "materials_copied": materials_copied,  # NEW
            }

            # Add file paths if source was provided (existing code)
            if source_path:
                response["working_file"] = str(working_dest)
                response["source_file"] = str(source_dest)
                response["message"] = f"Session startad. Arbetar med: {source_path.name}"
            # NEW: Add message for materials
            elif materials_folder:
                response["working_file"] = None
                response["source_file"] = None
                response["materials_folder"] = str(materials_dest)  # NEW: include path
                response["message"] = (
                    f"Session startad med entry point '{entry_point}'. "
                    f"{materials_copied} filer kopierade till 00_materials/ (mappstruktur bevarad). "
                    f"Nästa steg: {ep_config['next_module']} (qf-scaffolding)"
                )
            else:
                response["working_file"] = None
                response["source_file"] = None
                response["message"] = (
                    f"Session startad med entry point '{entry_point}'. "
                    f"Nästa steg: {ep_config['next_module']} (qf-scaffolding)"
                )

            return response
```

### 4d. Update logging:

**Location:** Where log_event is called for session_created (around line 340)

```python
            # Log session creation
            log_event(
                project_path,
                "session_start",
                tool="step0_start",
                entry_point=entry_point,
                session_id=session_id
            )
            log_event(
                project_path,
                "session_created",
                tool="step0_start",
                methodology_files=methodology_result.get("files_copied", 0),
                sources_count=len(initial_sources) if initial_sources else 0,
                materials_copied=materials_copied  # NEW
            )
```

---

## STEP 5: Update session_manager.py validate_entry_point()

**File:** `packages/qf-pipeline/src/qf_pipeline/utils/session_manager.py`

**Location:** `validate_entry_point()` function (around line 90)

**Update to handle materials_folder:**

```python
def validate_entry_point(
    entry_point: str, 
    source_file: Optional[str],
    materials_folder: Optional[str] = None  # NEW
) -> None:
    """Validate entry point and source_file/materials_folder combination.

    Args:
        entry_point: One of "m1", "m2", "m3", "m4", "pipeline"
        source_file: Path to source file (required for m2/m3/m4/pipeline)
        materials_folder: Path to materials folder (required for m1)

    Raises:
        ValueError: If entry_point is invalid or requirements not met
    """
    if entry_point not in ENTRY_POINT_REQUIREMENTS:
        valid_options = list(ENTRY_POINT_REQUIREMENTS.keys())
        raise ValueError(
            f"Invalid entry point: '{entry_point}'. "
            f"Valid options: {valid_options}"
        )

    config = ENTRY_POINT_REQUIREMENTS[entry_point]

    # m1 requires materials_folder
    if entry_point == "m1":
        if not materials_folder:
            raise ValueError(
                f"Entry point 'm1' requires materials_folder.\n"
                f"Description: {config['description']}\n"
                f"Expected workflow: {' → '.join(config['next_steps'])}"
            )
        if source_file:
            logger.warning(
                f"source_file provided for 'm1' entry point - "
                f"will be ignored. Use materials_folder instead."
            )
    
    # Other entry points require source_file
    elif config["requires_source_file"] and not source_file:
        raise ValueError(
            f"Entry point '{entry_point}' requires source_file.\n"
            f"Description: {config['description']}\n"
            f"Expected workflow: {' → '.join(config['next_steps'])}"
        )

    # Warn if materials_folder provided for non-m1
    if materials_folder and entry_point != "m1":
        logger.warning(
            f"materials_folder provided for '{entry_point}' entry point - "
            f"will be ignored. This parameter is only used for 'm1'."
        )
```

**Then update the call to validate_entry_point in create_session():**

```python
        # Validate entry point and source_file combination
        try:
            validate_entry_point(entry_point, source_file, materials_folder)  # NEW param
        except ValueError as e:
            return {
                "success": False,
                "error": {
                    "type": "validation_error",
                    "message": str(e)
                }
            }
```

---

## Testing

### Test 1: Entry Point m1 with materials_folder

```python
# In Claude conversation:
User: "Jag vill skapa quiz från föreläsningar"
Claude: init → visar M1/M2/M3/M4/Pipeline
User: "M1"
Claude: "Var ligger materialet?"
User: "/Users/niklas/Nextcloud/Biologi_VT2025/Föreläsningar"
Claude: "Var ska projektet sparas?"
User: "/Users/niklas/AIED_Projects"
Claude: step0_start(
    output_folder="/Users/niklas/AIED_Projects",
    materials_folder="/Users/niklas/Nextcloud/Biologi_VT2025/Föreläsningar",
    entry_point="m1"
)

# Verify:
# 1. Project created: /Users/niklas/AIED_Projects/project_YYYYMMDD_HHMMSS/
# 2. 00_materials/ contains copied files (PDFs, PPTX, etc)
# 3. 00_materials/ subdirectory structure preserved (if any)
# 4. 00_materials/.DS_Store does NOT exist (filtered)
# 5. methodology/ contains copied methodology files
# 6. session.yaml has methodology.entry_point = "m1"
# 7. Output says "X filer kopierade till 00_materials/ (mappstruktur bevarad)"
# 8. Output says "Nästa steg: m1 (qf-scaffolding)"
```

### Test 2: Entry Point m1 WITHOUT materials_folder (should fail)

```python
Claude: step0_start(
    output_folder="/Users/niklas/AIED_Projects",
    entry_point="m1"
)

# Verify:
# Error message says:
# "Error: materials_folder krävs för entry point 'm1'."
# Includes helpful explanation about what to provide
```

### Test 3: materials_folder for wrong entry point (should warn)

```python
Claude: step0_start(
    output_folder="/Users/niklas/AIED_Projects",
    source_file="/path/to/objectives.md",
    materials_folder="/path/to/materials",  # Wrong - m2 uses source_file
    entry_point="m2"
)

# Verify:
# 1. Session creates successfully
# 2. materials_folder is IGNORED (not copied)
# 3. Warning logged: "materials_folder provided for 'm2' - will be ignored"
# 4. source_file IS copied to 01_source/
```

### Test 4: materials_folder doesn't exist (should fail)

```python
Claude: step0_start(
    output_folder="/Users/niklas/AIED_Projects",
    materials_folder="/nonexistent/path",
    entry_point="m1"
)

# Verify:
# Error message says: "Error: materials_folder finns inte: /nonexistent/path"
```

### Test 5: materials_folder is file not directory (should fail)

```python
Claude: step0_start(
    output_folder="/Users/niklas/AIED_Projects",
    materials_folder="/path/to/file.pdf",
    entry_point="m1"
)

# Verify:
# Error message says: "Error: materials_folder är inte en mapp: /path/to/file.pdf"
```

### Test 6: Empty materials_folder (should succeed)

```python
# Create empty folder
mkdir /tmp/empty_materials

Claude: step0_start(
    output_folder="/Users/niklas/AIED_Projects",
    materials_folder="/tmp/empty_materials",
    entry_point="m1"
)

# Verify:
# 1. Session creates successfully
# 2. Output says "0 filer kopierade till 00_materials/"
# 3. 00_materials/ exists but is empty (no auto-generated README)
#    NOTE: README only created if NO materials_folder provided
```

### Test 7: Subdirectories preserved (NEW)

```python
# Create nested structure
mkdir -p /tmp/test_materials/Vecka1
mkdir -p /tmp/test_materials/Vecka2
echo "test" > /tmp/test_materials/Vecka1/slides.pdf
echo "test" > /tmp/test_materials/Vecka2/notes.md

Claude: step0_start(
    output_folder="/Users/niklas/AIED_Projects",
    materials_folder="/tmp/test_materials",
    entry_point="m1"
)

# Verify:
# 1. 00_materials/Vecka1/slides.pdf exists
# 2. 00_materials/Vecka2/notes.md exists
# 3. Structure preserved
```

### Test 8: Junk files filtered (NEW)

```python
# Create folder with junk
mkdir /tmp/test_junk
echo "test" > /tmp/test_junk/lecture.pdf
echo "junk" > /tmp/test_junk/.DS_Store
echo "junk" > /tmp/test_junk/Thumbs.db
echo "junk" > /tmp/test_junk/~$temp.docx

Claude: step0_start(
    output_folder="/Users/niklas/AIED_Projects",
    materials_folder="/tmp/test_junk",
    entry_point="m1"
)

# Verify:
# 1. 00_materials/lecture.pdf exists
# 2. 00_materials/.DS_Store does NOT exist
# 3. 00_materials/Thumbs.db does NOT exist
# 4. 00_materials/~$temp.docx does NOT exist
# 5. Output says "1 filer kopierade" (not 4)
```

### Test 9: README.md not overwritten if in source (NEW)

```python
# Create folder with own README
mkdir /tmp/test_readme
echo "# My Materials" > /tmp/test_readme/README.md
echo "test" > /tmp/test_readme/lecture.pdf

Claude: step0_start(
    output_folder="/Users/niklas/AIED_Projects",
    materials_folder="/tmp/test_readme",
    entry_point="m1"
)

# Verify:
# 1. 00_materials/README.md contains "# My Materials" (user's version)
# 2. NOT the auto-generated "Ladda upp..." text
```

---

## Edge Cases

### Large files
- shutil.copytree handles large files
- No size limit enforced (user's disk space problem)

### File permissions
- Copying preserves permissions (shutil.copytree with copy_function=copy2)
- If dest is read-only, copy will fail gracefully

### Subdirectories
- ✅ **FIXED in v2:** Full tree copied with subdirectories preserved
- Uses `shutil.copytree` with `dirs_exist_ok=True`

### Junk files
- ✅ **NEW in v2:** Filtered out automatically
- .DS_Store, Thumbs.db, ~$*, hidden files (except .md)

### README.md handling
- ✅ **FIXED in v2:** Auto-generated README only if NO materials_folder
- If user has own README.md in materials, it's preserved

### Symbolic links
- `shutil.copytree` follows symlinks by default
- If this causes issues, add `symlinks=True` to preserve symlinks

### Duplicate filenames
- If materials_folder has "lecture.pdf" and user later copies another "lecture.pdf"
- Second copy OVERWRITES first (shutil default behavior)
- This is acceptable for now

### Partial copy failure
- If copy fails mid-tree, partial files may remain
- Consider: wrap in try/except and clean up on failure (Phase 2)

---

## Completion Checklist

### Implementation
- [x] Updated `server.py` tool definition with materials_folder parameter ✅
- [x] Updated `server.py` handle_step0_start() with validation ✅
- [x] Updated `tools/session.py` start_session_tool() signature ✅
- [x] Updated `session_manager.py` create_session() signature ✅
- [x] Implemented materials copying logic with `shutil.copytree` ✅
- [x] Added `ignore_junk()` function for filtering ✅
- [x] Modified README.md logic (only if no materials_folder) ✅
- [x] Updated validate_entry_point() to handle materials_folder ✅
- [x] Updated response dict to include materials_copied ✅
- [x] Updated logging to include materials_copied ✅

### Testing
- [x] Test 1: m1 with materials_folder works ✅
- [x] Test 2: m1 without materials_folder fails correctly ✅
- [x] Test 3: materials_folder ignored for non-m1 ✅
- [x] Test 4: Non-existent folder fails correctly ✅
- [x] Test 5: File instead of folder fails correctly ✅
- [x] Test 6: Empty folder works ✅
- [x] Test 7: Subdirectories preserved ✅
- [x] Test 8: Junk files filtered ✅
- [x] Test 9: README.md from source preserved ✅

---

## After Implementation

1. Update ACDM log: Mark P1 as DONE ✅
2. Test with real Nextcloud folder
3. Document in CHANGELOG.md
4. Continue to P6-P7 (qf-scaffolding)

---

## Changelog

### v2 (2026-01-15)
- **BREAKING:** Changed from manual file loop to `shutil.copytree`
- **NEW:** Subdirectories now preserved (was: flattened)
- **NEW:** Junk file filtering (.DS_Store, Thumbs.db, ~$*, hidden)
- **FIX:** README.md only auto-generated if no materials_folder
- **NEW:** Tests 7-9 added for new functionality

### v1 (2026-01-15)
- Initial handoff

---

*Handoff created: 2026-01-15*
*Last updated: 2026-01-15 (v2)*
*Implementation time: ~1.5 hours*
