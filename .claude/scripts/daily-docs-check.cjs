#!/usr/bin/env node
/**
 * Daily Documentation Check
 * Run this at the start of each Claude Code session to auto-refresh docs if needed
 * Usage: node .claude/scripts/daily-docs-check.cjs
 */

const { spawn } = require('child_process');
const path = require('path');

const PROJECT_ROOT = path.join(__dirname, '..', '..');
const CACHE_SCRIPT = path.join(__dirname, 'cache-docs-simple.cjs');

async function checkAndRefreshDocs() {
  console.log('🔍 Checking if documentation needs daily refresh...');

  return new Promise((resolve) => {
    const child = spawn('node', [CACHE_SCRIPT], {
      cwd: PROJECT_ROOT,
      stdio: ['ignore', 'pipe', 'pipe'],
      env: {
        ...process.env,
        // Don't force refresh - let the script decide based on first session logic
        FORCE_DOC_REFRESH: 'false'
      }
    });

    let output = '';
    let hasOutput = false;

    child.stdout.on('data', (data) => {
      const text = data.toString();
      output += text;

      // Only show relevant output
      if (text.includes('First Claude Code session today') ||
          text.includes('Updated:') ||
          text.includes('Skipped:') ||
          text.includes('Documentation cache complete') ||
          text.includes('⚠️') ||
          text.includes('✅')) {
        process.stdout.write(text);
        hasOutput = true;
      }
    });

    child.stderr.on('data', (data) => {
      // Only show warnings and errors
      const text = data.toString();
      if (text.includes('⚠️') || text.includes('Failed')) {
        process.stderr.write(text);
      }
    });

    child.on('close', (code) => {
      if (!hasOutput && code === 0) {
        console.log('📖 Documentation already fresh today');
      }
      resolve(code);
    });

    child.on('error', (error) => {
      console.warn('⚠️  Could not check documentation:', error.message);
      resolve(1);
    });

    // Timeout after 3 minutes to not block session startup
    setTimeout(() => {
      child.kill();
      console.warn('⚠️  Documentation check timed out - continuing...');
      resolve(0);
    }, 180000);
  });
}

// Export for use in other scripts
module.exports = { checkAndRefreshDocs };

// Run if called directly
if (require.main === module) {
  checkAndRefreshDocs().then((code) => {
    process.exit(code);
  });
}