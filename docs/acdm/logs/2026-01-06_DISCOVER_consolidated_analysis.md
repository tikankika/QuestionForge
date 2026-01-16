# ACDM DISCOVER: Konsoliderad Analys

**Fas:** DISCOVER (slutlig)  
**Datum:** 2026-01-06  
**Källor:** Claude.ai analys + Claude Code djupanalys

---

## EXECUTIVE SUMMARY

Två parallella analyser har genomförts:

| Analys | Fokus | Kritiska fynd |
|--------|-------|---------------|
| Claude.ai | Arkitektur, UX, mappval | ADR-008: Config i utils/ |
| Claude Code | Funktionalitet, workflow | 🔴 Resources saknas i export |

---

## KRITISKT PROBLEM: Resources saknas

### Vad QTI-Generator gör (Step 3)

```python
# scripts/step3_copy_resources.py
1. Skannar markdown för bildref: ![alt](path)
2. Kopierar bilder till output-mapp
3. Byter namn enligt Inspera-krav (ID_question-prefix)
4. Validerar filstorlek (max 5 MB)
5. Uppdaterar XML med nya sökvägar
```

### Vad qf-pipeline gör

```python
# server.py:handle_step4_export()
1. parse_file() - Parsar markdown
2. generate_all_xml() - Genererar XML
3. create_qti_package() - Skapar ZIP
# 🔴 SAKNAS: copy_resources() anropas ALDRIG!
```

### Konsekvens

**Frågor med bilder fungerar INTE i Inspera** när man använder qf-pipeline.

### Kod som finns men inte används

```python
# wrappers/resources.py - FINNS men OANVÄNT:
validate_resources()       # ← Bör användas före export
copy_resources()           # ← KRITISKT - måste integreras
prepare_output_structure()
get_supported_formats()    # .png, .jpg, etc.
get_max_file_size_mb()     # 5 MB (Inspera limit)
```

---

## KOMPLETT GAP-ANALYS

| Funktion | QTI-Generator | qf-pipeline | Prioritet |
|----------|---------------|-------------|-----------|
| Resource copying | ✅ Step 3 | ❌ SAKNAS | 🔴 KRITISK |
| Question Set builder | ✅ Interaktiv | ❌ Saknas | 🟠 Hög |
| Tag filtering (Bloom, difficulty) | ✅ | ❌ | 🟠 Hög |
| Folder discovery | ✅ Config-baserad | ❌ Kräver full sökväg | 🟡 Medium |
| File browser/search | ✅ | ❌ | 🟡 Medium |
| Strict mode | ✅ | ❌ | 🟡 Medium |
| Step selection (1-5) | ✅ | ❌ | 🟡 Medium |
| History tracking | ✅ .qti_history.json | ❌ | 🟢 Låg |

---

## WORKFLOW-JÄMFÖRELSE

### QTI-Generator (5 steg, fullständig)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Välj MQG folder (från mqg_folders.json config)           │
│ 2. Välj subdirectory (med fil-count)                        │
│ 3. Välj markdown-fil (sök, mod-datum, ZIP-status ✓)         │
│ 4. Konfigurera (namn, språk, strict, keep folder)           │
│ 5. Välj steg: 1,2,3,4,5 individuellt eller alla             │
│    Step 1: Validate markdown                                │
│    Step 2: Create output folder                             │
│    Step 3: Copy resources ← KRITISKT!                       │
│    Step 4: Generate XML + optional Question Set             │
│    Step 5: Create ZIP                                       │
│ 6. Spara till history                                       │
└─────────────────────────────────────────────────────────────┘
```

### qf-pipeline MCP (3 steg, ofullständig)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. init → Läs instruktioner                                 │
│ 2. step0_start(source_file, output_folder)                  │
│    → Kräver full sökväg (ingen discovery)                   │
│ 3. step2_validate → Validera                                │
│ 4. step4_export → Exportera                                 │
│    → 🔴 HOPPAR ÖVER resources!                              │
└─────────────────────────────────────────────────────────────┘
```

---

## REVIDERAD PRIORITERING

### Prioritet 1: 🔴 Fixa resources (KRITISK)

**ADR behövs:** ADR-009-resource-handling.md

**Ändringar i step4_export:**
```python
# I server.py:handle_step4_export(), FÖRE XML-generering:
from .wrappers import copy_resources, validate_resources

# 1. Validera resources
resource_result = validate_resources(file_path, questions)
if not resource_result["valid"]:
    return [TextContent(type="text", text=f"Resource error: {resource_result}")]

# 2. Kopiera resources
copy_result = copy_resources(file_path, output_dir, questions)

# 3. Generera XML (med uppdaterade sökvägar)
```

### Prioritet 2: 🟠 Question Set builder

**Nytt tool:** `step4_questionset`

### Prioritet 3: 🟡 Folder discovery

**Nytt tool:** `list_projects` (ADR-008 redan skapad)

---

## DOKUMENTREFERENSER

| Dokument | Plats | Status |
|----------|-------|--------|
| Terminal vs qf-pipeline | `acdm/logs/2026-01-06_DISCOVER_Terminal_vs_qf-pipeline.md` | ✅ |
| Wrapper-analys | `acdm/logs/2026-01-06_DISCOVER_qf-pipeline_wrapper_analysis.md` | ✅ |
| ADR-008: Config location | `adr/ADR-008-project-configuration-location.md` | ✅ |
| Handoff: list_projects | `IMPLEMENT_handoff_list_projects.md` | ✅ |
| **ADR-009: Resources** | `adr/ADR-009-resource-handling.md` | ❌ BEHÖVS |

---

## NÄSTA STEG

1. **Skapa ADR-009** för resource-hantering (KRITISK)
2. **Uppdatera handoff** med resources-fix som prioritet 1
3. **list_projects** blir prioritet 2 (inte 1 som tidigare)

---

*Konsoliderad analys: 2026-01-06*
*Kritiskt fynd av Claude Code: resources.py används inte*
