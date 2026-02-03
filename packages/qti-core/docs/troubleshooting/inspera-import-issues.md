# Inspera Import Issues

This document lists known issues when importing QTI packages to Inspera, along with their solutions.

## Score-Related Issues

### Issue: Incorrect Maximum Scores After Import

**Problem:**
After importing a Question Set, Inspera displays incorrect maximum scores:
- Section shows 10.394 instead of 10
- Section shows 5.4 instead of 6
- Total score shows 121.009... instead of expected value

**Cause:**
The QTI package was missing explicit score declarations. Inspera attempted to calculate scores using its own heuristics, resulting in incorrect values.

**Solution:**
Ensure the assessmentTest XML includes:

1. `inspera:maximumScore` attribute on the root element
2. `<outcomeDeclaration>` for SCORE
3. `<outcomeProcessing>` block

**Fixed in:** Version after 2025-12-02

**Verification:**
```bash
grep "maximumScore" your_assessment.xml
```
Should show: `inspera:maximumScore="31.0"` (or your expected total)

---

### Issue: Section Pulling Wrong Number of Questions

**Problem:**
You configure "select 10 from 51" but Inspera shows different counts.

**Cause:**
1. Overlapping section filters causing duplicates
2. Inspera's duplicate detection removing questions
3. Filter logic matching unexpected questions

**Solution:**
1. Use the interactive script's duplicate prevention
2. Review logs to see actual matched question counts
3. Make section filters mutually exclusive

---

## Import Process Issues

### Issue: Import Hangs or Times Out

**Problem:**
The import process in Inspera gets stuck or times out.

**Possible Causes:**
- Large number of questions (>500)
- Large images in questions
- Network issues

**Solution:**
1. Split large question banks into smaller sets
2. Optimize images (max 500KB per image)
3. Try import during off-peak hours
4. Contact Inspera support if persistent

---

### Issue: "Invalid QTI Package" Error

**Problem:**
Inspera rejects the ZIP file with "Invalid QTI package" error.

**Common Causes:**

1. **Missing imsmanifest.xml**
   - Solution: Ensure `scripts/step5_create_zip.py` includes manifest generation

2. **Incorrect file structure**
   - Solution: ZIP should contain flat structure:
     ```
     your_quiz.zip
     ├── imsmanifest.xml
     ├── ID_ASSESSMENT_001-assessment.xml (if Question Set)
     ├── QUESTION_001-item.xml
     ├── QUESTION_002-item.xml
     └── ...
     ```

3. **XML namespace issues**
   - Solution: Verify namespaces in XML files:
     ```xml
     xmlns="http://www.imsglobal.org/xsd/imsqti_v2p2"
     xmlns:inspera="http://ns.inspera.no"
     ```

4. **Invalid XML syntax**
   - Solution: Validate XML before zipping:
     ```bash
     xmllint --noout ID_*-assessment.xml
     ```

---

## Question-Specific Issues

### Issue: Images Not Displaying

**Problem:**
Questions with images import successfully, but images don't display in Inspera.

**Causes:**
1. Image paths in XML don't match actual files
2. Images not included in ZIP
3. Unsupported image format
4. Image file names contain special characters

**Solution:**
1. Ensure `scripts/step3_copy_resources.py` ran successfully
2. Check `resource_mapping.json` for correct paths
3. Use supported formats: JPG, PNG, GIF
4. Avoid spaces and special characters in filenames
5. Verify images are in `resources/` folder in ZIP

---

### Issue: Special Characters Display Incorrectly

**Problem:**
Swedish characters (å, ä, ö) or special symbols display as garbage.

**Cause:**
Encoding mismatch between generation and import.

**Solution:**
1. Ensure all XML files are UTF-8 encoded
2. Check XML declaration: `<?xml version="1.0" encoding="UTF-8"?>`
3. Verify markdown source file is UTF-8

**Verification:**
```bash
file -I your_quiz_file.md
# Should show: charset=utf-8
```

---

### Issue: Math/LaTeX Not Rendering

**Problem:**
LaTeX expressions don't render as formulas in Inspera.

**Cause:**
Inspera requires MathML or specific LaTeX wrapping.

**Solution:**
1. Use `$$..$$` for display math
2. Use `$...$` for inline math
3. Ensure LaTeX is properly escaped in XML
4. Consider converting to MathML for better compatibility

**Note:** This may require additional configuration in the generator.

---

## Question Set (Assessment Test) Issues

### Issue: Sections Not Randomizing

**Problem:**
You set `shuffle="true"` but questions always appear in same order.

**Cause:**
1. Shuffle is set on section, not individual items
2. Browser caching in Inspera preview
3. Inspera configuration disabling shuffle

**Solution:**
1. Verify XML: `<ordering shuffle="true"/>`
2. Clear browser cache and retry
3. Test in actual Inspera assessment (not just preview)
4. Check Inspera test settings

---

### Issue: Selection Not Working

**Problem:**
You set `select="10"` but all questions appear.

**Cause:**
1. Selection element missing or malformed
2. Inspera not recognizing QTI 2.2 selection syntax

**Solution:**
1. Verify XML contains:
   ```xml
   <selection select="10"/>
   ```
2. Ensure it's placed before `<assessmentItemRef>` elements
3. Check Inspera version supports QTI 2.2 selection

---

## Metadata Issues

### Issue: Wrong Language in Inspera

**Problem:**
Questions appear with wrong language setting.

**Cause:**
Language code mismatch.

**Solution:**
1. Ensure `inspera:supportedLanguages` uses Inspera's format:
   - Swedish: `sv_se` (not `sv` or `se`)
   - English: `en_us` (not `en`)

2. Set in generation:
   ```python
   generator.generate(..., language='sv')
   ```

---

### Issue: Title or Metadata Missing

**Problem:**
Question bank shows "Untitled" or missing description.

**Cause:**
Metadata not properly set in markdown frontmatter or XML.

**Solution:**
1. Add frontmatter to markdown:
   ```yaml
   ---
   title: "EXAMPLE_COURSE Frågebank"
   identifier: "EXAMPLE_COURSE_001"
   ---
   ```

2. Or set in interactive mode when prompted

---

## Troubleshooting Steps

When encountering import issues:

1. **Check ZIP contents:**
   ```bash
   unzip -l your_quiz.zip | head -20
   ```

2. **Validate XML syntax:**
   ```bash
   xmllint --noout output/YOUR_QUIZ/*-item.xml
   xmllint --noout output/YOUR_QUIZ/ID_*-assessment.xml
   ```

3. **Check file sizes:**
   ```bash
   ls -lh output/YOUR_QUIZ/*.xml
   ```

4. **Review generation logs:**
   - Look for WARNING or ERROR messages
   - Check for "skipped" or "failed" notices

5. **Test with minimal set:**
   - Create quiz with 5 questions only
   - If that works, issue is likely scale-related

6. **Compare with working export:**
   - Export a known-working quiz from Inspera
   - Compare XML structure and attributes

## Getting Support

If you've tried the solutions above and still have issues:

1. Collect diagnostic information:
   - Generation logs (full output)
   - First 50 lines of generated assessment XML
   - Exact error message from Inspera
   - Number of questions and sections

2. Check for known issues:
   - Review CHANGELOG.md for recent fixes
   - Search GitHub issues

3. Create detailed bug report:
   - Include diagnostic information
   - Steps to reproduce
   - Expected vs actual behavior
   - Markdown file structure (sanitized if needed)

## Known Limitations

- Maximum 1000 questions per import (Inspera limit)
- Image file size limit: 10MB per image
- Total ZIP size limit: 100MB (may vary by Inspera instance)
- LaTeX support requires additional configuration
- Some HTML tags not supported in question text
- Nested sections not supported in QTI 2.2

## Additional Resources

- [QTI 2.2 Specification](http://www.imsglobal.org/question/)
- [Inspera Documentation](https://support.inspera.com/)
- Project CHANGELOG.md for version-specific fixes
- `docs/troubleshooting/question-set-debugging.md` for Question Set issues
