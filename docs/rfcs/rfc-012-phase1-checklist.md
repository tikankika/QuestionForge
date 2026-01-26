# Phase 1 Implementation Checklist

**Status:** Ready to implement
**Estimated time:** 1 day
**Risk:** Low

---

## Prerequisites

- [ ] Verifiera att qti-core scripts fungerar i terminal
- [ ] Bekräfta path till qti-core: `/Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/packages/qti-core`
- [ ] Testa subprocess isolation lokalt

---

## Implementation Tasks

### 1. Update server.py - step2_validate (30 min)

- [ ] Lägg till subprocess import
- [ ] Implementera `handle_step2_validate()` enligt RFC-012
- [ ] Lägg till timeout (60s)
- [ ] Parse exit code för validation status
- [ ] Update session state
- [ ] Logga action

**Test:**
```python
# Kör step2_validate på test file
# Verifiera output matchar manual run
```

---

### 2. Update server.py - step4_export (60 min)

- [ ] Implementera `handle_step4_export()` enligt RFC-012
- [ ] Definiera alla 5 scripts i array
- [ ] Loop genom scripts med subprocess
- [ ] Samla all output
- [ ] Error handling för varje steg
- [ ] Timeout (120s per script)
- [ ] Logga framgång/fel

**Test:**
```python
# Kör step4_export på test file med bilder
# Verifiera alla 5 steg körs
# Kontrollera att ZIP innehåller bilder med korrekta paths
```

---

### 3. Testing (2-3 timmar)

#### Test 1: Validation
```bash
# Terminal
cd /path/to/qti-core
python scripts/step1_validate.py test.md > manual.txt

# Desktop - kör step2_validate
# Spara output till desktop.txt

# Jämför
diff manual.txt desktop.txt
```

#### Test 2: Full Export
```bash
# Terminal - kör alla scripts manuellt
cd /path/to/qti-core
python scripts/step1_validate.py test.md
python scripts/step2_create_folder.py test.md
python scripts/step3_copy_resources.py
python scripts/step4_generate_xml.py
python scripts/step5_create_zip.py

# Desktop - kör step4_export
# Jämför ZIPs
```

#### Test 3: Bildhantering (KRITISK!)
```bash
# Test med quiz som har bilder
# Verifiera att XML innehåller: resources/Q001_image.png
# INTE: image.png
```

---

### 4. Documentation (30 min)

- [ ] Uppdatera WORKFLOW.md med subprocess approach
- [ ] Lägg till exempel på hur man kör via Desktop
- [ ] Dokumentera directory structure
- [ ] Notera att Phase 2 kommer senare

---

## Success Criteria

✅ step2_validate ger samma output som step1_validate.py
✅ step4_export kör alla 5 steg utan fel
✅ Bilder har korrekta paths i XML (`resources/Q001_image.png`)
✅ ZIP kan importeras i Inspera utan fel
✅ Output i Desktop matchar Terminal output

---

## Rollback Plan

Om subprocess inte fungerar:
1. Kommentera ut ny kod
2. Återställ till gamla wrappers
3. Dokumentera vad som gick fel
4. Omvärdera approach

---

## Next Steps (Phase 2)

Efter Phase 1 lyckad:
- Skapa RFC för script refactoring
- Planera migration från subprocess → import
- Definiera testplan för Phase 2

---

*Implementation Checklist | Phase 1 Subprocess | 2026-01-22*
