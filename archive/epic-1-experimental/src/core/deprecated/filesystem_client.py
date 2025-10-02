"""
Filesystem MCP Client - MCP Bridge Integration

Provides filesystem operations via mcp_bridge.py MCPBridge class.
Uses @modelcontextprotocol/server-filesystem MCP server via Python MCP SDK.
"""

import os
from typing import Dict, List, Any, Optional
import logging
from core.mcp_bridge import MCPBridge

logger = logging.getLogger(__name__)


class FilesystemClient:
    """Client for filesystem operations via MCP bridge"""

    def __init__(self, mcp_bridge: Optional[MCPBridge] = None):
        """
        Initialize Filesystem client with MCP bridge

        Args:
            mcp_bridge: Optional MCPBridge instance (creates new if not provided)

        Environment variables optional:
            - FILESYSTEM_ALLOWED_DIRS: Comma-separated list of allowed directories
        """
        self.mcp_bridge = mcp_bridge or MCPBridge()
        self.allowed_dirs = os.getenv("FILESYSTEM_ALLOWED_DIRS", "").split(",")
        self.allowed_dirs = [d.strip() for d in self.allowed_dirs if d.strip()]

        self._validate_config()
        self._initialized = False

    def _validate_config(self):
        """Validate configuration"""
        if not self.allowed_dirs:
            logger.info("No FILESYSTEM_ALLOWED_DIRS set - will use MCP server default configuration")

    async def initialize(self):
        """Initialize Filesystem connection (lazy initialization)"""
        if self._initialized:
            return

        try:
            # MCP server initialization handled by mcp_bridge
            self._initialized = True
            logger.info("Filesystem client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Filesystem: {e}")
            raise

    async def read_file(
        self,
        path: str,
        head: Optional[int] = None,
        tail: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Read complete file contents as text

        Args:
            path: File path to read
            head: Optional first N lines
            tail: Optional last N lines

        Returns:
            Dict containing file content
        """
        if not self._initialized:
            await self.initialize()

        try:
            # Build parameters
            parameters = {"path": path}
            if head is not None:
                parameters["head"] = head
            if tail is not None:
                parameters["tail"] = tail

            # Call filesystem MCP server via bridge
            result = await self.mcp_bridge.call_mcp_tool(
                server_name="filesystem",
                tool_name="read_text_file",
                parameters=parameters
            )

            if result.get("success"):
                # Extract content from MCP result
                mcp_result = result.get("result", {})
                # MCP returns list of TextContent objects
                if isinstance(mcp_result, list) and len(mcp_result) > 0:
                    content_obj = mcp_result[0]
                    if hasattr(content_obj, 'text'):
                        content = content_obj.text
                    elif isinstance(content_obj, dict):
                        content = content_obj.get('text', '')
                    else:
                        content = str(content_obj)
                else:
                    content = str(mcp_result)

                return {
                    "path": path,
                    "content": content,
                    "lines": len(content.split('\n')) if content else 0,
                    "size": len(content) if content else 0
                }
            else:
                return {"error": result.get("error", "Unknown error")}

        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            return {"error": str(e)}

    async def write_file(self, path: str, content: str) -> Dict[str, Any]:
        """
        Create new file or overwrite existing

        Args:
            path: File path to write
            content: File content

        Returns:
            Dict containing operation result
        """
        if not self._initialized:
            await self.initialize()

        try:
            result = await self.mcp_bridge.call_mcp_tool(
                server_name="filesystem",
                tool_name="write_file",
                parameters={"path": path, "content": content}
            )

            if result.get("success"):
                return {
                    "success": True,
                    "path": path,
                    "operation": "write",
                    "bytes_written": len(content)
                }
            else:
                return {"success": False, "error": result.get("error", "Unknown error")}

        except Exception as e:
            logger.error(f"Failed to write file: {e}")
            return {"success": False, "error": str(e)}

    async def create_directory(self, path: str) -> Dict[str, Any]:
        """
        Create directory with parent directories

        Args:
            path: Directory path to create

        Returns:
            Dict containing operation result
        """
        if not self._initialized:
            await self.initialize()

        try:
            result = await self.mcp_bridge.call_mcp_tool(
                server_name="filesystem",
                tool_name="create_directory",
                parameters={"path": path}
            )

            if result.get("success"):
                return {
                    "success": True,
                    "path": path,
                    "operation": "create_directory",
                    "created": True
                }
            else:
                return {"success": False, "error": result.get("error", "Unknown error")}

        except Exception as e:
            logger.error(f"Failed to create directory: {e}")
            return {"success": False, "error": str(e)}

    async def list_directory(self, path: str) -> List[Dict[str, Any]]:
        """
        List directory contents with [FILE] or [DIR] prefixes

        Args:
            path: Directory path to list

        Returns:
            List of directory entries
        """
        if not self._initialized:
            await self.initialize()

        try:
            result = await self.mcp_bridge.call_mcp_tool(
                server_name="filesystem",
                tool_name="list_directory",
                parameters={"path": path}
            )

            if result.get("success"):
                # Parse MCP result - returns list of TextContent with formatted strings
                mcp_result = result.get("result", {})
                entries = []

                if isinstance(mcp_result, list) and len(mcp_result) > 0:
                    content_obj = mcp_result[0]
                    if hasattr(content_obj, 'text'):
                        text = content_obj.text
                    elif isinstance(content_obj, dict):
                        text = content_obj.get('text', '')
                    else:
                        text = str(content_obj)

                    # Parse directory listing format: "[FILE] filename" or "[DIR] dirname"
                    for line in text.split('\n'):
                        line = line.strip()
                        if line.startswith('[FILE]'):
                            name = line.replace('[FILE]', '').strip()
                            entries.append({
                                "name": name,
                                "type": "file",
                                "path": f"{path}/{name}"
                            })
                        elif line.startswith('[DIR]'):
                            name = line.replace('[DIR]', '').strip()
                            entries.append({
                                "name": name,
                                "type": "directory",
                                "path": f"{path}/{name}"
                            })

                return entries
            else:
                logger.error(f"Failed to list directory: {result.get('error')}")
                return []

        except Exception as e:
            logger.error(f"Failed to list directory: {e}")
            return []

    async def list_directory_with_sizes(
        self,
        path: str,
        sort_by: str = "name"
    ) -> Dict[str, Any]:
        """
        List directory contents with sizes and statistics

        Args:
            path: Directory path to list
            sort_by: Sort by "name" or "size"

        Returns:
            Dict containing entries and summary statistics
        """
        if not self._initialized:
            await self.initialize()

        try:
            result = await self.mcp_bridge.call_mcp_tool(
                server_name="filesystem",
                tool_name="list_directory_with_sizes",
                parameters={"path": path, "sortBy": sort_by}
            )

            if result.get("success"):
                # Parse MCP result
                mcp_result = result.get("result", {})
                if isinstance(mcp_result, list) and len(mcp_result) > 0:
                    content_obj = mcp_result[0]
                    if hasattr(content_obj, 'text'):
                        text = content_obj.text
                    elif isinstance(content_obj, dict):
                        text = content_obj.get('text', '')
                    else:
                        text = str(content_obj)

                    # Parse formatted output
                    entries = []
                    total_files = 0
                    total_directories = 0
                    total_size = 0

                    for line in text.split('\n'):
                        line = line.strip()
                        if '[FILE]' in line:
                            # Parse: [FILE] filename (1024 bytes)
                            parts = line.split()
                            name = parts[1] if len(parts) > 1 else "unknown"
                            size = int(parts[2].replace('(', '')) if len(parts) > 2 else 0
                            entries.append({"name": name, "type": "file", "size": size})
                            total_files += 1
                            total_size += size
                        elif '[DIR]' in line:
                            name = line.replace('[DIR]', '').strip()
                            entries.append({"name": name, "type": "directory", "size": 0})
                            total_directories += 1

                    return {
                        "path": path,
                        "entries": entries,
                        "total_files": total_files,
                        "total_directories": total_directories,
                        "total_size": total_size
                    }
                else:
                    return {
                        "path": path,
                        "entries": [],
                        "total_files": 0,
                        "total_directories": 0,
                        "total_size": 0
                    }
            else:
                return {"error": result.get("error", "Unknown error")}

        except Exception as e:
            logger.error(f"Failed to list directory with sizes: {e}")
            return {"error": str(e)}

    async def move_file(self, source: str, destination: str) -> Dict[str, Any]:
        """
        Move or rename files/directories

        Args:
            source: Source path
            destination: Destination path

        Returns:
            Dict containing operation result
        """
        if not self._initialized:
            await self.initialize()

        try:
            result = await self.mcp_bridge.call_mcp_tool(
                server_name="filesystem",
                tool_name="move_file",
                parameters={"source": source, "destination": destination}
            )

            if result.get("success"):
                return {
                    "success": True,
                    "operation": "move",
                    "source": source,
                    "destination": destination
                }
            else:
                return {"success": False, "error": result.get("error", "Unknown error")}

        except Exception as e:
            logger.error(f"Failed to move file: {e}")
            return {"success": False, "error": str(e)}

    async def search_files(
        self,
        path: str,
        pattern: str,
        exclude_patterns: Optional[List[str]] = None
    ) -> List[str]:
        """
        Recursively search for files matching patterns

        Args:
            path: Starting directory
            pattern: Search pattern (glob-style)
            exclude_patterns: Optional exclude patterns

        Returns:
            List of matching file paths
        """
        if not self._initialized:
            await self.initialize()

        try:
            parameters = {"path": path, "pattern": pattern}
            if exclude_patterns:
                parameters["excludePatterns"] = exclude_patterns

            result = await self.mcp_bridge.call_mcp_tool(
                server_name="filesystem",
                tool_name="search_files",
                parameters=parameters
            )

            if result.get("success"):
                # Parse MCP result
                mcp_result = result.get("result", {})
                if isinstance(mcp_result, list) and len(mcp_result) > 0:
                    content_obj = mcp_result[0]
                    if hasattr(content_obj, 'text'):
                        text = content_obj.text
                    elif isinstance(content_obj, dict):
                        text = content_obj.get('text', '')
                    else:
                        text = str(content_obj)

                    # Parse file paths from result (one per line)
                    return [line.strip() for line in text.split('\n') if line.strip()]
                else:
                    return []
            else:
                logger.error(f"Failed to search files: {result.get('error')}")
                return []

        except Exception as e:
            logger.error(f"Failed to search files: {e}")
            return []

    async def directory_tree(
        self,
        path: str,
        exclude_patterns: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recursive JSON tree structure of directory

        Args:
            path: Starting directory
            exclude_patterns: Optional exclude patterns

        Returns:
            List representing directory tree structure
        """
        if not self._initialized:
            await self.initialize()

        try:
            parameters = {"path": path}
            if exclude_patterns:
                parameters["excludePatterns"] = exclude_patterns

            result = await self.mcp_bridge.call_mcp_tool(
                server_name="filesystem",
                tool_name="directory_tree",
                parameters=parameters
            )

            if result.get("success"):
                # MCP returns JSON structure directly
                mcp_result = result.get("result", {})
                if isinstance(mcp_result, list) and len(mcp_result) > 0:
                    content_obj = mcp_result[0]
                    if hasattr(content_obj, 'text'):
                        # Parse JSON from text
                        import json
                        return json.loads(content_obj.text)
                    elif isinstance(content_obj, dict):
                        # Already parsed
                        return [content_obj]
                    else:
                        return []
                else:
                    return []
            else:
                logger.error(f"Failed to get directory tree: {result.get('error')}")
                return []

        except Exception as e:
            logger.error(f"Failed to get directory tree: {e}")
            return []

    async def get_file_info(self, path: str) -> Dict[str, Any]:
        """
        Get detailed file/directory metadata

        Args:
            path: File or directory path

        Returns:
            Dict containing file metadata
        """
        if not self._initialized:
            await self.initialize()

        try:
            result = await self.mcp_bridge.call_mcp_tool(
                server_name="filesystem",
                tool_name="get_file_info",
                parameters={"path": path}
            )

            if result.get("success"):
                # Parse MCP result
                mcp_result = result.get("result", {})
                if isinstance(mcp_result, list) and len(mcp_result) > 0:
                    content_obj = mcp_result[0]
                    if hasattr(content_obj, 'text'):
                        # Parse structured info from text
                        text = content_obj.text
                        # Extract metadata (format may vary)
                        return {
                            "path": path,
                            "raw_info": text
                        }
                    elif isinstance(content_obj, dict):
                        return content_obj
                    else:
                        return {"path": path, "info": str(content_obj)}
                else:
                    return {"path": path}
            else:
                return {"error": result.get("error", "Unknown error")}

        except Exception as e:
            logger.error(f"Failed to get file info: {e}")
            return {"error": str(e)}

    async def list_allowed_directories(self) -> List[str]:
        """
        List directories the filesystem MCP server can access

        Returns:
            List of allowed directory paths
        """
        if not self._initialized:
            await self.initialize()

        try:
            result = await self.mcp_bridge.call_mcp_tool(
                server_name="filesystem",
                tool_name="list_allowed_directories",
                parameters={}
            )

            if result.get("success"):
                # Parse MCP result
                mcp_result = result.get("result", {})
                if isinstance(mcp_result, list) and len(mcp_result) > 0:
                    content_obj = mcp_result[0]
                    if hasattr(content_obj, 'text'):
                        text = content_obj.text
                    elif isinstance(content_obj, dict):
                        text = content_obj.get('text', '')
                    else:
                        text = str(content_obj)

                    # Parse directory paths from result (one per line)
                    return [line.strip() for line in text.split('\n') if line.strip()]
                else:
                    return []
            else:
                logger.error(f"Failed to list allowed directories: {result.get('error')}")
                return []

        except Exception as e:
            logger.error(f"Failed to list allowed directories: {e}")
            return []

    async def close(self):
        """Close Filesystem connection"""
        self._initialized = False
        logger.info("Filesystem client closed")
