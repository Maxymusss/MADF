#!/usr/bin/env node
/**
 * Test if Ollama modelfile rules are being used by MCPAgent
 */

import { ChatOllama } from '@langchain/ollama';

async function testOllamaRules() {
  const llm = new ChatOllama({
    baseUrl: 'http://localhost:11434',
    model: 'qwen2.5-mcp',
    temperature: 0
  });

  console.log('Testing Ollama modelfile rules...\n');

  // Test structured input (RULE 2)
  const structuredInput = '["filesystem", "list_allowed_directories", {}]';

  console.log('Input:', structuredInput);
  console.log('Expected: Execute immediately without reasoning\n');

  const response = await llm.invoke(structuredInput);

  console.log('Response:', response.content);
  console.log('\n---\n');

  // Check if system prompt is active
  const systemCheck = await llm.invoke('What are your embedded rules?');
  console.log('System prompt check:', systemCheck.content);
}

testOllamaRules().catch(console.error);