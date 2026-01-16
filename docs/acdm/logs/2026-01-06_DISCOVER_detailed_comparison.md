# ACDM DISCOVER: Terminal vs qf-pipeline - Detaljerad Jämförelse

**Fas:** DISCOVER (fördjupad)  
**Datum:** 2026-01-06  
**Status:** Uppdaterad efter kodgranskning

---

## IMPLEMENTATIONSSTATUS

### Redan implementerat (nyligen tillagt?)

| Feature | Terminal | qf-pipeline | Status |
|---------|----------|-------------|--------|
| Resource handling | Step 3 | `step4_export` | ✅ IMPLEMENTERAT |
| list_projects | Config-meny | `list_projects` tool | ✅ IMPLEMENTERAT |

### Kvarstående GAP

| Feature | Terminal | qf-pipeline | Prioritet |
|---------|----------|-------------|-----------|
| Subdirectory navigation | ✅ | ❌ | 🟡 Medium |
| File browser with dates | ✅ | ❌ | 🟡 Medium |
| ZIP status indicator | ✅ | ❌ | 🟢 Låg |
| Search function | ✅ | ❌ | 🟢 Låg |
| Strict mode | ✅ | ❌ | 🟡 Medium |
| Keep folder option | ✅ | ❌ | 🟢 Låg |
| Individual step selection | ✅ | ❌ | 🟢 Låg |
| Question Set builder | ✅ | ❌ | 🟠 Hög |
| Tag filtering (Bloom, difficulty) | ✅ | ❌ | 🟠 Hög |

---

## WORKFLOW-JÄMFÖRELSE (UPPDATERAD)

### Terminal QTI-Generator (Fullständig)

```
┌──────────────────────────────────────────────────────────────────┐
│ STEG 1: MAPPVAL                                                  │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ 1. Biologi BIOG001X (Autumn 2025) ✓                        │  │
│ │ 2. TRA265 LP2 2025 ✗                                       │  │
│ │ 3. Mate2b001x Autmn 2025 ✓                                 │  │
│ │ 98. Ange egen sökväg                                       │  │
│ └────────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│ STEG 2: FILVAL                                                   │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ 1. BIOG001X_Fys.md (2025-12-14 22:10)                      │  │
│ │ 9. BIOG001X_Fys_v65_5.md (2025-12-16 23:48) ✓              │  │
│ │ s. Sök efter fil                                           │  │
│ └────────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│ STEG 3: KONFIGURATION                                            │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ Output-namn: [BIOG001X_Fys_v65_5]                          │  │
│ │ Språk: [sv]                                                │  │
│ │ Strict mode: [n]                                           │  │
│ │ Behåll folder: [j]                                         │  │
│ └────────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│ STEG 4: PIPELINE (5 steg)                                        │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ ▶ Steg 1/5: Validerar markdown format...                   │  │
│ │ ▶ Steg 2/5: Skapar output-mapp...                          │  │
│ │ ▶ Steg 3/5: Kopierar resurser...                           │  │
│ │ ▶ Steg 4/5: Genererar QTI XML... [Question Set builder?]   │  │
│ │ ▶ Steg 5/5: Skapar ZIP-paket...                            │  │
│ └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### qf-pipeline MCP (Nuvarande)

```
┌──────────────────────────────────────────────────────────────────┐
│ STEG 1: INIT                                                     │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ init → Läs instruktioner                                   │  │
│ └────────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│ STEG 2: PROJEKTÖVERSIKT (NY!)                                    │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ list_projects → Visar konfigurerade mappar                 │  │
│ │   1. [+] Biologi BIOG001X                                  │  │
│ │   2. [-] TRA265 LP2 2025                                   │  │
│ └────────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│ STEG 3: SESSION                                                  │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ step0_start(source_file, output_folder)                    │  │
│ │ ❌ SAKNAS: Filbläddring inom projekt                       │  │
│ │ ❌ SAKNAS: Datumvisning, ZIP-status                        │  │
│ └────────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│ STEG 4: VALIDERING                                               │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ step2_validate → Validerar                                 │  │
│ │ ❌ SAKNAS: Strict mode                                     │  │
│ └────────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│ STEG 5: EXPORT                                                   │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ step4_export → Exporterar med resurser                     │  │
│ │ ✅ Resources kopieras (nyligen implementerat)              │  │
│ │ ❌ SAKNAS: Keep folder option                              │  │
│ │ ❌ SAKNAS: Question Set builder                            │  │
│ └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## DETALJANALYS: KVARSTÅENDE GAP

### 1. 🟠 Question Set Builder (HÖG PRIORITET)

**Terminal har:**
```
Question Set Builder
├── Filter på:
│   ├── Bloom's Taxonomy (Remember, Understand, Apply...)
│   ├── Difficulty (Easy, Medium, Hard)
│   ├── Custom tags
│   └── Points
├── "OR inom kategori, AND mellan kategorier"
├── Preview av matchande frågor
├── Välj antal (random sampling)
├── Toggle shuffle per sektion
├── Markera använda frågor (no duplicates)
└── Genererar assessmentTest XML
```

**qf-pipeline har:**
- ❌ Inget Question Set-stöd

**Varför viktigt:**
- Inspera använder "Question Sets" för dynamiska prov
- Utan detta kan man bara skapa statiska frågebanker
- ^labels-validering finns men används inte för filtrering

**Rekommendation:** ADR-010 för Question Set builder

---

### 2. 🟡 Filbläddring inom projekt (MEDIUM)

**Terminal har:**
```python
# interactive_qti.py
def scan_markdown_files(folder_path):
    # Listar alla .md-filer
    # Visar modification date
    # Visar ZIP-status (✓ om redan exporterad)
    # Sorterar efter namn/datum
```

**qf-pipeline har:**
- `list_projects` visar mappar, men INTE filer inom mapparna
- Användaren måste ange full sökväg manuellt

**Rekommendation:** Utöka `list_projects` eller skapa `list_files(project_path)`

---

### 3. 🟡 Strict Mode (MEDIUM)

**Terminal har:**
```python
strict_mode = input("Strict mode (behandla varningar som fel)? (j/n) [n]: ")
```

**qf-pipeline har:**
- Validatorn stödjer strict mode internt
- Men det exponeras INTE som parameter i `step2_validate`

**Fix (enkel):**
```python
# I step2_validate inputSchema:
"strict": {
    "type": "boolean",
    "description": "Behandla varningar som fel",
    "default": False
}
```

---

### 4. 🟢 Keep Folder Option (LÅG)

**Terminal har:**
```python
keep_folder = input("Behåll extracted folder efter zipping? (j/n) [j]: ")
```

**qf-pipeline:**
- `create_qti_package` har `keep_folder` parameter
- Men det exponeras INTE i `step4_export`

**Fix (enkel):**
```python
# I step4_export inputSchema:
"keep_folder": {
    "type": "boolean",
    "description": "Behåll extraherad mapp efter ZIP-skapande",
    "default": True
}
```

---

## VALIDATION OUTPUT-JÄMFÖRELSE

### Terminal Output (Rich formatting)
```
================================================================================
MQG FORMAT VALIDATION REPORT (v6.5)
================================================================================

❌ ERRORS FOUND:

Question 1 (BIOG_FYS_Q001):
  Missing ^labels field

Question 13 (BIOG_FYS_Q013):
  Match pairs must use inline format: "1. X → Y" (table format not supported)

================================================================================
SUMMARY
================================================================================
Total Questions: 27
✅ Valid: -2
❌ Errors: 29
⚠️  Warnings: 0

STATUS: ❌ NOT READY - Fix 29 error(s) before QTI generation
→ Go back to Claude Desktop and fix the errors listed above
```

### qf-pipeline Output (Plain text)
```
Invalid: /path/to/file.md
  Fragor: 27
  [ERROR] Missing ^labels field (rad ?)
  [ERROR] Match pairs must use inline format (rad ?)
```

**Skillnader:**
- Terminal: Grupperat per fråga, fråge-ID visas
- qf-pipeline: Flat lista, mindre kontextuell info
- Terminal: Tydlig SUMMARY + nästa steg
- qf-pipeline: Enklare output

**Rekommendation:** Förbättra output-formatering i qf-pipeline

---

## SAMMANFATTNING: NÄSTA STEG

### Redan klart
- [x] Resource handling i step4_export
- [x] list_projects tool

### Enkla förbättringar (kan göras snabbt)
1. **Strict mode** - Lägg till parameter i step2_validate
2. **Keep folder** - Lägg till parameter i step4_export
3. **Förbättrad output** - Gruppera valideringsfel per fråga

### Större features (kräver design)
1. **list_files** - Filbläddring inom projekt
2. **Question Set builder** - Filtrera och skapa dynamiska prov

### ADR-behov
- ADR-010: Question Set Builder design
- ADR-011: list_files tool design (eller utöka list_projects)

---

## PRIORITERAD BACKLOG

| Prio | Feature | Komplexitet | Dokument |
|------|---------|-------------|----------|
| 1 | Strict mode parameter | Enkel | - |
| 2 | Keep folder parameter | Enkel | - |
| 3 | Förbättrad validation output | Medium | - |
| 4 | list_files tool | Medium | ADR-011? |
| 5 | Question Set builder | Komplex | ADR-010 |

---

*ACDM DISCOVER fördjupad analys: 2026-01-06*
*Uppdaterad efter kodgranskning*
