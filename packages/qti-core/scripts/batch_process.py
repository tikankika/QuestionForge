#!/usr/bin/env python3
"""
Batch Process: Process Multiple Markdown Files

Processes all markdown files in a folder, skipping already processed files.

Usage:
    python scripts/batch_process.py --folder <path> [options]
    python scripts/batch_process.py --interactive

Options:
    --folder DIR            Folder containing markdown files
    --output-dir DIR        Output base directory (default: ~/Nextcloud/Inspera/QTI_export_INSPERA)
    --language LANG         Question language code (default: sv)
    --force                 Re-process even if ZIP exists
    --dry-run              Show what would be processed without doing it
    -v, --verbose          Show detailed information

Exit codes:
    0 = Success (all files processed or skipped)
    1 = Some files had errors

Examples:
    # Process all files in folder (skip already processed)
    python scripts/batch_process.py --folder /path/to/folder --language sv

    # Re-process all files (ignore existing ZIPs)
    python scripts/batch_process.py --folder /path/to/folder --force

    # Dry run (see what would be processed)
    python scripts/batch_process.py --folder /path/to/folder --dry-run
"""

import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Tuple


def find_markdown_files(folder: Path) -> List[Path]:
    """Find all markdown files in folder."""
    return sorted(folder.glob("*.md"))


def is_already_processed(markdown_file: Path, output_dir: Path) -> bool:
    """Check if markdown file has already been processed (ZIP exists)."""
    quiz_name = markdown_file.stem
    zip_path = output_dir / f"{quiz_name}.zip"
    return zip_path.exists()


def process_file(markdown_file: Path, output_dir: Path, language: str, verbose: bool) -> bool:
    """
    Process a single markdown file using run_all.py

    Returns:
        True if successful, False if error
    """
    cmd = [
        sys.executable,
        "scripts/run_all.py",
        str(markdown_file),
        "--output-dir", str(output_dir),
        "--language", language
    ]

    if verbose:
        cmd.append("--verbose")

    result = subprocess.run(cmd)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description='Batch process multiple markdown files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all files in folder (skip already processed)
  python scripts/batch_process.py --folder /path/to/folder --language sv

  # Re-process all files (ignore existing ZIPs)
  python scripts/batch_process.py --folder /path/to/folder --force

  # Dry run (see what would be processed)
  python scripts/batch_process.py --folder /path/to/folder --dry-run
        """
    )

    parser.add_argument(
        '--folder',
        type=str,
        help='Folder containing markdown files'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default=str(Path.home() / "Nextcloud" / "Inspera" / "QTI_export_INSPERA"),
        help='Output base directory (default: ~/Nextcloud/Inspera/QTI_export_INSPERA)'
    )

    parser.add_argument(
        '--language',
        type=str,
        default='sv',
        help='Question language code (default: sv)'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Re-process even if ZIP exists'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be processed without doing it'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed information'
    )

    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Interactive folder selection'
    )

    args = parser.parse_args()

    # Interactive mode
    if args.interactive:
        print("✗ Interactive mode not yet implemented", file=sys.stderr)
        print("  Use: python scripts/batch_process.py --folder <path>", file=sys.stderr)
        sys.exit(1)

    if not args.folder:
        print("✗ Error: --folder required", file=sys.stderr)
        print("  Use: python scripts/batch_process.py --folder <path>", file=sys.stderr)
        sys.exit(1)

    folder = Path(args.folder).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    if not folder.exists():
        print(f"✗ Error: Folder not found: {folder}", file=sys.stderr)
        sys.exit(1)

    if not folder.is_dir():
        print(f"✗ Error: Not a directory: {folder}", file=sys.stderr)
        sys.exit(1)

    # Find markdown files
    markdown_files = find_markdown_files(folder)

    if not markdown_files:
        print(f"✗ No markdown files found in: {folder}", file=sys.stderr)
        sys.exit(1)

    print("=" * 70)
    print("BATCH PROCESS QTI GENERATION")
    print("=" * 70)
    print(f"Folder:     {folder}")
    print(f"Output dir: {output_dir}")
    print(f"Language:   {args.language}")
    print(f"Found:      {len(markdown_files)} markdown files")
    print()

    # Categorize files
    to_process = []
    to_skip = []

    for md_file in markdown_files:
        if args.force or not is_already_processed(md_file, output_dir):
            to_process.append(md_file)
        else:
            to_skip.append(md_file)

    print(f"To process: {len(to_process)} files")
    if to_skip:
        print(f"To skip:    {len(to_skip)} files (already processed)")
        if args.verbose:
            for md_file in to_skip:
                print(f"  - {md_file.name}")
    print()

    if args.dry_run:
        print("DRY RUN - Would process:")
        for md_file in to_process:
            print(f"  ✓ {md_file.name}")
        print()
        print(f"Total: {len(to_process)} files to process, {len(to_skip)} to skip")
        return

    if not to_process:
        print("✓ All files already processed!")
        print("  Use --force to re-process")
        return

    # Process files
    processed = []
    errors = []

    for idx, md_file in enumerate(to_process, 1):
        print(f"[{idx}/{len(to_process)}] Processing: {md_file.name}")
        print("-" * 70)

        success = process_file(md_file, output_dir, args.language, args.verbose)

        if success:
            processed.append(md_file.name)
            print(f"✓ Success: {md_file.name}")
        else:
            errors.append(md_file.name)
            print(f"✗ Error: {md_file.name}")

        print()

    # Summary
    print("=" * 70)
    print("BATCH PROCESS COMPLETE")
    print("=" * 70)
    print(f"✓ Processed:  {len(processed)} files")
    if to_skip:
        print(f"⊘ Skipped:    {len(to_skip)} files (already processed)")
    if errors:
        print(f"✗ Errors:     {len(errors)} files")
        print()
        print("Files with errors:")
        for filename in errors:
            print(f"  - {filename}")

    print()
    print(f"Output directory: {output_dir}")
    print()

    if errors:
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAvbrutet av användare")
        sys.exit(130)
