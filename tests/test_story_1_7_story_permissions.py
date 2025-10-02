"""
Tests for Story 1.7 - Story File Permission Enforcement

Tests StoryFileManager enforces section-level permissions correctly
"""

import pytest
from pathlib import Path
import tempfile
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.story_file_manager import StoryFileManager, StorySection, EditPermission


# Sample story file content for testing
SAMPLE_STORY = """# Story 1.X - Sample Story

## User Story

As a developer, I want to implement feature X

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Tasks

### Task 1: Setup

- Subtask 1.1
- Subtask 1.2

## Dev Agent Record

_Implementation notes by developer agent_

### Implementation Notes

Code changes made:
- File A modified
- File B created

## QA Results

_Test results by validator agent_

### Test Results

All tests passing:
- Unit tests: 10/10 [OK]
- Integration tests: 5/5 [OK]

## Completion Notes

Story completed successfully
"""


class TestStoryFileParsing:
    """Test story file parsing into sections"""

    def test_parse_story_sections(self):
        """Should parse story file into sections correctly"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(SAMPLE_STORY)
            f.flush()
            file_path = Path(f.name)

        try:
            manager = StoryFileManager()
            sections = manager.parse_story_file(file_path)

            # Should find all level-2 headings
            section_names = [s.name for s in sections]
            assert "User Story" in section_names
            assert "Acceptance Criteria" in section_names
            assert "Tasks" in section_names
            assert "Dev Agent Record" in section_names
            assert "QA Results" in section_names
            assert "Completion Notes" in section_names

        finally:
            file_path.unlink()

    def test_section_content_capture(self):
        """Should capture section content correctly"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(SAMPLE_STORY)
            f.flush()
            file_path = Path(f.name)

        try:
            manager = StoryFileManager()
            sections = manager.parse_story_file(file_path)

            # Find "Acceptance Criteria" section
            ac_section = next(s for s in sections if s.name == "Acceptance Criteria")
            assert "Criterion 1" in ac_section.content
            assert "Criterion 2" in ac_section.content

        finally:
            file_path.unlink()


class TestDeveloperPermissions:
    """Test Developer agent permissions"""

    def test_developer_can_edit_dev_agent_record(self):
        """Developer should be allowed to edit Dev Agent Record"""
        manager = StoryFileManager()
        permission = manager.validate_edit(
            agent_id="developer",
            section_name="Dev Agent Record"
        )

        assert permission.allowed == True
        assert "allowed" in permission.reason.lower()

    def test_developer_can_edit_tasks(self):
        """Developer should be allowed to edit Tasks section"""
        manager = StoryFileManager()
        permission = manager.validate_edit(
            agent_id="developer",
            section_name="Tasks"
        )

        assert permission.allowed == True

    def test_developer_cannot_edit_acceptance_criteria(self):
        """Developer should NOT be allowed to edit Acceptance Criteria"""
        manager = StoryFileManager()
        permission = manager.validate_edit(
            agent_id="developer",
            section_name="Acceptance Criteria"
        )

        assert permission.allowed == False
        assert "forbidden" in permission.reason.lower()

    def test_developer_cannot_edit_qa_results(self):
        """Developer should NOT be allowed to edit QA Results"""
        manager = StoryFileManager()
        permission = manager.validate_edit(
            agent_id="developer",
            section_name="QA Results"
        )

        assert permission.allowed == False

    def test_developer_get_editable_sections(self):
        """Developer should get list of editable sections"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(SAMPLE_STORY)
            f.flush()
            file_path = Path(f.name)

        try:
            manager = StoryFileManager()
            editable = manager.get_editable_sections("developer", file_path)

            editable_names = [s.name for s in editable]
            assert "Dev Agent Record" in editable_names
            assert "Tasks" in editable_names
            assert "Acceptance Criteria" not in editable_names
            assert "QA Results" not in editable_names

        finally:
            file_path.unlink()


class TestValidatorPermissions:
    """Test Validator agent permissions"""

    def test_validator_can_edit_qa_results(self):
        """Validator should be allowed to edit QA Results"""
        manager = StoryFileManager()
        permission = manager.validate_edit(
            agent_id="validator",
            section_name="QA Results"
        )

        assert permission.allowed == True

    def test_validator_cannot_edit_dev_agent_record(self):
        """Validator should NOT be allowed to edit Dev Agent Record"""
        manager = StoryFileManager()
        permission = manager.validate_edit(
            agent_id="validator",
            section_name="Dev Agent Record"
        )

        assert permission.allowed == False

    def test_validator_cannot_edit_tasks(self):
        """Validator should NOT be allowed to edit Tasks"""
        manager = StoryFileManager()
        permission = manager.validate_edit(
            agent_id="validator",
            section_name="Tasks"
        )

        assert permission.allowed == False


class TestOrchestratorPermissions:
    """Test Orchestrator agent permissions"""

    def test_orchestrator_can_edit_all_sections(self):
        """Orchestrator should be allowed to edit all sections"""
        manager = StoryFileManager()

        sections_to_test = [
            "User Story",
            "Acceptance Criteria",
            "Tasks",
            "Dev Agent Record",
            "QA Results",
            "Completion Notes"
        ]

        for section in sections_to_test:
            permission = manager.validate_edit(
                agent_id="orchestrator",
                section_name=section
            )
            assert permission.allowed == True, f"Orchestrator should edit {section}"


class TestPartialMatching:
    """Test section name partial matching"""

    def test_partial_section_name_match(self):
        """Should match section names partially (case-insensitive)"""
        manager = StoryFileManager()

        # "Implementation Notes" is subsection of "Dev Agent Record"
        # Developer can edit anything with "Implementation" in allowed sections
        permission = manager.validate_edit(
            agent_id="developer",
            section_name="Implementation Notes"
        )

        assert permission.allowed == True

    def test_case_insensitive_matching(self):
        """Should match section names case-insensitively"""
        manager = StoryFileManager()

        permission1 = manager.validate_edit(
            agent_id="developer",
            section_name="dev agent record"
        )

        permission2 = manager.validate_edit(
            agent_id="developer",
            section_name="DEV AGENT RECORD"
        )

        assert permission1.allowed == True
        assert permission2.allowed == True


class TestApplyEdit:
    """Test applying edits with permission enforcement"""

    def test_apply_edit_allowed_section(self):
        """Should apply edit to allowed section"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(SAMPLE_STORY)
            f.flush()
            file_path = Path(f.name)

        try:
            manager = StoryFileManager()

            # Developer edits Dev Agent Record
            result = manager.apply_edit(
                agent_id="developer",
                file_path=file_path,
                section_name="Dev Agent Record",
                new_content="\nUpdated implementation notes\n"
            )

            assert result["success"] == True
            assert "Dev Agent Record" in result["section"]

            # Verify content changed
            content = file_path.read_text()
            assert "Updated implementation notes" in content

        finally:
            file_path.unlink()

    def test_apply_edit_forbidden_section(self):
        """Should reject edit to forbidden section"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(SAMPLE_STORY)
            f.flush()
            file_path = Path(f.name)

        try:
            manager = StoryFileManager()

            # Developer tries to edit Acceptance Criteria
            result = manager.apply_edit(
                agent_id="developer",
                file_path=file_path,
                section_name="Acceptance Criteria",
                new_content="\nHACKED CONTENT\n"
            )

            assert result["success"] == False
            assert "forbidden" in result["error"].lower()

            # Verify content NOT changed
            content = file_path.read_text()
            assert "HACKED CONTENT" not in content
            assert "Criterion 1" in content  # Original content preserved

        finally:
            file_path.unlink()

    def test_dry_run_mode(self):
        """Should validate without applying edit in dry run mode"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(SAMPLE_STORY)
            f.flush()
            file_path = Path(f.name)

        try:
            manager = StoryFileManager()

            # Dry run edit
            result = manager.apply_edit(
                agent_id="developer",
                file_path=file_path,
                section_name="Dev Agent Record",
                new_content="\nDry run content\n",
                dry_run=True
            )

            assert result["success"] == True
            assert result["dry_run"] == True
            assert "would_edit_lines" in result

            # Verify content NOT changed
            content = file_path.read_text()
            assert "Dry run content" not in content

        finally:
            file_path.unlink()


class TestCustomPermissions:
    """Test custom permission configuration"""

    def test_custom_permissions_override_defaults(self):
        """Should use custom permissions instead of defaults"""
        custom_perms = {
            "custom_agent": {
                "allowed_sections": ["Custom Section"],
                "forbidden_sections": ["Other Section"]
            }
        }

        manager = StoryFileManager(custom_permissions=custom_perms)

        # Custom agent can edit custom section
        permission = manager.validate_edit(
            agent_id="custom_agent",
            section_name="Custom Section"
        )
        assert permission.allowed == True

        # Custom agent cannot edit other section
        permission = manager.validate_edit(
            agent_id="custom_agent",
            section_name="Other Section"
        )
        assert permission.allowed == False


class TestUnknownAgent:
    """Test handling of unknown agents"""

    def test_unknown_agent_denied_by_default(self):
        """Unknown agents should be denied by default"""
        manager = StoryFileManager()

        permission = manager.validate_edit(
            agent_id="unknown_agent_xyz",
            section_name="Any Section"
        )

        assert permission.allowed == False
        assert "unknown" in permission.reason.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
