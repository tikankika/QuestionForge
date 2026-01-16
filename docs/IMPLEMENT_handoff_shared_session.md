# IMPLEMENT_handoff: Shared Session (P1-P5)

**Date:** 2026-01-14
**Updated:** 2026-01-16
**For:** Claude Code
**Priority:** HIGH
**Status:** ✅ COMPLETED (2026-01-16)
**Related:** ADR-014, qf-scaffolding-spec.md v2.2, WORKFLOW.md

---

## Overview

Implementera delad session mellan qf-pipeline och qf-scaffolding.
Denna handoff täcker P1-P5 (qf-pipeline ändringar).

**Pending Items:**
| ID | Beslut | Status |
|----|--------|--------|
| P1 | `step0_start` behöver `materials_folder` param | ✅ DONE |
| P2 | `step0_start` behöver `entry_point` param | ✅ DONE |
| P3 | `init` output ska inkludera A/B/C/D routing | ✅ DONE |
| P4 | Projektstruktur: `00_materials/` | ✅ DONE |
| P5 | Projektstruktur: `methodology/` | ✅ DONE |

---

## P3: Update Init Output

**File:** `packages/qf-pipeline/src/qf_pipeline/server.py`

**Function:** `handle_init()`

**Current output:** (se server.py rad ~480)

**New output:**

```python
async def handle_init() -> List[TextContent]:
    """Handle init tool call - return critical instructions."""
    instructions = """# QuestionForge - Kritiska Instruktioner

## STEG 1: FRÅGA VAD ANVÄNDAREN HAR

"Vad har du att börja med?"

A) **Material** (föreläsningar, slides, transkriberingar)
   → Du vill SKAPA frågor från scratch
   → Använd M1-M4 metodologi (qf-scaffolding)

B) **Lärandemål / Kursplan**
   → Du har redan mål, vill planera assessment
   → Börja M2 (qf-scaffolding)

C) **Blueprint / Plan**
   → Du har redan plan, vill generera frågor
   → Börja M3 (qf-scaffolding)

D) **Markdown-fil med frågor**
   → Du vill VALIDERA eller EXPORTERA
   → Använd Pipeline direkt (step2 → step4)

## STEG 2: SKAPA SESSION

EFTER användaren svarat, kör step0_start:
- Fråga: "Var ska projektet sparas?" (output_folder)
- Fråga: "Vad ska projektet heta?" (project_name, valfritt)
- För A: Fråga "Var ligger materialet?" (materials_folder)
- För B/C: Fråga "Var ligger filen?" (source_file)
- För D: Fråga "Vilken markdown-fil?" (source_file)

## STEG 3: VÄG BASERAT PÅ VAL

A) → list_modules (qf-scaffolding) → load_stage(m1, 0)
B) → list_modules (qf-scaffolding) → load_stage(m2, 0)
C) → list_modules (qf-scaffolding) → load_stage(m3, 0)
D) → step2_validate → step4_export

## REGLER

1. **VÄNTA** på svar innan du fortsätter
2. **GISSA INTE** sökvägar - fråga alltid
3. **VALIDERA** alltid innan export (step2 före step4)
"""
    return [TextContent(type="text", text=instructions)]
```

---

## P1 + P2: Update step0_start

**File:** `packages/qf-pipeline/src/qf_pipeline/server.py`

### Update Tool Definition

**Location:** `list_tools()` function, find `step0_start` Tool

```python
Tool(
    name="step0_start",
    description="Start a new session OR load existing. For new: provide output_folder + entry_point. For existing: provide project_path.",
    inputSchema={
        "type": "object",
        "properties": {
            # EXISTING
            "source_file": {
                "type": "string",
                "description": "Path to markdown file (for entry_point B/C/D)",
            },
            "output_folder": {
                "type": "string",
                "description": "Directory where project will be created",
            },
            "project_name": {
                "type": "string",
                "description": "Optional project name (auto-generated if not provided)",
            },
            "project_path": {
                "type": "string",
                "description": "LOAD SESSION: Path to existing project directory",
            },
            # NEW (P1)
            "materials_folder": {
                "type": "string",
                "description": "Path to folder with instructional materials (for entry_point A)",
            },
            # NEW (P2)
            "entry_point": {
                "type": "string",
                "description": "Entry point: 'materials' (A), 'objectives' (B), 'blueprint' (C), 'questions' (D)",
                "enum": ["materials", "objectives", "blueprint", "questions"],
            },
        },
    },
),
```

### Update Handler

**Location:** `handle_step0_start()` function

```python
async def handle_step0_start(arguments: dict) -> List[TextContent]:
    """Handle step0_start - create new session OR load existing."""

    # Load existing session (unchanged)
    if arguments.get("project_path"):
        result = await load_session_tool(arguments["project_path"])
        # ... existing code ...

    # Create new session (UPDATED)
    output_folder = arguments.get("output_folder")
    if not output_folder:
        return [TextContent(
            type="text",
            text="Error: output_folder krävs för ny session"
        )]

    # NEW: Get entry_point
    entry_point = arguments.get("entry_point", "questions")  # Default to D
    
    # NEW: Validate input based on entry_point
    source_file = arguments.get("source_file")
    materials_folder = arguments.get("materials_folder")
    
    if entry_point == "materials" and not materials_folder:
        return [TextContent(
            type="text",
            text="Error: materials_folder krävs för entry_point 'materials' (A)"
        )]
    
    if entry_point in ["objectives", "blueprint", "questions"] and not source_file:
        return [TextContent(
            type="text",
            text=f"Error: source_file krävs för entry_point '{entry_point}'"
        )]

    # Create session with new params
    result = await start_session_tool(
        source_file=source_file,
        output_folder=output_folder,
        project_name=arguments.get("project_name"),
        materials_folder=materials_folder,      # NEW
        entry_point=entry_point                 # NEW
    )

    if result.get("success"):
        # ... existing logging ...
        
        # NEW: Route guidance based on entry_point
        next_step = {
            "materials": "Kör list_modules (qf-scaffolding) → börja M1",
            "objectives": "Kör list_modules (qf-scaffolding) → börja M2",
            "blueprint": "Kör list_modules (qf-scaffolding) → börja M3",
            "questions": "Kör step2_validate → step4_export",
        }.get(entry_point, "")
        
        return [TextContent(
            type="text",
            text=f"Session startad!\n"
                 f"  Session ID: {result['session_id']}\n"
                 f"  Projekt: {result['project_path']}\n"
                 f"  Entry point: {entry_point}\n"
                 f"  Arbetsfil: {result.get('working_file', 'N/A')}\n\n"
                 f"Nästa steg: {next_step}"
        )]
    # ... rest of error handling ...
```

---

## P1 + P2: Update SessionManager

**File:** `packages/qf-pipeline/src/qf_pipeline/utils/session_manager.py`

### Update create_session method

```python
def create_session(
    self,
    source_file: str,
    output_folder: str,
    project_name: Optional[str] = None,
    materials_folder: Optional[str] = None,    # NEW (P1)
    entry_point: Optional[str] = None          # NEW (P2)
) -> dict:
    """Create a new session with project structure."""
    
    # ... existing validation ...
    
    # Create project structure (UPDATED for P4, P5)
    project_path = Path(output_folder) / (project_name or self._generate_name(source_file))
    
    # Create directories
    (project_path / "00_materials").mkdir(parents=True, exist_ok=True)    # NEW (P4)
    (project_path / "01_source").mkdir(exist_ok=True)
    (project_path / "02_working").mkdir(exist_ok=True)
    (project_path / "03_output").mkdir(exist_ok=True)
    (project_path / "methodology").mkdir(exist_ok=True)                   # NEW (P5)
    
    # Copy materials if provided (NEW)
    if materials_folder:
        materials_src = Path(materials_folder)
        if materials_src.exists():
            for item in materials_src.iterdir():
                if item.is_file():
                    shutil.copy2(item, project_path / "00_materials" / item.name)
    
    # Copy source file if provided
    working_file = None
    if source_file:
        source_path = Path(source_file)
        if source_path.exists():
            shutil.copy2(source_path, project_path / "01_source" / source_path.name)
            working_file = project_path / "02_working" / source_path.name
            shutil.copy2(source_path, working_file)
    
    # Create session.yaml (UPDATED)
    session_data = {
        "session_id": self._generate_session_id(),
        "created_at": datetime.now().isoformat(),
        "source_file": str(source_file) if source_file else None,
        "working_file": str(working_file) if working_file else None,
        "output_folder": str(project_path / "03_output"),
        "validation_status": "pending",
        "question_count": 0,
        "exports": [],
        
        # NEW: Methodology section (P2)
        "methodology": {
            "entry_point": entry_point or "questions",
            "active_module": None,
            "m1": {"status": "not_started", "loaded_stages": [], "outputs": {}},
            "m2": {"status": "not_started", "loaded_stages": [], "outputs": {}},
            "m3": {"status": "not_started", "loaded_stages": [], "outputs": {}},
            "m4": {"status": "not_started", "loaded_stages": [], "outputs": {}},
        }
    }
    
    # Save session.yaml
    with open(project_path / "session.yaml", "w") as f:
        yaml.dump(session_data, f, default_flow_style=False)
    
    # ... rest of method ...
```

---

## P4 + P5: Project Structure

After implementation, `step0_start` should create:

```
project_name/
├── 00_materials/           ← NEW (P4) - copied from materials_folder
├── 01_source/              ← Original markdown
├── 02_working/             ← Working copy
├── 03_output/              ← QTI export
├── methodology/            ← NEW (P5) - for M1-M4 outputs
│   └── (empty initially)
├── session.yaml            ← Extended with methodology section
└── logs/
```

---

## Testing

### Test 1: Entry Point A (Materials)

```bash
# In Claude conversation:
User: "Jag vill skapa quiz från föreläsningar"
Claude: init → visar A/B/C/D
User: "A"
Claude: "Var ligger materialet?"
User: "/path/to/lectures"
Claude: "Var ska projektet sparas?"
User: "/path/to/output"
Claude: step0_start(
    output_folder="/path/to/output",
    materials_folder="/path/to/lectures",
    entry_point="materials"
)

# Verify:
# - 00_materials/ contains copied files
# - methodology/ exists
# - session.yaml has methodology.entry_point = "materials"
# - Output says "Nästa steg: list_modules → börja M1"
```

### Test 2: Entry Point D (Questions)

```bash
# In Claude conversation:
User: "Jag har quiz-frågor att exportera"
Claude: init → visar A/B/C/D
User: "D"
Claude: "Vilken markdown-fil?"
User: "/path/to/questions.md"
Claude: step0_start(
    output_folder="/path/to/output",
    source_file="/path/to/questions.md",
    entry_point="questions"
)

# Verify:
# - 01_source/ contains questions.md
# - 02_working/ contains working copy
# - session.yaml has methodology.entry_point = "questions"
# - Output says "Nästa steg: step2_validate → step4_export"
```

### Test 3: Load Existing Session

```bash
# Should still work unchanged
step0_start(project_path="/path/to/existing/project")

# Verify:
# - Loads session.yaml
# - Returns existing session status
```

---

## Files to Modify

| File | Changes |
|------|---------|
| `server.py` | Update `handle_init()`, `list_tools()`, `handle_step0_start()` |
| `session_manager.py` | Update `create_session()` |
| `tools/session.py` | Update `start_session_tool()` signature |

---

## Completion Checklist

- [x] P1: `materials_folder` param added to step0_start ✅
- [x] P2: `entry_point` param added to step0_start ✅
- [x] P3: init output includes m1/m2/m3/m4/pipeline routing ✅
- [x] P4: 00_materials/ directory created ✅
- [x] P5: methodology/ directory created ✅
- [x] session.yaml includes methodology section ✅
- [x] Test: Entry point m1 works ✅
- [x] Test: Entry point pipeline works (backward compatible) ✅
- [x] Test: Load existing session works ✅

---

## After Implementation

1. Update ACDM-logg: Mark P1-P5 as DONE
2. Test with qf-scaffolding (when implemented)
3. Create IMPLEMENT_handoff for P6-P7 (qf-scaffolding)

---

*Handoff created: 2026-01-14*
