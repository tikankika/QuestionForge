# M5 Sync Status

## Varning: Second Source of Truth

**FORMAT_REFERENCE.md är en KOPIA** av format-reglerna från parsern.

```
SOURCE OF TRUTH (primär):
  qti-core/src/parser/markdown_parser.py

SECOND SOURCE OF TRUTH (kan drifta):
  methodology/m5/FORMAT_REFERENCE.md  ← DU ÄR HÄR
```

### Vad detta betyder

- FORMAT_REFERENCE.md kan bli **outdated** om parsern uppdateras
- Om step2_validate ger fel som inte matchar FORMAT_REFERENCE → parsern har ändrats
- Vid konflikt: **parsern har alltid rätt**

---

## Senaste synkronisering

| Datum | Källa | Uppdaterat av |
|-------|-------|---------------|
| 2026-02-01 | `qti-core/tests/fixtures/v65/*.md` | Claude Code |

### Synkade frågetyper

| Typ | Synkad | Fixture-fil |
|-----|--------|-------------|
| text_entry_numeric | ✅ | `text_entry_numeric.md` |
| text_entry_math | ✅ | `text_entry_math.md` |
| multiple_choice_single | ⚠️ Baserad på kunskap | - |
| multiple_response | ⚠️ Baserad på kunskap | - |

---

## Vid valideringsfel

Om step2_validate ger fel som **inte förklaras** av FORMAT_REFERENCE.md:

1. **Kontrollera fixtures först:**
   ```
   qti-core/tests/fixtures/v65/[frågetyp].md
   ```

2. **Om fixture saknas, kolla parsern:**
   ```
   qti-core/src/parser/markdown_parser.py
   ```
   Sök efter frågetypen och läs valideringslogiken.

3. **Uppdatera FORMAT_REFERENCE.md** med ny information.

4. **Uppdatera denna fil** med nytt synkdatum.

---

## Hur synka

### Steg 1: Läs fixtures
```bash
ls qti-core/tests/fixtures/v65/
cat qti-core/tests/fixtures/v65/text_entry_numeric.md
```

### Steg 2: Jämför med FORMAT_REFERENCE.md
Leta efter skillnader i:
- Fältnamn
- Obligatoriska fält
- Syntax (^, @, @@)

### Steg 3: Uppdatera
Ändra FORMAT_REFERENCE.md så den matchar fixtures.

### Steg 4: Dokumentera
Uppdatera tabellen ovan med nytt datum.

---

## Kontaktpunkt

Om du upptäcker drift mellan FORMAT_REFERENCE.md och parsern:
- Fixa FORMAT_REFERENCE.md
- Överväg att lägga till tester för fixtures i qti-core
