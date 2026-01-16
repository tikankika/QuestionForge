# KONKRET ANALYS: v6.3 vs v6.5 Format

**Datum:** 2026-01-07  
**Baserat på:** Verkliga filer från BIOG001X_Fys

---

## VERKLIGT EXEMPEL: Q001 (text_entry)

### v6.3 Format (BIOG001X_Fys_v63.md)

```markdown
# Q001 Muskelrörelse i mag-tarmkanalen
@question: Q001
@type: text_entry
@identifier: BIOG_FYS_Q001
@title: Muskelrörelse i mag-tarmkanalen
@points: 1
@tags: #BIOG001X #matsmältning #peristaltik #glatt_muskulatur #Remember #Easy

---

## Question Text
@field: question_text
Den muskelrörelse som pressar maten framåt genom mag-tarmkanalen kallas {{BLANK-1}}.

## Blanks
@field: blanks
### Blank 1
@field: blank_1
**Correct Answers:**
- peristaltik
- Peristaltik

**Case Sensitive:** No

## Scoring
@field: scoring
**Type:** ExactMatch  
**Points:** 1

## Feedback
@field: feedback
### General Feedback
@field: general_feedback
Peristaltik är de vågrörelser...
```

### v6.5 Format (BIOG001X_Fys_v65_5.md)

```markdown
# Q001 Muskelrörelse i mag-tarmkanalen
^question Q001
^type text_entry
^identifier BIOG_FYS_Q001
^title Muskelrörelse i mag-tarmkanalen
^points 1
^labels #BIOG001X #matsmältning #peristaltik #glatt_muskulatur #Remember #Easy

@field: question_text
Den muskelrörelse som pressar maten framåt genom mag-tarmkanalen kallas {{blank_1}}.
@end_field

@field: blanks

@@field: blank_1
^Correct_Answers
- peristaltik
- Peristaltik
^Case_Sensitive No
@@end_field

@end_field

@field: scoring
^Type ExactMatch
^Points 1
@end_field

@field: feedback

@@field: general_feedback
Peristaltik är de vågrörelser...
@@end_field

@@field: correct_feedback
...
@@end_field

@@field: incorrect_feedback
...
@@end_field

@@field: unanswered_feedback
...
@@end_field

@end_field
```

---

## EXAKTA SKILLNADER

### 1. Metadata-syntax

| Element | v6.3 | v6.5 |
|---------|------|------|
| Question ID | `@question: Q001` | `^question Q001` |
| Type | `@type: text_entry` | `^type text_entry` |
| Identifier | `@identifier: BIOG_FYS_Q001` | `^identifier BIOG_FYS_Q001` |
| Title | `@title: Title` | `^title Title` |
| Points | `@points: 1` | `^points 1` |
| Tags/Labels | `@tags: #tag1 #tag2` | `^labels #tag1 #tag2` |

**Skillnad:** `@key: value` → `^key value` (kolon borttagen)

### 2. Field-struktur

| Element | v6.3 | v6.5 |
|---------|------|------|
| Field start | `@field: name` | `@field: name` |
| Field end | (implicit/---) | `@end_field` |
| Subfield start | `@field: name` | `@@field: name` |
| Subfield end | (implicit) | `@@end_field` |

**Skillnad:** v6.5 kräver explicit `@end_field` och `@@` för subfields

### 3. In-field metadata

| Element | v6.3 | v6.5 |
|---------|------|------|
| Correct answers | `**Correct Answers:**` | `^Correct_Answers` |
| Case sensitive | `**Case Sensitive:** No` | `^Case_Sensitive No` |
| Type | `**Type:** ExactMatch` | `^Type ExactMatch` |

**Skillnad:** `**Label:** value` → `^Label value`

### 4. Blank placeholders

| Element | v6.3 | v6.5 |
|---------|------|------|
| Blank reference | `{{BLANK-1}}` | `{{blank_1}}` |

**Skillnad:** UPPERCASE med hyphen → lowercase med underscore

### 5. Human-readable headers

| Element | v6.3 | v6.5 |
|---------|------|------|
| Section headers | `## Question Text`, `## Blanks` | (optional, ignored) |
| Separators | `---` between questions | (not required) |

**Skillnad:** v6.5 ignorerar `##` headers (human decoration only)

---

## TRANSFORMATIONS NEEDED (v6.3 → v6.5)

### Regex-baserade transformationer:

```python
TRANSFORMS = [
    # 1. Metadata: @key: value → ^key value
    (r'^@question:\s*(.+)$', r'^question \1'),
    (r'^@type:\s*(.+)$', r'^type \1'),
    (r'^@identifier:\s*(.+)$', r'^identifier \1'),
    (r'^@title:\s*(.+)$', r'^title \1'),
    (r'^@points:\s*(.+)$', r'^points \1'),
    (r'^@tags:\s*(.+)$', r'^labels \1'),
    
    # 2. Bold labels → caret
    (r'\*\*Correct Answers:\*\*', '^Correct_Answers'),
    (r'\*\*Case Sensitive:\*\*\s*(.+)', r'^Case_Sensitive \1'),
    (r'\*\*Type:\*\*\s*(.+)', r'^Type \1'),
    (r'\*\*Points:\*\*\s*(.+)', r'^Points \1'),
    
    # 3. Blank placeholders
    (r'\{\{BLANK-(\d+)\}\}', r'{{blank_\1}}'),
    (r'\{\{DROPDOWN-(\d+)\}\}', r'{{dropdown_\1}}'),
]
```

### Strukturella transformationer:

```python
# Nested fields need @@ prefix
# @field: blank_1 inside @field: blanks → @@field: blank_1

# All fields need explicit closing
# @field: X ... → @field: X ... @end_field
```

---

## VALIDERINGS-REGLER (Step 2)

### För att passera step2_validate MÅSTE frågan ha:

**Required metadata (alla typer):**
- `^question Q###`
- `^type valid_type`
- `^identifier UNIQUE_ID`
- `^points N`
- `^labels #... #Bloom #Difficulty`

**Required fields per typ:**

| Type | Required Fields |
|------|-----------------|
| multiple_choice_single | question_text, options, answer, feedback |
| multiple_response | question_text, options, correct_answers, scoring, feedback |
| text_entry | question_text, blanks, feedback |
| inline_choice | question_text, dropdown_N, feedback |
| match | question_text, pairs, feedback |

**Required feedback subfields (auto-graded):**
- general_feedback
- correct_feedback
- incorrect_feedback
- unanswered_feedback
- (partial_feedback för partial credit)

**Required feedback subfields (manual-graded):**
- general_feedback
- answered_feedback
- unanswered_feedback

---

## VANLIGA FEL I VERKLIGA FILER

### Från v6.3-filen:

1. **Saknar `@end_field`**
   - Alla `@field:` saknar stängning
   - FIX: Lägg till `@end_field` efter varje field

2. **Fel subfield-syntax**
   - `@field: blank_1` istället för `@@field: blank_1`
   - FIX: Ändra till `@@` för nested fields

3. **Gammal metadata-syntax**
   - `@question:` istället för `^question`
   - FIX: Konvertera alla `@key:` till `^key`

4. **Bold labels istället för caret**
   - `**Correct Answers:**` istället för `^Correct_Answers`
   - FIX: Konvertera alla `**Label:**` till `^Label`

5. **Fel placeholder-format**
   - `{{BLANK-1}}` istället för `{{blank_1}}`
   - FIX: lowercase + underscore

6. **`@tags` istället för `^labels`**
   - FIX: Byt namn

### Icke-kritiska skillnader (kan ignoreras):

- `## Section Headers` (v6.5 ignorerar dessa)
- `---` separatorer (inte nödvändiga)
- Tomma rader (formatering)

---

## SLUTSATS: Kan vi använda XML-templates direkt?

**NEJ** - XML-templates är OUTPUT-format (för Inspera).

Vi behöver:
1. **INPUT-spec** = Vad måste finnas i markdown för varje frågetyp
2. **Validator** = Kolla att markdown har allt som krävs
3. **Transformer** = Konvertera gammal syntax till ny

**XML-templates visar VAD som behövs (placeholders), men:**
- Inte HUR det ska se ut i markdown
- Inte vilka VARIATIONER som är tillåtna
- Inte VAR felen brukar vara

---

## REKOMMENDATION: Förenklad Type Requirements

Skapa en fil per frågetyp med:

```yaml
# multiple_choice_single.yaml
type_name: "Multiple Choice (Single Answer)"
type_code: "multiple_choice_single"

required_metadata:
  - field: "^question"
    pattern: "Q\\d{3}"
    example: "Q001"
  - field: "^type"
    value: "multiple_choice_single"
  - field: "^identifier"
    pattern: "[A-Z_]+"
    example: "BIOG_FYS_Q001"
  - field: "^points"
    type: "integer"
  - field: "^labels"
    must_include: ["#Bloom_level", "#Difficulty"]

required_fields:
  - name: "question_text"
    content: "free_text"
  - name: "options"
    content: "A-F choices"
    min_options: 3
    max_options: 6
  - name: "answer"
    content: "single_letter"
  - name: "feedback"
    subfields:
      - "general_feedback"
      - "correct_feedback"
      - "incorrect_feedback"
      - "unanswered_feedback"

common_errors:
  - error: "Saknar ^labels"
    fix: "Lägg till: ^labels #COURSE #Topic #Bloom #Difficulty"
  - error: "Saknar answer field"
    fix: "Lägg till @field: answer\\nA\\n@end_field"
  - error: "Fel antal options"
    fix: "Behöver 3-6 options (A-F)"
```

---

## NÄSTA KONKRETA STEG

1. **Skapa type requirements** för de 5 vanligaste typerna:
   - multiple_choice_single
   - multiple_response  
   - text_entry
   - inline_choice
   - match

2. **Implementera v6.3→v6.5 transformer**
   - Regex för metadata
   - Structure för fields

3. **Testa på verkliga filer**
   - BIOG001X_Fys_v63.md → validera transformationen

---

*DISCOVER-fas konkret analys | 2026-01-07*
