#!/usr/bin/env node

import { readFile } from 'fs/promises';
import { resolve } from 'path';

async function readTextFile(filePath) {
  try {
    const absolutePath = resolve(filePath);
    const content = await readFile(absolutePath, 'utf-8');

    return {
      content: [
        {
          type: "text",
          text: content
        }
      ]
    };
  } catch (error) {
    throw new Error(`Failed to read file: ${error.message}`);
  }
}

// CLI usage
if (process.argv[1] && process.argv[1].endsWith('file-read.js')) {
  const filePath = process.argv[2];

  if (!filePath) {
    console.error('Usage: node file-read.js <file_path>');
    process.exit(1);
  }

  try {
    const result = await readTextFile(filePath);
    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

export { readTextFile };