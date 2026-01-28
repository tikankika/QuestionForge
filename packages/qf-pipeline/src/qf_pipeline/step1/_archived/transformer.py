"""
Apply transformations to fix issues.
Convert Legacy Syntax to QFMD (QuestionForge Markdown) format.
"""

import re
from typing import Tuple, List, Dict, Callable


class Transformer:
    """Registry of all transforms."""

    def __init__(self):
        self._transforms: Dict[str, Callable] = {}
        self._register_all()

    def _register_all(self):
        """Register all transform functions."""
        self._transforms = {
            # Legacy syntax transforms
            'metadata_syntax': self._transform_metadata_syntax,
            'placeholder_syntax': self._transform_placeholder_syntax,
            'upgrade_headers': self._transform_upgrade_headers,
            'add_end_fields': self._transform_add_end_fields,
            'nested_field_syntax': self._transform_nested_fields,
            # Format normalization transforms
            'normalize_type_names': self._transform_normalize_type_names,
            'extract_correct_answers': self._transform_extract_correct_answers,
            'restructure_text_entry': self._transform_restructure_text_entry,
        }

    def apply(self, transform_id: str, content: str) -> Tuple[str, bool, str]:
        """
        Apply a transform.

        Returns:
            (transformed_content, success, description)
        """
        if transform_id not in self._transforms:
            return content, False, f"Unknown transform: {transform_id}"

        try:
            result, description = self._transforms[transform_id](content)
            return result, True, description
        except Exception as e:
            return content, False, f"Transform failed: {str(e)}"

    def apply_all_auto(self, content: str) -> Tuple[str, List[str]]:
        """
        Apply all auto-fixable transforms in the correct order.

        Returns:
            (transformed_content, list_of_descriptions)
        """
        changes = []

        # Order matters - do metadata first, then type normalization, then structure
        transform_order = [
            # 1. Legacy syntax conversions
            'metadata_syntax',
            'placeholder_syntax',
            'upgrade_headers',
            # 2. Type and format normalization
            'normalize_type_names',
            'extract_correct_answers',
            'restructure_text_entry',
            # 3. Structure fixes (last)
            'nested_field_syntax',
            'add_end_fields',
        ]

        for transform_id in transform_order:
            new_content, success, description = self.apply(transform_id, content)
            if success and new_content != content:
                content = new_content
                changes.append(description)

        return content, changes

    # ════════════════════════════════════════════════════════════════
    # TRANSFORM IMPLEMENTATIONS
    # ════════════════════════════════════════════════════════════════

    def _transform_metadata_syntax(self, content: str) -> Tuple[str, str]:
        """Transform @key: value → ^key value (Legacy → QFMD)"""
        transforms = [
            (r'^@question:\s*(.+)$', r'^question \1'),
            (r'^@type:\s*(.+)$', r'^type \1'),
            (r'^@identifier:\s*(.+)$', r'^identifier \1'),
            (r'^@title:\s*(.+)$', r'^title \1'),
            (r'^@points:\s*(.+)$', r'^points \1'),
            (r'^@tags:\s*(.+)$', r'^tags \1'),
            (r'^@labels:\s*(.+)$', r'^tags \1'),  # @labels: → ^tags
            (r'^@shuffle:\s*(.+)$', r'^shuffle \1'),
            (r'^@language:\s*(.+)$', r'^language \1'),
        ]

        original = content
        for pattern, replacement in transforms:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        # Remove the --- separator after metadata block (Legacy style)
        # Look for pattern: ^tags line followed by --- on its own line
        content = re.sub(r'(\^tags\s+.+)\n+---\n+', r'\1\n\n', content)
        content = re.sub(r'(\^points\s+.+)\n+---\n+', r'\1\n\n', content)

        if content != original:
            return content, "Konverterade metadata-syntax (@key: → ^key)"
        return content, ""

    def _transform_placeholder_syntax(self, content: str) -> Tuple[str, str]:
        """Transform {{BLANK-1}} → {{blank_1}} and {{DROPDOWN-1}} → {{dropdown_1}}"""
        transforms = [
            (r'\{\{BLANK-(\d+)\}\}', r'{{blank_\1}}'),
            (r'\{\{BLANK(\d+)\}\}', r'{{blank_\1}}'),
            (r'\{\{DROPDOWN-(\d+)\}\}', r'{{dropdown_\1}}'),
            (r'\{\{DROPDOWN(\d+)\}\}', r'{{dropdown_\1}}'),
        ]

        original = content
        for pattern, replacement in transforms:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

        if content != original:
            return content, "Konverterade placeholder-syntax ({{BLANK-1}} → {{blank_1}})"
        return content, ""

    def _transform_upgrade_headers(self, content: str) -> Tuple[str, str]:
        """Transform ## headers → ### headers for field sections (Legacy → QFMD)"""

        # Map of field section headers that should be upgraded
        field_headers = [
            'Question Text',
            'Options',
            'Answer',
            'Feedback',
            'Blanks',
            'Scoring',
            'Pairs',
            'Dropdowns',
        ]

        # Map of subfield headers that should be upgraded from ### to ####
        subfield_headers = [
            'General Feedback',
            'Correct Response Feedback',
            'Correct Feedback',
            'Incorrect Response Feedback',
            'Incorrect Feedback',
            'Unanswered Feedback',
            'Partially Correct Response Feedback',
            'Partial Feedback',
            'Blank 1', 'Blank 2', 'Blank 3', 'Blank 4', 'Blank 5',
            'Dropdown 1', 'Dropdown 2', 'Dropdown 3', 'Dropdown 4', 'Dropdown 5',
            'Pair 1', 'Pair 2', 'Pair 3', 'Pair 4', 'Pair 5',
        ]

        original = content

        # First upgrade ## → ### for main field headers
        for header in field_headers:
            pattern = f'^##\\s+{re.escape(header)}\\s*$'
            replacement = f'### {header}'
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.IGNORECASE)

        # Then upgrade ### → #### for subfield headers
        for header in subfield_headers:
            pattern = f'^###\\s+{re.escape(header)}\\s*$'
            replacement = f'#### {header}'
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.IGNORECASE)

        if content != original:
            return content, "Uppgraderade headers (## → ###, ### → ####)"
        return content, ""

    def _transform_nested_fields(self, content: str) -> Tuple[str, str]:
        """Transform nested @field: to @@field: for subfields (Legacy → QFMD)"""

        # In Legacy Syntax, nested fields use @field:
        # In QFMD, nested fields use @@field:
        #
        # Pattern: After a subfield header (#### Header), @field: should become @@field:
        # Example:
        #   #### Blank 1
        #   @field: blank_1  →  @@field: blank_1

        original = content
        lines = content.split('\n')
        result = []
        in_main_field = False
        main_field_name = None

        for i, line in enumerate(lines):
            # Track main field blocks
            if line.strip().startswith('@field:') and not line.strip().startswith('@@field:'):
                field_match = re.match(r'@field:\s*(\w+)', line)
                if field_match:
                    field_name = field_match.group(1)
                    # These are top-level fields
                    if field_name in ['question_text', 'options', 'answer', 'feedback',
                                      'blanks', 'scoring', 'pairs', 'dropdowns']:
                        in_main_field = True
                        main_field_name = field_name
                        result.append(line)
                        continue
                    # These are nested fields within feedback, blanks, etc.
                    elif in_main_field and main_field_name in ['feedback', 'blanks', 'dropdowns', 'pairs']:
                        # Check if previous non-empty line is a subheader (####)
                        prev_lines = [l for l in lines[max(0, i-3):i] if l.strip()]
                        if prev_lines and prev_lines[-1].strip().startswith('####'):
                            # This should be a @@field:
                            line = line.replace('@field:', '@@field:', 1)
                            result.append(line)
                            continue

            # Track end of main field
            if line.strip() == '@end_field' and in_main_field:
                in_main_field = False
                main_field_name = None

            result.append(line)

        content = '\n'.join(result)

        if content != original:
            return content, "Konverterade nested fields (@field: → @@field:)"
        return content, ""

    def _transform_add_end_fields(self, content: str) -> Tuple[str, str]:
        """Add missing @end_field and @@end_field markers."""

        original = content
        lines = content.split('\n')
        result = []

        # Track state
        open_fields = []  # Stack of ('field' or 'subfield', field_name)

        # Section headers that indicate a new field section
        section_header_pattern = re.compile(r'^###\s+(Question Text|Options|Answer|Feedback|Blanks|Scoring|Pairs|Dropdowns)\s*$', re.IGNORECASE)
        subfield_header_pattern = re.compile(r'^####\s+', re.IGNORECASE)

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Detect section header (### Question Text, ### Blanks, etc.)
            # This indicates we should close any open fields before starting new section
            if section_header_pattern.match(stripped):
                # Close any open subfields first
                while open_fields and open_fields[-1][0] == 'subfield':
                    result.append('@@end_field')
                    open_fields.pop()
                # Close previous main field if open
                if open_fields and open_fields[-1][0] == 'field':
                    result.append('@end_field')
                    open_fields.pop()
                result.append(line)
                continue

            # Detect subfield header (#### General Feedback, #### Blank 1, etc.)
            # Close any open subfield before the header
            if subfield_header_pattern.match(stripped):
                if open_fields and open_fields[-1][0] == 'subfield':
                    result.append('@@end_field')
                    open_fields.pop()
                result.append(line)
                continue

            # Detect new main field
            if stripped.startswith('@field:') and not stripped.startswith('@@field:'):
                result.append(line)
                field_match = re.match(r'@field:\s*(\w+)', stripped)
                if field_match:
                    open_fields.append(('field', field_match.group(1)))
                continue

            # Detect new subfield
            if stripped.startswith('@@field:'):
                # Close previous subfield if open
                if open_fields and open_fields[-1][0] == 'subfield':
                    result.append('@@end_field')
                    open_fields.pop()

                result.append(line)
                field_match = re.match(r'@@field:\s*(\w+)', stripped)
                if field_match:
                    open_fields.append(('subfield', field_match.group(1)))
                continue

            # Detect existing end markers
            if stripped == '@end_field':
                # Close any open subfields first
                while open_fields and open_fields[-1][0] == 'subfield':
                    result.append('@@end_field')
                    open_fields.pop()
                # Then close the main field
                if open_fields and open_fields[-1][0] == 'field':
                    open_fields.pop()
                result.append(line)
                continue

            if stripped == '@@end_field':
                if open_fields and open_fields[-1][0] == 'subfield':
                    open_fields.pop()
                result.append(line)
                continue

            # Detect new question (closes all open fields)
            if stripped.startswith('# Q') and re.match(r'^#\s+Q\d{3}', stripped):
                # Close all open fields
                while open_fields:
                    if open_fields[-1][0] == 'subfield':
                        result.append('@@end_field')
                    else:
                        result.append('@end_field')
                    open_fields.pop()
                result.append(line)
                continue

            # Default: just append the line
            result.append(line)

        # Close any remaining open fields at end of file
        while open_fields:
            if open_fields[-1][0] == 'subfield':
                result.append('@@end_field')
            else:
                result.append('@end_field')
            open_fields.pop()

        content = '\n'.join(result)

        if content != original:
            return content, "La till saknade @end_field och @@end_field"
        return content, ""

    def _transform_normalize_type_names(self, content: str) -> Tuple[str, str]:
        """Normalize type aliases to valid QTI type names."""

        # Type aliases that need normalization
        type_aliases = {
            'multiple_choice': 'multiple_choice_single',
            'mc': 'multiple_choice_single',
            'mcq': 'multiple_choice_single',
            'mr': 'multiple_response',
            'tf': 'true_false',
        }

        original = content

        for alias, correct in type_aliases.items():
            # Match ^type: alias or ^type alias (with optional colon)
            pattern = rf'(\^type:?\s+){re.escape(alias)}(\s*$)'
            replacement = rf'\g<1>{correct}\2'
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.IGNORECASE)

        if content != original:
            return content, "Normaliserade typnamn (multiple_choice → multiple_choice_single)"
        return content, ""

    def _transform_extract_correct_answers(self, content: str) -> Tuple[str, str]:
        """Extract [correct] markers from options into correct_answers section."""

        original = content

        # Only apply to multiple_response questions
        if not re.search(r'\^type:?\s+multiple_response', content, re.IGNORECASE):
            return content, ""

        # Check if correct_answers section already exists
        if re.search(r'@field:\s*correct_answers', content, re.IGNORECASE):
            return content, ""

        # Find [correct] markers in options section
        correct_options = []
        options_match = re.search(
            r'(###\s*Options.*?)(?=###|\Z)',
            content,
            re.DOTALL | re.IGNORECASE
        )

        if options_match:
            options_section = options_match.group(1)
            # Find options marked with [correct]
            for match in re.finditer(r'-\s*\[([A-Z])\].*?\[correct\]', options_section, re.IGNORECASE):
                correct_options.append(match.group(1))

        if not correct_options:
            return content, ""

        # Create correct_answers section
        correct_answers_section = f"\n### Correct Answers\n@field: correct_answers\n{', '.join(correct_options)}\n@end_field\n"

        # Remove [correct] markers from options
        content = re.sub(r'\s*\[correct\]', '', content, flags=re.IGNORECASE)

        # Insert correct_answers section after Answer section or after Options
        # Look for ### Answer section
        answer_end = re.search(r'(###\s*Answer.*?@end_field\s*)', content, re.DOTALL | re.IGNORECASE)
        if answer_end:
            insert_pos = answer_end.end()
            content = content[:insert_pos] + correct_answers_section + content[insert_pos:]
        else:
            # Insert after Options section
            options_end = re.search(r'(###\s*Options.*?@end_field\s*)', content, re.DOTALL | re.IGNORECASE)
            if options_end:
                insert_pos = options_end.end()
                content = content[:insert_pos] + correct_answers_section + content[insert_pos:]

        if content != original:
            return content, f"Extraherade correct_answers: {', '.join(correct_options)}"
        return content, ""

    def _transform_restructure_text_entry(self, content: str) -> Tuple[str, str]:
        """Add {{blank_1}} placeholder and @field: blanks for text_entry questions."""

        original = content

        # Only apply to text_entry type questions
        if not re.search(r'\^type:?\s+text_entry', content, re.IGNORECASE):
            return content, ""

        # Check if blank placeholder already exists
        has_placeholder = bool(re.search(r'\{\{blank_\d+\}\}', content, re.IGNORECASE))
        # Check if blanks field already exists
        has_blanks_field = bool(re.search(r'@field:\s*blanks', content, re.IGNORECASE))

        if has_placeholder and has_blanks_field:
            return content, ""

        # If no placeholder, add one to question text
        if not has_placeholder:
            # Find the question_text section and add placeholder
            # Look for @field: question_text section
            qt_match = re.search(
                r'(@field:\s*question_text\s*\n)(.*?)(@end_field|(?=###))',
                content,
                re.DOTALL | re.IGNORECASE
            )
            if qt_match:
                field_start = qt_match.group(1)
                qt_content = qt_match.group(2).rstrip()
                field_end = qt_match.group(3)

                # Add blank placeholder at end of question text
                new_qt = f"{field_start}{qt_content}\n\nSvar: {{{{blank_1}}}}\n{field_end}"
                content = content[:qt_match.start()] + new_qt + content[qt_match.end():]

        # If no blanks field, add one
        if not has_blanks_field:
            # Try to extract answer from Answer section
            answer_value = ""
            answer_match = re.search(
                r'###\s*Answer.*?@field:\s*answer\s*\n(.*?)(?:@end_field|(?=###))',
                content,
                re.DOTALL | re.IGNORECASE
            )
            if answer_match:
                answer_value = answer_match.group(1).strip()

            # Create blanks section
            blanks_section = f"""
### Blanks
@field: blanks

#### Blank 1
@@field: blank_1
{answer_value if answer_value else "[ANGE SVAR]"}
@@end_field

@end_field
"""

            # Insert before Feedback section or at end
            feedback_pos = re.search(r'(###\s*Feedback)', content, re.IGNORECASE)
            if feedback_pos:
                content = content[:feedback_pos.start()] + blanks_section + "\n" + content[feedback_pos.start():]
            else:
                content = content.rstrip() + "\n" + blanks_section

        if content != original:
            return content, "Lade till {{blank_1}} placeholder och @field: blanks"
        return content, ""


# Global transformer instance
transformer = Transformer()
