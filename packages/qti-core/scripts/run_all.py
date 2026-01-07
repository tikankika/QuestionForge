#!/usr/bin/env python3
"""
Run All Steps: Complete QTI Generation Pipeline

Runs all steps of the QTI generation pipeline in sequence:
1. Validate markdown format
2. Create output folder structure
3. Copy and rename resources
4. Generate QTI XML files
5. Create QTI package (ZIP)

Usage:
    python scripts/run_all.py <markdown_file> [options]

Options:
    --output-name NAME      Override quiz name (default: markdown filename)
    --output-dir DIR        Output base directory (default: ./output)
    --media-dir DIR         Media directory (default: auto-detect)
    --language LANG         Question language code (default: en)
    --strict                Treat resource warnings as errors
    --no-keep-folder       Delete extracted folder after zipping
    -v, --verbose          Show detailed information

Exit codes:
    0 = Success
    1 = Error in any step

Example:
    python scripts/run_all.py input/quiz.md
    python scripts/run_all.py input/quiz.md --output-name evolution_test --language sv
    python scripts/run_all.py input/quiz.md --output-dir ~/Nextcloud/Export --verbose
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_step(script_name: str, args: list, step_num: int, total_steps: int, verbose: bool = False):
    """
    Run a single pipeline step.

    Args:
        script_name: Name of the script to run
        args: List of command-line arguments
        step_num: Current step number
        total_steps: Total number of steps
        verbose: If True, show detailed output

    Returns:
        True if successful, False otherwise
    """
    print()
    print("=" * 70)
    print(f"PIPELINE: STEP {step_num}/{total_steps}")
    print("=" * 70)

    # Build command
    script_path = Path(__file__).parent / script_name
    cmd = [sys.executable, str(script_path)] + args

    if verbose:
        print(f"Running: {' '.join(cmd)}")
        print()

    # Run step
    result = subprocess.run(cmd)

    if result.returncode != 0:
        print()
        print(f"✗ Step {step_num} failed with exit code {result.returncode}", file=sys.stderr)
        return False

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Run complete QTI generation pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage:
  python scripts/run_all.py quiz.md

  # Custom output name and Swedish language:
  python scripts/run_all.py quiz.md --output-name evolution_test --language sv

  # Export to Nextcloud:
  python scripts/run_all.py quiz.md --output-dir ~/Nextcloud/Export

  # Strict mode (treat warnings as errors):
  python scripts/run_all.py quiz.md --strict --verbose

This script runs all 5 steps of the QTI generation pipeline in sequence.
If you need to debug individual steps, run them separately using:
  step1_validate.py, step2_create_folder.py, step3_copy_resources.py,
  step4_generate_xml.py, step5_create_zip.py
        """
    )

    parser.add_argument(
        'markdown_file',
        type=str,
        help='Path to markdown quiz file'
    )

    parser.add_argument(
        '--output-name',
        type=str,
        help='Override quiz name (default: markdown filename)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Output base directory (default: ./output)'
    )

    parser.add_argument(
        '--media-dir',
        type=str,
        help='Media directory (default: auto-detect from markdown location)'
    )

    parser.add_argument(
        '--language',
        type=str,
        default='en',
        help='Question language code (default: en)'
    )

    parser.add_argument(
        '--strict',
        action='store_true',
        help='Treat resource warnings as errors'
    )

    parser.add_argument(
        '--no-keep-folder',
        action='store_true',
        help='Delete extracted folder after creating ZIP'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed information'
    )

    args = parser.parse_args()

    # Check markdown file exists
    markdown_path = Path(args.markdown_file)
    if not markdown_path.exists():
        print(f"✗ Error: File not found: {args.markdown_file}", file=sys.stderr)
        sys.exit(1)

    # Print pipeline header
    print("=" * 70)
    print("QTI GENERATION PIPELINE")
    print("=" * 70)
    print(f"Input:          {markdown_path}")
    print(f"Output dir:     {args.output_dir}")
    if args.output_name:
        print(f"Quiz name:      {args.output_name}")
    print(f"Language:       {args.language}")
    print(f"Strict mode:    {args.strict}")
    print()

    total_steps = 5

    # Step 1: Validate
    step1_args = [args.markdown_file]
    if args.verbose:
        step1_args.append('--verbose')

    if not run_step('step1_validate.py', step1_args, 1, total_steps, args.verbose):
        sys.exit(1)

    # Step 2: Create folder
    step2_args = [args.markdown_file, '--output-dir', args.output_dir]
    if args.output_name:
        step2_args.extend(['--output-name', args.output_name])
    if args.verbose:
        step2_args.append('--verbose')

    if not run_step('step2_create_folder.py', step2_args, 2, total_steps, args.verbose):
        sys.exit(1)

    # Determine quiz directory for subsequent steps
    quiz_name = args.output_name if args.output_name else markdown_path.stem
    quiz_dir = Path(args.output_dir).expanduser().resolve() / quiz_name

    # Step 3: Copy resources
    step3_args = ['--quiz-dir', str(quiz_dir)]
    if args.media_dir:
        step3_args.extend(['--media-dir', args.media_dir])
    if args.strict:
        step3_args.append('--strict')
    if args.verbose:
        step3_args.append('--verbose')

    if not run_step('step3_copy_resources.py', step3_args, 3, total_steps, args.verbose):
        sys.exit(1)

    # Step 4: Generate XML
    step4_args = ['--quiz-dir', str(quiz_dir), '--language', args.language]
    if args.verbose:
        step4_args.append('--verbose')

    if not run_step('step4_generate_xml.py', step4_args, 4, total_steps, args.verbose):
        sys.exit(1)

    # Step 5: Create ZIP
    step5_args = ['--quiz-dir', str(quiz_dir)]
    if args.output_name:
        step5_args.extend(['--output-name', f"{args.output_name}.zip"])
    if args.no_keep_folder:
        step5_args.append('--no-keep-folder')
    if args.verbose:
        step5_args.append('--verbose')

    if not run_step('step5_create_zip.py', step5_args, 5, total_steps, args.verbose):
        sys.exit(1)

    # Success!
    print()
    print("=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)
    print("✓ All steps completed successfully!")
    print()
    print("Your QTI package is ready for upload to Inspera.")
    print()

    sys.exit(0)


if __name__ == '__main__':
    main()
