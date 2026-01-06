# ACDM DISCOVER: qf-pipeline Standalone Migration

**Datum:** 2026-01-06  
**Status:** DISCOVER (slutförd)  
**Syfte:** Göra qf-pipeline till ett helt självständigt verktyg utan externa beroenden

---

## 1. NUVARANDE ARKITEKTUR

### Beroendekedja

```
qf-pipeline/
└── wrappers/
    ├── __init__.py          ← sys.path.insert(QTI-Generator-for-Inspera)
    ├── parser.py            → from src.parser.markdown_parser import MarkdownQuizParser
    ├── generator.py         → from src.generator.xml_generator import XMLGenerator
    ├── packager.py          → from src.packager.qti_packager import QTIPackager
    ├── validator.py         → from validate_mqg_format import validate_content
    └── resources.py         → (intern)

QTI-Generator-for-Inspera/     ← EXTERNT BEROENDE
├── src/
│   ├── parser/markdown_parser.py
│   ├── generator/
│   │   ├── xml_generator.py
│   │   ├── resource_manager.py
│   │   └── assessment_test_generator.py
│   └── packager/qti_packager.py
├── validate_mqg_format.py
└── templates/xml/*.xml        ← 21 XML-mallar
```

### Problem med nuvarande lösning

1. **Hårdkodad sökväg:** `/Users/niklaskarlsson/QTI-Generator-for-Inspera`
2. **Fungerar inte på andra datorer**
3. **Kan inte distribueras som pip-paket**
4. **Uppdateringar i QTI-Generator kan bryta qf-pipeline**

---

## 2. KARTLAGDA BEROENDEN

### Python-filer som behöver kopieras

| Fil | Importeras av | Storlek | Beroenden |
|-----|---------------|---------|-----------|
| `src/parser/markdown_parser.py` | parser.py | ~800 rader | yaml, re, logging |
| `src/generator/xml_generator.py` | generator.py | ~600 rader | templates/, markdown_parser |
| `src/generator/resource_manager.py` | xml_generator | ~200 rader | pathlib, shutil |
| `src/packager/qti_packager.py` | packager.py | ~400 rader | zipfile, xml.etree |
| `validate_mqg_format.py` | validator.py | ~600 rader | re, dataclasses |

**Total:** ~2600 rader Python-kod

### XML-mallar (templates/xml/)

```
templates/xml/
├── assessment_test.xml
├── audio_record.xml
├── composite_editor.xml
├── essay.xml
├── gapmatch.xml
├── graphicgapmatch_v2.xml
├── hotspot.xml
├── imsmanifest_template.xml    ← Kritisk för paketgenerering
├── inline_choice.xml
├── match.xml
├── math_working.xml
├── multiple_choice_single.xml
├── multiple_response.xml
├── nativehtml.xml
├── text_area.xml
├── text_entry.xml
├── text_entry_graphic.xml
├── text_entry_math.xml
├── text_entry_numeric.xml
└── true_false.xml
```

**Total:** 21 XML-mallar

---

## 3. IDENTIFIERADE UTMANINGAR

### 3.1 Template-sökvägar

**Problem:** `xml_generator.py` letar efter templates relativt till projektrot:

```python
project_root = Path(__file__).parent.parent.parent
templates_dir = project_root / 'templates' / 'xml'
```

**Lösning:** Bundla templates som package data och använd `importlib.resources` eller relativa sökvägar från `__file__`.

### 3.2 Intern import-struktur

**Problem:** QTI-Generator använder absoluta imports:

```python
from src.parser.markdown_parser import MarkdownQuizParser
from ..parser.markdown_parser import markdown_to_xhtml
```

**Lösning:** Refaktorera till relativa imports inom qf-pipeline.

### 3.3 validate_mqg_format.py

**Problem:** Fristående script i rotkatalogen, inte del av src/.

**Lösning:** Flytta in i qf-pipeline core/-strukturen.

---

## 4. UTVÄRDERADE ALTERNATIV

### Alternativ A: Full kopia med refaktorering ✅ VALT

```
qf-pipeline/
└── src/qf_pipeline/
    ├── core/                    ← NY MAPP (all QTI-logik)
    │   ├── __init__.py
    │   ├── parser.py            ← Från markdown_parser.py
    │   ├── generator.py         ← Från xml_generator.py
    │   ├── packager.py          ← Från qti_packager.py
    │   ├── validator.py         ← Från validate_mqg_format.py
    │   └── resource_manager.py
    ├── templates/               ← NY MAPP
    │   └── xml/
    │       └── *.xml            ← Alla 21 mallar
    ├── wrappers/                ← BEHÅLL (tunna wrappers)
    │   └── *.py                 → Importerar från core/
    └── pyproject.toml           ← Uppdatera package_data
```

**Fördelar:**
- Helt självständigt
- Kan distribueras som pip-paket
- Ingen extern path-manipulation
- **ETT repo att underhålla**

**Nackdelar:**
- ~2600 rader kod att underhålla (men detta är oundvikligt)

### Alternativ B: Git submodule ❌ AVVISAT

**Avvisat eftersom:** Fortfarande beroende av extern kod, mer komplex git-hantering.

### Alternativ C: Selektiv vendoring ❌ AVVISAT

**Avvisat eftersom:** Kräver fortfarande underhåll av `/Users/niklaskarlsson/QTI-Generator-for-Inspera` som separat projekt. Resulterar i dubbelt arbete vid varje uppdatering - måste först uppdatera QTI-Generator, sedan synka till qf-pipeline. Ingen verklig fördel jämfört med Alternativ A.

---

## 5. BESLUT: Alternativ A

### Motivering

**Kärninsikt:** Med Alternativ C måste man fortfarande underhålla QTI-Generator-for-Inspera separat. Vid varje uppdatering:
1. Uppdatera QTI-Generator-for-Inspera
2. Synka manuellt till qf-pipeline
3. Testa båda

**Med Alternativ A:**
1. All utveckling sker i QuestionForge/qf-pipeline
2. ETT repo att underhålla
3. QTI-Generator-for-Inspera arkiveras (read-only, historik bevaras)

### Konsekvenser

| Före | Efter |
|------|-------|
| QTI-Generator-for-Inspera = aktivt repo | QTI-Generator-for-Inspera = arkiverat |
| qf-pipeline = beroende wrapper | qf-pipeline = självständigt paket |
| Två repos att underhålla | Ett repo (QuestionForge) |

---

## 6. NY ARKITEKTUR (efter migration)

```
QuestionForge/
└── packages/
    └── qf-pipeline/
        └── src/qf_pipeline/
            ├── core/                        ← QTI-logik (migrerad)
            │   ├── __init__.py
            │   ├── parser.py                ← MarkdownQuizParser
            │   ├── generator.py             ← XMLGenerator
            │   ├── packager.py              ← QTIPackager
            │   ├── validator.py             ← validate_mqg_format
            │   └── resource_manager.py      ← ResourceManager
            │
            ├── templates/                   ← XML-mallar (kopierade)
            │   └── xml/
            │       ├── multiple_choice_single.xml
            │       ├── text_entry.xml
            │       └── ... (21 mallar totalt)
            │
            ├── wrappers/                    ← Tunna wrappers (befintliga)
            │   ├── __init__.py              ← Uppdatera imports
            │   ├── parser.py                → from ..core.parser import ...
            │   ├── generator.py             → from ..core.generator import ...
            │   ├── packager.py              → from ..core.packager import ...
            │   └── validator.py             → from ..core.validator import ...
            │
            ├── tools/                       ← MCP-verktyg (befintliga)
            ├── utils/                       ← Session management (befintliga)
            │
            └── pyproject.toml               ← Uppdatera package_data för templates
```

### Import-flöde efter migration

```
MCP Tool (server.py)
    ↓
wrappers/parser.py
    ↓ from ..core.parser import MarkdownQuizParser
core/parser.py
    ↓ (ingen extern import)
```

---

## 7. MIGRERINGSPLAN (SHAPE-input)

### Steg 1: Förberedelse
- [ ] Skapa `core/` mapp
- [ ] Skapa `templates/xml/` mapp

### Steg 2: Kopiera filer
- [ ] `markdown_parser.py` → `core/parser.py`
- [ ] `xml_generator.py` → `core/generator.py`
- [ ] `qti_packager.py` → `core/packager.py`
- [ ] `validate_mqg_format.py` → `core/validator.py`
- [ ] `resource_manager.py` → `core/resource_manager.py`
- [ ] `templates/xml/*.xml` → `templates/xml/`

### Steg 3: Refaktorera imports
- [ ] Uppdatera alla `from src.X import Y` till relativa imports
- [ ] Uppdatera template-sökvägar att använda `Path(__file__)`
- [ ] Uppdatera `wrappers/` att importera från `core/`

### Steg 4: Uppdatera pyproject.toml
- [ ] Lägg till `templates/xml/*.xml` i package_data
- [ ] Verifiera att mallar inkluderas i build

### Steg 5: Testa
- [ ] Kör alla befintliga tester
- [ ] Testa varje frågetyp (16 st)
- [ ] Testa full pipeline: parse → validate → generate → package

### Steg 6: Arkivera QTI-Generator
- [ ] Uppdatera README med "Arkiverad - se QuestionForge"
- [ ] Sätt repo till read-only (om möjligt)

---

## 8. RISKANALYS

| Risk | Sannolikhet | Påverkan | Mitigation |
|------|-------------|----------|------------|
| Missar viktiga filer | Medium | Hög | Testa alla 16 frågetyper |
| Import-fel efter refaktorering | Hög | Medium | Enhetstester per modul |
| Template-sökväg fungerar inte | Medium | Hög | Använd `Path(__file__).parent` |
| Glömmer någon template | Låg | Hög | Räkna: 21 mallar |

---

## 9. TIDSUPPSKATTNING

| Uppgift | Tid |
|---------|-----|
| Kopiera + refaktorera Python-filer | 2-3 timmar |
| Kopiera templates + uppdatera sökvägar | 1 timme |
| Uppdatera wrappers | 30 min |
| Testa alla frågetyper | 1-2 timmar |
| Dokumentera + arkivera | 30 min |
| **Total** | **5-7 timmar** |

---

*DISCOVER-fas slutförd 2026-01-06*  
*Beslut: Alternativ A (Full kopia med refaktorering)*  
*Nästa: SHAPE - Detaljerad handoff för implementation*
