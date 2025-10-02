"""
Story File Permission Manager

Enforces section-level edit permissions for story files as defined in BMAD agent configs.
Developer and Validator agents have restricted permissions for story file sections.

Example YAML config:
    story_file_permissions:
      allowed_sections:
        - "Dev Agent Record"
        - "Completion Notes"
      forbidden_sections:
        - "Acceptance Criteria"
        - "QA Results"

Usage:
    manager = StoryFileManager()
    if manager.validate_edit(agent_id="developer", section="Acceptance Criteria"):
        # Edit allowed
    else:
        # Edit forbidden
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass


@dataclass
class StorySection:
    """Represents a section in a story markdown file"""
    name: str
    start_line: int
    end_line: int
    content: str
    level: int  # Heading level (1=##, 2=###, etc.)


@dataclass
class EditPermission:
    """Permission result for edit validation"""
    allowed: bool
    reason: str
    section_name: Optional[str] = None
    agent_id: Optional[str] = None


class StoryFileManager:
    """
    Manages story file permissions and section-level editing

    Enforces BMAD-style story file permissions:
    - Developer: Can edit "Dev Agent Record", "Tasks", "Subtasks"
    - Validator: Can edit "QA Results", "QA Agent Record"
    - Orchestrator: Can create new stories, edit all sections
    - Others: Read-only access
    """

    # Default permissions (can be overridden by YAML config)
    DEFAULT_PERMISSIONS: Dict[str, Dict[str, List[str]]] = {
        "developer": {
            "allowed_sections": [
                "Dev Agent Record",
                "Tasks",
                "Subtasks",
                "Implementation Notes",
                "Completion Notes"
            ],
            "forbidden_sections": [
                "Acceptance Criteria",
                "QA Results",
                "User Story",
                "Definition of Done"
            ]
        },
        "validator": {
            "allowed_sections": [
                "QA Results",
                "QA Agent Record",
                "Test Results",
                "Validation Report"
            ],
            "forbidden_sections": [
                "Acceptance Criteria",
                "Dev Agent Record",
                "Tasks",
                "Subtasks"
            ]
        },
        "orchestrator": {
            "allowed_sections": ["*"],  # All sections
            "forbidden_sections": []
        },
        "analyst": {
            "allowed_sections": [
                "Research Findings",
                "Requirements Analysis"
            ],
            "forbidden_sections": [
                "Acceptance Criteria",
                "Implementation Notes"
            ]
        },
        "knowledge": {
            "allowed_sections": [
                "Architecture Notes",
                "Documentation Links"
            ],
            "forbidden_sections": [
                "Acceptance Criteria",
                "Implementation Notes"
            ]
        }
    }

    def __init__(self, custom_permissions: Optional[Dict[str, Dict[str, List[str]]]] = None):
        """
        Initialize story file manager

        Args:
            custom_permissions: Optional custom permissions dict (overrides defaults)
        """
        self.permissions = custom_permissions or self.DEFAULT_PERMISSIONS

    def parse_story_file(self, file_path: Path) -> List[StorySection]:
        """
        Parse story markdown file into sections

        Args:
            file_path: Path to story markdown file

        Returns:
            List of StorySection objects
        """
        if not file_path.exists():
            return []

        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')

        sections = []
        current_section = None
        current_content = []

        for i, line in enumerate(lines):
            # Match markdown headings (##, ###, etc.)
            heading_match = re.match(r'^(#{2,})\s+(.+)$', line)

            if heading_match:
                # Save previous section if exists
                if current_section:
                    current_section.end_line = i - 1
                    current_section.content = '\n'.join(current_content)
                    sections.append(current_section)

                # Start new section
                level = len(heading_match.group(1)) - 1  # ## = level 1, ### = level 2
                section_name = heading_match.group(2).strip()

                current_section = StorySection(
                    name=section_name,
                    start_line=i,
                    end_line=i,
                    content="",
                    level=level
                )
                current_content = []
            else:
                # Accumulate content for current section
                if current_section:
                    current_content.append(line)

        # Save last section
        if current_section:
            current_section.end_line = len(lines) - 1
            current_section.content = '\n'.join(current_content)
            sections.append(current_section)

        return sections

    def validate_edit(
        self,
        agent_id: str,
        section_name: str,
        file_path: Optional[Path] = None
    ) -> EditPermission:
        """
        Validate if agent can edit specific section

        Args:
            agent_id: Agent identifier (developer, validator, orchestrator, etc.)
            section_name: Section name to edit
            file_path: Optional story file path for context

        Returns:
            EditPermission object with validation result
        """
        agent_id_lower = agent_id.lower()

        # Unknown agent - deny by default
        if agent_id_lower not in self.permissions:
            return EditPermission(
                allowed=False,
                reason=f"Unknown agent '{agent_id}' - no permissions defined",
                section_name=section_name,
                agent_id=agent_id
            )

        agent_perms = self.permissions[agent_id_lower]
        allowed_sections = agent_perms.get("allowed_sections", [])
        forbidden_sections = agent_perms.get("forbidden_sections", [])

        # Check if all sections allowed (orchestrator case)
        if "*" in allowed_sections:
            return EditPermission(
                allowed=True,
                reason=f"Agent '{agent_id}' has unrestricted access",
                section_name=section_name,
                agent_id=agent_id
            )

        # Check forbidden sections first (explicit deny)
        if self._section_matches_any(section_name, forbidden_sections):
            return EditPermission(
                allowed=False,
                reason=f"Section '{section_name}' is explicitly forbidden for agent '{agent_id}'",
                section_name=section_name,
                agent_id=agent_id
            )

        # Check allowed sections
        if self._section_matches_any(section_name, allowed_sections):
            return EditPermission(
                allowed=True,
                reason=f"Section '{section_name}' is allowed for agent '{agent_id}'",
                section_name=section_name,
                agent_id=agent_id
            )

        # Not in allowed list - deny by default
        return EditPermission(
            allowed=False,
            reason=f"Section '{section_name}' not in allowed sections for agent '{agent_id}'",
            section_name=section_name,
            agent_id=agent_id
        )

    def _section_matches_any(self, section_name: str, section_list: List[str]) -> bool:
        """
        Check if section name matches any in list (case-insensitive, partial match)

        Args:
            section_name: Section name to check
            section_list: List of section patterns

        Returns:
            True if match found, False otherwise
        """
        section_lower = section_name.lower()

        for pattern in section_list:
            pattern_lower = pattern.lower()

            # Exact match
            if section_lower == pattern_lower:
                return True

            # Partial match (pattern in section name)
            if pattern_lower in section_lower:
                return True

        return False

    def get_editable_sections(self, agent_id: str, file_path: Path) -> List[StorySection]:
        """
        Get list of sections agent can edit in story file

        Args:
            agent_id: Agent identifier
            file_path: Path to story file

        Returns:
            List of editable StorySection objects
        """
        sections = self.parse_story_file(file_path)
        editable = []

        for section in sections:
            permission = self.validate_edit(agent_id, section.name, file_path)
            if permission.allowed:
                editable.append(section)

        return editable

    def get_forbidden_sections(self, agent_id: str, file_path: Path) -> List[StorySection]:
        """
        Get list of sections agent cannot edit in story file

        Args:
            agent_id: Agent identifier
            file_path: Path to story file

        Returns:
            List of forbidden StorySection objects
        """
        sections = self.parse_story_file(file_path)
        forbidden = []

        for section in sections:
            permission = self.validate_edit(agent_id, section.name, file_path)
            if not permission.allowed:
                forbidden.append(section)

        return forbidden

    def apply_edit(
        self,
        agent_id: str,
        file_path: Path,
        section_name: str,
        new_content: str,
        dry_run: bool = False
    ) -> Dict[str, any]:
        """
        Apply edit to specific section with permission enforcement

        Args:
            agent_id: Agent identifier
            file_path: Path to story file
            section_name: Section name to edit
            new_content: New content for section
            dry_run: If True, validate but don't apply edit

        Returns:
            Dict with operation result
        """
        # Validate permission
        permission = self.validate_edit(agent_id, section_name, file_path)

        if not permission.allowed:
            return {
                "success": False,
                "error": permission.reason,
                "permission": permission
            }

        # Parse file
        sections = self.parse_story_file(file_path)

        # Find target section
        target_section = None
        for section in sections:
            if self._section_matches_any(section_name, [section.name]):
                target_section = section
                break

        if not target_section:
            return {
                "success": False,
                "error": f"Section '{section_name}' not found in {file_path}",
                "permission": permission
            }

        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "permission": permission,
                "section": target_section.name,
                "would_edit_lines": f"{target_section.start_line}-{target_section.end_line}"
            }

        # Apply edit
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')

        # Replace section content (preserve heading)
        heading_line = lines[target_section.start_line]
        new_section_lines = [heading_line, new_content]

        # Reconstruct file
        new_lines = (
            lines[:target_section.start_line] +
            new_section_lines +
            lines[target_section.end_line + 1:]
        )

        # Write file
        file_path.write_text('\n'.join(new_lines), encoding='utf-8')

        return {
            "success": True,
            "permission": permission,
            "section": target_section.name,
            "lines_edited": f"{target_section.start_line}-{target_section.end_line}",
            "file_path": str(file_path)
        }

    def audit_edit_attempt(
        self,
        agent_id: str,
        file_path: Path,
        section_name: str,
        allowed: bool
    ) -> Dict[str, any]:
        """
        Log audit trail for edit attempt (for compliance/debugging)

        Args:
            agent_id: Agent identifier
            file_path: Story file path
            section_name: Section attempted
            allowed: Whether edit was allowed

        Returns:
            Dict with audit entry
        """
        return {
            "timestamp": "2025-10-01T00:00:00Z",  # Would use datetime.now() in real impl
            "agent_id": agent_id,
            "file_path": str(file_path),
            "section_name": section_name,
            "allowed": allowed,
            "action": "ALLOWED" if allowed else "DENIED"
        }
