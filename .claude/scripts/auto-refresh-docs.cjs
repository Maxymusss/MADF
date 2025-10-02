#!/usr/bin/env node
/**
 * Auto-refresh documentation on first Claude Code session each day
 * This script runs in the background and triggers doc refresh when needed
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const PROJECT_ROOT = path.join(__dirname, '..', '..');
const DOCS_DIR = path.join(__dirname, '..', 'docs-cache');
const SESSION_TRACKER = path.join(DOCS_DIR, '.session-tracker.json');
const CACHE_SCRIPT = path.join(__dirname, 'cache-docs-simple.cjs');

/**
 * Check if this is the first session today
 */
function isFirstSessionToday() {
  try {
    if (!fs.existsSync(SESSION_TRACKER)) {
      return true;
    }

    const tracker = JSON.parse(fs.readFileSync(SESSION_TRACKER, 'utf8'));
    const today = new Date().toDateString();

    return tracker.lastSession !== today;
  } catch (error) {
    console.log('⚠️  Session tracker error, assuming first session:', error.message);
    return true;
  }
}

/**
 * Update session tracker with today's date
 */
function updateSessionTracker() {
  const today = new Date().toDateString();
  const tracker = {
    lastSession: today,
    lastRefresh: new Date().toISOString(),
    autoRefreshEnabled: true
  };

  try {
    if (!fs.existsSync(DOCS_DIR)) {
      fs.mkdirSync(DOCS_DIR, { recursive: true });
    }
    fs.writeFileSync(SESSION_TRACKER, JSON.stringify(tracker, null, 2));
  } catch (error) {
    console.warn('⚠️  Could not update session tracker:', error.message);
  }
}

/**
 * Run documentation refresh in background
 */
function runDocRefresh() {
  return new Promise((resolve, reject) => {
    console.log('🔄 Starting automated daily documentation refresh...');

    const child = spawn('node', [CACHE_SCRIPT], {
      cwd: PROJECT_ROOT,
      env: {
        ...process.env,
        FORCE_DOC_REFRESH: 'false', // Only refresh stale docs
        AUTO_REFRESH: 'true'
      },
      stdio: ['ignore', 'pipe', 'pipe']
    });

    let output = '';
    let errors = '';

    child.stdout.on('data', (data) => {
      output += data.toString();
    });

    child.stderr.on('data', (data) => {
      errors += data.toString();
    });

    child.on('close', (code) => {
      if (code === 0) {
        console.log('✅ Documentation refresh completed successfully');
        // Only show summary, not full output
        const lines = output.split('\n');
        const summary = lines.filter(line =>
          line.includes('Updated:') ||
          line.includes('Skipped:') ||
          line.includes('Documentation cache complete')
        );
        console.log(summary.join('\n'));
        resolve(output);
      } else {
        console.warn('⚠️  Documentation refresh had issues (exit code:', code, ')');
        if (errors) console.warn('Errors:', errors);
        resolve(output); // Don't fail the session, just warn
      }
    });

    child.on('error', (error) => {
      console.warn('⚠️  Could not run documentation refresh:', error.message);
      resolve(''); // Don't fail the session
    });

    // Timeout after 5 minutes
    setTimeout(() => {
      child.kill();
      console.warn('⚠️  Documentation refresh timed out, continuing...');
      resolve('');
    }, 300000);
  });
}

/**
 * Main function - check and refresh if needed
 */
async function autoRefreshDocs() {
  try {
    if (isFirstSessionToday()) {
      console.log('📅 First Claude Code session today - checking documentation freshness...');

      // Update tracker immediately to prevent multiple simultaneous refreshes
      updateSessionTracker();

      // Run refresh (non-blocking for user)
      await runDocRefresh();
    } else {
      console.log('📖 Documentation already checked today');
    }
  } catch (error) {
    console.warn('⚠️  Auto-refresh error:', error.message);
  }
}

// Export for use in other scripts
module.exports = { autoRefreshDocs, isFirstSessionToday };

// Run if called directly
if (require.main === module) {
  autoRefreshDocs().catch(console.error);
}