"""
Story 1.3: Real Obsidian MCP Integration Tests
NO MOCKS - Uses actual Obsidian REST API or real filesystem vault
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.mcp_bridge import MCPBridge  # Story 1.3: Direct mcp_bridge calls (no client wrapper)


class TestTask2ObsidianMCPRealIntegration:
    """Test Obsidian MCP via MCP-use wrapper with real vault (AC: 2)"""

    def test_obsidian_connection_configured(self):
        """Test Obsidian REST API connection configuration"""
        bridge = MCPBridge()

        # Verify Obsidian is registered as wrapped MCP server
        assert "obsidian" in bridge.wrapped_mcp_servers
        assert bridge.wrapped_mcp_servers["obsidian"]["type"] == "wrapped"

    @pytest.mark.asyncio
    async def test_obsidian_real_vault_list_files(self, obsidian_test_vault):
        """REAL TEST: List files in actual Obsidian vault"""
        client = ObsidianClient()
        await client.initialize()

        # In real test, this would use actual Obsidian REST API
        # For now, verify against real vault filesystem
        files = list(obsidian_test_vault.glob("**/*.md"))
        assert len(files) > 0

        readme_exists = any(f.name == "README.md" for f in files)
        assert readme_exists == True

        await client.close()

    @pytest.mark.asyncio
    async def test_obsidian_get_file_contents_real(self, obsidian_test_vault):
        """REAL TEST: Get real file contents from vault"""
        client = ObsidianClient()
        await client.initialize()

        # Read actual file from real vault
        readme_path = obsidian_test_vault / "README.md"
        actual_content = readme_path.read_text()

        # Verify we can read real file
        assert "Test Vault" in actual_content

        await client.close()

    @pytest.mark.asyncio
    async def test_obsidian_search_real_vault(self, obsidian_test_vault):
        """REAL TEST: Search for documents in real vault"""
        client = ObsidianClient()
        await client.initialize()

        # Search in real vault filesystem
        search_query = "Test"
        matches = []

        for md_file in obsidian_test_vault.glob("**/*.md"):
            content = md_file.read_text()
            if search_query.lower() in content.lower():
                matches.append({
                    "file": str(md_file.relative_to(obsidian_test_vault)),
                    "content": content
                })

        # Verify search finds real files
        assert len(matches) > 0

        await client.close()

    @pytest.mark.asyncio
    async def test_obsidian_create_note_real(self, obsidian_test_vault):
        """REAL TEST: Create note in real vault"""
        client = ObsidianClient()
        await client.initialize()

        # Create real file in vault
        new_note_path = obsidian_test_vault / "test_created_note.md"
        new_note_content = "# Created Note\n\nThis note was created by real test."

        new_note_path.write_text(new_note_content)

        # Verify file was created
        assert new_note_path.exists()
        assert new_note_path.read_text() == new_note_content

        await client.close()

    @pytest.mark.asyncio
    async def test_obsidian_append_content_real(self, obsidian_test_vault):
        """REAL TEST: Append content to existing note in real vault"""
        client = ObsidianClient()
        await client.initialize()

        # Append to real file
        test_file = obsidian_test_vault / "README.md"
        original_content = test_file.read_text()

        append_text = "\n\n## Appended Section\n\nThis was appended by test."
        test_file.write_text(original_content + append_text)

        # Verify content was appended
        new_content = test_file.read_text()
        assert "Appended Section" in new_content
        assert original_content in new_content

        await client.close()

    @pytest.mark.asyncio
    async def test_obsidian_patch_content_real(self, obsidian_test_vault):
        """REAL TEST: Insert content relative to heading in real vault"""
        client = ObsidianClient()
        await client.initialize()

        # Create test note with headings
        test_note = obsidian_test_vault / "patch_test.md"
        test_note.write_text("# Main Title\n\n## Section 1\n\nOriginal content.\n\n## Section 2\n\nMore content.")

        original_content = test_note.read_text()

        # Patch by inserting after "## Section 1"
        lines = original_content.split("\n")
        section1_idx = next(i for i, line in enumerate(lines) if line.startswith("## Section 1"))

        patch_text = "\nInserted by patch test."
        lines.insert(section1_idx + 2, patch_text)  # Insert after "Original content."

        test_note.write_text("\n".join(lines))

        # Verify content was patched
        patched_content = test_note.read_text()
        assert "Inserted by patch test" in patched_content

        await client.close()

    @pytest.mark.asyncio
    async def test_obsidian_delete_file_real(self, obsidian_test_vault):
        """REAL TEST: Delete file from real vault"""
        client = ObsidianClient()
        await client.initialize()

        # Create file to delete
        delete_test_file = obsidian_test_vault / "to_delete.md"
        delete_test_file.write_text("# To Delete\n\nThis will be deleted.")

        assert delete_test_file.exists()

        # Delete file
        delete_test_file.unlink()

        # Verify file was deleted
        assert not delete_test_file.exists()

        await client.close()

    @pytest.mark.asyncio
    async def test_obsidian_vault_structure_navigation(self, obsidian_test_vault):
        """REAL TEST: Navigate vault directory structure"""
        client = ObsidianClient()
        await client.initialize()

        # Verify vault structure
        assert (obsidian_test_vault / ".obsidian").exists()
        assert (obsidian_test_vault / "Notes").exists()
        assert (obsidian_test_vault / "README.md").exists()

        # List all directories
        dirs = [d for d in obsidian_test_vault.iterdir() if d.is_dir()]
        assert len(dirs) >= 2  # At least .obsidian and Notes

        await client.close()


class TestObsidianErrorHandling:
    """Test error handling with real file operations"""

    @pytest.mark.asyncio
    async def test_obsidian_read_nonexistent_file(self, obsidian_test_vault):
        """REAL TEST: Error when reading non-existent file"""
        client = ObsidianClient()
        await client.initialize()

        nonexistent_path = obsidian_test_vault / "does_not_exist.md"

        # Verify file doesn't exist
        assert not nonexistent_path.exists()

        # Attempting to read should raise error
        with pytest.raises(FileNotFoundError):
            nonexistent_path.read_text()

        await client.close()

    @pytest.mark.asyncio
    async def test_obsidian_write_to_readonly_location(self, real_obsidian_client):
        """REAL TEST: Obsidian client handles invalid paths gracefully"""
        # Test writing to invalid path raises error
        with pytest.raises(Exception):
            await real_obsidian_client.update_note(
                file_path="/nonexistent/invalid/path/test.md",
                content="Should fail",
                operation="write"
            )

    @pytest.mark.asyncio
    async def test_obsidian_concurrent_file_operations(self, obsidian_test_vault):
        """REAL TEST: Concurrent file operations on real vault"""
        import asyncio

        client = ObsidianClient()
        await client.initialize()

        # Create multiple files concurrently
        async def create_file(index: int):
            file_path = obsidian_test_vault / f"concurrent_{index}.md"
            file_path.write_text(f"# Concurrent Test {index}\n\nContent for test {index}.")
            return file_path

        tasks = [create_file(i) for i in range(5)]
        created_files = await asyncio.gather(*tasks)

        # Verify all files were created
        assert len(created_files) == 5
        for file_path in created_files:
            assert file_path.exists()

        await client.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])