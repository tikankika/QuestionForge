"""Wrappers for QTI-Generator-for-Inspera classes.

This module configures the Python path to import from QTI-Generator-for-Inspera
and exposes clean wrapper functions for the MCP tools.

RFC-012 UPDATE (2026-01-24):
  - step2_validate and step4_export now use SUBPROCESS to call qti-core scripts
  - This guarantees consistency with manual terminal workflow
  - Archived wrappers (no longer used): validator.py, generator.py, packager.py, resources.py
  - Kept wrappers: parser.py (used by step1_* tools), errors.py
"""

import sys
from pathlib import Path

# QTI-Generator-for-Inspera location (now local as qti-core)
QTI_GENERATOR_PATH = Path(__file__).parent.parent.parent.parent.parent / "qti-core"

# Add to Python path if not already present
if str(QTI_GENERATOR_PATH) not in sys.path:
    sys.path.insert(0, str(QTI_GENERATOR_PATH))

# Verify the path exists
if not QTI_GENERATOR_PATH.exists():
    raise ImportError(
        f"QTI-Generator-for-Inspera not found at {QTI_GENERATOR_PATH}. "
        "Please update the path in wrappers/__init__.py"
    )

# =============================================================================
# ACTIVE WRAPPERS (still used)
# =============================================================================

# Parser - used by step1_* tools for guided build
from .parser import parse_markdown, parse_question, parse_file

# Errors - used for error handling
from .errors import WrapperError, ParsingError, GenerationError, PackagingError, ValidationError, ResourceError

# =============================================================================
# ARCHIVED WRAPPERS (RFC-012: replaced by subprocess)
# =============================================================================
# These are imported from _archived/ for backwards compatibility only.
# New code should NOT use these - use subprocess to call qti-core scripts instead.

from ._archived.validator import validate_markdown, validate_file
from ._archived.generator import get_supported_types

# NOTE: These are NO LONGER EXPORTED (fully obsolete):
# - generate_xml, generate_all_xml, get_generator (use step4_generate_xml.py)
# - create_qti_package, validate_package, inspect_package (use step5_create_zip.py)
# - validate_resources, copy_resources, etc. (use step3_copy_resources.py)

__all__ = [
    # Parser (ACTIVE - used by step1_*)
    "parse_markdown",
    "parse_question",
    "parse_file",
    # Validator (ARCHIVED - only validate_markdown used by step2_validate_content)
    "validate_markdown",
    "validate_file",  # Deprecated, kept for compatibility
    # Generator (ARCHIVED - only get_supported_types used by list_types)
    "get_supported_types",
    # Errors
    "WrapperError",
    "ParsingError",
    "GenerationError",
    "PackagingError",
    "ValidationError",
    "ResourceError",
]
