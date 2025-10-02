#!/usr/bin/env node

/**
 * Tool Statistics CLI
 * Command-line interface for viewing and managing tool usage analytics
 */

import { writeFileSync, existsSync } from 'fs';
import { resolve, dirname, join } from 'path';
import { fileURLToPath } from 'url';
import ToolAnalytics from '../tools/tool-analytics.js';
import { getToolStats } from '../tools/tool-tracker.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = resolve(__dirname, '../..');

class ToolStatsCLI {
  constructor() {
    this.analytics = new ToolAnalytics();
  }

  async run() {
    const args = process.argv.slice(2);
    const command = args[0] || 'help';

    try {
      switch (command) {
        case 'report':
        case 'r':
          await this.showReport(args.slice(1));
          break;
        case 'export':
        case 'e':
          await this.exportData(args.slice(1));
          break;
        case 'clear':
        case 'c':
          await this.clearData(args.slice(1));
          break;
        case 'live':
        case 'l':
          await this.liveMonitor(args.slice(1));
          break;
        case 'insights':
        case 'i':
          await this.showInsights();
          break;
        case 'status':
        case 's':
          await this.showStatus();
          break;
        case 'help':
        case 'h':
        default:
          this.showHelp();
          break;
      }
    } catch (error) {
      console.error('❌ Error:', error.message);
      process.exit(1);
    }
  }

  async showReport(args) {
    const options = this.parseOptions(args, {
      timeframe: 'session',
      detailed: false,
      format: 'text'
    });

    console.log(this.analytics.generateReport(options));
  }

  async exportData(args) {
    const options = this.parseOptions(args, {
      format: 'csv',
      output: null
    });

    const data = this.analytics.loadData();
    if (!data) {
      console.log('❌ No tracking data available to export');
      return;
    }

    let outputData;
    let filename;
    let extension;

    if (options.format === 'csv') {
      outputData = this.exportToCSV(data);
      extension = 'csv';
    } else {
      outputData = JSON.stringify(data, null, 2);
      extension = 'json';
    }

    if (options.output) {
      filename = options.output;
    } else {
      const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '').replace('T', '_');
      filename = `tool-usage-export-${timestamp}.${extension}`;
    }

    const fullPath = resolve(filename);
    writeFileSync(fullPath, outputData);
    console.log(`✅ Data exported to: ${fullPath}`);
    console.log(`📊 File size: ${Math.round(outputData.length / 1024)}KB`);
  }

  exportToCSV(data) {
    const headers = [
      'timestamp', 'session', 'toolName', 'serverName', 'toolType',
      'executionTime', 'success', 'parameterCount', 'resultSize', 'error'
    ];

    const rows = [headers.join(',')];

    for (const [sessionId, sessionData] of Object.entries(data.sessions)) {
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

  async clearData(args) {
    const options = this.parseOptions(args, {
      force: false,
      sessions: null
    });

    const dataFile = resolve(projectRoot, '.claude/analytics/tool-usage.json');

    if (!existsSync(dataFile)) {
      console.log('ℹ️  No tracking data to clear');
      return;
    }

    if (!options.force) {
      console.log('⚠️  This will permanently delete all tracking data.');
      console.log('   Use --force to confirm deletion');
      return;
    }

    if (options.sessions) {
      // Clear only old sessions
      const data = this.analytics.loadData();
      if (data) {
        const sessions = Object.entries(data.sessions)
          .sort(([,a], [,b]) => new Date(b.startTime) - new Date(a.startTime));

        const toKeep = parseInt(options.sessions);
        if (sessions.length > toKeep) {
          data.sessions = Object.fromEntries(sessions.slice(0, toKeep));
          writeFileSync(dataFile, JSON.stringify(data, null, 2));
          console.log(`✅ Cleared old sessions, kept ${toKeep} most recent`);
        } else {
          console.log(`ℹ️  Only ${sessions.length} sessions exist, nothing to clear`);
        }
      }
    } else {
      // Clear all data
      writeFileSync(dataFile, JSON.stringify({
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
      }, null, 2));
      console.log('✅ All tracking data cleared');
    }
  }

  async liveMonitor(args) {
    const options = this.parseOptions(args, {
      interval: 5000,
      count: 10
    });

    console.log('🔴 Live Tool Monitor (Ctrl+C to stop)');
    console.log('─'.repeat(60));

    let lastTotal = 0;
    let iterations = 0;

    const monitor = setInterval(() => {
      const stats = getToolStats({ timeframe: 'session' });

      if (stats.totalCalls > lastTotal) {
        const newCalls = stats.totalCalls - lastTotal;
        const latest = stats.recentActivity.slice(0, newCalls);

        latest.forEach(activity => {
          const timestamp = new Date().toLocaleTimeString();
          console.log(`[${timestamp}] ${activity.success} ${activity.tool} (${activity.time})`);
        });

        lastTotal = stats.totalCalls;
      }

      iterations++;
      if (options.count > 0 && iterations >= options.count) {
        clearInterval(monitor);
        console.log('\n🟢 Monitor stopped');
      }
    }, options.interval);

    // Handle Ctrl+C
    process.on('SIGINT', () => {
      clearInterval(monitor);
      console.log('\n🟢 Monitor stopped by user');
      process.exit(0);
    });
  }

  async showInsights() {
    console.log('🧠 TOOL USAGE INSIGHTS');
    console.log('═'.repeat(40));
    console.log(this.analytics.getInsights());
  }

  async showStatus() {
    const dataFile = resolve(projectRoot, '.claude/analytics/tool-usage.json');

    if (!existsSync(dataFile)) {
      console.log('📊 TRACKING STATUS: Not initialized');
      console.log('   Run any tool to start tracking');
      return;
    }

    const data = this.analytics.loadData();
    if (!data) {
      console.log('📊 TRACKING STATUS: Error reading data');
      return;
    }

    const sessionCount = Object.keys(data.sessions).length;
    const lastModified = data.lastModified ? new Date(data.lastModified).toLocaleString() : 'Unknown';

    console.log('📊 TRACKING STATUS');
    console.log('─'.repeat(30));
    console.log(`Total Calls: ${data.totalCalls || 0}`);
    console.log(`Sessions: ${sessionCount}`);
    console.log(`Last Updated: ${lastModified}`);
    console.log(`Data File: ${dataFile}`);

    if (sessionCount > 0) {
      const recentSession = Object.values(data.sessions)
        .sort((a, b) => new Date(b.startTime) - new Date(a.startTime))[0];
      console.log(`Current Session: ${recentSession.tools?.length || 0} calls`);
    }
  }

  parseOptions(args, defaults = {}) {
    const options = { ...defaults };

    for (let i = 0; i < args.length; i++) {
      const arg = args[i];

      if (arg.startsWith('--')) {
        const key = arg.slice(2);
        const value = args[i + 1];

        switch (key) {
          case 'timeframe':
          case 't':
            options.timeframe = value;
            i++;
            break;
          case 'detailed':
          case 'd':
            options.detailed = true;
            break;
          case 'format':
          case 'f':
            options.format = value;
            i++;
            break;
          case 'output':
          case 'o':
            options.output = value;
            i++;
            break;
          case 'force':
            options.force = true;
            break;
          case 'sessions':
            options.sessions = value;
            i++;
            break;
          case 'interval':
            options.interval = parseInt(value) || defaults.interval;
            i++;
            break;
          case 'count':
            options.count = parseInt(value) || defaults.count;
            i++;
            break;
        }
      }
    }

    return options;
  }

  showHelp() {
    console.log(`
🔧 Tool Statistics CLI

USAGE:
  node .claude/scripts/tool-stats.js <command> [options]

COMMANDS:
  report, r     Show usage analytics report
  export, e     Export tracking data
  clear, c      Clear tracking data
  live, l       Live monitor tool calls
  insights, i   Show usage insights and recommendations
  status, s     Show tracking system status
  help, h       Show this help message

OPTIONS:
  --timeframe, -t    Time period (session|today|week|month|all) [default: session]
  --detailed, -d     Include detailed breakdown
  --format, -f       Output format (text|json|csv) [default: text]
  --output, -o       Output filename for export
  --force            Force operation without confirmation
  --sessions         Keep N most recent sessions when clearing
  --interval         Live monitor interval in ms [default: 5000]
  --count            Number of iterations for live monitor [default: 10]

EXAMPLES:
  node .claude/scripts/tool-stats.js report --timeframe week --detailed
  node .claude/scripts/tool-stats.js export --format csv --output usage.csv
  node .claude/scripts/tool-stats.js clear --force --sessions 10
  node .claude/scripts/tool-stats.js live --interval 3000
  node .claude/scripts/tool-stats.js insights
`);
  }
}

// Run CLI if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const cli = new ToolStatsCLI();
  cli.run();
}

export default ToolStatsCLI;