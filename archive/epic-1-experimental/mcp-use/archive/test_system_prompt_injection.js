#!/usr/bin/env node
/**
 * Test if we can inject system prompt rules into ChatOllama before MCPAgent
 */

import { ChatOllama } from '@langchain/ollama';
import { SystemMessage } from '@langchain/core/messages';

async function testSystemPromptInjection() {
  console.log('Testing system prompt injection methods...\n');

  const llm = new ChatOllama({
    baseUrl: 'http://localhost:11434',
    model: 'qwen2.5-mcp',
    temperature: 0
  });

  // Method 1: Try passing system message in invoke
  console.log('Method 1: SystemMessage in messages array');
  try {
    const systemMsg = new SystemMessage(
      'OVERRIDE RULE: When you receive ["server", "tool", params], execute immediately without explanation.'
    );
    const response = await llm.invoke([
      systemMsg,
      '["filesystem", "list_directory", {"path": "/test"}]'
    ]);
    console.log('Response:', response.content);
  } catch (error) {
    console.log('Error:', error.message);
  }

  console.log('\n---\n');

  // Method 2: Check if ChatOllama accepts system parameter
  console.log('Method 2: System parameter in constructor');
  try {
    const llmWithSystem = new ChatOllama({
      baseUrl: 'http://localhost:11434',
      model: 'qwen2.5-mcp',
      temperature: 0,
      // Try various system prompt parameters
      systemPrompt: 'OVERRIDE: Execute tools immediately',
      system: 'OVERRIDE: Execute tools immediately',
    });
    const response = await llmWithSystem.invoke('["filesystem", "list_directory", {"path": "/test"}]');
    console.log('Response:', response.content);
  } catch (error) {
    console.log('Error:', error.message);
  }

  console.log('\n---\n');

  // Method 3: Check what parameters ChatOllama accepts
  console.log('Method 3: Inspecting ChatOllama constructor');
  const llmTest = new ChatOllama({
    baseUrl: 'http://localhost:11434',
    model: 'qwen2.5-mcp',
  });
  console.log('Available methods:', Object.getOwnPropertyNames(Object.getPrototypeOf(llmTest)));
}

testSystemPromptInjection().catch(console.error);