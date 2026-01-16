# STEP 1: GUIDED BUILD - BUILD GUIDE

**START HERE** - Detta dokument är ingångspunkten för att bygga Step 1.

---

## WHAT TO BUILD

Ett Python MCP-verktyg som hjälper lärare transformera quiz-frågor från olika format till valid v6.5 markdown genom interaktiv dialog.

```
INPUT:  Markdown med frågor (varierade format)
        └── v6.3 syntax (@question:, **Correct:**)
        └── Semi-structured (## Headers, **Type**:)
        
OUTPUT: Valid v6.5 markdown (redo för export)
        └── ^metadata syntax
        └── @field: struktur
        └── @end_field markers

METHOD: Fråga-för-fråga med lärar-verifikation
        └── Detektera → Analysera → Fixa → Bekräfta
```

---

## KEY DOCUMENTS

| Document | Purpose | Location |
|----------|---------|----------|
| **BUILD_INSTRUCTIONS.md** | Full implementation spec | `docs/specs/STEP1_BUILD_INSTRUCTIONS.md` |
| **step1_guided_build_spec.md** | Workflow design | `docs/specs/step1_guided_build_spec.md` |
| **Input format inventory** | Real file examples | `docs/acdm/logs/2026-01-07_DISCOVER_input_format_inventory.md` |
| **XML templates** | Output field reference | `packages/qti-core/templates/xml/` |

---

## FILE STRUCTURE TO CREATE

```
packages/qf-pipeline/src/qf_pipeline/
├── step1/
│   ├── __init__.py
│   ├── session.py        # Session state (progress, changes)
│   ├── parser.py         # Split file into questions
│   ├── detector.py       # Detect format level
│   ├── analyzer.py       # Find issues
│   ├── transformer.py    # Apply fixes
│   └── prompts.py        # User interaction
│
└── tools/
    └── step1_tools.py    # MCP tool definitions
```

---

## BUILD ORDER

```
1. session.py      [No dependencies]
2. detector.py     [No dependencies]  
3. parser.py       [Uses detector]
4. analyzer.py     [No dependencies]
5. transformer.py  [No dependencies]
6. prompts.py      [Uses analyzer]
7. step1_tools.py  [Uses all above]
```

---

## MCP TOOLS TO IMPLEMENT

| Tool | Description |
|------|-------------|
| `step1_start` | Start session, detect format, parse questions |
| `step1_status` | Show progress |
| `step1_analyze` | Find issues in current question |
| `step1_fix_auto` | Apply automatic fixes |
| `step1_fix_manual` | Apply user-provided fix |
| `step1_next` | Move to next/prev question |
| `step1_skip` | Skip question with reason |
| `step1_finish` | Generate summary report |

---

## CORE TRANSFORMS

These regex transforms handle 80% of cases:

```python
# Metadata: @key: value → ^key value
r'^@question:\s*(.+)$' → r'^question \1'
r'^@type:\s*(.+)$' → r'^type \1'
r'^@tags:\s*(.+)$' → r'^labels \1'

# In-field: **Key:** → ^Key
r'\*\*Correct Answers?:\*\*' → '^Correct_Answers'
r'\*\*Case Sensitive:\*\*\s*(.+)' → r'^Case_Sensitive \1'

# Placeholders: {{BLANK-1}} → {{blank_1}}
r'\{\{BLANK-(\d+)\}\}' → r'{{blank_\1}}'

# Options: 1. 2. 3. → A. B. C.
(context-aware, only in options section)
```

---

## TEST DATA

Use real file for testing:
```
/Users/niklaskarlsson/Nextcloud/Courses/Biologi/BIOG001x_2025/Exams/
  MQG_folders_biog001x_autmn_2025/biog001x_fys/BIOG001X_Fys_v63.md
```

Compare output against valid v6.5:
```
/Users/niklaskarlsson/Nextcloud/Courses/Biologi/BIOG001x_2025/Exams/
  MQG_folders_biog001x_autmn_2025/biog001x_fys_105/
  BIOG001X_Fys_v65_5/02_working/BIOG001X_Fys_v65_5.md
```

---

## SUCCESS CRITERIA

1. ✅ Detects v6.3 format correctly
2. ✅ Parses questions (Q001, Q002, etc.)
3. ✅ Identifies missing/wrong fields
4. ✅ Auto-transforms syntax
5. ✅ Prompts user for missing info (Bloom, Difficulty)
6. ✅ Produces valid v6.5 that passes Step 2 validation

---

## WHAT NOT TO BUILD (Yet)

- ❌ Image/resource handling
- ❌ AI-generated feedback
- ❌ Batch apply across files
- ❌ Undo/rollback
- ❌ Semi-structured → v6.5 (complex, phase 2)

Focus on **v6.3 → v6.5** transformation first.

---

## START BUILDING

1. Read `STEP1_BUILD_INSTRUCTIONS.md` for full implementation
2. Create file structure
3. Implement `session.py` first (simplest)
4. Test each module independently
5. Integrate via `step1_tools.py`
6. Test on real file

---

*Build Guide v1.0 | 2026-01-07*
