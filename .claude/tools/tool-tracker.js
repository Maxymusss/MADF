/**
 * Tool Tracking Module
 * Centralized tracking for all tool calls including MCP tools, commands, hooks, and agents
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = resolve(__dirname, '../..');

class ToolTracker {
  constructor() {
    this.dataFile = resolve(projectRoot, '.claude/analytics/tool-usage.json');
    this.sessionId = this.generateSessionId();
    this.data = this.loadData();

    // Initialize session if not exists
    if (!this.data.sessions[this.sessionId]) {
      this.data.sessions[this.sessionId] = {
        startTime: new Date().toISOString(),
        tools: [],
        summary: {}
      };
    }
  }

  generateSessionId() {
    const now = new Date();
    return `session_${now.toISOString().slice(0, 19).replace(/[:-]/g, '').replace('T', '_')}`;
  }

  loadData() {
    if (!existsSync(this.dataFile)) {
      return {
        version: '1.0.0',
        created: new Date().toISOString(),
        totalCalls: 0,
        sessions: {},
        globalStats: {
          toolCounts: {},
          serverCounts: {},
          averageExecutionTimes: {},
          successRates: {}
        }
      };
    }

    try {
      return JSON.parse(readFileSync(this.dataFile, 'utf8'));
    } catch (error) {
      console.error('Error loading tool tracking data:', error.message);
      return this.loadData(); // Return fresh data structure
    }
  }

  saveData() {
    try {
      // Update last modified timestamp
      this.data.lastModified = new Date().toISOString();
      writeFileSync(this.dataFile, JSON.stringify(this.data, null, 2));
    } catch (error) {
      console.error('Error saving tool tracking data:', error.message);
    }
  }

  /**
   * Track a tool call
   * @param {Object} toolCall - Tool call information
   * @param {string} toolCall.toolName - Name of the tool
   * @param {string} toolCall.serverName - Name of the server (for MCP tools)
   * @param {string} toolCall.toolType - Type of tool ('mcp', 'agent', 'native', 'command', 'hook')
   * @param {Object} toolCall.parameters - Tool parameters
   * @param {number} toolCall.executionTime - Execution time in milliseconds
   * @param {boolean} toolCall.success - Whether the tool call succeeded
   * @param {string} toolCall.error - Error message if failed
   * @param {any} toolCall.result - Tool result (truncated for large results)
   */
  track(toolCall) {
    const timestamp = new Date().toISOString();
    const sessionData = this.data.sessions[this.sessionId];

    // Prepare tracking entry
    const trackingEntry = {
      timestamp,
      toolName: toolCall.toolName,
      serverName: toolCall.serverName || null,
      toolType: toolCall.toolType || 'unknown',
      executionTime: toolCall.executionTime || 0,
      success: toolCall.success !== false, // Default to true if not specified
      parametersHash: this.hashParameters(toolCall.parameters),
      parameterCount: toolCall.parameters ? Object.keys(toolCall.parameters).length : 0,
      resultSize: this.getResultSize(toolCall.result),
      error: toolCall.error || null
    };

    // Add to session
    sessionData.tools.push(trackingEntry);

    // Update session summary
    const toolKey = toolCall.serverName ? `${toolCall.serverName}__${toolCall.toolName}` : toolCall.toolName;
    sessionData.summary[toolKey] = (sessionData.summary[toolKey] || 0) + 1;

    // Update global stats
    this.updateGlobalStats(trackingEntry);

    // Increment total calls
    this.data.totalCalls++;

    // Save data asynchronously to avoid blocking
    process.nextTick(() => this.saveData());
  }

  hashParameters(params) {
    if (!params || typeof params !== 'object') return '';

    // Create a simple hash of parameter structure (not values for privacy)
    const keys = Object.keys(params).sort();
    return keys.join(',');
  }

  getResultSize(result) {
    if (!result) return 0;
    try {
      return JSON.stringify(result).length;
    } catch {
      return String(result).length;
    }
  }

  updateGlobalStats(entry) {
    const { toolName, serverName, executionTime, success } = entry;
    const toolKey = serverName ? `${serverName}__${toolName}` : toolName;

    // Update tool counts
    this.data.globalStats.toolCounts[toolKey] = (this.data.globalStats.toolCounts[toolKey] || 0) + 1;

    // Update server counts (for MCP tools)
    if (serverName) {
      this.data.globalStats.serverCounts[serverName] = (this.data.globalStats.serverCounts[serverName] || 0) + 1;
    }

    // Update execution times (rolling average)
    const currentAvg = this.data.globalStats.averageExecutionTimes[toolKey] || 0;
    const currentCount = this.data.globalStats.toolCounts[toolKey];
    this.data.globalStats.averageExecutionTimes[toolKey] =
      (currentAvg * (currentCount - 1) + executionTime) / currentCount;

    // Update success rates
    if (!this.data.globalStats.successRates[toolKey]) {
      this.data.globalStats.successRates[toolKey] = { total: 0, successful: 0 };
    }
    this.data.globalStats.successRates[toolKey].total++;
    if (success) {
      this.data.globalStats.successRates[toolKey].successful++;
    }
  }

  /**
   * Get usage statistics
   * @param {Object} options - Query options
   * @param {string} options.timeframe - 'session', 'today', 'week', 'month', 'all'
   * @param {string} options.toolType - Filter by tool type
   * @param {string} options.serverName - Filter by server name
   */
  getStats(options = {}) {
    const { timeframe = 'session', toolType, serverName } = options;

    let relevantSessions = [];
    const now = new Date();

    // Filter sessions based on timeframe
    for (const [sessionId, sessionData] of Object.entries(this.data.sessions)) {
      const sessionStart = new Date(sessionData.startTime);
      let include = false;

      switch (timeframe) {
        case 'session':
          include = sessionId === this.sessionId;
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
        relevantSessions.push(sessionData);
      }
    }

    // Aggregate statistics
    const stats = {
      timeframe,
      totalCalls: 0,
      toolCounts: {},
      serverCounts: {},
      toolTypeCounts: {},
      averageExecutionTime: 0,
      successRate: 0,
      topTools: [],
      recentActivity: [],
      sessions: relevantSessions.length
    };

    let totalExecutionTime = 0;
    let totalSuccess = 0;
    let allTools = [];

    for (const session of relevantSessions) {
      for (const tool of session.tools) {
        // Apply filters
        if (toolType && tool.toolType !== toolType) continue;
        if (serverName && tool.serverName !== serverName) continue;

        const toolKey = tool.serverName ? `${tool.serverName}__${tool.toolName}` : tool.toolName;

        // Update counts
        stats.totalCalls++;
        stats.toolCounts[toolKey] = (stats.toolCounts[toolKey] || 0) + 1;
        stats.toolTypeCounts[tool.toolType] = (stats.toolTypeCounts[tool.toolType] || 0) + 1;

        if (tool.serverName) {
          stats.serverCounts[tool.serverName] = (stats.serverCounts[tool.serverName] || 0) + 1;
        }

        totalExecutionTime += tool.executionTime || 0;
        if (tool.success) totalSuccess++;

        allTools.push(tool);
      }
    }

    // Calculate averages
    if (stats.totalCalls > 0) {
      stats.averageExecutionTime = totalExecutionTime / stats.totalCalls;
      stats.successRate = (totalSuccess / stats.totalCalls) * 100;
    }

    // Get top tools
    stats.topTools = Object.entries(stats.toolCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10)
      .map(([tool, count]) => ({ tool, count }));

    // Get recent activity (last 10 calls)
    stats.recentActivity = allTools
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      .slice(0, 10)
      .map(tool => ({
        timestamp: tool.timestamp,
        tool: tool.serverName ? `${tool.serverName}__${tool.toolName}` : tool.toolName,
        success: tool.success,
        executionTime: tool.executionTime
      }));

    return stats;
  }

  /**
   * Export data for analysis
   * @param {string} format - 'json' or 'csv'
   */
  export(format = 'json') {
    if (format === 'csv') {
      return this.exportCSV();
    }
    return this.data;
  }

  exportCSV() {
    const headers = [
      'timestamp', 'session', 'toolName', 'serverName', 'toolType',
      'executionTime', 'success', 'parameterCount', 'resultSize', 'error'
    ];

    const rows = [headers.join(',')];

    for (const [sessionId, sessionData] of Object.entries(this.data.sessions)) {
      for (const tool of sessionData.tools) {
        const row = [
          tool.timestamp,
          sessionId,
          tool.toolName,
          tool.serverName || '',
          tool.toolType,
          tool.executionTime || 0,
          tool.success,
          tool.parameterCount || 0,
          tool.resultSize || 0,
          tool.error || ''
        ];
        rows.push(row.map(field => `"${field}"`).join(','));
      }
    }

    return rows.join('\n');
  }

  /**
   * Clear old session data (keep last N sessions)
   * @param {number} keepCount - Number of recent sessions to keep
   */
  cleanup(keepCount = 50) {
    const sessions = Object.entries(this.data.sessions)
      .sort(([,a], [,b]) => new Date(b.startTime) - new Date(a.startTime));

    if (sessions.length <= keepCount) return;

    const toKeep = sessions.slice(0, keepCount);
    this.data.sessions = Object.fromEntries(toKeep);

    this.saveData();
    return sessions.length - keepCount; // Return number of sessions cleaned
  }
}

// Create singleton instance
const tracker = new ToolTracker();

export default tracker;

// Helper function for external use
export function trackTool(toolCall) {
  return tracker.track(toolCall);
}

export function getToolStats(options) {
  return tracker.getStats(options);
}