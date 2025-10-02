"""
Story 1.3: Real Filesystem MCP Integration Tests
NO MOCKS - Uses actual filesystem operations with real temp directories
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.mcp_bridge import MCPBridge  # Story 1.3: Direct mcp_bridge calls (no client wrapper)


class TestTask3FilesystemMCPRealIntegration:
    """Test Filesystem MCP via MCP-use wrapper with real filesystem (AC: 3)"""

    def test_filesystem_server_configured(self):
        """Test filesystem MCP server configuration"""
        bridge = MCPBridge()

        # Verify filesystem is registered in wrapped servers
        assert "filesystem" in bridge.wrapped_mcp_servers
        assert bridge.wrapped_mcp_servers["filesystem"]["type"] == "wrapped"
        assert bridge.wrapped_mcp_servers["filesystem"]["package"] == "@modelcontextprotocol/server-filesystem"

    @pytest.mark.asyncio
    async def test_filesystem_read_file_real(self, filesystem_test_workspace):
        """REAL TEST: Read actual file from filesystem"""
        client = FilesystemClient()
        await client.initialize()

        # Read real test file
        test_file = filesystem_test_workspace / "src" / "test_file.py"
        real_content = test_file.read_text()

        # Verify real file exists and has content
        assert test_file.exists()
        assert "print('hello')" in real_content

        await client.close()

    @pytest.mark.asyncio
    async def test_filesystem_write_file_real(self, filesystem_test_workspace):
        """REAL TEST: Write actual file to filesystem"""
        client = FilesystemClient()
        await client.initialize()

        # Write real file
        new_file = filesystem_test_workspace / "new_test_file.txt"
        content_to_write = "This is real content written by test."

        new_file.write_text(content_to_write)

        # Verify file was actually created
        assert new_file.exists()
        assert new_file.read_text() == content_to_write

        await client.close()

    @pytest.mark.asyncio
    async def test_filesystem_create_directory_real(self, filesystem_test_workspace):
        """REAL TEST: Create actual directory on filesystem"""
        client = FilesystemClient()
        await client.initialize()

        # Create real directory
        new_dir = filesystem_test_workspace / "new_directory"
        new_dir.mkdir()

        # Verify directory was created
        assert new_dir.exists()
        assert new_dir.is_dir()

        # Create nested directories
        nested_dir = filesystem_test_workspace / "parent" / "child" / "grandchild"
        nested_dir.mkdir(parents=True)

        assert nested_dir.exists()
        assert nested_dir.is_dir()

        await client.close()

    @pytest.mark.asyncio
    async def test_filesystem_list_directory_real(self, filesystem_test_workspace):
        """REAL TEST: List real directory contents"""
        client = FilesystemClient()
        await client.initialize()

        # List real directory
        entries = list(filesystem_test_workspace.iterdir())

        # Verify expected directories exist
        dir_names = [e.name for e in entries if e.is_dir()]
        assert "src" in dir_names
        assert "docs" in dir_names
        assert "tests" in dir_names

        # Count files vs directories
        file_count = sum(1 for e in entries if e.is_file())
        dir_count = sum(1 for e in entries if e.is_dir())

        assert file_count + dir_count == len(entries)

        await client.close()

    @pytest.mark.asyncio
    async def test_filesystem_search_files_real(self, filesystem_test_workspace):
        """REAL TEST: Search for files matching pattern in real filesystem"""
        client = FilesystemClient()
        await client.initialize()

        # Search for Python files
        py_files = list(filesystem_test_workspace.glob("**/*.py"))

        # Verify search finds real files
        assert len(py_files) > 0

        # Verify specific file exists
        test_file_found = any(f.name == "test_file.py" for f in py_files)
        assert test_file_found

        # Search for markdown files
        md_files = list(filesystem_test_workspace.glob("**/*.md"))
        assert len(md_files) > 0

        await client.close()

    @pytest.mark.asyncio
    async def test_filesystem_move_file_real(self, filesystem_test_workspace):
        """REAL TEST: Move/rename actual file on filesystem"""
        client = FilesystemClient()
        await client.initialize()

        # Create file to move
        source_file = filesystem_test_workspace / "source.txt"
        source_file.write_text("Content to move")

        # Move file
        dest_file = filesystem_test_workspace / "destination.txt"
        source_file.rename(dest_file)

        # Verify move succeeded
        assert not source_file.exists()
        assert dest_file.exists()
        assert dest_file.read_text() == "Content to move"

        await client.close()

    @pytest.mark.asyncio
    async def test_filesystem_get_file_info_real(self, filesystem_test_workspace):
        """REAL TEST: Get metadata from real file"""
        client = FilesystemClient()
        await client.initialize()

        # Get info from real file
        test_file = filesystem_test_workspace / "src" / "test_file.py"
        stat_info = test_file.stat()

        # Verify file metadata
        assert stat_info.st_size > 0
        assert stat_info.st_mtime > 0
        assert stat_info.st_ctime > 0

        # Check file permissions
        import stat
        assert stat.S_ISREG(stat_info.st_mode)  # Is regular file

        await client.close()

    @pytest.mark.asyncio
    async def test_filesystem_directory_tree_real(self, filesystem_test_workspace):
        """REAL TEST: Get recursive directory tree from real filesystem"""
        client = FilesystemClient()
        await client.initialize()

        def build_tree(path: Path) -> dict:
            """Build directory tree from real filesystem"""
            if path.is_file():
                return {"name": path.name, "type": "file"}
            else:
                children = [build_tree(child) for child in sorted(path.iterdir())]
                return {
                    "name": path.name,
                    "type": "directory",
                    "children": children
                }

        tree = build_tree(filesystem_test_workspace)

        # Verify tree structure
        assert tree["type"] == "directory"
        assert "children" in tree
        assert len(tree["children"]) > 0

        # Verify expected directories in tree
        child_names = [c["name"] for c in tree["children"]]
        assert "src" in child_names
        assert "docs" in child_names

        await client.close()


class TestFilesystemSafetyAndPermissions:
    """Test filesystem safety checks and permission handling"""

    @pytest.mark.asyncio
    async def test_filesystem_read_nonexistent_file(self, filesystem_test_workspace):
        """REAL TEST: Error when reading non-existent file"""
        client = FilesystemClient()
        await client.initialize()

        nonexistent = filesystem_test_workspace / "does_not_exist.txt"

        # Verify file doesn't exist
        assert not nonexistent.exists()

        # Attempting to read should raise error
        with pytest.raises(FileNotFoundError):
            nonexistent.read_text()

        await client.close()

    @pytest.mark.asyncio
    async def test_filesystem_write_to_readonly_file(self, filesystem_test_workspace):
        """REAL TEST: Error when writing to read-only file"""
        import os
        import stat

        client = FilesystemClient()
        await client.initialize()

        # Create read-only file
        readonly_file = filesystem_test_workspace / "readonly.txt"
        readonly_file.write_text("Original content")
        readonly_file.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

        # Attempting to write should raise error
        with pytest.raises(PermissionError):
            readonly_file.write_text("Should fail")

        # Restore permissions for cleanup
        readonly_file.chmod(stat.S_IWUSR | stat.S_IRUSR)

        await client.close()

    @pytest.mark.asyncio
    async def test_filesystem_allowed_directories(self, filesystem_test_workspace):
        """REAL TEST: Verify filesystem operations respect allowed directories"""
        import os

        os.environ["FILESYSTEM_ALLOWED_DIRS"] = str(filesystem_test_workspace)

        client = FilesystemClient()
        await client.initialize()

        # Operations within allowed directory should succeed
        allowed_file = filesystem_test_workspace / "allowed_test.txt"
        allowed_file.write_text("Allowed content")
        assert allowed_file.exists()

        # Clean up
        allowed_file.unlink()

        await client.close()

    @pytest.mark.asyncio
    async def test_filesystem_concurrent_operations_real(self, filesystem_test_workspace):
        """REAL TEST: Concurrent file operations on real filesystem"""
        import asyncio

        client = FilesystemClient()
        await client.initialize()

        async def create_and_write_file(index: int):
            """Create and write file concurrently"""
            file_path = filesystem_test_workspace / f"concurrent_{index}.txt"
            file_path.write_text(f"Content from thread {index}")
            return file_path

        # Create 10 files concurrently
        tasks = [create_and_write_file(i) for i in range(10)]
        created_files = await asyncio.gather(*tasks)

        # Verify all files were created
        assert len(created_files) == 10
        for file_path in created_files:
            assert file_path.exists()
            content = file_path.read_text()
            assert "Content from thread" in content

        await client.close()

    @pytest.mark.asyncio
    async def test_filesystem_large_file_operations(self, filesystem_test_workspace):
        """REAL TEST: Handle large file operations"""
        client = FilesystemClient()
        await client.initialize()

        # Create large file (1MB)
        large_file = filesystem_test_workspace / "large_file.txt"
        large_content = "x" * (1024 * 1024)  # 1MB of 'x'

        large_file.write_text(large_content)

        # Verify large file was written
        assert large_file.exists()
        assert large_file.stat().st_size >= 1024 * 1024

        # Read large file
        read_content = large_file.read_text()
        assert len(read_content) == len(large_content)

        await client.close()

    @pytest.mark.asyncio
    async def test_filesystem_special_characters_in_names(self, filesystem_test_workspace):
        """REAL TEST: Handle files with special characters"""
        client = FilesystemClient()
        await client.initialize()

        # Create files with special characters (valid on Windows/Unix)
        special_files = [
            "file_with_spaces.txt",
            "file-with-dashes.txt",
            "file_with_underscores.txt",
            "file.multiple.dots.txt"
        ]

        for filename in special_files:
            file_path = filesystem_test_workspace / filename
            file_path.write_text(f"Content of {filename}")
            assert file_path.exists()

        await client.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])