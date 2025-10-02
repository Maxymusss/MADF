#!/usr/bin/env node

/**
 * Essential Tools List Updater
 * Updates the essential tools list in CLAUDE.md based on usage analytics
 */

import { readFileSync, writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import ToolAnalytics from '../tools/tool-analytics.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = resolve(__dirname, '../..');

class EssentialToolsUpdater {
  constructor() {
    this.analytics = new ToolAnalytics();
    this.claudeFile = resolve(projectRoot, 'CLAUDE.md');
    this.thresholds = {
      essential: 5,      // Tools used 5+ times become essential
      frequent: 10,      // Tools used 10+ times are highly essential
      minSessions: 3     // Need at least 3 sessions of data
    };
  }

  async updateEssentialTools() {
    console.log('🔄 Updating Essential Tools List...');
    console.log('═'.repeat(50));

    // Get analytics data
    const data = this.analytics.loadData();
    if (!data) {
      console.log('❌ No analytics data available');
      return;
    }

    const sessionCount = Object.keys(data.sessions).length;
    if (sessionCount < this.thresholds.minSessions) {
      console.log(`⚠️  Need at least ${this.thresholds.minSessions} sessions for reliable data (current: ${sessionCount})`);
      return;
    }

    // Calculate tool rankings for last 2 weeks
    const stats = this.analytics.calculateStats(data, 'month');

    console.log(`📊 Analyzing ${stats.overview.totalCalls} tool calls across ${stats.overview.totalSessions} sessions`);

    // Categorize tools by usage frequency
    const toolCategories = this.categorizeTools(stats.tools.mostUsed);

    // Generate new essential tools list
    const newEssentialTools = this.generateEssentialToolsList(toolCategories);

    // Update CLAUDE.md
    const updated = this.updateCLAUDEFile(newEssentialTools);

    if (updated) {
      console.log('✅ Essential tools list updated in CLAUDE.md');
      console.log('\n📋 New Essential Tools:');
      newEssentialTools.forEach(tool => {
        console.log(`  • ${tool.name} (${tool.calls} calls, ${tool.successRate.toFixed(1)}% success)`);
      });

      // Show changes summary
      this.showUpdateSummary(toolCategories);
    } else {
      console.log('ℹ️  No changes needed - current list is up to date');
    }
  }

  categorizeTools(toolStats) {
    const categories = {
      highly_essential: [],  // 10+ calls
      essential: [],         // 5-9 calls
      frequent: [],          // 2-4 calls
      occasional: []         // 1 call
    };

    toolStats.forEach(tool => {
      if (tool.calls >= this.thresholds.frequent) {
        categories.highly_essential.push(tool);
      } else if (tool.calls >= this.thresholds.essential) {
        categories.essential.push(tool);
      } else if (tool.calls >= 2) {
        categories.frequent.push(tool);
      } else {
        categories.occasional.push(tool);
      }
    });

    return categories;
  }

  generateEssentialToolsList(categories) {
    // Combine highly essential and essential tools
    const essentialTools = [
      ...categories.highly_essential,
      ...categories.essential
    ];

    // Sort by usage frequency and success rate
    essentialTools.sort((a, b) => {
      if (b.calls !== a.calls) return b.calls - a.calls;
      return b.successRate - a.successRate;
    });

    // Limit to top 15 tools to avoid context bloat
    return essentialTools.slice(0, 15);
  }

  updateCLAUDEFile(newEssentialTools) {
    try {
      const content = readFileSync(this.claudeFile, 'utf8');

      // Find the essential tools section
      const startMarker = '**Current Essential Tools** (Updated based on usage analytics every 1-2 weeks):';
      const endMarker = '**Cross-MCP Availability**:';

      const startIndex = content.indexOf(startMarker);
      const endIndex = content.indexOf(endMarker);

      if (startIndex === -1 || endIndex === -1) {
        console.log('⚠️  Could not find essential tools section in CLAUDE.md');
        return false;
      }

      // Generate new tools list with descriptions
      const toolsList = this.generateToolsListText(newEssentialTools);

      // Replace the section
      const beforeSection = content.substring(0, startIndex + startMarker.length);
      const afterSection = content.substring(endIndex);

      const newContent = beforeSection + '\n' + toolsList + '\n' + afterSection;

      // Add update timestamp comment
      const timestamp = new Date().toISOString().split('T')[0];
      const updatedContent = newContent.replace(
        startMarker,
        `${startMarker}\n<!-- Last updated: ${timestamp} based on analytics -->`
      );

      writeFileSync(this.claudeFile, updatedContent);
      return true;
    } catch (error) {
      console.error('❌ Error updating CLAUDE.md:', error.message);
      return false;
    }
  }

  generateToolsListText(tools) {
    const lines = [];

    tools.forEach(tool => {
      const toolName = this.getCleanToolName(tool.name);
      const description = this.getToolDescription(toolName, tool);
      lines.push(`- \`${toolName}\` - ${description}`);
    });

    return lines.join('\n');
  }

  getCleanToolName(toolName) {
    // Remove server prefixes for display
    if (toolName.includes('__')) {
      const parts = toolName.split('__');
      if (parts[0] === 'mcp' && parts.length === 3) {
        return `mcp__${parts[1]}__${parts[2]}`;
      } else if (parts.length === 2) {
        return parts[1];
      }
    }
    return toolName;
  }

  getToolDescription(toolName, tool) {
    // Focus only on MCP tools and essential coordination tools
    const descriptions = {
      'call_tool': `MCP tool execution and server management (${tool.calls} calls)`,
      'search_code': `Semantic code search and indexing (${tool.calls} calls)`,
      'index_codebase': `Codebase indexing for semantic search (${tool.calls} calls)`,
      'search_repositories': `GitHub repository operations (${tool.calls} calls, requires token)`,
      'get_user_info': `GitHub user information (${tool.calls} calls)`,
      'list_repositories': `GitHub repository listing (${tool.calls} calls)`,
      'list_servers': `MCP server management (${tool.calls} calls)`,
      'enable_server': `MCP server activation (${tool.calls} calls)`,
      'disable_server': `MCP server deactivation (${tool.calls} calls)`,
      'Task': `Agent and workflow orchestration (${tool.calls} calls)`,
      'TodoWrite': `Task progress tracking (${tool.calls} calls)`,
      'WebFetch': `Web content retrieval for documentation (${tool.calls} calls)`,
      'WebSearch': `Web search for current information (${tool.calls} calls)`,
      'read_multiple_files': `Batch file reading (${tool.calls} calls)`,
      'search_files': `Advanced file search (${tool.calls} calls)`
    };

    return descriptions[toolName] || `${toolName} (${tool.calls} calls, ${tool.successRate.toFixed(1)}% success)`;
  }

  showUpdateSummary(categories) {
    console.log('\n📈 Usage Analysis Summary:');
    console.log(`  Highly Essential (10+ calls): ${categories.highly_essential.length} tools`);
    console.log(`  Essential (5-9 calls): ${categories.essential.length} tools`);
    console.log(`  Frequent (2-4 calls): ${categories.frequent.length} tools`);
    console.log(`  Occasional (1 call): ${categories.occasional.length} tools`);

    if (categories.frequent.length > 0) {
      console.log('\n💡 Frequent tools (consider promoting):');
      categories.frequent.slice(0, 5).forEach(tool => {
        console.log(`    • ${tool.name} (${tool.calls} calls)`);
      });
    }
  }

  async generateReport() {
    console.log('📊 Essential Tools Analytics Report');
    console.log('═'.repeat(50));

    const stats = this.analytics.calculateStats(this.analytics.loadData(), 'month');

    console.log('🏆 Current Top 10 Tools:');
    stats.tools.mostUsed.slice(0, 10).forEach((tool, i) => {
      const essential = tool.calls >= this.thresholds.essential ? '⭐' : '  ';
      console.log(`${essential} ${i + 1}. ${tool.name} (${tool.calls} calls, ${tool.successRate.toFixed(1)}% success)`);
    });

    console.log('\n⚡ Performance Leaders:');
    stats.tools.fastest.slice(0, 5).forEach((tool, i) => {
      console.log(`  ${i + 1}. ${tool.name} (${tool.avgTime.toFixed(1)}ms avg)`);
    });

    console.log('\n🎯 Recommendations:');
    const categories = this.categorizeTools(stats.tools.mostUsed);
    if (categories.frequent.length > 3) {
      console.log('  • Consider promoting frequent tools to essential list');
    }
    if (categories.highly_essential.length > 10) {
      console.log('  • Context optimization needed - too many highly essential tools');
    }
    if (stats.overview.successRate < 90) {
      console.log('  • Review tools with low success rates');
    }
  }
}

// CLI Interface
const args = process.argv.slice(2);
const command = args[0] || 'update';

const updater = new EssentialToolsUpdater();

switch (command) {
  case 'update':
    updater.updateEssentialTools();
    break;
  case 'report':
    updater.generateReport();
    break;
  case 'help':
  default:
    console.log(`
🔧 Essential Tools Updater

USAGE:
  node .claude/scripts/update-essential-tools.js <command>

COMMANDS:
  update    Update essential tools list in CLAUDE.md (default)
  report    Show current tool rankings and recommendations
  help      Show this help message

EXAMPLES:
  node .claude/scripts/update-essential-tools.js update
  node .claude/scripts/update-essential-tools.js report
`);
    break;
}

export default EssentialToolsUpdater;