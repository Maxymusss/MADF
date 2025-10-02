# 11. Development Workflow

## Local Development Setup

### Prerequisites
```bash
# Required software
node --version  # v20.x or higher
python --version  # 3.11 or higher
npm --version  # Latest
pip --version  # Latest
```

### Initial Setup
```bash
# Clone repository
git clone <repository-url>
cd MADF

# Install Node.js dependencies
npm install

# Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# ANTHROPIC_API_KEY=your_key
# YAHOO_FINANCE_API_KEY=your_key
# GOOGLE_NEWS_API_KEY=your_key
# REUTERS_API_TOKEN=your_key

# Create required directories
python scripts/setup.py

# Verify setup
npm run verify
python -m pytest tests/unit/test_models.py
```

### Development Commands
```bash
# Start all services
./scripts/start-agents.sh

# Start PM Agent only
cd agents/orchestrator && npm start

# Start Research Agent 1 only
cd agents/python && python -m research.yahoo_agent

# Start Research Agent 2 only
cd agents/python && python -m research.news_agent

# Start Validator Agent only
cd agents/python && python -m validator.validator_agent

# Run tests
npm test  # Node.js tests
pytest  # Python tests

# Monitor logs
tail -f logs/agents/*/errors/*.json

# Clean up old data
python scripts/cleanup.py
```

## Environment Configuration

### Required Environment Variables
```bash
# .env file

# LLM Configuration
ANTHROPIC_API_KEY=sk-ant-xxx
CLAUDE_MODEL_ORCHESTRATOR=claude-3-opus-latest
CLAUDE_MODEL_EXECUTION=claude-3-sonnet-latest

# MCP Tool APIs
YAHOO_FINANCE_API_KEY=xxx
GOOGLE_NEWS_API_KEY=xxx
REUTERS_API_TOKEN=xxx

# System Configuration
LOG_LEVEL=INFO
MESSAGE_POLL_INTERVAL=1.0
CACHE_TTL_SECONDS=300
MAX_RETRY_ATTEMPTS=3

# File Paths (relative to project root)
MESSAGE_DIR=data/messages
LOG_DIR=logs
CACHE_DIR=data/cache
STATE_DIR=data/state
```
