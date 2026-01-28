"""
User interaction prompts for Step 1.
"""

from typing import Dict, List, Any, Optional


# Bloom taxonomy levels with descriptions
BLOOM_LEVELS = [
    ('Remember', 'Minnas fakta, definitioner, termer'),
    ('Understand', 'Förklara, sammanfatta, tolka'),
    ('Apply', 'Använda kunskap i ny situation'),
    ('Analyze', 'Bryta ner, jämföra, identifiera mönster'),
    ('Evaluate', 'Bedöma, kritisera, motivera'),
    ('Create', 'Skapa, designa, konstruera'),
]

DIFFICULTY_LEVELS = [
    ('Easy', 'Grundläggande - de flesta klarar'),
    ('Medium', 'Medel - kräver god förståelse'),
    ('Hard', 'Svår - kräver djup förståelse'),
]

PROMPTS = {
    'select_bloom': {
        'type': 'single_choice',
        'question': 'Vilken Bloom-nivå har denna fråga?',
        'options': BLOOM_LEVELS,
        'help': 'Välj den kognitiva nivå som bäst beskriver vad frågan testar.'
    },

    'select_difficulty': {
        'type': 'single_choice',
        'question': 'Vilken svårighetsgrad har denna fråga?',
        'options': DIFFICULTY_LEVELS,
        'help': 'Uppskatta hur svår frågan är för en typisk student.'
    },

    'confirm_identifier': {
        'type': 'confirm_or_edit',
        'question': 'Genererad identifier: {identifier}. Godkänn eller ändra:',
        'default': '{identifier}',
        'help': 'Identifier måste vara unik. Format: KURS_TYP_NUMMER'
    },

    'missing_labels': {
        'type': 'text_input',
        'question': 'Ange labels för frågan:',
        'placeholder': '#KURS #Ämne #Bloom #Difficulty',
        'help': 'Labels måste innehålla minst Bloom-nivå och svårighetsgrad.'
    },

    'suggest_feedback': {
        'type': 'confirm_suggestion',
        'question': 'Saknar {field}. Vill du att jag föreslår?',
        'options': [
            ('yes', 'Ja, föreslå'),
            ('manual', 'Nej, jag skriver själv'),
            ('skip', 'Hoppa över')
        ]
    },

    'ambiguous_type': {
        'type': 'single_choice',
        'question': 'Kan inte avgöra frågetyp. Vilken är det?',
        'options': [
            ('multiple_choice_single', 'Flerval (ett svar)'),
            ('multiple_response', 'Flerval (flera svar)'),
            ('text_entry', 'Fyll i lucka'),
            ('inline_choice', 'Dropdown'),
            ('match', 'Matchning'),
            ('text_area', 'Fritext/Essä'),
        ]
    },

    'batch_apply': {
        'type': 'batch_confirm',
        'question': 'Samma fix kan appliceras på {count} liknande frågor:',
        'preview_count': 3,  # Show first 3 as preview
        'options': [
            ('all', 'Applicera på alla {count}'),
            ('select', 'Låt mig välja'),
            ('skip', 'Bara denna fråga')
        ]
    },

    'image_missing': {
        'type': 'path_input',
        'question': 'Bildfil "{filename}" hittades inte. Var finns den?',
        'allow_skip': True,
        'skip_warning': 'Frågan exporteras utan bild.'
    },

    'confirm_changes': {
        'type': 'confirm',
        'question': 'Applicera dessa ändringar?',
        'show_diff': True
    }
}


def get_prompt(prompt_key: str, **kwargs) -> Dict[str, Any]:
    """
    Get a prompt configuration with interpolated values.

    Args:
        prompt_key: Key from PROMPTS dict
        **kwargs: Values to interpolate

    Returns:
        Prompt configuration dict
    """
    if prompt_key not in PROMPTS:
        raise ValueError(f"Unknown prompt: {prompt_key}")

    prompt = PROMPTS[prompt_key].copy()

    # Interpolate question text
    if 'question' in prompt:
        prompt['question'] = prompt['question'].format(**kwargs)

    # Interpolate options if present
    if 'options' in prompt and isinstance(prompt['options'], list):
        new_options = []
        for opt in prompt['options']:
            if isinstance(opt, tuple) and len(opt) == 2:
                try:
                    new_options.append((opt[0].format(**kwargs), opt[1].format(**kwargs)))
                except (KeyError, IndexError):
                    new_options.append(opt)
            else:
                new_options.append(opt)
        prompt['options'] = new_options

    return prompt


def format_issue_summary(issues: List[Any]) -> str:
    """Format issues for display to user."""
    lines = []

    critical = [i for i in issues if i.severity.value == 'critical']
    warning = [i for i in issues if i.severity.value == 'warning']
    info = [i for i in issues if i.severity.value == 'info']

    if critical:
        lines.append(f"**{len(critical)} kritiska problem** (måste fixas):")
        for issue in critical:
            auto = " [AUTO]" if issue.auto_fixable else ""
            lines.append(f"  - {issue.message}{auto}")

    if warning:
        lines.append(f"\n**{len(warning)} varningar** (rekommenderas):")
        for issue in warning:
            auto = " [AUTO]" if issue.auto_fixable else ""
            lines.append(f"  - {issue.message}{auto}")

    if info:
        lines.append(f"\n**{len(info)} förslag:**")
        for issue in info:
            lines.append(f"  - {issue.message}")

    if not lines:
        lines.append("Inga problem hittades!")

    return '\n'.join(lines)


def format_progress(progress: Dict) -> str:
    """Format progress for display."""
    bar_length = 20
    filled = int(bar_length * progress['percent'] / 100)
    bar = '█' * filled + '░' * (bar_length - filled)

    return (
        f"[{bar}] {progress['percent']}%\n"
        f"Fråga {progress['current']} av {progress['total']}\n"
        f"Klara: {progress['completed']} | Hoppade: {progress['skipped']} | Kvar: {progress['remaining']}"
    )


def format_question_preview(question_id: str, title: Optional[str], q_type: Optional[str],
                           issue_count: int) -> str:
    """Format question info for preview."""
    title_str = f" - {title}" if title else ""
    type_str = f" ({q_type})" if q_type else ""
    issues_str = f" [{issue_count} problem]" if issue_count > 0 else " [OK]"

    return f"{question_id}{title_str}{type_str}{issues_str}"
