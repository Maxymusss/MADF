# Parallel Task Workflow

## 8-Task Parallel Implementation Workflow

1. **Component**: Create main component file
2. **Styles**: Create component styles/CSS
3. **Tests**: Create test files
4. **Types**: Create type definitions
5. **Hooks**: Create custom hooks/utilities
6. **Integration**: Update routing, imports, exports
7. **Remaining**: Update package.json, documentation, configuration files
8. **Review and Validation**: Coordinate integration, run tests, verify build, check for conflicts

## Task Execution Workflow

### Simple Tasks (1-3 files, clear requirements)
- **Direct Execution**: Proceed immediately without extensive planning
- **Examples**: Fix typo, add single component, update config value

### Complex Tasks (4+ files, architecture changes, unclear scope)
- **Plan → Approve → Execute Fast**
  1. Brief planning phase (present approach)
  2. Get user confirmation
  3. Execute immediately with parallel tasks once approved
- **Examples**: New feature, refactoring, system integration

### Parallel Execution (Post-Approval)
- Use 8-task parallel method for approved complex features
- Launch all tasks simultaneously via Task tool
- No additional clarifications once execution begins

## Message & State Management
- **Context Optimization**: Read with comments for context, strip only if hitting token limits
- **Task Isolation**: Each task handles ONLY specified files or file types
- **Efficient Batching**: Final task combines small config/doc updates to prevent over-splitting
- **State Persistence**: Build consistent state management as patterns emerge