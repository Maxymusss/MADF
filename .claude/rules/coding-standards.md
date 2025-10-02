# Coding Standards

## Code Quality Standards
- DO NOT edit more code than you have to
- DO NOT WASTE TOKENS, be succinct and concise
- Follow project's established architecture and component patterns
- Use existing utility functions and avoid duplicating functionality
- Solve issues from the root and avoid scaffolding patch work on top of original problem

## String Literal Standards
**CRITICAL: Windows Path Handling**: Always properly escape backslashes in string literals
- [WRONG]: "D:\BT\madf\" (causes SyntaxWarning: invalid escape sequence)
- [CORRECT]: r"D:\BT\madf\" (raw string) OR "D:\\BT\\madf\\" (escaped backslashes)
- **COMMON ERRORS**: \B, \T, \N are invalid escape sequences - use raw strings or double backslashes
- **PREVENTION**: Use raw strings r"" for all Windows paths, or pathlib.Path() for cross-platform paths

## Timestamp and Timezone Standards
**CRITICAL: UTC Consistency**: Use consistent timezone handling throughout codebase
- **STANDARD**: Use `datetime.utcnow()` consistently, avoid mixing with `datetime.now()`
- **COMPARISONS**: Ensure all timestamp comparisons use same timezone basis
- **SERIALIZATION**: Use UTC for all stored timestamps and state persistence
- **TESTING**: Use consistent timezone in test fixtures and assertions
- **MIGRATION NOTE**: Replace deprecated `datetime.utcnow()` with `datetime.now(datetime.UTC)` when upgrading to Python 3.12+

## Security Considerations
- Always follow security best practices
- Never introduce code that exposes or logs secrets and keys
- Never commit secrets or keys to the repository
- Validate all inputs and handle errors gracefully

## Performance Requirements
- Optimize for readability first, performance second
- Use established patterns for state management
- Minimize unnecessary re-renders and calculations
- Consider memory usage in long-running processes

## Model Preferences
- **PRAGMATIC CHANGES**: Balance stability with necessary improvements. Preserve what works, refactor what doesn't.
- **EVOLVE CONVENTIONS**: Establish good patterns early, improve as needed
- **BUILD PATTERNS**: Create reusable patterns as they emerge
- **REUSE UTILITIES**: Use existing utility functions, avoid duplicating functionality