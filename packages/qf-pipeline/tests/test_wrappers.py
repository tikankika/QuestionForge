"""Tests for qf-pipeline wrappers.

These tests verify that the wrappers correctly interface with QTI-Generator-for-Inspera.
"""

import pytest
from pathlib import Path
import tempfile
import os

# Sample markdown content for testing
SAMPLE_MARKDOWN = '''---
test_metadata:
  title: Test Quiz
  description: A test quiz for validation
---

# Q001 Sample Multiple Choice Question
^question Q001
^type multiple_choice_single
^identifier MC_Q001
^points 1

@field: question_text
What is 2 + 2?
@end_field

@field: options
*A. 3
A. 4
A. 5
A. 6
@end_field

@field: feedback
@@field: general_feedback
The answer is 4.
@@end_field
@end_field
'''

SAMPLE_QUESTION_ONLY = '''# Q001 Test Question
^question Q001
^type multiple_choice_single
^identifier MC_TEST
^points 1

@field: question_text
Test question text
@end_field

@field: options
*A. Correct
A. Wrong
@end_field
'''


class TestParser:
    """Tests for parser wrapper."""

    def test_parse_markdown_returns_dict(self):
        """parse_markdown should return a dictionary."""
        from qf_pipeline.wrappers import parse_markdown

        result = parse_markdown(SAMPLE_MARKDOWN)
        assert isinstance(result, dict)

    def test_parse_markdown_has_questions(self):
        """parse_markdown should extract questions."""
        from qf_pipeline.wrappers import parse_markdown

        result = parse_markdown(SAMPLE_MARKDOWN)
        assert "questions" in result
        assert len(result["questions"]) >= 1

    def test_parse_markdown_has_metadata(self):
        """parse_markdown should extract metadata."""
        from qf_pipeline.wrappers import parse_markdown

        result = parse_markdown(SAMPLE_MARKDOWN)
        assert "metadata" in result

    def test_parse_question_single(self):
        """parse_question should return a single question dict."""
        from qf_pipeline.wrappers import parse_question

        result = parse_question(SAMPLE_QUESTION_ONLY)
        assert result is not None
        assert isinstance(result, dict)

    def test_parse_file_not_found(self):
        """parse_file should raise ParsingError for missing file."""
        from qf_pipeline.wrappers import parse_file, ParsingError

        with pytest.raises(ParsingError):
            parse_file("/nonexistent/path/to/file.md")


class TestGenerator:
    """Tests for generator wrapper."""

    def test_get_supported_types(self):
        """get_supported_types should return a list."""
        from qf_pipeline.wrappers import get_supported_types

        types = get_supported_types()
        assert isinstance(types, list)
        assert "multiple_choice_single" in types
        assert "multiple_response" in types
        assert len(types) >= 10

    def test_get_generator_singleton(self):
        """get_generator should return the same instance."""
        from qf_pipeline.wrappers import get_generator

        gen1 = get_generator()
        gen2 = get_generator()
        assert gen1 is gen2

    def test_generate_xml_returns_string(self):
        """generate_xml should return XML string."""
        from qf_pipeline.wrappers import parse_markdown, generate_xml

        data = parse_markdown(SAMPLE_MARKDOWN)
        if data["questions"]:
            question = data["questions"][0]
            xml = generate_xml(question, language="sv")
            assert isinstance(xml, str)
            assert "<?xml" in xml or "<assessmentItem" in xml

    def test_generate_all_xml_returns_list(self):
        """generate_all_xml should return list of tuples."""
        from qf_pipeline.wrappers import parse_markdown, generate_all_xml

        data = parse_markdown(SAMPLE_MARKDOWN)
        xml_list = generate_all_xml(data["questions"], language="sv")
        assert isinstance(xml_list, list)
        if xml_list:
            assert isinstance(xml_list[0], tuple)
            assert len(xml_list[0]) == 2  # (identifier, xml)


class TestValidator:
    """Tests for validator wrapper."""

    def test_validate_markdown_returns_dict(self):
        """validate_markdown should return validation result dict."""
        from qf_pipeline.wrappers import validate_markdown

        result = validate_markdown(SAMPLE_MARKDOWN)
        assert isinstance(result, dict)
        assert "valid" in result
        assert "issues" in result

    def test_validate_markdown_issues_format(self):
        """validate_markdown issues should have expected fields."""
        from qf_pipeline.wrappers import validate_markdown

        result = validate_markdown(SAMPLE_MARKDOWN)
        for issue in result.get("issues", []):
            assert "level" in issue
            assert "message" in issue


class TestPackager:
    """Tests for packager wrapper."""

    def test_create_qti_package_integration(self):
        """Full integration test: parse -> generate -> package."""
        from qf_pipeline.wrappers import (
            parse_markdown,
            generate_all_xml,
            create_qti_package,
        )

        # Parse
        data = parse_markdown(SAMPLE_MARKDOWN)
        assert data["questions"], "No questions parsed"

        # Generate
        xml_list = generate_all_xml(data["questions"], language="sv")
        assert xml_list, "No XML generated"

        # Package
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_package.zip")
            result = create_qti_package(
                xml_list,
                data.get("metadata", {}),
                output_path,
                keep_folder=True,
            )

            assert "zip_path" in result
            assert Path(result["zip_path"]).exists()


class TestResources:
    """Tests for resources wrapper."""

    def test_get_supported_formats(self):
        """get_supported_formats should return list of extensions."""
        from qf_pipeline.wrappers import get_supported_formats

        formats = get_supported_formats()
        assert isinstance(formats, list)
        assert ".png" in formats
        assert ".jpg" in formats

    def test_get_max_file_size_mb(self):
        """get_max_file_size_mb should return Inspera limit."""
        from qf_pipeline.wrappers import get_max_file_size_mb

        size = get_max_file_size_mb()
        assert isinstance(size, int)
        assert size == 5  # Inspera limit is 5 MB

    def test_validate_resources_returns_dict(self):
        """validate_resources should return validation result dict."""
        from qf_pipeline.wrappers import parse_markdown, validate_resources

        data = parse_markdown(SAMPLE_MARKDOWN)

        # Create a temp file to use as input_file
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            f.write(SAMPLE_MARKDOWN.encode())
            temp_path = f.name

        try:
            result = validate_resources(
                input_file=temp_path,
                questions=data["questions"],
            )
            assert isinstance(result, dict)
            assert "valid" in result
            assert "issues" in result
            assert "error_count" in result
            assert "warning_count" in result
        finally:
            os.unlink(temp_path)

    def test_resource_error_inheritance(self):
        """ResourceError should inherit from WrapperError."""
        from qf_pipeline.wrappers import WrapperError, ResourceError

        assert issubclass(ResourceError, WrapperError)


class TestErrors:
    """Tests for error classes."""

    def test_wrapper_error_to_dict(self):
        """WrapperError should convert to dict."""
        from qf_pipeline.wrappers import WrapperError

        err = WrapperError("Test error", source_error=ValueError("source"))
        d = err.to_dict()
        assert d["error"] == "WrapperError"
        assert d["message"] == "Test error"
        assert "source" in d

    def test_error_inheritance(self):
        """Custom errors should inherit from WrapperError."""
        from qf_pipeline.wrappers import (
            WrapperError,
            ParsingError,
            GenerationError,
            PackagingError,
            ResourceError,
        )

        assert issubclass(ParsingError, WrapperError)
        assert issubclass(GenerationError, WrapperError)
        assert issubclass(PackagingError, WrapperError)
        assert issubclass(ResourceError, WrapperError)
