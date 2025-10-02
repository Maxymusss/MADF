"""
Obsidian MCP Client - MCP Bridge Integration

Provides Obsidian note and documentation operations via mcp_bridge.py MCPBridge class.
Uses obsidian-mcp MCP server via Python MCP SDK.
"""

import os
from typing import Dict, List, Any, Optional
import logging
from core.mcp_bridge import MCPBridge

logger = logging.getLogger(__name__)


class ObsidianClient:
    """Client for Obsidian note and documentation operations via MCP bridge"""

    def __init__(self, mcp_bridge: Optional[MCPBridge] = None):
        """
        Initialize Obsidian client with MCP bridge

        Args:
            mcp_bridge: Optional MCPBridge instance (creates new if not provided)

        Environment variables required:
            - OBSIDIAN_API_KEY: Obsidian REST API key
            - OBSIDIAN_HOST: Obsidian host (default: 127.0.0.1)
            - OBSIDIAN_PORT: Obsidian port (default: 27124)
        """
        self.mcp_bridge = mcp_bridge or MCPBridge()
        self.api_key = os.getenv("OBSIDIAN_API_KEY")
        self.host = os.getenv("OBSIDIAN_HOST", "127.0.0.1")
        self.port = os.getenv("OBSIDIAN_PORT", "27124")

        self._validate_config()
        self._initialized = False

    def _validate_config(self):
        """Validate required configuration is present"""
        if not self.api_key:
            logger.warning("OBSIDIAN_API_KEY not set - Obsidian MCP may not function")

    async def initialize(self):
        """Initialize Obsidian connection (lazy initialization)"""
        if self._initialized:
            return

        try:
            # MCP server initialization handled by mcp_bridge
            self._initialized = True
            logger.info("Obsidian client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Obsidian: {e}")
            raise

    async def list_files_in_vault(self) -> List[Dict[str, Any]]:
        """
        List all files and directories in the root directory of Obsidian vault

        Returns:
            List of files and directories with metadata
        """
        if not self._initialized:
            await self.initialize()

        try:
            result = await self.mcp_bridge.call_mcp_tool(
                server_name="obsidian",
                tool_name="list_files_in_vault",
                parameters={}
            )

            if result.get("success"):
                # Parse MCP result
                mcp_result = result.get("result", {})
                if isinstance(mcp_result, list) and len(mcp_result) > 0:
                    content_obj = mcp_result[0]
                    if hasattr(content_obj, 'text'):
                        # Parse file listing from text
                        import json
                        return json.loads(content_obj.text)
                    elif isinstance(content_obj, dict):
                        return content_obj.get("files", [])
                return []
            else:
                logger.error(f"Failed to list files: {result.get('error')}")
                return []

        except Exception as e:
            logger.error(f"Failed to list files in vault: {e}")
            return []

    async def list_files_in_dir(self, directory: str) -> List[Dict[str, Any]]:
        """
        List all files and directories in a specific Obsidian directory

        Args:
            directory: Directory path in vault

        Returns:
            List of files and directories with metadata
        """
        if not self._initialized:
            await self.initialize()

        try:
            result = await self.mcp_bridge.call_mcp_tool(
                server_name="obsidian",
                tool_name="list_files_in_dir",
                parameters={"directory": directory}
            )

            if result.get("success"):
                mcp_result = result.get("result", {})
                if isinstance(mcp_result, list) and len(mcp_result) > 0:
                    content_obj = mcp_result[0]
                    if hasattr(content_obj, 'text'):
                        import json
                        return json.loads(content_obj.text)
                    elif isinstance(content_obj, dict):
                        return content_obj.get("files", [])
                return []
            else:
                logger.error(f"Failed to list directory: {result.get('error')}")
                return []

        except Exception as e:
            logger.error(f"Failed to list files in directory: {e}")
            return []

    async def get_file_contents(self, file_path: str) -> Dict[str, Any]:
        """
        Return the content of a single file in vault

        Args:
            file_path: Path to file in vault

        Returns:
            Dict containing file content and metadata
        """
        if not self._initialized:
            await self.initialize()

        try:
            result = await self.mcp_bridge.call_mcp_tool(
                server_name="obsidian",
                tool_name="get_file_contents",
                parameters={"file_path": file_path}
            )

            if result.get("success"):
                # Parse MCP result
                mcp_result = result.get("result", {})
                if isinstance(mcp_result, list) and len(mcp_result) > 0:
                    content_obj = mcp_result[0]
                    if hasattr(content_obj, 'text'):
                        content = content_obj.text
                    elif isinstance(content_obj, dict):
                        content = content_obj.get('text', '')
                    else:
                        content = str(content_obj)

                    return {
                        "path": file_path,
                        "content": content,
                        "status": "success"
                    }
                else:
                    return {"error": "No content returned"}
            else:
                return {"error": result.get("error", "Unknown error")}

        except Exception as e:
            logger.error(f"Failed to get file contents: {e}")
            return {"error": str(e)}

    async def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for documents matching a specified text query across all files

        Args:
            query: Text query to search for

        Returns:
            List of matching files with context
        """
        if not self._initialized:
            await self.initialize()

        try:
            result = await self.mcp_bridge.call_mcp_tool(
                server_name="obsidian",
                tool_name="search",
                parameters={"query": query}
            )

            if result.get("success"):
                # Parse MCP result
                mcp_result = result.get("result", {})
                if isinstance(mcp_result, list) and len(mcp_result) > 0:
                    content_obj = mcp_result[0]
                    if hasattr(content_obj, 'text'):
                        # Parse search results from JSON
                        import json
                        return json.loads(content_obj.text)
                    elif isinstance(content_obj, dict):
                        return content_obj.get("results", [])
                return []
            else:
                logger.error(f"Failed to search vault: {result.get('error')}")
                return []

        except Exception as e:
            logger.error(f"Failed to search vault: {e}")
            return []

    async def patch_content(
        self,
        file_path: str,
        content: str,
        heading: Optional[str] = None,
        block_ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Insert content into an existing note relative to a heading or block reference

        Args:
            file_path: Path to file in vault
            content: Content to insert
            heading: Optional heading to insert under
            block_ref: Optional block reference

        Returns:
            Dict containing operation result
        """
        if not self._initialized:
            await self.initialize()

        try:
            parameters = {
                "file_path": file_path,
                "content": content
            }
            if heading:
                parameters["heading"] = heading
            if block_ref:
                parameters["block_ref"] = block_ref

            result = await self.mcp_bridge.call_mcp_tool(
                server_name="obsidian",
                tool_name="patch_content",
                parameters=parameters
            )

            if result.get("success"):
                return {
                    "success": True,
                    "file_path": file_path,
                    "operation": "patch",
                    "heading": heading,
                    "block_ref": block_ref,
                    "content_added": len(content)
                }
            else:
                return {"success": False, "error": result.get("error", "Unknown error")}

        except Exception as e:
            logger.error(f"Failed to patch content: {e}")
            return {"success": False, "error": str(e)}

    async def append_content(
        self,
        file_path: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Append content to a new or existing file in the vault

        Args:
            file_path: Path to file in vault
            content: Content to append

        Returns:
            Dict containing operation result
        """
        if not self._initialized:
            await self.initialize()

        try:
            result = await self.mcp_bridge.call_mcp_tool(
                server_name="obsidian",
                tool_name="append_content",
                parameters={"file_path": file_path, "content": content}
            )

            if result.get("success"):
                return {
                    "success": True,
                    "file_path": file_path,
                    "operation": "append",
                    "content_added": len(content)
                }
            else:
                return {"success": False, "error": result.get("error", "Unknown error")}

        except Exception as e:
            logger.error(f"Failed to append content: {e}")
            return {"success": False, "error": str(e)}

    async def delete_file(self, file_path: str) -> Dict[str, Any]:
        """
        Delete a file or directory from vault

        Args:
            file_path: Path to file/directory to delete

        Returns:
            Dict containing operation result
        """
        if not self._initialized:
            await self.initialize()

        try:
            result = await self.mcp_bridge.call_mcp_tool(
                server_name="obsidian",
                tool_name="delete_file",
                parameters={"file_path": file_path}
            )

            if result.get("success"):
                return {
                    "success": True,
                    "file_path": file_path,
                    "operation": "delete"
                }
            else:
                return {"success": False, "error": result.get("error", "Unknown error")}

        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return {"success": False, "error": str(e)}

    async def close(self):
        """Close Obsidian connection"""
        self._initialized = False
        logger.info("Obsidian client closed")
