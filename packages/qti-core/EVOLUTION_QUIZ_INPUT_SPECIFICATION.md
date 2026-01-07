# Evolution Quiz - QTI Generator Input Specification

**Purpose**: This document shows the EXACT markdown format required for the Python QTI Generator scripts to successfully convert Evolution quiz questions to QTI 2.2 XML for Inspera import.

**Target Output**: `/Users/niklaskarlsson/QTI-Generator-for-Inspera/output/test02_evolution_biog001x_QTI/`

**Process**:
1. Claude Desktop + Teacher dialogue → Creates markdown following THIS specification
2. Python `markdown_parser.py` → Parses markdown to extract questions
3. Python `xml_generator.py` → Converts to QTI 2.2 XML
4. ZIP package ready for Inspera import

---

## ✅ EXACT FORMAT SPECIFICATION

### 1. File Header - YAML Frontmatter (REQUIRED)

**Location**: Top of file
**Delimiters**: Three dashes `---` on separate lines

```yaml
---
test_metadata:
  title: "Evolution Quiz - Formativ Bedömning"
  identifier: "BIOG1000X_EVOLUTION_FORMATIV_2025"
  language: "sv"
  description: "60 frågor om evolution för Biologi nivå 1"
  subject: "BIOG1000X"
  author: "Niklas"
  created_date: "2025-11-02"

assessment_configuration:
  type: "formative"
  time_limit: 90
  shuffle_questions: true
  shuffle_choices: true
  feedback_mode: "immediate"
  attempts_allowed: 3

learning_objectives:
  - id: "LO1"
    description: "Redogöra för grundprinciperna i Darwins evolutionsteori och naturligt urval"
  - id: "LO2"
    description: "Förklara hur variation, ärftlighet och selektion samverkar i naturligt urval"
  - id: "LO3"
    description: "Tillämpa kunskaper om naturligt urval för att predicera förändringar i populationer"
  - id: "LO4"
    description: "Analysera olika typer av urval (riktat, stabiliserande, disruptivt) och deras effekter"
  - id: "LO5"
    description: "Förklara sexuell selektion och dess roll i evolutionen"
  - id: "LO6"
    description: "Analysera hur artbildning sker genom geografisk och reproduktiv isolering"
  - id: "LO7"
    description: "Förklara genetisk drift och dess betydelse i evolutionära processer"
  - id: "LO8"
    description: "Beskriva hypoteser om livets uppkomst och kemisk evolution"
  - id: "LO9"
    description: "Utvärdera vetenskapliga påståenden om evolution och skilja mellan bevis och spekulation"
  - id: "LO10"
    description: "Jämföra olika artbegrepp och deras tillämpning"
---
```

**Critical Rules**:
- `identifier`: UPPERCASE, alphanumeric + underscores only
- `language`: ISO 639-1 code (`sv`, `en`, `no`, etc.)
- `type`: Must be exactly `"formative"` or `"summative"`
- `feedback_mode`: Must be `"immediate"`, `"deferred"`, or `"none"`

---

## 📋 REQUIRED vs OPTIONAL FIELDS

### Required Fields (Parser will fail without these):

**Per Question:**
- `**Type**:` - Question type (must be exact spelling: `multiple_choice_single`, `multiple_response`, etc.)
- `**Identifier**:` - Unique ID for the question (UPPERCASE: Q001, Q002, etc.)
- `**Points**:` - Point value (number)

**Per File (YAML frontmatter):**
- `title` - Assessment title
- `identifier` - Unique test ID
- `language` - ISO language code (sv, en, no, etc.)

### Optional Fields (Enhance functionality, become Inspera labels):

**Per Question:**
- `**Learning Objectives**:` - Which LOs this question assesses (e.g., `LO1, LO2`)
  - Becomes searchable label in Inspera question bank
- `**Bloom's Level**:` - Cognitive complexity level (Remember, Understand, Apply, Analyze, Evaluate, Create)
  - Becomes searchable label in Inspera question bank

**Why include optional fields?**
✅ Automatically become **searchable labels/tags** in Inspera
✅ Enable filtering by learning objective or Bloom's level
✅ Support curriculum alignment reporting
✅ Help organize large question banks
✅ No downside - if included, useful; if omitted, question still works

---

### 2. Question Structure - Multiple Choice Single

**Question Heading**: Single `#` (H1 level)
**Format**: `# Question [N]: [Descriptive Title]`

```markdown
# Question 1: Darwins observationer på Galápagos

## REQUIRED:
**Type**: multiple_choice_single
**Identifier**: Q001
**Points**: 1

## OPTIONAL (becomes Inspera labels):
**Learning Objectives**: LO1
**Bloom's Level**: Remember

## Question Text

När Charles Darwin besökte Galápagosöarna observerade han att finkarna på olika öar hade olika näbbformer. Vilken slutsats drog Darwin från dessa observationer?

## Options

A. Finkarna skapades ursprungligen med olika näbbformer anpassade till olika öars specifika födokällor
B. Finkarna hade anpassats till olika födokällor på respektive ö genom naturligt urval
C. Finkarna utvecklade olika näbbformer genom att använda sina näbbar på olika sätt under sin livstid
D. Finkarna förändrade sina näbbformer direkt som svar på vilken typ av mat som fanns tillgänglig

## Answer

B

## Feedback

### General Feedback
Darwin observerade att finkar på öar med olika typer av mat hade utvecklat olika näbbformer som passade deras specifika födokällor. Detta var en av nyckelobservationerna som ledde till hans teori om naturligt urval.

### Correct Response Feedback
Utmärkt! Du har förstått hur Darwin använde sina observationer av Galápagos-finkarna för att utveckla teorin om naturligt urval. Finkarna hade anpassats till olika födokällor genom att individer med fördelaktiga näbbformer fick fler avkommor.

### Incorrect Response Feedback
Inte helt rätt. Tänk på att naturligt urval verkar genom att befintlig variation i en population selekteras - organismerna förändras inte direkt som svar på miljön. Se Campus Biologi s. 10 för mer om Darwins observationer.

### Option-Specific Feedback
- **A**: Detta representerar en skapelseförklaring som Darwin förkastade. Evolution sker genom naturligt urval av befintlig variation, inte genom direkt skapande av anpassade former.
- **B**: Korrekt! Darwin insåg att finkarna hade utvecklats från en gemensam anfader och anpassats till olika nischer genom naturligt urval.
- **C**: Detta är Lamarcks teori om förvärvade egenskaper, inte Darwins förklaring. Egenskaper som utvecklas under en individs livstid kan inte ärvas genetiskt.
- **D**: Detta är en vanlig missuppfattning. Evolution sker inte genom direkt förändring som svar på miljön, utan genom selektion av befintlig genetisk variation.
```

**Question Separator**: Three dashes on separate line

```markdown
---
```

---

### 3. Question Structure - Multiple Response (Select All)

```markdown
# Question 13: Identifiera förutsättningar för naturligt urval

## REQUIRED:
**Type**: multiple_response
**Identifier**: Q013
**Points**: 2

## OPTIONAL (becomes Inspera labels):
**Learning Objectives**: LO2
**Bloom's Level**: Understand

## Question Text

Vilka av följande är nödvändiga förutsättningar för att naturligt urval ska kunna leda till evolution i en population?

## Prompt

Välj ALLA korrekta påståenden.

## Options

A. Det finns ärftlig variation mellan individer i populationen
B. Alla individer i populationen har exakt samma chanser att överleva och reproducera sig
C. Vissa egenskaper ger fördelar i överlevnad eller reproduktion i den aktuella miljön
D. Populationen är helt isolerad från andra populationer
E. Förändringar sker över flera generationer

## Answer

A, C, E

## Scoring

**Points per correct choice**: 0.67
**Points per incorrect choice**: 0
**Maximum score**: 2
**Minimum score**: 0

## Feedback

### General Feedback
För att naturligt urval ska leda till evolution krävs flera grundläggande förutsättningar som Darwin identifierade. Se Campus Biologi s. 12-14 för en fullständig genomgång.

### Correct Response Feedback
Perfekt! Du har identifierat alla tre nödvändiga förutsättningarna för naturligt urval: ärftlig variation, differentiell reproduktion baserad på egenskaper, och tid för förändringar att ackumuleras över generationer.

### Incorrect Response Feedback
Du missade några viktiga förutsättningar eller valde alternativ som inte är nödvändiga. Granska Darwins teori om naturligt urval och tänk på vad som MÅSTE finnas för att evolution ska kunna ske.

### Partially Correct Response Feedback
Bra start! Du har identifierat några korrekta förutsättningar, men kontrollera de övriga alternativen noggrant. Tänk på vad som är absolut nödvändigt för att naturligt urval ska fungera.

### Option-Specific Feedback
- **A**: Korrekt! Utan ärftlig variation finns inget för naturligt urval att verka på.
- **B**: Fel. Om alla individer hade samma chanser skulle det inte finnas någon differentiell reproduktion - ingen selektion.
- **C**: Korrekt! Detta är själva mekanismen för naturligt urval - vissa egenskaper gynnas.
- **D**: Fel. Isolering kan påverka evolution men är inte en nödvändig förutsättning för naturligt urval.
- **E**: Korrekt! Evolution är en process som sker över många generationer.

### Unanswered Feedback
Välj de alternativ som representerar nödvändiga förutsättningar för naturligt urval. Du kan välja flera alternativ.

---
```

---

### 4. Question Structure - True/False

```markdown
# Question 5: Evolution och allelfrekvens

## REQUIRED:
**Type**: true_false
**Identifier**: Q005
**Points**: 1

## OPTIONAL (becomes Inspera labels):
**Learning Objectives**: LO1
**Bloom's Level**: Remember

## Question Text

Sant eller falskt: Evolution kan definieras som förändring i allelfrekvenser i en population över tid.

## Options

A. Sant
B. Falskt

## Answer

A

## Feedback

### General Feedback
Evolution definieras på populationsnivå som förändring i allelfrekvenser över tid. En allel är en variant av en gen, och allelfrekvens är hur vanlig en viss variant är i populationen.

### Correct Response Feedback
Korrekt! Detta är den moderna genetiska definitionen av evolution. När naturligt urval, genetisk drift eller andra evolutionära mekanismer verkar, förändras hur vanliga olika alleler är i populationen.

### Incorrect Response Feedback
Detta är faktiskt sant. Evolution handlar inte om enskilda individer som förändras, utan om förändringar i genpoolen (alla gener) i en hel population över generationer. Se Campus Biologi s. 12 för mer om denna definition.

### Unanswered Feedback
Välj Sant eller Falskt för att besvara frågan om evolutionens definition.

---
```

---

### 5. Question Structure - Fill-in-the-Blank

```markdown
# Question 7: Begrepp - Fitness

## REQUIRED:
**Type**: fill_in_the_blank
**Identifier**: Q007
**Points**: 1

## OPTIONAL (becomes Inspera labels):
**Learning Objectives**: LO1
**Bloom's Level**: Remember

## Question Text

I evolutionär biologi mäts en individs **________** genom hur många avkommor individen får som själva överlever och reproducerar sig.

## Correct Answer

fitness

## Accepted Alternatives

fitness, fortplantningsframgång, reproduktiv framgång

## Case Sensitive

false

## Expected Length

20

## Feedback

### General Feedback
Fitness (eller fortplantningsframgång på svenska) är ett centralt begrepp i evolutionsbiologin som mäter en individs evolutionära framgång.

### Correct Response Feedback
Korrekt! Fitness mäter en individs evolutionära framgång genom att räkna hur många avkommor individen får som själva överlever till reproduktiv ålder. Viktigt: fitness handlar INTE om hur stark eller snabb en individ är, utan om genetisk representation i nästa generation.

### Incorrect Response Feedback
Inte riktigt. Det korrekta begreppet är "fitness" (eller "fortplantningsframgång" på svenska). Detta mäter hur många gener en individ för vidare till kommande generationer. Se Campus Biologi s. 16.

### Unanswered Feedback
Fyll i det evolutionsbiologiska begreppet som beskriver en individs reproduktiva framgång.

---
```

---

### 6. Question Structure - Matching (Associate Pairs)

```markdown
# Question 29: Matcha urvalstyper med scenario

## REQUIRED:
**Type**: match
**Identifier**: Q029
**Points**: 3

## OPTIONAL (becomes Inspera labels):
**Learning Objectives**: LO4
**Bloom's Level**: Understand

## Question Text

Matcha varje typ av urval med det scenario som bäst beskriver det.

## Premises (Left Column)

1. Riktat urval (directional selection)
2. Stabiliserande urval (stabilizing selection)
3. Disruptivt urval (disruptive selection)

## Choices (Right Column)

A. Medelvärdet för en egenskap förskjuts åt ett håll över tid
B. Extremvärdena gynnas medan medelvärdet missgynnas
C. Medelvärdet gynnas medan extremvärdena missgynnas
D. Alla individer överlever lika bra oavsett egenskaper

## Answer

1 → A
2 → C
3 → B

## Scoring

**Type**: partial_credit
**Points per correct match**: 1
**Minimum score**: 0

## Feedback

### General Feedback
De tre typerna av naturligt urval påverkar fördelningen av egenskaper i en population på olika sätt. Se Campus Biologi s. 20-21 för grafiska representationer av varje typ.

### Correct Response Feedback
Utmärkt! Du har korrekt matchat alla tre typer av urval med deras effekter på populationen. Riktat urval förskjuter medelvärdet, stabiliserande urval behåller medelvärdet, och disruptivt urval gynnar extremer.

### Incorrect Response Feedback
Granska hur varje typ av urval påverkar fördelningen av egenskaper i populationen. Tänk på om medelvärdet förskjuts, behålls, eller om extremvärdena gynnas.

### Partially Correct Response Feedback
Du har matchat några korrekt. Fortsätt tänka på hur varje urvalstyp påverkar fördelningen - förskjuts den, behålls medelvärdet, eller gynnas extremer?

### Unanswered Feedback
Matcha varje typ av urval med den beskrivning som bäst förklarar hur det påverkar populationen.

---
```

---

## ⚠️ CRITICAL FORMAT RULES

### Question Header Fields

**EXACT spelling required for Type field**:
- `multiple_choice_single` (NOT "Multiple Choice (Single)")
- `multiple_response` (NOT "Multiple Response")
- `true_false` (NOT "True/False")
- `fill_in_the_blank` (NOT "Fill-in-the-Blank")
- `match` (NOT "Matching" or "Match")
- `text_area` (for short response)
- `extended_text` (for essay)

**Identifier Rules**:
- UPPERCASE letters, numbers, underscores only
- Examples: `Q001`, `MC_001`, `EVOL_Q1`
- NO spaces, NO special characters

**Section Headers (## level 2 headings)**:
- `## Question Text` (EXACT - NOT "### Frågetext")
- `## Options` (NOT "### Alternativ")
- `## Answer` (NOT "### Korrekt svar")
- `## Feedback` (NOT "### Återkoppling")
- `## Prompt` (for multiple_response only)
- `## Premises (Left Column)` (for match)
- `## Choices (Right Column)` (for match)

**Answer Format**:
- Multiple Choice Single: Single letter `B` (NO period, NO quotes)
- Multiple Response: Comma-separated `A, C, E`
- True/False: `A` (where A=Sant, B=Falskt)
- Match: One pairing per line `1 → A` or `1 -> A`
- Fill-in-the-blank: Text answer under `## Correct Answer`

---

## 📊 Complete Evolution Quiz Template Structure

**File**: `evolution_quiz_60q_qti_ready.md`

```markdown
---
[YAML FRONTMATTER - see section 1 above]
---

# Question 1: [Title]
[Complete question structure - see section 2-6 above]

---

# Question 2: [Title]
[Complete question structure]

---

# Question 3: [Title]
[Complete question structure]

---

[... continue for all 60 questions ...]

---

# Question 60: [Title]
[Complete question structure]
```

---

## 🔄 Conversion Process

1. **Input**: This markdown file following EXACT specification above
2. **Parser** (`markdown_parser.py`):
   - Extracts YAML frontmatter → test metadata
   - Splits questions by `---` separator
   - Parses each question by section headers (`## Question Text`, `## Options`, etc.)
3. **Generator** (`xml_generator.py`):
   - Loads XML template for question type
   - Replaces placeholders with question data
   - Generates QTI 2.2 compliant XML
4. **Output**:
   - `/output/test02_evolution_biog001x_QTI/Evolution_quiz_with_labels/`
   - `imsmanifest.xml`
   - 60 individual question XML files
   - ZIP package ready for Inspera import

---

## ✅ Validation Checklist

Before running QTI generator, verify:

- [ ] YAML frontmatter valid (test with `yaml.safe_load()`)
- [ ] All 60 questions have `# Question [N]:` heading (H1 level)
- [ ] All questions have required fields: Type, Identifier, Points
- [ ] Type field uses EXACT spelling (lowercase, underscores)
- [ ] All Identifiers are unique and valid format
- [ ] Section headers use `##` (H2 level) with EXACT names
- [ ] Options format: `A. Text` (uppercase letter, period, space)
- [ ] Answer format matches question type
- [ ] Questions separated by `---` on separate line
- [ ] Learning Objectives in questions match IDs in YAML

---

## 🎯 Next Steps

1. **Use this specification** as THE authoritative format reference
2. **Claude Desktop dialogue** with teacher creates markdown following this spec
3. **Save** as `evolution_quiz_60q_qti_ready.md` in project root
4. **Run** QTI generator: `python -m src.main input.md -o output/`
5. **Import** ZIP to Inspera

---

**Document Version**: 1.0
**Created**: 2025-11-02
**Purpose**: The missing link - EXACT input specification for QTI Generator
