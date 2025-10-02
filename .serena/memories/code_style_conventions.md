# MADF Code Style & Conventions

## Python Code Style
Based on analysis of existing codebase:

### Import Organization
```python
# Standard library imports first
import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

# Third-party imports
import subprocess
import tempfile
```

### Class Naming & Structure
- **PascalCase** for class names: `ProductManagerAgent`, `MultiAgentFramework`
- **snake_case** for methods and variables: `get_week_timeframe`, `workspace_dir`
- Type hints required for all method parameters and returns

### Method Structure Pattern
```python
def method_name(self, param: type, optional: Optional[type] = None) -> return_type:
    """Docstring describing method purpose"""
    # Implementation
```

### Variable Naming
- Descriptive names: `current_session_id`, `error_log_file`, `performance_log_file`
- Directory paths end with `_dir`: `workspace_dir`, `tasks_dir`, `results_dir`, `logs_dir`
- File paths end with `_file`: `error_log_file`, `performance_log_file`

### Agent Class Pattern
All agent classes follow this structure:
1. `__init__` with workspace setup and directory creation
2. Core business logic methods
3. Helper/utility methods  
4. Logging and error handling methods
5. Main execution method (usually `execute_*`)

### File and Directory Handling
- Use `pathlib.Path` for path operations
- Create directories with `os.makedirs(path, exist_ok=True)`
- Use relative paths from workspace root

### Logging Convention
- Use structured logging with `logging` module
- Log levels: INFO for normal operations, ERROR for failures
- Include context in log messages

## Project Structure
- **agents/**: Individual agent implementations
- **agent_workspace/**: Runtime communication directory
  - `tasks/`: Task specifications (JSON)
  - `results/`: Agent outputs (JSON) 
  - `logs/`: Error tracking and metrics
- **projects/**: Individual project directories
- **.claude/**: Framework configuration and rules

## Documentation Style
- README files use markdown with clear sections
- Code comments explain "why" not "what"
- Type hints serve as inline documentation
- Methods include brief docstrings for complex logic

## Testing Conventions
- Test files prefix with `test_`
- Verification scripts prefix with `verify_`
- Simple tests for Windows compatibility
- Story-based test organization (`run_story_1_1_tests.py`)

## Development Tools Configuration
- **Black**: Code formatting (default settings)
- **Flake8**: Linting (default rules)
- **MyPy**: Type checking enabled
- **Pytest**: Testing framework