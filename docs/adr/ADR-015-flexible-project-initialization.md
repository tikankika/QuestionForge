# ADR-015: Flexible Project Initialization

**Status:** Implemented ✅
**Date:** 2026-01-30
**Deciders:** Niklas Karlsson, Claude
**Related:** RFC-017 (Existing Questions Entry Point)

---

## Context

Current `step0_start` requires both `entry_point` and source files at project creation:

```python
# Current - måste veta allt vid start
step0_start(
    entry_point="m3",           # Måste välja
    source_file="blueprint.md", # Måste ha fil
    output_folder="..."
)
```

**Problem:**
- Lärare måste veta "entry point" terminologi
- Fil måste finnas och vara åtkomlig vid projektstart
- Kan inte skapa projekt först, lägga till material senare
- Ingen flexibilitet för iterativt arbete

---

## Decision

**Separera projektskapande från filhantering och entry point-val.**

Nytt flöde:

```
1. step0_start()      → Skapa tomt projekt
2. step0_add_file()   → Lägg till fil(er), kan anropas flera gånger
3. step0_analyze()    → Systemet föreslår lämpligt flöde
```

---

## New Tools

### step0_start (updated)

```python
step0_start(
    output_folder: str,
    project_name: str = None,      # Auto-genereras om ej angivet
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
  - questions/source.md (20 frågor detekterade)
  - questions/resources/ (5 bilder)

recommended_flow: "M5 → Pipeline"
alternatives:
  - "M4 → M5 → Pipeline (granska först)"
  - "M2 → M5 → Pipeline (lägg till taxonomi)"

next_step: "Kör m5_start() för att börja formatkonvertering"
```

---

## Consequences

### Positive
- Lärare behöver inte förstå "entry points"
- Projekt kan skapas innan material finns
- Iterativt arbete möjligt (lägg till fler filer efteråt)
- Systemet guidar baserat på vad som faktiskt finns

### Negative
- Fler verktygsanrop (3 istället för 1)
- Befintligt flöde måste uppdateras

### Neutral
- Bakåtkompatibilitet: `step0_start(entry_point=..., source_file=...)` fungerar fortfarande

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
FRÅGA LÄRAREN: Vilka filer ska läggas till?
═══════════════════════════════════════════════════════

📝 PROV/FRÅGOR att konvertera?
   (Word, Excel, PDF med befintliga frågor)

📚 UNDERVISNINGSMATERIAL?
   (Föreläsningar, slides, transkriberingar)

🖼️  RESURSER (bilder, ljud, video)?
   (Figurer, diagram, ljudklipp till frågorna)
```

After each `step0_add_file()`, the system asks:

```
FLER FILER ATT LÄGGA TILL?

📚 Undervisningsmaterial? (slides, föreläsningar)
🖼️  Resurser? (bilder, ljud, video till frågorna)
📝 Fler prov/frågor?

Om JA: Använd step0_add_file igen
Om NEJ: Kör step0_analyze för att fortsätta
```

---

*ADR-015 created 2026-01-30, implemented 2026-01-30*
