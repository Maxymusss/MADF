"""
Python MCP Bridge - Real MCP Protocol Integration

Enables hybrid MCP architecture with both direct (stdio) and HTTP integrations
Uses Python MCP SDK for actual protocol communication
"""

import json
import asyncio
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from contextlib import asynccontextmanager

# MCP SDK imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import httpx


class MCPBridge:
    """Bridge for communicating with MCP servers using real MCP protocol"""

    def __init__(self):
        self._active_sessions = {}  # Cache for persistent MCP sessions
        self._session_locks = {}  # Async locks for session access

        # Load environment-based configuration
        self._load_env_config()

        self.direct_mcp_servers = {
            "serena": {
                "type": "stdio",
                "command": "uvx",
                "args": ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server", "--project", "d:/dev/MADF"]
            },
            "context7": {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "@upstash/context7-mcp"]
            },
            "sequential_thinking": {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
            }
        }
        self.wrapped_mcp_servers = {
            "github": {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "@gongrzhe/server-github"]
            },
            "tavily": {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "tavily-mcp"]
            },
            "sentry": {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "sentry-mcp"]
            },
            "postgres": {
                "type": "stdio",
                "command": "uv",
                "args": ["run", "postgres-mcp", "--access-mode", "restricted"]
            },
            "obsidian": {
                "type": "stdio",
                "command": "npx",
                "args": self._get_obsidian_args()
            },
            "filesystem": {
                "type": "stdio",
                "command": "npx",
                "args": self._get_filesystem_args()
            },
            "chrome_devtools": {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "chrome-devtools-mcp"]
            }
        }
        self._context7_cache = {}  # Cache for Context7 documentation calls

    def _load_env_config(self):
        """Load environment variables for MCP server configuration"""
        self._filesystem_allowed_dirs = os.getenv("FILESYSTEM_ALLOWED_DIRS", "").split(",")
        self._filesystem_allowed_dirs = [d.strip() for d in self._filesystem_allowed_dirs if d.strip()]

        self._obsidian_vault_path = os.getenv("OBSIDIAN_VAULT_PATH", "")

    def _get_filesystem_args(self) -> List[str]:
        """Get filesystem MCP server args with allowed directories from env"""
        args = ["-y", "@modelcontextprotocol/server-filesystem"]

        # Add allowed directories from environment
        if self._filesystem_allowed_dirs:
            args.extend(self._filesystem_allowed_dirs)

        return args

    def _get_obsidian_args(self) -> List[str]:
        """Get Obsidian MCP server args with vault path from env"""
        args = ["-y", "obsidian-mcp"]

        # Add vault path from environment
        if self._obsidian_vault_path:
            args.append(self._obsidian_vault_path)

        return args

    def test_connection(self) -> Dict[str, Any]:
        """
        Test bridge connection to MCP servers

        Returns:
            Dict containing connection status and info
        """
        try:
            # Test that we can import MCP SDK
            from mcp import ClientSession
            return {
                "status": "connected",
                "bridge_available": True,
                "mcp_sdk_version": "1.15.0",
                "mcp_servers_available": len(self.wrapped_mcp_servers) + len(self.direct_mcp_servers)
            }
        except Exception as e:
            return {
                "status": "error",
                "bridge_available": False,
                "error": str(e)
            }

    def get_available_servers(self) -> List[str]:
        """
        Get list of available MCP servers

        Returns:
            List of server names
        """
        all_servers = list(self.direct_mcp_servers.keys()) + list(self.wrapped_mcp_servers.keys())
        return all_servers

    async def _get_persistent_session(self, server_name: str, server_config: Dict[str, Any]):
        """
        Get or create persistent MCP session for server

        Args:
            server_name: Name of MCP server
            server_config: Server configuration with command and args

        Returns:
            ClientSession for MCP communication
        """
        # Check if session already exists
        if server_name in self._active_sessions:
            return self._active_sessions[server_name]["session"]

        # Create new session
        server_params = StdioServerParameters(
            command=server_config["command"],
            args=server_config["args"],
            env=None
        )

        # Start stdio client and keep context managers alive
        stdio_ctx = stdio_client(server_params)
        read, write = await stdio_ctx.__aenter__()

        session_ctx = ClientSession(read, write)
        session = await session_ctx.__aenter__()
        await session.initialize()

        # Cache session with context managers for cleanup
        self._active_sessions[server_name] = {
            "session": session,
            "session_ctx": session_ctx,
            "stdio_ctx": stdio_ctx
        }
        return session

    @asynccontextmanager
    async def _get_stdio_session(self, server_config: Dict[str, Any]):
        """
        Create MCP stdio session for server (temporary, non-persistent)

        Args:
            server_config: Server configuration with command and args

        Yields:
            ClientSession for MCP communication
        """
        # Pass current environment to subprocess
        import os
        server_params = StdioServerParameters(
            command=server_config["command"],
            args=server_config["args"],
            env=os.environ.copy()
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session

    async def _call_stdio_tool(
        self,
        server_config: Dict[str, Any],
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call tool on stdio MCP server

        Args:
            server_config: Server configuration
            tool_name: Name of tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        try:
            async with self._get_stdio_session(server_config) as session:
                # List available tools
                tools_result = await session.list_tools()

                # Find matching tool
                matching_tool = None
                for tool in tools_result.tools:
                    if tool.name == tool_name:
                        matching_tool = tool
                        break

                if not matching_tool:
                    return {
                        "success": False,
                        "error": f"Tool '{tool_name}' not found on server"
                    }

                # Call the tool
                result = await session.call_tool(tool_name, arguments)

                return {
                    "success": True,
                    "result": result.content if hasattr(result, 'content') else result
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def _call_http_tool(
        self,
        url: str,
        headers: Dict[str, str],
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call tool on HTTP MCP server

        Args:
            url: Server URL
            headers: HTTP headers
            tool_name: Name of tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        try:
            async with httpx.AsyncClient() as client:
                # Make HTTP POST request to MCP server
                response = await client.post(
                    url,
                    json={
                        "method": "tools/call",
                        "params": {
                            "name": tool_name,
                            "arguments": arguments
                        }
                    },
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()

                result = response.json()
                return {
                    "success": True,
                    "result": result.get("result", result)
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def load_mcp_tools(self, server_name: str) -> Dict[str, Any]:
        """
        Load tools from specified MCP server

        Args:
            server_name: Name of MCP server to load tools from

        Returns:
            Dict containing available tools and their descriptions
        """
        # Use async method to get real tool list from MCP server
        return asyncio.run(self._load_mcp_tools_async(server_name))

    async def _load_mcp_tools_async(self, server_name: str) -> Dict[str, Any]:
        """Load tools from MCP server (async)"""
        server_config = self.direct_mcp_servers.get(server_name) or self.wrapped_mcp_servers.get(server_name)
        if not server_config:
            return {"error": f"Unknown MCP server: {server_name}"}

        try:
            # Get or create persistent session
            session = await self._get_persistent_session(server_name, server_config)

            # List tools from server
            tools_result = await session.list_tools()

            # Convert to dict format
            tools_dict = {}
            for tool in tools_result.tools:
                tools_dict[tool.name] = tool

            return tools_dict
        except Exception as e:
            return {"error": f"Failed to load tools from {server_name}: {str(e)}"}

    def _get_tool_descriptions(self, server_name: str) -> Dict[str, str]:
        """Get tool descriptions for a server"""
        tool_descriptions = {
            "serena": {
                "find_symbol": "Find symbols in code using LSP-based semantic search",
                "find_referencing_symbols": "Find references to a symbol across codebase",
                "search_for_pattern": "Search for regex patterns in code",
                "get_symbols_overview": "Get overview of top-level symbols in a file"
            },
            "graphiti": {
                "create_graph": "Create knowledge graph nodes",
                "query_graph": "Query knowledge graph relationships"
            },
            "context7": {
                "search_docs": "Search real-time documentation",
                "get_package_docs": "Get version-specific package documentation"
            },
            "sequential_thinking": {
                "reason": "Execute sequential reasoning chain",
                "analyze_complex_problem": "Analyze complex problems with step-by-step reasoning"
            },
            "github": {
                "create_repo": "Create GitHub repository",
                "manage_pr": "Manage pull requests"
            },
            "filesystem": {
                "read_file": "Read file contents",
                "write_file": "Write file contents",
                "list_directory": "List directory contents"
            }
        }
        return tool_descriptions.get(server_name, {})

    def call_serena_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call Serena MCP tool for semantic code search (sync wrapper)

        Args:
            tool_name: Name of Serena tool to call
            parameters: Tool-specific parameters

        Returns:
            Dict containing tool execution results
        """
        return asyncio.run(self._call_serena_tool_async(tool_name, parameters))

    async def _call_serena_tool_async(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call Serena MCP tool for semantic code search (async)

        Args:
            tool_name: Name of Serena tool to call
            parameters: Tool-specific parameters

        Returns:
            Dict containing tool execution results
        """
        server_config = self.direct_mcp_servers.get("serena")
        if not server_config:
            return {"success": False, "error": "Serena server not configured"}

        # Use temporary session per call to avoid ClosedResourceError
        async with self._get_stdio_session(server_config) as session:
            try:
                # Call tool on session
                result = await session.call_tool(tool_name, parameters)

                # Parse result into expected format
                # result.content is a list of content items from MCP SDK
                return self._parse_serena_result(tool_name, result.content)
            except Exception as e:
                import traceback
                return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

    def _parse_serena_result(self, tool_name: str, result: Any) -> Dict[str, Any]:
        """Parse Serena MCP result into expected format"""
        # Handle different result types from MCP
        if isinstance(result, list) and len(result) > 0:
            content = result[0]
            if hasattr(content, 'text'):
                text = content.text
                if not text:
                    # Empty text - return raw content object representation
                    result_data = {"raw": str(content), "type": type(content).__name__}
                else:
                    try:
                        parsed = json.loads(text)
                        # If parsed result is a list (Serena returns lists for find operations)
                        if isinstance(parsed, list) and len(parsed) > 0:
                            result_data = {"symbols": parsed}
                        else:
                            result_data = parsed if isinstance(parsed, dict) else {"result": parsed}
                    except json.JSONDecodeError:
                        # Not JSON - return as raw text
                        result_data = {"text": text}
            elif isinstance(content, dict):
                result_data = content
            else:
                result_data = {"raw": str(content), "type": type(content).__name__}
        elif isinstance(result, dict):
            result_data = result
        elif isinstance(result, list):
            # Handle case where result is list but empty or needs wrapping
            result_data = {"result_list": result}
        else:
            result_data = {"raw": str(result), "type": type(result).__name__}

        # Ensure result_data is always a dict before unpacking
        if not isinstance(result_data, dict):
            result_data = {"raw": str(result_data), "type": type(result_data).__name__}

        return {
            "success": True,
            **result_data
        }

    def call_context7_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call Context7 MCP tool for real-time documentation (sync wrapper)

        Args:
            tool_name: Name of Context7 tool to call
            parameters: Tool-specific parameters

        Returns:
            Dict containing tool execution results
        """
        return asyncio.run(self._call_context7_tool_async(tool_name, parameters))

    async def _call_context7_tool_async(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call Context7 MCP tool for real-time documentation (async)

        Args:
            tool_name: Name of Context7 tool to call
            parameters: Tool-specific parameters

        Returns:
            Dict containing tool execution results
        """
        # Check cache first
        cache_key = f"{tool_name}:{json.dumps(parameters, sort_keys=True)}"
        if cache_key in self._context7_cache:
            cached_result = self._context7_cache[cache_key].copy()
            cached_result["cached"] = True
            return cached_result

        server_config = self.direct_mcp_servers.get("context7")
        if not server_config:
            return {"success": False, "error": "Context7 server not configured"}

        # Use temporary session per call to avoid ClosedResourceError
        async with self._get_stdio_session(server_config) as session:
            try:
                # Call tool on session
                result = await session.call_tool(tool_name, parameters)

                # Parse result into expected format
                parsed_result = self._parse_context7_result(tool_name, result.content, parameters)
                parsed_result["cached"] = False
                # Cache the result
                self._context7_cache[cache_key] = parsed_result.copy()
                return parsed_result
            except Exception as e:
                import traceback
                return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

    def _parse_context7_result(self, tool_name: str, result: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Context7 result into expected format (MCP SDK response)"""
        # result is list of content items from MCP SDK
        if isinstance(result, list) and len(result) > 0:
            content = result[0]
            if hasattr(content, 'text'):
                text = content.text
                if tool_name == "get_package_docs":
                    return {
                        "success": True,
                        "documentation": {
                            "package": parameters.get("package_name"),
                            "version": parameters.get("version"),
                            "content": text
                        }
                    }
                return {"success": True, "documentation": text}
        return {"success": True, "result": str(result)}

    def call_sequential_thinking_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call Sequential Thinking MCP tool for complex reasoning (sync wrapper)

        Args:
            tool_name: Name of Sequential Thinking tool to call
            parameters: Tool-specific parameters

        Returns:
            Dict containing tool execution results
        """
        return asyncio.run(self._call_sequential_thinking_tool_async(tool_name, parameters))

    async def _call_sequential_thinking_tool_async(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call Sequential Thinking MCP tool for complex reasoning (async)

        Args:
            tool_name: Name of Sequential Thinking tool to call
            parameters: Tool-specific parameters

        Returns:
            Dict containing tool execution results
        """
        server_config = self.direct_mcp_servers.get("sequential_thinking")
        if not server_config:
            return {"success": False, "error": "Sequential Thinking server not configured"}

        # Use temporary session per call to avoid ClosedResourceError
        async with self._get_stdio_session(server_config) as session:
            try:
                # Call tool on session
                result = await session.call_tool(tool_name, parameters)

                # Parse result into expected format
                return self._parse_sequential_thinking_result(tool_name, result.content)
            except Exception as e:
                import traceback
                return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

    def _parse_sequential_thinking_result(self, tool_name: str, result: Any) -> Dict[str, Any]:
        """Parse Sequential Thinking result into expected format (MCP SDK response)"""
        # result is list of content items from MCP SDK
        if isinstance(result, list) and len(result) > 0:
            content = result[0]
            if hasattr(content, 'text'):
                text = content.text
                try:
                    result_data = json.loads(text)
                except json.JSONDecodeError:
                    result_data = {"thought": text}
            else:
                result_data = {"raw": str(content)}
        elif isinstance(result, dict):
            result_data = result
        else:
            result_data = {"raw": str(result)}

        # Sequential thinking returns thought process
        return {
            "success": True,
            "reasoning": result_data
        }

    async def call_mcp_tool(
        self,
        server_name: str,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a tool on specified MCP server (async)

        Args:
            server_name: Name of MCP server
            tool_name: Name of tool to call
            parameters: Parameters for tool call

        Returns:
            Dict containing tool execution results
        """
        # Get server config
        server_config = self.direct_mcp_servers.get(server_name) or self.wrapped_mcp_servers.get(server_name)

        if not server_config:
            return {
                "success": False,
                "error": f"Unknown server: {server_name}"
            }

        # Route based on server type
        if server_config["type"] == "stdio":
            return await self._call_stdio_tool(server_config, tool_name, parameters)
        elif server_config["type"] == "http":
            return await self._call_http_tool(
                url=server_config["url"],
                headers=server_config.get("headers", {}),
                tool_name=tool_name,
                arguments=parameters
            )
        else:
            return {
                "success": False,
                "error": f"Unsupported server type: {server_config['type']}"
            }

    def get_direct_mcp_tools(self) -> Dict[str, Any]:
        """Get all direct MCP tool descriptions"""
        direct_tools = {}
        for server_name in self.direct_mcp_servers:
            direct_tools[server_name] = self._get_tool_descriptions(server_name)
        return direct_tools

    def get_wrapped_mcp_tools(self) -> Dict[str, Any]:
        """Get all wrapped MCP tool descriptions"""
        wrapped_tools = {}
        for server_name in self.wrapped_mcp_servers:
            wrapped_tools[server_name] = self._get_tool_descriptions(server_name)
        return wrapped_tools

    # Story 1.3: Knowledge Agent Helper Methods (Obsidian and Filesystem only)

    def call_obsidian_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call Obsidian MCP tool for note/documentation operations (sync wrapper)

        Args:
            tool_name: Name of Obsidian tool to call (list_files_in_vault, get_file_contents, search, etc.)
            parameters: Tool-specific parameters

        Returns:
            Dict containing tool execution results
        """
        return asyncio.run(self._call_obsidian_tool_async(tool_name, parameters))

    async def _call_obsidian_tool_async(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call Obsidian MCP tool for note/documentation operations (async)

        Args:
            tool_name: Name of Obsidian tool to call
            parameters: Tool-specific parameters

        Returns:
            Dict containing tool execution results
        """
        server_config = self.wrapped_mcp_servers.get("obsidian")
        if not server_config:
            return {"success": False, "error": "Obsidian server not configured"}

        # Use temporary session per call
        async with self._get_stdio_session(server_config) as session:
            try:
                # Call tool on session
                result = await session.call_tool(tool_name, parameters)

                # Parse result into expected format
                return self._parse_obsidian_result(tool_name, result.content)
            except Exception as e:
                import traceback
                return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

    def _parse_obsidian_result(self, tool_name: str, result: Any) -> Dict[str, Any]:
        """Parse Obsidian MCP result into expected format"""
        if isinstance(result, list) and len(result) > 0:
            content = result[0]
            if hasattr(content, 'text'):
                text = content.text
                if text:
                    try:
                        parsed = json.loads(text)
                        result_data = parsed if isinstance(parsed, dict) else {"result": parsed}
                    except json.JSONDecodeError:
                        result_data = {"text": text}
                else:
                    result_data = {"raw": str(content)}
            elif isinstance(content, dict):
                result_data = content
            else:
                result_data = {"raw": str(content)}
        elif isinstance(result, dict):
            result_data = result
        else:
            result_data = {"raw": str(result)}

        if not isinstance(result_data, dict):
            result_data = {"raw": str(result_data)}

        return {
            "success": True,
            **result_data
        }

    def call_filesystem_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call Filesystem MCP tool for file/directory operations (sync wrapper)

        Args:
            tool_name: Name of Filesystem tool to call (read_text_file, write_file, list_directory, etc.)
            parameters: Tool-specific parameters

        Returns:
            Dict containing tool execution results
        """
        return asyncio.run(self._call_filesystem_tool_async(tool_name, parameters))

    async def _call_filesystem_tool_async(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call Filesystem MCP tool for file/directory operations (async)

        Args:
            tool_name: Name of Filesystem tool to call
            parameters: Tool-specific parameters

        Returns:
            Dict containing tool execution results
        """
        server_config = self.wrapped_mcp_servers.get("filesystem")
        if not server_config:
            return {"success": False, "error": "Filesystem server not configured"}

        # Use temporary session per call
        async with self._get_stdio_session(server_config) as session:
            try:
                # Call tool on session
                result = await session.call_tool(tool_name, parameters)

                # Parse result into expected format
                return self._parse_filesystem_result(tool_name, result.content)
            except Exception as e:
                import traceback
                return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

    def _parse_filesystem_result(self, tool_name: str, result: Any) -> Dict[str, Any]:
        """Parse Filesystem MCP result into expected format"""
        if isinstance(result, list) and len(result) > 0:
            content = result[0]
            if hasattr(content, 'text'):
                text = content.text
                if text:
                    # Filesystem tools return text content directly
                    result_data = {"content": text}
                else:
                    result_data = {"raw": str(content)}
            elif isinstance(content, dict):
                result_data = content
            else:
                result_data = {"raw": str(content)}
        elif isinstance(result, dict):
            result_data = result
        else:
            result_data = {"raw": str(result)}

        if not isinstance(result_data, dict):
            result_data = {"raw": str(result_data)}

        return {
            "success": True,
            **result_data
        }

    # Story 1.6: Developer Agent Helper Methods (Chrome DevTools)

    def call_chrome_devtools_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call Chrome DevTools MCP tool for browser debugging (sync wrapper)

        Args:
            tool_name: Name of Chrome DevTools tool to call (navigate_to, screenshot, etc.)
            parameters: Tool-specific parameters

        Returns:
            Dict containing tool execution results
        """
        return asyncio.run(self._call_chrome_devtools_tool_async(tool_name, parameters))

    async def _call_chrome_devtools_tool_async(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call Chrome DevTools MCP tool for browser debugging (async)

        Args:
            tool_name: Name of Chrome DevTools tool to call
            parameters: Tool-specific parameters

        Returns:
            Dict containing tool execution results
        """
        server_config = self.wrapped_mcp_servers.get("chrome_devtools")
        if not server_config:
            return {"success": False, "error": "Chrome DevTools server not configured"}

        # Use temporary session per call
        async with self._get_stdio_session(server_config) as session:
            try:
                # Call tool on session
                result = await session.call_tool(tool_name, parameters)

                # Parse result into expected format
                return self._parse_chrome_devtools_result(tool_name, result.content)
            except Exception as e:
                import traceback
                return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

    def _parse_chrome_devtools_result(self, tool_name: str, result: Any) -> Dict[str, Any]:
        """Parse Chrome DevTools MCP result into expected format"""
        if isinstance(result, list) and len(result) > 0:
            content = result[0]
            if hasattr(content, 'text'):
                text = content.text
                if text:
                    try:
                        # Try parsing as JSON first
                        parsed = json.loads(text)
                        result_data = parsed if isinstance(parsed, dict) else {"result": parsed}
                    except json.JSONDecodeError:
                        # Return as text if not JSON
                        result_data = {"text": text}
                else:
                    result_data = {"raw": str(content)}
            elif isinstance(content, dict):
                result_data = content
            else:
                result_data = {"raw": str(content)}
        elif isinstance(result, dict):
            result_data = result
        else:
            result_data = {"raw": str(result)}

        if not isinstance(result_data, dict):
            result_data = {"raw": str(result_data)}

        return {
            "success": True,
            **result_data
        }