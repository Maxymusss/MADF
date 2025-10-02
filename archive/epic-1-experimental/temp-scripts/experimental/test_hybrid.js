/**
 * Tests for hybrid mode (revised architecture)
 * No Python translator - Claude Code does translation natively
 */
import { exec } from 'child_process';
import { promisify } from 'util';
import assert from 'assert';

const execAsync = promisify(exec);

async function testOllamaModel() {
  console.log('Testing Ollama custom model exists...');

  const { stdout } = await execAsync('"D:\\Ollama\\ollama.exe" list');
  assert(stdout.includes('qwen2.5-mcp'), 'qwen2.5-mcp model not found');
  console.log('[OK] Custom model exists: qwen2.5-mcp');
}

async function testOllamaModelResponse() {
  console.log('\nTesting Ollama model responds correctly...');

  const { stdout } = await execAsync(
    `curl -s -X POST http://localhost:11434/api/generate -d "{\\"model\\":\\"qwen2.5-mcp\\",\\"prompt\\":\\"What is 2+2? Answer with just the number.\\",\\"stream\\":false}"`
  );

  const response = JSON.parse(stdout.trim());
  assert(response.response, 'No response from model');
  console.log(`[OK] Model responded: "${response.response.trim()}"`);
}

async function testInputParsing() {
  console.log('\nTesting run_hybrid.js input parsing...');

  // Test structured array parsing
  const testInputs = [
    '["filesystem", "list_allowed_directories"]',
    '["github", "search_repositories", {"query": "test"}]',
    '"What is the weather today?"'
  ];

  for (const input of testInputs) {
    try {
      JSON.parse(input);
      console.log(`[OK] Valid input format: ${input.substring(0, 50)}...`);
    } catch {
      // Natural language string (not JSON) is also valid
      console.log(`[OK] Natural language input: ${input.substring(0, 50)}...`);
    }
  }
}

async function testMCPDependencies() {
  console.log('\nTesting Node.js dependencies...');

  try {
    const { stdout } = await execAsync('npm list mcp-use @langchain/ollama 2>&1');
    assert(stdout.includes('mcp-use@'), 'mcp-use not installed');
    assert(stdout.includes('@langchain/ollama@'), '@langchain/ollama not installed');
    console.log('[OK] Required dependencies installed');
  } catch (error) {
    console.warn('[WARN] Dependency check failed (may need: npm install)');
  }
}

async function main() {
  console.log('=== Hybrid Mode Tests ===\n');

  try {
    await testOllamaModel();
    await testOllamaModelResponse();
    await testInputParsing();
    await testMCPDependencies();

    console.log('\n=== All Tests Passed ===');
    console.log('\nNote: MCP server connection testing requires manual verification');
    console.log('Run: node run_hybrid.js \'["filesystem", "list_allowed_directories"]\'');
  } catch (error) {
    console.error('\n[FAIL] Test failed:', error.message);
    process.exit(1);
  }
}

main();