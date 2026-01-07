#!/usr/bin/env python3
"""
Interactive QTI Generator

User-friendly interactive interface for generating QTI packages.
Guides you through folder selection, file selection, and settings configuration.

Usage:
    python scripts/interactive_qti.py [options]

Options:
    --last              Use last selected file
    --quick             Use defaults without prompting
    --folder NAME       Start with specific folder
    -v, --verbose      Show detailed output

Example:
    python scripts/interactive_qti.py
    python scripts/interactive_qti.py --last --quick
"""

import sys
import json
import subprocess
import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Rich library for colored terminal output
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

# Initialize console for colored output
console = Console()


# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import for Question Set generation
from src.generator.assessment_test_generator import (
    AssessmentTestGenerator,
    SectionConfig,
    generate_assessment_test
)


def parse_selection_input(input_str: str) -> List[int]:
    """
    Parse user selection input supporting both comma and 'or' separators.

    Examples:
        "1,2,3" -> [1, 2, 3]
        "1 or 2 or 3" -> [1, 2, 3]
        "1 OR 2" -> [1, 2]
        "1or2" -> [1, 2]

    Returns:
        List of selected indices (1-based)
    """
    if not input_str:
        return []

    normalized = input_str.lower().strip()

    # Split on 'or' (case-insensitive, handles spaces)
    parts = re.split(r'\s*or\s*', normalized)

    # If no 'or' found, try comma (backward compatibility)
    if len(parts) == 1:
        parts = [p.strip() for p in normalized.split(',')]

    # Extract numbers
    selected = []
    for part in parts:
        part = part.strip()
        if part.isdigit():
            selected.append(int(part))

    return selected

# Import for parsing quiz data
from src.parser.markdown_parser import MarkdownQuizParser


def _parse_question_tags(tags) -> List[str]:
    """
    Parse question tags consistently, handling both list and string formats.

    Supports:
    - List format (already parsed): ['Easy', 'Remember', 'BIOG001X']
    - Comma-separated string: "Easy, Remember, BIOG001X"
    - Space-separated string: "Easy Remember BIOG001X" or "#Easy #Remember #BIOG001X"

    Returns:
        List of normalized tag strings (no # prefix)
    """
    if isinstance(tags, list):
        return [tag.strip().lstrip('#') for tag in tags]
    elif isinstance(tags, str):
        tag_value = tags.strip()
        if ',' in tag_value:
            # Comma-separated
            return [tag.strip().lstrip('#') for tag in tag_value.split(',')]
        else:
            # Space-separated
            return [tag.strip().lstrip('#') for tag in tag_value.split()]
    else:
        return []


def _calculate_remaining_counts(
    questions: List[Dict],
    used_question_ids: set,
    bloom_tags: Dict,
    difficulty_tags: Dict,
    custom_tags: Dict,
    points_distribution: Dict,
    selected_bloom: Optional[List[str]] = None,
    selected_difficulty: Optional[List[str]] = None,
    selected_custom: Optional[List[str]] = None,
    selected_points: Optional[List[int]] = None
) -> tuple:
    """
    Calculate total and remaining counts for each tag category.

    Takes into account currently selected filters to show how many questions
    are still available given the current filter selections.

    Args:
        questions: List of all questions
        used_question_ids: Set of already-used question IDs
        bloom_tags: Dict of Bloom taxonomy tags with counts
        difficulty_tags: Dict of difficulty tags with counts
        custom_tags: Dict of custom tags with counts
        points_distribution: Dict of point values with counts
        selected_bloom: Currently selected Bloom filters (OR within)
        selected_difficulty: Currently selected Difficulty filters (OR within)
        selected_custom: Currently selected Custom filters (OR within)
        selected_points: Currently selected Points filters (OR within)

    Returns:
        Tuple of (bloom_remaining, diff_remaining, custom_remaining, points_remaining)
        Each dict: {tag: (total_count, remaining_count)}
    """
    bloom_remaining = {}
    diff_remaining = {}
    custom_remaining = {}
    points_remaining = {}

    # Initialize with totals and zero remaining
    for tag, count in bloom_tags.items():
        bloom_remaining[tag] = (count, 0)
    for tag, count in difficulty_tags.items():
        diff_remaining[tag] = (count, 0)
    for tag, count in custom_tags.items():
        custom_remaining[tag] = (count, 0)
    for points, count in points_distribution.items():
        points_remaining[points] = (count, 0)

    # Define known tag categories for categorization
    bloom_tags_set = {'remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'}
    difficulty_tags_set = {'easy', 'medium', 'hard'}

    # Count remaining (unused) questions per tag
    for q in questions:
        if q.get('identifier') in used_question_ids:
            continue  # Skip used questions

        q_tags = _parse_question_tags(q.get('tags', []))
        q_tags_normalized = [t.lower() for t in q_tags]

        # Categorize question tags
        q_bloom = [t for t in q_tags_normalized if t in bloom_tags_set]
        q_difficulty = [t for t in q_tags_normalized if t in difficulty_tags_set]
        q_custom = [t for t in q_tags_normalized if t not in bloom_tags_set and t not in difficulty_tags_set]

        q_points = q.get('points', 1)

        # Check if question matches currently selected filters
        matches_filters = True

        # Check selected_bloom (OR within)
        if selected_bloom:
            bloom_match = any(b.lower() in q_bloom for b in selected_bloom)
            if not bloom_match:
                matches_filters = False

        # Check selected_difficulty (OR within)
        if selected_difficulty:
            diff_match = any(d.lower() in q_difficulty for d in selected_difficulty)
            if not diff_match:
                matches_filters = False

        # Check selected_custom (OR within)
        if selected_custom:
            custom_match = any(c.lower() in q_custom for c in selected_custom)
            if not custom_match:
                matches_filters = False

        # Check selected_points (OR within)
        if selected_points:
            if q_points not in selected_points:
                matches_filters = False

        # Only count if matches all filters
        if matches_filters:
            # Update remaining counts
            for tag in q_tags:
                tag_clean = tag.lstrip('#')

                if tag_clean in bloom_tags:
                    total, rem = bloom_remaining.get(tag_clean, (0, 0))
                    bloom_remaining[tag_clean] = (total, rem + 1)
                elif tag_clean in difficulty_tags:
                    total, rem = diff_remaining.get(tag_clean, (0, 0))
                    diff_remaining[tag_clean] = (total, rem + 1)
                elif tag_clean in custom_tags:
                    total, rem = custom_remaining.get(tag_clean, (0, 0))
                    custom_remaining[tag_clean] = (total, rem + 1)

            if q_points in points_distribution:
                total, rem = points_remaining.get(q_points, (0, 0))
                points_remaining[q_points] = (total, rem + 1)

    return bloom_remaining, diff_remaining, custom_remaining, points_remaining


def validate_questions_for_question_set(questions: List[Dict]) -> None:
    """
    Validate questions before creating Question Set.
    Shows warnings for match questions and float point values that were auto-corrected during parsing.

    Args:
        questions: List of parsed question dictionaries
    """
    validation_warnings = []

    for q in questions:
        q_id = q.get('identifier', 'UNKNOWN')

        # Check match questions - warn if premises count doesn't match points
        # (these should have been auto-corrected during parsing, but show warning)
        if q.get('question_type') == 'match':
            premise_count = len(q.get('premises', []))
            points = q.get('points', 1)

            if premise_count != points:
                # This shouldn't happen after auto-correction, but warn just in case
                validation_warnings.append(
                    f"  • {q_id}: Match question with {premise_count} premises has Points: {points}"
                )

        # Check for float points (these should also be auto-corrected, but check anyway)
        points = q.get('points')
        if isinstance(points, float) and points != int(points):
            validation_warnings.append(
                f"  • {q_id}: Points: {points} is a decimal value (unexpected)"
            )

    if validation_warnings:
        console.print("\n[yellow]⚠️  Validation issues detected:[/]")
        for warning in validation_warnings:
            console.print(f"[yellow]{warning}[/]")
        console.print()


def ask_create_question_set(quiz_dir: Path, quiz_data: dict) -> bool:
    """
    Ask user if they want to create a Question Set with sections.

    This function is called after XML generation but before ZIP creation.
    It analyzes questions and allows interactive section configuration.

    Args:
        quiz_dir: Path to the quiz output directory
        quiz_data: Parsed quiz data with 'metadata' and 'questions'

    Returns:
        True if Question Set was created, False otherwise
    """
    questions = quiz_data.get('questions', [])
    metadata = quiz_data.get('metadata', {})

    if not questions:
        return False

    # Validate questions before proceeding
    validate_questions_for_question_set(questions)

    if not questions:
        return False

    # Analyze questions
    all_tags = set()
    points_distribution = {}

    # Categorize tags for filtering
    bloom_levels = {'Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create'}
    difficulty_levels = {'Easy', 'Medium', 'Hard'}

    bloom_tags = {}
    difficulty_tags = {}
    custom_tags = {}

    for q in questions:
        tags = _parse_question_tags(q.get('tags', []))
        all_tags.update(tags)

        # Categorize each tag (tags are already cleaned by _parse_question_tags)
        for tag in tags:
            tag_clean = tag

            if tag_clean in bloom_levels:
                bloom_tags[tag_clean] = bloom_tags.get(tag_clean, 0) + 1
            elif tag_clean in difficulty_levels:
                difficulty_tags[tag_clean] = difficulty_tags.get(tag_clean, 0) + 1
            else:
                custom_tags[tag_clean] = custom_tags.get(tag_clean, 0) + 1

        points = q.get('points', 1)
        points_distribution[points] = points_distribution.get(points, 0) + 1

    # Sort custom tags by frequency, take top 20
    top_custom_tags = sorted(custom_tags.items(), key=lambda x: x[1], reverse=True)[:20]

    # Create analysis table
    console.print()
    console.print(Panel("[bold]📊 Frågeanalys[/]", border_style="blue"))

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Egenskap", style="dim")
    table.add_column("Värde")

    table.add_row("Totalt antal frågor", str(len(questions)))

    points_str = ", ".join([f"{p}p: {c} st" for p, c in sorted(points_distribution.items())])
    table.add_row("Poängfördelning", points_str)

    if all_tags:
        tags_str = ", ".join(sorted(all_tags))
        table.add_row("Tags", tags_str)
    else:
        table.add_row("Tags", "(inga)")

    console.print(table)
    console.print()

    # Ask user
    console.print("[bold yellow]🔀 Vill du skapa Question Set med sektioner?[/]")
    console.print("   Detta låter dig gruppera frågor och välja hur många som ska slumpas.")
    console.print()

    response = console.input("[bold]Skapa Question Set? (j/n): [/]").strip().lower()

    if response != 'j':
        console.print("[dim]Hoppar över Question Set[/]\n")
        return False

    # Collect section configuration
    sections = []
    console.print()
    console.print("[bold cyan]Definiera sektioner[/]")
    console.print("[dim]Tryck Enter för standardvärden, 'klar' för att avsluta[/]\n")

    # Add overview explanation
    console.print("[cyan]ℹ️  VAD ÄR EN SEKTION?[/]")
    console.print("   En sektion är en grupp frågor med gemensamma egenskaper.")
    console.print("   Du kan skapa flera sektioner med olika filter och antal frågor.\n")
    console.print("[dim]   EXEMPEL:[/]")
    console.print("[dim]   • \"Enkla frågor om cellbiologi\" - 10 frågor med Easy + Cellbiologi[/]")
    console.print("[dim]   • \"Svårare genetikfrågor\" - 5 frågor med Hard + Genetik[/]")
    console.print("[dim]   • \"Blandade 2-poängsfrågor\" - alla 2p frågor[/]\n")

    # Track used questions to prevent duplicates across sections
    used_question_ids = set()

    section_num = 1

    # Section creation loop (no longer points-based)
    while True:
        # Check if any questions remain
        remaining_questions = len([q for q in questions
                                  if q.get('identifier') not in used_question_ids])

        if remaining_questions == 0 and section_num > 1:
            console.print("\n[yellow]✓ Alla frågor har använts i sektioner![/]")
            console.print("[dim]Avslutar sektionskapande...[/]\n")
            break

        console.print(f"[bold]Sektion {section_num}[/] [dim]({remaining_questions} frågor kvar totalt)[/]")

        # Section name
        name = console.input(f"   Namn (t.ex. \"Enkla frågor\", eller 'klar' för att avsluta): ").strip()
        if name.lower() == 'klar':
            break

        # Iterative filter building - separate by category
        selected_bloom = []
        selected_difficulty = []
        selected_custom = []
        selected_points = []

        while True:
            # Calculate remaining counts
            bloom_remaining, diff_remaining, custom_remaining, points_remaining = \
                _calculate_remaining_counts(
                    questions, used_question_ids, bloom_tags,
                    difficulty_tags, custom_tags, points_distribution,
                    selected_bloom=selected_bloom if selected_bloom else None,
                    selected_difficulty=selected_difficulty if selected_difficulty else None,
                    selected_custom=selected_custom if selected_custom else None,
                    selected_points=selected_points if selected_points else None
                )

            # Tag filtering
            console.print()
            console.print("   [bold cyan]Välj filter-tags (Enter = inga filter):[/]")
            console.print("   [dim]💡 Tips: Välj flera genom att skriva \"1,2\" eller tryck Enter för att hoppa över[/]\n")

            # Show Bloom levels with remaining counts
            if bloom_tags:
                console.print("\n   [bold]Bloom's Taxonomy:[/]")
                bloom_list = sorted(bloom_remaining.items(), key=lambda x: x[1][1], reverse=True)
                for i, (tag, (total, remaining)) in enumerate(bloom_list, 1):
                    console.print(f"      {i}. {tag} ({total} st, {remaining} kvar)")
                bloom_input = console.input("   Välj Bloom (t.ex. \"1 or 2\" för Remember+Understand, eller Enter): ").strip()

                if bloom_input:
                    selected_nums = parse_selection_input(bloom_input)
                    for num in selected_nums:
                        idx = num - 1
                        if 0 <= idx < len(bloom_list):
                            tag_name = bloom_list[idx][0]
                            if tag_name not in selected_bloom:
                                selected_bloom.append(tag_name)

            # Show Difficulty levels with remaining counts
            if difficulty_tags:
                console.print("\n   [bold]Svårighetsgrad:[/]")
                diff_list = sorted(diff_remaining.items(), key=lambda x: x[1][1], reverse=True)
                for i, (tag, (total, remaining)) in enumerate(diff_list, 1):
                    console.print(f"      {i}. {tag} ({total} st, {remaining} kvar)")
                diff_input = console.input("   Välj Difficulty (t.ex. \"1 or 2\" för Easy+Medium, eller Enter): ").strip()

                if diff_input:
                    selected_nums = parse_selection_input(diff_input)
                    for num in selected_nums:
                        idx = num - 1
                        if 0 <= idx < len(diff_list):
                            tag_name = diff_list[idx][0]
                            if tag_name not in selected_difficulty:
                                selected_difficulty.append(tag_name)

            # Show Points options with remaining counts
            if points_distribution:
                console.print("\n   [bold]Poäng:[/]")
                points_list = sorted(points_remaining.items(), key=lambda x: x[0])
                for i, (points, (total, remaining)) in enumerate(points_list, 1):
                    console.print(f"      {i}. {points}p ({total} st, {remaining} kvar)")
                points_input = console.input("   Välj poäng (t.ex. \"1 or 2\" för 1p+2p, eller Enter): ").strip()

                if points_input:
                    selected_nums = parse_selection_input(points_input)
                    for num in selected_nums:
                        idx = num - 1
                        if 0 <= idx < len(points_list):
                            points_val = points_list[idx][0]
                            if points_val not in selected_points:
                                selected_points.append(points_val)

            # Show top custom tags with remaining counts
            if top_custom_tags:
                console.print("\n   [bold]Ämnestags (top 20):[/]")
                # Rebuild custom_remaining dict for top 20 only
                top_custom_remaining = {tag: custom_remaining[tag] for tag, _ in top_custom_tags if tag in custom_remaining}
                top_custom_list = [(tag, top_custom_remaining[tag]) for tag, _ in top_custom_tags if tag in top_custom_remaining]

                for i, (tag, (total, remaining)) in enumerate(top_custom_list, 1):
                    console.print(f"      {i}. {tag} ({total} st, {remaining} kvar)")
                custom_input = console.input("   Välj ämne (t.ex. \"1 or 4\" för flera ämnen, eller Enter): ").strip()

                if custom_input:
                    selected_nums = parse_selection_input(custom_input)
                    for num in selected_nums:
                        idx = num - 1
                        if 0 <= idx < len(top_custom_list):
                            tag_name = top_custom_list[idx][0]
                            if tag_name not in selected_custom:
                                selected_custom.append(tag_name)

            # Show summary of selected filters so far
            console.print("\n   [bold cyan]📋 Valda filter hittills:[/]")
            if selected_bloom:
                console.print(f"      • Bloom: {', '.join(selected_bloom)}")
            if selected_difficulty:
                console.print(f"      • Svårighetsgrad: {', '.join(selected_difficulty)}")
            if selected_points:
                console.print(f"      • Poäng: {', '.join([f'{p}p' for p in selected_points])}")
            if selected_custom:
                console.print(f"      • Ämnen: {', '.join(selected_custom)}")
            if not (selected_bloom or selected_difficulty or selected_points or selected_custom):
                console.print("      [dim](inga filter valda än)[/]")

            # Calculate preview count
            temp_matching = 0
            for q in questions:
                if q.get('identifier') in used_question_ids:
                    continue
                if selected_points and q.get('points') not in selected_points:
                    continue
                if selected_bloom or selected_difficulty or selected_custom:
                    q_tags = _parse_question_tags(q.get('tags', []))
                    q_tags_normalized = [t.lower() for t in q_tags]
                    bloom_tags_set = {'remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'}
                    difficulty_tags_set = {'easy', 'medium', 'hard'}
                    q_bloom = [t for t in q_tags_normalized if t in bloom_tags_set]
                    q_difficulty = [t for t in q_tags_normalized if t in difficulty_tags_set]
                    q_custom = [t for t in q_tags_normalized if t not in bloom_tags_set and t not in difficulty_tags_set]
                    if selected_bloom:
                        if not any(b.lower() in q_bloom for b in selected_bloom):
                            continue
                    if selected_difficulty:
                        if not any(d.lower() in q_difficulty for d in selected_difficulty):
                            continue
                    if selected_custom:
                        if not any(c.lower() in q_custom for c in selected_custom):
                            continue
                temp_matching += 1

            console.print(f"      [bold green]→ {temp_matching} frågor matchar[/]")

            # Ask if user wants to add more filters
            console.print("\n   [dim]💡 Vill du lägga till fler filter?[/]")
            console.print("   [dim]   'j' = Visa filtermenyn igen och välj fler filter[/]")
            console.print("   [dim]   'n' eller Enter = Fortsätt konfigurera denna sektion (antal, shuffle)[/]")
            more_filters = console.input("   (j/n): ").strip().lower()
            if more_filters == '':
                more_filters = 'n'  # Default to 'n' if Enter pressed
            if more_filters != 'j':
                break

        # Preview: How many questions match filters?
        matching_count = 0
        for q in questions:
            # Skip if already used
            if q.get('identifier') in used_question_ids:
                continue

            # Check points filter (if any)
            if selected_points and q.get('points') not in selected_points:
                continue

            # Check tags filter with categorized logic (OR within, AND between)
            if selected_bloom or selected_difficulty or selected_custom:
                q_tags = _parse_question_tags(q.get('tags', []))
                q_tags_normalized = [t.lower() for t in q_tags]

                # Define known tag categories
                bloom_tags_set = {'remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'}
                difficulty_tags_set = {'easy', 'medium', 'hard'}

                # Categorize question tags
                q_bloom = [t for t in q_tags_normalized if t in bloom_tags_set]
                q_difficulty = [t for t in q_tags_normalized if t in difficulty_tags_set]
                q_custom = [t for t in q_tags_normalized if t not in bloom_tags_set and t not in difficulty_tags_set]

                # Check Bloom filter (OR within category)
                if selected_bloom:
                    bloom_match = any(b.lower() in q_bloom for b in selected_bloom)
                    if not bloom_match:
                        continue

                # Check Difficulty filter (OR within category)
                if selected_difficulty:
                    diff_match = any(d.lower() in q_difficulty for d in selected_difficulty)
                    if not diff_match:
                        continue

                # Check Custom tags filter (OR within category)
                if selected_custom:
                    custom_match = any(c.lower() in q_custom for c in selected_custom)
                    if not custom_match:
                        continue

            matching_count += 1

        # Show preview with categorized filter description
        filter_parts = []
        if selected_bloom:
            bloom_str = " OR ".join(selected_bloom)
            if len(selected_bloom) > 1:
                bloom_str = f"({bloom_str})"
            filter_parts.append(bloom_str)
        if selected_difficulty:
            diff_str = " OR ".join(selected_difficulty)
            if len(selected_difficulty) > 1:
                diff_str = f"({diff_str})"
            filter_parts.append(diff_str)
        if selected_custom:
            custom_str = " OR ".join(selected_custom)
            if len(selected_custom) > 1:
                custom_str = f"({custom_str})"
            filter_parts.append(custom_str)
        if selected_points:
            points_str = " OR ".join([f"{p}p" for p in selected_points])
            if len(selected_points) > 1:
                points_str = f"({points_str})"
            filter_parts.append(points_str)

        if filter_parts:
            filter_description = " AND ".join(filter_parts)
            console.print(f"\n   [dim]Filter: {filter_description} → {matching_count} frågor (tillgängliga)[/]")
        else:
            console.print(f"\n   [dim]Inga filter → {matching_count} frågor (tillgängliga)[/]")
        console.print()

        # Check if empty section - skip if no matching questions
        if matching_count == 0:
            console.print("\n[red]✗ Inga frågor matchar de valda filtren![/]")
            console.print("[dim]Hoppar över denna sektion. Försök med andra filter.[/]\n")
            section_num += 1
            continue  # Skip to next section

        # Number to select
        select = None
        if matching_count > 0:
            console.print(f"   [dim]💡 Hur många frågor vill du inkludera från dessa {matching_count}?[/]")
            console.print(f"   [dim]   • Skriv ett nummer (t.ex. \"10\") för att slumpa 10 av {matching_count}[/]")
            console.print(f"   [dim]   • Tryck Enter för att ta med alla {matching_count} frågor[/]")
            select_input = console.input(f"   Välj antal (1-{matching_count}, eller Enter för alla): ").strip()
            if select_input.isdigit():
                select_val = int(select_input)
                if 0 < select_val < matching_count:
                    select = select_val

        # Shuffle
        console.print("\n   [dim]💡 Ska frågorna visas i slumpmässig ordning?[/]")
        console.print("   [dim]   'j' = Slumpa ordning [standard][/]")
        console.print("   [dim]   'n' = Behåll original ordning[/]")
        shuffle_input = console.input("   (j/n): ").strip().lower()
        if shuffle_input == '':
            shuffle_input = 'j'  # Default to shuffle
        shuffle = shuffle_input != 'n'

        # Mark questions as used for this section to prevent duplicates
        # Build the actual list of questions that match this section's filters
        section_questions = []
        for q in questions:
            if q.get('identifier') in used_question_ids:
                continue

            # Check points filter
            if selected_points and q.get('points') not in selected_points:
                continue

            # Check tags filter with categorized logic (OR within, AND between)
            if selected_bloom or selected_difficulty or selected_custom:
                q_tags = _parse_question_tags(q.get('tags', []))
                q_tags_normalized = [t.lower() for t in q_tags]

                # Define known tag categories
                bloom_tags_set = {'remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'}
                difficulty_tags_set = {'easy', 'medium', 'hard'}

                # Categorize question tags
                q_bloom = [t for t in q_tags_normalized if t in bloom_tags_set]
                q_difficulty = [t for t in q_tags_normalized if t in difficulty_tags_set]
                q_custom = [t for t in q_tags_normalized if t not in bloom_tags_set and t not in difficulty_tags_set]

                # Check Bloom filter (OR within category)
                if selected_bloom:
                    bloom_match = any(b.lower() in q_bloom for b in selected_bloom)
                    if not bloom_match:
                        continue

                # Check Difficulty filter (OR within category)
                if selected_difficulty:
                    diff_match = any(d.lower() in q_difficulty for d in selected_difficulty)
                    if not diff_match:
                        continue

                # Check Custom tags filter (OR within category)
                if selected_custom:
                    custom_match = any(c.lower() in q_custom for c in selected_custom)
                    if not custom_match:
                        continue

            section_questions.append(q)

        # Append section config and the filtered questions together
        sections.append({
            'config': SectionConfig(
                name=name,
                filter_bloom=selected_bloom if selected_bloom else None,
                filter_difficulty=selected_difficulty if selected_difficulty else None,
                filter_custom=selected_custom if selected_custom else None,
                filter_points=selected_points if selected_points else None,
                select=select,
                shuffle=shuffle
            ),
            'questions': section_questions  # Pass the actual filtered questions
        })

        # Mark all candidate questions as used
        for q in section_questions:
            used_question_ids.add(q.get('identifier'))

        # Success message and progress
        console.print(f"\n[green]✓ Sektion '{name}' skapad![/]")

        # Calculate remaining questions
        remaining = len([q for q in questions if q.get('identifier') not in used_question_ids])
        console.print(f"[dim]Totalt: {len(sections)} sektioner | {remaining} frågor kvar[/]\n")

        if remaining == 0:
            console.print("[yellow]Alla frågor har använts![/]")
            break

        # Ask to continue or exit
        console.print("[bold]Vad vill du göra?[/]")
        console.print("   [cyan]j[/] - Skapa en till sektion")
        console.print("   [cyan]n[/] - Klar med sektioner")
        console.print()

        choice = console.input("Fortsätt? (j/n): ").strip().lower()
        if choice in ['n', 'klar', '']:  # 'n', 'klar', or Enter = exit
            break

        console.print()  # Extra spacing before next section
        section_num += 1

    if not sections:
        console.print("[yellow]Inga sektioner definierade[/]\n")
        return False

    # Get test metadata
    test_meta = metadata.get('test_metadata', {})
    title = test_meta.get('title', metadata.get('title', 'Question Set'))
    identifier = test_meta.get('identifier', metadata.get('identifier', 'QSET_001'))
    language = metadata.get('language', 'sv')

    # Ask for title if not set
    console.print()
    title_input = console.input(f"[bold]Question Set titel [{title}]: [/]").strip()
    if title_input:
        title = title_input

    # Generate assessmentTest
    generator = AssessmentTestGenerator()
    assessment_xml = generator.generate(
        title=title,
        identifier=identifier,
        sections=sections,
        questions=questions,
        language=language
    )

    if not assessment_xml:
        console.print("[red]Kunde inte generera Question Set[/]\n")
        return False

    # Save to quiz directory
    assessment_filename = f"ID_{identifier}-assessment.xml"
    assessment_path = quiz_dir / assessment_filename

    with open(assessment_path, 'w', encoding='utf-8') as f:
        f.write(assessment_xml)

    # Show success summary
    console.print()
    console.print(Panel(f"[bold green]✓ Question Set skapat![/]", border_style="green"))
    console.print(f"   [cyan]Fil:[/] {assessment_filename}")
    console.print(f"   [cyan]Titel:[/] {title}")
    console.print()

    for i, section in enumerate(sections, 1):
        select_info = f"väljer {section.select}" if section.select else "alla"
        shuffle_info = "slumpas" if section.shuffle else "fast ordning"
        console.print(f"   [dim]Sektion {i}:[/] {section.name} ({select_info}, {shuffle_info})")

    console.print()
    return True


def load_config() -> dict:
    """Load MQG folders configuration"""
    config_file = project_root / "config" / "mqg_folders.json"

    if not config_file.exists():
        print("✗ Config file not found: config/mqg_folders.json")
        print("  Run 'python scripts/setup_mqg_folders.py' to create it")
        sys.exit(1)

    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(config: dict):
    """Save config to mqg_folders.json"""
    config_file = project_root / "config" / "mqg_folders.json"

    # Create config directory if it doesn't exist
    config_file.parent.mkdir(exist_ok=True)

    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def load_history() -> dict:
    """Load history of recent files"""
    history_file = project_root / ".qti_history.json"

    if not history_file.exists():
        return {"recent_files": []}

    with open(history_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_history(file_path: str, folder_name: str, success: bool):
    """Save file to history"""
    history_file = project_root / ".qti_history.json"
    history = load_history()

    # Add to recent files
    entry = {
        "file": str(file_path),
        "folder": folder_name,
        "timestamp": datetime.now().isoformat(),
        "success": success
    }

    # Remove duplicates
    history["recent_files"] = [e for e in history["recent_files"] if e["file"] != str(file_path)]

    # Add new entry at beginning
    history["recent_files"].insert(0, entry)

    # Keep only last 10
    history["recent_files"] = history["recent_files"][:10]

    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def save_workflow_settings(settings: dict):
    """Save current workflow settings for step scripts to read"""
    settings_file = project_root / ".workflow_settings.json"

    # Save settings with timestamp
    workflow_data = {
        "timestamp": datetime.now().isoformat(),
        "settings": settings
    }

    with open(settings_file, 'w', encoding='utf-8') as f:
        json.dump(workflow_data, f, indent=2, ensure_ascii=False)


def expand_path(path_str: str) -> Path:
    """Expand ~ and resolve path"""
    return Path(path_str).expanduser().resolve()


def scan_subdirectories(folder_path: Path) -> List[Dict[str, any]]:
    """
    Scan folder for direct subdirectories.

    Returns list of dicts with:
    - path: full path to subdirectory
    - name: subdirectory name
    - file_count: number of .md files in this directory (including subdirs)
    """
    subdirs = []

    for item in folder_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            # Skip _archive directories
            if '_archive' in item.name.lower():
                continue

            # Count markdown files in this subdirectory (excluding _archive)
            md_files = [f for f in item.rglob("*.md") if '_archive' not in str(f)]
            file_count = len([f for f in md_files if not f.name.startswith('.') and 'README' not in f.name])

            if file_count > 0:  # Only include dirs with markdown files
                subdirs.append({
                    "path": str(item),
                    "name": item.name,
                    "file_count": file_count
                })

    # Sort by name
    subdirs.sort(key=lambda x: x['name'])

    return subdirs


def scan_markdown_files(folder_path: Path, recursive: bool = True) -> List[Dict[str, str]]:
    """
    Scan folder for markdown files.

    Args:
        folder_path: Path to scan
        recursive: If True, scan subdirectories recursively. If False, only scan this directory.

    Returns list of dicts with:
    - path: full path
    - relative_path: path relative to folder
    - name: filename
    """
    files = []

    if recursive:
        md_iterator = folder_path.rglob("*.md")
    else:
        md_iterator = folder_path.glob("*.md")

    for md_file in md_iterator:
        if md_file.is_file():
            # Skip hidden files and certain patterns
            if md_file.name.startswith('.') or 'README' in md_file.name:
                continue

            # Skip files in _archive directories
            if '_archive' in str(md_file):
                continue

            relative_path = md_file.relative_to(folder_path)

            files.append({
                "path": str(md_file),
                "relative_path": str(relative_path),
                "name": md_file.name,
                "mtime": md_file.stat().st_mtime
            })

    # Sort by relative path
    files.sort(key=lambda x: x['relative_path'])

    return files


def display_header():
    """Display application header"""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]QTI Generator - Interaktiv Meny[/bold cyan]",
        border_style="cyan",
        padding=(0, 2)
    ))
    console.print()


def select_folder(config: dict, args) -> Optional[tuple]:
    """
    Select MQG folder.

    Returns: (folder_dict, folder_index) or None if cancelled
    """
    folders = config['folders']

    if not folders:
        console.print("[bold red]✗[/] Inga MQG folders konfigurerade!")
        console.print("  Kör: [cyan]python scripts/setup_mqg_folders.py[/]")
        return None

    # Quick mode with --folder argument
    if args.folder:
        for i, folder in enumerate(folders):
            if args.folder.lower() in folder['name'].lower():
                return folder, i
        console.print(f"[bold red]✗[/] Folder '{args.folder}' not found in config")
        return None

    # Display folders
    console.print("\n[bold]▶ Välj MQG folder:[/]\n")

    for i, folder in enumerate(folders, 1):
        folder_exists = expand_path(folder['path']).exists()
        status = "[bold green]✓[/]" if folder_exists else "[bold red]✗[/]"
        console.print(f"  {i}. {folder['name']} {status}")
        if args.verbose:
            console.print(f"     [dim]{folder['path']}[/]")

    console.print("\n  [cyan]98.[/] Ange egen sökväg manuellt")
    console.print("  [dim]0. Avsluta[/]\n")

    while True:
        try:
            choice = input("Val (nummer): ").strip()

            if choice == '0':
                return None

            # Manual path option
            if choice == '98':
                console.print("\n[bold cyan]▶ Ange sökväg till MQG folder:[/]")
                console.print("[dim]Tips: Du kan använda ~ för hemkatalogen[/]\n")

                manual_path_input = input("Sökväg: ").strip()

                if not manual_path_input:
                    console.print("[yellow]⚠[/] Ingen sökväg angiven")
                    continue

                manual_path = expand_path(manual_path_input)

                if not manual_path.exists():
                    console.print(f"[bold red]✗[/] Sökvägen finns inte: {manual_path}")
                    continue

                if not manual_path.is_dir():
                    console.print(f"[bold red]✗[/] Sökvägen är inte en mapp: {manual_path}")
                    continue

                console.print(f"[bold green]✓[/] Använder: {manual_path}\n")

                # Ask if user wants to save to config
                save_prompt = input("Vill du spara denna sökväg till konfigurationen? (j/n) [n]: ").strip().lower()

                if save_prompt == 'j':
                    # Auto-generate suggested name from folder name
                    suggested_name = manual_path.name.replace('_', ' ').replace('MQG folders', '').strip()
                    # Clean up the name a bit more
                    suggested_name = ' '.join(word.capitalize() for word in suggested_name.split())

                    console.print()
                    console.print("[bold]▶ Metadata för konfigurationen:[/]")

                    # Collect metadata
                    name = input(f"Namn [{suggested_name}]: ").strip() or suggested_name
                    language = input("Default språk [sv]: ").strip() or "sv"
                    description = input("Beskrivning (optional): ").strip()

                    # Create folder entry
                    folder_entry = {
                        "name": name,
                        "path": manual_path_input,  # Keep original path with ~ if provided
                        "default_language": language
                    }

                    if description:
                        folder_entry["description"] = description

                    # Add to config and save
                    config['folders'].append(folder_entry)
                    save_config(config)

                    console.print(f"\n[bold green]✓[/] Folder '{name}' sparad till konfigurationen!")
                    console.print("[dim]Den kommer att visas som ett alternativ nästa gång du kör scriptet.[/]\n")

                    # Return the newly saved folder
                    folder_idx = len(config['folders']) - 1
                    return folder_entry, folder_idx

                else:
                    # Create a temporary folder dict for manual path (not saved)
                    manual_folder = {
                        'name': f"Manuell: {manual_path.name}",
                        'path': str(manual_path),
                        'default_language': 'sv',
                        'description': 'Manuellt angiven sökväg'
                    }

                    return manual_folder, -1  # -1 indicates manual selection

            idx = int(choice) - 1
            if 0 <= idx < len(folders):
                folder = folders[idx]
                folder_path = expand_path(folder['path'])

                if not folder_path.exists():
                    console.print(f"[bold red]✗[/] Folder finns inte: {folder_path}")
                    console.print("  Fixa path i config eller välj en annan folder")
                    continue

                return folder, idx

            console.print("[yellow]⚠[/] Ogiltigt nummer, försök igen")

        except ValueError:
            console.print("[yellow]⚠[/] Ange ett nummer")
        except KeyboardInterrupt:
            return None


def select_subdirectory(subdirs: List[Dict[str, any]], args) -> Optional[tuple]:
    """
    Select subdirectory from list.

    Returns: (subdir_path, "selected") or (None, "all") or (None, "back")
    """
    if not subdirs:
        return None, "all"  # No subdirs, show all files

    console.print("\n[bold]▶ Välj undermapp:[/]\n")

    for i, subdir in enumerate(subdirs, 1):
        console.print(f"  {i}. {subdir['name']} [dim]({subdir['file_count']} filer)[/]")

    console.print()
    console.print("  [cyan]a.[/] Visa alla filer från alla mappar")
    console.print("  [dim]0. Tillbaka[/]")
    console.print()

    while True:
        try:
            choice = input("Val (nummer, 'a' för alla eller '0'): ").strip()

            if choice == '0':
                return None, "back"

            if choice.lower() == 'a':
                return None, "all"

            idx = int(choice) - 1
            if 0 <= idx < len(subdirs):
                return Path(subdirs[idx]['path']), "selected"

            console.print("[yellow]⚠[/] Ogiltigt nummer, försök igen")

        except ValueError:
            console.print("[yellow]⚠[/] Ange ett nummer, 'a' eller '0'")
        except KeyboardInterrupt:
            return None, "back"


def select_file(files: List[Dict[str, str]], args, config: dict = None) -> Optional[str]:
    """
    Select markdown file from list.

    Returns: file path or None if cancelled
    """
    if not files:
        console.print("\n[bold red]✗[/] Inga markdown-filer hittades i denna folder")
        return None

    console.print(f"\n[bold]ℹ Hittade {len(files)} markdown-filer:[/]\n")

    # Get output directory to check for existing ZIPs
    output_dir = None
    if config:
        output_dir_str = config.get('default_output_dir', 'output')
        output_dir = expand_path(output_dir_str)

    # Display files
    for i, file in enumerate(files, 1):
        # Check if already processed (ZIP exists)
        status = ""
        if output_dir:
            file_stem = Path(file['path']).stem
            zip_path = output_dir / f"{file_stem}.zip"
            if zip_path.exists():
                status = " [bold green]✓[/]"

        # Format modification date and time
        mtime = datetime.fromtimestamp(file.get('mtime', 0))
        date_str = mtime.strftime("%Y-%m-%d %H:%M")

        console.print(f"  {i}. {file['relative_path']}  [dim]({date_str})[/]{status}")

    console.print()
    console.print("  [dim]0. Tillbaka[/]")
    console.print("  [cyan]s.[/] Sök efter fil")
    console.print()

    while True:
        choice = input("Val (nummer eller 's' för sök): ").strip()

        if choice == '0':
            return None

        if choice.lower() == 's':
            search_term = input("Sök efter (del av filnamn): ").strip()
            if search_term:
                matching = [f for f in files if search_term.lower() in f['relative_path'].lower()]

                if not matching:
                    console.print(f"[yellow]⚠[/] Inga filer matchade '{search_term}'")
                    continue

                console.print(f"\n[bold]ℹ Hittade {len(matching)} matchande filer:[/]")
                for i, file in enumerate(matching, 1):
                    # Check if already processed (ZIP exists)
                    status = ""
                    if output_dir:
                        file_stem = Path(file['path']).stem
                        zip_path = output_dir / f"{file_stem}.zip"
                        if zip_path.exists():
                            status = " [bold green]✓[/]"
                    # Format modification date and time
                    mtime = datetime.fromtimestamp(file.get('mtime', 0))
                    date_str = mtime.strftime("%Y-%m-%d %H:%M")
                    console.print(f"  {i}. {file['relative_path']}  [dim]({date_str})[/]{status}")
                console.print()

                sub_choice = input("Val (nummer): ").strip()
                try:
                    idx = int(sub_choice) - 1
                    if 0 <= idx < len(matching):
                        return matching[idx]['path']
                except ValueError:
                    pass

                console.print("[yellow]⚠[/] Ogiltigt val")
            continue

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                return files[idx]['path']

            console.print("[yellow]⚠[/] Ogiltigt nummer, försök igen")

        except ValueError:
            console.print("[yellow]⚠[/] Ange ett nummer eller 's' för sök")
        except KeyboardInterrupt:
            return None


def configure_settings(folder: dict, file_path: str, config: dict, args) -> Optional[dict]:
    """
    Configure generation settings.

    Returns: settings dict or None if cancelled
    """
    file_name = Path(file_path).stem

    console.print()
    console.print(Panel.fit(
        f"[bold]Inställningar[/]\n[dim]Fil: {Path(file_path).name}[/]",
        border_style="blue"
    ))
    console.print()

    if args.quick:
        # Use all defaults
        settings = {
            "markdown_file": file_path,
            "output_name": file_name,
            "output_dir": config.get('default_output_dir', 'output'),
            "language": folder.get('default_language', 'sv'),
            "strict": False,
            "keep_folder": True,
            "verbose": args.verbose
        }
        console.print("[bold]ℹ Quick mode - använder defaults:[/]")
        console.print(f"  Output-namn: [cyan]{settings['output_name']}[/]")
        console.print(f"  Språk: [cyan]{settings['language']}[/]")
        console.print()
        return settings

    # Interactive configuration

    # Fixed output directory from config
    output_dir = config.get('default_output_dir', 'output')

    # Better output name selection with numbered choices
    console.print("[bold]▶ Output-namn:[/]")
    console.print(f"  1. {file_name} [dim](samma som fil)[/]")
    console.print(f"  2. Ange eget namn")
    console.print()
    name_choice = input("Val [1]: ").strip() or "1"

    if name_choice == "2":
        custom_name = input(f"Ange mapp-namn [{file_name}]: ").strip()
        output_name = custom_name if custom_name else file_name
    else:
        output_name = file_name

    console.print(f"[bold green]✓[/] Output directory: [cyan]{output_dir}[/]")
    console.print(f"[bold green]✓[/] Mapp-namn: [cyan]{output_name}[/]")
    console.print()

    default_lang = folder.get('default_language', 'sv')
    language = input(f"Språk [{default_lang}]: ").strip() or default_lang

    strict = input("Strict mode (behandla varningar som fel)? (j/n) [n]: ").strip().lower() == 'j'

    keep_folder = input("Behåll extracted folder efter zipping? (j/n) [j]: ").strip().lower() != 'n'

    return {
        "markdown_file": file_path,
        "output_name": output_name,
        "output_dir": output_dir,
        "language": language,
        "strict": strict,
        "keep_folder": keep_folder,
        "verbose": args.verbose
    }


def select_steps():
    """
    Select which steps to run.

    Returns: list of step numbers, None to run all, or "quit" to exit
    """
    print("\nVilka steg vill du köra?")
    print("  1. Validera markdown format")
    print("  2. Skapa output folder")
    print("  3. Kopiera resurser")
    print("  4. Generera XML-filer")
    print("  5. Skapa ZIP-paket")
    print()
    print("  a. Alla steg (1-5)")
    print("  q. Avsluta")
    print()

    choice = input("Val (t.ex. '1,2,3' eller 'a'): ").strip().lower()

    if choice == 'q' or choice == '0':
        return "quit"

    if choice == 'a' or choice == '':
        return None  # None means all steps

    # Parse comma-separated numbers
    try:
        steps = [int(s.strip()) for s in choice.split(',')]
        valid_steps = [s for s in steps if 1 <= s <= 5]

        if not valid_steps:
            print("Inga giltiga steg valda")
            return []

        return sorted(valid_steps)

    except ValueError:
        print("Ogiltigt format")
        return []


def run_pipeline(settings: dict, steps: Optional[List[int]] = None) -> bool:
    """
    Run QTI generation pipeline.

    Args:
        settings: generation settings
        steps: list of step numbers to run, or None for all

    Returns: True if successful
    """
    all_steps = [1, 2, 3, 4, 5] if steps is None else steps

    console.print()
    console.print(Panel.fit(
        f"[bold]Kör Pipeline ({len(all_steps)} steg)[/]",
        border_style="green"
    ))
    console.print()

    success = True

    # Step 1: Validate
    if 1 in all_steps:
        console.print("[bold blue]▶[/] [bold]Steg 1/5:[/] Validerar markdown format...")
        cmd = [
            sys.executable,
            str(project_root / "scripts" / "step1_validate.py"),
            settings["markdown_file"]
        ]
        if settings["verbose"]:
            cmd.append("--verbose")

        result = subprocess.run(cmd)
        if result.returncode != 0:
            console.print("[bold red]✗[/] Validering misslyckades")
            return False
        console.print("[bold green]✓[/] Validering klar\n")

    # Step 2: Create folder
    if 2 in all_steps:
        console.print("[bold blue]▶[/] [bold]Steg 2/5:[/] Skapar output folder...")
        cmd = [
            sys.executable,
            str(project_root / "scripts" / "step2_create_folder.py"),
            settings["markdown_file"],
            "--output-name", settings["output_name"],
            "--output-dir", settings["output_dir"]
        ]
        if settings["verbose"]:
            cmd.append("--verbose")

        result = subprocess.run(cmd)
        if result.returncode != 0:
            console.print("[bold red]✗[/] Folder-skapande misslyckades")
            return False
        console.print("[bold green]✓[/] Folder skapad\n")

    # Step 3: Copy resources
    if 3 in all_steps:
        console.print("[bold blue]▶[/] [bold]Steg 3/5:[/] Kopierar resurser...")

        # Build the quiz directory path from settings
        quiz_dir = Path(settings["output_dir"]) / settings["output_name"]

        cmd = [
            sys.executable,
            str(project_root / "scripts" / "step3_copy_resources.py"),
            "--quiz-dir", str(quiz_dir)
        ]
        if settings["strict"]:
            cmd.append("--strict")
        if settings["verbose"]:
            cmd.append("--verbose")

        result = subprocess.run(cmd)
        if result.returncode != 0:
            console.print("[bold red]✗[/] Resurs-kopiering misslyckades")
            return False
        console.print("[bold green]✓[/] Resurser kopierade\n")

    # Step 4: Generate XML
    if 4 in all_steps:
        console.print("[bold blue]▶[/] [bold]Steg 4/5:[/] Genererar XML-filer...")

        # Build the quiz directory path from settings
        quiz_dir = Path(settings["output_dir"]) / settings["output_name"]

        cmd = [
            sys.executable,
            str(project_root / "scripts" / "step4_generate_xml.py"),
            "--quiz-dir", str(quiz_dir),
            "--language", settings["language"]
        ]
        if settings["verbose"]:
            cmd.append("--verbose")

        result = subprocess.run(cmd)
        if result.returncode != 0:
            console.print("[bold red]✗[/] XML-generering misslyckades")
            return False
        console.print("[bold green]✓[/] XML genererat\n")

        # Step 4.5: Interactive Question Set creation
        console.print("\n[bold cyan]═══ Steg 4.5/5: Kontrollerar Question Set... ═══[/]\n")

        question_set_created = False
        try:
            # Read quiz data
            markdown_content = Path(settings["markdown_file"]).read_text(encoding='utf-8')
            parser = MarkdownQuizParser(markdown_content)
            quiz_data = parser.parse()

            if not quiz_data:
                console.print("[dim]Ingen frågedata hittades - hoppar över Question Set[/]\n")
            else:
                quiz_dir = Path(settings["output_dir"]) / settings["output_name"]

                # Call the interactive Question Set creation
                result = ask_create_question_set(quiz_dir, quiz_data)

                if result:
                    question_set_created = True
                    console.print("[green]✓ Question Set skapades framgångsrikt[/]\n")
                else:
                    console.print("[dim]Question Set valdes inte - fortsätter med vanligt quiz[/]\n")

        except FileNotFoundError as e:
            console.print(f"[yellow]⚠ Kunde inte läsa markdown-fil: {e}[/]")
            console.print("[dim]Fortsätter utan Question Set[/]\n")
        except Exception as e:
            console.print(f"[red]✗ Fel vid Question Set-skapande: {e}[/]")
            console.print("[dim]Fortsätter utan Question Set[/]\n")

        # Store state for Step 5
        settings["question_set_enabled"] = question_set_created

    # Step 5: Create ZIP
    if 5 in all_steps:
        console.print("[bold blue]▶[/] [bold]Steg 5/5:[/] Skapar ZIP-paket...")

        # Build the quiz directory path from settings
        quiz_dir = Path(settings["output_dir"]) / settings["output_name"]

        cmd = [
            sys.executable,
            str(project_root / "scripts" / "step5_create_zip.py"),
            "--quiz-dir", str(quiz_dir),
            "--output-name", f"{settings['output_name']}.zip"
        ]
        if not settings["keep_folder"]:
            cmd.append("--no-keep-folder")
        if settings["verbose"]:
            cmd.append("--verbose")

        result = subprocess.run(cmd)
        if result.returncode != 0:
            console.print("[bold red]✗[/] ZIP-skapande misslyckades")
            return False
        console.print("[bold green]✓[/] ZIP skapat\n")

    # Show contextual completion message based on which steps ran
    if 5 in all_steps:
        # All steps completed - ZIP file created
        output_path = Path(settings["output_dir"]) / f"{settings['output_name']}.zip"

        success_message = f"[bold green]✓ ALLA STEG KLARA![/]\n\n"
        success_message += f"[cyan]ZIP-fil:[/] {output_path}\n\n"
        success_message += "[bold]Nästa steg:[/]\n"
        success_message += "  1. Ladda upp ZIP-filen till Inspera Question Bank\n"
        success_message += "  2. Välj 'Import' → 'QTI 2.1' i Inspera"

        console.print(Panel(success_message, border_style="green", padding=(1, 2)))
        console.print()
    else:
        # Partial steps completed
        step_list = ", ".join(str(s) for s in sorted(all_steps))

        summary = f"[bold green]✓ STEG [{step_list}] KLARA![/]\n\n"

        # Show what was accomplished
        if 1 in all_steps:
            summary += "[green]✓[/] Markdown-fil validerad\n"
        if 2 in all_steps:
            output_folder = Path(settings["output_dir"]) / settings["output_name"]
            summary += f"[green]✓[/] Output-folder skapad: [cyan]{output_folder}[/]\n"
        if 3 in all_steps:
            summary += "[green]✓[/] Resurser kopierade och namngivna\n"
        if 4 in all_steps:
            summary += "[green]✓[/] XML-filer genererade\n"

        console.print(Panel(summary, border_style="green", padding=(1, 2)))
        console.print()

        # Suggest next step with complete command including arguments
        if max(all_steps) < 5:
            next_step = max(all_steps) + 1
            console.print(f"[bold]ℹ Nästa steg:[/] Kör steg {next_step}\n")

            if next_step == 2:
                cmd = f'python3 scripts/step2_create_folder.py "{settings["markdown_file"]}"'
                cmd += f' --output-name "{settings["output_name"]}"'
                cmd += f' --output-dir "{settings["output_dir"]}"'
                if settings['verbose']:
                    cmd += " --verbose"
                console.print(f"  [dim]{cmd}[/]")

            elif next_step == 3:
                cmd = "python3 scripts/step3_copy_resources.py"
                if settings['strict']:
                    cmd += " --strict"
                if settings['verbose']:
                    cmd += " --verbose"
                console.print(f"  [dim]{cmd}[/]")

            elif next_step == 4:
                cmd = f"python3 scripts/step4_generate_xml.py --language {settings['language']}"
                if settings['verbose']:
                    cmd += " --verbose"
                console.print(f"  [dim]{cmd}[/]")

            elif next_step == 5:
                cmd = f'python3 scripts/step5_create_zip.py --output-name "{settings["output_name"]}.zip"'
                if not settings['keep_folder']:
                    cmd += " --no-keep-folder"
                if settings['verbose']:
                    cmd += " --verbose"
                console.print(f"  [dim]{cmd}[/]")
            console.print()

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Interactive QTI Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--last',
        action='store_true',
        help='Use last selected file'
    )

    parser.add_argument(
        '--quick',
        action='store_true',
        help='Use defaults without prompting'
    )

    parser.add_argument(
        '--folder',
        type=str,
        help='Start with specific folder (name or partial match)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed output'
    )

    args = parser.parse_args()

    try:
        display_header()

        # Load configuration
        config = load_config()

        # Check for --last flag
        if args.last:
            history = load_history()
            if history["recent_files"]:
                last_file = history["recent_files"][0]
                print(f"Använder senast använda fil:")
                print(f"  {last_file['file']}")
                print(f"  (från {last_file['folder']})")
                print()

                # Find folder in config
                folder = None
                for f in config['folders']:
                    if f['name'] == last_file['folder']:
                        folder = f
                        break

                if not folder:
                    folder = config['folders'][0]  # Use first as fallback

                settings = configure_settings(folder, last_file['file'], config, args)
                if settings:
                    save_workflow_settings(settings)
                    success = run_pipeline(settings)
                    save_history(last_file['file'], folder['name'], success)
                    sys.exit(0 if success else 1)
            else:
                print("Ingen historik finns")
                print()

        # Select folder
        folder_result = select_folder(config, args)
        if not folder_result:
            print("\nAvbruten av användare")
            sys.exit(0)

        folder, folder_idx = folder_result
        folder_path = expand_path(folder['path'])

        print(f"\n✓ Vald folder: {folder['name']}")
        print(f"  Path: {folder_path}")
        print()

        # Scan for subdirectories
        subdirs = scan_subdirectories(folder_path)

        # If there are multiple subdirectories, let user choose
        if len(subdirs) > 1:
            selected_subdir, action = select_subdirectory(subdirs, args)

            if action == "back":
                print("\nAvbruten av användare")
                sys.exit(0)
            elif action == "all":
                # User wants to see all files from all subdirs
                scan_path = folder_path
                recursive = True
                print("\nVisar alla filer från alla mappar...")
            else:  # action == "selected"
                # User selected specific subdir
                scan_path = selected_subdir
                recursive = True  # Still scan recursively within this subdir
                print(f"\n✓ Vald undermapp: {selected_subdir.name}")
                print()
        else:
            # No subdirs or only one: scan entire folder
            scan_path = folder_path
            recursive = True

        # Scan for files
        print("Scannar efter markdown-filer...")
        files = scan_markdown_files(scan_path, recursive=recursive)

        if not files:
            print("✗ Inga markdown-filer hittades")
            sys.exit(1)

        # Select file
        file_path = select_file(files, args, config)
        if not file_path:
            print("\nAvbruten av användare")
            sys.exit(0)

        print(f"\n✓ Vald fil: {Path(file_path).name}")

        # Configure settings
        settings = configure_settings(folder, file_path, config, args)
        if not settings:
            print("\nAvbruten av användare")
            sys.exit(0)

        # Save settings for step scripts
        save_workflow_settings(settings)

        # Quick mode: run all steps once and exit
        if args.quick:
            success = run_pipeline(settings, None)
            save_history(file_path, folder['name'], success)
            sys.exit(0 if success else 1)

        # Interactive mode: ask what to run
        print()
        console.print("[bold]Vad vill du göra?[/]")
        console.print("  [cyan]j[/] = Kör alla steg (1-5) och avsluta")
        console.print("  [cyan]v[/] = Välj specifika steg (kan köras flera gånger)")
        console.print("  [cyan]n[/] = Avbryt")
        print()
        run_all = input("Val [j]: ").strip().lower()

        if run_all == 'n':
            print("\nAvbruten av användare")
            sys.exit(0)
        elif run_all == 'v':
            # Step-by-step mode: loop until user quits
            while True:
                steps = select_steps()
                if steps == "quit":
                    print("\nAvslutar...")
                    break
                if steps == []:
                    continue  # Invalid input, ask again

                success = run_pipeline(settings, steps)

            save_history(file_path, folder['name'], success if 'success' in dir() else True)
            sys.exit(0)
        else:
            # Run all steps and exit
            success = run_pipeline(settings, None)
            save_history(file_path, folder['name'], success)
            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\nAvbrutet av användare")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Fel: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
