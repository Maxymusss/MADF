#!/usr/bin/env node

// MCP Preloader - Ensures dotenv is loaded before MCP initialization
require('dotenv').config();

console.log('✅ Environment variables loaded from .env');
console.log(`📦 Loaded ${Object.keys(process.env).filter(key => !key.startsWith('npm_')).length} environment variables`);

// Verify critical environment variables are available
const criticalVars = ['GITHUB_TOKEN', 'OBSIDIAN_API_KEY', 'SENTRY_DSN'];
const missing = criticalVars.filter(v => !process.env[v]);

if (missing.length > 0) {
  console.warn(`⚠️  Missing environment variables: ${missing.join(', ')}`);
} else {
  console.log('✅ All critical environment variables are set');
}