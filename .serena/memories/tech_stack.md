# MADF Tech Stack

## Core Technologies
- **Python 3.13+**: Main runtime (requires >=3.13)
- **Node.js 22.19.0**: MCP proxy and tool orchestration
- **LangGraph**: Multi-agent workflow orchestration 
- **LangChain + Anthropic**: LLM integration

## Python Dependencies
### Core Framework
- `langgraph>=0.0.55`: State machine orchestration
- `langchain>=0.1.0` + `langchain-anthropic>=0.1.0`: LLM framework
- `mcp-use>=0.1.18`: Multi-server MCP tool loading

### Data Processing
- `pandas>=2.0.0`: Data manipulation
- `numpy>=1.24.0`: Numerical computing
- `pendulum>=2.1.2`: Timezone-aware datetime

### Async & HTTP
- `aiofiles>=23.1.0`: Async file operations
- `aiohttp>=3.8.0`: Async HTTP client
- `asyncio-mqtt>=0.13.0`: MQTT client

### Development Tools
- `black>=23.0.0`: Code formatter
- `flake8>=6.0.0`: Linting
- `mypy>=1.5.0`: Type checking
- `pytest>=7.4.0`: Testing framework

## Node.js Dependencies
### MCP Integration
- `@modelcontextprotocol/sdk@^1.18.1`: MCP SDK
- `mcp-use@^0.1.18`: Tool loading library
- `@playwright/mcp@^0.0.39`: Browser automation

### Financial Data
- `alphavantage@^2.5.0`: Alpha Vantage API
- `iex-cloud@^2.2.0`: IEX Cloud API
- `newsapi@^2.4.1`: News API

### Utilities
- `dotenv@^17.2.2`: Environment management
- `@gongrzhe/server-gmail-autoauth-mcp@^1.1.11`: Gmail integration

## Package Management
- **Python**: uv (preferred) or pip
- **Node.js**: npm