# LOGGING IMPLEMENTATION: TIER 1-2

**Datum:** 2026-01-17  
**Scope:** Tool logging (debugging) + Session resumption  
**Defer:** TIER 3 (user_decision) - utreds efter M1-M4 körts

---

## TIER 1: Tool Logging (Debugging)

### Events to Implement

| Event | When | Required Data | Optional Data |
|-------|------|--------------|---------------|
| `tool_start` | Tool execution begins | `tool`, `session_id` | `arguments` |
| `tool_end` | Tool execution completes | `tool`, `success` | `duration_ms`, `result_summary` |
| `tool_error` | Error occurs | `tool`, `error_type`, `message`, `stacktrace` | `context` |

### Implementation Locations

**File:** `packages/qf-pipeline/src/qf_pipeline/step*/`

Add to:
1. `step0_start()` - session creation
2. `step1_analyze()` - question analysis
3. `step1_fix_auto()` - automatic fixes
4. `step1_fix_manual()` - manual fixes
5. `step2_validate()` - validation
6. `step4_export()` - QTI export

### Pattern (Python)

```python
def step2_validate(file_path: str):
    """Validate markdown file."""
    session = SessionManager.load_from_path(project_path)
    
    # Log start
    log_event(
        project_path=session.project_path,
        session_id=session.session_id,
        tool="step2_validate",
        event="tool_start",
        level="info",
        data={"file": file_path}
    )
    
    start_time = time.time()
    
    try:
        # Do work
        result = validate(file_path)
        
        # Log success
        duration_ms = int((time.time() - start_time) * 1000)
        log_event(
            project_path=session.project_path,
            session_id=session.session_id,
            tool="step2_validate",
            event="tool_end",
            level="info",
            data={
                "success": True,
                "valid": result.valid,
                "question_count": result.question_count
            },
            duration_ms=duration_ms
        )
        
        return result
        
    except Exception as e:
        # Log error with full context
        log_event(
            project_path=session.project_path,
            session_id=session.session_id,
            tool="step2_validate",
            event="tool_error",
            level="error",
            data={
                "error_type": type(e).__name__,
                "message": str(e),
                "stacktrace": traceback.format_exc(),
                "context": {
                    "file": file_path,
                    "exists": Path(file_path).exists()
                }
            }
        )
        raise
```

### Pattern (TypeScript - qf-scaffolding)

```typescript
async function loadStage(module: string, stage: number) {
  const startTime = Date.now();
  
  // Log start
  logEvent(
    projectPath,
    sessionId,
    'load_stage',
    'tool_start',
    'info',
    { module, stage }
  );
  
  try {
    // Load stage content
    const content = await readStageFile(module, stage);
    
    // Log end
    logEvent(
      projectPath,
      sessionId,
      'load_stage',
      'tool_end',
      'info',
      { 
        module, 
        stage,
        success: true 
      },
      Date.now() - startTime
    );
    
    return content;
    
  } catch (error) {
    // Log error
    logEvent(
      projectPath,
      sessionId,
      'load_stage',
      'tool_error',
      'error',
      {
        module,
        stage,
        error_type: error.constructor.name,
        message: error.message,
        stack: error.stack
      }
    );
    throw error;
  }
}
```

---

## TIER 2: Session Resumption

### Events to Implement

| Event | When | Required Data |
|-------|------|--------------|
| `session_start` | New session created | `entry_point`, `source_file` |
| `session_resume` | Existing session loaded | `last_activity` |
| `session_end` | Session completed | `summary` |
| `stage_start` | M1-M4 stage begins | `module`, `stage` |
| `stage_complete` | Stage approved by teacher | `module`, `stage`, `outputs` |
| `validation_complete` | Validation finished | `valid`, `question_count` |
| `export_complete` | Export finished | `output_file`, `question_count` |

### Implementation Locations

**session_start:**
- `SessionManager.create_session()` (already logs session_created, add session_start)

**stage_start / stage_complete:**
- `qf-scaffolding/load_stage.ts` (TypeScript)

**validation_complete:**
- `step2_validate()` after validation succeeds

**export_complete:**
- `step4_export()` after QTI package created

### Example: session_start

```python
# In SessionManager.create_session()
# After session created:

log_event(
    project_path=project_path,
    session_id=session_id,
    tool="step0_start",
    event="session_start",
    level="info",
    data={
        "entry_point": entry_point,
        "source_file": str(source_path) if source_path else None,
        "materials_folder": str(materials_folder) if materials_folder else None
    }
)
```

### Example: stage_complete

```typescript
// In qf-scaffolding load_stage.ts
// After teacher approves stage:

logEvent(
  projectPath,
  sessionId,
  'load_stage',
  'stage_complete',
  'info',
  {
    module: module,
    stage: stage,
    outputs: {
      // Module-specific outputs
      // e.g., for M1 Stage 5: objectives_file
    }
  }
);

// Update session.yaml methodology section
updateSessionYaml(projectPath, {
  methodology: {
    [module]: {
      status: 'in_progress',
      loaded_stages: [...existingStages, stage]
    }
  }
});
```

### Example: validation_complete

```python
# In step2_validate()
# After validation succeeds:

log_event(
    project_path=session.project_path,
    session_id=session.session_id,
    tool="step2_validate",
    event="validation_complete",
    level="info",
    data={
        "valid": result.valid,
        "question_count": result.question_count,
        "errors": len(result.errors),
        "warnings": len(result.warnings)
    }
)

# Also update session.yaml
session.update_validation(
    is_valid=result.valid,
    question_count=result.question_count
)
```

### Example: export_complete

```python
# In step4_export()
# After QTI package created:

log_event(
    project_path=session.project_path,
    session_id=session.session_id,
    tool="step4_export",
    event="export_complete",
    level="info",
    data={
        "output_file": str(output_file),
        "question_count": len(questions),
        "format": "QTI 1.2"
    }
)

# Also update session.yaml
session.log_export(
    output_file=str(output_file.relative_to(session.project_path)),
    questions_exported=len(questions)
)
```

---

## TIER 3: DEFERRED

**user_decision events are NOT implemented yet.**

**Reason:** We need to run M1-M4 first to understand:
- What decisions teachers make
- What context is needed
- What options are presented
- How to structure the data

**Next step:** After M1-M4 implementation, create spec for user_decision logging.

---

## Implementation Checklist

### Python (qf-pipeline)

- [x] `step0_start()` - session_start event (was already implemented in session_manager.py)
- [x] `step1_analyze()` - tool_start/end/error
- [x] `step1_fix_auto()` - tool_start/end/error
- [x] `step1_fix_manual()` - tool_start/end/error
- [x] `step2_validate()` - tool_start/end/error + validation_complete
- [x] `step4_export()` - tool_start/end/error + export_complete
- [x] All errors include stacktrace + context

### TypeScript (qf-scaffolding)

- [x] `load_stage()` - tool_start/end/error
- [x] `load_stage()` - stage_start when stage begins
- [x] `completeStage()` - stage_complete when teacher approves (new exported function)
- [x] All errors include stack trace

### Testing

- [ ] Create test session
- [ ] Run step2_validate → check logs/session.jsonl
- [ ] Trigger error → check error logged with stacktrace
- [ ] Run M1 Stage 0 → check stage_start logged
- [ ] Complete M1 Stage 0 → check stage_complete logged
- [ ] Read logs with `get_session_state()` → verify resumption works

---

## Files to Modify

### Python
```
packages/qf-pipeline/src/qf_pipeline/
├── step0/
│   └── tools.py          # session_start
├── step1/
│   ├── analyzer.py       # tool logging
│   ├── fixer.py          # tool logging
│   └── tools.py          # tool logging
├── step2/
│   └── tools.py          # validation_complete
└── step4/
    └── tools.py          # export_complete
```

### TypeScript
```
packages/qf-scaffolding/src/
└── tools/
    └── load_stage.ts     # stage_start, stage_complete, tool logging
```

---

## Expected Log Output

After implementation, logs/session.jsonl should contain:

```jsonl
{"ts":"2026-01-17T10:00:00Z","v":1,"session_id":"abc-123","mcp":"qf-pipeline","tool":"step0_start","event":"session_start","level":"info","data":{"entry_point":"m1"}}
{"ts":"2026-01-17T10:01:00Z","v":1,"session_id":"abc-123","mcp":"qf-scaffolding","tool":"load_stage","event":"stage_start","level":"info","data":{"module":"m1","stage":0}}
{"ts":"2026-01-17T10:02:00Z","v":1,"session_id":"abc-123","mcp":"qf-scaffolding","tool":"load_stage","event":"tool_start","level":"info","data":{"module":"m1","stage":0}}
{"ts":"2026-01-17T10:02:30Z","v":1,"session_id":"abc-123","mcp":"qf-scaffolding","tool":"load_stage","event":"tool_end","level":"info","data":{"module":"m1","stage":0,"success":true},"duration_ms":500}
{"ts":"2026-01-17T10:05:00Z","v":1,"session_id":"abc-123","mcp":"qf-scaffolding","tool":"load_stage","event":"stage_complete","level":"info","data":{"module":"m1","stage":0,"outputs":{}}}
```

---

## Success Criteria

1. ✅ Every tool call logs tool_start and tool_end
2. ✅ Every error logs tool_error with stacktrace
3. ✅ Session creation logs session_start
4. ✅ Stage completion logs stage_complete
5. ✅ Validation logs validation_complete
6. ✅ Export logs export_complete
7. ✅ `get_session_state()` can determine last completed stage
8. ✅ No crashes due to missing project_path or session_id

---

**Ready for implementation handoff to Code.**
