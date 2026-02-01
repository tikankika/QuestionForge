# QFMD Format Reference

> **VARNING:** Detta är en "second source of truth".
> Den verkliga source of truth är `qti-core/src/parser/markdown_parser.py`.
> Se SYNC_STATUS.md för senaste synkdatum.

---

## Grundläggande struktur

```markdown
# Q001A [Titel]
^question Q001A
^type [frågetyp]
^identifier [KURSKOD]_[NNN]
^title [Titel]
^points [antal]
^labels #label1 #label2

@field: question_text
[Frågetext här]
@end_field

[Typ-specifika fält - se nedan]

@field: feedback

@@field: incorrect_feedback
[Feedback för fel svar]
@@end_field

@end_field
```

### Kritiska regler

| Regel | Rätt | Fel |
|-------|------|-----|
| Question ID | `# Q001A` (VERSAL) | `# Q001a` (gemen) |
| Metadata | `^type value` | `^type: value` (inget kolon!) |
| Fält | `@field: name` | `@field name` (kolon krävs) |
| Nästlade fält | `@@field: name` | `@field: name` (dubbel-@) |

---

## text_entry_numeric

För frågor med **numeriska svar** (heltal, decimaltal).

```markdown
# Q001A [Titel]
^question Q001A
^type text_entry_numeric
^identifier [KURSKOD]_001
^title [Titel]
^points 1
^labels #ämne #bloom_apply #difficulty_easy

@field: question_text
Beräkna $10 + 2 \cdot 5$ = {{blank_1}}
@end_field

@field: blanks

@@field: blank_1
^Correct_Answers
- 20
- 20.0
^Tolerance 0.1
^Input_type numeric
@@end_field

@end_field

@field: feedback

@@field: incorrect_feedback
Kom ihåg: multiplikation före addition.
@@end_field

@end_field
```

### Obligatoriska fält

| Fält | Beskrivning |
|------|-------------|
| `question_text` | Måste innehålla `{{blank_1}}` |
| `blanks` | Container för blank-definitioner |
| `blank_1` | Med `^Correct_Answers` lista |

### Valfria fält i blank

| Fält | Beskrivning |
|------|-------------|
| `^Tolerance` | Tolerans för numeriska svar (t.ex. `0.1`) |
| `^Input_type` | `numeric` |

---

## text_entry_math

För frågor med **matematiska uttryck** som svar (algebra, ekvationer).

```markdown
# Q001A [Titel]
^question Q001A
^type text_entry_math
^identifier [KURSKOD]_001
^title [Titel]
^points 1
^labels #ämne #bloom_apply #difficulty_medium

@field: question_text
Lös ekvationen: $2x + 6 = 16$

x = {{blank_1}}
@end_field

@field: blanks

@@field: blank_1
^Correct_Answers
- 5
- x=5
- x = 5
^Input_type math
@@end_field

@end_field

@field: feedback

@@field: incorrect_feedback
Subtrahera 6 från båda sidor, dela sedan med 2.
@@end_field

@end_field
```

### Obligatoriska fält

| Fält | Beskrivning |
|------|-------------|
| `question_text` | Måste innehålla `{{blank_1}}` |
| `blanks` | Container för blank-definitioner |
| `blank_1` | Med `^Correct_Answers` lista |

### Tips för Correct_Answers

Inkludera flera accepterade format:
```markdown
^Correct_Answers
- 14x + 2y
- 14x+2y
- 2y + 14x
- 2y+14x
```

---

## multiple_choice_single

För flervalsfrågor med **ett rätt svar**.

```markdown
# Q001A [Titel]
^question Q001A
^type multiple_choice_single
^identifier [KURSKOD]_001
^title [Titel]
^points 1
^labels #ämne #bloom_understand

@field: question_text
Vilken planet är närmast solen?
@end_field

@field: options
^Shuffle Yes
A. Venus
B. *Merkurius
C. Mars
D. Jorden
@end_field

@field: feedback

@@field: correct_feedback
Rätt! Merkurius är närmast solen.
@@end_field

@@field: incorrect_feedback
Fel. Merkurius är den planet som ligger närmast solen.
@@end_field

@end_field
```

### Obligatoriska fält

| Fält | Beskrivning |
|------|-------------|
| `question_text` | Frågetexten |
| `options` | Alternativen, markera rätt med `*` |

### Options-format

- Varje alternativ på egen rad
- Format: `A. Text` eller `A) Text`
- Markera rätt svar med `*` före texten: `B. *Rätt svar`
- `^Shuffle Yes` för att blanda alternativ

---

## multiple_response

För flervalsfrågor med **flera rätta svar**.

```markdown
# Q001A [Titel]
^question Q001A
^type multiple_response
^identifier [KURSKOD]_001
^title [Titel]
^points 2
^labels #ämne #bloom_analyze

@field: question_text
Vilka av följande är primtal? (Välj alla som stämmer)
@end_field

@field: options
^Shuffle Yes
A. *2
B. *3
C. 4
D. *5
E. 6
@end_field

@field: feedback

@@field: correct_feedback
Rätt! 2, 3 och 5 är primtal.
@@end_field

@@field: incorrect_feedback
Ett primtal är bara delbart med 1 och sig själv.
@@end_field

@end_field
```

---

## Feedback-struktur

Alla frågetyper kan ha feedback:

```markdown
@field: feedback

@@field: general_feedback
Visas alltid efter svar.
@@end_field

@@field: correct_feedback
Visas vid rätt svar.
@@end_field

@@field: incorrect_feedback
Visas vid fel svar.
@@end_field

@@field: partial_feedback
Visas vid delvis rätt (multiple_response).
@@end_field

@end_field
```

---

## Labels/Tags

Format: `#tag` (med hash)

```markdown
^labels #KURSKOD #bloom_apply #difficulty_medium #ämne
```

### Vanliga bloom-nivåer
- `#bloom_remember`
- `#bloom_understand`
- `#bloom_apply`
- `#bloom_analyze`
- `#bloom_evaluate`
- `#bloom_create`

### Vanliga difficulty
- `#difficulty_easy`
- `#difficulty_medium`
- `#difficulty_hard`

---

## Checklista före step2

- [ ] Question ID är VERSAL: `# Q001A` inte `# Q001a`
- [ ] Ingen kolon efter `^type`: `^type text_entry_numeric`
- [ ] text_entry har `{{blank_1}}` i question_text
- [ ] text_entry har `@field: blanks` med `@@field: blank_1`
- [ ] `^Correct_Answers` har minst ett svar
- [ ] Alla `@field:` har matchande `@end_field`
- [ ] Alla `@@field:` har matchande `@@end_field`
