# INPUT FORMAT INVENTORY: Verkliga Filer

**Datum:** 2026-01-07  
**Status:** DISCOVER-fas  
**Källa:** Verkliga filer från Niklas

---

## ÖVERSIKT: 5 Olika Input-Format

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INPUT FORMATS                                    │
│                                                                          │
│  LEVEL 1: RAW (behöver qf-scaffolding)                                  │
│  ────────────────────────────────────                                    │
│  • Quiz_Questions_BATCH_1.md                                            │
│  • **FRÅGA:**, **RÄTT SVAR:**, **FELAKTIGA ALTERNATIV:**               │
│  • Ingen struktur, bara innehåll                                        │
│                                                                          │
│  LEVEL 2: SEMI-STRUCTURED (behöver stor transformation)                 │
│  ───────────────────────────────────────────────────────                │
│  • TRA265 L2a/L2b format                                                │
│  • Evolution_Question_Bank format                                        │
│  • Quiz_Questions_KOMPLETT_DQM format                                   │
│  • Har **Type**: ..., ## Question Text, ## Options                      │
│  • Behöver omformatera till @field: syntax                              │
│                                                                          │
│  LEVEL 3: ALMOST VALID (behöver syntax-konvertering)                    │
│  ────────────────────────────────────────────────────                   │
│  • BIOG001X_Fys_v63.md                                                  │
│  • Har @question:, @field: men fel syntax                               │
│  • @key: → ^key konvertering                                            │
│                                                                          │
│  LEVEL 4: VALID v6.5                                                    │
│  ──────────────────                                                     │
│  • BIOG001X_Fys_v65_5.md                                                │
│  • Redan korrekt format                                                 │
│  • Passerar Step 2 validation                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## LEVEL 1: RAW FORMAT

### Exempel: Quiz_Questions_BATCH_1.md

```markdown
## Q001 - Cellkärnans närvaro

**Learning Objective:** LO1 (Förstå skillnader prokaryot/eukaryot)  
**Svårighetsnivå:** Lätt  
**Misconception addressed:** Grundförståelse av celltyper

**FRÅGA:**
Vad är den viktigaste skillnaden mellan prokaryota och eukaryota celler?

**RÄTT SVAR:**
Eukaryota celler har cellkärna där DNA förvaras, medan prokaryota 
celler (bakterier) saknar cellkärna och har sitt DNA fritt i cytoplasman.

**FELAKTIGA ALTERNATIV (distractors):**
- Prokaryota celler har cellkärna, eukaryota celler har inte cellkärna
- Prokaryota celler är större än eukaryota celler
- Eukaryota celler saknar DNA

**FEEDBACK:**
Rätt! Eukaryota celler har en cellkärna...
```

**Karakteristik:**
- Ingen explicit `type` - måste gissas från innehåll
- Svenska informella headers
- Fritt format för svar/alternativ
- Ingen metadata-struktur

**Transformation krävs:**
1. Identifiera frågetyp (MC om det finns alternativ)
2. Extrahera rätt svar
3. Bygga fullständig struktur
4. Generera ^metadata
5. Generera all feedback

**Beslut:** → qf-scaffolding (för ostrukturerat för Step 1)

---

## LEVEL 2A: TRA265 FORMAT

### Exempel: L2a_ALL_open_questions_EN.md

```markdown
## Question A1: E-fuel System Boundary Selection

**Type**: short_response
**Identifier**: L2A_APPLY_01
**Points**: 4
**Bloom's Level**: Apply
**Expected Length**: 100-150 words

### Question Text

A company wants to assess the climate impact...

### Editor Configuration
**Initial lines**: 8
**Field width**: 100%
**Show word count**: true
**Maximum words**: 200
**Editor prompt**: Explain your chosen system boundary...

### Scoring Rubric

#### Excellent (4 points)
- Correctly identifies cradle-to-grave...

#### Good (3 points)
- Identifies correct system boundary...

### Feedback

#### General Feedback
This question tests your ability...

#### Answered Feedback
Your answer will be evaluated...

#### Unanswered Feedback
Please provide an answer...
```

**Karakteristik:**
- Explicit `**Type**: short_response`
- Markdown headers `### Question Text`
- Rubric som punktlistor
- English
- Essay/short_response fokus

**Transformation krävs:**
1. `**Type**: short_response` → `^type text_area`
2. `### Question Text` → `@field: question_text`
3. Rubric → `@field: scoring_rubric`
4. Editor config → `@field: editor_config` med ^metadata
5. Feedback sections → nested `@@field:`

---

## LEVEL 2B: KOMPLETT DQM FORMAT

### Exempel: Quiz_Questions_KOMPLETT_DQM_Revision_All_40.md

```markdown
# Question 1: Prokaryot vs Eukaryot grundskillnad

**Type**: multiple_choice_single  
**Identifier**: MC_Q001  
**Points**: 1  
**Learning Objectives**: LO1  
**Bloom's Level**: Understand  
**Language**: sv  
**Difficulty**: easy

## Question Text
Vad är den viktigaste skillnaden mellan prokaryota och eukaryota celler?

## Options

**A)** Eukaryota celler har membranomslutna organeller... (13 ord)

**B)** Eukaryota celler har cellkärna... (15 ord) ✓

**C)** Eukaryota celler har linjärt DNA... (14 ord)

**D)** Eukaryota celler har större ribosomer... (14 ord)

## Answer
B

## Feedback

### General Feedback
Cellkärnan är den fundamentala skillnaden...

### Correct Response Feedback
Rätt! Eukaryota celler har en cellkärna...

### Incorrect Response Feedback
Tänk på vad som DEFINIERAR dessa två celltyper...

### Unanswered Feedback
Besvara frågan genom att tänka på...
```

**Karakteristik:**
- `# Question 1: Title` header
- `**Type**: multiple_choice_single`
- `## Options` med **A)** format
- `✓` för rätt svar
- Svenska
- Feedback i ### headers

**Transformation krävs:**
1. `# Question 1: Title` → `# Q001 Title`
2. `**Type**: X` → `^type X`
3. `## Question Text` → `@field: question_text`
4. `## Options` med **A)** → `@field: options` med `A.`
5. `✓` → parse för `@field: answer`
6. Feedback ### → `@@field:` nested

---

## LEVEL 2C: EVOLUTION FORMAT

### Exempel: Evolution_Question_Bank_60q.md

```markdown
# Question 1: Evolutionsdefinition (Ordagrann)

**Type**: fill_in_the_blank
**Identifier**: EVOL_Q001
**Points**: 1
**Learning Objectives**: LO1
**Bloom's Level**: Remember
**Difficulty**: easy
**Language**: sv

## Question Text

Enligt den definition som användes i lektionerna:

"Evolution är förändring i en populations _____ från en generation..."

## Correct Answer
allelfrekvens

## Accepted Alternatives
- Allelfrekvens
- allel frekvens

## Case Sensitive
false

## Expected Length
15

## Feedback

### General Feedback
Detta är den centrala definitionen...
```

**Karakteristik:**
- Liknar KOMPLETT DQM men:
- `## Correct Answer` istället för `## Answer`
- `## Accepted Alternatives` som lista
- `## Case Sensitive` explicit
- `fill_in_the_blank` som type

**Transformation krävs:**
1. Samma som 2B plus:
2. `## Correct Answer` + `## Accepted Alternatives` → `@@field: blank_1` med `^Correct_Answers`
3. `## Case Sensitive` → `^Case_Sensitive`
4. `_____` placeholder → `{{blank_1}}`

---

## LEVEL 3: GAMMAL SYNTAX (v6.3/v6.4)

### Exempel: BIOG001X_Fys_v63.md

```markdown
# Q001 Muskelrörelse i mag-tarmkanalen
@question: Q001
@type: text_entry
@identifier: BIOG_FYS_Q001
@title: Muskelrörelse i mag-tarmkanalen
@points: 1
@tags: #BIOG001X #matsmältning #peristaltik #Remember #Easy

---

## Question Text
@field: question_text
Den muskelrörelse som pressar maten framåt kallas {{BLANK-1}}.

## Blanks
@field: blanks
### Blank 1
@field: blank_1
**Correct Answers:**
- peristaltik
- Peristaltik

**Case Sensitive:** No

## Feedback
@field: feedback
### General Feedback
@field: general_feedback
Peristaltik är de vågrörelser...
```

**Karakteristik:**
- HAR `@field:` struktur
- Men gammal syntax:
  - `@question: Q001` istället för `^question Q001`
  - `@tags:` istället för `^labels`
  - `**Correct Answers:**` istället för `^Correct_Answers`
  - `{{BLANK-1}}` istället för `{{blank_1}}`
- Saknar `@end_field` och `@@field:`

**Transformation krävs:**
1. Regex: `@key: value` → `^key value`
2. Regex: `**Label:** value` → `^Label value`
3. Regex: `{{BLANK-N}}` → `{{blank_N}}`
4. Add `@end_field` efter varje field
5. Change nested `@field:` → `@@field:`

---

## LEVEL 4: VALID v6.5

### Exempel: BIOG001X_Fys_v65_5.md

```markdown
# Q001 Muskelrörelse i mag-tarmkanalen
^question Q001
^type text_entry
^identifier BIOG_FYS_Q001
^title Muskelrörelse i mag-tarmkanalen
^points 1
^labels #BIOG001X #matsmältning #peristaltik #Remember #Easy

@field: question_text
Den muskelrörelse som pressar maten framåt kallas {{blank_1}}.
@end_field

@field: blanks

@@field: blank_1
^Correct_Answers
- peristaltik
- Peristaltik
^Case_Sensitive No
@@end_field

@end_field

@field: feedback

@@field: general_feedback
Peristaltik är de vågrörelser...
@@end_field

...

@end_field
```

**Karakteristik:**
- Korrekt v6.5 syntax
- Passerar Step 2 validation
- Kan exporteras direkt

---

## TRANSFORMATION MATRIX

| Från Format | Till v6.5 | Verktyg | Komplexitet |
|-------------|-----------|---------|-------------|
| Level 1 (Raw) | Behöver bygga allt | qf-scaffolding | 🔴 HÖG |
| Level 2A (TRA265) | Header-parsing + restructure | qf-pipeline Step 1 | 🟠 MEDEL-HÖG |
| Level 2B (DQM) | Header-parsing + restructure | qf-pipeline Step 1 | 🟠 MEDEL-HÖG |
| Level 2C (Evolution) | Header-parsing + restructure | qf-pipeline Step 1 | 🟠 MEDEL-HÖG |
| Level 3 (v6.3) | Regex + structure | qf-pipeline Step 1 | 🟡 MEDEL |
| Level 4 (v6.5) | Ingen | - | ✅ KLAR |

---

## BESLUTSPUNKTER

### 1. Var går gränsen mellan qf-scaffolding och qf-pipeline?

**Förslag:**

```
qf-scaffolding handar:
- Level 1 (Raw) - helt ostrukturerat
- Output: Level 2 format (semi-structured)

qf-pipeline Step 1 hanterar:
- Level 2A, 2B, 2C, 3 - semi-structured till v6.3
- Output: Level 4 (valid v6.5)
```

### 2. Hur identifiera format automatiskt?

```python
def detect_format(content):
    if "^question" in content and "@field:" in content:
        return "v6.5"  # Level 4
    elif "@question:" in content and "@field:" in content:
        return "v6.3"  # Level 3
    elif "**Type**:" in content and "## Question Text" in content:
        return "semi_structured"  # Level 2
    elif "**FRÅGA:**" in content or "**RÄTT SVAR:**" in content:
        return "raw_swedish"  # Level 1
    else:
        return "unknown"
```

### 3. Ska vi prioritera?

**Förslag prioritering:**

1. **Level 3 → Level 4** (v6.3 → v6.5)
   - Mest mekanisk
   - Regex-baserad
   - Lätt att testa

2. **Level 2B/2C → Level 4** (DQM/Evolution → v6.5)
   - Header-parsing
   - Vanligt format
   - Medelstor komplexitet

3. **Level 2A → Level 4** (TRA265 → v6.5)
   - Essay-fokus
   - Rubric-hantering
   - Mer komplext

4. **Level 1 → Level 2** (Raw → Semi)
   - Kräver AI-assistans
   - Svårast att automatisera
   - qf-scaffolding

---

## NÄSTA STEG

**ALTERNATIV A: Börja med Level 3**
- Implementera v6.3 → v6.5 transformer
- Testa på BIOG001X_Fys_v63.md
- Mest mekaniskt, minst risk

**ALTERNATIV B: Börja med Level 2B**
- Implementera DQM → v6.5 transformer
- Testa på Quiz_Questions_KOMPLETT_DQM.md
- Täcker vanligt format

**ALTERNATIV C: Format-detektor först**
- Bygg auto-detect
- Sen implementera transformers per format
- Mer strukturerat tillvägagångssätt

---

*DISCOVER-fas inventering | 2026-01-07*
