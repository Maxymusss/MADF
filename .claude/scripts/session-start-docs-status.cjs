#!/usr/bin/env node
/**
 * SessionStart hook for showing documentation cache status
 * Outputs JSON format to add context without XML wrapper tags
 */

const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = path.join(__dirname, '..', '..');
const CLAUDE_MD_PATH = path.join(PROJECT_ROOT, 'CLAUDE.md');

function getDocsTimestamp() {
  try {
    if (!fs.existsSync(CLAUDE_MD_PATH)) {
      return null;
    }

    const claudeContent = fs.readFileSync(CLAUDE_MD_PATH, 'utf8');

    // Extract timestamp from docs-cache line
    const match = claudeContent.match(/- \*\*Docs Cache\*\*: Use `\.claude\/docs-cache\/` for cached documentation \([^,]+, [^,]+, ([^)]+)\)/);

    if (match && match[1]) {
      return match[1];
    }

    return null;
  } catch (error) {
    return null;
  }
}

function main() {
  const timestamp = getDocsTimestamp();

  const output = {
    hookSpecificOutput: {
      hookEventName: "SessionStart",
      additionalContext: timestamp ? `Last Doc Updated: ${timestamp}` : ""
    }
  };

  console.log(JSON.stringify(output));
  process.exit(0);
}

if (require.main === module) {
  main();
}