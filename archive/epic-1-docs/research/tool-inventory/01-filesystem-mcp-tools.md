# Filesystem MCP Server - Complete Tool List

**Package**: `@modelcontextprotocol/server-filesystem`
**Purpose**: File and directory operations with access control

## All Available Tools

### 1. read_text_file
**Purpose**: Read complete file contents as UTF-8 text
**Parameters**:
- `path` (string, required) - File path
- `head` (number, optional) - Read first N lines only
- `tail` (number, optional) - Read last N lines only

**Notes**: Cannot use head and tail simultaneously

---

### 2. read_media_file
**Purpose**: Read image or audio files as base64
**Parameters**:
- `path` (string, required) - Media file path

**Returns**: Base64 data with MIME type

---

### 3. read_multiple_files
**Purpose**: Read multiple files simultaneously
**Parameters**:
- `paths` (string[], required) - Array of file paths

**Notes**: Failed reads don't stop entire operation

---

### 4. write_file
**Purpose**: Create new file or overwrite existing
**Parameters**:
- `path` (string, required) - File location
- `content` (string, required) - File content

**Warning**: Overwrites without confirmation

---

### 5. edit_file
**Purpose**: Selective edits with pattern matching
**Parameters**:
- `path` (string, required) - File to edit
- `edits` (array, required) - List of edit operations
  - `oldText` (string) - Text to find
  - `newText` (string) - Replacement text
- `dryRun` (boolean, optional) - Preview without applying

**Features**:
- Whitespace normalization with indentation preservation
- Multiple simultaneous edits
- Git-style diff output
- Dry run mode for preview

**Best Practice**: Always use dryRun first

---

### 6. create_directory
**Purpose**: Create directory or ensure it exists
**Parameters**:
- `path` (string, required) - Directory path

**Notes**: Creates parent directories if needed

---

### 7. list_directory
**Purpose**: List directory contents with type indicators
**Parameters**:
- `path` (string, required) - Directory path

**Returns**: Items prefixed with [FILE] or [DIR]

---

### 8. list_directory_with_sizes
**Purpose**: List directory with file sizes and stats
**Parameters**:
- `path` (string, required) - Directory path
- `sortBy` (string, optional) - Sort by "name" or "size" (default: "name")

**Returns**:
- File sizes
- Total files/directories count
- Combined size

---

### 9. move_file
**Purpose**: Move or rename files/directories
**Parameters**:
- `source` (string, required) - Source path
- `destination` (string, required) - Destination path

**Notes**: Fails if destination exists

---

### 10. search_files
**Purpose**: Recursively search for files matching patterns
**Parameters**:
- `path` (string, required) - Starting directory
- `pattern` (string, required) - Glob pattern
- `excludePatterns` (string[], optional) - Patterns to exclude

**Returns**: Full paths to matches

---

### 11. directory_tree
**Purpose**: Get recursive JSON tree of directory
**Parameters**:
- `path` (string, required) - Starting directory
- `excludePatterns` (string[], optional) - Patterns to exclude

**Returns**: JSON array with:
- `name` (string) - File/directory name
- `type` ('file'|'directory') - Entry type
- `children` (array) - For directories only

---

### 12. get_file_info
**Purpose**: Get detailed file/directory metadata
**Parameters**:
- `path` (string, required) - File/directory path

**Returns**:
- Size
- Creation time
- Modified time
- Access time
- Type (file/directory)
- Permissions

---

### 13. list_allowed_directories
**Purpose**: List accessible directories
**Parameters**: None

**Returns**: Directories server can access

---

## Summary

**Total Tools**: 13
**Categories**:
- Read operations: 3 tools (read_text_file, read_media_file, read_multiple_files)
- Write operations: 2 tools (write_file, edit_file)
- Directory operations: 4 tools (create_directory, list_directory, list_directory_with_sizes, directory_tree)
- File management: 2 tools (move_file, get_file_info)
- Search operations: 1 tool (search_files)
- Access control: 1 tool (list_allowed_directories)
