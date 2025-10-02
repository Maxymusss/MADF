#!/usr/bin/env node

/**
 * Tool Usage Analytics Script
 * Generates bi-weekly suggestions for essential tools based on usage patterns
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { resolve, dirname } from 'path';

class ToolAnalyzer {
  constructor() {
    this.toolUsageFile = resolve('.claude/analytics/tool-usage.json');
    this.outputDir = resolve('.claude/docs');
    this.configDir = resolve('.claude/proxy-configs');
    this.threshold = 5; // Minimum usage count to be considered essential
  }

  loadToolUsage() {
    if (!existsSync(this.toolUsageFile)) {
      console.log('⚠️ No tool usage data found at:', this.toolUsageFile);
      return {};
    }

    try {
      const data = readFileSync(this.toolUsageFile, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      console.error('❌ Failed to load tool usage data:', error.message);
      return {};
    }
  }

  analyzeUsagePatterns(toolUsage) {
    const serverStats = {};
    const now = Date.now();
    const twoWeeksAgo = now - (14 * 24 * 60 * 60 * 1000);

    // Group tools by server and calculate usage stats
    Object.entries(toolUsage).forEach(([toolKey, usageData]) => {
      // Extract server name from tool key (e.g., "github__search_repositories" -> "github")
      let serverName = 'unknown';
      let toolName = toolKey;

      if (toolKey.includes('__')) {
        [serverName, toolName] = toolKey.split('__', 2);
      } else if (toolKey.startsWith('mcp__')) {
        // Handle MCP tools like "mcp__github__search_repositories"
        const parts = toolKey.split('__');
        if (parts.length >= 3) {
          serverName = parts[1];
          toolName = parts.slice(2).join('__');
        }
      }

      if (!serverStats[serverName]) {
        serverStats[serverName] = {
          tools: {},
          totalUsage: 0,
          recentUsage: 0
        };
      }

      // Calculate total and recent usage
      const totalCount = usageData.count || 0;
      const recentCount = (usageData.calls || [])
        .filter(call => call.timestamp > twoWeeksAgo)
        .length;

      serverStats[serverName].tools[toolName] = {
        totalCount,
        recentCount,
        avgExecutionTime: usageData.avgExecutionTime || 0,
        successRate: usageData.successRate || 0,
        lastUsed: usageData.lastUsed || 0
      };

      serverStats[serverName].totalUsage += totalCount;
      serverStats[serverName].recentUsage += recentCount;
    });

    return serverStats;
  }

  generateSuggestions(serverStats) {
    const suggestions = {};
    const currentDate = new Date().toISOString().split('T')[0].replace(/-/g, '');

    Object.entries(serverStats).forEach(([serverName, stats]) => {
      if (serverName === 'unknown' || stats.totalUsage === 0) return;

      // Sort tools by recent usage, then by total usage
      const sortedTools = Object.entries(stats.tools)
        .sort(([, a], [, b]) => {
          if (b.recentCount !== a.recentCount) {
            return b.recentCount - a.recentCount;
          }
          return b.totalCount - a.totalCount;
        });

      // Essential tools: used recently and frequently
      const essentialTools = sortedTools
        .filter(([, toolStats]) =>
          toolStats.recentCount >= this.threshold ||
          (toolStats.totalCount >= this.threshold * 2 && toolStats.successRate > 0.8)
        )
        .map(([toolName]) => toolName);

      // Recommended tools: occasionally used but reliable
      const recommendedTools = sortedTools
        .filter(([, toolStats]) =>
          !essentialTools.includes(toolStats) &&
          toolStats.totalCount >= 2 &&
          toolStats.successRate > 0.7
        )
        .map(([toolName]) => toolName);

      if (essentialTools.length > 0) {
        suggestions[serverName] = {
          essential: essentialTools,
          recommended: recommendedTools,
          stats: {
            totalTools: Object.keys(stats.tools).length,
            essentialCount: essentialTools.length,
            recommendedCount: recommendedTools.length,
            totalUsage: stats.totalUsage,
            recentUsage: stats.recentUsage,
            tokenSavingsEstimate: this.estimateTokenSavings(
              Object.keys(stats.tools).length,
              essentialTools.length
            )
          }
        };
      }
    });

    return { suggestions, date: currentDate };
  }

  estimateTokenSavings(totalTools, essentialTools) {
    // Rough estimate: each tool definition costs ~150 tokens
    const tokensPerTool = 150;
    const savedTools = totalTools - essentialTools;
    return savedTools * tokensPerTool;
  }

  generateMarkdownReport(analysisResult) {
    const { suggestions, date } = analysisResult;

    let markdown = `# Tool Usage Analysis Report\n\n`;
    markdown += `**Generated**: ${new Date().toLocaleDateString()}\n`;
    markdown += `**Analysis Period**: Last 14 days\n`;
    markdown += `**Minimum Usage Threshold**: ${this.threshold} calls\n\n`;

    markdown += `## Executive Summary\n\n`;

    const totalServers = Object.keys(suggestions).length;
    const totalTokenSavings = Object.values(suggestions)
      .reduce((sum, server) => sum + server.stats.tokenSavingsEstimate, 0);

    markdown += `- **Servers Analyzed**: ${totalServers}\n`;
    markdown += `- **Estimated Token Savings**: ~${totalTokenSavings} tokens\n`;
    markdown += `- **Recommendation**: Use selective loading for optimal context efficiency\n\n`;

    Object.entries(suggestions).forEach(([serverName, data]) => {
      markdown += `## ${serverName.toUpperCase()} Server\n\n`;

      markdown += `### Statistics\n`;
      markdown += `- **Total Tools Available**: ${data.stats.totalTools}\n`;
      markdown += `- **Essential Tools**: ${data.stats.essentialCount}\n`;
      markdown += `- **Recommended Tools**: ${data.stats.recommendedCount}\n`;
      markdown += `- **Recent Usage**: ${data.stats.recentUsage} calls\n`;
      markdown += `- **Token Savings**: ~${data.stats.tokenSavingsEstimate} tokens\n\n`;

      if (data.essential.length > 0) {
        markdown += `### Essential Tools (High Usage)\n`;
        markdown += `\`\`\`javascript\n`;
        markdown += `// Enable with essential tools only\n`;
        markdown += `enable_server('${serverName}', {\n`;
        markdown += `  tools: [\n`;
        data.essential.forEach(tool => {
          markdown += `    '${tool}',\n`;
        });
        markdown += `  ]\n`;
        markdown += `})\n`;
        markdown += `\`\`\`\n\n`;
      }

      if (data.recommended.length > 0) {
        markdown += `### Recommended Tools (Moderate Usage)\n`;
        data.recommended.forEach(tool => {
          markdown += `- \`${tool}\`\n`;
        });
        markdown += `\n`;
      }

      markdown += `---\n\n`;
    });

    markdown += `## Usage Instructions\n\n`;
    markdown += `1. **Review** the essential tools list for each server\n`;
    markdown += `2. **Test** selective loading in development environment\n`;
    markdown += `3. **Update** your startup scripts to use selective loading\n`;
    markdown += `4. **Monitor** tool usage and adjust selections as needed\n\n`;

    markdown += `## Configuration Template\n\n`;
    markdown += `\`\`\`javascript\n`;
    markdown += `// Add to your initialization script\n`;
    Object.keys(suggestions).forEach(serverName => {
      const tools = suggestions[serverName].essential;
      if (tools.length > 0) {
        markdown += `enable_server('${serverName}', {tools: [${tools.map(t => `'${t}'`).join(', ')}]})\n`;
      }
    });
    markdown += `\`\`\`\n\n`;

    markdown += `*Next analysis scheduled: ${new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toLocaleDateString()}*\n`;

    return markdown;
  }

  ensureDirectoryExists(dirPath) {
    if (!existsSync(dirPath)) {
      mkdirSync(dirPath, { recursive: true });
    }
  }

  run() {
    console.log('🔍 Analyzing tool usage patterns...');

    // Load usage data
    const toolUsage = this.loadToolUsage();
    if (Object.keys(toolUsage).length === 0) {
      console.log('❌ No tool usage data available. Run some MCP tools first.');
      return;
    }

    // Analyze patterns
    const serverStats = this.analyzeUsagePatterns(toolUsage);
    const analysisResult = this.generateSuggestions(serverStats);

    if (Object.keys(analysisResult.suggestions).length === 0) {
      console.log('⚠️ No tools meet the usage threshold. Consider lowering the threshold or using tools more.');
      return;
    }

    // Generate report
    const report = this.generateMarkdownReport(analysisResult);

    // Ensure output directory exists
    this.ensureDirectoryExists(this.outputDir);

    // Write report file
    const reportFile = resolve(this.outputDir, `essential-tools-suggestions_${analysisResult.date}.md`);
    writeFileSync(reportFile, report, 'utf8');

    console.log('✅ Analysis complete!');
    console.log(`📄 Report saved to: ${reportFile}`);
    console.log(`🎯 Found suggestions for ${Object.keys(analysisResult.suggestions).length} servers`);

    // Show summary
    Object.entries(analysisResult.suggestions).forEach(([serverName, data]) => {
      console.log(`   ${serverName}: ${data.stats.essentialCount}/${data.stats.totalTools} essential tools (~${data.stats.tokenSavingsEstimate} token savings)`);
    });
  }
}

// Run the analyzer
const analyzer = new ToolAnalyzer();
analyzer.run();