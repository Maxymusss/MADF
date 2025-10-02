# Claude+MCP+BMAD Integration Plan v2

## Overview
Create Claude+MCP-use native agents that are fully BMAD-compatible, enabling seamless use across Claude Code, MCP servers, and BMAD framework.

**v2 Improvements**: Addresses critique concerns around lifecycle management, permissions, BMAD orchestration, and streaming capabilities.

## Architecture Overview
- Create 5 enhanced agents in `.claude/agents/` that are Claude+MCP native but fully BMAD-compatible
- Keep 3 pure BMAD workflow agents unchanged in `.bmad-core/agents/`
- Use CLAUDE.md override mechanism to route agent calls appropriately
- **NEW**: Comprehensive lifecycle management and permission system
- **NEW**: Enhanced BMAD orchestrator compatibility with error handling

## Enhanced Agent Base Architecture

### Core AgentBase Class with Lifecycle Management
```javascript
// .claude/agents/lib/agent-base.js
import { MCPClient } from 'mcp-use';

export class AgentBase {
  constructor(config) {
    this.config = config;
    this.mcpClient = null;
    this.permissions = null;
    this.shutdownHandlers = [];
  }

  async initialize() {
    // Load permissions first
    this.permissions = await this.loadPermissions();

    // Initialize MCP client with lifecycle management
    this.mcpClient = MCPClient.fromDict(this.mcpServers);

    // Setup graceful shutdown handlers
    this.setupShutdownHandlers();
  }

  setupShutdownHandlers() {
    const shutdown = () => this.shutdown();
    process.on('SIGINT', shutdown);
    process.on('SIGTERM', shutdown);
    process.on('exit', shutdown);

    // Track handlers for cleanup
    this.shutdownHandlers = [
      { event: 'SIGINT', handler: shutdown },
      { event: 'SIGTERM', handler: shutdown },
      { event: 'exit', handler: shutdown }
    ];
  }

  async shutdown() {
    if (this.mcpClient) {
      // CRITICAL: Prevent resource leaks
      await this.mcpClient.closeAllSessions();
      this.mcpClient = null;
    }

    // Remove event listeners
    this.shutdownHandlers.forEach(({ event, handler }) => {
      process.removeListener(event, handler);
    });
  }

  async execute(command, args, options = {}) {
    // Permission validation
    if (!await this.permissions.canExecute(command, args)) {
      throw new Error(`Permission denied for command: ${command}`);
    }

    // Handle streaming if requested
    if (options.stream) {
      return this.mcpClient.stream(command, args, {
        onProgress: options.onProgress,
        onError: options.onError
      });
    }

    if (options.streamEvents) {
      return this.mcpClient.streamEvents(command, args);
    }

    // BMAD command routing
    if (command.startsWith('*')) {
      return this.bmadCompat.execute(command, args);
    }

    // Standard tool execution
    return this.mcpClient.run(command, args);
  }

  async loadPermissions() {
    const permissionPath = `.claude/agents/config/permissions.json`;
    const permissions = await import(permissionPath);
    return new PermissionManager(permissions[this.config.name]);
  }
}
```

## Permission & Security System

### Role-Based Permission Configuration
```json
// .claude/agents/config/permissions.json
{
  "dev-agent": {
    "allowedTools": ["Read", "Write", "Edit", "MultiEdit", "Bash", "Task"],
    "allowedMCPServers": ["filesystem", "git", "sequential-thinking"],
    "restrictedPaths": ["/etc", "/usr", "~/.ssh", "~/.aws"],
    "requireConfirmation": ["rm", "delete", "DROP", "truncate"],
    "maxFileSize": "10MB",
    "allowNetworkAccess": true
  },
  "architect-agent": {
    "allowedTools": ["Read", "Write", "WebSearch", "Task"],
    "allowedMCPServers": ["filesystem", "playwright", "postgres"],
    "restrictedPaths": ["/etc", "/usr"],
    "requireConfirmation": ["DROP", "ALTER TABLE"],
    "maxFileSize": "5MB",
    "allowNetworkAccess": true
  },
  "qa-agent": {
    "allowedTools": ["Read", "Edit", "Bash", "Task"],
    "allowedMCPServers": ["playwright", "sentry", "filesystem"],
    "restrictedPaths": ["/etc", "/usr", "~/.ssh"],
    "requireConfirmation": ["rm", "delete"],
    "maxFileSize": "5MB",
    "allowNetworkAccess": false
  },
  "analyst-agent": {
    "allowedTools": ["Read", "WebSearch", "Task"],
    "allowedMCPServers": ["sequential-thinking", "context7", "web-search"],
    "blockedTools": ["Bash", "Edit", "Write"],
    "readOnlyMode": true,
    "maxFileSize": "2MB",
    "allowNetworkAccess": true
  },
  "master-agent": {
    "allowedTools": ["*"],
    "allowedMCPServers": ["*"],
    "requireConfirmation": ["rm", "delete", "DROP", "shutdown", "reboot"],
    "maxFileSize": "50MB",
    "allowNetworkAccess": true,
    "adminMode": true
  }
}
```

### Permission Manager Implementation
```javascript
// .claude/agents/lib/permission-manager.js
export class PermissionManager {
  constructor(config) {
    this.config = config;
  }

  async canExecute(command, args = {}) {
    // Check allowed tools
    if (!this.isToolAllowed(command)) {
      return false;
    }

    // Check path restrictions
    if (args.path && !this.isPathAllowed(args.path)) {
      return false;
    }

    // Check confirmation requirements
    if (this.requiresConfirmation(command)) {
      return await this.getConfirmation(command, args);
    }

    return true;
  }

  isToolAllowed(tool) {
    if (this.config.allowedTools?.includes('*')) return true;
    if (this.config.allowedTools?.includes(tool)) return true;
    if (this.config.blockedTools?.includes(tool)) return false;
    return !this.config.readOnlyMode || this.isReadOnlyTool(tool);
  }

  isPathAllowed(path) {
    return !this.config.restrictedPaths?.some(restricted =>
      path.startsWith(restricted)
    );
  }

  requiresConfirmation(command) {
    return this.config.requireConfirmation?.some(pattern =>
      command.includes(pattern)
    );
  }

  async getConfirmation(command, args) {
    // Implementation depends on environment (CLI, UI, etc.)
    console.warn(`Dangerous operation: ${command}`);
    return true; // Simplified for now
  }
}
```

## Enhanced BMAD Compatibility Layer

### Orchestrator-Compatible BMAD Integration
```javascript
// .claude/agents/lib/bmad-compat.js
import { EventEmitter } from 'events';

export class BMADCompat extends EventEmitter {
  constructor(config) {
    super();
    this.agentId = config.agentId;
    this.tasksPath = config.tasksPath;
    this.templatesPath = config.templatesPath;
    this.commands = config.commands;
    this.orchestrator = null;
  }

  async initialize() {
    // Connect to BMAD orchestrator if available
    this.orchestrator = await this.connectToBMADOrchestrator();
  }

  async execute(command, args) {
    try {
      // Emit start event for orchestrator
      this.emit('task:start', { agent: this.agentId, command, args });

      const result = await this.executeCommand(command, args);

      // Handle orchestrator chaining (po → sm → dev flows)
      if (result.chainNext) {
        const chainResult = await this.delegateToAgent(
          result.chainNext.agent,
          result.chainNext.command,
          result.chainNext.args
        );
        result.chainResult = chainResult;
      }

      // Emit success event
      this.emit('task:success', { agent: this.agentId, command, result });

      return result;
    } catch (error) {
      // Enhanced error reporting to BMAD orchestrator
      const errorReport = {
        agent: this.agentId,
        command,
        args,
        error: {
          message: error.message,
          stack: error.stack,
          recoverable: this.isRecoverableError(error),
          retryable: this.isRetryableError(error),
          timestamp: new Date().toISOString()
        }
      };

      // Surface errors back to BMAD orchestrator
      await this.reportToBMADOrchestrator(errorReport);

      // Emit error event
      this.emit('task:error', errorReport);

      throw error;
    }
  }

  async executeCommand(command, args) {
    const handler = this.commands[command];
    if (!handler) {
      throw new Error(`Unknown BMAD command: ${command}`);
    }

    return handler(args);
  }

  async delegateToAgent(targetAgent, command, args = {}) {
    // Support BMAD's orchestrator chaining
    if (this.orchestrator) {
      return this.orchestrator.executeChain(targetAgent, command, args);
    }

    // Fallback: direct agent invocation
    const agent = await this.loadAgent(targetAgent);
    return agent.execute(command, args);
  }

  async reportToBMADOrchestrator(errorReport) {
    if (this.orchestrator) {
      await this.orchestrator.reportError(errorReport);
    }

    // Log to BMAD error tracking
    await this.logToBMADErrorSystem(errorReport);
  }

  async connectToBMADOrchestrator() {
    try {
      const { BMADOrchestrator } = await import('.bmad-core/orchestrator.js');
      return new BMADOrchestrator();
    } catch (error) {
      console.warn('BMAD orchestrator not available, running in standalone mode');
      return null;
    }
  }

  isRecoverableError(error) {
    // Define which errors can be recovered from
    const recoverableTypes = ['NetworkError', 'TemporaryFileError', 'RateLimitError'];
    return recoverableTypes.some(type => error.name === type);
  }

  isRetryableError(error) {
    // Define which errors should trigger automatic retries
    const retryableTypes = ['TimeoutError', 'ConnectionError', 'RateLimitError'];
    return retryableTypes.some(type => error.name === type);
  }
}
```

## Phase 1: Core Development Agents (Priority 1)

### 1. Enhanced Developer Agent
```javascript
// .claude/agents/dev-agent.js
import { AgentBase } from './lib/agent-base.js';
import { BMADCompat } from './lib/bmad-compat.js';

export class DevAgent extends AgentBase {
  constructor() {
    super({
      name: "dev-agent",
      claudeTools: ["Read", "Write", "Edit", "MultiEdit", "Bash", "Task"],
      mcpServers: {
        filesystem: { command: 'npx', args: ['@modelcontextprotocol/server-filesystem'] },
        git: { command: 'npx', args: ['@modelcontextprotocol/server-git'] },
        'sequential-thinking': { command: 'npx', args: ['@modelcontextprotocol/server-sequential-thinking'] }
      }
    });

    this.bmadCompat = new BMADCompat({
      agentId: 'dev',
      tasksPath: '.bmad-core/tasks/',
      templatesPath: '.bmad-core/templates/',
      commands: {
        '*develop-story': this.developStory.bind(this),
        '*create': this.createNextStory.bind(this),
        '*help': this.showHelp.bind(this),
        '*run-tests': this.runTests.bind(this)
      }
    });
  }

  async initialize() {
    await super.initialize();
    await this.bmadCompat.initialize();
  }

  async shutdown() {
    await this.bmadCompat.shutdown?.();
    await super.shutdown();
  }

  // BMAD command implementations
  async developStory(args) {
    // Enhanced story development with Claude tools + MCP servers
    const story = await this.loadStoryFromBMAD(args.storyId);
    const result = await this.implementStory(story);
    return { success: true, story: result };
  }

  async createNextStory(args) {
    // Create new story using BMAD templates
    const template = await this.loadBMADTemplate('story');
    const story = await this.generateStoryFromTemplate(template, args);
    return { success: true, story };
  }

  async runTests(args) {
    // Run tests with enhanced error reporting
    const testResult = await this.execute('Bash', { command: 'npm test' });
    if (!testResult.success) {
      // Enhanced error analysis using sequential-thinking MCP
      const analysis = await this.analyzeTestFailures(testResult.errors);
      return { success: false, errors: testResult.errors, analysis };
    }
    return { success: true, testResult };
  }
}
```

### 2. Enhanced Architect Agent
```javascript
// .claude/agents/architect-agent.js
export class ArchitectAgent extends AgentBase {
  constructor() {
    super({
      name: "architect-agent",
      claudeTools: ["Read", "Write", "WebSearch", "Task"],
      mcpServers: {
        filesystem: { command: 'npx', args: ['@modelcontextprotocol/server-filesystem'] },
        playwright: { command: 'npx', args: ['@modelcontextprotocol/server-playwright'] },
        postgres: { command: 'npx', args: ['@modelcontextprotocol/server-postgres'] }
      }
    });

    this.bmadCompat = new BMADCompat({
      agentId: 'architect',
      commands: {
        '*create-doc': this.createArchitectureDoc.bind(this),
        '*review': this.reviewArchitecture.bind(this),
        '*help': this.showHelp.bind(this)
      }
    });
  }
}
```

### 3. Enhanced QA Agent
```javascript
// .claude/agents/qa-agent.js
export class QAAgent extends AgentBase {
  constructor() {
    super({
      name: "qa-agent",
      claudeTools: ["Read", "Edit", "Bash", "Task"],
      mcpServers: {
        playwright: { command: 'npx', args: ['@modelcontextprotocol/server-playwright'] },
        sentry: { command: 'npx', args: ['@modelcontextprotocol/server-sentry'] },
        filesystem: { command: 'npx', args: ['@modelcontextprotocol/server-filesystem'] }
      }
    });

    this.bmadCompat = new BMADCompat({
      agentId: 'qa',
      commands: {
        '*review-story': this.reviewStory.bind(this),
        '*qa-gate': this.runQAGate.bind(this),
        '*execute-checklist': this.executeChecklist.bind(this)
      }
    });
  }
}
```

## Phase 2: Analysis Agents (Priority 2)

### 4. Enhanced Analyst Agent
```javascript
// .claude/agents/analyst-agent.js
export class AnalystAgent extends AgentBase {
  constructor() {
    super({
      name: "analyst-agent",
      claudeTools: ["WebSearch", "Read", "Write", "Task"],
      mcpServers: {
        'sequential-thinking': { command: 'npx', args: ['@modelcontextprotocol/server-sequential-thinking'] },
        context7: { command: 'npx', args: ['@modelcontextprotocol/server-context7'] },
        'web-search': { command: 'npx', args: ['@modelcontextprotocol/server-web-search'] }
      }
    });

    this.bmadCompat = new BMADCompat({
      agentId: 'analyst',
      commands: {
        '*document-project': this.documentProject.bind(this),
        '*brainstorm': this.brainstorm.bind(this),
        '*research': this.research.bind(this)
      }
    });
  }
}
```

### 5. Enhanced BMad Master
```javascript
// .claude/agents/master-agent.js
export class MasterAgent extends AgentBase {
  constructor() {
    super({
      name: "master-agent",
      claudeTools: ["*"], // All available tools
      mcpServers: {}, // Dynamic loading based on task requirements
      dynamicMCPLoading: true
    });

    this.bmadCompat = new BMADCompat({
      agentId: 'master',
      commands: {
        '*execute': this.executeAnyTask.bind(this),
        '*delegate': this.delegateToAgent.bind(this),
        '*orchestrate': this.orchestrateWorkflow.bind(this)
      }
    });
  }

  async loadMCPServersForTask(task) {
    // Dynamic MCP server loading based on task requirements
    const requiredServers = this.analyzeMCPRequirements(task);
    for (const server of requiredServers) {
      await this.mcpClient.addServer(server);
    }
  }
}
```

## Simple Override System

### Environment Variable Controls
```bash
# Simple override system (not complex configuration)
MADF_FORCE_PURE_BMAD=true    # Forces use of .bmad-core agents only
MADF_ENHANCED_AGENTS=false   # Disables .claude/agents entirely
MADF_DEBUG_AGENTS=true       # Enables agent debugging/streaming
```

### CLAUDE.md Override Logic
```markdown
## Agent Resolution System

### Agent Loading Priority
When an agent is called (e.g., /dev, @architect):

1. **Check Environment Overrides First**
   - If `MADF_FORCE_PURE_BMAD=true` → Skip to step 3
   - If `MADF_ENHANCED_AGENTS=false` → Skip to step 3

2. **Check Enhanced Agents** (`.claude/agents/`)
   - If `{agent-name}-agent.js` exists → Load Claude+MCP enhanced version
   - These agents have full Claude tools + MCP servers + BMAD compatibility

3. **Fallback to BMAD Agents** (`.bmad-core/agents/`)
   - Load original BMAD agent
   - Maintains compatibility with pure BMAD workflow agents

### Enhanced Agent Capabilities
Enhanced agents provide:
- Native Claude tool integration with lifecycle management
- MCP server access with session cleanup
- Permission-based security controls
- Full BMAD task/template/checklist compatibility
- Optional streaming support for debugging
- Error reporting to BMAD orchestrator
```

## File Structure After Implementation

```
.claude/
├── agents/
│   ├── dev-agent.js         # Enhanced developer with lifecycle mgmt
│   ├── architect-agent.js   # Enhanced architect with permissions
│   ├── qa-agent.js          # Enhanced QA with streaming support
│   ├── analyst-agent.js     # Enhanced analyst with error handling
│   └── master-agent.js      # Enhanced bmad-master with orchestration
├── agents/lib/
│   ├── agent-base.js        # Base class with lifecycle management
│   ├── bmad-compat.js       # Enhanced BMAD compatibility layer
│   ├── permission-manager.js # Permission system
│   └── mcp-client.js        # MCP-use integration wrapper
└── agents/config/
    ├── permissions.json     # Role-based permission configurations
    └── mcp-servers.json     # MCP server configurations

.bmad-core/agents/  # Keep unchanged
├── po.md           # Pure BMAD workflow agent
├── sm.md           # Pure BMAD workflow agent
└── bmad-orchestrator.md  # Pure BMAD workflow agent
```

## Implementation Steps

### Step 1: Enhanced Base Infrastructure
1. Create `AgentBase` with comprehensive lifecycle management
2. Implement `PermissionManager` with role-based controls
3. Enhance `BMADCompat` with orchestrator integration
4. Create MCP client wrapper with session management

### Step 2: Enhanced Agent Implementation
1. Start with `dev-agent.js` (most critical for development)
2. Test lifecycle management, permissions, and BMAD compatibility
3. Implement remaining 4 agents incrementally
4. Add streaming support as optional enhancement

### Step 3: Enhanced Testing Protocol
1. Test agent lifecycle (initialize → execute → shutdown)
2. Verify permission system prevents unauthorized operations
3. Test BMAD orchestrator chaining and error handling
4. Validate streaming capabilities for debugging
5. Ensure no interference with pure BMAD agents

### Step 4: Activate Enhanced Override in CLAUDE.md
1. Add environment variable override logic
2. Implement enhanced agent resolution system
3. Test rollback capabilities
4. Document migration for team

## Enhanced Testing Checklist
- [ ] **Lifecycle Management**: Agents properly initialize and cleanup MCP sessions
- [ ] **Permission System**: Role-based controls prevent unauthorized operations
- [ ] **BMAD Orchestration**: Enhanced dev can execute BMAD story development with error handling
- [ ] **Agent Chaining**: Orchestrator chaining (po → sm → dev) works with enhanced agents
- [ ] **Error Reporting**: Errors surface correctly to BMAD orchestrator
- [ ] **Streaming Support**: Debug streaming works for complex operations
- [ ] **Enhanced Architect**: Can create architecture docs with MCP integration
- [ ] **Enhanced QA**: Can run review workflows with Playwright/Sentry
- [ ] **Enhanced Analyst**: Can document projects with sequential thinking
- [ ] **Enhanced Master**: Can execute any BMAD task with dynamic MCP loading
- [ ] **Pure BMAD Compatibility**: Original agents (po, sm, orchestrator) work unchanged
- [ ] **Override System**: Environment variables correctly control agent selection
- [ ] **Rollback**: Can disable enhanced agents and fallback to pure BMAD

## Agent Compatibility Matrix

### Enhanced Agents (Claude+MCP+BMAD)
| Agent | Location | Claude Tools | MCP Servers | BMAD Compatible | Lifecycle Mgmt | Permissions | Streaming |
|-------|----------|--------------|-------------|-----------------|----------------|-------------|-----------|
| dev | `.claude/agents/dev-agent.js` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| architect | `.claude/agents/architect-agent.js` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| qa | `.claude/agents/qa-agent.js` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| analyst | `.claude/agents/analyst-agent.js` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| master | `.claude/agents/master-agent.js` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### Pure BMAD Agents (Unchanged)
| Agent | Location | Claude Tools | MCP Servers | BMAD Native | Legacy Support |
|-------|----------|--------------|-------------|-------------|----------------|
| po | `.bmad-core/agents/po.md` | ❌ | ❌ | ✅ | ✅ |
| sm | `.bmad-core/agents/sm.md` | ❌ | ❌ | ✅ | ✅ |
| bmad-orchestrator | `.bmad-core/agents/bmad-orchestrator.md` | ❌ | ❌ | ✅ | ✅ |

## Benefits of Enhanced v2 Approach
1. **No Breaking Changes**: BMAD framework continues working unchanged
2. **Production-Ready**: Proper lifecycle management prevents resource leaks
3. **Security-First**: Permission system prevents unauthorized operations
4. **Orchestrator Compatible**: Enhanced error handling and agent chaining
5. **Debug-Ready**: Optional streaming support for complex operations
6. **Simple Rollback**: Environment variables provide easy fallback
7. **Progressive Enhancement**: Add capabilities without losing existing functionality
8. **Claude+MCP Native**: Optimized for Claude Code with full MCP-use integration

## Timeline
- **Week 1**: Implement enhanced base infrastructure and dev agent
- **Week 2**: Implement remaining enhanced agents with full feature set
- **Week 3**: Comprehensive testing and orchestrator integration
- **Week 4**: Activate CLAUDE.md override and production deployment

## Success Criteria
- ✅ All enhanced agents work with Claude native tools and proper lifecycle management
- ✅ Permission system enforces security boundaries without breaking workflows
- ✅ MCP session lifecycle prevents resource leaks and dangling processes
- ✅ BMAD orchestrator chaining and error reporting work seamlessly
- ✅ Streaming support enables real-time debugging and UI integration
- ✅ Environment variable overrides provide simple rollback mechanism
- ✅ No disruption to existing BMAD framework or pure workflow agents
- ✅ Enhanced developer experience with unified, production-ready agents