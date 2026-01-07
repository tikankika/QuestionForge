# QTI Generator Development Plan

## Project Overview

### Goal
Develop a Python-based tool that converts Excel files to QTI 2.2 format for import into the Inspera Assessment Platform.

### Background
- **Problem**: Manual creation of questions in Inspera is time-consuming
- **Solution**: Automate the process by creating questions in Excel and converting to QTI 2.2
- **Use Case**: Import PDFs and images as questions in Inspera

### Project Scope
1. Excel template for data input
2. Python script for conversion
3. QTI 2.2 XML generation with Inspera compatibility
4. Packaging for import

### Project Uniqueness
- **First open-source Inspera QTI generator**: No existing tools currently support the Inspera assessment platform
- **Market Gap**: Current QTI tools (qti-package-maker, text2qti, and others) exclusively support Canvas, Moodle, or Blackboard platforms
- **Strategic Opportunity**: Position as the standard solution for Inspera users internationally

---

## Competition Analysis

### Existing QTI Tools Evaluation

A comprehensive analysis was conducted of existing QTI generation tools to assess their compatibility with the Inspera assessment platform. The following findings summarize the evaluation:

#### 1. **qti-package-maker** (PyPI)
- **Platforms**: Canvas (QTI 1.2), Blackboard (QTI 2.1), LibreTexts ADAPT, Moodle
- **Inspera Support**: None
- **Limitations**:
  - Incompatible QTI version (2.1 versus 2.2 required)
  - Lacks capability to read or parse existing QTI files
  - Absence of Inspera namespace support
- **Assessment**: Not suitable for Inspera implementation

#### 2. **text2qti** (GitHub/PyPI)
- **Platforms**: Canvas (QTI 1.2)
- **Inspera Support**: None
- **Limitations**:
  - Canvas-specific implementation
  - Limited to QTI 1.2 (Inspera requires 2.2)
  - Divergent XML structure
- **Assessment**: Not suitable for Inspera implementation

#### 3. **qti2txt** (GitHub)
- **Purpose**: Convert Canvas QTI exports to plaintext format
- **Inspera Support**: None
- **Limitations**: Canvas-specific functionality, reverse conversion only
- **Assessment**: Not suitable for Inspera implementation

#### 4. **Other Tools**
- **Learnosity QTI**: Proprietary format conversion
- **Citolab qti-convert**: QTI 2 to QTI 3 (not Inspera)
- **Commercial tools**: Respondus, ExamView (no Inspera support)

### Market Opportunity

**Principal Finding**: No existing open-source tool currently supports Inspera QTI generation.

This finding represents a significant market opportunity based on the following factors:
- Inspera maintains substantial market presence in Nordic countries with expanding global adoption
- Educational institutions require efficient question creation and management tools
- Current manual question creation workflows are resource-intensive and time-consuming
- This tool would represent the first open-source solution for Inspera users

### Rationale for Custom Development

1. **Technical Incompatibility**
   - Inspera utilizes QTI 2.2 with proprietary namespace implementations
   - Existing tools target different QTI version specifications
   - XML structure requirements differ substantially from other platforms

2. **Development Efficiency Analysis**
   - Modification of existing tools would necessitate comprehensive architectural changes
   - Custom development provides cleaner implementation and improved maintainability
   - Direct conversion pathway from Excel to Inspera QTI 2.2 format

3. **Strategic Advantages**
   - Complete control over Inspera-specific feature implementation
   - Optimization specifically for Inspera workflow requirements
   - Potential for future expansion to support additional platforms (Canvas, Moodle)

---

## Revised Project Architecture

### Overview

This project implements a two-phase workflow for generating QTI 2.2 packages for the Inspera assessment platform:

**Phase 1: Manual Preparation** (Claude Desktop)
- Question generation with theoretical grounding
- Structured markdown output with complete metadata

**Phase 2: Automated Pipeline** (Python)
- Markdown → XML → QTI ZIP conversion
- Template-based XML generation
- Validation and packaging

### Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Manual Preparation (Claude Desktop)                │
├─────────────────────────────────────────────────────────────┤
│ 1. Test Planning                                            │
│    - Define purpose (formative/summative)                   │
│    - Map learning objectives                                │
│    - Plan question distribution (Bloom's levels)            │
│                                                              │
│ 2. Question Generation                                      │
│    - AI-assisted question writing                           │
│    - Plausible distractor development                       │
│    - Feedback structure creation                            │
│                                                              │
│ 3. Structured Output                                        │
│    - Export to .md file                                     │
│    - Include all metadata                                   │
│    - Validate completeness                                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Automated Pipeline (Python Script)                 │
├─────────────────────────────────────────────────────────────┤
│ 1. Markdown Parser                                          │
│    → Parse .md file                                         │
│    → Extract questions and metadata                         │
│    → Validate structure                                     │
│                                                              │
│ 2. XML Generator                                            │
│    → Apply QTI 2.2 templates                               │
│    → Insert question data                                   │
│    → Add Inspera namespaces                                 │
│                                                              │
│ 3. Package Builder                                          │
│    → Create folder structure                                │
│    → Generate imsmanifest.xml                              │
│    → Build ZIP package                                      │
│                                                              │
│ 4. Validation                                               │
│    → Verify QTI 2.2 compliance                             │
│    → Check Inspera requirements                             │
│    → Generate validation report                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    QTI Package Ready for Inspera
```

### Theoretical Foundation

This implementation integrates three pedagogical frameworks:

#### 1. Bloom's Taxonomy (Anderson & Krathwohl, 2001)
Questions are classified by cognitive level:
- **Remember**: Recall facts, terms, concepts
- **Understand**: Explain ideas or concepts
- **Apply**: Use information in new situations
- **Analyze**: Draw connections among ideas
- **Evaluate**: Justify a decision or course of action
- **Create**: Produce new or original work

Each question includes Bloom's level metadata for systematic test construction and validation of cognitive level distribution.

#### 2. Test-Based Learning (Roediger & Karpicke, 2006)
Leverages the testing effect:
- Retrieval practice enhances long-term retention
- Frequent low-stakes testing supports learning
- Feedback mechanisms reinforce correct understanding
- Distributed practice through systematic question design

#### 3. Constructive Alignment (Biggs & Tang, 2011)
Ensures coherence across:
- **Learning Objectives**: What students should achieve
- **Assessment Tasks**: Questions that measure those objectives
- **Cognitive Levels**: Alignment between objective complexity and question difficulty

The system enforces alignment through:
- Explicit objective-to-question mapping
- Coverage completeness checks
- Cognitive level distribution analysis

### Project Structure

```
QTI-Generator-for-Inspera/
├── docs/                              # Documentation
│   ├── theoretical_framework.md       # Detailed pedagogical foundation
│   ├── markdown_specification.md      # Complete .md format specification
│   └── workflow.md                    # Step-by-step usage guide
├── templates/                         # All template files
│   ├── markdown/                      # Templates for Claude Desktop
│   │   ├── test_planning.md          # Test configuration template
│   │   ├── question_template.md      # Question generation guide
│   │   └── metadata_structure.md     # Metadata conventions
│   └── xml/                          # QTI XML templates
│       ├── multiple_choice.xml       # Single correct answer
│       ├── multiple_response.xml     # Multiple correct answers
│       ├── text_entry.xml            # Fill-in-the-blank
│       └── manifest_template.xml     # IMS manifest structure
├── src/                               # Python source code
│   ├── parser/                        # Markdown parsing module
│   │   ├── __init__.py
│   │   └── md_parser.py
│   ├── generator/                     # XML generation module
│   │   ├── __init__.py
│   │   └── xml_generator.py
│   ├── packager/                      # QTI packaging module
│   │   ├── __init__.py
│   │   └── qti_packager.py
│   ├── validator/                     # Validation module
│   │   ├── __init__.py
│   │   └── qti_validator.py
│   └── main.py                       # Command-line interface
├── tests/                             # Test files and examples
│   ├── sample_input/                 # Example .md files
│   └── sample_output/                # Expected QTI packages
├── output/                            # Generated QTI packages
├── QTI_test1/                        # Reference Inspera exports
├── development_plan.md               # This document
└── README.md                         # Project overview
```

---

## Technical Analysis

### QTI 2.2 Structure in Inspera

#### File Structure for QTI Package
```
QTI_Package/
├── imsmanifest.xml              # Package manifest with metadata
├── ID_[number]-item.xml         # Individual question files
├── ID_[number]-assessment.xml   # Assessment file (for multiple questions)
└── resources/                   # Folder for images and media
    ├── ID_[number].jpg
    └── ID_[number].png
```

#### XML Namespace and Schema

**Important Note**: The following are XML namespace declarations, not web URLs. These URIs serve as unique identifiers for XML schemas and do not need to resolve to actual web pages.

```xml
<!-- Inspera namespace declarations (required for proper functionality) -->
xmlns="http://www.imsglobal.org/xsd/imsqti_v2p2"
xmlns:inspera="http://www.inspera.no/qti"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
```

These namespace declarations:
- **xmlns**: Default namespace for QTI 2.2 standard elements
- **xmlns:inspera**: Inspera-specific extensions and attributes
- **xmlns:xsi**: XML Schema Instance namespace for schema validation

#### Required QTI Elements

1. **assessmentItem** (root element)
```xml
<assessmentItem
    identifier="421824545"
    title="Question Title"
    inspera:objectType="content_question_qti2_multiple_choice"
    adaptive="false"
    timeDependent="false">
```

2. **responseDeclaration** (defines correct answer)
```xml
<responseDeclaration identifier="RESPONSE" cardinality="single" baseType="identifier">
    <correctResponse>
        <value>rId1</value>
    </correctResponse>
    <mapping defaultValue="0">
        <mapEntry mapKey="rId1" mappedValue="1"/>
    </mapping>
</responseDeclaration>
```

3. **outcomeDeclaration** (score handling)
```xml
<outcomeDeclaration identifier="SCORE" cardinality="single" baseType="float">
    <defaultValue><value>0</value></defaultValue>
</outcomeDeclaration>
```

4. **templateDeclaration** (scoring settings)
```xml
<templateDeclaration identifier="SCORE_EACH_CORRECT" baseType="float" cardinality="single">
    <defaultValue><value>1</value></defaultValue>
</templateDeclaration>
```

5. **itemBody** (question content)
```xml
<itemBody inspera:defaultLanguage="sv_se" inspera:supportedLanguages="sv_se">
    <p>Question text here</p>
    <choiceInteraction responseIdentifier="RESPONSE" shuffle="true" maxChoices="1">
        <simpleChoice identifier="rId0"><p>Answer option 1</p></simpleChoice>
        <simpleChoice identifier="rId1"><p>Answer option 2</p></simpleChoice>
    </choiceInteraction>
</itemBody>
```

### Inspera-specific Features

#### Configuration Options (from screenshot analysis)
1. **Scoring**
   - Standard or per alternative
   - Points for correct answer (default: 1)
   - Points for incorrect answer (default: 0)
   - Points for unanswered (default: 0)
   - Min/max score boundaries

2. **Display Settings**
   - Random order of alternatives
   - Layout (vertical/horizontal)
   - Language settings

3. **Feedback**
   - Per answer alternative
   - Task level
   - Different for correct/incorrect/unanswered

4. **Media and Attachments**
   - Main illustration
   - PDF panel
   - Inline images in text

5. **Metadata**
   - Labels (tags)
   - Content type
   - Language

---

## Excel Template Structure

### Version 1: Minimal (for quick start)

| Column | Description | Example |
|--------|-------------|---------|
| question_id | Unique identifier | TRA265L1a1Q1 |
| question_text | Question text (HTML allowed) | Which factor affects most...? |
| answer_1 | Answer option 1 | Vehicle weight |
| answer_2 | Answer option 2 | Electricity mix in charging region |
| answer_3 | Answer option 3 | Ambient temperature |
| answer_4 | Answer option 4 | Driving speed |
| correct_answer | Correct answer (1-4) | 2 |
| tags | Labels (comma-separated) | TRA265,L1,environment |

### Version 2: Extended (all features)

| Column | Description | Required |
|--------|-------------|----------|
| **Basic** |  |  |
| question_id | Unique identifier | Yes |
| question_title | Short title | Yes |
| question_text | Full question text | Yes |
| question_type | Question type | Yes |
| language | Language code (sv_se, en_us) | No (default: sv_se) |
| **Answer Options** (repeat for each option) |  |  |
| answer_X_text | Text for option X | Yes |
| answer_X_correct | TRUE/FALSE | Yes |
| answer_X_feedback | Feedback for option | No |
| answer_X_image | Image filename | No |
| **Scoring** |  |  |
| score_correct | Points for correct answer | No (default: 1) |
| score_incorrect | Points for incorrect answer | No (default: 0) |
| score_unanswered | Points for unanswered | No (default: 0) |
| score_minimum | Minimum possible score | No |
| score_maximum | Maximum possible score | No |
| **Display** |  |  |
| shuffle_answers | TRUE/FALSE | No (default: TRUE) |
| answer_layout | vertical/horizontal | No (default: vertical) |
| **Feedback** |  |  |
| feedback_correct | Feedback for correct answer | No |
| feedback_incorrect | Feedback for incorrect answer | No |
| feedback_unanswered | Feedback for unanswered | No |
| **Media** |  |  |
| main_illustration | Main image filename | No |
| pdf_attachment | PDF attachment filename | No |
| **Metadata** |  |  |
| tags | Labels (comma-separated) | No |
| instruction_text | Instruction text | No |

---

## Development Roadmap

### Week 1: Foundation and Templates

**Objective**: Establish theoretical foundation, define specifications, and create all templates

#### Day 1-2: Documentation Foundation
- **Create**: `docs/theoretical_framework.md`
  - Bloom's Taxonomy application guidelines
  - Test-Based Learning principles
  - Constructive Alignment methodology
  - Integration framework for all three theories
- **Create**: `docs/markdown_specification.md`
  - Complete .md format specification
  - Field definitions and requirements
  - Examples for each question type
  - Metadata structure documentation

#### Day 3-4: Template Development
- **Create**: `templates/markdown/`
  - `test_planning.md`: Test configuration template
  - `question_template.md`: Question generation guide with theoretical grounding
  - `metadata_structure.md`: Naming conventions and categorization
- **Create**: `templates/xml/multiple_choice.xml`
  - Complete QTI 2.2 structure
  - Inspera namespace implementation
  - All scoring configuration options
  - Feedback structure

#### Day 5-7: Manual Workflow Validation
- Generate 5 sample questions using Claude Desktop
- Create complete .md file following specification
- Manually convert one question to XML
- Package and test import in Inspera
- Document issues and refine templates

**Deliverables**:
- Comprehensive documentation (theory + specifications)
- Complete template library
- Validated manual workflow
- Sample test data

### Week 2: Core Automation Implementation

**Objective**: Build functional Python pipeline for .md → XML → ZIP conversion

#### Day 1-2: Environment and Parser
- Set up Python virtual environment
- Install dependencies: `lxml`, `pyyaml`, `markdown2`
- **Build**: `src/parser/md_parser.py`
  - Parse structured markdown
  - Extract test configuration
  - Extract question data and metadata
  - Validate structure against specification

#### Day 3-4: XML Generator
- **Build**: `src/generator/xml_generator.py`
  - Load XML templates
  - Populate templates with question data
  - Apply Inspera namespaces correctly
  - Generate valid QTI 2.2 XML
- Test with sample data from Week 1

#### Day 5-7: Package Builder and Integration
- **Build**: `src/packager/qti_packager.py`
  - Create QTI folder structure
  - Generate imsmanifest.xml
  - Bundle resources
  - Create ZIP package
- **Build**: `src/main.py`
  - Command-line interface
  - Connect all modules
  - Basic error handling
- End-to-end test: .md → QTI package

**Deliverables**:
- Functional Python modules
- Command-line tool
- First automatically-generated QTI package
- Successful Inspera import

### Week 3: Enhancement and Validation

**Objective**: Add robustness, additional question types, and validation

#### Day 1-2: Validation Module
- **Build**: `src/validator/qti_validator.py`
  - XML schema validation
  - Inspera requirement checks
  - Alignment validation (objectives ↔ questions)
  - Bloom's level distribution analysis
- Generate validation reports

#### Day 3-4: Extended Question Types
- **Create**: `templates/xml/multiple_response.xml`
- **Create**: `templates/xml/text_entry.xml`
- Extend parser and generator for new types
- Test each question type thoroughly

#### Day 5-7: Error Handling and Logging
- Comprehensive error messages
- Logging system for debugging
- Input validation and sanitization
- Edge case handling
- Create troubleshooting guide

**Deliverables**:
- Robust validation system
- Support for 3+ question types
- Production-quality error handling
- Comprehensive logging

### Week 4: Documentation and Deployment

**Objective**: Complete documentation, create examples, and prepare for use

#### Day 1-2: User Documentation
- **Create**: `docs/workflow.md`
  - Step-by-step usage guide
  - Screenshots and examples
  - Troubleshooting section
- **Create**: `README.md`
  - Project overview
  - Installation instructions
  - Quick start guide

#### Day 3-4: Example Library
- Create 5-10 complete example tests
- Various subjects and difficulty levels
- Demonstrate all question types
- Include best practices

#### Day 5-7: Final Testing and Polish
- Comprehensive end-to-end testing
- Performance optimization
- Code cleanup and documentation
- Repository organization
- Release preparation

**Deliverables**:
- Complete documentation suite
- Example test library
- Production-ready tool
- GitHub release

---

## Technical Implementation

### Python Libraries and Dependencies

```python
# Core libraries
lxml            # XML generation with namespace support (essential for QTI 2.2)
pyyaml          # Configuration and metadata parsing
markdown2       # Markdown parsing for .md input files
zipfile         # Standard library - create QTI package ZIP files
uuid            # Standard library - generate unique IDs

# Validation
jsonschema      # Validate markdown structure against specification
xmlschema       # Validate XML against QTI 2.2 schema

# Optional for future enhancements
pypdf          # PDF handling (if PDF question content needed)
pillow         # Image processing (if image optimization needed)
click          # Enhanced CLI interface (if complex commands needed)
```

### Module Structure and Responsibilities

#### 1. Parser Module (`src/parser/md_parser.py`)
```python
class MarkdownParser:
    """Parse structured markdown files into Python data structures"""

    def parse_file(self, md_path: str) -> dict:
        """Parse complete .md file"""

    def extract_test_config(self, content: str) -> dict:
        """Extract test-level configuration"""

    def extract_questions(self, content: str) -> list:
        """Extract all questions with metadata"""

    def validate_structure(self, data: dict) -> bool:
        """Validate against markdown specification"""
```

#### 2. Generator Module (`src/generator/xml_generator.py`)
```python
class QTIGenerator:
    """Generate QTI 2.2 XML from parsed question data"""

    def __init__(self, template_dir: str):
        """Load XML templates"""

    def generate_item_xml(self, question: dict) -> etree.Element:
        """Generate single question XML"""

    def apply_inspera_namespace(self, element: etree.Element):
        """Add Inspera-specific namespaces and attributes"""

    def generate_scoring(self, question: dict) -> etree.Element:
        """Generate scoring declarations"""
```

#### 3. Packager Module (`src/packager/qti_packager.py`)
```python
class QTIPackager:
    """Create complete QTI package"""

    def create_manifest(self, items: list, config: dict) -> etree.Element:
        """Generate imsmanifest.xml"""

    def build_package_structure(self, output_dir: str):
        """Create folder structure"""

    def create_zip(self, source_dir: str, output_path: str):
        """Bundle into ZIP file"""
```

#### 4. Validator Module (`src/validator/qti_validator.py`)
```python
class QTIValidator:
    """Validate QTI packages"""

    def validate_xml_schema(self, xml_path: str) -> ValidationResult:
        """Check against QTI 2.2 schema"""

    def validate_inspera_requirements(self, package_dir: str) -> ValidationResult:
        """Check Inspera-specific requirements"""

    def validate_alignment(self, questions: list, objectives: list) -> AlignmentReport:
        """Check objective coverage and Bloom's distribution"""
```

### XML Generation Example

```python
from lxml import etree

def create_assessment_item(question_data):
    # Create root element with namespaces
    nsmap = {
        None: "http://www.imsglobal.org/xsd/imsqti_v2p2",
        'inspera': "http://www.inspera.no/qti",
        'xsi': "http://www.w3.org/2001/XMLSchema-instance"
    }

    root = etree.Element(
        "assessmentItem",
        nsmap=nsmap,
        identifier=str(question_data['id']),
        title=question_data['title']
    )
    root.set("{http://www.inspera.no/qti}objectType",
             "content_question_qti2_multiple_choice")

    # Add response declaration
    response_decl = etree.SubElement(root, "responseDeclaration")
    # ... etc

    return root
```

---

## References and Resources

### Example Files from Inspera
- `/Users/niklaskarlsson/QTI-Generator-for-Inspera/QTI_test1/InsperaAssessmentExport_731212122_422217866/`
  - ID_422217866-item.xml (simple multiple choice question)
  - imsmanifest.xml (package manifest)

- `/Users/niklaskarlsson/QTI-Generator-for-Inspera/QTI_test1/InsperaAssessmentExport_968954738_359001188/`
  - 16 question files with different types
  - 13 image resources
  - Complete assessment structure

### External Resources
1. **QTI 2.2 Specification**: [IMS Global QTI v2.2](http://www.imsglobal.org/question/)
2. **Inspera Documentation**: [Inspera Support](https://support.inspera.com/)
3. **Python XML Processing**: [lxml documentation](https://lxml.de/)

### Reference Repositories for Architectural Patterns
- **qti-package-maker**: Provides valuable architectural patterns for modular QTI generation (Note: Not compatible with Inspera platform)
- **text2qti**: Demonstrates effective lxml XML generation methodologies
- **Important Note**: While these repositories do not support Inspera, they offer instructive implementation approaches for XML generation and package structure

### Commercial Alternatives
- **Respondus 4.0**: Industry-standard QTI generation tool (does not support Inspera platform)
- **ExamView**: Commercial test generator with QTI export capabilities (does not support Inspera platform)
- **Question Writer**: Professional QTI authoring tool (does not support Inspera platform)

---

## Current Project Status

### Repository Information
- **GitHub Repository**: https://github.com/tikankika/QTI-Generator-for-Inspera (private)
- **Current Branch**: main
- **Version Control**: Git configured and operational
- **Project Structure**: Complete folder hierarchy established

### Completed Milestones
- [x] Analyzed existing Inspera QTI exports
- [x] Documented QTI 2.2 structure and requirements
- [x] Established Git repository with professional structure
- [x] Researched existing QTI tools (confirmed no Inspera support)
- [x] Validated unique market position
- [x] Defined project architecture and workflow
- [x] Integrated theoretical framework (Bloom's, TBL, Constructive Alignment)
- [x] Created professional folder structure

### Current Week 1 Priorities

#### Immediate Tasks (Next 1-2 Days)
1. **Create Theoretical Framework Document** (`docs/theoretical_framework.md`)
   - Bloom's Taxonomy implementation guidelines
   - Test-Based Learning principles
   - Constructive Alignment methodology
   - Integration strategies

2. **Define Markdown Specification** (`docs/markdown_specification.md`)
   - Complete format documentation
   - Field definitions and requirements
   - Examples for all question types
   - Validation rules

3. **Build First XML Template** (`templates/xml/multiple_choice.xml`)
   - QTI 2.2 compliant structure
   - Inspera namespace declarations
   - All scoring configurations
   - Feedback mechanisms

#### This Week's Goals (Days 3-7)
1. **Create Claude Desktop Templates**
   - Test planning template
   - Question generation guide
   - Metadata structure documentation

2. **Manual Workflow Testing**
   - Generate 5 sample questions
   - Create complete .md file
   - Manually convert to XML
   - Test import in Inspera
   - Document refinements needed

### Next 3 Weeks Roadmap

**Week 2: Core Implementation**
- Python environment setup
- Markdown parser development
- XML generator implementation
- Basic packager creation
- End-to-end test

**Week 3: Enhancement**
- Validation module
- Additional question types
- Error handling and logging
- Robustness improvements

**Week 4: Documentation & Polish**
- User documentation
- Example library
- Final testing
- Release preparation

### Long-term Vision

**Phase 1 (Months 1-2): Production Tool**
- Fully functional QTI generator
- Support for 5+ question types
- Comprehensive documentation
- Active use in test creation

**Phase 2 (Months 3-4): Community Release**
- Open source release
- Publish to PyPI as `inspera-qti-generator`
- Community documentation
- Issue tracking and support

**Phase 3 (Months 5-6): Platform Expansion**
- Canvas QTI 1.2 export
- Moodle XML export
- Universal QTI conversion tool
- Cross-platform compatibility

---

## Technical Notes

### Key Technical Insights
1. **Namespace Implementation**: The Inspera namespace is essential for complete functionality
2. **Identifier Format**: Numeric identifiers should exclude the "ID_" prefix when utilizing namespace declarations
3. **Label Storage Architecture**: Labels are stored within the manifest file rather than individual item XML files
4. **Resource Referencing**: Images are referenced using relative paths following the pattern `resources/ID_[number].ext`
5. **Language Configuration**: Language settings have comprehensive impact on all system components and must be configured correctly at initialization

### Identified Technical Challenges
1. **Character Encoding**: Proper XML encoding required for Swedish characters (å, ä, ö)
2. **HTML Content Formatting**: Question text containing HTML must maintain well-formed structure
3. **Image Specifications**: Inspera platform imposes specific limitations on image dimensions and file sizes
4. **XML Validation Requirements**: QTI standard enforces strict validation; minor errors prevent successful import

### Development Recommendations
1. **Incremental Development**: Begin with single question implementation before expanding functionality
2. **Continuous Testing**: Validate each feature against the Inspera platform
3. **Comprehensive Logging**: Maintain detailed logs for debugging import processes
4. **Version Control**: Git repository established from project inception

---

*Document created: 2025-10-29*
*Last updated: 2025-10-30*
*Major revision: 2025-10-30 - Added revised architecture, theoretical framework integration, and professional project structure*