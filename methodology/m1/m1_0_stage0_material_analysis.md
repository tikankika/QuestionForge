
## STAGE 0: MATERIAL ANALYSIS

**Duration:** 60-90 minutes
**Nature:** Claude's independent analysis before dialogue
**Purpose:** Understand instructional content to prepare for dialogue

---

### ⚠️ KRITISK WORKFLOW: Hur du läser material

**Du har INTE direkt tillgång till användarens filer.** Följ detta workflow:

```
┌─────────────────────────────────────────────────────────────────┐
│ STEG-FÖR-STEG WORKFLOW                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 1. LISTA filer (MCP):                                           │
│    read_materials(project_path="...", filename=null)            │
│    → Får tillbaka: ["fil1.pdf", "fil2.pdf", ...]                │
│                                                                 │
│ 2. BE användaren ladda upp FÖRSTA filen:                        │
│    "Ladda upp [fil1.pdf] till chatten så analyserar jag den."   │
│    (Dra-och-släpp eller klicka på gem-ikonen)                   │
│                                                                 │
│ 3. VÄNTA tills användaren laddat upp filen                      │
│                                                                 │
│ 4. ANALYSERA PDF:en med dina inbyggda multimodala förmågor      │
│                                                                 │
│ 5. PRESENTERA analys för användaren och be om feedback          │
│                                                                 │
│ 6. SPARA analysen (MCP):                                        │
│    save_m1_progress(action="add_material", data={material:...}) │
│                                                                 │
│ 7. UPPREPA steg 2-6 för varje fil                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**VARFÖR detta workflow?**
- Du (Claude.ai) har **bättre PDF-läsning** än MCP:ens enkla textextraktion
- Du kan se bilder, tabeller och formatering i PDF:er
- MCP:ens `read_materials(filename="X.pdf")` är endast en FALLBACK

**Exempeldialog:**
```
Claude: "Jag ser 10 filer i materialmappen. Låt oss börja med
         'Vad är AI.pdf'. Ladda upp den till chatten så analyserar
         jag den."

Användaren: [Drar PDF till chatten]

Claude: [Analyserar PDF, presenterar findings]
        "Vill du justera något innan jag sparar och går vidare?"

Användaren: "Ser bra ut!"

Claude: [Anropar save_m1_progress]
        "Sparat! Ladda upp nästa fil: 'Hur fungerar GenAI.pdf'"
```

---

### FOR CLAUDE: Pre-Dialogue Analysis Strategy

#### Input Materials
Teachers provide:
- Lecture recordings or transcripts
- Presentation slides (PowerPoint, PDF, Keynote)
- Assigned readings with specific page numbers
- Handouts, worksheets, supplementary materials
- Lab instructions or activity guides (if applicable)
- Course syllabus with learning objectives (if available)

#### Systematic Analysis Process

**1. Read All Materials Thoroughly**
- Process materials in chronological order (as students experienced them)
- Note timestamps in recordings for reference
- Identify major topics and subtopics
- Map relationships between concepts

**2. Identify Content Emphasis Patterns**

Look for multiple signals of importance:

**Repetition (Strong Signal):**
- Concepts mentioned 3+ times across materials
- Topics revisited in multiple contexts
- Ideas referenced in summaries or reviews

**Time Allocation (Strong Signal):**
- Topics with longest coverage duration
- Concepts explored in depth vs. mentioned briefly
- Multi-part explanations or demonstrations

**Explicit Prioritization (Strongest Signal):**
- "This will be on the test"
- "Remember this for the exam"
- "This is really important"
- "Make sure you understand..."
- "I cannot stress enough..."

**Instructional Investment (Strong Signal):**
- Multiple examples for same concept
- Demonstrations or activities
- Practice problems or exercises
- Detailed explanations or clarifications

**Student Struggle Indicators (Important Signal):**
- "This is tricky"
- Repeated clarifications
- Multiple approaches to same concept
- Misconception corrections

**3. Catalog Instructional Examples**
Document major examples used to illustrate concepts:
- What concept each example illustrates
- Where it appears in materials
- How it was used (demonstration, comparison, application)

**4. Identify Misconceptions Addressed**
Note when instructor:
- Corrects common errors
- Says "students often think..." or "a common mistake is..."
- Emphasizes distinctions between confused concepts
- Warns against oversimplifications

**5. Establish Initial Content Architecture**

Organize content into priority tiers:

**TIER 1 - Essential (Highest Priority):**
- Multiple emphasis signals (repetition + time + explicit priority)
- Foundation for other concepts
- Designated as critical by instructor

**TIER 2 - Important (Secondary Priority):**
- Substantial coverage but less explicit emphasis
- Supporting concepts that connect to Tier 1
- Moderate instructional time

**TIER 3 - Supplementary (Context/Background):**
- Brief mentions
- Contextual information
- Optional enrichment

**TIER 4 - Out of Scope (Explicitly Excluded):**
- Mentioned but skipped ("we won't cover this")
- Started but time ran out
- Designated as "beyond this course"
- Advanced topics for later courses

---

#### Handling Incomplete or Ambiguous Materials

**If materials are incomplete:**
- Note gaps explicitly in Stage 0 output
- Flag missing components for teacher clarification in Stage 1
- Make best analysis with available materials
- Document assumptions made

**If no explicit priority signals exist:**
- Rely primarily on time allocation and repetition patterns
- Use depth of explanation and number of examples as secondary signals
- Note the absence of explicit signals in output
- Flag ambiguity for teacher validation in Stage 1

**If tier boundaries are unclear:**
- Make best judgment based on available evidence
- Document reasoning for tier assignments
- Use broader tier ranges when uncertain (e.g., "Tier 1 or 2")
- Expect significant refinement during Stage 1 validation

**If everything seems equally emphasized:**
- Look for subtle differences in treatment
- Consider prerequisite relationships (foundational topics likely Tier 1)
- Note the challenge in analysis output
- Defer to teacher expertise in Stage 1

**Remember:** Stage 0 is initial analysis, not final determination. Stage 1 validation will correct misinterpretations and refine categorizations. It's better to produce a directionally accurate analysis quickly than to agonize over perfect precision.

---

#### Stage 0 Output Format

Present findings in structured format:

```markdown
# STAGE 0: MATERIAL ANALYSIS COMPLETE

## Materials Analyzed
- [List all materials with dates/versions]

## Content Emphasis Patterns

### TIER 1: Essential Content (Highest Priority)
**Evidence: Multiple emphasis signals**

1. **[Topic A]**
   - Repetition: Mentioned [N] times across [lectures/materials]
   - Time: Approximately [N] minutes total coverage
   - Explicit priority: "[Quote instructor statement]"
   - Instructional investment: [Examples, demonstrations, activities]
   
2. **[Topic B]**
   - [Similar evidence structure]

### TIER 2: Important Content (Secondary Priority)
**Evidence: Substantial coverage**

1. **[Topic C]**
   - Time: [N] minutes coverage
   - Connection: Supports understanding of [Tier 1 topics]
   
### TIER 3: Supplementary Content (Background)
- [Topic E]: Brief mention in [location]
- [Topic F]: Contextual information

### TIER 4: Out of Scope (Explicitly Excluded)
- [Topic X]: Mentioned but skipped due to [reason]
- [Topic Y]: Designated as "[instructor quote]"

## Key Instructional Examples
1. **[Example Name/Description]**
   - Location: [Lecture X, timestamp/slide]
   - Illustrates: [Concept]
   - Type: [Demonstration/Comparison/Application]

2. **[Example Name]**
   - [Similar structure]

[Continue for 5-10 major examples]

## Addressed Misconceptions
1. **[Misconception]**: [Student error]
   - Correction: [Instructor clarification]
   - Location: [Where addressed]

2. **[Misconception]**: [Student error]
   - [Similar structure]

[Continue for major misconceptions]
```

#### Quality Check Before Presenting

Before moving to Stage 1, verify:
- [ ] All materials read thoroughly
- [ ] Clear Tier 1 content identified (2-5 major topics)
- [ ] Evidence cited for each tier assignment
- [ ] At least 5 major examples cataloged
- [ ] Common misconceptions noted (if addressed)
- [ ] Scope boundaries identified (what's out)
- [ ] Ready to present for teacher validation

---

### FOR TEACHERS: What Happens in Stage 0

**What Claude Is Doing:**
Reading all your instructional materials to understand what you taught, what you emphasized, and how you taught it. This takes 60-90 minutes and happens before your dialogue begins.

**Why This Matters:**
When dialogue starts, Claude will present findings about your teaching for validation. This makes the dialogue much more efficient—you confirm or correct rather than explaining everything from scratch. By doing the heavy analytical work upfront, Claude can focus the dialogue on refinement and validation rather than basic information gathering.

**What to Expect:**
Stage 0 analysis will be directionally accurate but not perfect. Claude identifies patterns in your materials, but you know your teaching better than any AI. Expect to correct some tier assignments, add context Claude missed, and clarify priorities. This is normal and expected—the goal is to start the dialogue with a strong foundation, not to eliminate the need for your expertise.

**What You Don't Need to Do:**
Nothing! This stage is Claude's independent preparation. Relax and wait for Stage 1.

---

## STAGE 0 COMPLETION CHECKPOINT

**When Stage 0 analysis is complete:**

### CRITICAL: STOP HERE

**DO NOT PROCEED AUTOMATICALLY TO STAGE 1**

### Required Actions:

1. **PRESENT** the Stage 0 output document to the teacher
2. **STOP** and WAIT for teacher response
3. **Teacher must explicitly approve** before proceeding

### Stage 1 Requirements:

**Before proceeding to Stage 1, you MUST have:**
- ✅ bb1c (Stage1_Initial_Validation.md) instructions loaded
- ✅ Teacher has reviewed Stage 0 output
- ✅ Teacher explicitly says: "Start Stage 1" or "Proceed to validation"

### DO NOT:

- ❌ Start Stage 1 dialogue without teacher request
- ❌ Proceed without bb1c instructions loaded
- ❌ Improvise validation questions
- ❌ Assume teacher approval
- ❌ Continue to next stage automatically

### Transition Statement:

After presenting Stage 0 output, say:

"Stage 0 analysis is now complete. I have presented my findings above.

To proceed to Stage 1 (Initial Validation), I need:
1. Your feedback on this analysis
2. Explicit instruction to proceed
3. bb1c file loaded (Stage 1 instructions)

Please review the analysis and let me know when you're ready to start Stage 1."

---

**Stage 0 Status:** ✅ COMPLETE - AWAITING TEACHER APPROVAL TO PROCEED
