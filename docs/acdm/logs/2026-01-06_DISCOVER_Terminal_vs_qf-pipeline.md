# ACDM DISCOVER: Terminal QTI Generator vs qf-pipeline

**Fas:** DISCOVER  
**Datum:** 2026-01-06  
**Kontext:** Djup jämförande analys inför `list_projects` implementation

---

## 1. EXECUTIVE SUMMARY

### Kärninsikt
Terminal QTI Generator har en **avgörande UX-fördel**: fördefinierad mappöversikt med status. qf-pipeline saknar detta och kräver att användaren anger sökvägar manuellt.

### Rekommendation
Implementera `list_projects` verktyg i qf-pipeline som ger samma funktionalitet som Terminal-menyn.

---

## 2. TERMINAL QTI GENERATOR - DJUPANALYS

### 2.1 Fil: `scripts/interactive_qti.py` (1200+ rader)

**Nyckelkomponenter:**

| Komponent | Syfte | Fil/Funktion |
|-----------|-------|--------------|
| Konfiguration | Fördefinierade MQG-mappar | `config/mqg_folders.json` |
| Historik | Senaste filer | `.qti_history.json` |
| Mappscanning | Hitta undermappar med .md-filer | `scan_subdirectories()` |
| Filscanning | Hitta markdown-filer | `scan_markdown_files()` |
| Menyval | Nummerbaserad navigation | `select_folder()`, `select_file()` |
| Question Set | Interaktiv sektion-skapare | `ask_create_question_set()` |
| Pipeline | 5-stegs workflow | `run_pipeline()` |

### 2.2 Konfigurationsfilen `mqg_folders.json`

```json
{
  "folders": [
    {
      "name": "Biologi BIOG001X (Autumn 2025)",
      "path": "~/Nextcloud/Courses/Biologi/Biog001x_2025/...",
      "default_language": "sv",
      "description": "Biologifrågor för BIOG001X hösten 2025"
    }
  ],
  "default_output_dir": "/Users/.../QTI_export_INSPERA",
  "remember_last_selection": true
}
```

**Nyckelobservationer:**
- Path kan använda `~` (expanderas av `expand_path()`)
- `default_language` per mapp
- Global `default_output_dir`
- `description` är valfritt

### 2.3 Status-indikering (✓/✗)

```python
def select_folder(config: dict, args) -> Optional[tuple]:
    for i, folder in enumerate(folders, 1):
        folder_exists = expand_path(folder['path']).exists()
        status = "[bold green]✓[/]" if folder_exists else "[bold red]✗[/]"
        console.print(f"  {i}. {folder['name']} {status}")
```

**Logik:**
- ✓ = Mappen finns
- ✗ = Mappen finns INTE

**BONUS i fil-visningen:**
```python
# Check if already processed (ZIP exists)
if output_dir:
    file_stem = Path(file['path']).stem
    zip_path = output_dir / f"{file_stem}.zip"
    if zip_path.exists():
        status = " [bold green]✓[/]"  # ZIP redan skapad
```

### 2.4 Question Set-funktionalitet

Terminal har avancerad Question Set-skapare:
- Filter på Bloom's Taxonomy (Remember, Understand, Apply, etc.)
- Filter på svårighetsgrad (Easy, Medium, Hard)
- Filter på poäng (1p, 2p, etc.)
- Filter på ämnestags
- "OR within category, AND between categories" logik
- Slumpning och antal-val per sektion

**qf-pipeline SAKNAR denna funktionalitet.**

---

## 3. qf-pipeline MCP - DJUPANALYS

### 3.1 Fil: `src/qf_pipeline/server.py` (400+ rader)

**Verktyg:**

| Verktyg | Syfte |
|---------|-------|
| `init` | Returnera kritiska instruktioner |
| `step0_start` | Starta/ladda session |
| `step0_status` | Visa sessionstatus |
| `step2_validate` | Validera markdown |
| `step2_validate_content` | Validera content-sträng |
| `step2_read` | Läs arbetsfil |
| `step4_export` | Exportera till QTI |
| `list_types` | Lista frågetyper |

### 3.2 Session-modellen

```
qf_pipeline skapar:
  {project_path}/
  ├── 01_source/
  │   └── {filename}.md  (kopia av källfil)
  ├── 02_work/           (arbetsarea)
  ├── 03_output/         (QTI-paket)
  └── .qf_session.json   (session-metadata)
```

### 3.3 Workflow-jämförelse

| Steg | Terminal | qf-pipeline |
|------|----------|-------------|
| 1 | Visa mappöversikt | `init` (instruktioner) |
| 2 | Välj nummer | Dialog: "Vilken fil?" |
| 3 | Visa filer i mappen | Dialog: "Vilken output?" |
| 4 | Välj nummer | `step0_start` |
| 5 | Konfigurera | (ingen config) |
| 6 | Kör pipeline | `step2_validate` |
| 7 | Question Set? | (saknas) |
| 8 | Skapa ZIP | `step4_export` |

---

## 4. GAP-ANALYS

### 4.1 Vad qf-pipeline SAKNAR

| Feature | Terminal | qf-pipeline | Prioritet |
|---------|----------|-------------|-----------|
| Mappöversikt | ✅ | ❌ | **HÖG** |
| Status-indikatorer | ✅ | ❌ | **HÖG** |
| Nummerval | ✅ | ❌ | MEDIUM |
| Question Set | ✅ | ❌ | LÅG (separat tool?) |
| Historik | ✅ | ❌ | LÅG |
| Quick mode | ✅ | ❌ | LÅG |
| Sök i filer | ✅ | ❌ | LÅG |

### 4.2 Vad qf-pipeline HAR som Terminal saknar

| Feature | Terminal | qf-pipeline |
|---------|----------|-------------|
| AI-assisterad felsökning | ❌ | ✅ |
| Session-hantering | ❌ | ✅ |
| Obligatorisk validering | ❌ | ✅ |
| Naturlig dialog | ❌ | ✅ |

---

## 5. SPECIFIKATION: `list_projects` verktyg

### 5.1 Syfte
Ge samma mappöversikt som Terminal, men inom MCP-ramverket.

### 5.2 Föreslaget API

```python
Tool(
    name="list_projects",
    description="List configured MQG folders with status. Returns folder list for quick selection.",
    inputSchema={
        "type": "object",
        "properties": {
            "include_files": {
                "type": "boolean",
                "description": "Also scan and list markdown files in each folder",
                "default": False
            },
            "config_path": {
                "type": "string",
                "description": "Path to mqg_folders.json (optional, uses default if not provided)"
            }
        }
    }
)
```

### 5.3 Förväntat output

```
MQG Projekt (5 st):

  1. ✅ Biologi BIOG001X (Autumn 2025)
     Path: ~/Nextcloud/Courses/Biologi/...
     Språk: sv
     
  2. ❌ TRA265 LP2 2025
     Path: ~/Nextcloud/Chalmers/TRA265/...
     Status: Mappen finns inte
     
  3. ✅ Mate2b001x Autmn 2025
     Path: /Users/niklaskarlsson/Nextcloud/...
     Språk: sv

Tips: Använd step0_start med source_file från önskad mapp.
```

### 5.4 Implementation - Nyckellogik

```python
from pathlib import Path
import json

def list_projects(config_path: str = None) -> dict:
    """List configured MQG folders with status."""
    
    # Default config location
    if not config_path:
        config_path = Path(__file__).parent.parent.parent.parent.parent / \
                      "QTI-Generator-for-Inspera" / "config" / "mqg_folders.json"
    
    # Load config
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    projects = []
    for folder in config.get('folders', []):
        path = Path(folder['path']).expanduser()
        exists = path.exists()
        
        # Count markdown files if folder exists
        md_count = 0
        if exists:
            md_count = len(list(path.rglob("*.md")))
        
        projects.append({
            "name": folder['name'],
            "path": str(path),
            "exists": exists,
            "language": folder.get('default_language', 'sv'),
            "description": folder.get('description', ''),
            "md_file_count": md_count
        })
    
    return {
        "projects": projects,
        "default_output_dir": config.get('default_output_dir'),
        "count": len(projects)
    }
```

### 5.5 Konfigurationsdelning

**Kritisk fråga:** Var ska `mqg_folders.json` bo?

**Alternativ:**

| Alternativ | Fördelar | Nackdelar |
|------------|----------|-----------|
| A) Läs från QTI-Generator | Delad källa, ingen duplicering | Hårdkodad sökväg |
| B) Kopiera till qf-pipeline | Oberoende | Kan bli osynkad |
| C) Symbolisk länk | Delad, flexibel | Kan vara förvirrande |
| D) Miljövariabel | Konfigurerbar | Kräver setup |

**Rekommendation:** Alternativ A med fallback

```python
# Primär: QTI-Generator config
QTI_GEN_CONFIG = Path.home() / "QTI-Generator-for-Inspera" / "config" / "mqg_folders.json"

# Fallback: qf-pipeline egen config
QF_CONFIG = Path(__file__).parent / "config" / "mqg_folders.json"

config_path = QTI_GEN_CONFIG if QTI_GEN_CONFIG.exists() else QF_CONFIG
```

---

## 6. NÄSTA STEG (ACDM)

### 6.1 SHAPE-fas
- [ ] Besluta om config-delning (Alternativ A, B, C eller D)
- [ ] Definiera exakt output-format för `list_projects`
- [ ] Besluta om `list_files` ska vara separat verktyg

### 6.2 DECIDE-fas
- [ ] ADR: Config-delning mellan QTI-Generator och qf-pipeline
- [ ] ADR: list_projects vs list_files separation

### 6.3 COORDINATE-fas
- [ ] Implementera `list_projects` i server.py
- [ ] Lägga till i `list_tools()`
- [ ] Testa med Claude

---

## 7. FILREFERENSER

| Fil | Plats | Syfte |
|-----|-------|-------|
| `interactive_qti.py` | `QTI-Generator-for-Inspera/scripts/` | Terminal-gränssnitt |
| `mqg_folders.json` | `QTI-Generator-for-Inspera/config/` | Mappkonfiguration |
| `server.py` | `QuestionForge/packages/qf-pipeline/src/qf_pipeline/` | MCP-server |
| `.qti_history.json` | `QTI-Generator-for-Inspera/` | Filhistorik |

---

*ACDM DISCOVER fas slutförd: 2026-01-06*
