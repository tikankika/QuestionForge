# RFC-012 SUBPROCESS IMPLEMENTATION - COMPLETE

**För:** Claude Code (Windsurf)
**Från:** Claude Desktop (Claude Sonnet) + Niklas
**Datum:** 2026-01-24
**RFC:** RFC-012 Pipeline-Script Alignment
**Status:** Ready for implementation - ALL critical details included

---

## BESLUT: Subprocess approach (Option B)

Niklas har valt: **Rätt arkitektur från start**
- Implementera subprocess korrekt med alla detaljer
- Scripts = Source of Truth
- Längre implementationstid accepterad för korrekt lösning

---

## DUAL-USE: Terminal + MCP

**Scripts ändras INTE.** Båda metoder använder samma scripts:

```
┌─────────────────────────────────────────────────────────────┐
│                    SAMMA SCRIPTS                            │
│  step1_validate.py, step2_create_folder.py, ...            │
├─────────────────────────────────────────────────────────────┤
│  TERMINAL (manuellt)         │  MCP (subprocess)           │
│  ─────────────────────────   │  ────────────────────────   │
│  cd qti-core                 │  cwd=qti-core               │
│  python3 scripts/step1...    │  subprocess.run([...])      │
│                              │  + --output-dir             │
│                              │  + --quiz-dir               │
│  Output: qti-core/output/    │  Output: project/03_output/ │
└─────────────────────────────────────────────────────────────┘
```

**Workflow:**
1. ✅ Uppdatera/fixa scripts
2. ✅ Testa i terminal → fungerar
3. ✅ MCP använder samma scripts via subprocess
4. ✅ Garanterat samma resultat

---

## KRITISKA KOMPLEXITETER (MÅSTE LÖSAS)

### 🔴 Problem 1: Directory Mismatch

**Scripts default output:**
```
/Users/.../qti-core/output/quiz_name/
```

**MCP session expects:**
```
/Users/.../project_name/03_output/
```

**Lösning:**
```python
# step2_create_folder.py supports --output-dir
subprocess.run([
    'python3', 'scripts/step2_create_folder.py',
    file_path,
    '--output-dir', str(session.output_folder),  # Map to project
    '--output-name', quiz_name
])
```

---

### 🔴 Problem 2: State Synkronisering

**Scripts state:**
- `.workflow/metadata.json`
- `.workflow/resource_mapping.json`
- `.workflow/xml_files.json`
- `.workflow/package_info.json`

**MCP state:**
- `session.yaml`

**Lösning:**
Efter subprocess success, uppdatera session:
```python
# Efter step5 klar
if all_scripts_succeeded:
    # Läs package_info för att få ZIP path
    package_info = read_json(quiz_dir / '.workflow/package_info.json')
    
    session.exports.append({
        'path': package_info['package_path'],
        'timestamp': datetime.now().isoformat(),
        'question_count': len(questions)
    })
    session.save()
```

---

### 🔴 Problem 3: Argument Mapping per Script

Varje script har OLIKA requirements:

| Script | Required Args | Source |
|--------|--------------|--------|
| step1_validate.py | `<file> --verbose` | `session.working_file` |
| step2_create_folder.py | `<file> --output-dir <dir> --output-name <name>` | `session.working_file`, `session.output_folder`, quiz name |
| step3_copy_resources.py | `--markdown-file <file> --quiz-dir <dir> --verbose` | Explicit args (kan EJ auto-detect) |
| step4_generate_xml.py | `--markdown-file <file> --quiz-dir <dir> --language <lang> --verbose` | Explicit args + `arguments.get("language", "sv")` |
| step5_create_zip.py | `--quiz-dir <dir> --verbose` | Explicit args (kan EJ auto-detect) |

**VIKTIGT:** step3/4/5 auto-detect fungerar ENDAST om output är i `qti-core/output/`.
När MCP använder `--output-dir` till projektmappen MÅSTE vi skicka explicit `--quiz-dir`!

---

## IMPLEMENTATION

### File to modify
`/Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/packages/qf-pipeline/src/qf_pipeline/server.py`

---

### 1. handle_step2_validate

**Current location:** Line ~1155
**Replace:** Entire function

```python
async def handle_step2_validate(arguments: dict) -> list[types.TextContent]:
    """
    Validate markdown file using step1_validate.py subprocess.
    
    RFC-012: Run actual script instead of wrapper to guarantee consistency.
    """
    import subprocess
    from pathlib import Path
    
    session = get_current_session()
    if not session:
        return [types.TextContent(
            type="text",
            text="No active session. Run step0_start first."
        )]
    
    file_path = session.working_file
    if not file_path or not Path(file_path).exists():
        return [types.TextContent(
            type="text",
            text=f"Working file not found: {file_path}"
        )]
    
    # Path to qti-core
    qti_core_path = Path(__file__).parent.parent.parent.parent / "qti-core"
    if not qti_core_path.exists():
        return [types.TextContent(
            type="text",
            text=f"qti-core not found at: {qti_core_path}"
        )]
    
    try:
        # Run step1_validate.py
        result = subprocess.run(
            ['python3', 'scripts/step1_validate.py', str(file_path), '--verbose'],
            cwd=qti_core_path,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Parse validation status
        is_valid = (result.returncode == 0)
        
        # Update session
        # TODO: Parse question count from output
        session.update_validation(is_valid, 0)
        
        # Log action
        if session.project_path:
            log_action(
                session.project_path,
                "step2_validate",
                f"Validation: {'VALID' if is_valid else 'INVALID'}"
            )
        
        # Return output
        return [types.TextContent(type="text", text=result.stdout)]
        
    except subprocess.TimeoutExpired:
        return [types.TextContent(
            type="text",
            text="Validation timeout (>60s). File may be too large."
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Validation error: {str(e)}"
        )]
```

---

### 2. handle_step4_export

**Current location:** Line ~1223
**Replace:** Entire function

```python
async def handle_step4_export(arguments: dict) -> list[types.TextContent]:
    """
    Export to QTI package using ALL 5 scripts sequentially.
    
    RFC-012: Run actual scripts instead of wrappers to guarantee:
    1. apply_resource_mapping() is called (fixes critical bug)
    2. Consistency with manual terminal workflow
    3. Scripts = source of truth
    """
    import subprocess
    from pathlib import Path
    from datetime import datetime
    import json
    
    session = get_current_session()
    if not session:
        return [types.TextContent(
            type="text",
            text="No active session. Run step0_start first."
        )]
    
    file_path = session.working_file
    if not file_path or not Path(file_path).exists():
        return [types.TextContent(
            type="text",
            text=f"Working file not found: {file_path}"
        )]
    
    # Language
    language = arguments.get("language", "sv")
    
    # Paths
    qti_core_path = Path(__file__).parent.parent.parent.parent / "qti-core"
    if not qti_core_path.exists():
        return [types.TextContent(
            type="text",
            text=f"qti-core not found at: {qti_core_path}"
        )]
    
    # Quiz name from file
    quiz_name = Path(file_path).stem
    
    # Output directory (map to project's 03_output/)
    output_dir = Path(session.output_folder) if session.output_folder else qti_core_path / "output"

    # Quiz directory (where step2 creates the structure)
    quiz_dir = output_dir / quiz_name

    # Scripts to run sequentially
    # NOTE: step3/4/5 need explicit --quiz-dir because they can't auto-detect
    # when output is outside qti-core/output/ (which is where they look by default)
    scripts = [
        {
            'name': 'step1_validate.py',
            'args': [str(file_path), '--verbose'],
            'description': 'Validerar markdown format',
            'timeout': 60
        },
        {
            'name': 'step2_create_folder.py',
            'args': [str(file_path), '--output-dir', str(output_dir), '--output-name', quiz_name],
            'description': 'Skapar output-struktur',
            'timeout': 30
        },
        {
            'name': 'step3_copy_resources.py',
            'args': ['--markdown-file', str(file_path), '--quiz-dir', str(quiz_dir), '--verbose'],
            'description': 'Kopierar och byter namn på resurser',
            'timeout': 60
        },
        {
            'name': 'step4_generate_xml.py',
            'args': ['--markdown-file', str(file_path), '--quiz-dir', str(quiz_dir), '--language', language, '--verbose'],
            'description': 'Genererar QTI XML-filer (+ apply_resource_mapping)',
            'timeout': 120
        },
        {
            'name': 'step5_create_zip.py',
            'args': ['--quiz-dir', str(quiz_dir), '--verbose'],
            'description': 'Skapar QTI-paket (ZIP)',
            'timeout': 60
        }
    ]
    
    # Collect output
    all_output = []
    all_output.append("="*70)
    all_output.append("QTI EXPORT - SUBPROCESS APPROACH (RFC-012)")
    all_output.append("="*70)
    all_output.append(f"Source: {file_path}")
    all_output.append(f"Output: {output_dir}")
    all_output.append(f"Language: {language}")
    all_output.append("")
    
    # Run each script
    for i, script in enumerate(scripts, 1):
        all_output.append(f"\n{'='*70}")
        all_output.append(f"STEG {i}/5: {script['name']}")
        all_output.append(f"{script['description']}")
        all_output.append(f"{'='*70}\n")
        
        try:
            result = subprocess.run(
                ['python3', f"scripts/{script['name']}"] + script['args'],
                cwd=qti_core_path,
                capture_output=True,
                text=True,
                timeout=script['timeout']
            )
            
            # Append output
            all_output.append(result.stdout)
            
            # Check for errors
            if result.returncode != 0:
                all_output.append(f"\n❌ FEL i {script['name']}!")
                all_output.append(f"\nStderr:\n{result.stderr}")
                
                # Log error
                if session.project_path:
                    log_action(
                        session.project_path,
                        "step4_export",
                        f"Error in {script['name']}: exit {result.returncode}"
                    )
                
                return [types.TextContent(type="text", text="\n".join(all_output))]
            
            all_output.append(f"✓ {script['name']} slutförd!\n")
            
        except subprocess.TimeoutExpired:
            all_output.append(f"\n❌ TIMEOUT i {script['name']} (>{script['timeout']}s)!")
            return [types.TextContent(type="text", text="\n".join(all_output))]
        
        except Exception as e:
            all_output.append(f"\n❌ EXCEPTION i {script['name']}: {str(e)}")
            return [types.TextContent(type="text", text="\n".join(all_output))]
    
    # Success - update session state
    try:
        # Read package_info.json to get ZIP path
        quiz_dir = output_dir / quiz_name
        package_info_path = quiz_dir / ".workflow" / "package_info.json"
        
        if package_info_path.exists():
            with open(package_info_path) as f:
                package_info = json.load(f)
            
            zip_path = package_info.get('package_path', f'{quiz_name}.zip')
            
            # Update session
            session.exports.append({
                'path': zip_path,
                'timestamp': datetime.now().isoformat(),
                'question_count': 0  # TODO: Parse from output
            })
            session.save()
            
            # Log success
            if session.project_path:
                log_action(
                    session.project_path,
                    "step4_export",
                    f"Export complete: {zip_path}"
                )
    
    except Exception as e:
        all_output.append(f"\n⚠️  Warning: Could not update session state: {e}")
    
    # Final summary
    all_output.append("\n" + "="*70)
    all_output.append("✅ EXPORT SLUTFÖRD!")
    all_output.append("="*70)
    all_output.append(f"\nKontrollera: {output_dir}/{quiz_name}.zip")
    
    return [types.TextContent(type="text", text="\n".join(all_output))]
```

---

## TESTING CHECKLIST

### Test 1: Validation
```bash
# Via Claude Desktop
"Validate my quiz file"

# Verify:
- [ ] Same output as terminal: python3 scripts/step1_validate.py file.md
- [ ] Session state updated
- [ ] Action logged
```

### Test 2: Export without images
```bash
# Via Claude Desktop
"Export to QTI"

# Verify:
- [ ] All 5 steps run
- [ ] ZIP created in correct location
- [ ] session.yaml updated
- [ ] Can import in Inspera
```

### Test 3: Export WITH images (CRITICAL!)
```bash
# Use test file from rfc-012-image-path-verification.md
# Via Claude Desktop
"Export image_test.md to QTI"

# Verify:
- [ ] XML contains: resources/IMG_TEST_Q001_test_image.png
- [ ] NOT: test_image.png
- [ ] ZIP contains both XML and resources/
- [ ] Bilder visas i Inspera
```

### Test 4: Error handling
```bash
# Test with invalid file
# Verify:
- [ ] Error message shown
- [ ] Process stops at failing step
- [ ] stderr included in output
```

---

## SUCCESS CRITERIA

✅ step2_validate output = step1_validate.py output
✅ step4_export runs all 5 scripts sequentially
✅ Images have correct paths in XML (resources/Q001_*)
✅ Session state updated after export
✅ ZIP created in project/03_output/
✅ Error handling works (stops on first failure)
✅ Logging works for both success and failure

---

## CRITICAL NOTES

### python3 not python
```python
subprocess.run(['python3', ...])  # ✅ CORRECT
subprocess.run(['python', ...])   # ❌ FAILS (command not found)
```

### cwd is critical
```python
subprocess.run([...], cwd=qti_core_path)  # ✅ MUST be qti-core/
```

### Scripts auto-detect ONLY works in qti-core/output/
Scripts auto-find `.workflow/metadata.json` ONLY when:
- cwd = qti-core/
- Output is in qti-core/output/ (default)

**MCP uses project/03_output/ → auto-detect FAILS!**
Therefore we MUST pass explicit `--quiz-dir` to step3/4/5.

### Timeout values
- Validation: 60s
- Folder creation: 30s
- Resource copy: 60s
- XML generation: 120s (slowest)
- ZIP creation: 60s

---

## ROLLBACK PLAN

If subprocess fails:
1. Keep old functions as `handle_step4_export_legacy()`
2. Switch back by renaming
3. Document failure in RFC-012
4. Consider Option A (direct fix) instead

---

## NEXT STEPS AFTER IMPLEMENTATION

1. Test thoroughly with real projects
2. Document any edge cases found
3. Update WORKFLOW.md with subprocess approach
4. Consider Phase 2: Refactor scripts to importable functions

---

*RFC-012 Subprocess Implementation - Complete | 2026-01-24*
