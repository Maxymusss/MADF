"""
Story 1.1: Real Developer Agent Tests
NO MOCKS - Tests with real Chrome DevTools MCP and file operations
"""

import pytest
import os
from pathlib import Path
import tempfile


@pytest.fixture
async def real_developer_agent():
    """Initialize Developer with real MCP clients"""
    from src.agents.developer_agent import DeveloperAgent

    agent = DeveloperAgent()
    await agent.initialize_real_mcp_clients()

    yield agent

    await agent.cleanup()


@pytest.fixture
def temp_workspace():
    """Create temporary workspace for file operations"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestRealDeveloperChromeDevTools:
    """Real Chrome DevTools MCP integration tests"""

    @pytest.mark.asyncio
    async def test_chrome_devtools_client_initialization(self, real_developer_agent):
        """REAL TEST: Verify Chrome DevTools MCP client initializes"""
        assert real_developer_agent.chrome_devtools_client is not None
        assert real_developer_agent.chrome_devtools_client._initialized

    @pytest.mark.asyncio
    async def test_connect_to_browser_real(self, real_developer_agent):
        """REAL TEST: Connect to Chrome browser via DevTools"""
        # Requires Chrome running with --remote-debugging-port=9222
        try:
            result = await real_developer_agent.connect_to_browser(
                port=9222
            )

            assert result["connected"] == True
            assert "browser_version" in result
        except Exception as e:
            # Allow test to pass if Chrome not running with debug port
            if "connect" in str(e).lower() or "refused" in str(e).lower():
                pytest.skip("Chrome not running with remote debugging port")
            raise

    @pytest.mark.asyncio
    async def test_execute_javascript_real(self, real_developer_agent):
        """REAL TEST: Execute JavaScript in browser via DevTools"""
        # Requires active browser connection
        try:
            await real_developer_agent.connect_to_browser(port=9222)

            result = await real_developer_agent.execute_javascript(
                script="return 2 + 2;"
            )

            assert result["success"] == True
            assert result["result"] == 4
        except Exception as e:
            if "connect" in str(e).lower():
                pytest.skip("Chrome not available for testing")
            raise

    @pytest.mark.asyncio
    async def test_inspect_dom_real(self, real_developer_agent):
        """REAL TEST: Inspect DOM elements via DevTools"""
        try:
            await real_developer_agent.connect_to_browser(port=9222)

            # Navigate to simple page
            await real_developer_agent.navigate_to("about:blank")

            # Inspect DOM
            result = await real_developer_agent.inspect_dom(
                selector="body"
            )

            assert result["success"] == True
            assert "element" in result
        except Exception as e:
            if "connect" in str(e).lower():
                pytest.skip("Chrome not available for testing")
            raise


class TestRealDeveloperFileOperations:
    """Real file operation tests"""

    @pytest.mark.asyncio
    async def test_create_file_real(self, real_developer_agent, temp_workspace):
        """REAL TEST: Create file with real filesystem"""
        file_path = temp_workspace / "test_agent.py"

        content = '''"""Test Agent Module"""
from typing import List

class TestAgent:
    def __init__(self, name: str):
        self.name = name

    def get_tools(self) -> List[str]:
        return ["tool1", "tool2"]
'''

        result = await real_developer_agent.create_file(
            path=str(file_path),
            content=content
        )

        # Verify file created
        assert result["success"] == True
        assert file_path.exists()
        assert file_path.read_text() == content

    @pytest.mark.asyncio
    async def test_edit_file_real(self, real_developer_agent, temp_workspace):
        """REAL TEST: Edit existing file with real filesystem"""
        file_path = temp_workspace / "config.py"

        # Create initial file
        initial_content = "DEBUG = False\nLOG_LEVEL = 'INFO'"
        file_path.write_text(initial_content)

        # Edit file
        result = await real_developer_agent.edit_file(
            path=str(file_path),
            old_content="DEBUG = False",
            new_content="DEBUG = True"
        )

        # Verify edit applied
        assert result["success"] == True
        updated_content = file_path.read_text()
        assert "DEBUG = True" in updated_content
        assert "DEBUG = False" not in updated_content

    @pytest.mark.asyncio
    async def test_read_file_real(self, real_developer_agent, temp_workspace):
        """REAL TEST: Read file from real filesystem"""
        file_path = temp_workspace / "data.json"

        # Create test file
        test_data = '{"agent": "developer", "tools": ["chrome", "files"]}'
        file_path.write_text(test_data)

        # Read file
        result = await real_developer_agent.read_file(str(file_path))

        # Verify content read correctly
        assert result["success"] == True
        assert result["content"] == test_data

    @pytest.mark.asyncio
    async def test_execute_code_real(self, real_developer_agent, temp_workspace):
        """REAL TEST: Execute Python code with real runtime"""
        code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
"""

        execution_result = await real_developer_agent.execute_python_code(
            code=code,
            capture_output=True
        )

        # Verify execution
        assert execution_result["success"] == True
        assert "result" in execution_result["variables"]
        assert execution_result["variables"]["result"] == 55


class TestRealDeveloperWorkflow:
    """Real development workflow integration tests"""

    @pytest.mark.asyncio
    async def test_implement_feature_real(self, real_developer_agent, temp_workspace):
        """REAL TEST: Complete feature implementation workflow"""
        # Step 1: Create module file
        module_path = temp_workspace / "message_handler.py"
        module_content = '''"""Message Handler Module"""
from typing import Dict, Any

class MessageHandler:
    def __init__(self):
        self.messages = []

    def add_message(self, role: str, content: str) -> Dict[str, Any]:
        message = {"role": role, "content": content}
        self.messages.append(message)
        return message

    def get_messages(self) -> list:
        return self.messages
'''

        create_result = await real_developer_agent.create_file(
            path=str(module_path),
            content=module_content
        )
        assert create_result["success"]

        # Step 2: Create test file
        test_path = temp_workspace / "test_message_handler.py"
        test_content = '''"""Test Message Handler"""
import pytest
from message_handler import MessageHandler

def test_add_message():
    handler = MessageHandler()
    result = handler.add_message("user", "Hello")
    assert result["role"] == "user"
    assert result["content"] == "Hello"

def test_get_messages():
    handler = MessageHandler()
    handler.add_message("user", "Hi")
    handler.add_message("assistant", "Hello")
    messages = handler.get_messages()
    assert len(messages) == 2
'''

        test_create_result = await real_developer_agent.create_file(
            path=str(test_path),
            content=test_content
        )
        assert test_create_result["success"]

        # Step 3: Verify both files exist
        assert module_path.exists()
        assert test_path.exists()

        # Verify implementation workflow complete
        workflow_result = {
            "module_created": module_path.exists(),
            "tests_created": test_path.exists(),
            "files_count": len(list(temp_workspace.glob("*.py")))
        }

        assert workflow_result["module_created"]
        assert workflow_result["tests_created"]
        assert workflow_result["files_count"] == 2

    @pytest.mark.asyncio
    async def test_debug_with_devtools_real(self, real_developer_agent):
        """REAL TEST: Debug code using Chrome DevTools"""
        try:
            await real_developer_agent.connect_to_browser(port=9222)

            # Set up debugging context
            debug_script = """
function testFunction(x, y) {
    debugger;
    return x + y;
}
testFunction(5, 10);
"""

            result = await real_developer_agent.debug_with_breakpoint(
                script=debug_script,
                breakpoint_line=3
            )

            assert result["success"] == True
            assert "debug_state" in result
        except Exception as e:
            if "connect" in str(e).lower():
                pytest.skip("Chrome not available for debugging tests")
            raise

    @pytest.mark.asyncio
    async def test_delegate_to_validator_real(self, real_developer_agent, temp_workspace):
        """REAL TEST: Developer delegates code to Validator"""
        # Create implementation
        impl_path = temp_workspace / "calculator.py"
        impl_content = '''def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
'''

        await real_developer_agent.create_file(
            path=str(impl_path),
            content=impl_content
        )

        # Delegate to Validator
        delegation = await real_developer_agent.delegate_to_agent(
            target_agent="validator",
            task="Test and validate calculator implementation",
            context={
                "file_path": str(impl_path),
                "functions": ["add", "multiply"]
            }
        )

        # Verify delegation
        assert delegation["target_agent"] == "validator"
        assert delegation["status"] == "delegated"
        assert "context" in delegation


class TestRealDeveloperErrorHandling:
    """Real error handling tests"""

    @pytest.mark.asyncio
    async def test_file_permission_error_handling(self, real_developer_agent):
        """REAL TEST: Handle file permission errors gracefully"""
        # Try to write to protected location (Windows system directory)
        protected_path = "C:\\Windows\\System32\\test_forbidden.txt"

        result = await real_developer_agent.create_file(
            path=protected_path,
            content="This should fail"
        )

        # Should handle permission error gracefully
        assert result["success"] == False
        assert "permission" in str(result.get("error", "")).lower() or \
               "denied" in str(result.get("error", "")).lower()

    @pytest.mark.asyncio
    async def test_invalid_code_execution_handling(self, real_developer_agent):
        """REAL TEST: Handle invalid Python code execution"""
        invalid_code = "def broken_function(\n    return 'missing closing paren'"

        result = await real_developer_agent.execute_python_code(
            code=invalid_code,
            capture_output=True
        )

        # Should capture syntax error
        assert result["success"] == False
        assert "error" in result
        assert "syntax" in str(result["error"]).lower()

    @pytest.mark.asyncio
    async def test_browser_connection_failure_handling(self, real_developer_agent):
        """REAL TEST: Handle browser connection failures gracefully"""
        result = await real_developer_agent.connect_to_browser(
            port=9999  # Invalid port
        )

        # Should handle connection failure
        assert result["connected"] == False
        assert "error" in result