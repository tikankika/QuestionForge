"""
Self-Learning Pattern System for Step 1.

Manages structural fix patterns that improve based on teacher decisions.
Similar to Step 3's fix_rules.json but focused on teacher-approved patterns.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any


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
