#!/usr/bin/env node

/**
 * Tool registry for direct filesystem operations
 * This bypasses MCP naming issues by providing direct access to filesystem tools
 */

import { readTextFile } from './file-read.js';
import { listDirectory } from './file-list.js';

export const tools = {
  'mcp__file__read_text_file': readTextFile,
  'mcp__file__list_directory': listDirectory
};

// Command-line interface
if (import.meta.url === `file://${process.argv[1]}`) {
  const [,, toolName, ...args] = process.argv;

  if (!toolName || !tools[toolName]) {
    console.error('Available tools:', Object.keys(tools).join(', '));
    process.exit(1);
  }

  try {
    const result = await tools[toolName](...args);
    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}