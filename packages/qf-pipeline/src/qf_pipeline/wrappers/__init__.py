"""Wrappers for QTI-Generator-for-Inspera classes.

This module configures the Python path to import from QTI-Generator-for-Inspera
and exposes clean wrapper functions for the MCP tools.
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

# Export wrapper functions
from .parser import parse_markdown, parse_question, parse_file
from .generator import generate_xml, generate_all_xml, get_generator, get_supported_types
from .packager import create_qti_package, validate_package, inspect_package
from .validator import validate_markdown, validate_file
from .resources import (
    validate_resources,
    prepare_output_structure,
    copy_resources,
    get_supported_formats,
    get_max_file_size_mb,
)
from .errors import WrapperError, ParsingError, GenerationError, PackagingError, ValidationError, ResourceError

__all__ = [
    # Parser
    "parse_markdown",
    "parse_question",
    "parse_file",
    # Generator
    "generate_xml",
    "generate_all_xml",
    "get_generator",
    "get_supported_types",
    # Packager
    "create_qti_package",
    "validate_package",
    "inspect_package",
    # Validator
    "validate_markdown",
    "validate_file",
    # Resources
    "validate_resources",
    "prepare_output_structure",
    "copy_resources",
    "get_supported_formats",
    "get_max_file_size_mb",
    # Errors
    "WrapperError",
    "ParsingError",
    "GenerationError",
    "PackagingError",
    "ValidationError",
    "ResourceError",
]
