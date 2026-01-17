# RFC-003: ML Training Dataset from Logs [PLACEHOLDER]

| Field | Value |
|-------|-------|
| **Status** | DRAFT - Not Started |
| **Created** | 2026-01-17 |
| **Author** | Niklas Karlsson |
| **Depends on** | RFC-001 (Unified Logging) |
| **Blocks** | None |

## Status Note

**THIS RFC IS A PLACEHOLDER**

Implementation should wait until:
1. ✅ RFC-001 logging is fully implemented (TIER 1-2)
2. ✅ M1-M4 scaffolding is operational
3. ✅ TIER 3 logging (user_decision) is specified and implemented
4. ✅ We have collected real usage data from teachers

**Estimated timeline:** Q2-Q3 2026

---

## Summary (Preliminary)

This RFC will define how to extract ML training data from logs/session.jsonl for:
1. Training AI to make better pedagogical suggestions
2. Understanding teacher decision patterns
3. Improving question generation quality
4. Automating more of the question creation workflow

---

## Scope (Preliminary)

### In Scope
- Dataset export pipeline from logs/session.jsonl
- Event types used for training (user_decision, ai_suggestion, correction_made)
- Dataset format and schema
- Privacy and GDPR compliance
- Training data versioning
- Quality metrics for dataset

### Out of Scope
- Actual ML model architecture (separate RFC/project)
- Training infrastructure
- Model deployment
- A/B testing framework

---

## Key Questions to Answer

1. **Dataset Format**
   - CSV? JSON? Parquet? TFRecord?
   - One file or sharded?
   - Versioning scheme?

2. **Events to Include**
   - Which event types are relevant?
   - user_decision - YES
   - ai_suggestion - YES
   - tool_error - Maybe (for debugging, not training)
   - Format conversion - Probably not

3. **Privacy & GDPR**
   - Can we log question text? (contains course content)
   - Can we log teacher decisions? (personal data?)
   - Anonymization strategy?
   - Consent flow?
   - Data retention policy?

4. **Features to Extract**
   - Question text (if allowed)
   - Question type
   - Bloom level (target)
   - Difficulty (target)
   - Teacher's rationale (if provided)
   - Context (module, stage, timing)

5. **Quality Control**
   - How to validate dataset quality?
   - Train/test/validation split?
   - Minimum sessions per dataset?
   - Handling outliers/errors?

---

## Preliminary Architecture (Ideas)

### Export Pipeline

```
logs/session.jsonl
    ↓
Filter (keep only ML-relevant events)
    ↓
Transform (extract features)
    ↓
Validate (check schema, quality)
    ↓
Output (ml_dataset_v1.parquet)
```

### Dataset Schema (Draft)

```python
{
    "session_id": "uuid",
    "timestamp": "ISO8601",
    "event_type": "user_decision",
    "decision_type": "bloom_level",
    
    # Features
    "question_text": "What is mitochondria?",  # If allowed
    "question_type": "multiple_choice_single",
    "context": {
        "module": "m3",
        "stage": 2,
        "previous_decisions": [...]
    },
    
    # Target
    "user_choice": "Remember",
    "options_presented": ["Remember", "Understand", "Apply"],
    "ai_suggestion": "Understand",  # If available
    "ai_confidence": 0.75,
    
    # Metadata
    "dataset_version": "1.0",
    "anonymized": true
}
```

---

## Dependencies

**Must be completed first:**
1. RFC-001 TIER 1-2 logging implemented
2. M1-M4 scaffolding operational
3. TIER 3 logging (user_decision) specified
4. Real teacher usage data collected (>100 sessions?)

**Helpful but not required:**
1. Multiple teachers using the system
2. Different course domains (biology, physics, etc)
3. Variety of question types

---

## References (To Research Later)

- [OpenAI's dataset preparation guide](https://platform.openai.com/docs/guides/fine-tuning)
- [Hugging Face datasets library](https://huggingface.co/docs/datasets/)
- GDPR compliance for educational data
- Parquet format for ML datasets
- MLOps best practices

---

## Next Steps (When Ready)

1. Collect 100+ real teacher sessions
2. Analyze logs to understand decision patterns
3. Define concrete dataset schema
4. Implement export pipeline
5. Validate dataset quality
6. Write full RFC with implementation plan

---

**DO NOT START THIS RFC YET**

Wait for:
- TIER 1-2 logging ✅
- M1-M4 operational ✅
- TIER 3 logging specified ✅
- Real usage data collected ✅

---

**Status:** PLACEHOLDER - Revisit in Q2 2026
