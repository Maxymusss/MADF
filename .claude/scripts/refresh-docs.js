#!/usr/bin/env node
/**
 * Force refresh specific documentation - bypasses session caching
 * Usage:
 *   node .claude/scripts/refresh-docs.js                    # Refresh all docs
 *   node .claude/scripts/refresh-docs.js langgraph         # Refresh specific doc
 *   node .claude/scripts/refresh-docs.js langgraph claude-code  # Refresh multiple docs
 */

const fs = require('fs');
const path = require('path');

// Note: cache-docs-simple.cjs is the main cache script

const args = process.argv.slice(2);
const forceRefresh = args.length === 0 ? 'all' : args;

async function forceRefreshDocs() {
  console.log('🔄 Force refreshing documentation...');

  if (Array.isArray(forceRefresh) && forceRefresh.length > 0) {
    console.log(`📋 Targeting: ${forceRefresh.join(', ')}`);
  } else {
    console.log('📋 Refreshing all documentation');
  }

  // Clear session tracking to force checks
  delete process.env.CLAUDE_SESSION_START;

  // Set force refresh flag
  process.env.FORCE_DOC_REFRESH = 'true';
  process.env.TARGET_DOCS = Array.isArray(forceRefresh) ? forceRefresh.join(',') : 'all';

  // Run the main cache script
  try {
    await require('./cache-docs-simple.js');
  } catch (error) {
    console.error('❌ Force refresh failed:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  forceRefreshDocs().catch(console.error);
}