# MADF Essential Commands

## Development Setup
```bash
# Install Python dependencies (preferred)
uv sync

# Alternative Python setup
pip install -r requirements.txt

# Install Node.js dependencies
npm install

# Check installation status
python --version  # Should be 3.13+
node --version     # Should be 22.19.0+
npm list mcp-use   # Verify MCP integration
```

## Running the Framework
```bash
# Main MADF entry point
python main.py

# Multi-agent framework
python run_multi_agent_framework.py

# Product manager agent
python agents/product_manager_agent.py

# Simple test (Windows-compatible)
python simple_test.py

# Story 1.1 verification tests
python verify_story_1_1.py
python run_story_1_1_tests.py
```

## NPM Scripts (defined in package.json)
```bash
# Framework utilities
npm run startup          # Manual startup
npm run health-check     # System health check
npm run load-tools       # Load essential tools
npm run tool-stats       # Tool usage statistics
npm run update-tools     # Update essential tools
npm run analyze-tools    # Tool analysis

# MCP Proxy services
npm run mcp-proxy        # Main MCP proxy server
npm run fs-proxy         # Filesystem proxy
npm run coordinator      # Coordinator service
```

## Testing & Quality
```bash
# Run tests
pytest                   # Full test suite
pytest tests/           # Specific test directory

# Code quality
black .                 # Format code
flake8 .               # Lint code
mypy .                 # Type checking
```

## Development Tools
```bash
# Version control
git status
git add .
git commit -m "message"

# Directory navigation (Windows)
dir                    # List directory contents
cd path               # Change directory
ls                    # Unix-style listing (if available)

# Process management (Windows)
tasklist              # List running processes
taskkill /PID <pid>   # Kill process by PID
```

## Project Structure Navigation
```bash
# View project layout
tree                  # If tree command available
ls -la               # Detailed directory listing

# Key directories
ls agents/           # Agent implementations
ls projects/         # Individual projects (alphaseek, totorich, etc.)
ls agent_workspace/  # Agent communication files
ls .claude/          # Framework configuration
```