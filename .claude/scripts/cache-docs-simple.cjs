#!/usr/bin/env node
/**
 * Simple documentation caching - reads MCP list from CLAUDE.md
 * Checks remote freshness once per day before downloading
 * Run: node .claude/scripts/cache-docs-simple.js
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const crypto = require('crypto');

const DOCS_DIR = path.join(__dirname, '..', 'docs-cache');
const PROJECT_ROOT = path.join(__dirname, '..', '..');
const CLAUDE_MD_PATH = path.join(PROJECT_ROOT, 'CLAUDE.md');

// Static documentation sources (non-MCP)
const STATIC_DOCS = {
  // Core Framework Docs
  'langgraph': 'https://langchain-ai.github.io/langgraph/llms.txt',
  'langchain': 'https://python.langchain.com/llms.txt',
  'claude-api': 'https://docs.anthropic.com/en/api/getting-started',

  // Claude Code Docs
  'claude-code': 'https://docs.anthropic.com/en/docs/claude-code/claude_code_docs_map.md',
  'claude-code-getting-started': 'https://docs.anthropic.com/en/docs/claude-code/getting-started',
  'claude-code-features': 'https://docs.anthropic.com/en/docs/claude-code/features',
  'claude-code-mcp': 'https://docs.anthropic.com/en/docs/claude-code/mcp',

  // MCP Tools
  'mcp-use': 'https://raw.githubusercontent.com/mcp-use/mcp-use-ts/main/README.md',

  // Development & Research Tools
  'tmux-orchestrator': 'https://raw.githubusercontent.com/Jedward23/Tmux-Orchestrator/main/README.md',
  'gpt-researcher': 'https://raw.githubusercontent.com/assafelovic/gpt-researcher/master/README.md',
  'graphiti-mcp': 'https://raw.githubusercontent.com/gifflet/graphiti-mcp-server/main/README.md',
  'serena': 'https://raw.githubusercontent.com/oraios/serena/main/README.md',

  // Additional MCP Servers
  'github-mcp-server': 'https://raw.githubusercontent.com/github/github-mcp-server/main/README.md',
  'git-mcp': 'https://raw.githubusercontent.com/idosal/git-mcp/main/README.md',

  // BMAD-METHOD Documentation
  'bmad-readme': 'https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/README.md',
  'bmad-changelog': 'https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/CHANGELOG.md',
  'bmad-contributing': 'https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/CONTRIBUTING.md',
  'bmad-pr-opencode': 'https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/PR-opencode-agents-generator.md',
  'bmad-guiding-principles': 'https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/docs/GUIDING-PRINCIPLES.md',
  'bmad-core-architecture': 'https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/docs/core-architecture.md',
  'bmad-ide-workflow': 'https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/docs/enhanced-ide-development-workflow.md',
  'bmad-expansion-packs': 'https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/docs/expansion-packs.md',
  'bmad-flattener': 'https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/docs/flattener.md',
  'bmad-pull-requests': 'https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/docs/how-to-contribute-with-pull-requests.md',
  'bmad-user-guide': 'https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/docs/user-guide.md',
  'bmad-versioning': 'https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/docs/versioning-and-releases.md',
  'bmad-versions': 'https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/docs/versions.md',
  'bmad-brownfield': 'https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/docs/working-in-the-brownfield.md'
};

// MCP documentation URL patterns
const MCP_DOC_PATTERNS = {
  'task-master-ai': 'https://raw.githubusercontent.com/chrishayuk/task-master-ai/main/README.md',
  'sequential-thinking': 'https://raw.githubusercontent.com/modelcontextprotocol/server-sequential-thinking/main/README.md',
  'filesystem': 'https://raw.githubusercontent.com/modelcontextprotocol/servers/main/src/filesystem/README.md',
  'postgres': 'https://raw.githubusercontent.com/modelcontextprotocol/servers/main/src/postgres/README.md',
  'playwright': 'https://raw.githubusercontent.com/modelcontextprotocol/servers/main/src/playwright/README.md',
  'notion': 'https://raw.githubusercontent.com/modelcontextprotocol/servers/main/src/notion/README.md',
  'context7': 'https://raw.githubusercontent.com/upstash/context7-mcp/main/README.md',
  'langgraph-docs-mcp': 'https://raw.githubusercontent.com/chriscarrollsmith/mcpdoc/main/README.md',
  'outlook': 'https://raw.githubusercontent.com/your-repo/outlook-mcp-server/main/README.md',
  'claude-context': 'https://raw.githubusercontent.com/zilliztech/claude-context/main/README.md',
  'mcp-use': 'https://raw.githubusercontent.com/mcp-use/mcp-use-ts/main/README.md',
  'github-mcp-server': 'https://raw.githubusercontent.com/github/github-mcp-server/main/README.md',
  'git-mcp': 'https://raw.githubusercontent.com/idosal/git-mcp/main/README.md'
};

function readMCPsFromClaudeMD() {
  const mcpData = { essential: [], optional: [] };
  
  try {
    if (!fs.existsSync(CLAUDE_MD_PATH)) {
      console.warn('⚠️  CLAUDE.md not found');
      return mcpData;
    }

    const claudeContent = fs.readFileSync(CLAUDE_MD_PATH, 'utf8');
    
    // Extract essential MCPs
    const essentialMatch = claudeContent.match(/### Essential Servers[\s\S]*?- \*\*([\s\S]*?)\*\*:[\s\S]*?(?=### Optional Servers)/);
    if (essentialMatch) {
      const essentialSection = essentialMatch[0];
      const essentialMatches = essentialSection.match(/- \*\*(.*?)\*\*:/g);
      if (essentialMatches) {
        mcpData.essential = essentialMatches.map(match => 
          match.replace(/- \*\*(.*?)\*\*:/, '$1').toLowerCase()
        );
      }
    }
    
    // Extract optional MCPs
    const optionalMatch = claudeContent.match(/### Optional Servers[\s\S]*?(?=### MCP Installation Rule)/);
    if (optionalMatch) {
      const optionalSection = optionalMatch[0];
      const optionalMatches = optionalSection.match(/- \*\*(.*?)\*\*:/g);
      if (optionalMatches) {
        mcpData.optional = optionalMatches.map(match => 
          match.replace(/- \*\*(.*?)\*\*:/, '$1').toLowerCase()
        );
      }
    }
    
  } catch (error) {
    console.warn('⚠️  Failed to parse MCPs from CLAUDE.md:', error.message);
  }

  return mcpData;
}

function generateDocSources() {
  const mcpData = readMCPsFromClaudeMD();
  const docSources = { ...STATIC_DOCS };
  
  // Add MCP documentation sources
  [...mcpData.essential, ...mcpData.optional].forEach(mcpName => {
    if (MCP_DOC_PATTERNS[mcpName]) {
      docSources[`mcp-${mcpName}`] = MCP_DOC_PATTERNS[mcpName];
    } else {
      console.warn(`⚠️  No documentation URL pattern for MCP: ${mcpName}`);
    }
  });
  
  return { docSources, mcpData };
}

async function getRemoteETag(url) {
  return new Promise((resolve) => {
    const urlObj = new URL(url);
    const options = {
      hostname: urlObj.hostname,
      path: urlObj.pathname + urlObj.search,
      method: 'HEAD',
      headers: { 'User-Agent': 'MADF-Doc-Cache/1.0' }
    };

    const req = https.request(options, (res) => {
      resolve(res.headers.etag || res.headers['last-modified'] || null);
    });

    req.on('error', () => resolve(null));
    req.setTimeout(5000, () => {
      req.destroy();
      resolve(null);
    });
    req.end();
  });
}

async function downloadFile(url, filepath) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(filepath);
    const urlObj = new URL(url);

    const options = {
      hostname: urlObj.hostname,
      path: urlObj.pathname + urlObj.search,
      headers: { 'User-Agent': 'MADF-Doc-Cache/1.0' }
    };

    https.get(options, (response) => {
      if (response.statusCode === 302 || response.statusCode === 301 || response.statusCode === 307 || response.statusCode === 308) {
        // Handle redirects (support both absolute and relative URLs)
        file.close();
        fs.unlinkSync(filepath);
        const redirectUrl = response.headers.location.startsWith('http')
          ? response.headers.location
          : `https://${urlObj.hostname}${response.headers.location}`;
        return downloadFile(redirectUrl, filepath).then(resolve).catch(reject);
      }

      if (response.statusCode !== 200) {
        file.close();
        fs.unlinkSync(filepath);
        reject(new Error(`HTTP ${response.statusCode} for ${url}`));
        return;
      }

      response.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve();
      });
    }).on('error', (err) => {
      file.close();
      fs.unlinkSync(filepath);
      reject(err);
    });
  });
}

function getFileHash(filepath) {
  try {
    const content = fs.readFileSync(filepath);
    return crypto.createHash('md5').update(content).digest('hex');
  } catch {
    return null;
  }
}

function saveMetadata(name, etag, hash) {
  const metaPath = path.join(DOCS_DIR, '.metadata.json');
  let metadata = {};

  try {
    metadata = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
  } catch {}

  metadata[name] = { etag, hash, lastChecked: Date.now(), lastCheckedDate: new Date().toDateString() };
  fs.writeFileSync(metaPath, JSON.stringify(metadata, null, 2));
}

function updateClamdeMdTimestamp() {
  try {
    if (!fs.existsSync(CLAUDE_MD_PATH)) {
      console.warn('⚠️  CLAUDE.md not found, skipping timestamp update');
      return;
    }

    const claudeContent = fs.readFileSync(CLAUDE_MD_PATH, 'utf8');
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
    const dateStr = now.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit', year: 'numeric' });
    const timestamp = `${timeStr} ${dateStr}`;

    // Update the docs-cache timestamp line
    const updatedContent = claudeContent.replace(
      /- \*\*Docs Cache\*\*: Use `\.claude\/docs-cache\/` for cached documentation \([^)]+\)/,
      `- **Docs Cache**: Use \`.claude/docs-cache/\` for cached documentation (13 files, 2.1MB total, ${timestamp})`
    );

    fs.writeFileSync(CLAUDE_MD_PATH, updatedContent);
    console.log(`✅ Updated CLAUDE.md timestamp: ${timestamp}`);
  } catch (error) {
    console.warn('⚠️  Failed to update CLAUDE.md timestamp:', error.message);
  }
}

function getMetadata(name) {
  try {
    const metaPath = path.join(DOCS_DIR, '.metadata.json');
    const metadata = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
    return metadata[name] || {};
  } catch {
    return {};
  }
}

async function main() {
  // Create docs cache directory
  if (!fs.existsSync(DOCS_DIR)) {
    fs.mkdirSync(DOCS_DIR, { recursive: true });
  }

  console.log('📖 Reading MCP list from CLAUDE.md...');
  const { docSources, mcpData } = generateDocSources();

  console.log(`📋 Found ${mcpData.essential.length} essential MCPs, ${mcpData.optional.length} optional MCPs`);

  console.log('🔄 Checking documentation freshness...');

  let updatedCount = 0;
  let skippedCount = 0;

  for (const [name, url] of Object.entries(docSources)) {
    try {
      const filepath = path.join(DOCS_DIR, `${name}-docs.md`);
      const metadata = getMetadata(name);

      // Check if file exists and was checked today
      const fileExists = fs.existsSync(filepath);
      const today = new Date().toDateString();
      const isToday = metadata.lastCheckedDate === today;
      const forceRefresh = process.env.FORCE_DOC_REFRESH === 'true';
      const targetDocs = process.env.TARGET_DOCS || 'all';
      const shouldForceThis = forceRefresh && (targetDocs === 'all' || targetDocs.split(',').includes(name));

      if (fileExists && isToday && !shouldForceThis) {
        console.log(`⏭️  Skipped: ${name} (already checked today)`);
        skippedCount++;
        continue;
      }

      if (shouldForceThis) {
        console.log(`🔄 Force refreshing: ${name}`);
      }

      // Check remote freshness
      const remoteETag = await getRemoteETag(url);
      const localHash = getFileHash(filepath);

      if (fileExists && remoteETag && metadata.etag === remoteETag && !shouldForceThis) {
        console.log(`✅ Fresh: ${name} (no changes)`);
        saveMetadata(name, remoteETag, localHash);
        skippedCount++;
        continue;
      }

      // Download updated file
      console.log(`📥 Downloading: ${name}...`);
      await downloadFile(url, filepath);

      const newHash = getFileHash(filepath);
      saveMetadata(name, remoteETag, newHash);

      console.log(`✅ Updated: ${name}`);
      updatedCount++;

    } catch (error) {
      console.warn(`⚠️  Failed to process ${name}: ${error.message}`);
    }
  }

  // Create/update index file
  const coreFrameworkDocs = Object.keys(STATIC_DOCS).filter(name =>
    ['langgraph', 'langchain', 'claude-api'].includes(name)
  );

  const claudeCodeDocs = Object.keys(STATIC_DOCS).filter(name =>
    name.startsWith('claude-code')
  );

  const bmadDocs = Object.keys(STATIC_DOCS).filter(name =>
    name.startsWith('bmad-')
  );

  const toolsDocs = Object.keys(STATIC_DOCS).filter(name =>
    ['mcp-use', 'tmux-orchestrator', 'gpt-researcher', 'graphiti-mcp', 'serena', 'github-mcp-server', 'git-mcp'].includes(name)
  );

  const essentialMCPDocs = mcpData.essential.map(name => `mcp-${name}`);
  const optionalMCPDocs = mcpData.optional.map(name => `mcp-${name}`);

  const indexContent = `# Documentation Cache

Last updated: ${new Date().toISOString()}
Files updated: ${updatedCount}
Files skipped: ${skippedCount}

## Core Framework
${coreFrameworkDocs.map(name => `- [${name}](${name}-docs.md)`).join('\n')}

## Claude Code
${claudeCodeDocs.map(name => `- [${name}](${name}-docs.md)`).join('\n')}

## Development Tools
${toolsDocs.map(name => `- [${name}](${name}-docs.md)`).join('\n')}

## BMAD-METHOD
${bmadDocs.map(name => `- [${name}](${name}-docs.md)`).join('\n')}

## Essential MCP Servers
${essentialMCPDocs.map(name => `- [${name}](${name}-docs.md)`).join('\n')}

## Optional MCP Servers
${optionalMCPDocs.map(name => `- [${name}](${name}-docs.md)`).join('\n')}
`;

  fs.writeFileSync(path.join(DOCS_DIR, 'README.md'), indexContent);

  // Update CLAUDE.md timestamp
  updateClamdeMdTimestamp();

  console.log(`\n✅ Documentation cache complete!`);
  console.log(`📊 Updated: ${updatedCount} files`);
  console.log(`⏭️  Skipped: ${skippedCount} files`);
  console.log(`📁 Cache location: ${DOCS_DIR}`);
}

if (require.main === module) {
  main().catch(console.error);
}