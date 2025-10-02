#!/usr/bin/env python
"""
Update all 5 agent implementations to:
1. Pass agent_id to BaseAgent constructor
2. Remove _initialize_tools() methods (tools now loaded from YAML)
"""

import re
from pathlib import Path

def update_agent_file(file_path: Path, agent_id: str, old_init_pattern: str, new_init_line: str):
    """Update single agent file"""
    content = file_path.read_text()

    # Replace super().__init__() call to add agent_id
    content = re.sub(
        old_init_pattern,
        new_init_line,
        content,
        count=1
    )

    # Remove _initialize_tools() method completely
    content = re.sub(
        r'\n    def _initialize_tools\(self\):.*?\n(?=\n    def |\nclass |\Z)',
        '\n',
        content,
        flags=re.DOTALL
    )

    # Remove call to self._initialize_tools() in __init__
    content = content.replace('\n        self._initialize_tools()', '')

    file_path.write_text(content)
    print(f"[OK] Updated {file_path.name}")

def main():
    agents_dir = Path("src/agents")

    # Orchestrator
    update_agent_file(
        agents_dir / "orchestrator_agent.py",
        "orchestrator",
        r'super\(\).__init__\("Orchestrator", "Workflow Coordinator"\)',
        'super().__init__("Orchestrator", "Workflow Coordinator", agent_id="orchestrator")'
    )

    # Analyst
    update_agent_file(
        agents_dir / "analyst_agent.py",
        "analyst",
        r'super\(\).__init__\("Analyst", "Code Analysis Specialist"\)',
        'super().__init__("Analyst", "Code Analysis Specialist", agent_id="analyst")'
    )

    # Knowledge
    update_agent_file(
        agents_dir / "knowledge_agent.py",
        "knowledge",
        r'super\(\).__init__\("Knowledge", "Knowledge Management Specialist"\)',
        'super().__init__("Knowledge", "Knowledge Management Specialist", agent_id="knowledge")'
    )

    # Developer
    update_agent_file(
        agents_dir / "developer_agent.py",
        "developer",
        r'super\(\).__init__\("Developer", "Implementation Specialist"\)',
        'super().__init__("Developer", "Implementation Specialist", agent_id="developer")'
    )

    # Validator
    update_agent_file(
        agents_dir / "validator_agent.py",
        "validator",
        r'super\(\).__init__\("Validator", "Quality Assurance Specialist"\)',
        'super().__init__("Validator", "Quality Assurance Specialist", agent_id="validator")'
    )

    print("\n[SUCCESS] All 5 agent implementations updated")
    print("- Added agent_id parameter to BaseAgent constructor")
    print("- Removed _initialize_tools() methods (tools now loaded from YAML)")

if __name__ == "__main__":
    main()
