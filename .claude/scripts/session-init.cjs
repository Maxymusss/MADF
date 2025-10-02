#!/usr/bin/env node
/**
 * Claude Code Session Initialization Hook
 * Automatically runs on Claude Code startup to handle daily tasks
 */

const { autoRefreshDocs } = require('./auto-refresh-docs.cjs');

/**
 * Initialize Claude Code session with automated tasks
 */
async function initializeSession() {
  console.log('🚀 Initializing Claude Code session...');

  try {
    // Run automated documentation refresh check
    await autoRefreshDocs();

    console.log('✅ Session initialization complete');
  } catch (error) {
    console.warn('⚠️  Session initialization had issues:', error.message);
    console.log('✅ Continuing with Claude Code session...');
  }
}

// Run initialization
if (require.main === module) {
  initializeSession().catch((error) => {
    console.warn('⚠️  Session init error:', error.message);
    process.exit(0); // Don't block Claude Code startup
  });
}

module.exports = { initializeSession };