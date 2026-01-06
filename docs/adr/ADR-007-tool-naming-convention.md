# ADR-007: Tool Naming Convention för qf-pipeline

## Status
**Accepted**

## Datum
2026-01-06

## Kontext

qf-pipeline har en pipeline-struktur med distinkta steg (Steps 0-4). Under utvecklingen uppstod frågan om hur MCP-verktyg ska namnges för att:

1. Tydliggöra vilket steg verktyget tillhör
2. Hålla namnen konsekventa med Assessment_suite (som använder `phaseN_`)
3. Undvika förvirring när fler verktyg läggs till

### Referens: Assessment_suite mönster

Assessment_suite använder `phaseN_` prefix:
```
phase4a_questions
phase4b_rubric
phase6_start
phase6_status
```

Plus cross-phase verktyg utan prefix:
```
rubric_read
rubric_edit
```

## Beslut

### Namnkonvention: `stepN_verb`

Alla qf-pipeline verktyg använder prefix `stepN_` där N är step-nummer:

```
step0_  → Session Management
step1_  → Guided Build
step2_  → Validator
step3_  → Decision
step4_  → Export
```

### Regler

1. **Prefix:** `stepN_` (step + nummer + underscore)
2. **Verb:** Kort, beskrivande (start, validate, export)
3. **Cross-step verktyg:** Inget prefix (ex: `list_types`)
4. **Konsekvent med Assessment_suite:** Samma mönster som `phaseN_`

## Verktygsnamn

### Step 0: Session Management

| Verktyg | Funktion |
|---------|----------|
| `step0_start` | Skapa ny session ELLER ladda befintlig |
| `step0_status` | Visa sessionstatus |

### Step 1: Guided Build (PLANERAD)

| Verktyg | Funktion |
|---------|----------|
| `step1_build` | Starta/fortsätt guided build |
| `step1_fix` | Applicera fix (+ apply to similar) |
| `step1_skip` | Hoppa över aktuell fråga |
| `step1_done` | Avsluta guided build |

### Step 2: Validator

| Verktyg | Funktion |
|---------|----------|
| `step2_validate` | Validera fil (använder working_file om session aktiv) |
| `step2_validate_content` | Validera markdown-innehåll direkt (för snippets) |

### Step 3: Decision (PLANERAD)

| Verktyg | Funktion |
|---------|----------|
| `step3_choose` | Välj exportformat (QTI Questions / Question Set) |

### Step 4: Export

| Verktyg | Funktion |
|---------|----------|
| `step4_export` | Exportera till QTI-paket |

### Cross-Step (Utilities)

| Verktyg | Funktion |
|---------|----------|
| `list_types` | Lista stödda frågetyper |

## Komplett verktygslista

```
Step 0 (Session):
  step0_start     # Ny eller ladda session
  step0_status    # Visa status

Step 1 (Guided Build) - PLANERAD:
  step1_build     # Starta/fortsätt
  step1_fix       # Applicera fix
  step1_skip      # Hoppa över
  step1_done      # Avsluta

Step 2 (Validator):
  step2_validate          # Validera fil
  step2_validate_content  # Validera innehåll direkt

Step 3 (Decision) - PLANERAD:
  step3_choose    # Välj exportformat

Step 4 (Export):
  step4_export    # Skapa QTI-paket

Cross-Step:
  list_types      # Frågetyper
```

**Totalt:** 12 verktyg (5 byggda, 6 planerade, 1 utility)

## Mappning: Nuvarande → Nytt

| Nuvarande namn | Nytt namn | Status |
|----------------|-----------|--------|
| `start_session` | `step0_start` | Byggt → byt namn |
| `get_session_status` | `step0_status` | Byggt → byt namn |
| `end_session` | *(ta bort)* | Onödig |
| `load_session` | `step0_start` | Slå ihop |
| `validate_file` | `step2_validate` | Byggt → byt namn |
| `validate_content` | `step2_validate_content` | Byggt → byt namn (behålls separat) |
| `export_questions` | `step4_export` | Byggt → byt namn |
| `parse_markdown` | *(ta bort)* | Intern utility, ej publikt verktyg |
| `list_question_types` | `list_types` | Byggt → byt namn |

## Jämförelse med Assessment_suite

| Koncept | Assessment_suite | qf-pipeline |
|---------|------------------|-------------|
| Prefix | `phaseN_` | `stepN_` |
| Session | `phase6_start` | `step0_start` |
| Status | `phase6_status` | `step0_status` |
| Cross-phase | `rubric_read` | `list_types` |

## Konsekvenser

### Positiva
- Konsekvent med Assessment_suite mönster
- Tydlig visuell gruppering
- Lätt att förstå pipeline-ordning
- Skalbar för nya verktyg

### Negativa
- Kräver refaktorering av befintlig kod
- `stepN_` är lite längre än `sN_`

## Alternativ som övervägdes

### A: `sN_` (kortare)
```
s0_start, s2_validate, s4_export
```
**Avvisat:** Mindre läsbart, avviker från Assessment_suite

### B: `stepN_` (valt)
```
step0_start, step2_validate, step4_export
```
**Valt:** Konsekvent med `phaseN_`, tydligt

## Implementation

1. ✅ Uppdatera `server.py` med nya verktygsnamn
2. ✅ Slå ihop `start_session` + `load_session` → `step0_start`
3. ✅ Behåll `validate_file` → `step2_validate` och `validate_content` → `step2_validate_content` (separata)
4. ✅ Ta bort `end_session` och `parse_markdown` som publika verktyg
5. Uppdatera tester

---

## TILLÄGG: Init-verktyg (KRITISKT)

### Bakgrund

Vid testning upptäcktes att Claude hoppade över att fråga användaren om fil och mapp innan `step0_start` kördes. Detta beror på att Claude inte har instruktioner om HUR verktygen ska användas.

**Lösning:** Samma mönster som Assessment_suite - ett `init`-verktyg som Claude MÅSTE kalla först.

### Nytt verktyg: `init`

| Verktyg | Funktion |
|---------|----------|
| `init` | CALL THIS FIRST! Returnerar kritiska instruktioner |

### Specifikation

```python
def init() -> dict:
    """
    CALL THIS FIRST!
    
    Returnerar kritiska instruktioner för att använda qf-pipeline.
    Claude MÅSTE följa dessa instruktioner.
    
    Returns:
        {
            "instructions": str,       # Markdown med instruktioner
            "available_tools": [...],  # Lista på verktyg
            "critical_rules": [...]    # Regler som MÅSTE följas
        }
    """
```

### Init-instruktioner (innehåll som returneras)

```markdown
# QF-Pipeline - Kritiska Instruktioner

## REGLER (MÅSTE FÖLJAS)

1. **FRÅGA ALLTID användaren INNAN du kör step0_start:**
   - "Vilken markdown-fil vill du arbeta med?" (source_file)
   - "Var ska projektet sparas?" (output_folder)
   - Vänta på svar innan du fortsätter!

2. **ANVÄND INTE bash/cat/ls** - qf-pipeline har full filåtkomst

3. **SÄG ALDRIG "ladda upp filen"** - MCP kan läsa filer direkt

4. **FÖLJ PIPELINE-ORDNINGEN:**
   - step0_start → step2_validate → step4_export
   - Validera ALLTID innan export!

## STANDARD WORKFLOW

1. User: "Använd qf-pipeline" / "Exportera till QTI"
2. Claude: "Vilken markdown-fil vill du arbeta med?"
3. User: "/path/to/file.md"
4. Claude: "Var ska projektet sparas? (output_folder)"
5. User: "/path/to/output/"
6. Claude: [step0_start] → Skapar session
7. Claude: [step2_validate] → Validerar
8. Om valid: [step4_export] → Exporterar
   Om invalid: Visa fel, hjälp användaren fixa
```

### Tool Description (för server.py)

```python
Tool(
    name="init",
    description=(
        "CALL THIS FIRST! Returns critical instructions for using qf-pipeline. "
        "You MUST follow these instructions. "
        "ALWAYS ask user for source_file and output_folder BEFORE calling step0_start. "
        "NEVER use bash/cat/ls - MCP has full file access."
    ),
    inputSchema={
        "type": "object",
        "properties": {},
        "required": [],
    },
)
```

### Uppdaterad verktygslista

```
System:
  init                    # CALL THIS FIRST!

Step 0 (Session):
  step0_start             # Ny eller ladda session
  step0_status            # Visa status

Step 2 (Validator):
  step2_validate          # Validera fil
  step2_validate_content  # Validera innehåll

Step 4 (Export):
  step4_export            # Skapa QTI-paket

Cross-Step:
  list_types              # Frågetyper
```

**Totalt:** 7 byggda verktyg (+ 6 planerade för Step 1 och Step 3)

---

## Relaterade dokument

- [ADR-006: Session Management](ADR-006-session-management.md)
- [qf-pipeline-spec.md](../specs/qf-pipeline-spec.md)
- Assessment_suite init: `/Assessment_suite/packages/assessment-mcp/src/tools/init.ts`

---

*Dokumenterat 2026-01-06 som del av ACDM IMPLEMENT-fasen*
*Uppdaterat 2026-01-06: Tillagt init-verktyg efter testning*
