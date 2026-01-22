# RFC-009: M3 Conversation Capture for Question Generation

| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Created** | 2026-01-21 |
| **Author** | Niklas Karlsson |
| **Relates to** | qf-scaffolding, RFC-004 (M1 tools), RFC-007 (LLM workflow patterns) |

## Summary

M3 (Question Generation) requires a different saving pattern than M1/M2. While M1/M2 produce complete "stage documents" that can be frozen and saved with `write_m1_stage`, M3 is an **iterative conversation** where questions are proposed, reviewed, revised, and approved one at a time.

This RFC proposes tools and patterns for capturing M3's conversational workflow.

## Problem Statement

### M1/M2 Pattern (Works with `write_m1_stage`)

```
Claude analyzes → Presents findings → Teacher approves → Save complete stage
```

Each stage produces a **complete document** that can be saved atomically:
- `m1_stage0_materials.md` - All material analyses
- `m1_stage1_validation.md` - Validated priorities
- etc.

### M3 Pattern (Needs Something Different)

```
Claude proposes Q01-Q04 → Teacher: "Q1 inte bra! 2-4 ok" →
Claude revises Q01 → Teacher: "bra" →
Claude proposes Q05-Q08 → Teacher feedback →
... repeat for 40 questions ...
```

M3 characteristics:
1. **Iterative**: Questions generated in batches (4-8 at a time)
2. **Dialog-driven**: Teacher feedback shapes each batch
3. **Accumulating**: Approved questions added to running document
4. **Revision history matters**: Understanding WHY a question was changed is pedagogically valuable

### The Gap

`write_m1_stage` writes a **complete stage** at once. M3 needs:
- **Incremental accumulation** of approved questions
- **Conversation capture** for pedagogical traceability
- **Progress tracking** across potentially multiple sessions

## Proposed Solution

### Option A: `append_m3_question` Tool (Recommended)

Add approved questions one at a time to a running document.

```typescript
const appendM3QuestionSchema = z.object({
  project_path: z.string(),
  question_id: z.string(),        // "Q01", "Q02", etc.
  content: z.string(),            // Complete question in markdown
  status: z.enum(["approved", "needs_revision"]),
  revision_note: z.string().optional(), // Why it was revised
});
```

**Output file:** `03_questions/m3_generated_questions.md`

**Behavior:**
- Appends new questions to existing file
- Updates progress tracker in YAML frontmatter
- Marks revision history if question was previously saved

### Option B: `save_m3_batch` Tool

Save multiple questions at once (after a batch is approved).

```typescript
const saveM3BatchSchema = z.object({
  project_path: z.string(),
  batch_name: z.string(),         // "tier1_q01-q08"
  questions: z.array(z.object({
    id: z.string(),
    content: z.string(),
    status: z.enum(["approved", "needs_revision"]),
  })),
});
```

### Option C: `save_conversation_segment` Tool

Save conversation chunks for full traceability.

```typescript
const saveConversationSchema = z.object({
  project_path: z.string(),
  segment_name: z.string(),       // "m3_tier1_questions"
  conversation_markdown: z.string(), // Full dialogue as markdown
});
```

**Output file:** `03_questions/conversation/m3_tier1_questions.md`

## Recommendation

**Implement Option A first**, with Option C as future enhancement.

Rationale:
- Option A provides the core functionality (accumulating approved questions)
- Option A is simpler to implement and use
- Option C adds pedagogical value but isn't blocking for M3 workflow
- Can add Option C later for teachers who want full traceability

## Implementation Plan

### Phase 1: Core M3 Tool (Priority)

1. Create `append_m3_question.ts`
2. Create `03_questions/` folder structure
3. Track progress in `m3_progress.yaml`
4. Update `load_stage` with M3 tool hints

### Phase 2: Conversation Capture (Future)

1. Create `save_conversation_segment.ts`
2. Define conversation export format
3. Add option to export full M3 dialogue

## File Structure

```
project/
├── 03_questions/
│   ├── m3_generated_questions.md    # Running question accumulator
│   ├── m3_progress.yaml             # Progress tracking
│   └── conversation/                # (Phase 2)
│       ├── m3_tier1_dialogue.md
│       ├── m3_tier2_dialogue.md
│       └── m3_tier3_dialogue.md
```

## M3 Progress YAML Schema

```yaml
version: "1.0"
created: "2026-01-21T10:00:00Z"
updated: "2026-01-21T14:30:00Z"
status: "in_progress"  # not_started | in_progress | complete

tiers:
  tier1:
    total: 20
    approved: 12
    needs_revision: 2
    pending: 6
  tier2:
    total: 12
    approved: 0
    pending: 12
  tier3:
    total: 8
    approved: 0
    pending: 8

questions:
  Q01: { status: approved, saved_at: "2026-01-21T10:15:00Z" }
  Q02: { status: approved, saved_at: "2026-01-21T10:15:00Z" }
  Q03: { status: needs_revision, note: "Distraktorer för svaga" }
  # ...
```

## Comparison with M1/M2

| Aspect | M1/M2 | M3 |
|--------|-------|-----|
| Output | Complete stage documents | Accumulated questions |
| Saving | Atomic (whole stage) | Incremental (per question/batch) |
| Progress | Stage 0-5 complete/pending | Question count + status |
| Conversation | Not critical | Pedagogically valuable |
| Tool | `write_m1_stage` | `append_m3_question` |

## Open Questions

1. **Should M2 use the same tool as M1?**
   - Likely yes - M2 produces assessment blueprint in stages

2. **How to handle question revisions?**
   - Overwrite with revision note, or keep history?

3. **Export format for conversation?**
   - Plain markdown, or structured JSON?

## Related Documents

- RFC-004: M1 Methodology Tools
- RFC-007: LLM Workflow Control Patterns
- `write_m1_stage.ts`: Reference implementation for stage-based saving

---

*RFC-009 - M3 Conversation Capture*
