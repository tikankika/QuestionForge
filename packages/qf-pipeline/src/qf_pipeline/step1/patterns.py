"""
Self-Learning Pattern System for Step 1.

Manages structural fix patterns that improve based on teacher decisions.
Similar to Step 3's fix_rules.json but focused on teacher-approved patterns.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple


def get_timestamp() -> str:
    """Get current timestamp in ISO format with Z suffix."""
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


@dataclass
class Pattern:
    """A structural fix pattern learned from teacher decisions."""

    pattern_id: str                    # "STEP1_001"
    issue_type: str                    # "missing_separator_after"
    description: str                   # Human-readable description
    fix_suggestion: str                # What to suggest to teacher
    confidence: float = 0.9            # 0.0 - 0.99
    teacher_accepted: int = 0          # Count of accept_ai decisions
    teacher_modified: int = 0          # Count of modify decisions
    teacher_manual: int = 0            # Count of manual decisions
    learned_from: int = 0              # Total decisions
    created_at: str = field(default_factory=get_timestamp)
    last_used: str = ""

    def update_stats(self, decision: str) -> None:
        """
        Update pattern statistics based on teacher decision.

        Args:
            decision: "accept_ai", "modify", "manual", "skip", "delete"
        """
        self.learned_from += 1
        self.last_used = get_timestamp()

        if decision == "accept_ai":
            self.teacher_accepted += 1
        elif decision == "modify":
            self.teacher_modified += 1
        elif decision == "manual":
            self.teacher_manual += 1
        # skip and delete don't update acceptance stats

        # Recalculate confidence after 5+ decisions
        if self.learned_from >= 5:
            self._recalculate_confidence()

    def _recalculate_confidence(self) -> None:
        """
        Recalculate confidence based on teacher decisions.

        Weighting:
        - accept_ai: 1.0 (full confidence)
        - modify: 0.5 (partial confidence - suggestion was useful)
        - manual: 0.1 (low confidence - teacher had different idea)
        """
        if self.learned_from == 0:
            return

        weighted_score = (
            self.teacher_accepted * 1.0 +
            self.teacher_modified * 0.5 +
            self.teacher_manual * 0.1
        )
        max_possible = self.learned_from * 1.0

        self.confidence = min(0.99, weighted_score / max_possible)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pattern':
        """Create Pattern from dictionary."""
        return cls(**data)


# Default patterns for common structural issues
DEFAULT_PATTERNS: List[Pattern] = [
    Pattern(
        pattern_id="STEP1_001",
        issue_type="missing_separator_after",
        description="Saknar separator (---) efter fråga",
        fix_suggestion="Lägg till '---' efter @end_field",
        confidence=0.9
    ),
    Pattern(
        pattern_id="STEP1_002",
        issue_type="missing_separator_before",
        description="Saknar separator (---) före fråga",
        fix_suggestion="Lägg till '---' före # Q-header",
        confidence=0.9
    ),
    Pattern(
        pattern_id="STEP1_003",
        issue_type="metadata_colon",
        description="Metadata har kolon (^type: istället för ^type)",
        fix_suggestion="Ta bort kolon från metadata-fält",
        confidence=0.95
    ),
    Pattern(
        pattern_id="STEP1_004",
        issue_type="unclosed_field_block",
        description="Fält saknar @end_field",
        fix_suggestion="Lägg till @end_field efter fältinnehåll",
        confidence=0.85
    ),
    Pattern(
        pattern_id="STEP1_005",
        issue_type="malformed_field_start",
        description="Felaktigt @field: syntax",
        fix_suggestion="Korrigera till @field: [fältnamn]",
        confidence=0.8
    ),
    Pattern(
        pattern_id="STEP1_006",
        issue_type="legacy_at_syntax",
        description="Gammal @-syntax istället för ^-syntax",
        fix_suggestion="Konvertera @type: till ^type",
        confidence=0.95
    ),
]


def load_patterns(project_path: Optional[Path]) -> List[Pattern]:
    """
    Load patterns from project's logs/step1_patterns.json.

    Falls back to DEFAULT_PATTERNS if file doesn't exist.

    Args:
        project_path: Path to project directory

    Returns:
        List of Pattern objects
    """
    if not project_path:
        return [Pattern(**asdict(p)) for p in DEFAULT_PATTERNS]

    patterns_file = Path(project_path) / "logs" / "step1_patterns.json"

    if not patterns_file.exists():
        # Initialize with default patterns
        save_patterns(project_path, DEFAULT_PATTERNS)
        return [Pattern(**asdict(p)) for p in DEFAULT_PATTERNS]

    try:
        with open(patterns_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        patterns = []
        for pattern_data in data.get('patterns', []):
            patterns.append(Pattern.from_dict(pattern_data))

        return patterns if patterns else [Pattern(**asdict(p)) for p in DEFAULT_PATTERNS]

    except Exception as e:
        print(f"Warning: Could not load patterns: {e}")
        return [Pattern(**asdict(p)) for p in DEFAULT_PATTERNS]


def save_patterns(project_path: Path, patterns: List[Pattern]) -> None:
    """
    Save patterns to project's logs/step1_patterns.json.

    Args:
        project_path: Path to project directory
        patterns: List of Pattern objects to save
    """
    logs_dir = Path(project_path) / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    patterns_file = logs_dir / "step1_patterns.json"

    # Calculate metadata
    avg_confidence = sum(p.confidence for p in patterns) / len(patterns) if patterns else 0

    data = {
        "version": "1.0",
        "updated_at": get_timestamp(),
        "metadata": {
            "total_patterns": len(patterns),
            "avg_confidence": round(avg_confidence, 3)
        },
        "patterns": [p.to_dict() for p in patterns]
    }

    with open(patterns_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def find_pattern_for_issue(patterns: List[Pattern], issue_type: str) -> Optional[Pattern]:
    """
    Find the best pattern for an issue type.

    Args:
        patterns: List of available patterns
        issue_type: The type of issue to match

    Returns:
        Best matching Pattern, or None
    """
    matching = [p for p in patterns if p.issue_type == issue_type]

    if not matching:
        return None

    # Return highest confidence pattern
    return max(matching, key=lambda p: p.confidence)


def get_pattern_by_id(patterns: List[Pattern], pattern_id: str) -> Optional[Pattern]:
    """Get pattern by its ID."""
    for p in patterns:
        if p.pattern_id == pattern_id:
            return p
    return None


def generate_pattern_id(patterns: List[Pattern]) -> str:
    """
    Generate a unique pattern ID.

    Format: STEP1_NNN where NNN is sequential.
    """
    existing_nums = []
    for p in patterns:
        if p.pattern_id.startswith("STEP1_"):
            try:
                num = int(p.pattern_id.replace("STEP1_", ""))
                existing_nums.append(num)
            except ValueError:
                pass

    next_num = max(existing_nums, default=0) + 1
    return f"STEP1_{next_num:03d}"


def create_pattern_from_error(
    patterns: List[Pattern],
    error_message: str,
    error_field: Optional[str] = None,
    question_type: Optional[str] = None,
    teacher_fix: Optional[str] = None
) -> Pattern:
    """
    Create a new pattern from a validation error.

    This is the core of the self-learning system:
    1. Parser gives error message
    2. We create a tentative pattern with low confidence
    3. Teacher provides fix → pattern is saved
    4. Next time same error → pattern is suggested
    5. Teacher accepts → confidence increases

    Args:
        patterns: Existing patterns (to generate unique ID)
        error_message: Error from markdown_parser validation
        error_field: Field that caused error (e.g., "answer", "correct_answers")
        question_type: Type of question (e.g., "multiple_response")
        teacher_fix: Optional fix provided by teacher (for learning)

    Returns:
        New Pattern with low initial confidence
    """
    # Generate unique ID
    pattern_id = generate_pattern_id(patterns)

    # Derive issue_type from error message
    issue_type = _derive_issue_type(error_message, error_field, question_type)

    # Create description in Swedish
    description = _create_description(error_message, question_type)

    # Create fix suggestion (will be refined by teacher)
    fix_suggestion = _create_fix_suggestion(error_message, error_field, question_type)

    # New patterns start with low confidence until teacher confirms
    initial_confidence = 0.3

    return Pattern(
        pattern_id=pattern_id,
        issue_type=issue_type,
        description=description,
        fix_suggestion=fix_suggestion,
        confidence=initial_confidence,
        teacher_accepted=0,
        teacher_modified=0,
        teacher_manual=0,
        learned_from=0
    )


def _derive_issue_type(error_message: str, error_field: Optional[str], question_type: Optional[str]) -> str:
    """
    Derive a canonical issue_type from error message.

    This creates a key for pattern matching. Examples:
    - "multiple_response question requires correct answers" → "mr_requires_correct_answers"
    - "true_false question requires answer" → "tf_requires_answer"
    """
    msg_lower = error_message.lower()

    # Type-specific issues
    if question_type:
        type_prefix = {
            "multiple_response": "mr",
            "multiple_choice_single": "mc",
            "true_false": "tf",
            "inline_choice": "ic",
            "text_entry": "te",
            "match": "match",
        }.get(question_type, question_type[:3])
    else:
        type_prefix = "generic"

    # Extract key action from error message
    if "requires" in msg_lower:
        if error_field:
            return f"{type_prefix}_requires_{error_field}"
        elif "correct answers" in msg_lower:
            return f"{type_prefix}_requires_correct_answers"
        elif "answer" in msg_lower:
            return f"{type_prefix}_requires_answer"
        elif "options" in msg_lower:
            return f"{type_prefix}_requires_options"
        else:
            return f"{type_prefix}_requires_unknown"

    elif "missing" in msg_lower:
        if error_field:
            return f"{type_prefix}_missing_{error_field}"
        else:
            return f"{type_prefix}_missing_field"

    elif "invalid" in msg_lower:
        if error_field:
            return f"{type_prefix}_invalid_{error_field}"
        else:
            return f"{type_prefix}_invalid_format"

    # Fallback: use sanitized error message
    sanitized = msg_lower.replace(" ", "_")[:40]
    return f"{type_prefix}_{sanitized}"


def _create_description(error_message: str, question_type: Optional[str]) -> str:
    """Create Swedish description from error message."""
    msg_lower = error_message.lower()

    # Type names in Swedish
    type_sv = {
        "multiple_response": "flervalsfråga",
        "multiple_choice_single": "envalsfråga",
        "true_false": "sant/falskt-fråga",
        "inline_choice": "dropdown-fråga",
        "text_entry": "textinmatningsfråga",
        "match": "matchningsfråga",
    }.get(question_type, "fråga")

    if "requires correct answers" in msg_lower:
        return f"En {type_sv} kräver correct_answers (plural), inte answer"
    elif "requires answer" in msg_lower:
        return f"En {type_sv} saknar svarsfält"
    elif "requires options" in msg_lower:
        return f"En {type_sv} saknar svarsalternativ"
    else:
        return f"Valideringsfel: {error_message}"


def _create_fix_suggestion(error_message: str, error_field: Optional[str], question_type: Optional[str]) -> str:
    """Create fix suggestion based on error."""
    msg_lower = error_message.lower()

    if question_type == "multiple_response" and "correct answers" in msg_lower:
        return "Byt @field: answer till @field: correct_answers för multiple_response"

    elif "requires answer" in msg_lower:
        return "Lägg till @field: answer med korrekt svar"

    elif "requires options" in msg_lower:
        return "Lägg till @field: options med svarsalternativ"

    elif "requires correct answers" in msg_lower:
        return "Lägg till @field: correct_answers med korrekta svar (kommaseparerade)"

    else:
        return f"Fixa: {error_message}"


def find_or_create_pattern(
    patterns: List[Pattern],
    error_message: str,
    error_field: Optional[str] = None,
    question_type: Optional[str] = None
) -> Tuple[Pattern, bool]:
    """
    Find existing pattern or create new one.

    Args:
        patterns: List of existing patterns
        error_message: Error from validation
        error_field: Field that caused error
        question_type: Question type

    Returns:
        Tuple of (pattern, is_new) where is_new=True if pattern was created
    """
    # Derive what the issue_type would be
    issue_type = _derive_issue_type(error_message, error_field, question_type)

    # Try to find existing pattern
    existing = find_pattern_for_issue(patterns, issue_type)
    if existing:
        return existing, False

    # Create new pattern
    new_pattern = create_pattern_from_error(
        patterns=patterns,
        error_message=error_message,
        error_field=error_field,
        question_type=question_type
    )

    return new_pattern, True


def update_pattern_from_teacher_fix(
    pattern: Pattern,
    teacher_action: str,
    teacher_fix: Optional[str] = None,
    teacher_note: Optional[str] = None
) -> None:
    """
    Update pattern based on teacher's fix.

    This is how patterns learn:
    - accept_ai: AI suggestion was correct → confidence increases
    - modify: AI was close but teacher tweaked → moderate increase
    - manual: Teacher had different idea → low increase

    Args:
        pattern: Pattern to update
        teacher_action: "accept_ai", "modify", "manual", "skip"
        teacher_fix: The actual fix content (for learning)
        teacher_note: Teacher's reasoning
    """
    pattern.update_stats(teacher_action)

    # If teacher provided a better fix suggestion, update it (for modify/manual)
    if teacher_action in ["modify", "manual"] and teacher_note:
        # Could update fix_suggestion based on teacher's note
        # For now, just let confidence handle it
        pass
