# IMPLEMENTATION HANDOFF: RFC-012 Phase 1C - Subprocess Testing

**För:** Claude Code (Windsurf)  
**Från:** Claude Desktop (Claude Sonnet)  
**Datum:** 2026-01-22  
**RFC:** RFC-012 Pipeline-Script Alignment  
**Phase:** 1C - Testing subprocess approach  
**Status:** Ready for implementation

---

## CONTEXT

RFC-012 beslutade om **Hybrid Approach**:
- **Phase 1 (NU):** Pipeline kör scripts via subprocess
- **Phase 2 (SENARE):** Refactor scripts till importerbara funktioner

Detta handoff omfattar: **STEG C - Testa subprocess approach**

**Relaterad dokumentation:**
- `/docs/rfcs/rfc-012-pipeline-script-alignment.md`
- `/docs/rfcs/rfc-012-phase1-checklist.md`
- `/WORKFLOW.md` (Appendix A)

---

## SCOPE

### I Scope
✅ Skapa test-script för subprocess integration  
✅ Verifiera att subprocess.run() fungerar med qti-core scripts  
✅ Testa exit codes, output capture, error handling  
✅ Dokumentera resultat

### Out of Scope
❌ Implementation i server.py (det är Phase 1D)  
❌ Refactoring av scripts (det är Phase 2)  
❌ Produktionskod (endast test)

---

## IMPLEMENTATION

### Step 1: Hitta eller skapa test data

**Check om test data finns:**
```bash
find /Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/packages/qti-core -name "*.md" -type f | head -5
```

**Om ingen lämplig fil finns, skapa:**

**Fil:** `/Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/packages/qti-core/tests/test_data/sample_subprocess_test.md`

```markdown
# Q001 Test fråga för subprocess
^type multiple_choice_single
^identifier SUBPROCESS_TEST_Q001
^points 1

@field: question_text
Vad är 2 + 2?
@end_field

@field: options
A. 3
B. 4*
C. 5
D. 6
@end_field

@field: answer
B
@end_field

@field: feedback
@@field: correct_feedback
Korrekt! 2 + 2 = 4
@@end_field

@@field: incorrect_feedback
Fel svar. Rätt svar är 4.
@@end_field
@end_field
```

---

### Step 2: Skapa test-script

**Fil:** `/Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/tests/test_subprocess_integration.py`

```python
#!/usr/bin/env python3
"""
RFC-012 Phase 1C: Subprocess Integration Test

Verifierar att subprocess.run() fungerar för att köra qti-core scripts.
Detta är förberedelse för Phase 1D implementation i server.py.
"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
QTI_CORE_PATH = PROJECT_ROOT / "packages" / "qti-core"
TEST_DATA_PATH = QTI_CORE_PATH / "tests" / "test_data" / "sample_subprocess_test.md"

# Results for summary
test_results = []

def log_test(name: str, passed: bool, details: str = ""):
    """Log test result."""
    test_results.append((name, passed, details))
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"   {details}")

def test_1_validate_subprocess():
    """Test 1: Kan vi köra step1_validate.py via subprocess?"""
    print("\n" + "="*70)
    print("TEST 1: step1_validate.py via subprocess")
    print("="*70)
    
    try:
        result = subprocess.run(
            ['python', 'scripts/step1_validate.py', str(TEST_DATA_PATH), '--verbose'],
            cwd=QTI_CORE_PATH,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(f"\nExit code: {result.returncode}")
        print(f"Stdout length: {len(result.stdout)} chars")
        print(f"\nFirst 300 chars of output:")
        print(result.stdout[:300])
        
        if result.stderr:
            print(f"\nStderr: {result.stderr[:200]}")
        
        # Success if exit code is 0 (valid) or 1 (invalid but script ran)
        success = result.returncode in [0, 1]
        
        if success:
            log_test("Subprocess execution", True, f"Exit code: {result.returncode}")
        else:
            log_test("Subprocess execution", False, f"Unexpected exit code: {result.returncode}")
        
        return success
        
    except subprocess.TimeoutExpired:
        log_test("Subprocess execution", False, "Timeout after 60s")
        return False
    except Exception as e:
        log_test("Subprocess execution", False, f"Exception: {e}")
        return False

def test_2_capture_output():
    """Test 2: Kan vi fånga och läsa output?"""
    print("\n" + "="*70)
    print("TEST 2: Output capture och parsing")
    print("="*70)
    
    try:
        result = subprocess.run(
            ['python', 'scripts/step1_validate.py', str(TEST_DATA_PATH)],
            cwd=QTI_CORE_PATH,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = result.stdout
        
        # Kan vi extrahera information?
        has_output = len(output) > 0
        is_text = isinstance(output, str)
        exit_code_valid = result.returncode in [0, 1]
        
        print(f"Has output: {has_output}")
        print(f"Is text: {is_text}")
        print(f"Exit code valid: {exit_code_valid}")
        print(f"Output sample:\n{output[:200]}")
        
        success = has_output and is_text and exit_code_valid
        
        if success:
            log_test("Output capture", True, f"Captured {len(output)} chars")
        else:
            log_test("Output capture", False, "Could not capture valid output")
        
        return success
        
    except Exception as e:
        log_test("Output capture", False, f"Exception: {e}")
        return False

def test_3_error_handling():
    """Test 3: Fungerar error handling med felaktig fil?"""
    print("\n" + "="*70)
    print("TEST 3: Error handling med felaktig fil")
    print("="*70)
    
    fake_file = QTI_CORE_PATH / "nonexistent_file.md"
    
    try:
        result = subprocess.run(
            ['python', 'scripts/step1_validate.py', str(fake_file)],
            cwd=QTI_CORE_PATH,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Förväntar oss non-zero exit code
        failed_correctly = result.returncode != 0
        has_error_output = len(result.stderr) > 0 or "error" in result.stdout.lower()
        
        print(f"Exit code: {result.returncode} (should be non-zero)")
        print(f"Has error output: {has_error_output}")
        
        if result.stderr:
            print(f"Stderr sample:\n{result.stderr[:200]}")
        
        success = failed_correctly
        
        if success:
            log_test("Error handling", True, f"Script failed correctly (exit {result.returncode})")
        else:
            log_test("Error handling", False, "Script did not fail for bad input")
        
        return success
        
    except Exception as e:
        log_test("Error handling", False, f"Exception: {e}")
        return False

def test_4_sequential_execution():
    """Test 4: Kan vi köra flera scripts i följd?"""
    print("\n" + "="*70)
    print("TEST 4: Sequential script execution")
    print("="*70)
    
    # Simulera step4_export som kör flera scripts
    scripts = [
        ('step1_validate.py', [str(TEST_DATA_PATH), '--verbose'], "Validation"),
        # Lägg till fler när de fungerar
    ]
    
    all_success = True
    
    for script_name, args, description in scripts:
        print(f"\n--- {description} ({script_name}) ---")
        
        try:
            result = subprocess.run(
                ['python', f'scripts/{script_name}'] + args,
                cwd=QTI_CORE_PATH,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            script_success = result.returncode in [0, 1]  # 0=valid, 1=invalid
            
            if script_success:
                print(f"✅ {description} OK (exit {result.returncode})")
            else:
                print(f"❌ {description} FAILED (exit {result.returncode})")
                print(f"Stderr: {result.stderr[:200]}")
                all_success = False
                
        except Exception as e:
            print(f"❌ {description} EXCEPTION: {e}")
            all_success = False
    
    if all_success:
        log_test("Sequential execution", True, f"All {len(scripts)} scripts ran")
    else:
        log_test("Sequential execution", False, "Some scripts failed")
    
    return all_success

def main():
    """Run all tests."""
    print("="*70)
    print("RFC-012 PHASE 1C: SUBPROCESS INTEGRATION TESTS")
    print("="*70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"QTI Core Path: {QTI_CORE_PATH}")
    print(f"Test Data: {TEST_DATA_PATH}")
    print("="*70)
    
    # Pre-flight checks
    if not QTI_CORE_PATH.exists():
        print(f"\n❌ ERROR: QTI Core path not found: {QTI_CORE_PATH}")
        return 1
    
    if not TEST_DATA_PATH.exists():
        print(f"\n⚠️  WARNING: Test data not found: {TEST_DATA_PATH}")
        print("You may need to create it first (see handoff instructions)")
        # Continue anyway to test with existing files
    
    # Run tests
    test_1_validate_subprocess()
    test_2_capture_output()
    test_3_error_handling()
    test_4_sequential_execution()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for name, passed, details in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if details:
            print(f"        {details}")
    
    all_passed = all(r[1] for r in test_results)
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED - Subprocess approach is viable!")
        print("Next step: Implement Phase 1D (server.py integration)")
    else:
        print("❌ SOME TESTS FAILED - Review errors before proceeding")
        print("Fix issues before implementing Phase 1D")
    print("="*70)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
```

---

### Step 3: Run tests

```bash
cd /Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge
python tests/test_subprocess_integration.py
```

---

### Step 4: Document results

**Fil:** `/Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/docs/rfcs/rfc-012-subprocess-test-results.md`

```markdown
# RFC-012 Phase 1C: Subprocess Test Results

**Datum:** [FYLL I]  
**Testad av:** Claude Code  
**Status:** [PASS/FAIL]

## Test Environment

- OS: macOS
- Python: [version]
- QTI Core Path: `/Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/packages/qti-core`

## Test Results

### Test 1: Subprocess Execution
Status: [✅ PASS / ❌ FAIL]
Details: [Fyll i]

### Test 2: Output Capture
Status: [✅ PASS / ❌ FAIL]
Details: [Fyll i]

### Test 3: Error Handling
Status: [✅ PASS / ❌ FAIL]
Details: [Fyll i]

### Test 4: Sequential Execution
Status: [✅ PASS / ❌ FAIL]
Details: [Fyll i]

## Example Output

```
[Inkludera faktisk test output här]
```

## Issues Found

[Lista eventuella problem]

## Recommendations

[Rekommendationer för Phase 1D]

## Conclusion

[✅ Ready for Phase 1D / ❌ Need fixes first]
```

---

## SUCCESS CRITERIA

✅ **Test script created** - File exists and is executable  
✅ **Subprocess works** - Can execute step1_validate.py  
✅ **Output captured** - stdout/stderr readable  
✅ **Exit codes correct** - 0 for success, non-zero for errors  
✅ **Error handling** - Graceful failure for bad input  
✅ **Results documented** - RFC-012-subprocess-test-results.md created

---

## TROUBLESHOOTING

### "python: command not found"
```bash
# Try python3
python3 tests/test_subprocess_integration.py
```

### "No such file or directory: scripts/..."
```bash
# Verify cwd is correct
ls /Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/packages/qti-core/scripts/
```

### "Test data not found"
```bash
# Create test data directory
mkdir -p /Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/packages/qti-core/tests/test_data

# Create sample file (see Step 1)
```

---

## NEXT STEPS

After successful testing:

1. ✅ Phase 1C complete (subprocess testing)
2. → Phase 1D: Implement subprocess in server.py
   - Update `handle_step2_validate()`
   - Update `handle_step4_export()`
   - Test with real projects
3. → Phase 1E: Integration testing
4. → Phase 2: Refactor to importable functions (later)

---

## NOTES

- This is TEST code only, not production
- Purpose: Verify subprocess approach before implementing in server.py
- If tests fail, re-evaluate approach before Phase 1D
- Keep test script for regression testing

---

*RFC-012 Phase 1C Handoff | 2026-01-22*
