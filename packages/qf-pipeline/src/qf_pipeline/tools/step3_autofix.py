"""
Step 3: Auto-Fix Iteration Engine

Automatically fixes mechanical errors in MQG markdown files.
Runs validation → fix → validation loop until valid or max rounds.

Usage:
    # As MCP tool
    step3_autofix({project_path: "...", input_file: "questions/draft.md"})

    # As CLI
    python -m qf_pipeline.tools.step3_autofix input.md [--max-rounds 10]

RFC-013: Pipeline Architecture v2.1
"""

import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import validator from qti-core
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "qti-core"))
from src.parser.markdown_parser import MarkdownQuizParser


def get_timestamp() -> str:
    """Generate ISO 8601 timestamp."""
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


@dataclass
class FixRule:
    """A rule for auto-fixing a specific error type."""
    rule_id: str
    error_pattern: str  # Regex or string to match in error message
    fix_function: str   # Name of fix function
    confidence: float   # 0.0 - 1.0
    description: str
    success_count: int = 0
    applied_count: int = 0


@dataclass
class FixResult:
    """Result of applying a fix."""
    success: bool
    rule_id: str
    error_message: str
    fix_applied: str
    lines_changed: int = 0


@dataclass
class Step3Result:
    """Final result of Step 3 iteration."""
    status: str  # "valid", "needs_m5", "needs_step1", "max_rounds", "error"
    rounds: int
    fixes_applied: List[FixResult] = field(default_factory=list)
    remaining_errors: List[Dict] = field(default_factory=list)
    message: str = ""


# Built-in fix rules
DEFAULT_FIX_RULES = [
    FixRule(
        rule_id="STEP3_001",
        error_pattern="\\^type has colon",
        fix_function="fix_metadata_colon",
        confidence=0.95,
        description="Remove colon from ^type field"
    ),
    FixRule(
        rule_id="STEP3_002",
        error_pattern="\\^identifier has colon",
        fix_function="fix_metadata_colon",
        confidence=0.95,
        description="Remove colon from ^identifier field"
    ),
    FixRule(
        rule_id="STEP3_003",
        error_pattern="\\^points has colon",
        fix_function="fix_metadata_colon",
        confidence=0.95,
        description="Remove colon from ^points field"
    ),
]


class Step3AutoFix:
    """
    Auto-fix mechanical errors through iteration.

    Workflow:
    1. Validate markdown
    2. Categorize errors (mechanical vs pedagogical)
    3. If mechanical: fix 1 error → save → loop
    4. If pedagogical: return "needs M5"
    5. If valid: return "ready for Step 4"
    6. Max rounds protection
    """

    def __init__(
        self,
        content: str,
        max_rounds: int = 10,
        fix_rules: Optional[List[FixRule]] = None
    ):
        self.content = content
        self.max_rounds = max_rounds
        self.fix_rules = fix_rules or DEFAULT_FIX_RULES
        self.iteration_log: List[Dict] = []

    def run(self) -> Step3Result:
        """
        Run the auto-fix iteration loop.

        Returns:
            Step3Result with status and details
        """
        fixes_applied = []

        for round_num in range(self.max_rounds):
            # Validate current content
            validation = self._validate()

            # Check if valid
            if validation['valid']:
                return Step3Result(
                    status="valid",
                    rounds=round_num,
                    fixes_applied=fixes_applied,
                    message=f"✅ Valid after {round_num} fix(es)"
                )

            # Categorize errors
            errors = validation['errors']
            mechanical, pedagogical = self._categorize_errors(errors)

            # If only pedagogical errors remain, exit to M5
            if not mechanical and pedagogical:
                return Step3Result(
                    status="needs_m5",
                    rounds=round_num,
                    fixes_applied=fixes_applied,
                    remaining_errors=pedagogical,
                    message=f"❌ {len(pedagogical)} pedagogical error(s) - needs M5"
                )

            # If no errors but not valid (shouldn't happen)
            if not mechanical and not pedagogical:
                return Step3Result(
                    status="error",
                    rounds=round_num,
                    fixes_applied=fixes_applied,
                    message="Unexpected state: no errors but not valid"
                )

            # Pick one mechanical error to fix
            error = mechanical[0]

            # Find matching fix rule
            rule = self._match_rule(error)

            if not rule:
                # No rule for this error - skip to next or exit
                if len(mechanical) == 1:
                    return Step3Result(
                        status="needs_step1",
                        rounds=round_num,
                        fixes_applied=fixes_applied,
                        remaining_errors=mechanical,
                        message=f"❌ No fix rule for: {error.get('message', 'unknown')}"
                    )
                # Try next error
                mechanical.pop(0)
                continue

            # Apply fix
            fix_result = self._apply_fix(error, rule)

            if fix_result.success:
                fixes_applied.append(fix_result)
                self._log_iteration(round_num, error, rule, fix_result)
            else:
                # Fix failed - try next error or exit
                if len(mechanical) == 1:
                    return Step3Result(
                        status="error",
                        rounds=round_num,
                        fixes_applied=fixes_applied,
                        remaining_errors=mechanical,
                        message=f"❌ Fix failed: {fix_result.fix_applied}"
                    )

        # Max rounds reached
        final_validation = self._validate()
        return Step3Result(
            status="max_rounds",
            rounds=self.max_rounds,
            fixes_applied=fixes_applied,
            remaining_errors=final_validation.get('errors', []),
            message=f"⚠️ Max rounds ({self.max_rounds}) reached"
        )

    def _validate(self) -> Dict[str, Any]:
        """Validate current content using markdown_parser."""
        parser = MarkdownQuizParser(self.content)
        return parser.validate()

    def _categorize_errors(
        self,
        errors: List[Dict]
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Categorize errors into mechanical vs pedagogical.

        Mechanical (auto-fixable):
        - Colon in metadata fields
        - Field not at start of line

        Pedagogical (needs human):
        - Missing required fields
        - Missing content (options, blanks, etc.)
        """
        mechanical = []
        pedagogical = []

        for error in errors:
            msg = error.get('message', '').lower()

            # Mechanical errors (can auto-fix)
            if 'has colon' in msg:
                mechanical.append(error)
            elif 'not at start of line' in msg:
                mechanical.append(error)
            # Pedagogical errors (need human)
            elif 'missing' in msg:
                pedagogical.append(error)
            elif 'requires' in msg:
                pedagogical.append(error)
            else:
                # Unknown - treat as pedagogical (safer)
                pedagogical.append(error)

        return mechanical, pedagogical

    def _match_rule(self, error: Dict) -> Optional[FixRule]:
        """Find a fix rule matching this error."""
        msg = error.get('message', '')

        for rule in self.fix_rules:
            if re.search(rule.error_pattern, msg, re.IGNORECASE):
                return rule

        return None

    def _apply_fix(self, error: Dict, rule: FixRule) -> FixResult:
        """Apply a fix rule to the content."""
        fix_func = getattr(self, f'_{rule.fix_function}', None)

        if not fix_func:
            return FixResult(
                success=False,
                rule_id=rule.rule_id,
                error_message=error.get('message', ''),
                fix_applied=f"Fix function not found: {rule.fix_function}"
            )

        try:
            lines_changed = fix_func(error)
            rule.applied_count += 1
            rule.success_count += 1

            return FixResult(
                success=True,
                rule_id=rule.rule_id,
                error_message=error.get('message', ''),
                fix_applied=rule.description,
                lines_changed=lines_changed
            )
        except Exception as e:
            rule.applied_count += 1
            return FixResult(
                success=False,
                rule_id=rule.rule_id,
                error_message=error.get('message', ''),
                fix_applied=f"Error: {str(e)}"
            )

    def _fix_metadata_colon(self, error: Dict) -> int:
        """
        Fix: Remove colon from metadata field.

        ^type: value → ^type value
        ^identifier: Q001 → ^identifier Q001
        ^points: 1 → ^points 1
        """
        msg = error.get('message', '')

        # Determine which field
        if 'type' in msg.lower():
            pattern = r'(\^type):\s*'
        elif 'identifier' in msg.lower():
            pattern = r'(\^identifier):\s*'
        elif 'points' in msg.lower():
            pattern = r'(\^points):\s*'
        else:
            return 0

        # Replace in content
        new_content, count = re.subn(pattern, r'\1 ', self.content)

        if count > 0:
            self.content = new_content
            return count

        return 0

    def _log_iteration(
        self,
        round_num: int,
        error: Dict,
        rule: FixRule,
        result: FixResult
    ):
        """Log iteration for learning/debugging."""
        self.iteration_log.append({
            'timestamp': get_timestamp(),
            'round': round_num,
            'error': {
                'question_id': error.get('question_id', 'UNKNOWN'),
                'message': error.get('message', '')
            },
            'rule_id': rule.rule_id,
            'success': result.success,
            'lines_changed': result.lines_changed
        })

    def get_fixed_content(self) -> str:
        """Return the fixed content."""
        return self.content

    def get_iteration_log(self) -> List[Dict]:
        """Return the iteration log."""
        return self.iteration_log


def autofix_file(
    input_path: Path,
    output_path: Optional[Path] = None,
    max_rounds: int = 10
) -> Step3Result:
    """
    Auto-fix a markdown file.

    Args:
        input_path: Path to input markdown file
        output_path: Path to save fixed file (default: overwrite input)
        max_rounds: Maximum fix iterations

    Returns:
        Step3Result with status and details
    """
    # Read input
    content = input_path.read_text(encoding='utf-8')

    # Run auto-fix
    fixer = Step3AutoFix(content, max_rounds=max_rounds)
    result = fixer.run()

    # Save if successful
    if result.status == "valid" and result.fixes_applied:
        save_path = output_path or input_path
        save_path.write_text(fixer.get_fixed_content(), encoding='utf-8')
        result.message += f"\n📄 Saved to: {save_path}"

    return result


def autofix_content(
    content: str,
    max_rounds: int = 10
) -> Tuple[Step3Result, str]:
    """
    Auto-fix markdown content string.

    Args:
        content: Markdown content
        max_rounds: Maximum fix iterations

    Returns:
        (Step3Result, fixed_content)
    """
    fixer = Step3AutoFix(content, max_rounds=max_rounds)
    result = fixer.run()
    return result, fixer.get_fixed_content()


# CLI entry point
def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m qf_pipeline.tools.step3_autofix <input.md> [--max-rounds N]")
        sys.exit(2)

    input_path = Path(sys.argv[1])

    # Parse --max-rounds
    max_rounds = 10
    if '--max-rounds' in sys.argv:
        idx = sys.argv.index('--max-rounds')
        if idx + 1 < len(sys.argv):
            max_rounds = int(sys.argv[idx + 1])

    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(2)

    print(f"Step 3 Auto-Fix: {input_path}")
    print(f"Max rounds: {max_rounds}")
    print("=" * 60)

    result = autofix_file(input_path, max_rounds=max_rounds)

    print(f"\nStatus: {result.status}")
    print(f"Rounds: {result.rounds}")
    print(f"Fixes applied: {len(result.fixes_applied)}")

    if result.fixes_applied:
        print("\nFixes:")
        for fix in result.fixes_applied:
            print(f"  - [{fix.rule_id}] {fix.fix_applied}")

    if result.remaining_errors:
        print(f"\nRemaining errors: {len(result.remaining_errors)}")
        for err in result.remaining_errors[:5]:  # Show first 5
            print(f"  - {err.get('message', 'Unknown')}")

    print(f"\n{result.message}")

    # Exit code
    if result.status == "valid":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
