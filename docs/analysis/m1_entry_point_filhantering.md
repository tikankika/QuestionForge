# Entry Point M1 - Filhantering Analys

**Datum:** 2026-01-14  
**Kontext:** Niklas fråga om vad som händer med filer i första steget

---

## KRITISK INSIKT: Entry Point M1 KOPIERAR INGA FILER!

### Vad session_manager.py FAKTISKT gör

**Kod från session_manager.py (rad 24-30):**
```python
"m1": {
    "requires_source_file": False,  # ← INGEN fil krävs!
    "next_module": "m1",
    "description": "Börja från undervisningsmaterial → Content Analysis",
    "next_steps": ["M1", "M2", "M3", "M4", "Pipeline"],
    "skips": []
}
```

**Kod från session_manager.py (rad 88-92):**
```python
if not config["requires_source_file"] and source_file:
    logger.warning(
        f"source_file provided for '{entry_point}' entry point - "
        f"will be ignored. This entry point creates files during workflow."
    )
```

---

## VAD HÄNDER VID step0_start(entry_point="m1")

### Scenario 1: Utan source_file (NORMALT för M1)
```python
step0_start(
    output_folder="/path/to/output",
    entry_point="m1"
    # source_file saknas → OK!
)
```

**Resultat:**
1. Skapar projektmappar:
   ```
   QF_test_2/
   ├── 00_materials/        ← Tom + README.md
   ├── 01_source/           ← Tom
   ├── 02_working/          ← Tom
   ├── 03_output/           ← Tom
   ├── methodology/         ← Tom
   └── session.yaml
   ```

2. `00_materials/README.md` innehåller:
   ```markdown
   # Undervisningsmaterial
   
   Ladda upp allt material från din undervisning här:
   - Presentationer (PDF, PPTX)
   - Föreläsningsanteckningar
   - Transkriptioner från inspelningar
   - Läroböcker/artiklar som använts
   ```

3. **INGEN filkopiering sker!**

4. session.yaml:
   ```yaml
   source:
     original_path: null
     filename: null
     copied_to: null
   
   working:
     path: null
     validation_status: "not_validated"
   
   methodology:
     entry_point: "m1"
     active_module: "m1"
   ```

### Scenario 2: Med source_file (OVANLIGT för M1)
```python
step0_start(
    output_folder="/path/to/output",
    entry_point="m1",
    source_file="/path/to/some_file.md"  # Onödigt!
)
```

**Resultat:**
1. Logger WARNING: "source_file will be ignored"
2. INGEN kopiering av filen
3. Samma resultat som Scenario 1

---

## JÄMFÖRELSE: Entry Point M1 vs D

### Entry Point M1 (Materials)
```python
"m1": {
    "requires_source_file": False  # ← INGEN fil behövs
}
```

**När används:**
- Startar från undervisningsmaterial (presentationer, transkriptioner)
- Material läggs i 00_materials/ MANUELLT eller refereras via sources.yaml
- M1 Stage 0 analyserar materialet
- M1 Stage 5 SKAPAR lärandemål.md → det blir source för M2

**Filflöde:**
```
[Material i 00_materials/ eller sources.yaml]
    ↓
[M1 Stage 0-5 analys]
    ↓
[methodology/m1_objectives.md SKAPAS]
    ↓
[Används som input till M2]
```

### Entry Point D (Pipeline)
```python
"pipeline": {
    "requires_source_file": True  # ← FIL KRÄVS!
}
```

**När används:**
- Startar från färdiga frågor (markdown)
- source_file MÅSTE anges
- Filen KOPIERAS till 01_source/ och 02_working/

**Filflöde:**
```
[questions.md]
    ↓ KOPIERAS
[01_source/questions.md] (original, read-only)
[02_working/questions.md] (editable)
    ↓
[Step 1: Transform]
    ↓
[Step 2: Validate]
    ↓
[Step 4: Export → QTI]
```

---

## VAD HÄNDE I CHATTEN?

### Problem
Claude (den tidigare sessionen) försökte KOPIERA transkriptionerna:
```
Filesystem icon: write_file
```

Detta MISSLYCKADES eftersom:
1. Filesystem write_file hade problem
2. Det är INTE vad M1 entry point ska göra

### Niklas Lösning: sources.yaml
**Assessment-MCP mönster - MYCKET BÄTTRE!**

```yaml
# sources.yaml
sources:
  transcriptions:
    - path: /Users/.../Recording Cellen.txt
      type: lecture_transcript
      date: 2025-10-20
      topic: Cellen
    - path: /Users/.../Recording 2 virus.txt
      type: lecture_transcript
      date: 2025-10-20
      topic: Virus
  
  curriculum:
    - path: https://syllabuswebb.skolverket.se/...
      type: curriculum
      source: Skolverket
```

**Fördelar:**
- ✅ INGEN duplikering av filer
- ✅ Versionshantering enklare (ändra original → uppdateras automatiskt)
- ✅ Tydlig referens till källor
- ✅ Metadata om varje källa
- ✅ Kan använda URLs direkt

---

## REKOMMENDERAT WORKFLOW FÖR M1

### Steg 1: Skapa session (UTAN source_file)
```
step0_start(
    output_folder="/Users/.../Exams/QF/",
    project_name="QF_test_2",
    entry_point="m1"
    # INGEN source_file!
)
```

### Steg 2: Skapa sources.yaml MANUELLT
Antingen:
- **A)** Claude skapar sources.yaml med referenser
- **B)** Läraren lägger filer i 00_materials/ manuellt

### Steg 3: M1 Stage 0 - Material Analysis
Claude läser:
- sources.yaml → hittar filer
- ELLER läser direkt från 00_materials/
- Analyserar innehåll
- Skapar initial analys

### Steg 4: M1 Stage 1-5
Dialog med läraren genom qf-scaffolding load_stage

### Steg 5: M1 Output
M1 SKAPAR filen:
```
methodology/m1_objectives.md
```

Denna fil blir sedan source för M2!

---

## SOURCES.YAML vs KOPIERING

### Assessment-MCP Pattern (sources.yaml)
```
Project/
├── sources.yaml          ← Referenser till externa filer
├── methodology/          ← Arbetsfiler/outputs
└── session.yaml
```

**Pros:**
- Ingen duplikering
- Enkla uppdateringar
- Tydliga referenser
- Kan hantera stora filer (transkriptioner)

**Cons:**
- Filer måste finnas på ursprungsplats
- Flyttar man mappen → länkar bryts

### QuestionForge Original Pattern (kopiering)
```
Project/
├── 01_source/original.md   ← Kopia (read-only)
├── 02_working/original.md  ← Kopia (editable)
└── session.yaml
```

**Pros:**
- Self-contained projekt
- Portabelt
- Säkert från ändringar i original

**Cons:**
- Duplikering
- Versionskonflikter
- Tar mer diskutrymme

---

## REKOMMENDATION

### För Entry Point M1 (Materials):
**✅ Använd sources.yaml (Assessment-MCP pattern)**

Varför:
1. Material är ofta stort (transkriptioner, presentationer)
2. Material uppdateras sällan under projektet
3. Tydligare vad som är källa vs output
4. Ingen risk att råka editera original

### För Entry Point D (Pipeline):
**✅ Använd kopiering (QuestionForge pattern)**

Varför:
1. Frågor editeras MYCKET under Step 1
2. Vill bevara original
3. Behöver working copy för transformations
4. Relativt små filer

---

## SAMMANFATTNING

**Niklas fråga:**
> "låt oss noga tänka igenom vad som händer i första steget!! filer som kopieras..."

**SVAR:**
För Entry Point M1 (materials):
- ❌ INGA filer kopieras automatiskt
- ✅ sources.yaml är rätt approach
- ✅ 00_materials/ är tom (eller får README.md)
- ✅ M1 läser från sources.yaml-referenser
- ✅ M1 SKAPAR output i methodology/

**Workflow:**
```
1. step0_start(entry_point="m1")        → Skapar tom struktur
2. Skapa sources.yaml                    → Referenser till material
3. load_stage(module="m1", stage=0)     → Läser från sources
4. M1 Stage 0-5                          → Analyserar material
5. M1 output: methodology/m1_objectives.md → Skapas av processen
```

**Koden har rätt:**
- `requires_source_file: False` för M1
- Ingen automatisk kopiering
- sources.yaml är bättre lösning än kopiering för M1

---

*Analys: 2026-01-14 23:10*  
*QuestionForge Entry Point M1 Filhantering*
