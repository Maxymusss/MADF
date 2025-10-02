# Claude+MCP+BMAD Integration Plan

## Overview
Create Claude+MCP-use native agents that are fully BMAD-compatible, enabling seamless use across Claude Code, MCP servers, and BMAD framework.

## Architecture Overview
- Create 5 enhanced agents in `.claude/agents/` that are Claude+MCP native but fully BMAD-compatible
- Keep 3 pure BMAD workflow agents unchanged in `.bmad-core/agents/`
- Use CLAUDE.md override mechanism to route agent calls appropriately

## Phase 1: Core Development Agents (Priority 1)

### 1. Enhanced Developer Agent (`.claude/agents/dev-agent.js`)
```javascript
// Core structure with Claude tools, MCP servers, and BMAD compatibility
- Claude Tools: Read, Write, Edit, MultiEdit, Bash, Task
- MCP Servers: filesystem, git, sequential-thinking
- BMAD Commands: *develop-story, *create, *help, *run-tests
- Can execute .bmad-core/tasks/ when in BMAD mode
```

### 2. Enhanced Architect Agent (`.claude/agents/architect-agent.js`)
```javascript
- Claude Tools: Read, Write, WebSearch, Task
- MCP Servers: filesystem, playwright (for arch testing), postgres (data modeling)
- BMAD Commands: *create-doc architecture, *review, *help
- Access to .bmad-core/templates/architecture templates
```

### 3. Enhanced QA Agent (`.claude/agents/qa-agent.js`)
```javascript
- Claude Tools: Read, Edit, Bash, Task
- MCP Servers: playwright (E2E testing), sentry (error tracking), filesystem
- BMAD Commands: *review-story, *qa-gate, *execute-checklist
- Can run .bmad-core/checklists/ validations
```

## Phase 2: Analysis Agents (Priority 2)

### 4. Enhanced Analyst Agent (`.claude/agents/analyst-agent.js`)
```javascript
- Claude Tools: WebSearch, Read, Write, Task
- MCP Servers: sequential-thinking, context7, web-search
- BMAD Commands: *document-project, *brainstorm, *research
- Access to brainstorming techniques and elicitation methods
```

### 5. Enhanced BMad Master (`.claude/agents/master-agent.js`)
```javascript
- Claude Tools: All available tools
- MCP Servers: All configured servers (dynamic loading)
- BMAD Commands: All bmad-master commands
- Universal task executor with full framework access
```

## File Structure After Implementation

```
.claude/
├── agents/
│   ├── dev-agent.js        # Enhanced developer
│   ├── architect-agent.js  # Enhanced architect
│   ├── qa-agent.js         # Enhanced QA
│   ├── analyst-agent.js    # Enhanced analyst
│   └── master-agent.js     # Enhanced bmad-master
├── agents/lib/
│   ├── bmad-compat.js     # BMAD compatibility layer
│   ├── mcp-client.js      # MCP-use integration
│   └── agent-base.js      # Base agent class
└── agents/config/
    └── mcp-servers.json    # MCP server configurations

.bmad-core/agents/  # Keep unchanged
├── po.md           # Pure BMAD workflow agent
├── sm.md           # Pure BMAD workflow agent
└── bmad-orchestrator.md  # Pure BMAD workflow agent
```

## CLAUDE.md Override Configuration

Add to CLAUDE.md after testing:

```markdown
## Agent Resolution System

### Agent Loading Priority (ACTIVATED AFTER TESTING)
When an agent is called (e.g., /dev, @architect):

1. **Check Enhanced Agents First** (`.claude/agents/`)
   - If `{agent-name}-agent.js` exists → Load Claude+MCP enhanced version
   - These agents have full Claude tools + MCP servers + BMAD compatibility

2. **Fallback to BMAD Agents** (`.bmad-core/agents/`)
   - If no enhanced version → Load original BMAD agent
   - Maintains compatibility with pure BMAD workflow agents (po, sm, bmad-orchestrator)

### Enhanced Agent Capabilities
Enhanced agents in `.claude/agents/` provide:
- Native Claude tool integration (Read, Write, Edit, etc.)
- MCP server access via mcp-use library
- Full BMAD task/template/checklist compatibility
- Can be used standalone OR within BMAD framework

### BMAD Command Compatibility
Enhanced agents recognize BMAD commands:
- Commands starting with `*` trigger BMAD compatibility mode
- Loads resources from `.bmad-core/` directories
- Maintains BMAD workflow integrity

### MCP Server Integration
Enhanced agents use `.claude/agents/config/mcp-servers.json`:
- Dynamic server loading based on agent needs
- Shared configuration across all enhanced agents
- Easy to add new MCP servers globally
```

## Implementation Steps

### Step 1: Create Base Infrastructure
1. Create `.claude/agents/lib/agent-base.js` - shared functionality
2. Create `.claude/agents/lib/bmad-compat.js` - BMAD compatibility layer
3. Create `.claude/agents/lib/mcp-client.js` - MCP-use wrapper
4. Create `.claude/agents/config/mcp-servers.json` - server configs

### Step 2: Implement Enhanced Agents
1. Start with `dev-agent.js` (most critical)
2. Test Claude tools + MCP + BMAD commands
3. Implement remaining 4 agents incrementally
4. Each agent extends base class for consistency

### Step 3: Testing Protocol
1. Test enhanced agent standalone (Claude tools only)
2. Test MCP server integration
3. Test BMAD command compatibility
4. Test task/template loading from .bmad-core
5. Verify no interference with pure BMAD agents

### Step 4: Activate Override in CLAUDE.md
1. Add override logic to CLAUDE.md (shown above)
2. System now checks .claude/agents/ first
3. Falls back to .bmad-core/agents/ when needed
4. Document the migration for team

## Testing Checklist
- [ ] Enhanced dev can execute BMAD story development
- [ ] Enhanced architect can create architecture docs
- [ ] Enhanced QA can run review workflows
- [ ] Enhanced analyst can document projects
- [ ] Enhanced master can execute any BMAD task
- [ ] Pure BMAD agents (po, sm, orchestrator) work unchanged
- [ ] MCP servers connect and function properly
- [ ] Claude native tools work in all enhanced agents

## Agent Compatibility Matrix

### Enhanced Agents (Claude+MCP+BMAD)
| Agent | Location | Claude Tools | MCP Servers | BMAD Compatible | Use Cases |
|-------|----------|--------------|-------------|-----------------|-----------|
| dev | `.claude/agents/dev-agent.js` | ✅ | ✅ | ✅ | General development, debugging, BMAD stories |
| architect | `.claude/agents/architect-agent.js` | ✅ | ✅ | ✅ | System design, architecture docs |
| qa | `.claude/agents/qa-agent.js` | ✅ | ✅ | ✅ | Testing, code review, quality gates |
| analyst | `.claude/agents/analyst-agent.js` | ✅ | ✅ | ✅ | Research, analysis, documentation |
| master | `.claude/agents/master-agent.js` | ✅ | ✅ | ✅ | Universal tasks, admin operations |

### Pure BMAD Agents (Unchanged)
| Agent | Location | Claude Tools | MCP Servers | BMAD Native | Use Cases |
|-------|----------|--------------|-------------|-------------|-----------|
| po | `.bmad-core/agents/po.md` | ❌ | ❌ | ✅ | Product owner tasks, backlog management |
| sm | `.bmad-core/agents/sm.md` | ❌ | ❌ | ✅ | Scrum master, story creation |
| bmad-orchestrator | `.bmad-core/agents/bmad-orchestrator.md` | ❌ | ❌ | ✅ | BMAD workflow orchestration |

## Benefits of This Approach
1. **No Breaking Changes**: BMAD framework continues working
2. **Progressive Enhancement**: Add capabilities without losing existing functionality
3. **Clean Separation**: Enhanced agents isolated in .claude/
4. **Easy Rollback**: Can disable override in CLAUDE.md if issues arise
5. **Unified Experience**: Same agents work everywhere with more power
6. **Claude+MCP Native**: Optimized for Claude Code with full MCP-use integration

## Example Enhanced Agent Structure

```javascript
// .claude/agents/dev-agent.js
import { MCPClient } from 'mcp-use';
import { AgentBase } from './lib/agent-base.js';
import { BMADCompat } from './lib/bmad-compat.js';

export class DevAgent extends AgentBase {
  constructor() {
    super({
      name: "Enhanced Developer",
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
    this.mcpClient = MCPClient.fromDict(this.mcpServers);
    await this.bmadCompat.loadCoreConfig();
  }

  async execute(command, args) {
    // Handle BMAD commands
    if (command.startsWith('*')) {
      return this.bmadCompat.execute(command, args);
    }

    // Handle Claude/MCP tools
    return this.executeTool(command, args);
  }
}
```

## Timeline
- **Week 1**: Implement Phase 1 agents (dev, architect, qa)
- **Week 2**: Implement Phase 2 agents (analyst, master)
- **Week 3**: Testing and refinement
- **Week 4**: Activate CLAUDE.md override and document

## Success Criteria
- All enhanced agents work with Claude native tools
- MCP-use integration provides access to any MCP server
- BMAD commands and workflows function correctly
- No disruption to existing BMAD framework
- Improved developer experience with unified agents


## Critic on Plan

### Strengths of the Plan

**Progressive Enhancement Strategy**

You keep .bmad-core/agents/ untouched while building enhanced Claude+MCP-native versions in .claude/agents/. This matches Claude Code's guidance on subagents and CLAUDE.md overrides — minimal risk of breaking legacy workflows.

**MCP Integration Design**

Using .claude/agents/config/mcp-servers.json for server configs is consistent with both Claude Code's MCP config system and mcp-use's fromConfigFile method. The plan's dynamic server loading idea is supported by MCPClient.fromDict and MCPAgent multi-server features.

**Clear Separation of Concerns**

- agent-base.js → shared logic
- bmad-compat.js → BMAD command mapping
- mcp-client.js → unified MCP client

This separation aligns well with Claude Code SDK best practices on modular subagent design.

**Fallback Mechanism in CLAUDE.md**

Override system prioritizing enhanced agents, with graceful fallback to BMAD-native ones, ensures easy rollback and minimal disruption.

**Testing & Compatibility Matrix**

Explicit stepwise testing (Claude tools → MCP integration → BMAD tasks) is pragmatic and reduces debugging complexity.

### ⚠️ Potential Gaps / Risks

**MCP Client Lifecycle**

In your dev-agent.js example, you create this.mcpClient = MCPClient.fromDict(...) but don't handle session cleanup. According to mcp-use docs, you should call await client.closeAllSessions() after tasks, or risk dangling processes.

**Permission & Security Model**

Claude Code SDK enforces tool permission rules (acceptEdits, bypassPermissions, hooks). Your plan doesn't mention permission handling — enhanced agents may expose unsafe tools (filesystem, bash) without safeguards.

**BMAD Compatibility Layer Detail**

You've defined a mapping (*develop-story, *create, etc.) but not clarified:
- How errors are surfaced back to BMAD orchestrator
- Whether enhanced agents support BMAD's orchestrator chaining (e.g., po → sm → dev flows)

This could break complex BMAD workflows unless tested carefully.

**Agent Resolution Edge Cases**

In CLAUDE.md overrides, if both enhanced and BMAD versions exist, you always prefer enhanced. Some teams may still want opt-in control (e.g., force "pure BMAD dev agent"). You may want a manual flag or slash command to bypass enhancement.

**Streaming / Observability**

mcp-use supports stream() and streamEvents() for step-wise or token-wise streaming. Your plan assumes run() style execution only. For debugging or UI integration, you should extend agents to support streaming.

### 🔧 Suggested Improvements

**Add Session Lifecycle Management**

```javascript
async shutdown() {
  if (this.mcpClient) {
    await this.mcpClient.closeAllSessions();
  }
}
```

Ensure agents clean up on exit.

**Permission Rules Integration**

Add a permissions.json under .claude/agents/config/ mapping allowed/disallowed tools. Hook into Claude Code's canUseTool and BMADCompat layer to enforce safety.

**BMAD Orchestrator Compatibility**

Ensure bmad-compat.js allows chaining (e.g., one agent can hand off tasks to another in .bmad-core/agents/). Consider extending with hook-based delegation (BMAD command → redirect to another enhanced agent).

**Override Flexibility**

Extend CLAUDE.md config to support flags like:
```yaml
enhanced_agents: true   # default
fallback_only: true     # force BMAD originals
```

This matches Claude Code's philosophy of configurable subagent management.

**Streaming Support**

Modify execute(command, args) to support:
```javascript
if (args.stream) return this.mcpClient.stream(command, args);
```

This enables real-time debugging and UI integration (aligns with streamEventsToAISDK flow).

### ✅ Overall Assessment

Solid foundation — your architecture is consistent with Claude Code's subagent model and mcp-use's client library. Main missing pieces are around session lifecycle, permissions/security, and BMAD orchestration edge cases. If those are handled, this will give you a powerful, unified Claude+MCP+BMAD ecosystem with minimal disruption.