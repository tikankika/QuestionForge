"""
Session management for Step 1 Guided Build.
Tracks progress, changes, and allows resume.
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional


@dataclass
class Change:
    """Record of a single change made."""
    timestamp: str
    question_id: str
    field: str
    old_value: Optional[str]
    new_value: str
    change_type: str  # 'auto', 'user_input', 'batch'


@dataclass
class QuestionStatus:
    """Status of a single question."""
    question_id: str
    status: str  # 'pending', 'completed', 'skipped', 'has_warnings'
    issues_found: int = 0
    issues_fixed: int = 0
    issues_skipped: int = 0


@dataclass
class Session:
    """Step 1 session state."""
    session_id: str
    source_file: str
    working_file: str
    output_folder: str
    created_at: str
    updated_at: str

    # Progress
    total_questions: int = 0
    current_index: int = 0
    questions: List[QuestionStatus] = field(default_factory=list)

    # Changes log
    changes: List[Change] = field(default_factory=list)

    # Format info
    detected_format: str = ""  # 'v65', 'v63', 'semi', 'raw'

    def save(self, path: Path):
        """Save session to JSON file."""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: Path) -> 'Session':
        """Load session from JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Reconstruct dataclasses
        data['questions'] = [QuestionStatus(**q) for q in data['questions']]
        data['changes'] = [Change(**c) for c in data['changes']]
        return cls(**data)

    @classmethod
    def create_new(cls, source_file: str, output_folder: str) -> 'Session':
        """Create a new session."""
        now = datetime.now().isoformat()
        session_id = str(uuid.uuid4())[:8]

        # Create working file path
        source_path = Path(source_file)
        working_file = str(Path(output_folder) / f"{source_path.stem}_working.md")

        return cls(
            session_id=session_id,
            source_file=source_file,
            working_file=working_file,
            output_folder=output_folder,
            created_at=now,
            updated_at=now
        )

    def get_current_question(self) -> Optional[QuestionStatus]:
        """Get current question being processed."""
        if 0 <= self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    def add_change(self, question_id: str, field: str,
                   old_value: Optional[str], new_value: str, change_type: str):
        """Record a change."""
        self.changes.append(Change(
            timestamp=datetime.now().isoformat(),
            question_id=question_id,
            field=field,
            old_value=old_value,
            new_value=new_value,
            change_type=change_type
        ))
        self.updated_at = datetime.now().isoformat()

    def get_progress(self) -> Dict:
        """Get progress summary."""
        completed = sum(1 for q in self.questions if q.status == 'completed')
        skipped = sum(1 for q in self.questions if q.status == 'skipped')
        return {
            'total': self.total_questions,
            'current': self.current_index + 1,
            'completed': completed,
            'skipped': skipped,
            'remaining': self.total_questions - completed - skipped,
            'percent': int((completed / self.total_questions) * 100) if self.total_questions > 0 else 0
        }

    def mark_current_completed(self):
        """Mark current question as completed."""
        q = self.get_current_question()
        if q:
            q.status = 'completed'
            self.updated_at = datetime.now().isoformat()

    def mark_current_skipped(self, reason: Optional[str] = None):
        """Mark current question as skipped."""
        q = self.get_current_question()
        if q:
            q.status = 'skipped'
            if reason:
                self.add_change(q.question_id, 'skip_reason', None, reason, 'skip')
            self.updated_at = datetime.now().isoformat()
