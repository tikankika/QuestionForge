# Utility Scripts

This directory contains utility scripts for converting and processing question banks from various formats into the QTI Generator markdown format.

## Interactive Mode (NEWEST!)

The easiest way to use QTI Generator is through the new interactive menu system.

### Quick Start - Interactive Mode

**First time setup** (configure your MQG folders):
```bash
python scripts/setup_mqg_folders.py
```

**Then use interactive mode**:
```bash
python scripts/interactive_qti.py
```

The interactive menu will:
1. Let you choose from your configured MQG folders
2. Show all markdown files in that folder
3. Let you select a file (by number or search)
4. Ask about settings (language, output name, etc.)
5. Run all steps automatically

**Quick shortcuts**:
```bash
# Use last selected file with defaults
python scripts/interactive_qti.py --last --quick

# Start with specific folder
python scripts/interactive_qti.py --folder biologi
```

---

## Modular Pipeline Scripts

The QTI generation process is split into 5 independent scripts that can be run separately for debugging or used together.

### Quick Start - Manual Mode

**Run all steps at once**:
```bash
python scripts/run_all.py input/quiz.md --language sv
```

**Or run steps individually** (recommended for debugging):
```bash
# Step 1: Validate markdown format
python scripts/step1_validate.py input/quiz.md

# Step 2: Create output folder structure
python scripts/step2_create_folder.py input/quiz.md

# Step 3: Copy and rename resources (images)
python scripts/step3_copy_resources.py

# Step 4: Generate QTI XML files
python scripts/step4_generate_xml.py --language sv

# Step 5: Create ZIP package
python scripts/step5_create_zip.py
```

---

## Interactive System - Detailed Documentation

### setup_mqg_folders.py
**Purpose**: Configure MQG folder locations for easy access.

**Usage**:
```bash
python scripts/setup_mqg_folders.py
```

**Interactive menu to**:
- Add new MQG folders (with name, path, default language)
- Edit existing folder configurations
- Remove folders from config
- Verify folder paths

**Config file**: `config/mqg_folders.json`

---

### interactive_qti.py
**Purpose**: User-friendly interactive interface for QTI generation.

**Usage**:
```bash
python scripts/interactive_qti.py [options]

Options:
  --last              Use last selected file
  --quick             Use defaults without prompting
  --folder NAME       Start with specific folder
  -v, --verbose      Show detailed output
```

**Features**:
- Folder selection from configured MQG folders
- Automatic file scanning (recursive .md search)
- Search function for finding files
- Interactive settings wizard
- Step selection (run all or choose specific steps)
- History tracking (remembers last used files)
- Progress display with status messages

**History file**: `.qti_history.json` (automatically created)

---

### Pipeline Scripts

#### run_all.py
**Purpose**: Run complete QTI generation pipeline in sequence.

**Usage**:
```bash
python scripts/run_all.py <markdown_file> [options]

Options:
  --output-name NAME      Override quiz name (default: markdown filename)
  --output-dir DIR        Output base directory (default: ./output)
  --media-dir DIR         Media directory (default: auto-detect)
  --language LANG         Question language code (default: en)
  --strict                Treat resource warnings as errors
  --no-keep-folder       Delete extracted folder after zipping
  -v, --verbose          Show detailed information
```

**Example**:
```bash
python scripts/run_all.py quiz.md --output-name evolution_test --language sv --verbose
```

---

#### step1_validate.py
**Purpose**: Validate markdown format against MQG_bb6 specifications.

**Usage**:
```bash
python scripts/step1_validate.py <markdown_file> [-v]
```

**Exit Codes**:
- 0 = Valid (ready for next step)
- 1 = Validation errors found
- 2 = File not found

**Example**:
```bash
python scripts/step1_validate.py quiz.md
```

---

#### step2_create_folder.py
**Purpose**: Create output folder structure for QTI generation.

**Usage**:
```bash
python scripts/step2_create_folder.py <markdown_file> [options]

Options:
  --output-name NAME      Override quiz name (default: markdown filename)
  --output-dir DIR        Output base directory (default: ./output)
  -v, --verbose          Show detailed information
```

**Creates**:
- `output/{quiz_name}/` - Main quiz directory
- `output/{quiz_name}/resources/` - Media files directory
- `output/{quiz_name}/.workflow/metadata.json` - Workflow metadata

**Example**:
```bash
python scripts/step2_create_folder.py quiz.md --output-name my_quiz
```

---

#### step3_copy_resources.py
**Purpose**: Validate and copy media resources with question ID prefixing and filename sanitization.

**Usage**:
```bash
python scripts/step3_copy_resources.py [options]

Options:
  --markdown-file FILE    Path to markdown file (overrides metadata.json)
  --quiz-dir DIR          Quiz output directory (overrides metadata.json)
  --media-dir DIR         Media directory (default: auto-detect)
  --strict                Treat warnings as errors
  -v, --verbose          Show detailed information
```

**Features**:
- Auto-detects media directory from markdown file location
- Renames resources with question ID prefix (e.g., `virus.png` → `HS_Q014_virus.png`)
- Sanitizes filenames (Swedish characters, spaces)
- Validates file formats and sizes (Inspera requirements)
- Saves resource mapping to `.workflow/resource_mapping.json`

**Example**:
```bash
# Using metadata from step 2 (recommended)
python scripts/step3_copy_resources.py

# Or specify paths manually
python scripts/step3_copy_resources.py --markdown-file quiz.md --quiz-dir output/quiz
```

---

#### step4_generate_xml.py
**Purpose**: Generate QTI XML files for each question.

**Usage**:
```bash
python scripts/step4_generate_xml.py [options]

Options:
  --markdown-file FILE    Path to markdown file (overrides metadata.json)
  --quiz-dir DIR          Quiz output directory (overrides metadata.json)
  --language LANG         Question language code (default: en)
  -v, --verbose          Show detailed information
```

**Features**:
- Reads resource mapping from step 3
- Updates image paths in question data
- Generates XML for all supported question types
- Saves XML files to quiz directory
- Saves metadata to `.workflow/xml_files.json`

**Example**:
```bash
# Using metadata from previous steps (recommended)
python scripts/step4_generate_xml.py --language sv

# Or specify paths manually
python scripts/step4_generate_xml.py --markdown-file quiz.md --quiz-dir output/quiz
```

---

#### step5_create_zip.py
**Purpose**: Create final QTI package (ZIP) with imsmanifest.xml.

**Usage**:
```bash
python scripts/step5_create_zip.py [options]

Options:
  --quiz-dir DIR          Quiz output directory (overrides metadata.json)
  --output-name NAME      Output ZIP filename (default: quiz_dir name)
  --no-keep-folder       Delete extracted folder after zipping
  -v, --verbose          Show detailed information
```

**Creates**:
- `imsmanifest.xml` - QTI package manifest
- `{quiz_name}.zip` - Final QTI package for Inspera upload
- `.workflow/package_info.json` - Package metadata

**Example**:
```bash
# Using metadata from previous steps (recommended)
python scripts/step5_create_zip.py

# Or specify paths manually
python scripts/step5_create_zip.py --quiz-dir output/quiz --output-name final_quiz.zip
```

---

### Workflow Metadata

Each step saves metadata to `.workflow/` directory for the next step to use:

- **metadata.json** (step 2): Input file, quiz name, directory paths
- **resource_mapping.json** (step 3): Original → renamed resource mappings
- **xml_files.json** (step 4): Generated XML files and quiz metadata
- **package_info.json** (step 5): Final ZIP path and folder path

This allows you to:
- Run steps independently without repeating arguments
- Resume from any step if previous steps completed successfully
- Inspect intermediate results for debugging

---

### Debugging Workflow

When you encounter issues, run steps individually to isolate the problem:

1. **Validation fails**: Fix markdown format issues, then continue from step 2
2. **Resource errors**: Fix image paths/formats, re-run step 3 only
3. **XML generation fails**: Fix question data, re-run step 4 only
4. **ZIP packaging fails**: Re-run step 5 only

**Example debugging session**:
```bash
# Step 1 passes
python scripts/step1_validate.py quiz.md

# Step 2 passes
python scripts/step2_create_folder.py quiz.md

# Step 3 fails (missing image)
python scripts/step3_copy_resources.py
# Fix: Add missing image to media directory

# Re-run step 3 (no need to repeat steps 1-2)
python scripts/step3_copy_resources.py

# Continue with step 4
python scripts/step4_generate_xml.py --language sv

# Continue with step 5
python scripts/step5_create_zip.py
```

---

## Conversion Scripts

### convert_evolution_format.py

**Purpose**: Convert dual-structure markdown format (separate Metadata and Question Content sections) to QTI Generator inline format.

**Usage**:
```bash
python scripts/convert_evolution_format.py <input_file> [output_file]
```

**Example**:
```bash
python scripts/convert_evolution_format.py Evolution_Fragebank.md Evolution_CONVERTED.md
```

**Input Format**: Markdown file with dual structure:
- Separate "Metadata" section with bullet lists for labels
- Separate "Question Content" section with question text and answers
- Questions separated by `---` delimiters

**Output Format**: QTI Generator-compatible markdown:
- YAML frontmatter with test metadata
- Inline metadata fields (**Identifier**, **Type**, **Labels**, etc.)
- Labels extracted from metadata section and merged into **Labels**: field
- Questions separated by `---` delimiters

**Features**:
- Extracts labels from bullet lists in metadata sections
- Generates YAML frontmatter with test metadata (title, identifier, language)
- Merges metadata into inline format for each question
- Preserves question identifiers and types

**Output**: Single markdown file ready for filtering and QTI generation

---

### filter_supported_questions.py

**Purpose**: Filter question bank to only include question types supported by the QTI Generator.

**Usage**:
```bash
python scripts/filter_supported_questions.py <input_file> [output_file]
```

**Example**:
```bash
python scripts/filter_supported_questions.py Evolution_CONVERTED.md Evolution_FILTERED.md
```

**Supported Types** (as of v0.2.3-alpha):
- `multiple_choice_single` - Single-answer multiple choice questions
- `text_area` - Short text response questions
- `extended_text` - Long essay response questions

**Input Format**: QTI Generator markdown format with inline metadata

**Output Format**: Same as input, but with unsupported question types removed

**Features**:
- Filters questions by **Type**: field
- Reports statistics on:
  - Total questions processed
  - Number of questions kept (supported types)
  - Number of questions skipped (unsupported types)
- Lists skipped questions with identifiers and types
- Preserves YAML frontmatter and test metadata

**Output**:
- Filtered markdown file with only supported questions
- Console report with filtering statistics

**Example Output**:
```
Filtering results:
  Total questions: 68
  Kept (supported): 56
  Skipped (unsupported): 12

Skipped questions:
  - Question 5 (Q005): true_false
  - Question 12 (Q012): fill_in_the_blank
  - Question 23 (Q023): multiple_choice_multiple
  ...

Skipped by type:
  - true_false: 6
  - multiple_choice_multiple: 4
  - fill_in_the_blank: 2
```

---

## Conversion Pipeline Workflow

The complete workflow for converting external question banks to QTI packages:

### Step 1: Convert Format
```bash
python scripts/convert_evolution_format.py source.md converted.md
```

**Input**: External question bank markdown (dual-structure format)
**Output**: QTI Generator-compatible markdown with inline metadata

### Step 2: Filter Supported Types
```bash
python scripts/filter_supported_questions.py converted.md filtered.md
```

**Input**: Converted markdown from Step 1
**Output**: Filtered markdown with only supported question types

### Step 3: Generate QTI Package
```bash
python main.py filtered.md output.zip --language sv
```

**Input**: Filtered markdown from Step 2
**Output**: QTI ZIP package ready for Inspera import

### Complete Example

```bash
# Convert Evolution question bank format
python scripts/convert_evolution_format.py \
    Evolution_Fragebank_68_fragor_LABELED.md \
    Evolution_CONVERTED.md

# Filter to supported types only
python scripts/filter_supported_questions.py \
    Evolution_CONVERTED.md \
    Evolution_FILTERED.md

# Generate QTI package
python main.py Evolution_FILTERED.md Evolution_quiz.zip --language sv

# Package will be in: output/Evolution_quiz.zip
# Extract folder: output/Evolution_quiz/
```

---

## Case Study: Evolution Question Bank

**Source**: BIOG001X Evolution - Question Bank (68 questions)
**Format**: Dual-structure markdown with separate Metadata/Question Content sections
**Conversion Results**:
- **Total questions**: 68
- **Supported and converted**: 56 questions
- **Unsupported (skipped)**: 12 questions
  - 6 true_false questions
  - 4 multiple_choice_multiple questions
  - 2 fill_in_the_blank questions

**Files Created**:
- `output/test02_evolution_biog001x_QTI/Evolution_CONVERTED.md` - All 68 questions converted
- `output/test02_evolution_biog001x_QTI/Evolution_FILTERED.md` - 56 supported questions
- `output/test02_evolution_biog001x_QTI/Evolution_quiz_with_labels.zip` - Importable QTI package

**Outcome**: Successfully imported 56 questions into Inspera Assessment Platform with custom labels

---

## Troubleshooting

### Error: "Could not find YAML frontmatter"
**Cause**: Input file missing `---` delimiters for frontmatter
**Solution**: Ensure input file has proper frontmatter structure or is using expected format

### Error: "Question has no type field, skipping"
**Cause**: Question missing **Type**: metadata field
**Solution**: Ensure all questions have `**Type**: question_type` in the converted format

### Warning: "Media file not found"
**Cause**: Referenced image/media file doesn't exist in media directory
**Solution**: Ensure all media files are in the specified media directory before generating QTI

### No questions kept after filtering
**Cause**: All questions in input file are unsupported types
**Solution**: Check the "Skipped by type" report and implement missing question types (see ROADMAP.md)

---

## Supported Question Types (v0.2.3-alpha)

| Type | Status | XML Template | Converter |
|------|--------|--------------|-----------|
| `multiple_choice_single` | Production | ✓ | ✓ |
| `text_area` | Production | ✓ | ✓ |
| `extended_text` | Production | ✓ | ✓ |
| `multiple_response` | Beta | ✓ | Partial |
| `true_false` | Planned (v0.3.0) | ✗ | ✗ |
| `fill_blank` | Planned (v0.3.0) | ✗ | ✗ |
| `multiple_choice_multiple` | Planned (v0.3.0) | ? | ✗ |

---

## Future Enhancements (v0.3.0)

See [IDEAS.md](../IDEAS.md) for detailed feature proposals:

- **Batch Processing**: Convert entire directories of markdown files
- **Integration with main.py**: Single command for convert → filter → generate
- **Additional Format Support**: CSV, Excel imports
- **Validation Reports**: Detailed statistics on conversion quality
- **Automated Testing**: Unit and integration tests for conversion scripts

---

## Contributing

When adding new conversion scripts:

1. Follow the naming convention: `convert_<format>_format.py`
2. Add comprehensive docstrings with usage examples
3. Include error handling and validation
4. Report statistics on conversion results
5. Update this README.md with script documentation

See [CONTRIBUTING.md](../CONTRIBUTING.md) (coming soon) for detailed guidelines.

---

**Last Updated**: 2025-11-02
**Version**: v0.2.3-alpha
