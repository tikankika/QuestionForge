# Roadmap: QTI Generator Feature Development

**Version**: 1.0
**Last Updated**: 2025-11-01
**Protocol Level**: 2 (6-12 Month Feature Planning)
**Current Release**: v0.2.3-alpha

---

## Current Status: v0.2.3-alpha (Released: 2025-11-01)

### Implemented Features
- **3 Production-Ready Question Types**: `multiple_choice_single`, `extended_text`, `text_area`
- **1 Beta Question Type**: `multiple_response` (basic scoring)
- **15 Complete XML Templates**: 87% coverage of Inspera question types
- **Custom Label System**: User-controlled labels via **Labels**: field in markdown (no auto-generation)
- **Markdown-to-QTI Converter**: Operational CLI tool (`python main.py`)
- **Package Validation**: QTI ZIP inspection and structure verification
- **Comprehensive Documentation**: 16 question type templates, metadata reference, specification

### Recent Additions (2025-11-02 - Session 2)

#### Question Bank Conversion Pipeline
- **`scripts/convert_evolution_format.py`**: Transform dual-structure markdown to QTI Generator format
  - Extracts labels from separate metadata sections
  - Generates YAML frontmatter with test metadata
  - Merges into inline **Labels**: field
- **`scripts/filter_supported_questions.py`**: Filter question banks to only supported types
  - Reports statistics on skipped questions by type
  - Enables processing partial question banks
- **Case Study**: Successfully converted 68-question Evolution bank (56 supported, 12 skipped)

#### Breaking Change: Custom Labels Only
- Removed auto-generated labels from subject, learning objectives, Bloom's level, question type
- Users now have complete control via **Labels**: field in markdown
- Aligns with actual Inspera export format (plain text, no prefixes)
- **Migration Impact**: Existing markdown files with **Labels**: field unaffected; auto-generation feature removed

### Known Limitations
- Converter only supports 4 question types (XML templates ready for 15)
- **BLOCKERS**: 12 Evolution questions cannot be converted (missing types: true_false, multiple_choice_multiple, fill_blank)
- Multiple Response lacks advanced partial credit logic
- No batch conversion utilities (manual 3-step pipeline)
- No cross-platform export (Inspera only)
- No automated testing framework

### Known Issues
- **gap_match / gapmatch question type NOT FUNCTIONAL** (Added: 2025-11-09)
  - Template exists (`templates/xml/gapmatch.xml`) but generator implementation incomplete
  - XML generation fails: placeholders (`{{GAP-N}}`, `{{GAP_ITEMS}}`, `{{REUSE_ALTERNATIVES}}`, etc.) not replaced
  - Results in invalid QTI XML that Inspera cannot parse
  - **Error in Inspera**: "Inte översatt" (Not translated) - question cannot be opened
  - **Workaround**: Remove gap_match questions from assessment or convert to other types (e.g., inline_choice, multiple_choice)
  - **Status**: Needs implementation in `src/generator/xml_generator.py` - `_build_gapmatch_replacements()` method
  - **Impact**: Questions using `**Type**: gap_match` or `**Type**: gapmatch` will fail QTI generation
  - **Validation**: Type has been commented out in `validate_mqg_format.py` to prevent usage until fixed

---

## Milestone v0.3.0 (Target: 2025-12-15) ⚠️ OVERDUE
**Theme**: Core Question Type Expansion
**Duration**: 6 weeks
**Priority**: High

### Priority Summary

| Priority | Item | Status | Impact |
|----------|------|--------|--------|
| **P0** | True/False | 🔴 Not started | Blocks 6 questions |
| **P0** | Multiple Response | 🟡 Partial | Blocks 4 questions |
| **P1** | Fill-in-the-Blank | 🔴 Not started | Blocks 2 questions |
| **P2** | Matching | 🟡 Template ready | - |

### Question Type Implementations

#### True/False (`true_false`) 🔴
**Status**: XML template needed
**Priority**: P0 - Evolution bank blocker (6 questions)
- [ ] Analyze Inspera export format for true/false questions
- [ ] Create `true_false.xml` template based on Inspera exports
- [ ] Implement converter logic with boolean response handling
- [ ] Add validation for True/False format in markdown parser
- [ ] Create example questions using MQG Framework specifications (BB6A)
- [ ] Test import into Inspera Assessment Suite (Evolution questions)

**Complexity**: Low | **Effort**: 1 week | **Value**: Very High (Evolution blocker, widely used)
**Reference**: Evolution bank questions need this type

#### Fill-in-the-Blank (`fill_blank`) 🔴
**Status**: XML template needed
**Priority**: P1 - Evolution bank blocker (2 questions)
- [ ] Analyze Inspera export format for fill-in-the-blank questions
- [ ] Create `fill_blank.xml` template (single blank, string matching)
- [ ] Implement string comparison logic (case-sensitive/insensitive)
- [ ] Support multiple acceptable answer variants
- [ ] Add expected length hints for student interface
- [ ] Distinguish from `text_entry` (multiple blanks)
- [ ] Test with Evolution bank questions

**Complexity**: Medium | **Effort**: 1.5 weeks | **Value**: High (common in language/STEM)
**Reference**: 2 Evolution bank questions need this type

#### Matching (`matching`) 🟡
**Status**: XML template complete (`match.xml`)
**Priority**: P2
- [ ] Implement converter logic for directed pair mapping
- [ ] Generate `correctResponse` values from markdown pairings
- [ ] Create `mapEntry` elements for partial credit scoring
- [ ] Handle randomization and shuffle options
- [ ] Support distractor items (more responses than premises)

**Complexity**: Medium | **Effort**: 2 weeks | **Value**: Medium (used in definition/concept matching)

#### Multiple Response Enhancement / Multiple Choice Multiple (`multiple_response` / `multiple_choice_multiple`) 🟡
**Status**: Partial implementation (basic scoring only)
**Priority**: P0 - Evolution bank blocker (4 questions)
- [ ] Analyze if `multiple_choice_multiple` is distinct from `multiple_response` in Inspera
- [ ] Implement advanced partial credit mapping logic
- [ ] Generate `CORRECT_MATCH_LOGIC` placeholder content
- [ ] Generate `PARTIAL_MATCH_LOGIC` placeholder content
- [ ] Create `MAPPING_ENTRIES` from correct/incorrect choices
- [ ] Add configuration options for scoring strategies (all-or-nothing vs. partial credit)
- [ ] Test with Evolution bank questions (4 questions need this)

**Complexity**: High | **Effort**: 1.5 weeks | **Value**: Very High (Evolution blocker, common type)
**Note**: Determine if this is same as `multiple_response` or requires separate implementation
**Reference**: 4 Evolution bank questions need multiple_choice_multiple type

### Technical Improvements
- [ ] Refactor `xml_generator.py` to support type-specific placeholder generation
- [ ] Improve validation error messages with line numbers and context
- [ ] Add `--validate-only` CLI flag for checking markdown before conversion
- [ ] Performance optimization for large question banks (100+ questions)
- [ ] Template placeholder documentation in CLI help text

### Scripts and Utilities

#### Question Bank Conversion Pipeline
**Status**: Operational (v0.2.3-alpha)
- [x] `scripts/convert_evolution_format.py` - Convert dual-structure markdown to QTI format
- [x] `scripts/filter_supported_questions.py` - Filter unsupported question types
- [x] YAML frontmatter generation for test metadata
- [x] Label merging from separate metadata sections
- [ ] **v0.3.0**: Integrate conversion scripts into main.py CLI
- [ ] **v0.3.0**: Add batch directory processing mode (convert all .md files in folder)
- [ ] **v0.3.0**: Support additional source formats (CSV, Excel imports)
- [ ] **v0.3.0**: Generate validation reports with statistics on skipped questions
- [ ] **v0.3.0**: Add unit tests for conversion utilities
- [ ] **v0.3.0**: Create scripts/README.md documentation

**Workflow**: Convert → Filter → Generate QTI
**Use Cases**:
- Converting external question banks to QTI Generator format
- Filtering large banks to only supported question types
- Preprocessing before QTI generation

**Current Limitations**:
- Manual execution of 3-step pipeline
- No integration with main.py CLI (separate commands)
- No automated testing of conversion scripts
- Single-file processing only (no batch mode)

**Effort**: 1 week | **Value**: Medium (improves workflow efficiency)

### Documentation
- [ ] Update MQG Framework specifications (BB6A) with production-ready status for v0.3.0 types
- [ ] Create video tutorial: "Getting Started with QTI Generator"
- [ ] Write migration guide from Excel-based workflow to Markdown
- [ ] Document scoring strategies for Multiple Response questions
- [ ] Add troubleshooting guide for common conversion errors

### Testing & Quality
- [ ] Create integration test suite (pytest framework)
- [ ] Test all v0.3.0 types with real Inspera imports
- [ ] Performance benchmarks: 100 questions in <5 seconds
- [ ] Accessibility validation for generated QTI

### Success Criteria
- ✅ **7 production-ready question types** (up from 3)
- ✅ **65% coverage** of analyzed question type usage
- ✅ **<3 seconds** conversion time for 100-question assessment
- ✅ **Zero critical bugs** in Inspera import for supported types
- ✅ **User documentation** complete for all v0.3.0 types

**Risk Mitigation**: True/False template development may encounter Inspera-specific quirks; allocate buffer time for testing cycles.

---

## Milestone v0.4.0 (Target: 2026-02-15)
**Theme**: Advanced Interaction Types
**Duration**: 10 weeks
**Priority**: Medium

### Question Type Implementations (9 Advanced Types)

All XML templates already exist and are validated. Implementation focuses on **converter logic** for complex placeholder generation.

#### Inline Choice (`inline_choice`)
**Status**: XML template ready
- [ ] Multi-dropdown interaction converter
- [ ] Generate response declarations for each dropdown
- [ ] Per-dropdown feedback generation
- [ ] Support for `feedbackInline` elements

**Complexity**: High | **Effort**: 2 weeks

#### Text Entry (`text_entry`)
**Status**: XML template ready
- [ ] Multiple fill-in-the-blank fields within text
- [ ] String matching logic for each field
- [ ] Per-field correctness tracking
- [ ] Distinguish from `fill_blank` (single field)

**Complexity**: High | **Effort**: 2 weeks

#### Gap Match (`gapmatch`)
**Status**: XML template ready
- [ ] Drag-and-drop text/images into gaps
- [ ] Directed pair mapping for gap associations
- [ ] Support for reusable alternatives
- [ ] Token positioning and ordering options

**Complexity**: High | **Effort**: 2 weeks

#### Hotspot (`hotspot`)
**Status**: XML template ready
- [ ] Click on image regions (rect/circle shapes)
- [ ] Coordinate-based interaction handling
- [ ] Shape coloring and visual feedback
- [ ] Canvas height and image scaling

**Complexity**: Medium | **Effort**: 1.5 weeks

#### Graphic Gap Match (`graphicgapmatch`)
**Status**: XML template ready (`graphicgapmatch_v2.xml`)
- [ ] Drag text/images onto image hotspots
- [ ] Combine gap match + hotspot logic
- [ ] Token sizing and positioning
- [ ] Hotspot shape definition (rect/circle)

**Complexity**: Very High | **Effort**: 2.5 weeks

#### Text Entry Graphic (`text_entry_graphic`)
**Status**: XML template ready
- [ ] Multiple text fields positioned over image
- [ ] Absolute CSS positioning logic
- [ ] Per-field string matching
- [ ] Image dimension handling

**Complexity**: High | **Effort**: 2 weeks

#### Audio Record (`audio_record`)
**Status**: XML template ready
- [ ] File upload interaction for audio
- [ ] Manual grading rubric generation
- [ ] Simple answered/unanswered feedback
- [ ] Upload prompt configuration

**Complexity**: Low | **Effort**: 1 week

#### Composite Editor (`composite_editor`)
**Status**: XML template ready
- [ ] Mix multiple interaction types in single question
- [ ] Per-sub-question scoring aggregation
- [ ] Complex response processing generation
- [ ] Support text entry + choice combinations

**Complexity**: Very High | **Effort**: 3 weeks

#### Native HTML (`nativehtml`)
**Status**: XML template ready
- [ ] Non-scored instructional content
- [ ] Rich HTML rendering
- [ ] Section breaks and information blocks
- [ ] Language attribute support

**Complexity**: Low | **Effort**: 0.5 weeks

### Technical Infrastructure
- [ ] Image asset management: packaging, validation, path resolution
- [ ] Audio file upload handling and validation
- [ ] Multi-field interaction architecture (shared converter base class)
- [ ] Coordinate system abstraction for image-based interactions
- [ ] Resource manifest generation for media assets

### Quality Assurance
- [ ] Comprehensive integration tests for all 16 question types
- [ ] Inspera import validation for every type
- [ ] Performance benchmarks: 1000-question bank in <30 seconds
- [ ] Cross-browser rendering tests (Inspera student interface)
- [ ] Accessibility audit (WCAG 2.1 AA compliance)

### Documentation
- [ ] Complete examples for all v0.4.0 types in templates
- [ ] Developer guide: Adding custom question types
- [ ] Architecture documentation: Converter design patterns
- [ ] Media asset guide: Images, audio, video handling

### Success Criteria
- ✅ **All 16 documented question types operational**
- ✅ **87% coverage** of analyzed Inspera question types
- ✅ **Media handling** for images and audio files
- ✅ **Performance target**: 1000 questions in <30 seconds
- ✅ **Accessibility compliance** validated

**Risk Mitigation**: Image-based interactions (hotspot, graphic gap match) are highest complexity; prioritize early to surface technical challenges.

---

## Milestone v0.5.0 (Target: 2026-04-15)
**Theme**: Multi-Platform Export
**Duration**: 8 weeks
**Priority**: High

### Cross-Platform Support

#### Canvas QTI Export
- [ ] Implement QTI 1.2 format (Canvas-specific)
- [ ] Question type mapping: Inspera → Canvas equivalents
- [ ] Canvas-specific metadata and styling
- [ ] Import validation in Canvas LMS test instance

**Effort**: 3 weeks | **Value**: Very High (largest LMS)

#### Moodle XML Export
- [ ] Moodle Question XML format implementation
- [ ] Question type mapping: Inspera → Moodle
- [ ] Category and tag structure
- [ ] Import validation in Moodle test instance

**Effort**: 2 weeks | **Value**: High (popular in academia)

#### Blackboard Export
- [ ] Blackboard pool format support
- [ ] Question type mapping and limitations
- [ ] Import validation in Blackboard test instance

**Effort**: 2 weeks | **Value**: Medium (institutional use)

#### Platform Detection
- [ ] Auto-detect target platform from CLI flags or configuration
- [ ] Format-specific validation rules
- [ ] Export format selection interface

**Effort**: 1 week

### Enhanced Validation

#### Schema Validation
- [ ] QTI 2.2 XSD schema validation (Inspera)
- [ ] QTI 1.2 schema validation (Canvas)
- [ ] Moodle XML schema validation
- [ ] Validation error reporting with actionable fixes

**Effort**: 2 weeks

#### Accessibility Compliance
- [ ] WCAG 2.1 AA automated checks
- [ ] Alt text requirements for images
- [ ] Proper heading hierarchy
- [ ] Color contrast validation for styled content

**Effort**: 1.5 weeks

#### Question Quality Metrics
- [ ] Bloom's level distribution dashboard
- [ ] Learning objective coverage analysis
- [ ] Question bank statistics (difficulty, discrimination estimates)
- [ ] Readability scores (Flesch-Kincaid)

**Effort**: 2 weeks

### Tooling Enhancements

#### Batch Conversion CLI
- [ ] Convert entire folder of markdown files
- [ ] Progress reporting for large batches
- [ ] Error aggregation and reporting
- [ ] Parallel processing for performance

**Effort**: 1 week

#### Web Preview Interface
- [ ] Generate HTML preview of QTI questions
- [ ] Interactive demo of question interactions
- [ ] Pre-import validation checks
- [ ] Export to PDF for review

**Effort**: 2 weeks

#### Question Bank Diff Tool
- [ ] Compare two versions of question bank
- [ ] Highlight changes, additions, deletions
- [ ] Version control integration (git diff support)
- [ ] Generate change reports for review

**Effort**: 1.5 weeks

### Success Criteria
- ✅ **4 export platforms** supported (Inspera, Canvas, Moodle, Blackboard)
- ✅ **Automated validation** for all formats
- ✅ **Accessibility compliance** enforced
- ✅ **Batch conversion** operational
- ✅ **Quality metrics** dashboard functional

**Risk Mitigation**: Platform-specific quirks may require additional testing cycles; maintain test LMS instances for validation.

---

## Milestone v1.0.0 (Target: 2026-06-01)
**Theme**: Production-Ready Stable Release
**Duration**: 6 weeks
**Priority**: Critical

### Stability & Quality

#### Comprehensive Testing
- [ ] Unit test coverage >90% (pytest + coverage.py)
- [ ] Integration tests for all question types × all platforms
- [ ] Performance regression test suite
- [ ] Stress testing: 10,000-question banks
- [ ] Memory leak detection and profiling

**Effort**: 2 weeks

#### Bug Elimination
- [ ] Triage and fix all open GitHub issues
- [ ] Field testing with 20+ beta users
- [ ] Edge case testing (unusual markdown, complex questions)
- [ ] Zero critical or high-severity bugs

**Effort**: 2 weeks

#### Performance Optimization
- [ ] Sub-second conversion for 100 questions (currently 3 seconds)
- [ ] Parallel processing for batch conversions
- [ ] Memory optimization for large question banks
- [ ] Caching for repeated conversions

**Effort**: 1 week

### Documentation & Guides

#### User Documentation
- [ ] Complete user guide (all 16 question types)
- [ ] Quick start tutorial with video
- [ ] Best practices guide for assessment design
- [ ] Troubleshooting guide (common errors + solutions)
- [ ] FAQ section

**Effort**: 1.5 weeks

#### Developer Documentation
- [ ] API documentation (all public methods)
- [ ] Architecture overview and design decisions
- [ ] Contributing guide (how to add question types)
- [ ] Code style guide and conventions
- [ ] Release process documentation

**Effort**: 1 week

#### Assessment Design Guide
- [ ] Evidence-based assessment creation
- [ ] Bloom's taxonomy application
- [ ] Learning objective alignment
- [ ] Feedback writing best practices
- [ ] Accessibility considerations

**Effort**: 1 week

### Community Infrastructure

#### Open Source Essentials
- [ ] CODE_OF_CONDUCT.md (Contributor Covenant)
- [ ] SECURITY.md (vulnerability reporting process)
- [ ] CONTRIBUTING.md (comprehensive contributor guide)
- [ ] Issue templates (bug report, feature request)
- [ ] Pull request template with checklist

**Effort**: 0.5 weeks

#### Communication Channels
- [ ] GitHub Discussions enabled
- [ ] Documentation website (GitHub Pages)
- [ ] Announcement/newsletter setup
- [ ] User survey for feedback collection

**Effort**: 0.5 weeks

### Release Management

#### PyPI Publication
- [ ] Package metadata and versioning
- [ ] Build and distribution pipeline
- [ ] Automated release workflow (GitHub Actions)
- [ ] Installation documentation

**Effort**: 1 week

#### Semantic Versioning
- [ ] Enforce semver conventions (MAJOR.MINOR.PATCH)
- [ ] Changelog generation from git commits
- [ ] Version bumping automation
- [ ] Deprecation policy documentation

**Effort**: 0.5 weeks

#### Migration Guide
- [ ] Document breaking changes from alpha/beta
- [ ] Provide migration scripts for v0.x → v1.0
- [ ] Example conversions showing before/after
- [ ] Deprecation warnings in v0.5.0

**Effort**: 1 week

### Success Criteria
- ✅ **Zero critical bugs** from field testing (20+ users)
- ✅ **>90% test coverage** automated
- ✅ **Complete documentation** (user + developer)
- ✅ **PyPI package** published and installable
- ✅ **Production-ready** stable release

**Risk Mitigation**: Field testing may reveal unanticipated issues; budget 2-week buffer for fixes.

---

## Post-v1.0 Vision (v1.x and v2.0)

### Potential Future Directions
*Features below moved to IDEAS.md for community discussion and prioritization.*

#### Question Bank Management UI (v1.5)
- Web-based interface for non-command-line users
- Visual question editor with live preview
- Question bank organization and tagging
- Export wizard with platform selection

#### Real-Time Collaboration (v2.0)
- Google Docs-style simultaneous editing
- Conflict resolution and merge strategies
- Comment/review workflow for team development
- Version history and rollback

#### AI-Assisted Features (v2.0)
- Auto-generate distractors for multiple choice
- Suggest Bloom's level from question text analysis
- Generate questions from learning objective descriptions
- Automated feedback generation

#### Cloud Service Option (v2.0)
- SaaS deployment for ease of use
- User accounts and question bank hosting
- Collaboration features (sharing, permissions)
- Export to multiple platforms from web interface

#### Statistical Analysis (v1.5)
- Item difficulty and discrimination analysis
- Reliability estimates (KR-20, Cronbach's alpha)
- Distractor analysis and recommendations
- Question bank quality dashboards

---

## Version Timeline Summary

| Version | Target Date | Duration | Key Features | Question Types | Coverage |
|---------|-------------|----------|--------------|----------------|----------|
| v0.2.3-alpha | 2025-11-01 | Released | Metadata labels, 15 XML templates | 4 types | 52.6% |
| **v0.3.0** | **2025-12-15** | **6 weeks** | **Core question expansion** | **7 types** | **65%** |
| **v0.4.0** | **2026-02-15** | **10 weeks** | **Advanced interactions** | **16 types** | **87%** |
| **v0.5.0** | **2026-04-15** | **8 weeks** | **Multi-platform export** | 16 types | 87% |
| **v1.0.0** | **2026-06-01** | **6 weeks** | **Stable production release** | 16 types | 87% |
| v1.5.0 | 2026-10-01 | TBD | Statistical analysis, UI | 16+ types | 90%+ |
| v2.0.0 | 2027-06-01 | TBD | Cloud service, AI features | 20+ types | 95%+ |

---

## Review and Adaptation

This roadmap is reviewed and updated:
- **Biweekly** during sprint planning (tactical adjustments)
- **Monthly** during retrospectives (feature prioritization)
- **Quarterly** for strategic alignment with VISION.md

Changes to this roadmap are documented in CHANGELOG.md with rationale for adjustments.

---

**Maintenance Notes**:
- Milestone targets are estimates; actual dates may shift based on complexity discoveries
- User feedback may reprioritize features between milestones
- Technical debt addressed incrementally rather than accumulated for major refactor
- Security vulnerabilities addressed immediately outside normal sprint cadence

---

**Document Metadata**:
- **Protocol Document**: Level 2 Planning (6-12 Month Features)
- **Review Schedule**: Monthly (during retrospectives)
- **Last Major Revision**: 2025-11-01
- **Next Review**: 2025-12-01
