#!/usr/bin/env python3
"""
QTI Generator for Inspera - Development Entry Point

This is a convenience wrapper for development. For production use,
install the package and use the 'qti-gen' command:

    pip install .
    qti-gen quiz.md output.zip

For development, you can run this script directly:

    python main.py quiz.md output.zip
"""

from src.cli import main

if __name__ == '__main__':
    main()
