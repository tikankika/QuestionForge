# QF-Pipeline Wrapper Specification

**Version:** 1.0  
**Status:** Draft  
**Date:** 2026-01-05  
**Source:** Analysis of QTI-Generator-for-Inspera codebase

---

## Overview

This document specifies how qf-pipeline wraps the existing QTI-Generator-for-Inspera code. The wrapper provides a clean MCP interface while reusing proven Python implementations.

---

## Source Code Analysis

### Directory Structure (QTI-Generator-for-Inspera)

```
QTI-Generator-for-Inspera/
├── src/
│   ├── __init__.py
│   ├── cli.py                          # CLI entry point
│   ├── error_handler.py                # Error handling utilities
│   ├── parser/
│   │   ├── __init__.py
│   │   └── markdown_parser.py          # MarkdownQuizParser class (~1900 lines)
│   ├── generator/
│   │   ├── __init__.py
│   │   ├── xml_generator.py            # XMLGenerator class
│   │   ├── resource_manager.py         # ResourceManager class
│   │   └── assessment_test_generator.py
│   └── packager/
│       ├── __init__.py
│       └── qti_packager.py             # QTIPackager class
├── templates/xml/                       # 20 QTI XML templates
├── validate_mqg_format.py              # Format validation script
└── main.py                              # Entry point
```

---

## Core Classes to Wrap

### 1. MarkdownQuizParser

**Location:** `src/parser/markdown_parser.py`

**Purpose:** Parse markdown questions into structured data

**Key Methods:**
```python
class MarkdownQuizParser:
    def __init__(self, markdown_content: str)
    def parse(self) -> Dict[str, Any]
        # Returns: {
        #     'metadata': {...},      # Test-level config from YAML frontmatter
        #     'questions': [...]      # List of parsed question dicts
        # }
```

**Wrapper Interface:**
```python
# In qf-pipeline/wrappers/parser.py
from src.parser.markdown_parser import MarkdownQuizParser

def parse_markdown(content: str) -> dict:
    """Parse markdown content into structured data."""
    parser = MarkdownQuizParser(content)
    return parser.parse()

def parse_question(content: str) -> dict:
    """Parse a single question block."""
    parser = MarkdownQuizParser(content)
    result = parser.parse()
    if result['questions']:
        return result['questions'][0]
    return None
```

---

### 2. XMLGenerator

**Location:** `src/generator/xml_generator.py`

**Purpose:** Generate QTI XML from parsed question data

**Key Methods:**
```python
class XMLGenerator:
    def __init__(self, templates_dir: str = None)
    def generate_question(self, question_data: Dict, language: str = 'en') -> str
        # Returns: Complete QTI XML string for one question
```

**Supported Question Types:**
| Type | Status | Template |
|------|--------|----------|
| `multiple_choice_single` | ✅ Production | `multiple_choice_single.xml` |
| `multiple_response` | ✅ Production | `multiple_response.xml` |
| `true_false` | ✅ Production | `true_false.xml` |
| `text_entry` | ✅ Production | `text_entry.xml` |
| `text_entry_numeric` | ✅ Production | `text_entry_numeric.xml` |
| `text_entry_math` | ✅ Production | `text_entry_math.xml` |
| `inline_choice` | ✅ Production | `inline_choice.xml` |
| `match` | ✅ Production | `match.xml` |
| `hotspot` | ✅ Production | `hotspot.xml` |
| `graphicgapmatch_v2` | ✅ Production | `graphicgapmatch_v2.xml` |
| `text_area` | ✅ Production | `text_area.xml` |
| `essay` | ✅ Production | `essay.xml` |
| `audio_record` | ✅ Production | `audio_record.xml` |
| `composite_editor` | ⚠️ Stub | `composite_editor.xml` |
| `nativehtml` | ✅ Production | `nativehtml.xml` |

**Wrapper Interface:**
```python
# In qf-pipeline/wrappers/generator.py
from src.generator.xml_generator import XMLGenerator

_generator = None

def get_generator() -> XMLGenerator:
    """Get singleton XMLGenerator instance."""
    global _generator
    if _generator is None:
        _generator = XMLGenerator()
    return _generator

def generate_xml(question_data: dict, language: str = 'sv') -> str:
    """Generate QTI XML for a single question."""
    return get_generator().generate_question(question_data, language)

def generate_all_xml(questions: list, language: str = 'sv') -> list:
    """Generate QTI XML for all questions.
    
    Returns: List of (identifier, xml_content) tuples
    """
    gen = get_generator()
    result = []
    for q in questions:
        xml = gen.generate_question(q, language)
        result.append((q.get('identifier', 'Q001'), xml))
    return result
```

---

### 3. QTIPackager

**Location:** `src/packager/qti_packager.py`

**Purpose:** Create IMS Content Package (ZIP) with manifest

**Key Methods:**
```python
class QTIPackager:
    def __init__(self, output_dir: str = None)
    
    def create_package(
        self,
        questions_xml: List[tuple[str, str]],  # (identifier, xml_content)
        metadata: Dict[str, Any],
        output_filename: str,
        keep_folder: bool = True,
        base_dir: Optional[str] = None,
        assessment_test_xml: Optional[str] = None
    ) -> Dict[str, str]
        # Returns: {
        #     'zip_path': str,      # Path to created ZIP
        #     'folder_path': str    # Path to extracted folder (if kept)
        # }
    
    def validate_package(self, package_dir: Path) -> Dict[str, Any]
        # Returns: {
        #     'valid': bool,
        #     'issues': list,
        #     'warnings': list
        # }
    
    def get_package_tree(self, package_path: str) -> str
        # Returns: Tree view string of package contents
```

**Wrapper Interface:**
```python
# In qf-pipeline/wrappers/packager.py
from src.packager.qti_packager import QTIPackager

def create_qti_package(
    questions_xml: list,
    metadata: dict,
    output_path: str,
    keep_folder: bool = True
) -> dict:
    """Create QTI package from generated XML."""
    packager = QTIPackager()
    return packager.create_package(
        questions_xml,
        metadata,
        output_path,
        keep_folder=keep_folder
    )

def validate_package(package_path: str) -> dict:
    """Validate existing QTI package."""
    packager = QTIPackager()
    from pathlib import Path
    return packager.validate_package(Path(package_path))

def inspect_package(package_path: str) -> str:
    """Get tree view of package contents."""
    packager = QTIPackager()
    return packager.get_package_tree(package_path)
```

---

### 4. ResourceManager

**Location:** `src/generator/resource_manager.py`

**Purpose:** Handle images and media files

**Key Methods:**
```python
class ResourceManager:
    def __init__(
        self,
        input_file: Path,
        output_dir: Path,
        media_dir: Path = None,
        strict: bool = False
    )
    
    def validate_resources(self, questions: list) -> list
        # Returns: List of ResourceIssue objects
    
    def prepare_output_structure(self, quiz_name: str) -> Path
        # Returns: Path to quiz directory
    
    def copy_resources(self, questions: list, output_dir: Path) -> dict
        # Returns: {original_name: renamed_name} mapping
```

**Wrapper Interface:**
```python
# In qf-pipeline/wrappers/resources.py
from src.generator.resource_manager import ResourceManager

def validate_resources(
    input_file: str,
    questions: list,
    media_dir: str = None,
    strict: bool = False
) -> dict:
    """Validate media resources referenced in questions."""
    from pathlib import Path
    rm = ResourceManager(
        input_file=Path(input_file),
        output_dir=Path('.'),
        media_dir=Path(media_dir) if media_dir else None,
        strict=strict
    )
    issues = rm.validate_resources(questions)
    return {
        'valid': not any(i.level == 'ERROR' for i in issues),
        'issues': [{'level': i.level, 'message': str(i)} for i in issues]
    }
```

---

### 5. Format Validator

**Location:** `validate_mqg_format.py`

**Purpose:** Validate markdown format before processing

**Key Function:**
```python
def validate_content(content: str) -> tuple[bool, list]:
    """Validate markdown content.
    
    Returns: (is_valid, list_of_issues)
    """
```

**Wrapper Interface:**
```python
# In qf-pipeline/wrappers/validator.py
from validate_mqg_format import validate_content

def validate_markdown(content: str) -> dict:
    """Validate markdown format."""
    is_valid, issues = validate_content(content)
    return {
        'valid': is_valid,
        'issues': [
            {
                'level': i.level,
                'question_num': i.question_num,
                'question_id': i.question_id,
                'message': i.message,
                'line_num': i.line_num
            }
            for i in issues
        ]
    }
```

---

## MCP Tool → Wrapper Mapping

| MCP Tool | Wrapper Function | QTI-Generator Class |
|----------|------------------|---------------------|
| `start_build_session` | `parse_markdown()` | `MarkdownQuizParser` |
| `get_question` | `parse_question()` | `MarkdownQuizParser` |
| `get_question_spec` | (reads from qf-specifications) | N/A |
| `compare_to_spec` | Custom logic + `validate_markdown()` | `validate_content` |
| `validate_file` | `validate_markdown()` | `validate_content` |
| `validate_question` | `validate_markdown()` (single) | `validate_content` |
| `export_questions` | `generate_xml()` + `create_qti_package()` | `XMLGenerator` + `QTIPackager` |
| `generate_qti_package` | `create_qti_package()` | `QTIPackager` |

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    qf-pipeline MCP                               │
├─────────────────────────────────────────────────────────────────┤
│  tools/                                                          │
│  ├── build_session.py ──────┐                                   │
│  ├── validator.py ──────────┼───────┐                           │
│  ├── decision.py ───────────┤       │                           │
│  └── exporter.py ───────────┘       │                           │
│           │                          │                           │
│           ▼                          ▼                           │
│  wrappers/                    qf-specifications/                 │
│  ├── parser.py               ├── question-types/*.md            │
│  ├── generator.py            ├── metadata-schema.json           │
│  ├── packager.py             └── platforms/inspera/             │
│  ├── resources.py                                                │
│  └── validator.py                                                │
│           │                                                      │
└───────────┼──────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│              QTI-Generator-for-Inspera (Existing)                │
├─────────────────────────────────────────────────────────────────┤
│  src/parser/           src/generator/        src/packager/       │
│  └── MarkdownQuiz      ├── XMLGenerator      └── QTIPackager     │
│      Parser            └── ResourceManager                       │
│                                                                  │
│  templates/xml/        validate_mqg_format.py                    │
│  └── *.xml (20)        └── validate_content()                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Notes

### Python Path Configuration

qf-pipeline needs QTI-Generator on its Python path:

```python
# In qf-pipeline/wrappers/__init__.py
import sys
from pathlib import Path

# Add QTI-Generator to path
QTI_GENERATOR_PATH = Path(__file__).parent.parent.parent.parent / 'QTI-Generator-for-Inspera'
if str(QTI_GENERATOR_PATH) not in sys.path:
    sys.path.insert(0, str(QTI_GENERATOR_PATH))
```

### Error Handling

Wrap QTI-Generator exceptions in MCP-friendly formats:

```python
# In qf-pipeline/wrappers/errors.py
class WrapperError(Exception):
    """Base exception for wrapper errors."""
    def __init__(self, message: str, source_error: Exception = None):
        super().__init__(message)
        self.source_error = source_error

class ParsingError(WrapperError):
    """Error during markdown parsing."""
    pass

class GenerationError(WrapperError):
    """Error during XML generation."""
    pass

class PackagingError(WrapperError):
    """Error during package creation."""
    pass
```

### Template Access

XMLGenerator expects templates at `templates/xml/`. Configure path:

```python
# Option 1: Use QTI-Generator's templates (recommended)
generator = XMLGenerator()  # Auto-detects project root

# Option 2: Specify custom path
generator = XMLGenerator(templates_dir='/path/to/templates/xml')
```

---

## Testing Strategy

### Unit Tests

```python
# tests/wrappers/test_parser.py
def test_parse_markdown():
    content = """---
test_metadata:
  title: Test Quiz
---
# Q001 Test Question
^type multiple_choice_single
...
"""
    result = parse_markdown(content)
    assert 'questions' in result
    assert len(result['questions']) == 1
```

### Integration Tests

```python
# tests/integration/test_full_pipeline.py
def test_full_export():
    # Parse → Generate → Package
    data = parse_markdown(test_content)
    xml_list = generate_all_xml(data['questions'])
    result = create_qti_package(xml_list, data['metadata'], 'test.zip')
    assert Path(result['zip_path']).exists()
```

---

## Migration Checklist

- [ ] Create `qf-pipeline/wrappers/` directory
- [ ] Implement `parser.py` wrapper
- [ ] Implement `generator.py` wrapper
- [ ] Implement `packager.py` wrapper
- [ ] Implement `resources.py` wrapper
- [ ] Implement `validator.py` wrapper
- [ ] Configure Python path for QTI-Generator
- [ ] Write unit tests for each wrapper
- [ ] Write integration tests
- [ ] Document any QTI-Generator modifications needed

---

## Format Version Compatibility

QTI-Generator currently supports markdown format v6.5:

```markdown
# Q001 Title
^question Q001
^type multiple_choice_single
^identifier MC_Q001
^points 1
^labels #label1 #label2

@field: question_text
Content...
@end_field

@field: options
A. Option 1
B. Option 2
@end_field

@field: feedback
@@field: general_feedback
...
@@end_field
@end_field
```

This format is defined in qf-specifications as `question-format-v7.md`.

---

*Specification v1.0 | QuestionForge | 2026-01-05*
