# RFC-014: Resource Handling for Complex Question Types

**Status:** DRAFT
**Created:** 2026-01-28
**Author:** QuestionForge Team
**Deferred from:** RFC-013 Step 1 (Vision A refactor)

---

## Summary

Handle resource-rich question types that require:
- Image attachments and previews
- Audio file management
- Coordinate-based interactions (hotspots, drag-and-drop)
- Visual verification by teacher

## Motivation

During the RFC-013 Step 1 refactor, we identified that resource handling is a distinct concern that deserves its own RFC. Simple text-based questions can flow through the pipeline without manual intervention, but complex question types need specialized tooling.

## Question Types Requiring Resource Handling

| Type | Resources | Needs Visual Verification |
|------|-----------|--------------------------|
| `hotspot` | Image + coordinates | Yes - zones on image |
| `graphicgapmatch_v2` | Image + drop zones | Yes - drag targets |
| `audio_record` | Audio file | Yes - playback test |
| `text_entry_graphic` | Image + text fields | Yes - field positions |
| Any with `@field: image` | Image file | Yes - display check |

## Proposed Features

### 1. Resource Discovery
- Find referenced files in project
- Validate file existence
- Map relative ↔ absolute paths

### 2. Resource Preview
- Display images in terminal (ASCII art?) or open in viewer
- Audio playback capability
- Coordinate overlay visualization

### 3. Coordinate Editor
- View zones on image
- Adjust coordinates interactively
- Validate bounds

### 4. Path Management
- Normalize file paths
- Copy resources to output
- Update references in markdown

## Implementation Notes

- May require GUI component (web viewer?)
- Consider integration with Claude Desktop's capabilities
- Reference archived Step 1 code in `step1/_archived/` for patterns

## Timeline

TBD - Lower priority than current pipeline stabilization.

## Related Documents

- RFC-013 v2.5: Step 1 Vision A refactor
- `step1/_archived/README.md`: Archived code reference
- `docs/analysis/Step1_Critical_Analysis_2026-01-28.md`: Analysis that identified this need
