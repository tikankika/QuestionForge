# RFC-013 Updates for Desktop

**Datum:** 2026-01-25
**Uppdaterad:** 2026-01-25 (validation responsibilities)
**Från:** Code session review + Desktop diskussion

---

## Del A: Tekniska fixes (4 st)

## Del B: Validation Responsibilities (6 beslut)

---

# DEL A: TEKNISKA FIXES

## 4 Ändringar att göra i RFC-013

### 1. Question Type Names - FIX
**Fel:** `multiple_choice_question`
**Rätt:** `multiple_choice_single` (en rätt) och `multiple_response` (flera rätt)

Alla korrekta typnamn:
```
multiple_choice_single    text_entry              match
multiple_response         text_entry_numeric      hotspot
true_false                text_entry_math         graphicgapmatch_v2
inline_choice             text_area               text_entry_graphic
essay                     audio_record            composite_editor
nativehtml
```

### 2. Ta bort Line Numbering - REMOVE
**Beslut:** Line numbers är over-engineering. Question IDs räcker.

Ta bort:
- Section om "Line Numbering System"
- `001`, `002` prefix i alla exempel
- "strip line numbers before export" logik

Question ID (`Q001`, `Q002`) + YAML frontmatter ger all tracking vi behöver.

### 3. Lägg till RFC-012 Reference - ADD
I Introduction, lägg till:

```markdown
### Related RFCs
- **RFC-012:** Subprocess architecture, unified validator, single source of truth for parsing
```

### 4. Step 2 Already Implemented - NOTE
I Step 2 section, lägg till note:

```markdown
**Note:** Validator implementerad i RFC-012. Använder `markdown_parser.validate()` -
samma parser som Step 4. Garanterar: validate pass → export works.
```

---

## Sammanfattning

| Issue | Åtgärd |
|-------|--------|
| Question type names | Byt `multiple_choice_question` → `multiple_choice_single` |
| Line numbering | Ta bort helt - använd Question IDs istället |
| RFC-012 reference | Lägg till i Introduction |
| Step 2 validator | Notera att det redan är implementerat |

---

# DEL B: VALIDATION RESPONSIBILITIES

Från diskussion om överlappning mellan M5, Step 1, Step 2, Step 3.

---

## Beslut 5: M5 Ansvar - STRUKTURELLT KORREKT OUTPUT

M5 ska generera markdown med korrekt struktur från början:

```
M5's ansvar:
├── Separatorer mellan frågor (---)
├── Korrekt field syntax (@field: / @end_field)
├── Komplett struktur för varje frågetyp
└── Valid MQG format

OUTPUT: Strukturellt valid markdown
(Kan ha content-issues, men struktur = OK)
```

**Uppdatera i RFC-013:** M5 section ska tydligt specificera att output ska vara strukturellt korrekt.

---

## Beslut 6: Step 1 Ansvar - SÄKERHETSNÄT

Step 1 fixar "oväntade" strukturproblem som INTE borde finnas:

```
Step 1's ansvar:
├── M5 buggar (genererade fel syntax)
├── File corruption (user redigerade manuellt)
├── Import från äldre format
└── Oväntade edge cases

Om M5 är perfekt → Step 1 hittar 0 issues ✅
```

**Uppdatera i RFC-013:** Step 1 är ett säkerhetsnät, inte en obligatorisk fix-station.

---

## Beslut 7: "Structural" Definition - RELATIV, INTE FAST

**Nyckelinsikt:** "Structural" betyder "Step 3 kan inte auto-fixa detta JUST NU"

```
Samma error kan vara:
├── "Structural" → När Step 3 saknar pattern
└── "Auto-fixable" → När Step 3 lärt sig pattern

Över tid: Färre saker är "structural" (Step 3 lär sig)
```

**Startlista för "structural" (alltid route till Step 1 i iteration 0):**
- Missing separator between questions
- Unclosed fields (@field utan @end_field)
- Unknown field types

**Uppdatera i RFC-013:** Förklara att "structural" är relativ kategori.

---

## Beslut 8: Pattern Separation - TVÅ SEPARATA SYSTEM

Step 1 och Step 3 har SEPARATA pattern-databaser:

```
Step 1 patterns:
├── Används ENDAST i Step 1
├── Hjälper AI föreslå fix till lärare
└── "Baserat på 15 tidigare filer, separator brukar vara här"

Step 3 patterns:
├── Används ENDAST i Step 3
├── Auto-appliceras utan lärare
└── "Denna error har auto-fixats 47 gånger framgångsrikt"

INGEN DELNING mellan systemen (enklare, inga edge cases)
```

**Uppdatera i RFC-013:** Specificera att pattern-databaser är separata.

---

## Beslut 9: Step 3 Routing - FÖRSÖK AUTO-FIXA ÄVEN "STRUCTURAL"

I iteration > 0, försöker Step 3 auto-fixa även "structural" errors:

```python
# Step 3 logik (pseudokod)
for error in errors:
    pattern = find_pattern(error, min_confidence=0.9)

    if pattern:
        # Lärt pattern med hög confidence
        apply_pattern(error)  # Auto-fix
    else:
        if iteration == 0:
            route_to_step1(error)  # Första gången: lärare
        else:
            mark_unfixable(error)  # Redan försökt: ge upp
```

**Uppdatera i RFC-013:** Step 3 försöker alltid auto-fixa om pattern finns.

---

## Beslut 10: Skip Tracking - INGEN DELNING

```
Step 1: Teacher skippar issue
    ↓ (ingen tracking till Step 3)
Step 2: Validation failar (samma issue)
    ↓
Step 3: Försöker auto-fixa
    ├── Har pattern? → Auto-fix → Success
    └── Inget pattern? → Route till Step 1 ELLER fail
```

**Resultat:** Teacher får ny chans i Step 1, eller filen failar.

**Uppdatera i RFC-013:** Step 3 vet INTE vad som skippades i Step 1.

---

# SAMMANFATTNING ALLA BESLUT

| # | Beslut | Kort |
|---|--------|------|
| 1 | Question type names | `multiple_choice_single`, inte `multiple_choice_question` |
| 2 | Line numbering | Ta bort - Question IDs räcker |
| 3 | RFC-012 reference | Lägg till i Introduction |
| 4 | Step 2 validator | Redan implementerat (RFC-012) |
| 5 | M5 ansvar | Generera strukturellt korrekt output |
| 6 | Step 1 ansvar | Säkerhetsnät för oväntade problem |
| 7 | "Structural" definition | Relativ - "kan inte auto-fixas just nu" |
| 8 | Pattern separation | Två separata databaser (Step 1 / Step 3) |
| 9 | Step 3 routing | Försök auto-fixa även structural om pattern finns |
| 10 | Skip tracking | Ingen delning - skipped failar i Step 2 |

---

## Flowchart att lägga till i RFC-013

```
M5: Generera markdown
  ↓ (ska vara strukturellt perfekt)

Step 1: Review för oväntade issues
  ├─ 0 issues? → Step 2
  ├─ Issues? → Teacher fixar → Step 2
  └─ Skip? → Step 2 (kommer faila)

Step 2: Validera
  ├─ Valid? → Step 4 Export
  └─ Invalid? → Step 3

Step 3: Auto-fix iteration
  ├─ Auto-fixable? → Apply → Step 2 (loop)
  ├─ Missing content? → Route till M5
  ├─ Structural (inget pattern)? → Route till Step 1
  └─ Max iterations? → Rapport failure
```
