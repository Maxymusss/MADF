# Global CLAUDE.md Best Practices Guide

## Overview

A well-structured global `CLAUDE.md` file serves as a universal configuration that guides Claude Code across all your development projects. This guide outlines the best practices for creating and maintaining an effective global configuration.

## Key Benefits

1. **Consistency**: Ensures uniform development practices across all projects
2. **Efficiency**: Reduces context switching and setup time
3. **Quality**: Maintains high standards through documented guidelines
4. **Collaboration**: Provides clear expectations for team members
5. **Automation**: Enables better MCP integration and workflow automation

## File Structure Best Practices

### 1. Location & Naming
```
~/.claude/claude.md          # Global configuration (recommended)
~/.claude/CLAUDE.md         # Alternative naming
project/CLAUDE.md           # Project-specific overrides
```

### 2. Content Organization
Use a hierarchical structure with clear sections:

```markdown
# Global Claude Code Configuration

## Table of Contents
- [Development Philosophy](#development-philosophy)
- [Code Style Guidelines](#code-style-guidelines)
- [Common Commands & Tools](#common-commands--tools)
- [Repository Etiquette](#repository-etiquette)
- [Environment Setup](#environment-setup)
- [MCP Integration](#mcp-integration)
- [Project-Specific Notes](#project-specific-notes)
- [Quality Standards](#quality-standards)
```

## Essential Sections

### 1. Development Philosophy
Define your core principles:
- Code quality standards
- Problem-solving approach
- Security considerations
- Performance requirements

### 2. Code Style Guidelines
Include:
- Formatting rules (indentation, line length)
- Naming conventions
- Documentation standards
- Language-specific guidelines

### 3. Common Commands & Tools
Document frequently used:
- Package management commands
- Git workflow commands
- Development server commands
- Testing and build commands

### 4. Repository Etiquette
Establish:
- Branch naming conventions
- Commit message formats
- Merge vs rebase policies
- Code review processes

### 5. Environment Setup
Provide:
- Required software versions
- Environment variable templates
- IDE configuration recommendations
- Platform-specific setup instructions

### 6. MCP Integration
Configure:
- Available MCP servers
- Server configurations
- API key management
- Workflow automation
- MCP tool naming conventions

## Content Writing Best Practices

### 1. Clarity & Conciseness
- Use short, clear sentences
- Avoid jargon and technical terms without explanation
- Provide examples for complex concepts
- Use bullet points for lists

### 2. Structure & Navigation
- Use consistent heading hierarchy (H1 → H2 → H3)
- Include a table of contents for long documents
- Use descriptive section names
- Group related information together

### 3. Examples & Code Blocks
- Provide practical examples
- Use syntax highlighting for code blocks
- Include both positive and negative examples
- Show before/after comparisons

### 4. Maintenance & Updates
- Include version information
- Document when last updated
- Provide update procedures
- Include change log for major updates

## Implementation Strategy

### Phase 1: Basic Structure
1. Create the global file with essential sections
2. Add your current development practices
3. Include common commands and tools
4. Test with a few projects

### Phase 2: Enhancement
1. Add MCP server configurations
2. Include project-specific notes
3. Add troubleshooting sections
4. Create templates for new projects

### Phase 3: Optimization
1. Gather feedback from usage
2. Refine based on common issues
3. Add automation where possible
4. Create project-specific overrides

## Project-Specific Overrides

### When to Use Project-Specific CLAUDE.md
- Unique technology stacks
- Specialized development workflows
- Project-specific tools and commands
- Different quality standards

### How to Structure Overrides
```markdown
# Project-Specific Configuration

This file extends the global CLAUDE.md configuration.

## Project Overview
Brief description of the project and its unique requirements.

## Technology Stack
- Frontend: React, TypeScript, Tailwind CSS
- Backend: Node.js, Express, PostgreSQL
- Testing: Jest, Cypress
- Deployment: Docker, AWS

## Project-Specific Commands
```bash
npm run dev:frontend     # Start frontend development server
npm run dev:backend      # Start backend development server
npm run test:e2e         # Run end-to-end tests
```

## Override Global Settings
- Use 4-space indentation (overrides global 2-space)
- Use semicolons (overrides global no-semicolon policy)
```

## Maintenance Best Practices

### 1. Regular Updates
- Review monthly for outdated information
- Update when adopting new tools or practices
- Remove deprecated commands and tools
- Add new best practices as they emerge

### 2. Version Control
- Track changes in version control
- Use meaningful commit messages
- Tag major versions
- Maintain a changelog

### 3. Team Collaboration
- Share with team members
- Gather feedback regularly
- Document team-specific practices
- Resolve conflicts between global and project-specific settings

### 4. Testing & Validation
- Test with different project types
- Validate MCP server configurations
- Check command examples work
- Verify environment setup instructions

## Common Pitfalls to Avoid

### 1. Over-Documentation
- Don't include every possible command
- Focus on commonly used practices
- Avoid redundant information
- Keep it concise and actionable

### 2. Outdated Information
- Don't let examples become stale
- Update version numbers regularly
- Remove deprecated tools and commands
- Keep links and references current

### 3. Inconsistent Structure
- Use consistent formatting throughout
- Maintain the same section order
- Use consistent code block formatting
- Keep heading hierarchy logical

### 4. Missing Context
- Don't assume prior knowledge
- Provide context for complex concepts
- Include prerequisites where needed
- Explain the reasoning behind practices

## Advanced Features

### 1. Dynamic Content
- Use placeholders for environment-specific values
- Include conditional sections based on project type
- Provide templates for common scenarios
- Use includes for shared content

### 2. Integration with Tools
- Configure MCP servers for automation
- Set up custom slash commands
- Integrate with CI/CD pipelines
- Connect with project management tools

### 3. Multi-Language Support
- Document practices for different programming languages
- Include language-specific tools and commands
- Provide examples in multiple languages
- Handle cross-language dependencies

## MCP Server Naming Convention Rules

### Mandatory 4-Letter Acronym System
All MCP servers MUST use a standardized 4-letter prefix followed by a single underscore (_) to prevent naming conflicts and ensure consistency across projects.

### Naming Format
```
{4char}_{tool_name}
```
**Examples:**
- `seqt_sequentialthinking` (sequential-thinking server)
- `file_read_text_file` (filesystem server)
- `task_initialize_project` (task-master-ai server)

### Acronym Assignment Rules
1. **Uniqueness**: Each MCP server must have a unique 4-letter acronym
2. **Consistency**: Once assigned, acronyms should never change
3. **Clarity**: Acronyms should be recognizable and relate to the server name
4. **Documentation**: All acronyms must be documented in CLAUDE.md

### Reserved Acronyms Registry
Maintain this table in your project's CLAUDE.md to prevent conflicts:

| Server Name | Acronym | Status | Example Tools |
|-------------|---------|---------|---------------|
| sequential-thinking | `seqt` | Reserved | `seqt_sequentialthinking` |
| filesystem | `file` | Reserved | `file_read_text_file` |
| task-master-ai | `task` | Reserved | `task_initialize_project` |
| github | `ghub` | Reserved | `ghub_create_issue` |
| obsidian | `obsi` | Reserved | `obsi_get_note` |
| context7 | `ctx7` | Reserved | `ctx7_search` |
| langgraph-docs-mcp | `lang` | Reserved | `lang_fetch_docs` |
| outlook | `outl` | Reserved | `outl_get_email_by_number` |
| mcp-proxy | `prxy` | Reserved | `prxy_list_servers` |

### Adding New MCP Servers
When integrating a new MCP server:

1. **Choose Unique Acronym**: Check the registry table to avoid conflicts
2. **Update Documentation**: Add the new server to your CLAUDE.md registry
3. **Configure Proxy**: Add acronym mapping to proxy server configuration
4. **Update Permissions**: Add `{Acronym}_*` pattern to settings.local.json allowlist
5. **Test Integration**: Verify tools load with correct naming format

### Implementation Requirements
- **Proxy Configuration**: Implement acronym mapping in MCP proxy server
- **Permission System**: Use capitalized patterns in Claude Code settings (e.g., `Seqt_*`)
- **Documentation**: Maintain current registry in project CLAUDE.md files
- **Validation**: Prevent duplicate acronyms through documentation reviews

## Conclusion

A well-maintained global `CLAUDE.md` file is an investment in development efficiency and code quality. By following these best practices, you'll create a comprehensive guide that serves as a reliable reference for all your development projects.

Remember to:
- Start simple and iterate
- Gather feedback from actual usage
- Keep it updated and relevant
- Balance global consistency with project flexibility
- Use it as a living document that evolves with your practices
