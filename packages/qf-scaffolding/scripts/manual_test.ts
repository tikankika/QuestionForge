/**
 * Manual test script for Phase 1 & 2 outputs (Complete M1)
 *
 * Tests:
 * Phase 1:
 * - complete_stage with misconceptions output (Stage 4)
 * - complete_stage with learning_objectives output (Stage 5)
 *
 * Phase 2:
 * - complete_stage with material_analysis output (Stage 0)
 * - complete_stage with emphasis_patterns output (Stage 2)
 * - complete_stage with examples output (Stage 3)
 *
 * Verifies:
 * - Files are created correctly
 * - session.yaml is updated
 * - Logging works
 *
 * Run: npx tsx scripts/manual_test.ts
 */

import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'js-yaml';
import { completeStage } from '../src/tools/complete_stage.js';

const TEST_PROJECT_PATH = '/tmp/qf-test-project';

// Test data for learning objectives
const learningObjectivesData = {
  course: "Celler och Virus (BI1001)",
  instructor: "Niklas Karlsson",
  tier1: [
    {
      id: "LO1.1",
      text: "Describe the basic structure of prokaryotic and eukaryotic cells",
      bloom: "Remember",
      rationale: "Fundamental concept, 30% of instruction time"
    },
    {
      id: "LO1.2",
      text: "Explain the function of mitochondria in cellular respiration",
      bloom: "Understand",
      rationale: "Explicitly stated as 'critical for exam'"
    }
  ],
  tier2: [
    {
      id: "LO2.1",
      text: "Analyze how cell membrane structure relates to function",
      bloom: "Analyze",
      rationale: "Important for lab work, moderate emphasis"
    }
  ],
  tier3: [
    {
      id: "LO3.1",
      text: "Describe the endosymbiotic theory",
      bloom: "Remember",
      rationale: "Background knowledge, mentioned once"
    }
  ],
  tier4_excluded: [
    "Advanced molecular genetics (explicitly out of scope)",
    "Detailed biochemical pathways (covered in BI2002)"
  ]
};

// Test data for misconceptions
const misconceptionsData = {
  misconceptions: [
    {
      id: "M1",
      topic: "Mitochondria function",
      misconception: "Mitochondria create energy from nothing",
      correct: "Mitochondria convert chemical energy (glucose → ATP)",
      evidence: [
        { source: "Formative quiz week 3", frequency: "8/15 students (53%)" },
        { source: "Lab 2 discussion", frequency: "Common verbal error" }
      ],
      severity: "high" as const,
      rationale: "Fundamental misunderstanding of energy transformation",
      teaching_strategy: "Emphasize conversion not creation, use battery analogy",
      distractor_example: "Mitokondrier skapar energi från ingenting"
    },
    {
      id: "M2",
      topic: "Cell walls",
      misconception: "All cells have cell walls",
      correct: "Only plant cells and prokaryotes have cell walls; animal cells do not",
      evidence: [
        { source: "Homework assignment 1", frequency: "5/15 students (33%)" }
      ],
      severity: "medium" as const,
      rationale: "Overgeneralization from plant cell focus in early lectures",
      teaching_strategy: "Explicit contrast table: Animal vs Plant cells",
      distractor_example: "Alla celler har cellvägg för strukturellt stöd"
    }
  ]
};

// Test data for material_analysis (Phase 2 - Stage 0)
const materialAnalysisData = {
  analysis_duration: 90,
  analyst: "Claude Sonnet 4",
  materials_analyzed: {
    lectures: [
      {
        title: "Lecture 1: Introduction to Cells",
        date: "2025-09-15",
        duration: 90,
        slides: 45,
        transcript: true,
        topics: ["Cell types", "prokaryotic vs eukaryotic"]
      },
      {
        title: "Lecture 2: Mitochondria and Energy",
        date: "2025-09-22",
        duration: 60,
        slides: 30,
        transcript: true,
        topics: ["Cellular respiration", "ATP production"]
      }
    ],
    labs: [
      {
        title: "Lab 1: Cell Observation",
        date: "2025-09-20",
        handout_pages: 8,
        practical: true,
        activities: ["Microscopy", "diffusion demonstration"]
      }
    ],
    readings: [
      {
        title: "Campbell Biology Ch. 3-4",
        pages: 45,
        required: true,
        topics: ["Cell structure", "organelles"]
      }
    ]
  },
  completeness: {
    all_lectures: true,
    all_labs: true,
    all_readings: true,
    missing: ["Guest lecture (scheduled 2026-02-05)"]
  },
  quality_assessment: {
    lecture_clarity: "high" as const,
    lecture_consistency: "high" as const,
    emphasis_signals: "very_high" as const,
    lab_connection: "good" as const,
    reading_alignment: "strong" as const
  }
};

// Test data for emphasis_patterns (Phase 2 - Stage 2)
const emphasisPatternsData = {
  materials_analyzed: "2 lectures, 1 lab, 1 reading chapter",
  total_instruction_time: "2.5 hours",
  tier1: [
    {
      topic: "Mitochondria function",
      signals: [
        { type: "explicit" as const, count: 6, examples: ["Detta är VIKTIGT för tentan"] },
        { type: "time" as const, percentage: 30, context: "Primary focus of Lecture 2" }
      ],
      rationale: "Highest combination of explicit and time signals"
    }
  ],
  tier2: [
    {
      topic: "Cell structure basics",
      signals: [
        { type: "repetition" as const, count: 5, context: "Diagrams in multiple lectures" },
        { type: "foundational" as const, evidence: "Required for all subsequent topics" }
      ],
      rationale: "Foundation concept with high repetition"
    }
  ],
  tier3: [
    {
      topic: "Endosymbiotic theory",
      signals: [
        { type: "explicit" as const, count: 1, examples: ["Interesting but not on exam"] }
      ],
      rationale: "Explicitly de-emphasized"
    }
  ],
  tier4: [
    {
      topic: "Advanced molecular genetics",
      signals: [
        { type: "explicit" as const, count: 1, examples: ["Out of scope"] }
      ],
      rationale: "Explicitly excluded"
    }
  ]
};

// Test data for examples (Phase 2 - Stage 3)
const examplesData = {
  materials_reviewed: "2 lectures, 1 lab",
  examples: [
    {
      id: "EX1",
      title: "Red Blood Cell Diagram",
      source: "Lecture 1, Slide 12",
      topic: "Cell structure - animal cells",
      learning_objective: "LO1.1",
      context: "Compared to plant cell to show differences",
      visual: true,
      usage_count: 3,
      contexts: ["Lecture 1: Introduction", "Lab 1: Microscopy", "Lecture 2: Review"],
      effectiveness: "high" as const,
      student_familiarity: "very_high" as const,
      question_potential: {
        bloom_levels: ["Remember", "Understand"],
        question_types: ["multiple_choice", "labeling"],
        example_stem: "Vilken struktur saknar röda blodkroppar?"
      }
    },
    {
      id: "EX2",
      title: "Diffusion Lab Demo",
      source: "Lab 1",
      topic: "Membrane transport",
      learning_objective: "LO2.1",
      context: "Hands-on dye diffusion observation",
      visual: true,
      hands_on: true,
      usage_count: 2,
      contexts: ["Lab 1: Practical", "Lecture 2: Theory connection"],
      effectiveness: "very_high" as const,
      student_familiarity: "high" as const,
      question_potential: {
        bloom_levels: ["Apply", "Analyze"],
        question_types: ["scenario_based"],
        example_stem: "Om koncentrationen ökas, vad händer med diffusionen?"
      }
    }
  ]
};

async function setupTestProject() {
  console.log('📁 Setting up test project...');

  // Clean up if exists
  if (fs.existsSync(TEST_PROJECT_PATH)) {
    fs.rmSync(TEST_PROJECT_PATH, { recursive: true });
  }

  // Create project structure
  fs.mkdirSync(TEST_PROJECT_PATH, { recursive: true });
  fs.mkdirSync(path.join(TEST_PROJECT_PATH, 'logs'), { recursive: true });

  // Create session.yaml
  const sessionYaml = {
    session: {
      id: 'test-session-123',
      created: new Date().toISOString(),
      updated: new Date().toISOString()
    },
    methodology: {
      m1: {
        status: 'in_progress',
        completed_stages: [],
        outputs: {}
      }
    }
  };

  fs.writeFileSync(
    path.join(TEST_PROJECT_PATH, 'session.yaml'),
    yaml.dump(sessionYaml),
    'utf-8'
  );

  console.log('✅ Test project created at:', TEST_PROJECT_PATH);
}

async function testLearningObjectives() {
  console.log('\n📝 Testing learning_objectives output...');

  const result = await completeStage({
    project_path: TEST_PROJECT_PATH,
    module: 'm1',
    stage: 5,
    output: {
      type: 'learning_objectives',
      data: learningObjectivesData
    }
  });

  if (!result.success) {
    console.error('❌ Failed:', result.error);
    return false;
  }

  console.log('✅ Stage completed successfully');
  console.log('   Output file:', result.output_filepath);

  // Verify file exists and content
  if (result.output_filepath && fs.existsSync(result.output_filepath)) {
    const content = fs.readFileSync(result.output_filepath, 'utf-8');
    console.log('   File size:', content.length, 'bytes');

    // Check key content
    if (content.includes('# M1 Learning Objectives') &&
        content.includes('LO1.1') &&
        content.includes('tier1:')) {
      console.log('✅ File content verified');
    } else {
      console.error('❌ File content missing expected sections');
      return false;
    }
  } else {
    console.error('❌ Output file not found');
    return false;
  }

  return true;
}

async function testMaterialAnalysis() {
  console.log('\n📝 Testing material_analysis output (Phase 2 - Stage 0)...');

  const result = await completeStage({
    project_path: TEST_PROJECT_PATH,
    module: 'm1',
    stage: 0,
    output: {
      type: 'material_analysis',
      data: materialAnalysisData
    }
  });

  if (!result.success) {
    console.error('❌ Failed:', result.error);
    return false;
  }

  console.log('✅ Stage completed successfully');
  console.log('   Output file:', result.output_filepath);

  if (result.output_filepath && fs.existsSync(result.output_filepath)) {
    const content = fs.readFileSync(result.output_filepath, 'utf-8');
    console.log('   File size:', content.length, 'bytes');

    if (content.includes('# M1 Material Analysis') &&
        content.includes('## Materials Analyzed') &&
        content.includes('Lecture 1:')) {
      console.log('✅ File content verified');
    } else {
      console.error('❌ File content missing expected sections');
      return false;
    }
  } else {
    console.error('❌ Output file not found');
    return false;
  }

  return true;
}

async function testEmphasisPatterns() {
  console.log('\n📝 Testing emphasis_patterns output (Phase 2 - Stage 2)...');

  const result = await completeStage({
    project_path: TEST_PROJECT_PATH,
    module: 'm1',
    stage: 2,
    output: {
      type: 'emphasis_patterns',
      data: emphasisPatternsData
    }
  });

  if (!result.success) {
    console.error('❌ Failed:', result.error);
    return false;
  }

  console.log('✅ Stage completed successfully');
  console.log('   Output file:', result.output_filepath);

  if (result.output_filepath && fs.existsSync(result.output_filepath)) {
    const content = fs.readFileSync(result.output_filepath, 'utf-8');
    console.log('   File size:', content.length, 'bytes');

    if (content.includes('# M1 Emphasis Patterns Analysis') &&
        content.includes('## Tier 1:') &&
        content.includes('Mitochondria function')) {
      console.log('✅ File content verified');
    } else {
      console.error('❌ File content missing expected sections');
      return false;
    }
  } else {
    console.error('❌ Output file not found');
    return false;
  }

  return true;
}

async function testExamples() {
  console.log('\n📝 Testing examples output (Phase 2 - Stage 3)...');

  const result = await completeStage({
    project_path: TEST_PROJECT_PATH,
    module: 'm1',
    stage: 3,
    output: {
      type: 'examples',
      data: examplesData
    }
  });

  if (!result.success) {
    console.error('❌ Failed:', result.error);
    return false;
  }

  console.log('✅ Stage completed successfully');
  console.log('   Output file:', result.output_filepath);

  if (result.output_filepath && fs.existsSync(result.output_filepath)) {
    const content = fs.readFileSync(result.output_filepath, 'utf-8');
    console.log('   File size:', content.length, 'bytes');

    if (content.includes('# M1 Instructional Examples Catalog') &&
        content.includes('Red Blood Cell Diagram') &&
        content.includes('EX1')) {
      console.log('✅ File content verified');
    } else {
      console.error('❌ File content missing expected sections');
      return false;
    }
  } else {
    console.error('❌ Output file not found');
    return false;
  }

  return true;
}

async function testMisconceptions() {
  console.log('\n📝 Testing misconceptions output (Phase 1 - Stage 4)...');

  const result = await completeStage({
    project_path: TEST_PROJECT_PATH,
    module: 'm1',
    stage: 4,
    output: {
      type: 'misconceptions',
      data: misconceptionsData
    }
  });

  if (!result.success) {
    console.error('❌ Failed:', result.error);
    return false;
  }

  console.log('✅ Stage completed successfully');
  console.log('   Output file:', result.output_filepath);

  // Verify file exists and content
  if (result.output_filepath && fs.existsSync(result.output_filepath)) {
    const content = fs.readFileSync(result.output_filepath, 'utf-8');
    console.log('   File size:', content.length, 'bytes');

    // Check key content
    if (content.includes('# M1 Common Student Misconceptions') &&
        content.includes('M1:') &&
        content.includes('HIGH SEVERITY')) {
      console.log('✅ File content verified');
    } else {
      console.error('❌ File content missing expected sections');
      return false;
    }
  } else {
    console.error('❌ Output file not found');
    return false;
  }

  return true;
}

async function verifySessionYaml() {
  console.log('\n📝 Verifying session.yaml updates...');

  const sessionPath = path.join(TEST_PROJECT_PATH, 'session.yaml');
  const content = fs.readFileSync(sessionPath, 'utf-8');
  const session = yaml.load(content) as any;

  console.log('   Completed stages:', session.methodology?.m1?.completed_stages);
  console.log('   Outputs:', Object.keys(session.methodology?.m1?.outputs || {}));

  // Verify all M1 stages are marked complete (0, 2, 3, 4, 5)
  const completedStages = session.methodology?.m1?.completed_stages || [];
  const expectedStages = [0, 2, 3, 4, 5];
  const allStagesComplete = expectedStages.every(s => completedStages.includes(s));

  if (allStagesComplete) {
    console.log('✅ All M1 output stages completed (0, 2, 3, 4, 5)');
  } else {
    console.error('❌ Some stages missing. Expected:', expectedStages, 'Got:', completedStages);
    return false;
  }

  // Verify all outputs registered
  const outputs = session.methodology?.m1?.outputs || {};
  const expectedOutputs = ['material_analysis', 'emphasis_patterns', 'examples', 'misconceptions', 'learning_objectives'];
  const allOutputsRegistered = expectedOutputs.every(o => outputs[o]);

  if (allOutputsRegistered) {
    console.log('✅ All 5 M1 outputs registered in session.yaml');
  } else {
    console.error('❌ Some outputs missing. Expected:', expectedOutputs, 'Got:', Object.keys(outputs));
    return false;
  }

  return true;
}

async function verifyLogFile() {
  console.log('\n📝 Verifying log file...');

  const logPath = path.join(TEST_PROJECT_PATH, 'logs', 'session.jsonl');
  if (fs.existsSync(logPath)) {
    const content = fs.readFileSync(logPath, 'utf-8');
    const lines = content.trim().split('\n');
    console.log('   Log entries:', lines.length);

    // Check for expected events
    const hasStageComplete = lines.some(l => l.includes('stage_complete'));
    const hasToolStart = lines.some(l => l.includes('tool_start'));
    const hasToolEnd = lines.some(l => l.includes('tool_end'));

    if (hasStageComplete && hasToolStart && hasToolEnd) {
      console.log('✅ Log events verified (tool_start, tool_end, stage_complete)');
    } else {
      console.error('❌ Missing expected log events');
      return false;
    }
  } else {
    console.log('⚠️  No log file found (logging may be optional)');
  }

  return true;
}

async function listCreatedFiles() {
  console.log('\n📁 Files created in 01_methodology/:');

  const methodologyDir = path.join(TEST_PROJECT_PATH, '01_methodology');
  if (fs.existsSync(methodologyDir)) {
    const files = fs.readdirSync(methodologyDir);
    files.forEach(f => {
      const stats = fs.statSync(path.join(methodologyDir, f));
      console.log(`   - ${f} (${stats.size} bytes)`);
    });
  }
}

async function cleanup() {
  console.log('\n🧹 Cleaning up...');
  if (fs.existsSync(TEST_PROJECT_PATH)) {
    fs.rmSync(TEST_PROJECT_PATH, { recursive: true });
    console.log('✅ Test project removed');
  }
}

async function main() {
  console.log('='.repeat(60));
  console.log('Complete M1 Manual Test - All 5 Output Types');
  console.log('='.repeat(60));

  try {
    await setupTestProject();

    // Run tests in stage order (0, 2, 3, 4, 5)
    console.log('\n--- Phase 2 Outputs ---');
    const test1 = await testMaterialAnalysis();   // Stage 0
    const test2 = await testEmphasisPatterns();   // Stage 2
    const test3 = await testExamples();           // Stage 3

    console.log('\n--- Phase 1 Outputs ---');
    const test4 = await testMisconceptions();     // Stage 4
    const test5 = await testLearningObjectives(); // Stage 5

    console.log('\n--- Verification ---');
    const test6 = await verifySessionYaml();
    const test7 = await verifyLogFile();

    await listCreatedFiles();

    const allPassed = test1 && test2 && test3 && test4 && test5 && test6 && test7;

    console.log('\n' + '='.repeat(60));
    if (allPassed) {
      console.log('✅ ALL 5 M1 OUTPUT TESTS PASSED');
      console.log('   - material_analysis (Stage 0)');
      console.log('   - emphasis_patterns (Stage 2)');
      console.log('   - examples (Stage 3)');
      console.log('   - misconceptions (Stage 4)');
      console.log('   - learning_objectives (Stage 5)');
    } else {
      console.log('❌ SOME TESTS FAILED');
    }
    console.log('='.repeat(60));

    // Uncomment to keep files for inspection:
    // console.log('\n📁 Files kept at:', TEST_PROJECT_PATH);

    // Cleanup
    await cleanup();

  } catch (error) {
    console.error('💥 Error:', error);
    process.exit(1);
  }
}

main();
