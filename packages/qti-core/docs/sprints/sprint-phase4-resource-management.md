# Sprint: Phase 4 - Resource Management Restructuring

**Sprint Duration:** 2-3 weeks (10 working days)
**Target Completion:** [To be scheduled]
**Sprint Goal:** Centralize resource management with early validation, pre-processing pipeline, and Nextcloud path support while maintaining backward compatibility.

---

## Table of Contents
1. [Sprint Goal](#sprint-goal)
2. [Current State Analysis](#current-state-analysis)
3. [Proposed Architecture](#proposed-architecture)
4. [Implementation Plan](#implementation-plan)
5. [Success Criteria](#success-criteria)
6. [Definition of Done](#definition-of-done)
7. [Daily Breakdown](#daily-breakdown)
8. [Risk Assessment](#risk-assessment)
9. [Retrospective](#retrospective)

---

## Sprint Goal

**One Sentence:**
Implement centralized resource management that validates assets early, copies resources before XML generation, and supports Nextcloud collaboration workflows without breaking existing functionality.

**User Story:**
As a **course developer**, I want the QTI generator to validate my images and resources **before** generating XML, so that I catch errors early and can work seamlessly with Nextcloud-synced assessment folders.

**Why This Matters:**
- Current pain point: Errors discovered late (during XML generation or after zipping)
- User need: Collaborate via Nextcloud with colleagues
- Technical debt: Resource handling scattered across 4 modules
- Future enabler: Foundation for PDF support, audio resources, LaTeX rendering

---

## Current State Analysis

### Current Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CURRENT WORKFLOW                         │
└─────────────────────────────────────────────────────────────┘

Input: quiz.md
   ↓
┌──────────────────────┐
│  markdown_parser.py  │  ← Extracts image references
│  - parse_markdown()  │     Stores: {'alt': '...', 'path': 'file.png'}
└──────────────────────┘
   ↓
┌──────────────────────┐
│  xml_generator.py    │  ← Generates QTI XML
│  - Multiple modules  │     Each question type handles images differently
│    per question type │     (hotspot, graphicgapmatch, etc.)
└──────────────────────┘
   ↓
┌──────────────────────┐
│  packager.py         │  ← Copies images during packaging
│  - create_qti()      │     Error: Image not found (too late!)
└──────────────────────┘
   ↓
Output: quiz.zip
```

### Pain Points

1. **Late Error Detection**
   - Images validated only during packaging (after XML generation)
   - User wastes time if image missing/invalid
   - Hard to debug: which question references the broken image?

2. **Fragmented Resource Handling**
   - `markdown_parser.py`: Extracts image references
   - `xml_generator.py`: 8+ modules each handle images differently
   - `packager.py`: Copies images to ZIP
   - No single source of truth

3. **No Pre-flight Validation**
   - Cannot validate resources before generation
   - No file size checks (Inspera has 5MB limit)
   - No format validation (.png, .jpg, .svg only)
   - Invalid filenames not caught (spaces, special chars)

4. **Local-only Workflow**
   - Hardcoded relative paths (`./images/`, `../resources/`)
   - Cannot use Nextcloud paths directly
   - Manual file copying required for collaboration

5. **Debugging Difficulty**
   - Cannot inspect `output/resources/` before zipping
   - Resources copied inside packager (black box)
   - Errors don't show which question caused issue

### Technical Debt

- **Inconsistent image key usage**: Some code reads `image_data['path']`, others read `image_data['file']` (bug fixed 2025-11-10)
- **No abstraction**: Each question type reimplements image handling
- **Tight coupling**: XML generation depends on filesystem structure
- **No validation layer**: Trust that files exist and are valid

---

## Proposed Architecture

### New Workflow (Phase 4)

```
┌─────────────────────────────────────────────────────────────┐
│                    NEW WORKFLOW                             │
└─────────────────────────────────────────────────────────────┘

Input: quiz.md (local or Nextcloud path)
   ↓
┌──────────────────────────────────────────────────────────┐
│  NEW: ResourceManager                                    │
│  Step 1: Validate All Resources                          │
│    ✓ File exists?                                        │
│    ✓ Valid format? (.png, .jpg, .svg)                    │
│    ✓ Size < 5MB?                                         │
│    ✓ Valid filename? (no spaces, special chars)          │
│    ✓ Readable?                                           │
│  → Fail fast with clear error messages                   │
└──────────────────────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────────────────────┐
│  NEW: ResourceManager                                    │
│  Step 2: Prepare Output Structure                        │
│    output/quiz_name/                                     │
│      ├── resources/ ← Create this early                  │
│      └── (XML files added later)                         │
└──────────────────────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────────────────────┐
│  NEW: ResourceManager                                    │
│  Step 3: Copy Resources Early                            │
│    Copy all images to output/quiz_name/resources/        │
│    → Visible before XML generation                       │
│    → Easy to inspect/debug                               │
└──────────────────────────────────────────────────────────┘
   ↓
┌──────────────────────┐
│  markdown_parser.py  │  ← Parse markdown (unchanged)
└──────────────────────┘
   ↓
┌──────────────────────┐
│  xml_generator.py    │  ← Generate XML (unchanged)
│                      │     Resources already in place
└──────────────────────┘
   ↓
┌──────────────────────┐
│  packager.py         │  ← SIMPLIFIED: Just zip the folder
│  (simplified)        │     No longer copies media
└──────────────────────┘
   ↓
Output: quiz.zip
```

### ResourceManager Class Design

**Location:** `src/generator/resource_manager.py` (new file)

```python
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class ResourceIssue:
    """Represents a resource validation issue"""
    level: str  # 'ERROR', 'WARNING', 'INFO'
    resource_path: str
    question_id: Optional[str]
    message: str
    fix_suggestion: Optional[str]

class ResourceManager:
    """
    Centralized resource management for QTI generation.

    Responsibilities:
    1. Validate resources before generation
    2. Prepare output directory structure
    3. Copy resources early in pipeline
    4. Support multiple path formats (local, Nextcloud, absolute)
    5. Provide clear error messages with fix suggestions
    """

    def __init__(self,
                 input_file: Path,
                 output_dir: Path,
                 media_dir: Optional[Path] = None,
                 strict: bool = False):
        """
        Initialize ResourceManager.

        Args:
            input_file: Path to input markdown file
            output_dir: Path to output directory
            media_dir: Optional media directory (auto-detect if None)
            strict: If True, treat warnings as errors
        """
        self.input_file = Path(input_file).expanduser().resolve()
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.strict = strict

        # Auto-detect media directory
        if media_dir:
            self.media_dir = Path(media_dir).expanduser().resolve()
        else:
            self.media_dir = self._auto_detect_media_dir()

    def _auto_detect_media_dir(self) -> Path:
        """
        Auto-detect media directory using search order:
        1. ./resources/ (Nextcloud convention)
        2. ./images/
        3. Same directory as input file
        """
        candidates = [
            self.input_file.parent / "resources",
            self.input_file.parent / "images",
            self.input_file.parent
        ]

        for candidate in candidates:
            if candidate.exists():
                return candidate

        return self.input_file.parent  # Default fallback

    def validate_resources(self, questions: List[Dict]) -> List[ResourceIssue]:
        """
        Validate all resources referenced in questions.

        Returns:
            List of ResourceIssue objects (errors, warnings, info)
        """
        issues = []

        for question in questions:
            # Extract all resource references
            resources = self._extract_resources(question)

            for resource_path in resources:
                # Check file existence
                full_path = self.media_dir / resource_path
                if not full_path.exists():
                    issues.append(ResourceIssue(
                        level='ERROR',
                        resource_path=resource_path,
                        question_id=question.get('identifier'),
                        message=f"Resource not found: {resource_path}",
                        fix_suggestion=f"Check media directory: {self.media_dir}"
                    ))
                    continue

                # Check file format
                if full_path.suffix.lower() not in ['.png', '.jpg', '.jpeg', '.svg', '.gif']:
                    issues.append(ResourceIssue(
                        level='WARNING',
                        resource_path=resource_path,
                        question_id=question.get('identifier'),
                        message=f"Unsupported format: {full_path.suffix}",
                        fix_suggestion="Convert to .png, .jpg, or .svg"
                    ))

                # Check file size (Inspera limit: 5MB)
                size_mb = full_path.stat().st_size / (1024 * 1024)
                if size_mb > 5:
                    issues.append(ResourceIssue(
                        level='ERROR' if self.strict else 'WARNING',
                        resource_path=resource_path,
                        question_id=question.get('identifier'),
                        message=f"File too large: {size_mb:.1f}MB (limit: 5MB)",
                        fix_suggestion="Compress image or reduce dimensions"
                    ))

                # Check filename validity (no spaces, special chars)
                if not resource_path.replace('_', '').replace('-', '').replace('.', '').isalnum():
                    issues.append(ResourceIssue(
                        level='WARNING',
                        resource_path=resource_path,
                        question_id=question.get('identifier'),
                        message=f"Filename contains special characters: {resource_path}",
                        fix_suggestion="Use only letters, numbers, underscore, hyphen"
                    ))

        return issues

    def prepare_output_structure(self, quiz_name: str) -> Path:
        """
        Create output directory structure.

        Returns:
            Path to quiz output directory
        """
        quiz_dir = self.output_dir / quiz_name
        resources_dir = quiz_dir / "resources"

        quiz_dir.mkdir(parents=True, exist_ok=True)
        resources_dir.mkdir(exist_ok=True)

        return quiz_dir

    def copy_resources(self, questions: List[Dict], quiz_dir: Path) -> Dict[str, str]:
        """
        Copy all resources to output directory with question ID prefix.

        Naming Convention:
            Original: virus_structure.png
            Renamed: HS_Q014_virus_structure.png
            Format: {question_id}_{original_filename}

        Returns:
            Mapping of original paths to renamed paths
        """
        import shutil

        resources_dir = quiz_dir / "resources"
        copied = {}

        for question in questions:
            question_id = question.get('identifier', 'UNKNOWN')
            resources = self._extract_resources(question)

            for resource_path in resources:
                src = self.media_dir / resource_path

                # Generate renamed filename with question ID prefix
                original_name = Path(resource_path).name
                renamed_name = f"{question_id}_{original_name}"
                dst = resources_dir / renamed_name

                if src.exists() and resource_path not in copied:
                    shutil.copy2(src, dst)
                    copied[resource_path] = renamed_name  # Map: original → renamed

        # Save mapping to JSON for reference
        import json
        mapping_file = quiz_dir / "resource_mapping.json"
        with open(mapping_file, 'w') as f:
            json.dump(copied, f, indent=2)

        return copied

    def _extract_resources(self, question: Dict) -> List[str]:
        """Extract all resource paths from a question."""
        resources = []

        # Image in question text
        if 'image' in question and question['image']:
            img = question['image']
            if isinstance(img, dict):
                resources.append(img.get('path', img.get('file', '')))
            elif isinstance(img, str):
                resources.append(img)

        # Hotspot/graphicgapmatch images
        if question.get('type') in ['hotspot', 'graphicgapmatch_v2']:
            # Same logic as above
            pass

        # Match question images (in stems/options)
        if question.get('type') == 'match':
            # Extract from stems/options
            pass

        return [r for r in resources if r]  # Filter empty strings
```

### Integration Points

**1. Update `main.py`** (main workflow)
```python
from src.generator.resource_manager import ResourceManager

def main():
    # Parse CLI args
    args = parse_args()

    # Initialize ResourceManager
    rm = ResourceManager(
        input_file=args.input,
        output_dir=args.output,
        media_dir=args.images,
        strict=args.strict
    )

    # Parse markdown
    questions = parse_markdown(args.input)

    # VALIDATE RESOURCES EARLY
    issues = rm.validate_resources(questions)
    if has_errors(issues):
        print_issues(issues)
        sys.exit(1)

    # PREPARE OUTPUT STRUCTURE
    quiz_dir = rm.prepare_output_structure(quiz_name)

    # COPY RESOURCES EARLY
    copied = rm.copy_resources(questions, quiz_dir)
    print(f"✓ Copied {len(copied)} resources to {quiz_dir}/resources/")

    # Generate XML (unchanged)
    generate_xml(questions, quiz_dir)

    # Package (simplified - no media copying)
    create_zip(quiz_dir)
```

**2. Update `src/cli.py`** (new CLI flags)
```python
parser.add_argument('--strict', action='store_true',
    help='Treat warnings as errors (fail fast)')

parser.add_argument('--validate-resources', action='store_true',
    help='Only validate resources without generating QTI')
```

**3. Simplify `src/utils/packager.py`**
```python
def create_qti_package(quiz_dir: Path, output_zip: Path):
    """
    Create QTI ZIP package from prepared directory.

    Note: Resources already copied by ResourceManager.
    This function now only handles zipping.
    """
    import shutil
    shutil.make_archive(output_zip.stem, 'zip', quiz_dir)
```

---

## Implementation Plan

### Phase 1: Foundation (Days 1-2)
**Goal:** Create ResourceManager class with validation

**Tasks:**
1. Create `src/generator/resource_manager.py` (3 hours)
   - Class structure
   - `__init__` with path handling
   - `_auto_detect_media_dir()` method
   - Tilde expansion support (`~/Nextcloud/...`)

2. Implement `validate_resources()` (4 hours)
   - File existence check
   - Format validation (.png, .jpg, .svg)
   - Size validation (< 5MB)
   - Filename validation
   - Clear error messages with fix suggestions

3. Write unit tests for validation (2 hours)
   - Test missing files
   - Test invalid formats
   - Test large files
   - Test special characters in filenames

**Estimated:** 9 hours (2 short days)

---

### Phase 2: Pre-processing Pipeline (Days 3-5)
**Goal:** Implement early resource copying

**Tasks:**
1. Implement `prepare_output_structure()` (1 hour)
   - Create `output/quiz_name/`
   - Create `output/quiz_name/resources/`
   - Handle existing directories

2. Implement `copy_resources()` with renaming (4 hours)
   - Extract resources from all question types
   - Rename with question ID prefix: `{question_id}_{filename}`
   - Copy to `resources/` folder with new names
   - Generate `resource_mapping.json` (original → renamed)
   - Return mapping for verification
   - Handle duplicates and edge cases

3. Implement `_extract_resources()` (3 hours)
   - Hotspot questions
   - GraphicGapMatch questions
   - Match questions with images
   - Inline images in text
   - Handle all edge cases

4. Write integration tests (3 hours)
   - Test with BIOG001X Evolution (1 image)
   - Test with BIOG001X Virus (3 images)
   - Test with TRA265 (hotspot images)

**Estimated:** 11 hours (2.5 days)
**Note:** +1 hour for resource renaming logic

---

### Phase 3: Integration (Days 6-7)
**Goal:** Integrate ResourceManager into main workflow

**Tasks:**
1. Update `main.py` (2 hours)
   - Initialize ResourceManager
   - Call validation before generation
   - Prepare structure early
   - Copy resources before XML

2. Update `src/cli.py` (1 hour)
   - Add `--strict` flag
   - Add `--validate-resources` flag
   - Update help text with examples

3. Simplify `src/utils/packager.py` (2 hours)
   - Remove media copying logic
   - Keep only ZIP creation
   - Update tests

4. Test backward compatibility (2 hours)
   - Verify old workflows still work
   - Test with local paths
   - Test with `--images` flag
   - Regression testing

**Estimated:** 7 hours (2 days)

---

### Phase 4: Nextcloud Support (Days 8-9)
**Goal:** Enable Nextcloud collaboration workflows

**Tasks:**
1. Test with Nextcloud paths (2 hours)
   - `~/Nextcloud/Courses/.../quiz.md`
   - Auto-detect `resources/` subfolder
   - Verify syncing works

2. Document Nextcloud workflow (2 hours)
   - Update README.md
   - Add examples
   - Migration guide

3. Create folder structure guide (1 hour)
   - Recommended structure
   - Best practices
   - Naming conventions

**Estimated:** 5 hours (1.5 days)

---

### Phase 5: Documentation & Polish (Day 10)
**Goal:** Professional documentation and retrospective

**Tasks:**
1. Update CHANGELOG.md (1 hour)
   - Document architecture changes
   - List new features
   - Migration notes

2. Update README.md (1 hour)
   - Architecture diagram
   - New CLI flags
   - Examples

3. Code review (2 hours)
   - Self-review with Claude
   - Refactor if needed
   - Check test coverage

4. Sprint retrospective (1 hour)
   - What went well
   - What was tricky
   - Lessons learned

**Estimated:** 5 hours (1 day)

---

## Success Criteria

### Functional Requirements
- [ ] ResourceManager validates all resource types (images, future: PDFs, audio)
- [ ] Validation catches missing files before XML generation
- [ ] Validation checks file size (< 5MB Inspera limit)
- [ ] Validation checks file format (.png, .jpg, .svg)
- [ ] Resources copied to `output/quiz_name/resources/` before XML generation
- [ ] Nextcloud paths supported (`~/Nextcloud/...`)
- [ ] Auto-detect `resources/` subfolder
- [ ] `--strict` flag treats warnings as errors
- [ ] `--validate-resources` flag for validation-only mode

### Non-Functional Requirements
- [ ] Backward compatible (no breaking changes)
- [ ] Test coverage maintained > 85%
- [ ] All existing tests pass
- [ ] Performance: Validation adds < 2 seconds overhead
- [ ] Clear error messages with fix suggestions
- [ ] Professional documentation (README, CHANGELOG, code comments)

### Edge Cases Handled
- [ ] Missing images: Clear error with question ID
- [ ] Invalid format: Warning with conversion suggestion
- [ ] Large files: Warning/error with compression suggestion
- [ ] Special chars in filename: Warning with rename suggestion
- [ ] Duplicate filenames: Handled gracefully
- [ ] Nextcloud sync conflicts: Detected and reported

---

## Definition of Done

### Code Complete
- [ ] All Phase 1-5 tasks implemented
- [ ] ResourceManager class complete and tested
- [ ] Integration with main workflow complete
- [ ] CLI flags added and working
- [ ] Packager simplified (media copying removed)

### Testing
- [ ] Unit tests for ResourceManager (>90% coverage)
- [ ] Integration tests with real assessments:
  - [ ] BIOG001X Evolution (61 questions, 1 image)
  - [ ] BIOG001X Virus (39 questions, 3 images)
  - [ ] TRA265 L1b (13 questions, hotspot images)
- [ ] Regression tests (all existing tests pass)
- [ ] Manual testing with Nextcloud paths

### Documentation
- [ ] CHANGELOG.md updated with architecture changes
- [ ] README.md updated with:
  - [ ] Architecture diagram (before/after)
  - [ ] New CLI flags documented
  - [ ] Nextcloud workflow examples
  - [ ] Migration guide (if applicable)
- [ ] Code comments explain WHY (not just WHAT)
- [ ] Docstrings for all public methods
- [ ] Sprint retrospective completed in this document

### Version Control
- [ ] Feature branch created: `feature/resource-pipeline-restructure`
- [ ] Commits follow conventional format
- [ ] Code reviewed (by Claude or self)
- [ ] All tests passing in CI (if CI exists)
- [ ] Merged to main branch
- [ ] Feature branch deleted
- [ ] GitHub release created (if applicable)

---

## Daily Breakdown

### Day 1: Monday - Foundation Setup
**Hours:** 4-5 hours

**Morning (2-3 hours):**
- [ ] Create `src/generator/resource_manager.py`
- [ ] Implement class structure and `__init__`
- [ ] Implement `_auto_detect_media_dir()`
- [ ] Add tilde expansion support

**Afternoon (2 hours):**
- [ ] Start `validate_resources()` method
- [ ] Implement file existence check
- [ ] Add format validation

**Evening (5 min):**
- [ ] Update CHANGELOG.md
- [ ] Commit: `feat(resource-manager): create ResourceManager class with path handling`
- [ ] Push to feature branch

---

### Day 2: Tuesday - Validation Complete
**Hours:** 4-5 hours

**Morning (2-3 hours):**
- [ ] Complete `validate_resources()` method
- [ ] Add file size validation (< 5MB)
- [ ] Add filename validation
- [ ] Implement clear error messages with fix suggestions

**Afternoon (2 hours):**
- [ ] Write unit tests for validation
- [ ] Test missing files, invalid formats, large files

**Evening (5 min):**
- [ ] Update CHANGELOG.md
- [ ] Commit: `feat(resource-manager): add comprehensive resource validation`
- [ ] Push to feature branch

---

### Day 3: Wednesday - Pre-processing Part 1
**Hours:** 4-5 hours

**Morning (2-3 hours):**
- [ ] Implement `prepare_output_structure()`
- [ ] Implement `copy_resources()`
- [ ] Test basic copying workflow

**Afternoon (2 hours):**
- [ ] Start `_extract_resources()` helper
- [ ] Handle hotspot questions
- [ ] Handle graphicgapmatch questions

**Evening (5 min):**
- [ ] Update CHANGELOG.md
- [ ] Commit: `feat(resource-manager): implement resource copying pipeline`
- [ ] Push to feature branch

---

### Day 4: Thursday - Pre-processing Part 2
**Hours:** 4-5 hours

**Morning (2-3 hours):**
- [ ] Complete `_extract_resources()` for all question types
- [ ] Handle match questions with images
- [ ] Handle inline images in text

**Afternoon (2 hours):**
- [ ] Write integration tests
- [ ] Test with BIOG001X Evolution
- [ ] Test with BIOG001X Virus

**Evening (5 min):**
- [ ] Update CHANGELOG.md
- [ ] Commit: `feat(resource-manager): complete resource extraction for all question types`
- [ ] Push to feature branch

---

### Day 5: Friday - Integration Testing
**Hours:** 3-4 hours

**Morning (2 hours):**
- [ ] Test with TRA265 (hotspot images)
- [ ] Fix any edge cases discovered
- [ ] Verify all validation rules work

**Afternoon (1-2 hours):**
- [ ] Code review (self or Claude)
- [ ] Refactor if needed
- [ ] Check test coverage

**Evening (5 min):**
- [ ] Update CHANGELOG.md
- [ ] Commit: `test(resource-manager): add comprehensive integration tests`
- [ ] Push to feature branch

---

### Day 6: Monday - Main Workflow Integration
**Hours:** 4-5 hours

**Morning (2-3 hours):**
- [ ] Update `main.py` to use ResourceManager
- [ ] Initialize ResourceManager
- [ ] Call validation before generation
- [ ] Prepare structure and copy resources early

**Afternoon (2 hours):**
- [ ] Update `src/cli.py` with new flags
- [ ] Add `--strict` flag
- [ ] Add `--validate-resources` flag

**Evening (5 min):**
- [ ] Update CHANGELOG.md
- [ ] Commit: `feat(main): integrate ResourceManager into generation workflow`
- [ ] Push to feature branch

---

### Day 7: Tuesday - Simplify Packager
**Hours:** 4 hours

**Morning (2 hours):**
- [ ] Simplify `src/utils/packager.py`
- [ ] Remove media copying logic
- [ ] Keep only ZIP creation

**Afternoon (2 hours):**
- [ ] Test backward compatibility
- [ ] Verify old workflows still work
- [ ] Regression testing with all assessments

**Evening (5 min):**
- [ ] Update CHANGELOG.md
- [ ] Commit: `refactor(packager): simplify by removing media copying`
- [ ] Push to feature branch

---

### Day 8: Wednesday - Nextcloud Support
**Hours:** 3-4 hours

**Morning (2 hours):**
- [ ] Test with Nextcloud paths
- [ ] Verify auto-detect `resources/` subfolder
- [ ] Test syncing behavior

**Afternoon (1-2 hours):**
- [ ] Document Nextcloud workflow
- [ ] Create folder structure guide
- [ ] Add best practices

**Evening (5 min):**
- [ ] Update CHANGELOG.md
- [ ] Commit: `feat(resource-manager): add Nextcloud path support`
- [ ] Push to feature branch

---

### Day 9: Thursday - Documentation Part 1
**Hours:** 3 hours

**Morning (2 hours):**
- [ ] Update CHANGELOG.md with full architecture changes
- [ ] Document migration notes
- [ ] List all new features

**Afternoon (1 hour):**
- [ ] Start README.md update
- [ ] Add architecture diagram

**Evening (5 min):**
- [ ] Commit: `docs: update CHANGELOG with Phase 4 architecture`
- [ ] Push to feature branch

---

### Day 10: Friday - Documentation Part 2 & Merge
**Hours:** 4 hours

**Morning (2 hours):**
- [ ] Complete README.md update
- [ ] Document new CLI flags
- [ ] Add Nextcloud workflow examples

**Afternoon (2 hours):**
- [ ] Final code review
- [ ] Sprint retrospective (in this document)
- [ ] Prepare merge to main

**Evening (15 min):**
- [ ] Merge feature branch to main
- [ ] Delete feature branch
- [ ] Create GitHub release (if applicable)
- [ ] Celebrate! 🎉

---

## Risk Assessment

### High Risk (Mitigation Required)

1. **Breaking Changes to Existing Workflows**
   - **Risk:** Users' scripts break after update
   - **Mitigation:**
     - Maintain backward compatibility
     - ResourceManager is opt-in (enhancement, not replacement)
     - Extensive regression testing
     - Clear migration guide in docs

2. **Performance Degradation**
   - **Risk:** Validation adds significant overhead
   - **Mitigation:**
     - Target: < 2 seconds overhead
     - Validate only when needed (not in production)
     - Option to skip validation (`--no-validate`)
     - Profile with large assessments (100+ questions)

### Medium Risk (Monitor)

3. **Nextcloud Sync Conflicts**
   - **Risk:** Resources change during generation
   - **Mitigation:**
     - Copy resources early (atomic operation)
     - Document best practices
     - Detect and warn about sync conflicts

4. **Path Handling Edge Cases**
   - **Risk:** Unusual path formats not handled
   - **Mitigation:**
     - Use `pathlib.Path` consistently
     - Handle `~`, `..`, absolute, relative paths
     - Comprehensive path testing

### Low Risk (Accept)

5. **Test Coverage Gaps**
   - **Risk:** Some edge cases not tested
   - **Mitigation:**
     - Target > 85% coverage
     - Manual testing with real assessments
     - Add tests as edge cases discovered

---

## Retrospective

**To be completed after sprint:**

### What Went Well
- [To be filled in]

### What Was Tricky
- [To be filled in]

### Lessons Learned
- [To be filled in]

### Future Improvements
- [To be filled in]

---

## Related Documents

- [ROADMAP.md](../../ROADMAP.md) - Strategic milestone planning
- [CHANGELOG.md](../../CHANGELOG.md) - Daily implementation log
- [README.md](../../README.md) - User-facing documentation
- [Software Development Protocol](../../../Nextcloud/AIED_EdTech_Dev_documentation/Software_Development_Protocol/) - Process guidelines

---

**Document Version:** 1.0
**Created:** 2025-11-10
**Last Updated:** 2025-11-10
**Status:** Planning Complete, Ready for Implementation
