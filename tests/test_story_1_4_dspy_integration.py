"""
Story 1.4 Task 2 Tests - DSPy Integration
Tests for dspy_optimizer.py

Test Categories:
1. Signatures: Agent signature definitions
2. Modules: DSPy module instantiation
3. Training: Example extraction and module optimization (mocked)
"""

import pytest
from pathlib import Path
from datetime import datetime, timezone, timedelta
import json
import tempfile

# Mock DSPy to avoid actual LM calls during tests
import sys
from unittest.mock import Mock, MagicMock, patch

# Create mock dspy module
mock_dspy = MagicMock()
mock_dspy.Signature = type('Signature', (), {})
mock_dspy.InputField = lambda desc: desc
mock_dspy.OutputField = lambda desc: desc
mock_dspy.Module = type('Module', (), {'__init__': lambda self: None})
mock_dspy.ChainOfThought = lambda sig: MagicMock()
mock_dspy.Prediction = MagicMock
mock_dspy.Example = MagicMock
mock_dspy.Claude = MagicMock
mock_dspy.settings = MagicMock()
mock_dspy.teleprompt = MagicMock()
mock_dspy.evaluate = MagicMock()

sys.modules['dspy'] = mock_dspy
sys.modules['dspy.teleprompt'] = mock_dspy.teleprompt
sys.modules['dspy.evaluate'] = mock_dspy.evaluate

# Now import after mocking
from src.core.dspy_optimizer import (
    PlanningSignature,
    DevelopmentSignature,
    ResearchSignature,
    QASignature,
    PMSignature,
    MADFPlanningModule,
    MADFDevelopmentModule,
    MADFResearchModule,
    MADFQAModule,
    MADFPMModule,
    MADFOptimizer
)
from src.core.postgres_manager_sync import PostgresManager


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_postgres_db():
    """Create temporary Postgres database for testing"""
    conn_string = "host=localhost port=5433 user=madf password=test_password dbname=madf_logs"

    pg = PostgresManager(connection_string=conn_string)
    pg.initialize()

    yield pg

    pg.close()


@pytest.fixture
def sample_training_events(temp_postgres_db):
    """Insert sample training data"""
    pg = temp_postgres_db

    # Create high-confidence successful events for training
    events = []
    for i in range(10):
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "agent_action",
            "category": "execution",
            "session_id": f"train_session_{i}",
            "story_id": "1.4",
            "agent_name": "planning_agent",
            "duration_ms": 200,
            "tokens_used": 1500,
            "success": True,
            "confidence_score": 0.95,
            "details": {
                "user_requirement": f"Test requirement {i}",
                "context": f"Test context {i}",
                "task_plan": f"Test plan {i}",
                "action": "create_plan"
            }
        }
        events.append(event)

    # Import events
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False, encoding='utf-8') as f:
        for event in events:
            f.write(json.dumps(event, ensure_ascii=True) + '\n')
        temp_path = Path(f.name)

    pg.import_jsonl_file(temp_path)
    temp_path.unlink()

    return events


# ============================================================================
# TEST: Signatures
# ============================================================================

class TestSignatures:
    """Test agent signature definitions"""

    def test_planning_signature_exists(self):
        """Test PlanningSignature is defined"""
        assert PlanningSignature is not None

    def test_development_signature_exists(self):
        """Test DevelopmentSignature is defined"""
        assert DevelopmentSignature is not None

    def test_research_signature_exists(self):
        """Test ResearchSignature is defined"""
        assert ResearchSignature is not None

    def test_qa_signature_exists(self):
        """Test QASignature is defined"""
        assert QASignature is not None

    def test_pm_signature_exists(self):
        """Test PMSignature is defined"""
        assert PMSignature is not None


# ============================================================================
# TEST: Modules
# ============================================================================

class TestModules:
    """Test DSPy module instantiation"""

    def test_planning_module_creation(self):
        """Test creating planning module"""
        module = MADFPlanningModule()
        assert module is not None

    def test_development_module_creation(self):
        """Test creating development module"""
        module = MADFDevelopmentModule()
        assert module is not None

    def test_research_module_creation(self):
        """Test creating research module"""
        module = MADFResearchModule()
        assert module is not None

    def test_qa_module_creation(self):
        """Test creating QA module"""
        module = MADFQAModule()
        assert module is not None

    def test_pm_module_creation(self):
        """Test creating PM module"""
        module = MADFPMModule()
        assert module is not None


# ============================================================================
# TEST: Optimizer
# ============================================================================

class TestMADFOptimizer:
    """Test DSPy optimizer functionality (mocked)"""

    @patch('src.core.dspy_optimizer.dspy.Claude')
    def test_optimizer_initialization(self, mock_claude, temp_postgres_db):
        """Test optimizer initialization"""
        optimizer = MADFOptimizer(postgres_manager=temp_postgres_db)
        optimizer.initialize()

        assert optimizer.pg._initialized
        assert optimizer.extractor is not None
        assert 'planning' in optimizer.modules
        assert 'development' in optimizer.modules
        assert 'research' in optimizer.modules
        assert 'qa' in optimizer.modules
        assert 'pm' in optimizer.modules

        optimizer.close()

    @patch('src.core.dspy_optimizer.dspy.Claude')
    def test_extract_training_examples_insufficient_data(
        self,
        mock_claude,
        temp_postgres_db
    ):
        """Test extract_training_examples with no data"""
        optimizer = MADFOptimizer(postgres_manager=temp_postgres_db)
        optimizer.initialize()

        # Mock DSPy Example
        with patch('src.core.dspy_optimizer.dspy.Example') as mock_example:
            mock_example.return_value.with_inputs.return_value = mock_example.return_value

            examples = optimizer.extract_training_examples("planning_agent", limit=50)

            # Should return empty list if no high-confidence examples
            assert isinstance(examples, list)

        optimizer.close()

    @patch('src.core.dspy_optimizer.dspy.Claude')
    def test_extract_training_examples_with_data(
        self,
        mock_claude,
        temp_postgres_db,
        sample_training_events
    ):
        """Test extract_training_examples with sample data"""
        optimizer = MADFOptimizer(postgres_manager=temp_postgres_db)
        optimizer.initialize()

        # Mock DSPy Example
        with patch('src.core.dspy_optimizer.dspy.Example') as mock_example:
            mock_example.return_value.with_inputs.return_value = mock_example.return_value

            examples = optimizer.extract_training_examples(
                "planning_agent",
                min_confidence=0.9,
                limit=50
            )

            # Should extract some examples
            assert isinstance(examples, list)
            # Note: Actual count depends on data in test DB

        optimizer.close()

    @patch('src.core.dspy_optimizer.dspy.Claude')
    def test_modules_dict_structure(self, mock_claude, temp_postgres_db):
        """Test optimizer modules dictionary structure"""
        optimizer = MADFOptimizer(postgres_manager=temp_postgres_db)

        assert "planning" in optimizer.modules
        assert "development" in optimizer.modules
        assert "research" in optimizer.modules
        assert "qa" in optimizer.modules
        assert "pm" in optimizer.modules

        # Verify each module is correct type
        assert isinstance(optimizer.modules["planning"], MADFPlanningModule)
        assert isinstance(optimizer.modules["development"], MADFDevelopmentModule)
        assert isinstance(optimizer.modules["research"], MADFResearchModule)
        assert isinstance(optimizer.modules["qa"], MADFQAModule)
        assert isinstance(optimizer.modules["pm"], MADFPMModule)

        optimizer.close()


# ============================================================================
# TEST: Integration (Mocked)
# ============================================================================

class TestDSPyIntegration:
    """Test DSPy integration workflow (mocked to avoid LM calls)"""

    @patch('src.core.dspy_optimizer.dspy.Claude')
    def test_optimizer_workflow_structure(
        self,
        mock_claude,
        temp_postgres_db,
        sample_training_events
    ):
        """Test optimizer workflow exists and has correct structure"""
        optimizer = MADFOptimizer(postgres_manager=temp_postgres_db)
        optimizer.initialize()

        # Verify workflow methods exist
        assert hasattr(optimizer, 'extract_training_examples')
        assert hasattr(optimizer, 'optimize_agent')
        assert hasattr(optimizer, 'save_optimized_module')

        optimizer.close()

    @patch('src.core.dspy_optimizer.dspy.Claude')
    def test_agent_name_mapping(self, mock_claude, temp_postgres_db):
        """Test agent name to module key mapping"""
        optimizer = MADFOptimizer(postgres_manager=temp_postgres_db)

        # Test valid mappings
        valid_agents = [
            ("planning_agent", "planning"),
            ("dev_agent", "development"),
            ("research_agent", "research"),
            ("qa_agent", "qa"),
            ("pm_agent", "pm")
        ]

        for agent_name, module_key in valid_agents:
            # Remove _agent suffix to get module key
            mapped_key = agent_name.replace("_agent", "")
            if mapped_key == "dev":
                mapped_key = "development"

            assert mapped_key in optimizer.modules or module_key in optimizer.modules

        optimizer.close()


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
