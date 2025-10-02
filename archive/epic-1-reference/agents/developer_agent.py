"""
Developer Agent - Code implementation and debugging

Responsibilities:
- Browser debugging via Chrome DevTools MCP
- Code execution and testing
- File operations and code generation
- Implementation coordination with other agents
"""

from typing import List, Dict, Any, Optional
from .base_agent import BaseAgent


class DeveloperAgent(BaseAgent):
    """Developer agent for code implementation and debugging"""

    def __init__(self, mcp_bridge=None):
        super().__init__("Developer", "Implementation Specialist", agent_id="developer")
        self.mcp_bridge = mcp_bridge


    def get_available_tools(self) -> List[str]:
        """Return implementation and debugging tools"""
        return self._tools.copy()

    def launch_browser(self, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Launch browser and optionally navigate to URL

        Args:
            url: URL to navigate to (required by Chrome DevTools new_page)

        Returns:
            Dict with launch results
        """
        if not self.mcp_bridge:
            return {
                "success": False,
                "error": "MCPBridge not initialized"
            }

        # Default to about:blank if no URL provided
        target_url = url or "about:blank"

        # Create new page with URL
        result = self.mcp_bridge.call_chrome_devtools_tool(
            tool_name="new_page",
            parameters={"url": target_url}
        )

        if not result.get("success"):
            return result

        return {
            "success": True,
            "message": f"Browser launched and navigated to {target_url}"
        }

    def inspect_page(self) -> Dict[str, Any]:
        """
        Take snapshot of current page for inspection

        Returns:
            Dict with page snapshot
        """
        if not self.mcp_bridge:
            return {
                "success": False,
                "error": "MCPBridge not initialized"
            }

        return self.mcp_bridge.call_chrome_devtools_tool(
            tool_name="take_snapshot",
            parameters={}
        )

    def debug_console(self) -> Dict[str, Any]:
        """
        Get console messages from current page

        Returns:
            Dict with console messages
        """
        if not self.mcp_bridge:
            return {
                "success": False,
                "error": "MCPBridge not initialized"
            }

        return self.mcp_bridge.call_chrome_devtools_tool(
            tool_name="list_console_messages",
            parameters={}
        )

    def take_screenshot(self) -> Dict[str, Any]:
        """
        Take screenshot of current page

        Returns:
            Dict with screenshot data
        """
        if not self.mcp_bridge:
            return {
                "success": False,
                "error": "MCPBridge not initialized"
            }

        return self.mcp_bridge.call_chrome_devtools_tool(
            tool_name="take_screenshot",
            parameters={}
        )

    def evaluate_javascript(self, script: str) -> Dict[str, Any]:
        """
        Execute JavaScript in current page context

        Args:
            script: JavaScript code to execute

        Returns:
            Dict with execution result
        """
        if not self.mcp_bridge:
            return {
                "success": False,
                "error": "MCPBridge not initialized"
            }

        return self.mcp_bridge.call_chrome_devtools_tool(
            tool_name="evaluate_script",
            parameters={"functionDeclaration": script}
        )

    def start_performance_trace(self) -> Dict[str, Any]:
        """
        Start performance profiling trace

        Returns:
            Dict with trace start confirmation
        """
        if not self.mcp_bridge:
            return {
                "success": False,
                "error": "MCPBridge not initialized"
            }

        return self.mcp_bridge.call_chrome_devtools_tool(
            tool_name="performance_start_trace",
            parameters={}
        )

    def stop_performance_trace(self) -> Dict[str, Any]:
        """
        Stop performance profiling trace and get results

        Returns:
            Dict with performance metrics
        """
        if not self.mcp_bridge:
            return {
                "success": False,
                "error": "MCPBridge not initialized"
            }

        return self.mcp_bridge.call_chrome_devtools_tool(
            tool_name="performance_stop_trace",
            parameters={}
        )

    def process_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process development implementation tasks

        Args:
            task_description: Description of development task
            context: Current development context

        Returns:
            Dict containing implementation results
        """
        operation = context.get("operation", "")
        results = {
            "agent": "developer",
            "task_processed": task_description,
            "tools_used": self._tools,
            "implementation_complete": True,
            "code_generated": [],
            "tests_created": [],
            "debugging_sessions": []
        }

        # Handle browser debugging operations
        if operation == "inspect_page":
            url = context.get("url", "https://example.com")
            launch_result = self.launch_browser(url)
            if launch_result.get("success"):
                inspect_result = self.inspect_page()
                results["debugging_sessions"].append({
                    "operation": "inspect_page",
                    "result": inspect_result
                })

        return results