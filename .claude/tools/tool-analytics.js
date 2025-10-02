/**
 * Tool Analytics Dashboard
 * Provides reporting and visualization for tool usage statistics
 */

import { readFileSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = resolve(__dirname, '../..');

class ToolAnalytics {
  constructor() {
    this.dataFile = resolve(projectRoot, '.claude/analytics/tool-usage.json');
  }

  loadData() {
    if (!existsSync(this.dataFile)) {
      return null;
    }

    try {
      return JSON.parse(readFileSync(this.dataFile, 'utf8'));
    } catch (error) {
      console.error('Error loading analytics data:', error.message);
      return null;
    }
  }

  /**
   * Generate comprehensive analytics report
   * @param {Object} options - Report options
   * @param {string} options.timeframe - 'session', 'today', 'week', 'month', 'all'
   * @param {boolean} options.detailed - Include detailed breakdown
   * @param {string} options.format - 'text', 'json', 'table'
   */
  generateReport(options = {}) {
    const { timeframe = 'session', detailed = false, format = 'text' } = options;
    const data = this.loadData();

    if (!data) {
      return this.formatOutput('No tracking data available', format);
    }

    const stats = this.calculateStats(data, timeframe);

    if (format === 'json') {
      return JSON.stringify(stats, null, 2);
    }

    if (format === 'table') {
      return this.formatAsTable(stats, detailed);
    }

    return this.formatAsText(stats, detailed);
  }

  calculateStats(data, timeframe) {
    const now = new Date();
    let relevantSessions = [];

    // Filter sessions based on timeframe
    for (const [sessionId, sessionData] of Object.entries(data.sessions)) {
      const sessionStart = new Date(sessionData.startTime);
      let include = false;

      switch (timeframe) {
        case 'session':
          // Get the most recent session
          include = true;
          break;
        case 'today':
          include = sessionStart.toDateString() === now.toDateString();
          break;
        case 'week':
          const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
          include = sessionStart >= weekAgo;
          break;
        case 'month':
          const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
          include = sessionStart >= monthAgo;
          break;
        case 'all':
        default:
          include = true;
      }

      if (include) {
        relevantSessions.push({ sessionId, ...sessionData });
      }
    }

    // If session timeframe, get only the most recent session
    if (timeframe === 'session' && relevantSessions.length > 0) {
      relevantSessions = [relevantSessions.sort((a, b) =>
        new Date(b.startTime) - new Date(a.startTime))[0]];
    }

    return this.aggregateSessionStats(relevantSessions, data.globalStats);
  }

  aggregateSessionStats(sessions, globalStats) {
    const stats = {
      overview: {
        totalSessions: sessions.length,
        totalCalls: 0,
        averageExecutionTime: 0,
        successRate: 0,
        timespan: this.getTimespan(sessions)
      },
      tools: {
        mostUsed: [],
        leastUsed: [],
        fastest: [],
        slowest: [],
        mostReliable: [],
        leastReliable: []
      },
      servers: {
        usage: {},
        reliability: {}
      },
      toolTypes: {
        distribution: {},
        performance: {}
      },
      trends: {
        hourlyDistribution: new Array(24).fill(0),
        recentActivity: []
      }
    };

    let totalExecutionTime = 0;
    let totalSuccess = 0;
    let allTools = [];
    const toolStats = {};
    const serverStats = {};
    const typeStats = {};

    // Process all tool calls
    for (const session of sessions) {
      for (const tool of session.tools) {
        const toolKey = tool.serverName ? `${tool.serverName}__${tool.toolName}` : tool.toolName;

        allTools.push(tool);
        stats.overview.totalCalls++;
        totalExecutionTime += tool.executionTime || 0;
        if (tool.success) totalSuccess++;

        // Update hourly distribution
        const hour = new Date(tool.timestamp).getHours();
        stats.trends.hourlyDistribution[hour]++;

        // Tool statistics
        if (!toolStats[toolKey]) {
          toolStats[toolKey] = {
            name: toolKey,
            toolName: tool.toolName,
            serverName: tool.serverName,
            calls: 0,
            totalTime: 0,
            successes: 0,
            failures: 0,
            avgTime: 0,
            successRate: 0
          };
        }

        const ts = toolStats[toolKey];
        ts.calls++;
        ts.totalTime += tool.executionTime || 0;
        ts.successes += tool.success ? 1 : 0;
        ts.failures += tool.success ? 0 : 1;
        ts.avgTime = ts.totalTime / ts.calls;
        ts.successRate = (ts.successes / ts.calls) * 100;

        // Server statistics
        if (tool.serverName) {
          if (!serverStats[tool.serverName]) {
            serverStats[tool.serverName] = { calls: 0, successes: 0, totalTime: 0 };
          }
          serverStats[tool.serverName].calls++;
          serverStats[tool.serverName].successes += tool.success ? 1 : 0;
          serverStats[tool.serverName].totalTime += tool.executionTime || 0;
        }

        // Tool type statistics
        if (!typeStats[tool.toolType]) {
          typeStats[tool.toolType] = { calls: 0, successes: 0, totalTime: 0 };
        }
        typeStats[tool.toolType].calls++;
        typeStats[tool.toolType].successes += tool.success ? 1 : 0;
        typeStats[tool.toolType].totalTime += tool.executionTime || 0;
      }
    }

    // Calculate overview metrics
    if (stats.overview.totalCalls > 0) {
      stats.overview.averageExecutionTime = totalExecutionTime / stats.overview.totalCalls;
      stats.overview.successRate = (totalSuccess / stats.overview.totalCalls) * 100;
    }

    // Sort and populate tool rankings
    const toolList = Object.values(toolStats);
    stats.tools.mostUsed = toolList
      .sort((a, b) => b.calls - a.calls)
      .slice(0, 10);

    stats.tools.fastest = toolList
      .filter(t => t.calls > 1)
      .sort((a, b) => a.avgTime - b.avgTime)
      .slice(0, 5);

    stats.tools.slowest = toolList
      .filter(t => t.calls > 1)
      .sort((a, b) => b.avgTime - a.avgTime)
      .slice(0, 5);

    stats.tools.mostReliable = toolList
      .filter(t => t.calls > 2)
      .sort((a, b) => b.successRate - a.successRate)
      .slice(0, 5);

    stats.tools.leastReliable = toolList
      .filter(t => t.calls > 2)
      .sort((a, b) => a.successRate - b.successRate)
      .slice(0, 5);

    // Server statistics
    for (const [server, data] of Object.entries(serverStats)) {
      stats.servers.usage[server] = data.calls;
      stats.servers.reliability[server] = (data.successes / data.calls) * 100;
    }

    // Tool type distribution
    for (const [type, data] of Object.entries(typeStats)) {
      stats.toolTypes.distribution[type] = data.calls;
      stats.toolTypes.performance[type] = {
        avgTime: data.totalTime / data.calls,
        successRate: (data.successes / data.calls) * 100
      };
    }

    // Recent activity
    stats.trends.recentActivity = allTools
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      .slice(0, 10)
      .map(tool => ({
        timestamp: new Date(tool.timestamp).toLocaleString(),
        tool: tool.serverName ? `${tool.serverName}::${tool.toolName}` : tool.toolName,
        success: tool.success ? '✅' : '❌',
        time: `${tool.executionTime || 0}ms`
      }));

    return stats;
  }

  getTimespan(sessions) {
    if (sessions.length === 0) return 'No data';
    if (sessions.length === 1) return 'Single session';

    const dates = sessions.map(s => new Date(s.startTime)).sort();
    const start = dates[0];
    const end = dates[dates.length - 1];
    const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24));

    return `${days} day${days !== 1 ? 's' : ''}`;
  }

  formatAsText(stats, detailed) {
    const lines = [];

    lines.push('🔧 TOOL USAGE ANALYTICS REPORT');
    lines.push('═'.repeat(50));
    lines.push('');

    // Overview
    lines.push('📊 OVERVIEW');
    lines.push(`Total Sessions: ${stats.overview.totalSessions}`);
    lines.push(`Total Tool Calls: ${stats.overview.totalCalls}`);
    lines.push(`Average Execution Time: ${stats.overview.averageExecutionTime.toFixed(1)}ms`);
    lines.push(`Success Rate: ${stats.overview.successRate.toFixed(1)}%`);
    lines.push(`Timespan: ${stats.overview.timespan}`);
    lines.push('');

    // Top tools
    lines.push('🏆 TOP TOOLS BY USAGE');
    stats.tools.mostUsed.slice(0, 5).forEach((tool, i) => {
      lines.push(`${i + 1}. ${tool.name} (${tool.calls} calls, ${tool.successRate.toFixed(1)}% success)`);
    });
    lines.push('');

    // Performance insights
    if (stats.tools.fastest.length > 0) {
      lines.push('⚡ FASTEST TOOLS');
      stats.tools.fastest.slice(0, 3).forEach((tool, i) => {
        lines.push(`${i + 1}. ${tool.name} (${tool.avgTime.toFixed(1)}ms avg)`);
      });
      lines.push('');
    }

    if (stats.tools.slowest.length > 0) {
      lines.push('🐌 SLOWEST TOOLS');
      stats.tools.slowest.slice(0, 3).forEach((tool, i) => {
        lines.push(`${i + 1}. ${tool.name} (${tool.avgTime.toFixed(1)}ms avg)`);
      });
      lines.push('');
    }

    // Server usage
    if (Object.keys(stats.servers.usage).length > 0) {
      lines.push('🖥️  SERVER USAGE');
      Object.entries(stats.servers.usage)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 5)
        .forEach(([server, calls]) => {
          const reliability = stats.servers.reliability[server];
          lines.push(`• ${server}: ${calls} calls (${reliability.toFixed(1)}% success)`);
        });
      lines.push('');
    }

    // Tool types
    if (Object.keys(stats.toolTypes.distribution).length > 0) {
      lines.push('📁 TOOL TYPE DISTRIBUTION');
      Object.entries(stats.toolTypes.distribution)
        .sort(([,a], [,b]) => b - a)
        .forEach(([type, calls]) => {
          const perf = stats.toolTypes.performance[type];
          lines.push(`• ${type}: ${calls} calls (${perf.avgTime.toFixed(1)}ms avg, ${perf.successRate.toFixed(1)}% success)`);
        });
      lines.push('');
    }

    // Recent activity
    if (stats.trends.recentActivity.length > 0) {
      lines.push('🕐 RECENT ACTIVITY');
      stats.trends.recentActivity.slice(0, 5).forEach(activity => {
        lines.push(`${activity.success} ${activity.tool} (${activity.time}) at ${activity.timestamp}`);
      });
      lines.push('');
    }

    if (detailed) {
      // Hourly distribution
      lines.push('📈 HOURLY DISTRIBUTION (24h)');
      const maxHourly = Math.max(...stats.trends.hourlyDistribution);
      if (maxHourly > 0) {
        for (let i = 0; i < 24; i++) {
          const count = stats.trends.hourlyDistribution[i];
          const bar = '█'.repeat(Math.round((count / maxHourly) * 20));
          lines.push(`${i.toString().padStart(2, '0')}:00 │${bar} ${count}`);
        }
      }
      lines.push('');
    }

    return lines.join('\n');
  }

  formatAsTable(stats, detailed) {
    // This would create a more structured table format
    // For now, return the text format
    return this.formatAsText(stats, detailed);
  }

  formatOutput(content, format) {
    switch (format) {
      case 'json':
        return JSON.stringify({ message: content }, null, 2);
      default:
        return content;
    }
  }

  /**
   * Get performance insights and recommendations
   */
  getInsights() {
    const data = this.loadData();
    if (!data) return 'No data available for insights';

    const stats = this.calculateStats(data, 'all');
    const insights = [];

    // Performance insights
    if (stats.overview.averageExecutionTime > 1000) {
      insights.push('⚠️  High average execution time detected. Consider optimizing frequently used tools.');
    }

    if (stats.overview.successRate < 90) {
      insights.push('⚠️  Low success rate detected. Check error logs for failing tools.');
    }

    // Usage patterns
    const totalCalls = stats.overview.totalCalls;
    const uniqueTools = stats.tools.mostUsed.length;

    if (uniqueTools > 0 && totalCalls / uniqueTools < 2) {
      insights.push('💡 Low tool reuse detected. Consider creating reusable workflows.');
    }

    // Server reliability
    const unreliableServers = Object.entries(stats.servers.reliability)
      .filter(([, rate]) => rate < 80);

    if (unreliableServers.length > 0) {
      insights.push(`⚠️  Unreliable servers detected: ${unreliableServers.map(([s]) => s).join(', ')}`);
    }

    // Peak usage times
    const maxHour = stats.trends.hourlyDistribution.indexOf(Math.max(...stats.trends.hourlyDistribution));
    insights.push(`📊 Peak usage time: ${maxHour}:00 - ${maxHour + 1}:00`);

    return insights.length > 0 ? insights.join('\n') : '✅ All metrics look healthy!';
  }
}

export default ToolAnalytics;