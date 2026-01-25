# RFC-013 Updates for Desktop

**Datum:** 2026-01-25
**Från:** Code session review

---

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
