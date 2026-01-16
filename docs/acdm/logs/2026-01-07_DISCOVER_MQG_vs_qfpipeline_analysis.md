# DJUPANALYS: MQG vs qf-pipeline - Två System, En Process

**Datum:** 2026-01-07  
**Status:** KRITISK INSIKT  
**Metod:** Försiktig, metodisk analys

---

## UPPTÄCKT: TVÅ OLIKA SYSTEM

### System 1: MQG (Modular Question Generation)

**Typ:** PEDAGOGISKT RAMVERK  
**Plats:** `/Modular QGen - Modular Question Generation Framework/docs/MQG_0.2/`  
**Dokumentation:** ~8,000 rader, 46 filer

**Syfte:** Guida lärare genom HELA processen från innehåll till export

```
BB1: Content Analysis        (4-6 timmar)
  ↓
BB2: Assessment Design       (1.5-2.5 timmar)
  ↓
BB3: Technical Setup         (2-3 timmar)
  ↓
BB4: Question Generation     (varierande)
  ↓
BB4.5: Exam Assembly         (15-30 min)
  ↓
BB5: Quality Assurance       (varierande)
  ↓
BB6: Export & Integration    (30-60 min)
```

**Kärnidé:** 
- Läraren har pedagogisk auktoritet
- AI faciliterar dialogen
- Stage gates förhindrar att AI rusar iväg

---

### System 2: qf-pipeline

**Typ:** TEKNISKT VERKTYG (MCP)  
**Plats:** `/QuestionForge/packages/qf-pipeline/`  
**Dokumentation:** ~500 rader spec

**Syfte:** Automatisera validering och export till QTI

```
Step 0: Session Management
  ↓
Step 1: Guided Build         ← SAKNAS IMPLEMENTATION
  ↓
Step 2: Validate             ← FUNGERAR (mot BB6 v6.5)
  ↓
Step 3: Decision             ← DOKUMENTERAD (ADR-010, 011)
  ↓
Step 4: Export               ← FUNGERAR
```

**Kärnidé:**
- Teknisk pipeline
- Validera markdown-format
- Exportera till QTI

---

## RELATIONEN MELLAN SYSTEMEN

```
┌─────────────────────────────────────────────────────────────────┐
│                    MQG FRAMEWORK                                │
│                                                                  │
│   BB1 → BB2 → BB3 → BB4 → BB4.5 → BB5 → BB6                     │
│                                          │                       │
│                                          │ OUTPUT:               │
│                                          │ Markdown i BB6 v6.5   │
│                                          │ format                │
└──────────────────────────────────────────┼───────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    qf-pipeline                                   │
│                                                                  │
│   Step 0 → Step 1 → Step 2 → Step 3 → Step 4                    │
│            (hjälp)  (valid)  (beslut) (export)                   │
│                                                                  │
│   INPUT: Markdown (kan vara ofullständigt)                       │
│   OUTPUT: QTI-paket för Inspera                                  │
└─────────────────────────────────────────────────────────────────┘
```

**MQG BB6 = Specifikationen som qf-pipeline Step 2 validerar mot**

---

## VAD ÄR "SPEC" FÖR FRÅGETYP?

### Det som FINNS:

**1. MQG_bb6_v6.5.md** (~1000 rader)
- Komplett specifikation för markdown-format
- Alla 17 frågetyper med templates
- Syntax: `^metadata`, `@field:`, `@@field:`
- Validerings-regler

**2. XML Templates** (17 filer)
- OUTPUT-format för QTI
- `{{PLACEHOLDER}}` syntax
- Mappas från markdown via parser

### Det som SAKNAS:

**"Förenklad spec per frågetyp"**

Exempel på vad som skulle behövas för Step 1:

```yaml
# multiple_choice_single.yaml
name: "Multiple Choice (Single Answer)"
code: "multiple_choice_single"
aliases: ["MCSA", "MC single", "flerval"]

required_metadata:
  - ^question
  - ^type
  - ^identifier
  - ^points
  - ^labels

required_fields:
  - question_text
  - options (min 3, max 6)
  - answer (en bokstav)
  - feedback

optional_fields:
  - ^title
  - ^shuffle

common_errors:
  - "Saknar ^labels med Bloom + Difficulty"
  - "Saknar feedback-subfields"
  - "Fel antal options (behöver 3-6)"

fix_examples:
  - error: "Saknar ^labels"
    fix: "Lägg till: ^labels #COURSE_CODE #Topic #Bloom #Difficulty"
```

---

## KRITISK INSIKT: "DET HAR ALDRIG BLIVIT BRA"

### Varför specifikationer misslyckats:

**Problem 1: För komplicerat**
- MQG_bb6_v6.5.md är 1000 rader
- Svårt att överblicka
- Ingen "quick reference" per frågetyp

**Problem 2: Två system, oklar koppling**
- MQG är pedagogiskt ramverk
- qf-pipeline är tekniskt verktyg
- Oklart var de möts

**Problem 3: Ingen "error catalog"**
- Vilka fel är vanligast?
- Vilka kan fixas automatiskt?
- Vilka kräver lärarbeslut?

**Problem 4: MPC_MQG_v3 var placeholder**
- `convertToBB6()` kopierade bara filen
- Ingen faktisk transformation
- Kommentar: "Real conversion requires LLM"

---

## VAD SKA qf-pipeline Step 1 GÖRA?

### Scenario A: Frågor som är HELT ostrukturerade

```
Input:
Vad är mitokondrien?
a) Cellens kraftverk
b) Cellkärnan
c) Cellmembranet

Output efter Step 1:
# Q001 Mitokondrien
^question Q001
^type multiple_choice_single
^identifier BIOG_Q001
^points 1
^labels #BIOG001X #Cellbiologi #Remember #Easy

@field: question_text
Vad är mitokondrien?
@end_field

@field: options
A. Cellens kraftverk
B. Cellkärnan
C. Cellmembranet
@end_field

@field: answer
A
@end_field

@field: feedback
@@field: general_feedback
Mitokondrien kallas cellens kraftverk...
@@end_field
...
@end_field
```

### Scenario B: Frågor med DELVIS struktur

```
Input:
# Q001 Mitokondrien
^type multiple_choice_single

@field: question_text
Vad är mitokondrien?
@end_field

@field: options
a) Cellens kraftverk
b) Cellkärnan
@end_field

Problem: Saknar ^identifier, ^points, ^labels, answer, feedback
```

### Scenario C: Frågor med FEL format (v6.4 → v6.5)

```
Input (v6.4):
@question: Q001
@type: multiple_choice_single
@tags: #Easy #Remember

Output (v6.5):
^question Q001
^type multiple_choice_single
^labels #Easy #Remember
```

---

## VEM GÖR VAD?

### Alternativ 1: Claude gör ALLT (nuvarande qf-pipeline-spec.md)

```
Claude:
  - Identifierar frågetyp
  - Jämför med spec
  - Föreslår fixar
  - Applicerar fixar
  - "Fix similar" automatiskt

MCP-tools:
  - start_build_session() - starta session
  - get_question() - hämta en fråga
  - suggest_fixes() - returnera förslag
  - apply_fix() - skriv fix till fil
  - next_question() - gå till nästa
```

**Problem:** Kräver att Claude har full spec i context

### Alternativ 2: MCP-tools gör validering, Claude guidar

```
MCP-tools:
  - validate_question(q) - returnera fel-lista per fråga
  - get_type_requirements(type) - returnera vad som krävs
  - apply_template(q, type) - applicera template

Claude:
  - Tolkar fel-listan för användaren
  - Förklarar vad som behövs
  - Hjälper skriva innehåll
  - Bekräftar fixar
```

**Fördel:** Claude behöver inte hela spec, tools returnerar relevant info

### Alternativ 3: Hybrid (REKOMMENDERAD)

```
Step 1.1: Analys (MCP)
  - Läs fil
  - Identifiera alla frågor
  - Per fråga: validera mot typ-spec
  - Returnera: lista av frågor med fel

Step 1.2: Guidning (Claude)
  - Visa sammanfattning av fel
  - Fråga: "Vill du fixa alla [saknar labels] på en gång?"
  - Hjälp skriva innehåll som saknas

Step 1.3: Applicera (MCP)
  - Skriv fixar till fil
  - Validera resultat
  - Gå vidare
```

---

## NÄSTA STEG (FÖRSLAG)

### Steg 1: Definiera "Type Requirements" format

Skapa förenklad spec per frågetyp:
- Vad MÅSTE finnas
- Vad ÄR VALFRITT
- Vanliga fel
- Exempel på fix

**Format:** YAML eller JSON (maskinläsbart)
**Plats:** `/packages/qf-pipeline/src/qf_pipeline/specs/`

### Steg 2: Analysera vanliga fel

Gå igenom verkliga frågedokument:
- Vilka fel är vanligast?
- Vilka kan fixas automatiskt?
- Vilka kräver lärarbeslut?

### Steg 3: Skapa ADR-013

Arkitekturbeslut för Step 1:
- Tool-design
- Claude vs MCP ansvarsfördelning
- "Fix similar" strategi

### Steg 4: Minimal prototyp

Börja med EN frågetyp (multiple_choice_single):
- Implementera validate_question()
- Implementera get_type_requirements()
- Testa flödet

---

## ÖPPNA FRÅGOR TILL NIKLAS

1. **Vilket scenario är vanligast?**
   - A) Helt ostrukturerade frågor
   - B) Delvis strukturerade
   - C) Fel format (v6.4 → v6.5)
   - D) Blandning

2. **Vad har "aldrig blivit bra" specifikt?**
   - Är specen för komplicerad?
   - Saknas verktyg?
   - Fel abstraktionsnivå?

3. **Ska Step 1 vara i qf-pipeline eller separat MCP?**
   - qf-pipeline = teknisk pipeline
   - Kanske Step 1 är för "pedagogisk" för att passa där?

4. **Vad är relationen till MQG BB4?**
   - BB4 Stage 4C = formatera frågor (med lärardialog)
   - Step 1 = samma sak? Eller något annat?

---

*DISCOVER-fas djupanalys | 2026-01-07*
