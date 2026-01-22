# RFC-011: Self-Learning Transformation System

**Status:** Proposal  
**Author:** Claude + Niklas Karlsson  
**Created:** 2026-01-21  
**Depends on:** RFC-010 (QFMD Canonicalization)  
**Type:** Future Enhancement / Machine Learning

---

## Executive Summary

RFC-010 proposes step3 with **hard-coded transformation rules**. This RFC proposes making step3 **self-learning** - automatically discovering new transformation patterns from user data, validation failures, and successful exports. The system would evolve from a rule-based transformer to an **intelligent normalization engine** that improves over time.

**Core Idea:** Every time a user encounters a QFMD variant that step3 can't handle, the system should:
1. Capture the pattern
2. Learn the correct transformation
3. Add it to the transformation registry
4. Help future users automatically

**Impact:** Transform step3 from a **static tool** to a **living knowledge base** that grows smarter with every use.

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Learning Mechanisms](#learning-mechanisms)
3. [Architecture](#architecture)
4. [Implementation Approaches](#implementation-approaches)
5. [Data Collection & Privacy](#data-collection--privacy)
6. [Evaluation & Quality Control](#evaluation--quality-control)
7. [Deployment Strategy](#deployment-strategy)
8. [Long-term Vision](#long-term-vision)

---

## Problem Statement

### The Static Rule Problem

RFC-010 proposes step3 with transformation rules like:

```python
TYPE_ALIASES = {
    'multiple_choice': 'multiple_choice_single',
    'mc': 'multiple_choice_single',
    'mcq': 'multiple_choice_single',
    # ... 10 hard-coded aliases
}
```

**Problems:**

1. **Manual discovery:** Someone has to encounter `single_choice`, realize it should map to `multiple_choice_single`, and add it to the code.

2. **Slow updates:** New patterns require code changes, testing, and deployment.

3. **Coverage gaps:** Only handles patterns we've explicitly coded.

4. **Language/culture barriers:** Swedish users might write `flerval_en` (multiple choice one), English users `mc_single`, Chinese users 单选题. Hard to anticipate all variants.

5. **Evolution lag:** QFMD v7 might introduce new patterns. Rule updates lag behind usage.

### The Opportunity

QuestionForge has access to rich learning signals:

**Success signals:**
- Files that pass step2 validation
- Files that export successfully via step4
- User-approved step3 transformations

**Failure signals:**
- Validation errors from step2
- Export failures from step4
- Rejected step3 suggestions

**User corrections:**
- When user manually fixes a file after step3
- When user reverts a step3 transformation
- When user provides custom transformation rules

**Question:** Can we build a system that learns from these signals?

---

## Learning Mechanisms

### Mechanism 1: Pattern Mining from Validation Errors

**How it works:**

1. **Collect validation error patterns**
   ```
   User file: ^type: single_choice
   step2 error: Invalid question type: "single_choice"
   User fix: ^type: multiple_choice_single
   ```

2. **Extract transformation rule**
   ```python
   Rule discovered:
     pattern: "single_choice"
     replacement: "multiple_choice_single"
     context: ^type field
     confidence: 0.95 (based on frequency)
   ```

3. **Validate rule quality**
   - Test on held-out dataset
   - Check if rule breaks any existing files
   - Require minimum support (e.g., 3+ users hit this pattern)

4. **Add to transformation registry**
   ```python
   TYPE_ALIASES['single_choice'] = 'multiple_choice_single'  # Auto-learned
   ```

**Data needed:**
- Validation error logs
- User corrections (before/after)
- Timestamp and user ID (for frequency analysis)

**ML approach:** Sequence-to-sequence learning
- Input: Error message + original text
- Output: Corrected text
- Model: Fine-tuned T5 or similar

### Mechanism 2: Successful Transformation Tracking

**How it works:**

1. **Track transformation success rate**
   ```
   Transformation: multiple_choice → multiple_choice_single
   Applied: 1,247 times
   Accepted: 1,243 times (99.7%)
   Rejected: 4 times (0.3%)
   ```

2. **Identify high-confidence transformations**
   - Success rate >95% → auto-apply
   - Success rate 80-95% → suggest to user
   - Success rate <80% → requires user approval

3. **Detect failing transformations**
   - If rejection rate increases → flag for review
   - If causes downstream errors → disable temporarily

**Data needed:**
- Transformation application logs
- User acceptance/rejection (did they keep the change?)
- Post-transformation validation results

**ML approach:** Classification
- Features: transformation type, file characteristics, user history
- Target: accept/reject probability
- Model: Logistic regression or XGBoost

### Mechanism 3: LLM-Assisted Rule Generation

**How it works:**

1. **Capture novel error patterns**
   ```
   User file: @field: svar_text
   step2 error: Unknown field name
   User manually changes to: @field: question_text
   ```

2. **Ask LLM to explain transformation**
   ```
   Prompt: "The user changed '@field: svar_text' to '@field: question_text'.
           'svar' is Swedish for 'answer'. What transformation rule should we add?"
   
   LLM: "Add Swedish field name alias: svar_text → question_text"
   ```

3. **Generate candidate rule**
   ```python
   FIELD_ALIASES['svar_text'] = 'question_text'  # LLM-suggested
   ```

4. **Human review before deployment**
   - Show rule to moderators
   - Require 2+ approvals
   - Test on sample dataset

**Data needed:**
- User corrections
- Language/locale information
- Field usage statistics

**ML approach:** Few-shot learning with Claude/GPT-4
- Input: Before/after examples + context
- Output: Transformation rule in JSON
- Validation: Human-in-the-loop

### Mechanism 4: Crowdsourced Transformation Rules

**How it works:**

1. **User contributes transformation**
   ```
   User interface:
   "I often write 'mc' instead of 'multiple_choice_single'.
    Can step3 learn this?"
   
   [Submit transformation rule]
   ```

2. **Community voting**
   ```
   Transformation: mc → multiple_choice_single
   Votes: 👍 47  👎 2
   Status: Approved (95% support)
   ```

3. **Automatic integration**
   - Rules with >80% approval auto-deploy
   - Available to all users immediately
   - Can be overridden in personal config

**Data needed:**
- User-submitted rules
- Community votes
- Usage statistics (how many users benefit?)

**ML approach:** Collaborative filtering
- Similar to recommendation systems
- "Users who liked this rule also liked..."

### Mechanism 5: Active Learning Loop

**How it works:**

1. **System detects uncertainty**
   ```
   File: ^type: multiple_selection
   System: "I'm 60% confident this should be 'multiple_response'.
           User, can you confirm?"
   ```

2. **User provides label**
   ```
   User: "Yes, correct" OR "No, should be 'multiple_choice_single'"
   ```

3. **Update model**
   - Add labeled example to training set
   - Retrain model weekly
   - Improve confidence over time

**Data needed:**
- Uncertain predictions (confidence <70%)
- User labels
- Model prediction history

**ML approach:** Active learning
- Model: Probabilistic classifier
- Strategy: Uncertainty sampling
- Update: Online learning or batch retraining

---

## Architecture

### High-Level Design

```
┌───────────────────────────────────────────────────────────────┐
│                   Step 3: Self-Learning System                │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Transformation Engine                      │ │
│  │                                                         │ │
│  │  [Rule-Based]  ──┐                                     │ │
│  │  - Hard-coded    │                                     │ │
│  │  - Fast          │  ──→  [Hybrid Arbiter]  ──→ Output │ │
│  │  - Deterministic │                                     │ │
│  │                  │                                     │ │
│  │  [ML-Based]  ────┘                                     │ │
│  │  - Learned                                             │ │
│  │  - Flexible                                            │ │
│  │  - Probabilistic                                       │ │
│  └─────────────────────────────────────────────────────────┘ │
│                          ↓                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Learning System                            │ │
│  │                                                         │ │
│  │  [Data Collection] → [Pattern Mining] → [Rule Gen]    │ │
│  │         ↓                  ↓                 ↓         │ │
│  │  [Validation]      [ML Training]      [Human Review]  │ │
│  │         ↓                  ↓                 ↓         │ │
│  │  [Deployment]  ←────────────────────────────┘         │ │
│  └─────────────────────────────────────────────────────────┘ │
│                          ↓                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Knowledge Base                             │ │
│  │                                                         │ │
│  │  [Transformation Rules]  [Success Metrics]             │ │
│  │  [Pattern Library]       [User Feedback]               │ │
│  │  [ML Models]             [Version History]             │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Hybrid Transformation Engine

Combines rule-based and ML-based approaches:

```python
class HybridTransformer:
    def __init__(self):
        self.rule_engine = RuleBasedTransformer()
        self.ml_engine = MLTransformer()
        self.arbiter = TransformationArbiter()
    
    def transform(self, content: str, question_id: str, error: Error):
        # Try rule-based first (fast, deterministic)
        rule_result = self.rule_engine.apply(content, question_id, error)
        
        if rule_result.confidence > 0.95:
            return rule_result
        
        # Fall back to ML (flexible, handles novel patterns)
        ml_result = self.ml_engine.predict(content, question_id, error)
        
        # Arbitrate between rule-based and ML
        return self.arbiter.decide(rule_result, ml_result)
```

**Arbiter logic:**
- Rule confidence >95% → use rule
- ML confidence >90% → use ML
- Both low → ask user
- Disagreement → show both options

#### 2. Learning Pipeline

```python
class LearningPipeline:
    def __init__(self):
        self.collector = DataCollector()
        self.miner = PatternMiner()
        self.generator = RuleGenerator()
        self.validator = RuleValidator()
    
    def run_learning_cycle(self):
        # 1. Collect data from last week
        data = self.collector.fetch(days=7)
        
        # 2. Mine patterns
        patterns = self.miner.discover_patterns(data)
        
        # 3. Generate candidate rules
        rules = self.generator.create_rules(patterns)
        
        # 4. Validate rules
        validated = self.validator.test_rules(rules)
        
        # 5. Deploy high-confidence rules
        for rule in validated:
            if rule.confidence > 0.95:
                self.deploy(rule)
            elif rule.confidence > 0.80:
                self.queue_for_review(rule)
```

**Learning cycle frequency:**
- Pattern mining: Daily
- Rule generation: Weekly
- Model retraining: Monthly
- Human review: Continuous (queue-based)

#### 3. Knowledge Base Schema

```yaml
transformations:
  - id: "type_mc_001"
    pattern: "multiple_choice"
    replacement: "multiple_choice_single"
    context: "^type field"
    source: "hard_coded"  # or "ml_learned", "user_contributed"
    confidence: 1.0
    created_at: "2026-01-15"
    usage_count: 1247
    success_rate: 0.997
    last_used: "2026-01-21"
  
  - id: "type_mc_002"
    pattern: "single_choice"
    replacement: "multiple_choice_single"
    context: "^type field"
    source: "ml_learned"
    confidence: 0.92
    created_at: "2026-01-18"
    usage_count: 34
    success_rate: 0.941
    last_used: "2026-01-21"
    requires_approval: false  # auto-learned, high confidence

patterns:
  - id: "pattern_001"
    before: "^type: {TYPE}"
    after: "^type {TYPE}"
    description: "Remove colon after ^type"
    frequency: 89
    languages: ["sv", "en"]

ml_models:
  - id: "seq2seq_v1"
    type: "sequence-to-sequence"
    framework: "transformers"
    checkpoint: "t5-small-qfmd-finetuned"
    accuracy: 0.87
    trained_on: 12450
    last_updated: "2026-01-20"
```

---

## Implementation Approaches

### Approach A: Rule Mining Only (Recommended for MVP)

**What:** Start simple - just mine patterns from user corrections.

**How:**
1. Log every validation error + user fix
2. Weekly batch job: analyze logs, extract patterns
3. Human reviews top 10 patterns
4. Deploy as new rules

**Pros:**
- Simple to implement
- No ML infrastructure needed
- Deterministic behavior
- Easy to debug

**Cons:**
- Requires manual review
- Can't handle novel patterns
- Limited to seen examples

**Timeline:** 2 weeks

**Code Example:**

```python
# Learning pipeline (weekly cron job)

import pandas as pd
from collections import Counter

def mine_type_transformations():
    # 1. Load logs
    logs = pd.read_csv('step3_corrections.csv')
    # Columns: timestamp, user_id, original_type, corrected_type, accepted
    
    # 2. Filter to accepted corrections
    accepted = logs[logs['accepted'] == True]
    
    # 3. Count patterns
    patterns = Counter(zip(accepted['original_type'], accepted['corrected_type']))
    
    # 4. Generate candidate rules
    rules = []
    for (original, corrected), count in patterns.items():
        if count >= 3:  # Min support: 3 users
            # Calculate success rate
            total = len(logs[(logs['original_type'] == original) & 
                            (logs['corrected_type'] == corrected)])
            success_rate = count / total
            
            if success_rate > 0.8:
                rules.append({
                    'pattern': original,
                    'replacement': corrected,
                    'confidence': success_rate,
                    'support': count
                })
    
    # 5. Save for human review
    pd.DataFrame(rules).to_csv('candidate_rules.csv')
    
    return rules
```

### Approach B: LLM-Assisted Rule Generation

**What:** Use Claude/GPT-4 to explain and generate transformation rules.

**How:**
1. Detect novel error pattern (not in rule registry)
2. Call LLM with before/after example + context
3. LLM generates transformation rule in JSON
4. Human reviews and approves
5. Deploy to production

**Pros:**
- Handles novel patterns immediately
- Explains reasoning (interpretable)
- Language/culture aware
- No training data needed

**Cons:**
- API costs ($)
- Latency (seconds per call)
- Non-deterministic
- Requires human review

**Timeline:** 3 weeks

**Code Example:**

```python
import anthropic

class LLMRuleGenerator:
    def __init__(self):
        self.client = anthropic.Anthropic()
    
    def generate_rule(self, before: str, after: str, context: str) -> dict:
        prompt = f"""
You are a QFMD transformation expert. A user corrected a validation error:

BEFORE: {before}
AFTER:  {after}
CONTEXT: {context}

Analyze this correction and generate a transformation rule in JSON format:
{{
  "pattern": "regex or literal pattern to match",
  "replacement": "what to replace with",
  "context": "where this applies (field name, question type, etc)",
  "explanation": "why this transformation is correct",
  "confidence": 0.0-1.0
}}

Only output the JSON, no other text.
"""
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse JSON response
        rule = json.loads(response.content[0].text)
        rule['source'] = 'llm_generated'
        rule['requires_review'] = True
        
        return rule

# Usage
generator = LLMRuleGenerator()

# User corrected: ^type: mc → ^type: multiple_choice_single
rule = generator.generate_rule(
    before="^type: mc",
    after="^type: multiple_choice_single",
    context="Question type metadata field"
)

print(rule)
# {
#   "pattern": "^type:?\\s+mc\\s*$",
#   "replacement": "^type multiple_choice_single",
#   "context": "^type metadata field",
#   "explanation": "'mc' is common abbreviation for multiple choice single answer",
#   "confidence": 0.9,
#   "source": "llm_generated",
#   "requires_review": true
# }
```

### Approach C: Sequence-to-Sequence ML Model

**What:** Train a neural network to learn transformations directly from examples.

**How:**
1. Collect training data (10,000+ before/after pairs)
2. Fine-tune T5 or BART on transformation task
3. Input: error message + original text
4. Output: corrected text
5. Beam search to generate multiple candidates

**Pros:**
- Handles complex transformations
- Learns patterns automatically
- No manual rule writing
- Generalizes to unseen cases

**Cons:**
- Requires large training dataset
- Expensive to train
- Black box (hard to debug)
- Might introduce errors

**Timeline:** 2 months (including data collection)

**Code Example:**

```python
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch

class Seq2SeqTransformer:
    def __init__(self, model_path="t5-small-qfmd"):
        self.model = T5ForConditionalGeneration.from_pretrained(model_path)
        self.tokenizer = T5Tokenizer.from_pretrained(model_path)
    
    def transform(self, error_msg: str, original_text: str) -> List[str]:
        # Format input
        input_text = f"fix qfmd error: {error_msg} ||| {original_text}"
        
        # Tokenize
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=512,
            truncation=True
        )
        
        # Generate (beam search for multiple candidates)
        outputs = self.model.generate(
            **inputs,
            max_length=512,
            num_beams=5,
            num_return_sequences=3,
            early_stopping=True
        )
        
        # Decode candidates
        candidates = [
            self.tokenizer.decode(output, skip_special_tokens=True)
            for output in outputs
        ]
        
        return candidates

# Usage
model = Seq2SeqTransformer()

candidates = model.transform(
    error_msg='Invalid question type: "multiple_choice"',
    original_text='^type: multiple_choice'
)

print(candidates)
# [
#   '^type: multiple_choice_single',   # Top candidate
#   '^type multiple_choice_single',    # Alternative (no colon)
#   '^type: multiple_response'          # Less likely
# ]
```

### Approach D: Hybrid System (Long-term Goal)

**What:** Combine all three approaches with intelligent routing.

**Architecture:**

```python
class HybridLearningSystem:
    def __init__(self):
        self.rule_miner = RuleMiner()         # Approach A
        self.llm_generator = LLMRuleGenerator()  # Approach B
        self.ml_model = Seq2SeqTransformer()     # Approach C
    
    def learn_transformation(self, error: Error, correction: UserCorrection):
        # 1. Check if this is a known pattern
        if self.rule_miner.has_pattern(error.type):
            # Update pattern statistics
            self.rule_miner.record_correction(error, correction)
            return
        
        # 2. Novel pattern - use LLM for fast rule generation
        rule = self.llm_generator.generate_rule(
            before=error.original_text,
            after=correction.corrected_text,
            context=error.context
        )
        
        # 3. Add to pending review queue
        self.queue_for_review(rule)
        
        # 4. Periodically retrain ML model with all data
        if self.should_retrain():
            self.ml_model.retrain(self.get_all_corrections())
    
    def apply_transformation(self, error: Error):
        # 1. Try rule-based (fast, deterministic)
        rule_result = self.rule_miner.apply(error)
        if rule_result.confidence > 0.95:
            return rule_result
        
        # 2. Try ML model (flexible, generalizes)
        ml_result = self.ml_model.transform(
            error.message,
            error.original_text
        )
        if ml_result.confidence > 0.90:
            return ml_result
        
        # 3. Fall back to LLM (expensive but accurate)
        llm_result = self.llm_generator.generate_fix(error)
        
        # 4. Show user all options, let them choose
        return {
            'candidates': [rule_result, ml_result, llm_result],
            'recommendation': self.rank_candidates([rule_result, ml_result, llm_result])
        }
```

---

## Data Collection & Privacy

### What Data to Collect

**Essential (Tier 1):**
- Validation error messages
- User corrections (before/after)
- Transformation acceptance (kept or reverted?)
- Success/failure of export after transformation

**Useful (Tier 2):**
- File metadata (language, QFMD version, question count)
- User locale/language preference
- Transformation timing (how long did user take to review?)
- Error recurrence (same error in multiple files?)

**Nice-to-have (Tier 3):**
- User expertise level (inferred from error frequency)
- File topic/domain (education, corporate training, etc.)
- Question difficulty (from metadata)

**Never collect:**
- Actual question content (privacy!)
- Personal identifiable information
- Student data or test answers
- Proprietary assessment content

### Privacy-Preserving Approach

```python
class PrivacyPreservingCollector:
    def log_correction(self, error: Error, correction: UserCorrection):
        # Extract ONLY the transformation pattern
        log_entry = {
            'timestamp': datetime.now(),
            'user_id': hash(user_id),  # Anonymized
            'error_type': error.type,
            'pattern_before': self.extract_pattern(error.original_text),
            'pattern_after': self.extract_pattern(correction.corrected_text),
            'context': error.field_name,
            'accepted': True,
            # NO actual question content!
        }
        
        self.db.insert('corrections', log_entry)
    
    def extract_pattern(self, text: str) -> str:
        """Extract just the transformation pattern, not content."""
        # Example: "^type: multiple_choice" → "^type: {TYPE}"
        # Example: "A) Correct answer" → "A) {CONTENT}"
        
        # Remove actual content, keep structure
        pattern = re.sub(r'(?<=\^type:?\s+)\w+', '{TYPE}', text)
        pattern = re.sub(r'(?<=[A-Z]\)\s+).*', '{CONTENT}', pattern)
        
        return pattern
```

**Key principles:**
1. **Collect patterns, not content**
2. **Anonymize user IDs**
3. **Opt-in for data sharing**
4. **Local-first learning** (learn from user's own data first)
5. **Transparent logging** (users can view what's collected)

### User Consent

```
┌─────────────────────────────────────────────────────┐
│  QuestionForge Learning System                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Help improve QuestionForge for everyone!           │
│                                                     │
│  ☑ Share transformation patterns (anonymized)      │
│    Your corrections help step3 learn new patterns  │
│                                                     │
│  ☐ Share error statistics (aggregated)             │
│    Help us prioritize which errors to fix          │
│                                                     │
│  ☐ Join beta testing for ML features               │
│    Get early access to AI-powered transformations  │
│                                                     │
│  We NEVER collect:                                  │
│  • Your question content                            │
│  • Student data or answers                          │
│  • Personal information                             │
│                                                     │
│  [View Privacy Policy]  [Save Preferences]         │
└─────────────────────────────────────────────────────┘
```

---

## Evaluation & Quality Control

### Metrics

**Transformation Quality:**
- **Precision:** % of suggested transformations that are correct
- **Recall:** % of errors that get fixed
- **Acceptance rate:** % of suggestions user accepts
- **Reversion rate:** % of accepted suggestions later reverted

**Learning System:**
- **Pattern discovery rate:** New patterns learned per week
- **Rule coverage:** % of errors covered by learned rules
- **Model accuracy:** % of predictions that match user corrections
- **Time to deployment:** Days from pattern discovery to production

**User Experience:**
- **Time saved:** Manual editing time before/after step3
- **Error reduction:** Validation errors before/after step3
- **User satisfaction:** Survey ratings
- **Adoption rate:** % of users who enable learning features

### Quality Gates

```python
class QualityGate:
    def should_deploy_rule(self, rule: TransformationRule) -> bool:
        """Multi-stage quality check before deploying learned rule."""
        
        # Gate 1: Statistical significance
        if rule.support < 5:
            return False  # Need at least 5 occurrences
        
        # Gate 2: Success rate
        if rule.success_rate < 0.85:
            return False  # Must work 85%+ of the time
        
        # Gate 3: No conflicts
        if self.conflicts_with_existing_rule(rule):
            return False
        
        # Gate 4: Validation test
        if not self.passes_validation_tests(rule):
            return False
        
        # Gate 5: Human review (for high-impact rules)
        if rule.estimated_usage > 100:  # Will affect many users
            if not rule.human_reviewed:
                self.queue_for_review(rule)
                return False
        
        return True
    
    def passes_validation_tests(self, rule: TransformationRule) -> bool:
        """Test rule on held-out dataset."""
        test_cases = self.get_test_cases(rule.pattern)
        
        correct = 0
        for case in test_cases:
            result = rule.apply(case.original)
            if result == case.expected:
                correct += 1
        
        accuracy = correct / len(test_cases)
        return accuracy > 0.9
```

### A/B Testing

```python
class ABTest:
    def __init__(self, rule: TransformationRule):
        self.rule = rule
        self.control_group = []  # Users WITHOUT new rule
        self.treatment_group = []  # Users WITH new rule
    
    def assign_user(self, user_id: str) -> str:
        """50/50 split."""
        if hash(user_id) % 2 == 0:
            return 'control'
        else:
            return 'treatment'
    
    def evaluate(self) -> dict:
        """Compare metrics between groups."""
        return {
            'control': {
                'error_rate': self.get_error_rate(self.control_group),
                'time_to_fix': self.get_avg_time(self.control_group),
                'satisfaction': self.get_satisfaction(self.control_group),
            },
            'treatment': {
                'error_rate': self.get_error_rate(self.treatment_group),
                'time_to_fix': self.get_avg_time(self.treatment_group),
                'satisfaction': self.get_satisfaction(self.treatment_group),
            },
            'improvement': {
                'error_reduction': ...,
                'time_saved': ...,
                'p_value': ...  # Statistical significance
            }
        }
```

---

## Deployment Strategy

### Phase 1: Data Collection (Month 1)

**Goals:**
- Instrument step3 with logging
- Collect 1,000+ correction examples
- Build initial dataset

**Implementation:**
```python
# Add to step3_canonicalize

def apply_transformation(content, rule):
    result = rule.apply(content)
    
    # Log transformation
    logger.log_transformation({
        'rule_id': rule.id,
        'applied_at': datetime.now(),
        'content_hash': hash(content),  # Anonymized
    })
    
    # Show user and ask for feedback
    if ask_user_for_feedback():
        feedback = get_user_feedback()  # Accept/Reject/Edit
        logger.log_feedback({
            'rule_id': rule.id,
            'feedback': feedback,
        })
    
    return result
```

### Phase 2: Pattern Mining (Month 2)

**Goals:**
- Analyze collected data
- Discover top 20 patterns
- Deploy as new rules

**Process:**
1. Weekly batch job mines patterns
2. Human reviews top 10
3. Deploy 5 highest-confidence rules
4. Monitor impact

### Phase 3: LLM Integration (Month 3)

**Goals:**
- Add LLM-assisted rule generation
- Handle novel patterns
- Reduce manual review burden

**Implementation:**
- Call Claude API for unknown errors
- Generate candidate rules
- Queue for human approval
- Fast-track high-confidence rules

### Phase 4: ML Model (Month 4-6)

**Goals:**
- Train seq2seq model
- Achieve 90%+ accuracy
- Enable fully automated learning

**Milestones:**
- Month 4: Data preparation, model selection
- Month 5: Training, hyperparameter tuning
- Month 6: Evaluation, deployment

### Phase 5: Hybrid System (Month 7+)

**Goals:**
- Integrate all approaches
- Intelligent routing
- Self-improving system

**Features:**
- Rule-based for known patterns (fast)
- ML for frequent patterns (generalizes)
- LLM for rare patterns (flexible)
- User choice for uncertainty

---

## Long-term Vision

### Year 1: Foundation

**MVP:**
- step3 with hard-coded rules (RFC-010)
- Basic logging and data collection
- Pattern mining pipeline
- Human review dashboard

**Metrics:**
- 1,000+ transformations logged
- 50 learned patterns deployed
- 85% transformation accuracy

### Year 2: Intelligence

**Features:**
- LLM-assisted rule generation
- Automatic pattern discovery
- Community-contributed rules
- Multi-language support

**Metrics:**
- 10,000+ transformations logged
- 200+ learned patterns
- 92% transformation accuracy
- 30% reduction in manual fixes

### Year 3: Autonomy

**Features:**
- Seq2seq model for complex transformations
- Fully automated learning pipeline
- Real-time pattern deployment
- Personalized transformations (per-user learning)

**Metrics:**
- 100,000+ transformations logged
- 95% transformation accuracy
- 60% reduction in validation errors
- Zero-touch experience for common cases

### Year 5: Ecosystem

**Vision:**
- QuestionForge becomes the smartest QFMD tool
- Community drives transformation library
- ML model generalizes to OTHER document formats
- Open-source learning pipeline

**Impact:**
- Standard for intelligent document transformation
- Referenced by other education tech tools
- Research papers on self-learning systems
- Community of 10,000+ active users

---

## Open Questions

### Q1: How much data is enough?

**Options:**
- 100 examples per pattern (high bar)
- 10 examples per pattern (realistic)
- 3 examples per pattern (minimum)

**Recommendation:** Start with 3 (min viable), target 10 (production quality)

### Q2: How to handle conflicting corrections?

**Example:**
```
User A: mc → multiple_choice_single
User B: mc → multiple_response
```

**Options:**
- Majority vote
- Context-aware (use question structure)
- Ask both users to clarify
- LLM explains difference

**Recommendation:** Context-aware + majority vote

### Q3: Should users opt-in or opt-out?

**Opt-in:**
- Pro: Explicit consent
- Con: Low participation

**Opt-out:**
- Pro: High participation
- Con: Privacy concerns

**Recommendation:** Opt-in with clear benefits shown

### Q4: How to version transformation rules?

**Challenge:** Rules change over time. How to handle?

**Options:**
- Semantic versioning (v1.0, v2.0)
- Git-like branching (stable, beta, experimental)
- Time-based (2026-01, 2026-02)

**Recommendation:** Time-based with rollback capability

### Q5: Can this work for other file formats?

**Potential applications:**
- LaTeX → Markdown
- DOCX → QFMD
- HTML → QFMD
- CSV → Structured Data

**Recommendation:** Yes! Design learning system to be format-agnostic.

---

## Risks & Mitigations

### Risk 1: Poor Data Quality

**Risk:** Users make wrong corrections, system learns bad patterns.

**Mitigation:**
- Minimum support threshold (3+ users)
- Outlier detection (flag unusual patterns)
- Human review for high-impact rules
- User reputation system (trust experienced users more)

### Risk 2: Privacy Violations

**Risk:** Accidentally collect sensitive content.

**Mitigation:**
- Pattern extraction only (no content)
- Hash all user IDs
- Regular privacy audits
- User consent + transparency

### Risk 3: Model Drift

**Risk:** ML model accuracy degrades over time.

**Mitigation:**
- Continuous monitoring
- Monthly retraining
- A/B testing for new models
- Fallback to rule-based

### Risk 4: Adversarial Input

**Risk:** Malicious users submit bad transformations.

**Mitigation:**
- Human review queue
- Reputation system
- Rate limiting
- Anomaly detection

### Risk 5: Cost

**Risk:** LLM API costs explode.

**Mitigation:**
- Cache LLM responses
- Use LLM only for novel patterns
- Local model for common cases
- Cost monitoring + alerts

---

## Success Criteria

### Phase 1 (Month 1-3): Data Collection

- ✅ 1,000+ transformations logged
- ✅ Logging pipeline stable
- ✅ Privacy-preserving by design

### Phase 2 (Month 4-6): Pattern Mining

- ✅ 50+ patterns discovered
- ✅ 20+ patterns deployed
- ✅ 80% precision on test set

### Phase 3 (Month 7-12): LLM Integration

- ✅ LLM generates valid rules
- ✅ 90% acceptance rate
- ✅ Human review time <1hr/week

### Phase 4 (Year 2): ML Model

- ✅ 92% transformation accuracy
- ✅ Handles novel patterns
- ✅ 30% error reduction

### Long-term (Year 3+): Autonomy

- ✅ 95% accuracy
- ✅ Zero-touch experience
- ✅ Community of 1,000+ contributors

---

## Related RFCs

- **RFC-010:** QFMD Canonicalization (foundation for learning)
- **RFC-012:** Community Transformation Library (crowdsourcing)
- **RFC-013:** Multi-format Learning System (generalization)

---

## Conclusion

This RFC proposes transforming step3 from a static tool to a **living, learning system**. By capturing user corrections, mining patterns, and deploying learned rules, QuestionForge can:

1. **Automatically discover** new QFMD variants
2. **Continuously improve** transformation quality
3. **Scale knowledge** across the user community
4. **Reduce manual work** by 60%+

**Key Innovation:** Use validation errors AS transformation specifications. Every error message is a learning opportunity.

**Recommendation:** Implement in phases:
- Phase 1: Data collection (Month 1)
- Phase 2: Pattern mining (Month 2-3)
- Phase 3: LLM integration (Month 4-6)
- Phase 4: ML model (Year 2)

**Expected Impact:**
- 95% of errors auto-fixable (vs 0% today)
- 30-60% reduction in manual editing time
- 1,000+ community-contributed transformations

**Final Thought:** The best tools don't just work - they **learn** from their users and get better over time. This is how step3 becomes that tool.

---

**RFC Status:** Proposal → Review → Phased Implementation

**Next Steps:**
1. Approve RFC-011 concept
2. Design data collection schema
3. Implement logging in step3 (RFC-010)
4. Start Phase 1 (Month 1)

---

*"The goal is not to write perfect transformation rules. The goal is to build a system that writes them for us."*
