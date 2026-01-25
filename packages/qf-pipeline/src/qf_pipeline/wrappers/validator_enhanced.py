"""Enhanced wrapper for validation - tests BOTH quality AND exportability.

This module addresses a critical architecture issue:
- validate_mqg_format.py checks for IDEAL format (quality)
- markdown_parser.py checks for EXPORTABLE format (actual functionality)

They use DIFFERENT parsing logic and can disagree!

Solution: step2 now tests BOTH to give accurate feedback.
"""

from .errors import ValidationError

# Import BOTH validators
from validate_mqg_format import validate_content  # Quality check
from .parser import parse_markdown  # Exportability check


def validate_markdown(content: str) -> dict:
    """Validate markdown content using BOTH quality and exportability checks.

    Args:
        content: Markdown content to validate.

    Returns:
        Dictionary with:
        {
            'valid': bool,              # True only if exportable (parser finds questions)
            'exportable': bool,         # Can step4 export this?
            'question_count': int,      # How many questions parser found
            'quality_issues': [...],    # Issues from validate_mqg_format
            'export_blocker': str|None, # Why export would fail (if any)
        }

    Raises:
        ValidationError: If validation process fails.
    """
    try:
        # 1. Quality check (validate_mqg_format)
        is_quality_valid, quality_issues = validate_content(content)
        
        # 2. Exportability check (markdown_parser)
        try:
            parser_result = parse_markdown(content)
            questions_found = len(parser_result.get('questions', []))
            exportable = questions_found > 0
            export_blocker = None if exportable else "Parser found 0 questions - export will fail!"
        except Exception as e:
            questions_found = 0
            exportable = False
            export_blocker = f"Parser failed: {str(e)}"
        
        # 3. Combine results
        result = {
            "valid": exportable,  # Overall validity = can we export?
            "exportable": exportable,
            "question_count": questions_found,
            "quality_issues": [
                {
                    "level": getattr(i, "level", "ERROR"),
                    "question_num": getattr(i, "question_num", None),
                    "question_id": getattr(i, "question_id", None),
                    "message": getattr(i, "message", str(i)),
                    "line_num": getattr(i, "line_num", None),
                }
                for i in quality_issues
            ],
            "export_blocker": export_blocker,
        }
        
        # 4. Classify quality issues based on exportability
        if exportable and len(quality_issues) > 0:
            # Questions can be exported but have quality issues
            # Downgrade ERRORs to WARNINGs if export works
            for issue in result["quality_issues"]:
                if issue["level"] == "ERROR":
                    issue["level"] = "WARNING"
                    issue["message"] += " (export will work but quality could be improved)"
        
        return result
        
    except Exception as e:
        raise ValidationError(f"Validation failed: {e}", source_error=e)


def validate_file(file_path: str) -> dict:
    """Validate a markdown file.

    Args:
        file_path: Path to the markdown file.

    Returns:
        Validation result dictionary.

    Raises:
        ValidationError: If file cannot be read or validation fails.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        result = validate_markdown(content)
        result["file_path"] = file_path
        return result
    except FileNotFoundError:
        raise ValidationError(f"File not found: {file_path}")
    except Exception as e:
        raise ValidationError(f"Failed to validate file {file_path}: {e}", source_error=e)


def get_error_count(validation_result: dict) -> dict:
    """Count issues by level from validation result.

    Args:
        validation_result: Result from validate_markdown().

    Returns:
        Dictionary with counts: {'errors': int, 'warnings': int, 'info': int}
    """
    quality_issues = validation_result.get("quality_issues", [])
    
    counts = {
        "errors": sum(1 for i in quality_issues if i.get("level") == "ERROR"),
        "warnings": sum(1 for i in quality_issues if i.get("level") == "WARNING"),
        "info": sum(1 for i in quality_issues if i.get("level") == "INFO"),
    }
    
    # Add export blocker as error if present
    if validation_result.get("export_blocker"):
        counts["errors"] += 1
    
    return counts
