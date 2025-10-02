"""
Demo: Real Tests Catch Neo4j Authentication Failures
Shows difference between mock tests (always pass) vs real tests (catch actual errors)
"""

import pytest
from neo4j import GraphDatabase
from neo4j.exceptions import AuthError, ServiceUnavailable


class TestRealAuthenticationFailures:
    """Real tests that catch actual Neo4j authentication errors"""

    def test_valid_credentials_succeed(self):
        """REAL TEST: Valid credentials connect successfully"""
        # Using real credentials from .env
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "madf-dev-password")
        )

        # Real Neo4j connection - will fail if Neo4j down or wrong password
        driver.verify_connectivity()

        # If we get here, connection succeeded
        driver.close()
        assert True

    def test_invalid_password_fails(self):
        """REAL TEST: Invalid password raises AuthError"""
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "wrong_password_that_will_fail")
        )

        # Real test catches authentication failure
        with pytest.raises(AuthError) as exc_info:
            driver.verify_connectivity()

        # Verify we got real authentication error
        assert "unauthorized" in str(exc_info.value).lower() or "authentication" in str(exc_info.value).lower()

        driver.close()

    def test_invalid_user_fails(self):
        """REAL TEST: Invalid username raises AuthError"""
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("wrong_user", "madf-dev-password")
        )

        # Real test catches authentication failure
        with pytest.raises(AuthError) as exc_info:
            driver.verify_connectivity()

        # Verify we got real authentication error
        assert "unauthorized" in str(exc_info.value).lower() or "authentication" in str(exc_info.value).lower()

        driver.close()

    def test_wrong_port_fails(self):
        """REAL TEST: Wrong port raises ServiceUnavailable"""
        driver = GraphDatabase.driver(
            "bolt://localhost:9999",  # Wrong port
            auth=("neo4j", "madf-dev-password")
        )

        # Real test catches connection failure
        with pytest.raises(ServiceUnavailable):
            driver.verify_connectivity()

        driver.close()


class TestMockTestProblems:
    """Demonstrate how mock tests hide authentication failures"""

    def test_mock_always_passes_WRONG(self):
        """MOCK TEST (WRONG): Always passes even with invalid credentials"""
        from unittest.mock import MagicMock

        # Mock driver - doesn't actually connect to Neo4j
        mock_driver = MagicMock()
        mock_driver.verify_connectivity.return_value = True

        # This "passes" but proves nothing about real connection
        mock_driver.verify_connectivity()

        # Test passes even if:
        # - Neo4j is not running
        # - Password is wrong
        # - Network is down
        # - Port is blocked
        assert True  # Always passes - useless!

    def test_mock_hides_auth_errors_WRONG(self):
        """MOCK TEST (WRONG): Doesn't catch authentication failures"""
        from unittest.mock import MagicMock

        # Mock with wrong password - doesn't matter, mock ignores it
        mock_driver = MagicMock()
        mock_driver.verify_connectivity.return_value = True

        # This "succeeds" with wrong password
        result = mock_driver.verify_connectivity()

        # Test passes - but in production, this would fail!
        assert result == True  # False confidence!


def run_demo():
    """Run demo to show real vs mock tests"""
    print("\n" + "="*70)
    print("DEMO: Real Tests vs Mock Tests - Neo4j Authentication")
    print("="*70)

    print("\n[1] Testing with VALID credentials...")
    print("    Real test: Connects to actual Neo4j")
    try:
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "madf-dev-password")
        )
        driver.verify_connectivity()
        driver.close()
        print("    [OK] SUCCESS: Connected to Neo4j")
    except Exception as e:
        print(f"    [FAIL] FAILED: {e}")

    print("\n[2] Testing with INVALID password...")
    print("    Real test: Should catch AuthError")
    try:
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "wrong_password")
        )
        driver.verify_connectivity()
        driver.close()
        print("    [FAIL] PROBLEM: Should have failed but didn't!")
    except AuthError as e:
        print(f"    [OK] SUCCESS: Caught real authentication error")
        print(f"    Error: {e}")

    print("\n[3] Mock test with invalid password...")
    print("    Mock test: Always passes (BAD!)")
    from unittest.mock import MagicMock
    mock_driver = MagicMock()
    mock_driver.verify_connectivity.return_value = True
    result = mock_driver.verify_connectivity()
    print(f"    [WARN] Mock result: {result} - False confidence!")
    print("    Mock test passes even with wrong password (DANGEROUS!)")

    print("\n" + "="*70)
    print("CONCLUSION:")
    print("  Real tests catch actual errors: AuthError, ServiceUnavailable")
    print("  Mock tests hide errors: Always pass even when they shouldn't")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Run pytest tests
    print("Running pytest tests...")
    pytest.main([__file__, "-v", "--tb=short"])

    # Run demo
    run_demo()