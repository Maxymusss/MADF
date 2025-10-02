"""
Tests for Story 1.7 - Requirements Tracer (Given-When-Then Mapping)

Tests RequirementsTracer enforces traceability between acceptance criteria and tests
"""

import pytest
from pathlib import Path
import tempfile
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.requirements_tracer import (
    RequirementsTracer,
    AcceptanceCriterion,
    GivenWhenThen,
    TraceabilityStatus,
    TraceabilityReport
)


# Sample story file with acceptance criteria
SAMPLE_STORY_WITH_AC = """# Story 1.X - Export Feature

## User Story

As a user, I want to export data

## Acceptance Criteria

- [ ] AC-1.1: User can export data as CSV
- [ ] AC-1.2: User can export data as JSON
- [x] AC-1.3: User can cancel export operation

## Tasks

Implementation tasks here
"""


# Sample test file with Given-When-Then
SAMPLE_TEST_FILE = """
import pytest

def test_export_csv():
    '''
    Test CSV export functionality

    Given: User has selected 10 data rows
    When: User clicks "Export as CSV" button
    Then: CSV file downloads with 10 rows of data

    Traces: AC-1.1
    '''
    # Test implementation
    assert True


def test_export_json():
    '''
    Test JSON export functionality

    Given: User has selected data with nested objects
    When: User clicks "Export as JSON" button
    Then: JSON file downloads with properly formatted nested data

    Traces: AC-1.2
    '''
    # Test implementation
    assert True


def test_cancel_export():
    '''
    Test canceling export operation

    Given: User has started export process
    When: User clicks "Cancel" button
    Then: Export is cancelled and no file is generated

    Traces: AC-1.3
    '''
    # Test implementation
    assert True


def test_orphaned_test_no_ac():
    '''
    This test has no AC traceability

    Given: Some condition
    When: Some action
    Then: Some result
    '''
    # Test with no Traces comment
    assert True
"""


class TestAcceptanceCriteriaParsing:
    """Test parsing acceptance criteria from story files"""

    def test_parse_ac_from_story_file(self):
        """Should parse acceptance criteria from story markdown"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(SAMPLE_STORY_WITH_AC)
            f.flush()
            file_path = Path(f.name)

        try:
            tracer = RequirementsTracer()
            criteria = tracer.parse_acceptance_criteria(file_path)

            assert len(criteria) == 3, "Should find 3 acceptance criteria"

            # Check AC IDs
            ac_ids = [ac.id for ac in criteria]
            assert "AC-1.1" in ac_ids
            assert "AC-1.2" in ac_ids
            assert "AC-1.3" in ac_ids

        finally:
            file_path.unlink()

    def test_ac_status_detection(self):
        """Should detect AC status from checkbox"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(SAMPLE_STORY_WITH_AC)
            f.flush()
            file_path = Path(f.name)

        try:
            tracer = RequirementsTracer()
            criteria = tracer.parse_acceptance_criteria(file_path)

            # AC-1.1 and AC-1.2 are unchecked (pending)
            ac_1_1 = next(ac for ac in criteria if ac.id == "AC-1.1")
            assert ac_1_1.status == "pending"

            # AC-1.3 is checked (tested)
            ac_1_3 = next(ac for ac in criteria if ac.id == "AC-1.3")
            assert ac_1_3.status == "tested"

        finally:
            file_path.unlink()

    def test_ac_description_capture(self):
        """Should capture AC descriptions correctly"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(SAMPLE_STORY_WITH_AC)
            f.flush()
            file_path = Path(f.name)

        try:
            tracer = RequirementsTracer()
            criteria = tracer.parse_acceptance_criteria(file_path)

            ac_1_1 = next(ac for ac in criteria if ac.id == "AC-1.1")
            assert "export data as CSV" in ac_1_1.description

        finally:
            file_path.unlink()


class TestGivenWhenThenParsing:
    """Test parsing Given-When-Then from test files"""

    def test_parse_gwt_from_test_content(self):
        """Should parse Given-When-Then from test docstring"""
        tracer = RequirementsTracer()

        test_content = """
def test_export_csv():
    '''
    Given: User has selected data
    When: User clicks export
    Then: CSV file downloads

    Traces: AC-1.1
    '''
    assert True
"""

        gwt = tracer.parse_test_case(test_content)

        assert gwt is not None
        assert gwt.given == "User has selected data"
        assert gwt.when == "User clicks export"
        assert gwt.then == "CSV file downloads"
        assert gwt.test_id == "test_export_csv"

    def test_parse_gwt_without_traces(self):
        """Should parse GWT even without Traces comment"""
        tracer = RequirementsTracer()

        test_content = """
def test_something():
    '''
    Given: Some condition
    When: Some action
    Then: Some result
    '''
    assert True
"""

        gwt = tracer.parse_test_case(test_content)

        assert gwt is not None
        assert gwt.given == "Some condition"
        assert gwt.test_id == "test_something"

    def test_parse_test_file_multiple_tests(self):
        """Should parse multiple tests from file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(SAMPLE_TEST_FILE)
            f.flush()
            file_path = Path(f.name)

        try:
            tracer = RequirementsTracer()
            test_cases = tracer.parse_test_file(file_path)

            # Should find 4 tests with GWT
            assert len(test_cases) == 4

            test_ids = [tc.test_id for tc in test_cases]
            assert "test_export_csv" in test_ids
            assert "test_export_json" in test_ids
            assert "test_cancel_export" in test_ids
            assert "test_orphaned_test_no_ac" in test_ids

        finally:
            file_path.unlink()


class TestTraceabilityMapping:
    """Test traceability mapping between ACs and tests"""

    def test_trace_tests_to_acs(self):
        """Should link tests to ACs via Traces comment"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as story_f:
            story_f.write(SAMPLE_STORY_WITH_AC)
            story_f.flush()
            story_path = Path(story_f.name)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as test_f:
            test_f.write(SAMPLE_TEST_FILE)
            test_f.flush()
            test_path = Path(test_f.name)

        try:
            tracer = RequirementsTracer()

            # Parse story and tests
            tracer.parse_acceptance_criteria(story_path)
            tracer.parse_test_file(test_path)

            # Check AC-1.1 has test linked
            ac_1_1 = tracer.acceptance_criteria["AC-1.1"]
            assert len(ac_1_1.test_cases) == 1
            assert ac_1_1.test_cases[0].test_id == "test_export_csv"

            # Check AC-1.2 has test linked
            ac_1_2 = tracer.acceptance_criteria["AC-1.2"]
            assert len(ac_1_2.test_cases) == 1
            assert ac_1_2.test_cases[0].test_id == "test_export_json"

        finally:
            story_path.unlink()
            test_path.unlink()

    def test_generate_traceability_matrix(self):
        """Should generate traceability matrix mapping ACs to tests"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as story_f:
            story_f.write(SAMPLE_STORY_WITH_AC)
            story_f.flush()
            story_path = Path(story_f.name)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as test_f:
            test_f.write(SAMPLE_TEST_FILE)
            test_f.flush()
            test_path = Path(test_f.name)

        try:
            tracer = RequirementsTracer()
            tracer.parse_acceptance_criteria(story_path)
            tracer.parse_test_file(test_path)

            matrix = tracer.generate_traceability_matrix()

            # AC-1.1 should map to test_export_csv
            assert "test_export_csv" in matrix["AC-1.1"]

            # AC-1.2 should map to test_export_json
            assert "test_export_json" in matrix["AC-1.2"]

            # AC-1.3 should map to test_cancel_export
            assert "test_cancel_export" in matrix["AC-1.3"]

        finally:
            story_path.unlink()
            test_path.unlink()


class TestCoverageCalculation:
    """Test coverage calculation and reporting"""

    def test_calculate_coverage_full(self):
        """Should calculate 100% coverage when all ACs have tests"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as story_f:
            story_f.write(SAMPLE_STORY_WITH_AC)
            story_f.flush()
            story_path = Path(story_f.name)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as test_f:
            test_f.write(SAMPLE_TEST_FILE)
            test_f.flush()
            test_path = Path(test_f.name)

        try:
            tracer = RequirementsTracer()
            tracer.parse_acceptance_criteria(story_path)
            tracer.parse_test_file(test_path)

            report = tracer.calculate_coverage()

            assert report.total_criteria == 3
            assert report.traced_criteria == 3
            assert report.coverage_percentage == 100.0
            assert len(report.missing_tests) == 0

        finally:
            story_path.unlink()
            test_path.unlink()

    def test_calculate_coverage_partial(self):
        """Should calculate partial coverage when some ACs lack tests"""
        # Story with 3 ACs
        story_content = """
## Acceptance Criteria

- [ ] AC-1.1: Feature A
- [ ] AC-1.2: Feature B
- [ ] AC-1.3: Feature C
"""

        # Test file with only 1 test (traces AC-1.1)
        test_content = """
def test_feature_a():
    '''
    Given: Condition A
    When: Action A
    Then: Result A

    Traces: AC-1.1
    '''
    pass
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as story_f:
            story_f.write(story_content)
            story_f.flush()
            story_path = Path(story_f.name)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as test_f:
            test_f.write(test_content)
            test_f.flush()
            test_path = Path(test_f.name)

        try:
            tracer = RequirementsTracer()
            tracer.parse_acceptance_criteria(story_path)
            tracer.parse_test_file(test_path)

            report = tracer.calculate_coverage()

            assert report.total_criteria == 3
            assert report.traced_criteria == 1
            assert report.coverage_percentage == pytest.approx(33.33, rel=0.1)
            assert "AC-1.2" in report.missing_tests
            assert "AC-1.3" in report.missing_tests

        finally:
            story_path.unlink()
            test_path.unlink()

    def test_identify_orphaned_tests(self):
        """Should identify tests not linked to any AC"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as story_f:
            story_f.write(SAMPLE_STORY_WITH_AC)
            story_f.flush()
            story_path = Path(story_f.name)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as test_f:
            test_f.write(SAMPLE_TEST_FILE)
            test_f.flush()
            test_path = Path(test_f.name)

        try:
            tracer = RequirementsTracer()
            tracer.parse_acceptance_criteria(story_path)
            tracer.parse_test_file(test_path)

            report = tracer.calculate_coverage()

            # test_orphaned_test_no_ac should be identified as orphaned
            assert "test_orphaned_test_no_ac" in report.orphaned_tests

        finally:
            story_path.unlink()
            test_path.unlink()


class TestValidation:
    """Test validation methods"""

    def test_validate_criterion_coverage_traced(self):
        """Should validate AC has test coverage"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as story_f:
            story_f.write(SAMPLE_STORY_WITH_AC)
            story_f.flush()
            story_path = Path(story_f.name)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as test_f:
            test_f.write(SAMPLE_TEST_FILE)
            test_f.flush()
            test_path = Path(test_f.name)

        try:
            tracer = RequirementsTracer()
            tracer.parse_acceptance_criteria(story_path)
            tracer.parse_test_file(test_path)

            result = tracer.validate_criterion_coverage("AC-1.1")

            assert result["covered"] == True
            assert result["test_count"] == 1
            assert result["status"] == "traced"
            assert "test_export_csv" in result["tests"]

        finally:
            story_path.unlink()
            test_path.unlink()

    def test_validate_criterion_coverage_missing(self):
        """Should validate AC has no test coverage"""
        story_content = """
## Acceptance Criteria

- [ ] AC-1.1: Feature without test
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as story_f:
            story_f.write(story_content)
            story_f.flush()
            story_path = Path(story_f.name)

        try:
            tracer = RequirementsTracer()
            tracer.parse_acceptance_criteria(story_path)

            result = tracer.validate_criterion_coverage("AC-1.1")

            assert result["covered"] == False
            assert result["test_count"] == 0
            assert result["status"] == "missing"

        finally:
            story_path.unlink()


class TestReportGeneration:
    """Test report generation"""

    def test_generate_coverage_report(self):
        """Should generate human-readable coverage report"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as story_f:
            story_f.write(SAMPLE_STORY_WITH_AC)
            story_f.flush()
            story_path = Path(story_f.name)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as test_f:
            test_f.write(SAMPLE_TEST_FILE)
            test_f.flush()
            test_path = Path(test_f.name)

        try:
            tracer = RequirementsTracer()
            tracer.parse_acceptance_criteria(story_path)
            tracer.parse_test_file(test_path)

            report = tracer.generate_coverage_report()

            # Should contain key sections
            assert "# Requirements Traceability Report" in report
            assert "Total Acceptance Criteria" in report
            assert "Coverage" in report
            assert "Traceability Matrix" in report
            assert "AC-1.1" in report
            assert "test_export_csv" in report

        finally:
            story_path.unlink()
            test_path.unlink()

    def test_export_to_dict(self):
        """Should export traceability data as dict"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as story_f:
            story_f.write(SAMPLE_STORY_WITH_AC)
            story_f.flush()
            story_path = Path(story_f.name)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as test_f:
            test_f.write(SAMPLE_TEST_FILE)
            test_f.flush()
            test_path = Path(test_f.name)

        try:
            tracer = RequirementsTracer()
            tracer.parse_acceptance_criteria(story_path)
            tracer.parse_test_file(test_path)

            data = tracer.export_to_dict()

            assert "acceptance_criteria" in data
            assert "test_cases" in data
            assert "coverage" in data
            assert "AC-1.1" in data["acceptance_criteria"]
            assert "test_export_csv" in data["test_cases"]

        finally:
            story_path.unlink()
            test_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
