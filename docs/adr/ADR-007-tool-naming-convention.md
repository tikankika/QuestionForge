# ADR-007: Tool Naming Convention for qf-pipeline

## Status
**Accepted**

## Date
2026-01-06

## Context

qf-pipeline has a pipeline structure with distinct steps (Steps 0-4). During development the question arose of how MCP tools should be named to:

1. Clarify which step the tool belongs to
2. Keep names consistent with Assessment_suite (which uses `phaseN_`)
3. Avoid confusion when more tools are added

### Reference: Assessment_suite Pattern

Assessment_suite uses `phaseN_` prefix:
```
phase4a_questions
phase4b_rubric
phase6_start
phase6_status
```

Plus cross-phase tools without prefix:
```
rubric_read
rubric_edit
```

## Decision

### Naming Convention: `stepN_verb`

All qf-pipeline tools use prefix `stepN_` where N is the step number:

```
step0_  → Session Management
step1_  → Guided Build
step2_  → Validator
step3_  → Decision
step4_  → Export
```

### Rules

1. **Prefix:** `stepN_` (step + number + underscore)
2. **Verb:** Short, descriptive (start, validate, export)
3. **Cross-step tools:** No prefix (e.g., `list_types`)
4. **Consistent with Assessment_suite:** Same pattern as `phaseN_`

## Tool Names

### Step 0: Session Management

| Tool | Function |
|------|----------|
| `step0_start` | Create new session OR load existing |
| `step0_status` | Show session status |

### Step 1: Guided Build (PLANNED)

| Tool | Function |
|------|----------|
| `step1_build` | Start/continue guided build |
| `step1_fix` | Apply fix (+ apply to similar) |
| `step1_skip` | Skip current question |
| `step1_done` | End guided build |

### Step 2: Validator

| Tool | Function |
|------|----------|
| `step2_validate` | Validate file (uses working_file if session active) |
| `step2_validate_content` | Validate markdown content directly (for snippets) |
| `step2_read` | Read working file for inspection/debugging |

### Step 3: Decision (PLANNED)

| Tool | Function |
|------|----------|
| `step3_choose` | Choose export format (QTI Questions / Question Set) |

### Step 4: Export

| Tool | Function |
|------|----------|
| `step4_export` | Export to QTI package |

### Cross-Step (Utilities)

| Tool | Function |
|------|----------|
| `list_types` | List supported question types |

## Complete Tool List

```
Step 0 (Session):
  step0_start     # New or load session
  step0_status    # Show status

Step 1 (Guided Build) - PLANNED:
  step1_build     # Start/continue
  step1_fix       # Apply fix
  step1_skip      # Skip
  step1_done      # End

Step 2 (Validator):
  step2_validate          # Validate file
  step2_validate_content  # Validate content directly
  step2_read              # Read file for debugging

Step 3 (Decision) - PLANNED:
  step3_choose    # Choose export format

Step 4 (Export):
  step4_export    # Create QTI package

Cross-Step:
  list_types      # Question types
```

**Total:** 12 tools (5 built, 6 planned, 1 utility)

## Mapping: Current → New

| Current Name | New Name | Status |
|--------------|----------|--------|
| `start_session` | `step0_start` | Built → rename |
| `get_session_status` | `step0_status` | Built → rename |
| `end_session` | *(remove)* | Unnecessary |
| `load_session` | `step0_start` | Merge |
| `validate_file` | `step2_validate` | Built → rename |
| `validate_content` | `step2_validate_content` | Built → rename (keep separate) |
| `export_questions` | `step4_export` | Built → rename |
| `parse_markdown` | *(remove)* | Internal utility, not public tool |
| `list_question_types` | `list_types` | Built → rename |

## Comparison with Assessment_suite

| Concept | Assessment_suite | qf-pipeline |
|---------|------------------|-------------|
| Prefix | `phaseN_` | `stepN_` |
| Session | `phase6_start` | `step0_start` |
| Status | `phase6_status` | `step0_status` |
| Cross-phase | `rubric_read` | `list_types` |

## Consequences

### Positive
- Consistent with Assessment_suite pattern
- Clear visual grouping
- Easy to understand pipeline order
- Scalable for new tools

### Negative
- Requires refactoring of existing code
- `stepN_` is slightly longer than `sN_`

## Alternatives Considered

### A: `sN_` (shorter)
```
s0_start, s2_validate, s4_export
```
**Rejected:** Less readable, deviates from Assessment_suite

### B: `stepN_` (chosen)
```
step0_start, step2_validate, step4_export
```
**Chosen:** Consistent with `phaseN_`, clear

## Implementation

1. ✅ Update `server.py` with new tool names
2. ✅ Merge `start_session` + `load_session` → `step0_start`
3. ✅ Keep `validate_file` → `step2_validate` and `validate_content` → `step2_validate_content` (separate)
4. ✅ Remove `end_session` and `parse_markdown` as public tools
5. Update tests

---

## ADDENDUM: Init Tool (CRITICAL)

### Background

During testing it was discovered that Claude skipped asking the user for file and folder before running `step0_start`. This is because Claude has no instructions about HOW the tools should be used.

**Solution:** Same pattern as Assessment_suite - an `init` tool that Claude MUST call first.

### New Tool: `init`

| Tool | Function |
|------|----------|
| `init` | CALL THIS FIRST! Returns critical instructions |

### Specification

```python
def init() -> dict:
    """
    CALL THIS FIRST!
    
    Returns critical instructions for using qf-pipeline.
    Claude MUST follow these instructions.
    
    Returns:
        {
            "instructions": str,       # Markdown with instructions
            "available_tools": [...],  # List of tools
            "critical_rules": [...]    # Rules that MUST be followed
        }
    """
```

### Init Instructions (returned content)

```markdown
# QF-Pipeline - Critical Instructions

## RULES (MUST BE FOLLOWED)

1. **ALWAYS ASK the user BEFORE running step0_start:**
   - "Which markdown file do you want to work with?" (source_file)
   - "Where should the project be saved?" (output_folder)
   - Wait for response before continuing!

2. **DO NOT USE bash/cat/ls** - qf-pipeline has full file access

3. **NEVER SAY "upload the file"** - MCP can read files directly

4. **FOLLOW THE PIPELINE ORDER:**
   - step0_start → step2_validate → step4_export
   - ALWAYS validate before export!

## STANDARD WORKFLOW

1. User: "Use qf-pipeline" / "Export to QTI"
2. Claude: "Which markdown file do you want to work with?"
3. User: "/path/to/file.md"
4. Claude: "Where should the project be saved? (output_folder)"
5. User: "/path/to/output/"
6. Claude: [step0_start] → Creates session
7. Claude: [step2_validate] → Validates
8. If valid: [step4_export] → Exports
   If invalid: Show errors, help user fix
```

### Tool Description (for server.py)

```python
Tool(
    name="init",
    description=(
        "CALL THIS FIRST! Returns critical instructions for using qf-pipeline. "
        "You MUST follow these instructions. "
        "ALWAYS ask user for source_file and output_folder BEFORE calling step0_start. "
        "NEVER use bash/cat/ls - MCP has full file access."
    ),
    inputSchema={
        "type": "object",
        "properties": {},
        "required": [],
    },
)
```

### Updated Tool List

```
System:
  init                    # CALL THIS FIRST!

Step 0 (Session):
  step0_start             # New or load session
  step0_status            # Show status

Step 2 (Validator):
  step2_validate          # Validate file
  step2_validate_content  # Validate content
  step2_read              # Read file for debugging

Step 4 (Export):
  step4_export            # Create QTI package

Cross-Step:
  list_types              # Question types
```

**Total:** 8 built tools (+ 6 planned for Step 1 and Step 3)

---

## Related Documents

- [ADR-006: Session Management](ADR-006-session-management.md)
- [qf-pipeline-spec.md](../specs/qf-pipeline-spec.md)
- Assessment_suite init: `/Assessment_suite/packages/assessment-mcp/src/tools/init.ts`

---

*Documented 2026-01-06 as part of ACDM IMPLEMENT phase*
*Updated 2026-01-06: Added init tool after testing*
