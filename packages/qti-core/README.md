# QTI Generator for Inspera

Convert markdown quiz files to QTI 2.2 packages for import into Inspera Assessment Platform.

## Quick Start - Get Running in 30 Seconds

```bash
# 1. Navigate to project folder
cd QTI-Generator-for-Inspera

# 2. Install dependencies (first time only)
pip install -r requirements.txt

# 3. Run interactive mode
python3 scripts/interactive_qti.py
```

That's it! The interactive script guides you through folder selection, file selection, and QTI generation.

---

## Installation (Detailed)

### Option 1: Traditional
1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Option 2: Development Installation
1. Clone or download this repository
2. Install package in editable mode:
   ```bash
   # Basic installation
   pip install -e .

   # With development tools (testing, linting, formatting)
   pip install -e ".[dev]"
   ```

This enables:
- Running `qti-gen` command from anywhere (in addition to `python main.py`)
- Automatic inclusion of all templates and resources
- Development tools (pytest, black, flake8, mypy)

### Command Reference

```bash
# Interactive mode (recommended)
python3 scripts/interactive_qti.py

# Interactive with last file
python3 scripts/interactive_qti.py --last

# Quick mode (all defaults, no prompts)
python3 scripts/interactive_qti.py --quick

# Step-by-step commands
python3 scripts/step1_validate.py quiz.md           # Validate markdown
python3 scripts/step2_create_folder.py quiz.md      # Create output folder
python3 scripts/step3_copy_resources.py             # Copy images/media
python3 scripts/step4_generate_xml.py               # Generate QTI XML
python3 scripts/step5_create_zip.py                 # Create ZIP package

# Direct conversion (old method)
python main.py quiz.md output.zip
python main.py quiz.md output.zip --verbose --language sv
```

### Basic Usage

Convert a markdown quiz to QTI package:

```bash
python main.py quiz.md output.zip
```

This creates **both** a browsable folder and a ZIP file:
- `output/quiz/` - Extracted folder for inspection
- `output/quiz.zip` - ZIP file for Inspera import

With custom options:

```bash
python main.py quiz.md --output TRA265_quiz.zip --language en --verbose
```

To create only the ZIP file (no extracted folder):

```bash
python main.py quiz.md output.zip --no-keep-folder
```

### Example

An example quiz is included: `TRA265_L1a1_quiz.md`

```bash
python main.py TRA265_L1a1_quiz.md TRA265_quiz.zip --verbose
```

This generates:
- `output/TRA265_quiz/` - Browsable folder structure (same format as Inspera exports)
- `output/TRA265_quiz.zip` - QTI package ready for import into Inspera

You can manually inspect the folder contents before importing the ZIP file.

### Inspecting & Validating Packages

Inspect package contents (tree view):

```bash
python main.py --inspect output/TRA265_L1a1_quiz.zip
```

Output:
```
TRA265_L1a1_quiz.zip/
├── TRA265_L1a1_Q01-item.xml (10.7KB)
├── TRA265_L1a1_Q02-item.xml (10.3KB)
...
├── imsmanifest.xml (2.7KB)
└── resources/ (when images present)
    ├── image1.png
    └── image2.jpg
```

Validate package structure:

```bash
python main.py --validate output/TRA265_L1a1_quiz.zip
```

Output:
```
✓ Package validation passed: output/TRA265_L1a1_quiz.zip

Warnings:
  - resources/ folder missing (okay if no media files)
```

## Package Structure

By default, the tool creates **both** an extracted folder and a ZIP file in the `output/` directory. This allows you to:
1. Browse the folder structure for inspection and comparison with Inspera exports
2. Import the ZIP file directly into Inspera

The generated QTI packages follow Inspera's expected structure:

**Without media files:**
```
quiz.zip/
├── imsmanifest.xml
├── Q001-item.xml
├── Q002-item.xml
└── ...
```

**With media files:**
```
quiz.zip/
├── imsmanifest.xml
├── Q001-item.xml
├── Q002-item.xml
└── resources/
    ├── image1.png
    ├── image2.jpg
    └── ...
```

The `resources/` subfolder is automatically created when questions reference images or other media files. Media files must be referenced in question XML as `resources/filename.ext`.

## Markdown Format

See `docs/markdown_specification.md` for complete format documentation.

### Basic Structure

```markdown
---
test_metadata:
  title: "Quiz Title"
  identifier: "QUIZ_ID"
  language: "en"
  description: "Quiz description"
  subject: "Course Name"
  author: "Author Name"
  created_date: "2025-10-30"

assessment_configuration:
  type: "formative"
  time_limit: 15
  shuffle_questions: true
  shuffle_choices: true
  feedback_mode: "immediate"
  attempts_allowed: 3

learning_objectives:
  - id: "LO1"
    description: "Students will be able to..."
---

# Question 1: Question Title

**Type**: multiple_choice_single
**Identifier**: Q001
**Points**: 1
**Learning Objectives**: LO1
**Bloom's Level**: Remember

## Question Text

What is 2 + 2?

## Options

A. 3
B. 4
C. 5
D. 6

## Answer

B

## Feedback

### General Feedback
Basic arithmetic question.

### Correct Response Feedback
Correct! 2 + 2 = 4.

### Incorrect Response Feedback
Not quite. Try again.

### Unanswered Feedback
Please select an answer.

### Option-Specific Feedback
- **A**: Too low
- **B**: Correct!
- **C**: Too high
- **D**: Too high

---

# Question 2: Next Question Title
...
```

## Supported Question Types

### Priority 1 (Production Ready)
- `multiple_choice_single` - Single answer multiple choice ✅
- `extended_text` - Essay questions (coming soon)
- `text_area` - Short text response (coming soon)
- `multiple_response` - Multiple answer multiple choice (coming soon)

## Project Structure

```
QTI-Generator-for-Inspera/
├── main.py                 # CLI tool
├── requirements.txt        # Python dependencies
├── src/
│   ├── parser/            # Markdown parsing
│   ├── generator/         # XML generation
│   └── packager/          # QTI package creation
├── templates/
│   └── xml/               # QTI 2.2 templates (15 types, 87% coverage)
├── docs/                  # Documentation
└── output/                # Generated QTI packages

```

## Import into Inspera

1. Log in to Inspera Assessment
2. Navigate to Question Bank or Test Designer
3. Click "Import" and select "QTI 2.2"
4. Upload the generated ZIP file
5. Review imported questions

## Features

- ✅ YAML frontmatter for quiz metadata
- ✅ Multiple choice (single answer) questions
- ✅ Rich text support (bold, italic, code)
- ✅ Detailed feedback (correct, incorrect, unanswered, option-specific)
- ✅ Automatic QTI 2.2 XML generation
- ✅ IMS Content Package (ZIP) creation
- ✅ Inspera-specific namespace support
- ✅ **resources/ folder structure** for media files
- ✅ **Package validation** (verify structure before import)
- ✅ **Package inspection** (tree view of ZIP contents)

## Future Enhancements

- [ ] Additional question types (essay, multiple response, etc.)
- [ ] Image support
- [ ] LaTeX math support
- [ ] XML schema validation
- [ ] Batch conversion of multiple quizzes

## Documentation

### QTI Generator Documentation
- `docs/markdown_specification.md` - Complete markdown format specification
- `docs/research/qti-question-types-inventory.md` - Analysis of Inspera question types
- `templates/xml/README.md` - XML template documentation

### Question Authoring Specifications (Modular QGen Framework)
For authoring questions with Claude Desktop, refer to the Modular QGen Framework specifications:
- **BB6A**: Question Output Specifications (structure for all 16 question types)
- **BB6B**: Metadata Requirements (Type, Identifier, Points, Language, Labels)
- **BB6C**: Validation Checklist (pre-export validation rules)

These specifications define the exact format expected by this QTI Generator.

## Development

### Running Tests

```bash
# Test with example quiz
python main.py TRA265_L1a1_quiz.md test_output.zip --verbose

# Verify output structure
unzip -l output/test_output.zip
```

### Adding New Question Types

1. Create XML template in `templates/xml/`
2. Update parser if new markdown fields needed
3. Update generator to handle new template placeholders
4. Test with example questions

## License

CC BY-NC-SA 4.0 - See [LICENSE.md](../../LICENSE.md)

## Citation

When citing this software in academic work:

**APA:**
```
Karlsson, N. (2025). QTI Generator for Inspera (Version 0.2.2-alpha) [Computer software].
https://github.com/tikankika/QTI-Generator-for-Inspera
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Support

For issues or questions:
- Check `docs/` for documentation
- Review example quiz: `TRA265_L1a1_quiz.md`
- Open an issue on GitHub

## Project Planning

This project follows the [Software Development Protocol v2.2](Software_Development_Protocol_v2.2/) for systematic development and continuous improvement.

### Strategic Documents

- **[VISION.md](VISION.md)** - Long-term vision and impact goals (1-3 years)
  - Target users and communities
  - Technical roadmap to v2.0
  - Research integration strategy
  - Success metrics and sustainability

- **[ROADMAP.md](ROADMAP.md)** - Feature development roadmap (6-12 months)
  - Milestone v0.3.0 (Dec 2025): Core question type expansion
  - Milestone v0.4.0 (Feb 2026): Advanced interaction types
  - Milestone v0.5.0 (Apr 2026): Multi-platform export
  - Milestone v1.0.0 (Jun 2026): Stable production release

- **[CHANGELOG.md](CHANGELOG.md)** - Detailed version history with daily progress tracking
  - Daily development logs with research notes
  - Follows "Keep a Changelog" specification
  - Contemporaneous documentation of all changes

- **[IDEAS.md](IDEAS.md)** - Feature wishlist and community suggestions (coming soon)
  - Candidate features for future consideration
  - User-requested enhancements
  - Research opportunities

### Current Development Status

**Release**: v0.2.4-alpha (2025-11-01)
**Focus**: Modern Python packaging infrastructure
**Next Milestone**: v0.3.0 (Target: 2025-12-15)

## Version History

### v0.2.4-alpha (2025-11-01)
- **NEW**: Modern Python packaging with pyproject.toml (PEP 517/518)
- **NEW**: CC BY-NC-SA 4.0 License for open source distribution
- **NEW**: Development dependencies in requirements-dev.txt
- **NEW**: Package manifest (MANIFEST.in) for template inclusion
- **IMPROVED**: Dual installation methods (traditional + modern)
- **FEATURE**: Optional `qti-gen` CLI command (alongside `python main.py`)
- **PREPARED**: PyPI publication readiness for v1.0.0

### v0.2.3-alpha (2025-11-01)
- **NEW**: Strategic planning documentation (VISION.md, ROADMAP.md)
- **NEW**: Complete documentation for all 16 question types in templates
- **IMPROVED**: Professional text-based status indicators (removed emojis)
- **IMPROVED**: Reorganized metadata documentation (single source of truth)
- **ENHANCED**: Metadata label generation documentation with best practices
- **ALIGNED**: All documentation with Software Development Protocol v2.2 standards

### v0.2.2-alpha (2025-10-31)
- **NEW**: Folder preservation - keeps extracted package folder alongside ZIP by default
- **NEW**: `--no-keep-folder` flag to create ZIP only (deletes folder after packaging)
- **IMPROVED**: Package folder named after output file (e.g., `quiz.zip` → `output/quiz/`)
- **IMPROVED**: Better output messaging showing both folder and ZIP paths
- **FEATURE**: Enables manual inspection of package structure before import (matches Inspera export format)

### v0.2.1-alpha (2025-10-31)
- **IMPROVED**: resources/ subfolder support for media files
- **NEW**: Package validation (`--validate` flag)
- **NEW**: Package inspection (`--inspect` flag with tree view)
- **NEW**: Automatic media file detection and manifest updates
- **IMPROVED**: Package structure matches Inspera's exact requirements
- **FIX**: Manifest now correctly references media files in resources/

### v0.2.0-alpha (2025-10-31)
- **NEW**: Python implementation complete
  - Markdown parser module
  - XML generator module
  - QTI packager module
  - CLI tool (main.py)
- **NEW**: Full markdown-to-QTI conversion pipeline
- **NEW**: Example quiz (TRA265_L1a1_quiz.md) with 10 questions
- **FEATURE**: multiple_choice_single question type support
- **COVERAGE**: 87% template coverage (15 question types)

### v0.1.0-alpha (2025-10-30)
- Initial release with XML templates
- Documentation and specifications
- Research and reverse engineering of Inspera QTI format

---

**Built with Claude Code by Anthropic**
