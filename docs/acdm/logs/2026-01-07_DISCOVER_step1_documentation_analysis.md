# ANALYS: Step 1 Guided Build - Dokumentationsöversikt

**Datum:** 2026-01-07  
**Status:** DISCOVER-fas  
**Metod:** Försiktig, grundlig analys

---

## DOKUMENTATION SOM FINNS

### 1. OUTPUT-specifikationer (QTI XML)

**Plats:** `/QuestionForge/packages/qti-core/templates/xml/`

| Fil | Frågetyp | Status |
|-----|----------|--------|
| multiple_choice_single.xml | MC single | ✅ Ready |
| multiple_response.xml | MC multiple | ✅ Ready |
| true_false.xml | Sant/Falskt | ✅ Ready |
| text_entry.xml | Fill-in-blank | ✅ Ready |
| text_entry_math.xml | Math entry | ✅ Ready |
| text_entry_numeric.xml | Numeric entry | ✅ Ready |
| inline_choice.xml | Dropdown | ✅ Ready |
| match.xml | Matching | ✅ Ready |
| hotspot.xml | Click-on-image | ✅ Ready |
| graphicgapmatch_v2.xml | Drag-to-image | ✅ Ready |
| text_entry_graphic.xml | Fill-in-on-image | ✅ Ready |
| text_area.xml | Short text | ✅ Ready |
| essay.xml | Long text | ✅ Ready |
| audio_record.xml | Audio | ✅ Ready |
| composite_editor.xml | Mixed | ✅ Ready |
| nativehtml.xml | Info page | ✅ Ready |
| gapmatch.xml | Drag-to-gaps | ✅ Ready |

**Totalt:** 17 frågetyper, 87% täckning av Inspera-funktioner

**Innehåll:** `{{PLACEHOLDER}}` syntax för dynamiskt innehåll

---

### 2. INPUT-specifikationer (Markdown format)

**Plats:** `/QTI-Generator-for-Inspera_MPC/docs/specs/MQG_bb6_v6.5.md`

**Innehåll:** Komplett specifikation för markdown-format:

```markdown
# Q001 Title
^question Q001
^type multiple_choice_single
^identifier MC_Q001
^points 1
^labels #Tag1 #Tag2

@field: question_text
...
@end_field

@field: options
...
@end_field

@field: feedback
@@field: general_feedback
...
@@end_field
@end_field
```

**Syntax:**
- `^key value` = Metadata
- `@field: identifier` / `@end_field` = Top-level fields
- `@@field: identifier` / `@@end_field` = Subfields (nested)

**Täckning:** Alla 17 frågetyper dokumenterade med templates

---

### 3. Validator (Befintlig kod)

**Plats:** `/QTI-Generator-for-Inspera/validate_mqg_format.py`

**Funktion:** Validerar markdown mot v6.5 spec

**Vad den kollar:**
- `^type` finns och är giltig
- `^identifier` finns och är unik
- `^points` finns
- `^labels` finns med Bloom + Difficulty
- Rätt `@field:` för frågetyp
- Rätt `@@field:` för feedback
- Match-pairs format
- Blank/dropdown placeholders

---

### 4. MPC_MQG_v3 (Tidigare försök)

**Plats:** `/AIED_EdTech_projects/MPC_MQG_v3/`

**Vad det gjorde:**
- Manifest-tracking
- Version-hantering
- BB6 "konvertering" (placeholder - kopierade bara filen)

**Varför det "inte blev bra":**
- `convertToBB6()` var INTE implementerad
- Kommentar i kod: "Real BB6 conversion requires LLM assistance"
- Ingen faktisk transformering av content
- Bara validering + filkopiering

---

## VAD STEP 1 BEHÖVER (Analys)

### Konceptuell förståelse

```
Step 1: Guided Build
─────────────────────────────────────────────────────────
INPUT:  Ostrukturerade eller delvis strukturerade frågor
        (kan sakna metadata, fel format, ofullständiga)

PROCESS: Fråga-för-fråga genomgång
        1. Identifiera frågetyp
        2. Jämför med spec för den typen
        3. Visa vad som saknas/är fel
        4. Guida användaren att fixa
        5. "Fix once, apply to all similar"

OUTPUT: Markdown som klarar Step 2 validering
─────────────────────────────────────────────────────────
```

### Kritiska frågor att besvara

| Fråga | Svar/Analys |
|-------|-------------|
| **Vad är input?** | Markdown med frågor som KAN vara ofullständiga |
| **Vem identifierar frågetyp?** | Claude (AI) baserat på innehåll |
| **Vad är en "spec"?** | MQG_bb6_v6.5.md - fält-krav per typ |
| **Vad betyder "similar"?** | Samma `^type` (t.ex. alla multiple_choice_single) |
| **Hur fungerar "fix all similar"?** | Om Q001 (MC) får feedback-fix, applicera på Q005, Q012 (också MC) |

---

## GAP-ANALYS

### Dokumentation som FINNS:
- [x] OUTPUT-format (XML templates)
- [x] INPUT-format (MQG_bb6_v6.5.md)
- [x] Validator (Python)
- [x] Konceptuell beskrivning i qf-pipeline-spec.md

### Dokumentation som SAKNAS:

| Gap | Beskrivning | Kritiskt? |
|-----|-------------|-----------|
| **ADR för Step 1** | Arkitekturbeslut | 🔴 Ja |
| **"Fix similar" algoritm** | Hur identifiera och applicera | 🔴 Ja |
| **Dialogue flow** | Exakt hur Claude guidar | 🟡 Medium |
| **State management** | Hur spåra progress genom frågor | 🟡 Medium |
| **Error categories** | Vilka fel kan fixas automatiskt vs manuellt | 🟡 Medium |

---

## KOPPLING INPUT → OUTPUT

```
┌─────────────────────────────────────────────────────────────────┐
│  MQG_bb6_v6.5.md          →    Step 1: Guided Build            │
│  (INPUT spec)                  (SAKNAS)                         │
│                                                                  │
│  ^type multiple_choice_single                                    │
│  ^identifier MC_Q001                                             │
│  @field: options           →   Kolla att dessa finns            │
│  @field: answer                och är korrekta                   │
│  @field: feedback                                                │
│    @@field: general_feedback                                     │
│    @@field: correct_feedback                                     │
│    ...                                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: Validate          →    validate_mqg_format.py          │
│  (FINNS)                        (FINNS)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: Export            →    XML Templates                   │
│  (FINNS)                        (FINNS)                         │
│                                                                  │
│  multiple_choice_single.xml                                      │
│  {{IDENTIFIER}}, {{TITLE}}, {{CHOICES}}...                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## REKOMMENDATION: NÄSTA STEG

### Fas 1: Förstå problemet djupare

1. **Analysera verkliga fel-scenarion**
   - Vilka fel är vanligast? (saknar ^labels, fel feedback-struktur?)
   - Vilka fel kan Claude fixa automatiskt?
   - Vilka kräver användarinput?

2. **Definiera "similar"**
   - Är det samma `^type`?
   - Eller samma typ av FEL? (t.ex. "saknar ^labels")

### Fas 2: Skapa ADR-013

Innan implementation behövs arkitekturbeslut:
- Tool-design (många små tools vs få stora)
- State management (hur spåra var vi är)
- Fix-strategi (vad kan automatiseras)

### Fas 3: Prototyp

Börja med EN frågetyp (t.ex. multiple_choice_single):
- Hur ser en "broken" fråga ut?
- Vad behöver fixas?
- Hur guidar Claude?

---

## ÖPPEN FRÅGA TILL NIKLAS

**Vad är det vanligaste scenariot?**

A) Frågor som är HELT ostrukturerade (ren text, ingen markdown-struktur)
B) Frågor som har DELVIS struktur (har @field: men saknar metadata)
C) Frågor som har struktur men FEL (t.ex. v6.4 format istället för v6.5)
D) Annat?

Detta påverkar hur Step 1 bör designas.

---

*DISCOVER-fas analys | 2026-01-07*
