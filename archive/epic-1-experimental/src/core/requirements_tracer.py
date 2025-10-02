"""
Requirements Tracer - Given-When-Then Mapping

Maps acceptance criteria to test cases using Given-When-Then format for traceability.
Validator agent uses this to ensure all acceptance criteria have corresponding tests.

Example:
    Acceptance Criterion: "User can export data as CSV"

    Test Case:
        Given: User has selected data rows
        When: User clicks "Export as CSV" button
        Then: CSV file downloads with selected data

    Traceability: AC-1.2 → TC-export-csv-001
"""

import re
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


class TraceabilityStatus(Enum):
    """Traceability status between AC and test"""
    TRACED = "traced"  # AC has corresponding test
    PARTIAL = "partial"  # AC partially tested
    MISSING = "missing"  # AC has no test
    ORPHANED = "orphaned"  # Test with no AC


@dataclass
class GivenWhenThen:
    """Given-When-Then test specification"""
    given: str  # Precondition
    when: str  # Action
    then: str  # Expected result
    test_id: Optional[str] = None
    test_file: Optional[str] = None


@dataclass
class AcceptanceCriterion:
    """Acceptance criterion from story file"""
    id: str  # AC-1.1, AC-1.2, etc.
    description: str
    status: str = "pending"  # pending, traced, tested, passed, failed
    test_cases: List[GivenWhenThen] = field(default_factory=list)


@dataclass
class TraceabilityReport:
    """Traceability report between ACs and tests"""
    total_criteria: int
    traced_criteria: int
    missing_tests: List[str]
    orphaned_tests: List[str]
    coverage_percentage: float
    details: Dict[str, any] = field(default_factory=dict)


class RequirementsTracer:
    """
    Maps acceptance criteria to test cases using Given-When-Then format

    Provides traceability between requirements and tests for QA governance
    """

    def __init__(self):
        """Initialize requirements tracer"""
        self.acceptance_criteria: Dict[str, AcceptanceCriterion] = {}
        self.test_cases: Dict[str, GivenWhenThen] = {}

    def parse_acceptance_criteria(self, story_file: Path) -> List[AcceptanceCriterion]:
        """
        Parse acceptance criteria from story file

        Args:
            story_file: Path to story markdown file

        Returns:
            List of AcceptanceCriterion objects

        Example:
            ## Acceptance Criteria

            - [ ] AC-1.1: User can create new project
            - [ ] AC-1.2: User can edit project name
            - [x] AC-1.3: User can delete project
        """
        if not story_file.exists():
            return []

        content = story_file.read_text(encoding='utf-8')
        criteria = []

        # Find Acceptance Criteria section
        ac_section_match = re.search(
            r'##\s+Acceptance Criteria\s*\n(.*?)(?=\n##|\Z)',
            content,
            re.DOTALL
        )

        if not ac_section_match:
            return []

        ac_section = ac_section_match.group(1)

        # Parse criteria (checkbox format)
        # Matches: - [ ] AC-1.1: Description
        # Matches: - [x] AC-1.2: Description
        pattern = r'- \[([ x])\]\s+(AC-[\d.]+):\s+(.+?)(?=\n|$)'

        for match in re.finditer(pattern, ac_section):
            checked = match.group(1)
            ac_id = match.group(2)
            description = match.group(3).strip()

            status = "tested" if checked == 'x' else "pending"

            criterion = AcceptanceCriterion(
                id=ac_id,
                description=description,
                status=status
            )

            criteria.append(criterion)
            self.acceptance_criteria[ac_id] = criterion

        return criteria

    def parse_test_case(self, test_content: str, test_file: str = "") -> Optional[GivenWhenThen]:
        """
        Parse Given-When-Then from test docstring or comments

        Args:
            test_content: Test function content
            test_file: Test file name

        Returns:
            GivenWhenThen object or None

        Example:
            def test_user_can_export_csv():
                '''
                Given: User has selected data rows
                When: User clicks "Export as CSV" button
                Then: CSV file downloads with selected data

                Traces: AC-1.2
                '''
        """
        # Extract test ID from function name
        test_id_match = re.search(r'def (test_[\w]+)', test_content)
        test_id = test_id_match.group(1) if test_id_match else ""

        # Parse Given-When-Then from docstring or comments
        given_match = re.search(r'Given:\s*(.+?)(?=\n\s*When:|\n\n|$)', test_content, re.DOTALL)
        when_match = re.search(r'When:\s*(.+?)(?=\n\s*Then:|\n\n|$)', test_content, re.DOTALL)
        then_match = re.search(r'Then:\s*(.+?)(?=\n\s*Traces:|\n\n|$)', test_content, re.DOTALL)

        if not (given_match and when_match and then_match):
            return None

        given = given_match.group(1).strip()
        when = when_match.group(1).strip()
        then = then_match.group(1).strip()

        gwt = GivenWhenThen(
            given=given,
            when=when,
            then=then,
            test_id=test_id,
            test_file=test_file
        )

        # Extract traced AC IDs
        traces_match = re.search(r'Traces:\s*(AC-[\d.]+(?:,\s*AC-[\d.]+)*)', test_content)
        if traces_match:
            traced_acs = [ac.strip() for ac in traces_match.group(1).split(',')]

            # Link test to ACs
            for ac_id in traced_acs:
                if ac_id in self.acceptance_criteria:
                    self.acceptance_criteria[ac_id].test_cases.append(gwt)

        self.test_cases[test_id] = gwt
        return gwt

    def parse_test_file(self, test_file: Path) -> List[GivenWhenThen]:
        """
        Parse all test cases from test file

        Args:
            test_file: Path to test file

        Returns:
            List of GivenWhenThen objects
        """
        if not test_file.exists():
            return []

        content = test_file.read_text(encoding='utf-8')
        test_cases = []

        # Find all test functions with Given-When-Then
        # Split by "def test_" to get individual test functions
        test_functions = re.split(r'\ndef (test_[\w]+)', content)[1:]

        # Process pairs (function_name, function_body)
        for i in range(0, len(test_functions), 2):
            if i + 1 < len(test_functions):
                test_name = test_functions[i]
                test_body = test_functions[i + 1]

                # Reconstruct test function
                test_content = f"def {test_name}{test_body}"

                gwt = self.parse_test_case(test_content, str(test_file))
                if gwt:
                    test_cases.append(gwt)

        return test_cases

    def generate_traceability_matrix(self) -> Dict[str, List[str]]:
        """
        Generate traceability matrix mapping ACs to tests

        Returns:
            Dict mapping AC IDs to test IDs

        Example:
            {
                "AC-1.1": ["test_create_project", "test_create_project_validation"],
                "AC-1.2": ["test_edit_project_name"],
                "AC-1.3": []  # Missing test
            }
        """
        matrix = {}

        for ac_id, criterion in self.acceptance_criteria.items():
            test_ids = [tc.test_id for tc in criterion.test_cases if tc.test_id]
            matrix[ac_id] = test_ids

        return matrix

    def calculate_coverage(self) -> TraceabilityReport:
        """
        Calculate test coverage for acceptance criteria

        Returns:
            TraceabilityReport with coverage metrics
        """
        total_criteria = len(self.acceptance_criteria)
        traced_criteria = 0
        missing_tests = []

        for ac_id, criterion in self.acceptance_criteria.items():
            if len(criterion.test_cases) > 0:
                traced_criteria += 1
            else:
                missing_tests.append(ac_id)

        # Find orphaned tests (tests not linked to any AC)
        orphaned_tests = []
        for test_id, test_case in self.test_cases.items():
            # Check if test is linked to any AC
            is_linked = False
            for criterion in self.acceptance_criteria.values():
                if test_case in criterion.test_cases:
                    is_linked = True
                    break

            if not is_linked:
                orphaned_tests.append(test_id)

        coverage_pct = (traced_criteria / total_criteria * 100) if total_criteria > 0 else 0.0

        return TraceabilityReport(
            total_criteria=total_criteria,
            traced_criteria=traced_criteria,
            missing_tests=missing_tests,
            orphaned_tests=orphaned_tests,
            coverage_percentage=coverage_pct,
            details={
                "acceptance_criteria": {ac_id: len(ac.test_cases) for ac_id, ac in self.acceptance_criteria.items()},
                "traceability_matrix": self.generate_traceability_matrix()
            }
        )

    def validate_criterion_coverage(self, ac_id: str) -> Dict[str, any]:
        """
        Validate test coverage for specific acceptance criterion

        Args:
            ac_id: Acceptance criterion ID (e.g., "AC-1.1")

        Returns:
            Dict with validation result

        Example:
            {
                "ac_id": "AC-1.1",
                "covered": True,
                "test_count": 2,
                "status": "traced",
                "tests": ["test_create_project", "test_create_project_validation"]
            }
        """
        if ac_id not in self.acceptance_criteria:
            return {
                "ac_id": ac_id,
                "covered": False,
                "error": f"Acceptance criterion {ac_id} not found"
            }

        criterion = self.acceptance_criteria[ac_id]
        test_count = len(criterion.test_cases)
        covered = test_count > 0

        status = TraceabilityStatus.TRACED if covered else TraceabilityStatus.MISSING

        return {
            "ac_id": ac_id,
            "covered": covered,
            "test_count": test_count,
            "status": status.value,
            "tests": [tc.test_id for tc in criterion.test_cases if tc.test_id],
            "description": criterion.description
        }

    def generate_coverage_report(self) -> str:
        """
        Generate human-readable coverage report

        Returns:
            Markdown-formatted coverage report
        """
        report = self.calculate_coverage()

        output = []
        output.append("# Requirements Traceability Report\n")
        output.append(f"**Total Acceptance Criteria**: {report.total_criteria}")
        output.append(f"**Traced Criteria**: {report.traced_criteria}")
        output.append(f"**Coverage**: {report.coverage_percentage:.1f}%\n")

        if report.missing_tests:
            output.append("## Missing Tests\n")
            output.append("The following acceptance criteria have no test coverage:\n")
            for ac_id in report.missing_tests:
                criterion = self.acceptance_criteria[ac_id]
                output.append(f"- **{ac_id}**: {criterion.description}")
            output.append("")

        if report.orphaned_tests:
            output.append("## Orphaned Tests\n")
            output.append("The following tests are not linked to any acceptance criteria:\n")
            for test_id in report.orphaned_tests:
                output.append(f"- `{test_id}`")
            output.append("")

        output.append("## Traceability Matrix\n")
        matrix = report.details.get("traceability_matrix", {})
        for ac_id, test_ids in matrix.items():
            criterion = self.acceptance_criteria[ac_id]
            status_icon = "✓" if test_ids else "✗"
            output.append(f"- {status_icon} **{ac_id}**: {criterion.description}")
            if test_ids:
                for test_id in test_ids:
                    output.append(f"  - `{test_id}`")
            else:
                output.append("  - *No tests*")

        return "\n".join(output)

    def export_to_dict(self) -> Dict[str, any]:
        """
        Export traceability data as dict for JSON serialization

        Returns:
            Dict with all traceability data
        """
        return {
            "acceptance_criteria": {
                ac_id: {
                    "id": ac.id,
                    "description": ac.description,
                    "status": ac.status,
                    "test_cases": [
                        {
                            "given": tc.given,
                            "when": tc.when,
                            "then": tc.then,
                            "test_id": tc.test_id,
                            "test_file": tc.test_file
                        }
                        for tc in ac.test_cases
                    ]
                }
                for ac_id, ac in self.acceptance_criteria.items()
            },
            "test_cases": {
                test_id: {
                    "given": tc.given,
                    "when": tc.when,
                    "then": tc.then,
                    "test_id": tc.test_id,
                    "test_file": tc.test_file
                }
                for test_id, tc in self.test_cases.items()
            },
            "coverage": self.calculate_coverage().__dict__
        }
