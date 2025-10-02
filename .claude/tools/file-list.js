#!/usr/bin/env node

import { readdir, stat } from 'fs/promises';
import { resolve, join } from 'path';

async function listDirectory(dirPath) {
  try {
    const absolutePath = resolve(dirPath || '.');
    const entries = await readdir(absolutePath);

    const contents = [];

    for (const entry of entries) {
      const fullPath = join(absolutePath, entry);
      try {
        const stats = await stat(fullPath);
        contents.push({
          name: entry,
          type: stats.isDirectory() ? 'directory' : 'file',
          size: stats.isFile() ? stats.size : undefined
        });
      } catch (error) {
        // Skip entries we can't stat
        continue;
      }
    }

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(contents, null, 2)
        }
      ]
    };
  } catch (error) {
    throw new Error(`Failed to list directory: ${error.message}`);
  }
}

// CLI usage
if (process.argv[1] && process.argv[1].endsWith('file-list.js')) {
  const dirPath = process.argv[2] || '.';

  try {
    const result = await listDirectory(dirPath);
    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

export { listDirectory };