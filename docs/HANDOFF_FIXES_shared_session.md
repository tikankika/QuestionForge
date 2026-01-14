# HANDOFF FIXES: Shared Session Implementation

**Baserat på analys från Windsurf session**

**Datum:** 2026-01-14
**Status:** 3 problem identifierade, ~90% korrekt

---

## ENTRY POINTS ÖVERSIKT (4 st)

| ID | Entry Point | source_file? | Nästa Modul | Beskrivning |
|----|-------------|--------------|-------------|-------------|
| **A** | materials | ❌ Nej (valfri) | M1 (scaffolding) | Börja från undervisningsmaterial |
| **B** | objectives | ✅ Ja (krävs) | M2 (scaffolding) | Börja från learning objectives |
| **C** | blueprint | ✅ Ja (krävs) | M3 (scaffolding) | Börja från assessment plan |
| **D** | questions | ✅ Ja (krävs) | Pipeline direkt | Validera färdiga frågor |

**Workflow per entry point:**
- **A:** Materials → Objectives → Blueprint → Questions → QTI
- **B:** Objectives → Blueprint → Questions → QTI
- **C:** Blueprint → Questions → QTI
- **D:** Questions → Validate → Transform → QTI

---

## Problem 1: source_file måste vara Optional

### Nuvarande kod
```python
def create_session(self, source_file: str, ...)  # REQUIRED
```

### Problem
För entry_point A (materials) finns ingen source_file. Användaren börjar med material-analys och har ännu ingen källfil.

### Fix
```python
def create_session(
    self,
    source_file: Optional[str] = None,  # FIX: Gör valfri
    output_folder: str,
    project_name: Optional[str] = None,
    entry_point: str = "materials"  # A, B, C, eller D
) -> Dict[str, Any]:
    """
    Create new session with flexible entry points.

    Args:
        source_file: Optional path to existing source file (required for B/C/D)
        output_folder: Directory for project
        project_name: Optional project name
        entry_point: "materials" (A), "objectives" (B), "blueprint" (C), "questions" (D)
    """
```

### Validering i kod
```python
# I create_session metod:
if entry_point in ["objectives", "blueprint", "questions"] and not source_file:
    raise ValueError(
        f"Entry point '{entry_point}' requires source_file parameter"
    )

if entry_point == "materials" and source_file:
    logger.warning(
        "source_file provided for 'materials' entry point - will be ignored"
    )
```

---

## Problem 2: FOLDERS konstant saknas uppdatering

### Nuvarande
```python
FOLDERS = ["01_source", "02_working", "03_output"]
```

### Nytt behov
För shared session med materials entry point behöver vi:
- `00_materials/` - För uppladdade undervisningsmaterial
- `methodology/` - För metodologidokumentation

### Fix
```python
FOLDERS = [
    "00_materials",    # NEW: För entry point A (materials)
    "01_source",       # Befintlig källfil (entry point B/C)
    "02_working",      # Arbetsfiler under transformation
    "03_output",       # Exporterade QTI-filer
    "methodology"      # NEW: För metodologidokumentation
]
```

### Skapande i session_manager.py
```python
def create_session(...):
    # ...

    # Skapa alla folders
    for folder in FOLDERS:
        folder_path = session_path / folder
        folder_path.mkdir(exist_ok=True)

        # Lägg till README om det är materials folder
        if folder == "00_materials":
            readme_path = folder_path / "README.md"
            readme_path.write_text(
                "# Undervisningsmaterial\n\n"
                "Ladda upp allt material från din undervisning här:\n"
                "- Presentationer (PDF, PPTX)\n"
                "- Föreläsningsanteckningar\n"
                "- Transkriptioner från inspelningar\n"
                "- Läroböcker/artiklar som använts\n"
            )
```

---

## Problem 3: Entry point B/C/D logik - förtydligande

### Nuvarande oklarheter
Handoffen säger att B/C/D kräver `source_file`, men:
- Vad om användaren väljer "Objectives" (B) men inte har en fil ännu?
- Ska de kunna skapa en ny fil från scratch?
- Eller förväntar vi oss ALLTID en befintlig fil för B/C/D?

### Beslut: B/C/D KRÄVER befintlig fil

**Motivering:**
- Entry point B (Objectives) förutsätter learning objectives från materials-analys ELLER extern källa
- Entry point C (Blueprint) förutsätter att du har en färdig assessment plan
- Entry point D (Questions) förutsätter att du har färdiga frågor som behöver formateras
- Om du börjar från scratch → använd entry point A (Materials)

### Uppdaterad dokumentation

```markdown
## Entry Points

### A: Materials (Från undervisningsmaterial)
**När:** Du har undervisningsmaterial men inga frågor ännu
**Kräver:** Undervisningsmaterial (PDF, slides, transkriptioner)
**source_file:** Nej (skapas under processen)
**Nästa modul:** M1 (qf-scaffolding)
**Workflow:** Materials → Objectives → Blueprint → Questions → QTI

### B: Objectives (Från learning objectives)
**När:** Du har learning objectives (från BB1 eller extern källa)
**Kräver:** Fil med learning objectives
**source_file:** Ja (OBLIGATORISKT)
**Nästa modul:** M2 (qf-scaffolding)
**Workflow:** Objectives → Blueprint → Questions → QTI

### C: Blueprint (Från assessment plan)
**När:** Du har en färdig assessment plan/bedömningsplan
**Kräver:** Fil med assessment blueprint (frågetyper, viktning, scope)
**source_file:** Ja (OBLIGATORISKT)
**Nästa modul:** M3 (qf-scaffolding)
**Workflow:** Blueprint → Questions → QTI

### D: Questions (Från befintliga frågor)
**När:** Du har färdiga frågor som behöver formateras
**Kräver:** Markdown-fil med frågor (v6.3 eller liknande)
**source_file:** Ja (OBLIGATORISKT)
**Nästa modul:** Pipeline direkt (ingen scaffolding)
**Workflow:** Questions → Validate → Transform → QTI
```

### Kod för validering
```python
ENTRY_POINT_REQUIREMENTS = {
    "materials": {           # A
        "requires_source_file": False,
        "next_module": "m1",
        "description": "Börja från undervisningsmaterial",
        "next_steps": ["analyze_materials", "create_objectives"]
    },
    "objectives": {          # B
        "requires_source_file": True,
        "next_module": "m2",
        "description": "Börja från learning objectives",
        "next_steps": ["create_blueprint", "create_questions"]
    },
    "blueprint": {           # C
        "requires_source_file": True,
        "next_module": "m3",
        "description": "Börja från befintlig assessment plan",
        "next_steps": ["create_questions"]
    },
    "questions": {           # D
        "requires_source_file": True,
        "next_module": None,  # → Pipeline direkt
        "description": "Validera och exportera färdiga frågor",
        "next_steps": ["validate", "transform", "export"]
    }
}

def validate_entry_point(entry_point: str, source_file: Optional[str]) -> None:
    """Validate entry point and source_file combination."""
    if entry_point not in ENTRY_POINT_REQUIREMENTS:
        raise ValueError(f"Invalid entry point: {entry_point}")

    config = ENTRY_POINT_REQUIREMENTS[entry_point]

    if config["requires_source_file"] and not source_file:
        raise ValueError(
            f"Entry point '{entry_point}' requires source_file.\n"
            f"Description: {config['description']}\n"
            f"Expected workflow: {' → '.join(config['next_steps'])}"
        )

    if not config["requires_source_file"] and source_file:
        logger.warning(
            f"source_file provided for '{entry_point}' entry point - "
            f"will be ignored. This entry point creates files during workflow."
        )
```

---

## IMPLEMENTATION CHECKLIST

### session_manager.py

- [ ] **Line ~34:** Uppdatera `FOLDERS` konstant
  ```python
  FOLDERS = ["00_materials", "01_source", "02_working", "03_output", "methodology"]
  ```

- [ ] **Line ~86:** Uppdatera `create_session` signatur
  ```python
  def create_session(
      self,
      source_file: Optional[str] = None,  # FIX
      output_folder: str,
      project_name: Optional[str] = None,
      entry_point: str = "materials"
  ) -> Dict[str, Any]:
  ```

- [ ] **Line ~90:** Lägg till validering
  ```python
  # Validate entry point + source_file combination
  validate_entry_point(entry_point, source_file)
  ```

- [ ] **Line ~120:** Lägg till README för 00_materials
  ```python
  if folder == "00_materials":
      # Skapa README
  ```

### server.py

- [ ] **Line ~467:** Uppdatera `handle_step0_start` för att hantera Optional source_file

- [ ] **Lägg till:** `validate_entry_point` funktion (eller importera från utils)

### ADR-014-shared-session.md

- [ ] **Section 3:** Uppdatera "Technical Implementation" med FOLDERS
- [ ] **Section 4:** Lägg till validering av entry points
- [ ] **Section 5:** Förtydliga B/C requirements

---

## TESTING SCENARIOS (efter fix)

### Test 1: Entry Point A (Materials) utan source_file
```python
# SKA FUNGERA
session = manager.create_session(
    source_file=None,  # Inget behövs
    output_folder="~/test_materials",
    entry_point="materials"
)
# Förväntat: Lyckas, skapar 00_materials folder
```

### Test 2: Entry Point B (Objectives) utan source_file
```python
# SKA MISSLYCKAS
session = manager.create_session(
    source_file=None,  # Saknas!
    output_folder="~/test_objectives",
    entry_point="objectives"
)
# Förväntat: ValueError "Entry point 'objectives' requires source_file"
```

### Test 2b: Entry Point C (Blueprint) utan source_file
```python
# SKA MISSLYCKAS
session = manager.create_session(
    source_file=None,  # Saknas!
    output_folder="~/test_blueprint",
    entry_point="blueprint"
)
# Förväntat: ValueError "Entry point 'blueprint' requires source_file"
```

### Test 3: Entry Point C (Blueprint) med source_file
```python
# SKA FUNGERA
session = manager.create_session(
    source_file="~/assessment_blueprint.md",
    output_folder="~/test_blueprint",
    entry_point="blueprint"
)
# Förväntat: Lyckas, kopierar fil till 01_source, redo för M3
```

### Test 4: Entry Point D (Questions) med source_file
```python
# SKA FUNGERA
session = manager.create_session(
    source_file="~/questions_v6.3.md",
    output_folder="~/test_questions",
    entry_point="questions"
)
# Förväntat: Lyckas, kopierar fil till 01_source, går direkt till pipeline
```

### Test 5: FOLDERS skapande
```python
session = manager.create_session(...)
session_path = Path(session["session_path"])

# Kontrollera att alla folders finns
expected_folders = ["00_materials", "01_source", "02_working", "03_output", "methodology"]
for folder in expected_folders:
    assert (session_path / folder).exists()

# Kontrollera README i 00_materials
readme = session_path / "00_materials" / "README.md"
assert readme.exists()
```

### Test 6: Entry point routing till rätt modul
```python
# Test A → M1
session_a = manager.create_session(entry_point="materials", ...)
assert session_a["next_module"] == "m1"

# Test B → M2
session_b = manager.create_session(entry_point="objectives", source_file="...", ...)
assert session_b["next_module"] == "m2"

# Test C → M3
session_c = manager.create_session(entry_point="blueprint", source_file="...", ...)
assert session_c["next_module"] == "m3"

# Test D → Pipeline direkt
session_d = manager.create_session(entry_point="questions", source_file="...", ...)
assert session_d["next_module"] is None  # Ingen scaffolding
assert session_d["pipeline_ready"] == True
```

---

## SUMMARY

**Problem 1: source_file Optional** → FIXAT med `Optional[str] = None`
**Problem 2: FOLDERS konstant** → FIXAT med `["00_materials", ..., "methodology"]`
**Problem 3: B/C/D logik** → FIXAT med explicit validering och dokumentation för alla 4 entry points

**Entry Points (komplett):**
- **A: materials** - source_file VALFRI → M1 (qf-scaffolding)
- **B: objectives** - source_file OBLIGATORISKT → M2 (qf-scaffolding)
- **C: blueprint** - source_file OBLIGATORISKT → M3 (qf-scaffolding)
- **D: questions** - source_file OBLIGATORISKT → Pipeline direkt

**Estimerad fix-tid:** 25-35 minuter
**Risk:** Låg (små ändringar, tydlig logik)
**Testing:** 7 scenarios definierade (inklusive routing-test)

**Nästa steg efter fix:**
1. Implementera ändringar i `session_manager.py`
2. Uppdatera `server.py` entry point handling (alla 4 entry points: A/B/C/D)
3. Uppdatera ADR-014 med blueprint entry point
4. Kör alla 7 test scenarios (inklusive routing-test)
5. Commit med meddelande: "fix: add blueprint entry point and make source_file optional for materials"

---

**Handoff status:** KLAR FÖR IMPLEMENTATION ✅

**VIKTIGT:** Arbeta noggrant och steg för steg!

---

*Handoff skapad: 2026-01-14*
