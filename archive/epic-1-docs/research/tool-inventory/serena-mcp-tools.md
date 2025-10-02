# Serena MCP Server - Complete Tool List

**Package**: `oraios/serena`
**Purpose**: Semantic code search and LSP-powered code operations
**Integration**: Direct Python MCP SDK (stdio)
**Total Tools**: 26

---

## Category 1: File Operations (6 tools)

### 1. read_file
**Purpose**: Read file contents with optional line range
**Parameters**:
- `relative_path` (string, required) - File path relative to project root
- `start_line` (number, optional) - Starting line number
- `end_line` (number, optional) - Ending line number

---

### 2. create_text_file
**Purpose**: Create new text file
**Parameters**:
- `relative_path` (string, required) - File path to create
- `content` (string, required) - File content

---

### 3. list_dir
**Purpose**: List directory contents
**Parameters**:
- `relative_path` (string, required) - Directory path
- `recursive` (boolean, optional) - Recursive listing

---

### 4. find_file
**Purpose**: Find files matching pattern
**Parameters**:
- `file_mask` (string, required) - File pattern (e.g., `*.py`)
- `relative_path` (string, optional) - Starting directory

---

### 5. replace_regex
**Purpose**: Regex find-and-replace in file
**Parameters**:
- `relative_path` (string, required) - File path
- `regex` (string, required) - Regex pattern
- `repl` (string, required) - Replacement string

---

### 6. search_for_pattern
**Purpose**: Search for substring pattern in file
**Parameters**:
- `substring_pattern` (string, required) - Pattern to find
- `relative_path` (string, required) - File to search

---

## Category 2: LSP Symbol Operations (6 tools)

### 7. get_symbols_overview
**Purpose**: Get overview of all symbols in file
**Parameters**:
- `relative_path` (string, required) - File path

**Returns**: List of classes, functions, methods with line numbers

---

### 8. find_symbol
**Purpose**: Find symbol definition
**Parameters**:
- `name_path` (string, required) - Symbol name (e.g., "MCPBridge")
- `relative_path` (string, required) - File path
- `include_body` (boolean, optional) - Include symbol body code

**Returns**: Symbol location, signature, optional body

---

### 9. find_referencing_symbols
**Purpose**: Find all references to a symbol
**Parameters**:
- `name_path` (string, required) - Symbol name
- `relative_path` (string, required) - File path

**Returns**: List of locations where symbol is used

---

### 10. replace_symbol_body
**Purpose**: Replace symbol implementation
**Parameters**:
- `name_path` (string, required) - Symbol to replace
- `relative_path` (string, required) - File path
- `new_body` (string, required) - New implementation code

**Warning**: Destructive operation

---

### 11. insert_after_symbol
**Purpose**: Insert code after symbol
**Parameters**:
- `name_path` (string, required) - Symbol name
- `relative_path` (string, required) - File path
- `code_to_insert` (string, required) - Code to insert

**Warning**: Destructive operation

---

### 12. insert_before_symbol
**Purpose**: Insert code before symbol
**Parameters**:
- `name_path` (string, required) - Symbol name
- `relative_path` (string, required) - File path
- `code_to_insert` (string, required) - Code to insert

**Warning**: Destructive operation

---

## Category 3: Memory Management (4 tools)

### 13. write_memory
**Purpose**: Store memory/note for session
**Parameters**:
- `memory_name` (string, required) - Memory identifier
- `content` (string, required) - Markdown content to store

---

### 14. read_memory
**Purpose**: Retrieve stored memory
**Parameters**:
- `memory_file_name` (string, required) - Memory identifier

**Returns**: Stored markdown content

---

### 15. list_memories
**Purpose**: List all stored memories
**Parameters**: None

**Returns**: Array of memory names

---

### 16. delete_memory
**Purpose**: Delete stored memory
**Parameters**:
- `memory_file_name` (string, required) - Memory to delete

---

## Category 4: System Operations (7 tools)

### 17. execute_shell_command
**Purpose**: Execute shell command in project context
**Parameters**:
- `command` (string, required) - Shell command

**Returns**: Command output

---

### 18. activate_project
**Purpose**: Activate specific project context
**Parameters**:
- `project` (string, required) - Project name

---

### 19. switch_modes
**Purpose**: Change Serena operation modes
**Parameters**:
- `modes` (array, required) - Mode names (e.g., ["interactive"])

---

### 20. get_current_config
**Purpose**: Get current Serena configuration
**Parameters**: None

**Returns**: Configuration object

---

### 21. check_onboarding_performed
**Purpose**: Check if onboarding completed
**Parameters**: None

**Returns**: Boolean status

---

### 22. onboarding
**Purpose**: Perform Serena onboarding/setup
**Parameters**: Various setup parameters

**Note**: Time-consuming operation

---

### 23. prepare_for_new_conversation
**Purpose**: Reset state for new conversation
**Parameters**: None

**Returns**: Success status

---

## Category 5: Thinking Tools (3 tools)

### 24. think_about_collected_information
**Purpose**: Reflect on gathered code information
**Parameters**:
- Context about collected information

**Returns**: Analysis/reflection

---

### 25. think_about_task_adherence
**Purpose**: Evaluate task completion progress
**Parameters**:
- Task description
- Current state

**Returns**: Adherence analysis

---

### 26. think_about_whether_you_are_done
**Purpose**: Determine if task is complete
**Parameters**:
- Task requirements
- Work completed

**Returns**: Completion assessment

---

## Summary by Category

| Category | Tool Count | Key Use Cases |
|----------|-----------|---------------|
| File Operations | 6 | Reading, creating, searching files |
| LSP Symbol Operations | 6 | Finding classes/functions, references, editing |
| Memory Management | 4 | Session memory/notes storage |
| System Operations | 7 | Shell commands, config, project management |
| Thinking Tools | 3 | Meta-cognition, task tracking |

**Most Used Tools** (based on actual usage in MADF):
1. `get_symbols_overview` - Get file structure
2. `find_symbol` - Locate class/function definitions
3. `find_referencing_symbols` - Find where symbols are used
4. `search_for_pattern` - Text-based code search
5. `read_file` - Read file contents

**Performance Notes**:
- Direct Python MCP SDK via stdio (faster than HTTP bridge)
- LSP-powered = semantic understanding (not just text search)
- Supports 20+ programming languages via LSP
