# Phase 1 Implementation Checklist

**Status:** Ready to implement
**Estimated time:** 1 day
**Risk:** Low

---

## Prerequisites

- [ ] Verify that qti-core scripts work in terminal
- [ ] Confirm path to qti-core: `./packages/qti-core`
- [ ] Test subprocess isolation locally

---

## Implementation Tasks

### 1. Update server.py - step2_validate (30 min)

- [ ] Add subprocess import
- [ ] Implement `handle_step2_validate()` per RFC-012
- [ ] Add timeout (60s)
- [ ] Parse exit code for validation status
- [ ] Update session state
- [ ] Log action

**Test:**
```python
# Run step2_validate on test file
# Verify output matches manual run
```

---

### 2. Update server.py - step4_export (60 min)

- [ ] Implement `handle_step4_export()` per RFC-012
- [ ] Define all 5 scripts in array
- [ ] Loop through scripts with subprocess
- [ ] Collect all output
- [ ] Error handling for each step
- [ ] Timeout (120s per script)
- [ ] Log success/failure

**Test:**
```python
# Run step4_export on test file with images
# Verify all 5 steps run
# Check that ZIP contains images with correct paths
```

---

### 3. Testing (2-3 hours)

#### Test 1: Validation
```bash
# Terminal
cd /path/to/qti-core
python scripts/step1_validate.py test.md > manual.txt

# Desktop - run step2_validate
# Save output to desktop.txt

# Compare
diff manual.txt desktop.txt
```

#### Test 2: Full Export
```bash
# Terminal - run all scripts manually
cd /path/to/qti-core
python scripts/step1_validate.py test.md
python scripts/step2_create_folder.py test.md
python scripts/step3_copy_resources.py
python scripts/step4_generate_xml.py
python scripts/step5_create_zip.py

# Desktop - run step4_export
# Compare ZIPs
```

#### Test 3: Image Handling (CRITICAL!)
```bash
# Test with quiz that has images
# Verify that XML contains: resources/Q001_image.png
# NOT: image.png
```

---

### 4. Documentation (30 min)

- [ ] Update WORKFLOW.md with subprocess approach
- [ ] Add examples of how to run via Desktop
- [ ] Document directory structure
- [ ] Note that Phase 2 comes later

---

## Success Criteria

✅ step2_validate gives same output as step1_validate.py
✅ step4_export runs all 5 steps without errors
✅ Images have correct paths in XML (`resources/Q001_image.png`)
✅ ZIP can be imported in Inspera without errors
✅ Output in Desktop matches Terminal output

---

## Rollback Plan

If subprocess doesn't work:
1. Comment out new code
2. Restore to old wrappers
3. Document what went wrong
4. Re-evaluate approach

---

## Next Steps (Phase 2)

After Phase 1 succeeds:
- Create RFC for script refactoring
- Plan migration from subprocess → import
- Define test plan for Phase 2

---

*Implementation Checklist | Phase 1 Subprocess | 2026-01-22*
