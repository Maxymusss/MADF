# Quality Standards

**BMAD Pattern**: TDD workflow, QA governance, and requirements traceability

## Overview

Quality standards ensure consistent code quality, test coverage, and gate governance across the multiagent framework. Story 1.7 adopts BMAD's programmatic quality patterns for LangGraph agents.

## TDD Workflow (Developer Agent)

### RED → GREEN → REFACTOR

Developer agent enforces Test-Driven Development workflow:

```python
# 1. RED: Write failing test first
def test_user_authentication():
    """
    Given: Unauthenticated user
    When: User provides valid credentials
    Then: User receives access token
    """
    auth = AuthService()
    result = auth.login("user@example.com", "password")
    assert result.success is True
    assert result.token is not None

# 2. GREEN: Write minimal implementation
class AuthService:
    def login(self, email: str, password: str):
        # Minimal implementation to pass test
        return LoginResult(success=True, token="test_token")

# 3. REFACTOR: Improve quality without breaking tests
class AuthService:
    def login(self, email: str, password: str):
        # Refactored with proper validation
        if not self._validate_email(email):
            return LoginResult(success=False, error="Invalid email")

        user = self._find_user(email)
        if not user or not self._verify_password(user, password):
            return LoginResult(success=False, error="Invalid credentials")

        token = self._generate_token(user)
        return LoginResult(success=True, token=token)
```

### TDD Capability Definition

```yaml
# config/agents/developer_config.yaml
capabilities:
  - name: "implement_story"
    description: "Implement story with TDD workflow"
    workflow:
      - "Write failing test (RED)"
      - "Write minimal code to pass (GREEN)"
      - "Refactor for quality"
    quality_gates:
      - "All tests pass"
      - "Code coverage ≥ 70%"
      - "No critical linting errors"
```

### TDD Enforcement

Developer agent checks TDD compliance:

```python
class DeveloperAgent(BaseAgent):
    def implement_story(self, story: Story) -> ImplementationResult:
        # Step 1: Verify test exists
        test_file = self._find_test_file(story)
        if not test_file:
            return ImplementationResult(
                status="blocked",
                reason="No test file found - TDD requires tests first"
            )

        # Step 2: Run test (should fail initially - RED)
        test_result = self._run_tests(test_file)
        if test_result.passed:
            logger.warning("Test passed before implementation - consider edge cases")

        # Step 3: Implement minimal solution (GREEN)
        self._implement_code(story)

        # Step 4: Run tests again
        test_result = self._run_tests(test_file)
        if not test_result.passed:
            return ImplementationResult(
                status="failed",
                reason=f"Tests failed: {test_result.failures}"
            )

        # Step 5: Refactor (REFACTOR)
        self._apply_refactoring(story)

        # Step 6: Verify tests still pass
        test_result = self._run_tests(test_file)
        return ImplementationResult(
            status="complete" if test_result.passed else "failed",
            test_coverage=test_result.coverage,
            metrics=test_result.metrics
        )
```

## QA Gate Governance (Validator Agent)

### Gate Decisions

Validator agent makes deterministic gate decisions:

```yaml
gate_decisions:
  PASS:
    criteria:
      - All acceptance criteria met
      - No high-severity issues
      - Test coverage ≥ 70%
      - No security vulnerabilities

  CONCERNS:
    criteria:
      - All acceptance criteria met
      - Medium-severity issues present
      - Test coverage < 70% but ≥ 50%
      - Non-critical NFR violations

  FAIL:
    criteria:
      - Missing acceptance criteria
      - High-severity issues present
      - Test coverage < 50%
      - Security vulnerabilities found

  WAIVED:
    criteria:
      - FAIL/CONCERNS conditions present
      - Explicit waiver with business justification
      - Approved by product owner
```

### Gate File Structure

```yaml
# docs/qa/gates/1.7-bmad-agent-integration.yml
schema: 1
story: "1.7"
story_title: "BMAD Agent Best Practices Integration"
gate: "PASS"
status_reason: "All ACs met, 69 tests passing, quality score 98/100"
reviewer: "Quinn (Test Architect)"
updated: "2025-10-01T10:00:00Z"

quality_score: 98  # 100 - (20*FAILs) - (10*CONCERNS)

top_issues:
  - id: "DEPRECATE-001"
    severity: low
    finding: "datetime.utcnow() deprecated in Python 3.13+"
    suggested_action: "Replace with datetime.now(timezone.utc)"

  - id: "DOC-001"
    severity: low
    finding: "Optional documentation files not created"
    suggested_action: "Create quality-standards.md, agent-capabilities.md, langgraph-orchestration.md"

evidence:
  tests_reviewed: 69
  risks_identified: 2
  trace:
    ac_covered: [1, 2, 3, 4, 5, 6]  # All ACs have test coverage
    ac_gaps: []  # No gaps

nfr_validation:
  security:
    status: PASS
    notes: "No auth code touched, permissions enforced, Pydantic validation prevents injection"
  performance:
    status: PASS
    notes: "Keyword extraction optimized, tools loaded once at init"
  reliability:
    status: PASS
    notes: "69 tests passing, error handling comprehensive"
  maintainability:
    status: PASS
    notes: "Code well-structured, documentation complete"

recommendations:
  immediate: []  # No blocking issues
  future:
    - action: "Consider deprecation warnings cleanup"
      refs: ["langgraph_core/workflow_enhanced.py"]
    - action: "Complete optional documentation"
      refs: ["docs/bmad-integration/"]

waiver:
  active: false
```

### Gate Decision Logic

```python
class ValidatorAgent(BaseAgent):
    def make_gate_decision(self, story: Story, test_results: TestResults) -> GateDecision:
        # Collect evidence
        evidence = self._collect_evidence(story, test_results)

        # Assess risks
        risks = self._assess_risks(evidence)

        # Check NFRs
        nfr_status = self._validate_nfrs(evidence)

        # Apply deterministic rules
        gate = self._apply_gate_rules(evidence, risks, nfr_status)

        # Calculate quality score
        quality_score = self._calculate_quality_score(evidence, risks)

        return GateDecision(
            gate=gate,
            quality_score=quality_score,
            evidence=evidence,
            recommendations=self._generate_recommendations(evidence)
        )

    def _apply_gate_rules(self, evidence, risks, nfr_status):
        # Rule 1: High-severity issues → FAIL
        if any(issue.severity == "high" for issue in evidence.issues):
            return "FAIL"

        # Rule 2: NFR FAIL → FAIL
        if any(nfr.status == "FAIL" for nfr in nfr_status.values()):
            return "FAIL"

        # Rule 3: Medium-severity issues → CONCERNS
        if any(issue.severity == "medium" for issue in evidence.issues):
            return "CONCERNS"

        # Rule 4: NFR CONCERNS → CONCERNS
        if any(nfr.status == "CONCERNS" for nfr in nfr_status.values()):
            return "CONCERNS"

        # Rule 5: All clear → PASS
        return "PASS"
```

## Requirements Traceability

### Given-When-Then Format

Map acceptance criteria to tests using Given-When-Then:

```python
# Acceptance Criteria
"""
AC-1: Agents load persona from YAML config
AC-2: Agents call clarify_task() before execution
AC-3: Story file permissions prevent unauthorized edits
"""

# Test Traceability
"""
AC-1: Agent Persona Patterns (7 tests)
├─ test_orchestrator_loads_persona
│  Given: Orchestrator config exists
│  When: Agent initialized
│  Then: Persona loaded with role, style, core_principles
│
├─ test_analyst_loads_persona
│  Given: Analyst config exists
│  When: Agent initialized
│  Then: Persona loaded correctly
│
└─ [5 more tests...]

AC-2: Inquiry & Planning Protocols (5 tests)
├─ test_clarify_task_identifies_missing_context
│  Given: Incomplete context
│  When: clarify_task() called
│  Then: Returns clear=False with questions
│
├─ test_clarify_task_proceeds_with_complete_context
│  Given: Complete context
│  When: clarify_task() called
│  Then: Returns clear=True
│
└─ [3 more tests...]

AC-3: Story File Permissions (18 tests)
├─ test_developer_can_edit_dev_record
│  Given: Developer agent
│  When: Edit "Dev Agent Record" section
│  Then: Edit allowed
│
├─ test_developer_cannot_edit_qa_results
│  Given: Developer agent
│  When: Edit "QA Results" section
│  Then: Edit blocked with PermissionError
│
└─ [16 more tests...]
"""
```

### Traceability Implementation

```python
from src.core.requirements_tracer import RequirementsTracer

class RequirementsTracer:
    def calculate_coverage(self, story: Story, tests: List[Test]) -> CoverageReport:
        # Parse acceptance criteria
        acs = self.parse_acceptance_criteria(story)

        # Parse test docstrings for Given-When-Then
        test_mappings = self.parse_test_mappings(tests)

        # Map tests to ACs
        coverage = {}
        for ac in acs:
            matched_tests = [
                test for test in test_mappings
                if ac.id in test.covered_acs
            ]
            coverage[ac.id] = matched_tests

        # Calculate metrics
        total_acs = len(acs)
        covered_acs = len([ac for ac, tests in coverage.items() if tests])
        coverage_percentage = (covered_acs / total_acs) * 100

        return CoverageReport(
            total_acs=total_acs,
            covered_acs=covered_acs,
            coverage_percentage=coverage_percentage,
            missing_tests=[ac for ac, tests in coverage.items() if not tests],
            test_mappings=coverage
        )
```

## Story File Permissions

### Permission Rules

```yaml
# config/agents/developer_config.yaml
story_file_permissions:
  allowed_sections:
    - "Dev Agent Record"
    - "Agent Model Used"
    - "Debug Log References"
    - "Completion Notes"
    - "File List"

  forbidden_sections:
    - "Acceptance Criteria"
    - "Tasks / Subtasks"
    - "QA Results"
    - "Status"

# config/agents/validator_config.yaml
story_file_permissions:
  allowed_sections:
    - "QA Results"
    - "Review Date"
    - "Code Quality Assessment"
    - "Compliance Check"
    - "Gate Status"

  forbidden_sections:
    - "Acceptance Criteria"
    - "Tasks / Subtasks"
    - "Dev Agent Record"
    - "Status"
```

### Permission Enforcement

```python
from src.core.story_file_manager import StoryFileManager

class StoryFileManager:
    def validate_edit(
        self,
        agent_id: str,
        section_name: str
    ) -> PermissionResult:
        """Validate agent can edit specified section"""
        agent_config = self._load_agent_config(agent_id)
        permissions = agent_config.story_file_permissions

        if section_name in permissions.allowed_sections:
            return PermissionResult(allowed=True)

        if section_name in permissions.forbidden_sections:
            return PermissionResult(
                allowed=False,
                reason=f"{agent_id} cannot edit {section_name}"
            )

        # Default: deny
        return PermissionResult(
            allowed=False,
            reason=f"Section {section_name} not in allowed list"
        )

    def apply_edit(
        self,
        agent_id: str,
        file_path: str,
        section_name: str,
        new_content: str
    ) -> EditResult:
        """Apply edit with permission check"""
        permission = self.validate_edit(agent_id, section_name)

        if not permission.allowed:
            raise PermissionError(permission.reason)

        # Parse story file
        sections = self._parse_sections(file_path)

        # Update section
        sections[section_name] = new_content

        # Write back
        self._write_sections(file_path, sections)

        return EditResult(success=True)
```

## Test Report Generation

Automated test reports in [tests/reports/](../../tests/reports/):

```bash
tests/reports/
├── story-1-7-test-report-20251001.md
├── coverage-report-20251001.html
└── traceability-matrix-20251001.csv
```

### Test Report Structure

```markdown
# Story 1.7 Test Report

**Date**: 2025-10-01
**Story**: BMAD Agent Best Practices Integration
**Total Tests**: 69
**Passed**: 69
**Failed**: 0
**Coverage**: 100%

## Requirements Traceability

| AC | Description | Tests | Coverage |
|----|-------------|-------|----------|
| AC-1 | Persona Patterns | 7 | 100% |
| AC-2 | Inquiry Protocols | 5 | 100% |
| AC-3 | Capability Patterns | 3 | 100% |
| AC-4 | Quality Standards | 33 | 100% |
| AC-5 | YAML Config System | 11 | 100% |
| AC-6 | LangGraph Integration | 14 | 100% |

## Test Results by Category

### AC-1: Agent Persona Patterns (7 tests)
✓ test_orchestrator_loads_persona
✓ test_analyst_loads_persona
✓ test_knowledge_loads_persona
✓ test_developer_loads_persona
✓ test_validator_loads_persona
✓ test_persona_validation
✓ test_core_principles_loaded

### AC-2: Inquiry & Planning Protocols (5 tests)
✓ test_clarify_task_identifies_missing_context
✓ test_clarify_task_proceeds_with_complete_context
✓ test_keyword_extraction
✓ test_inquiry_pattern_matching
✓ test_clarification_request_structure

[... additional sections ...]

## Quality Metrics

- **Code Coverage**: 100% (69/69 tests)
- **Quality Score**: 98/100
- **Gate Decision**: PASS
- **Execution Time**: 0.47s
```

## References

- **Story 1.7**: [story-1-7-bmad-agent-integration.md](../stories/epic-1/story-1-7-bmad-agent-integration.md)
- **Validator Agent**: [src/agents/validator_agent.py](../../src/agents/validator_agent.py)
- **Developer Agent**: [src/agents/developer_agent.py](../../src/agents/developer_agent.py)
- **Requirements Tracer**: [src/core/requirements_tracer.py](../../src/core/requirements_tracer.py)
- **Story File Manager**: [src/core/story_file_manager.py](../../src/core/story_file_manager.py)
