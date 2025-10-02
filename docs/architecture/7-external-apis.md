# 7. External APIs

## Yahoo Finance API (via MCP)

- **Purpose:** Real-time and historical market data for FX pairs and related financial instruments
- **Documentation:** Accessed through yahoo-finance-mcp server configuration
- **Base URL(s):** Handled internally by MCP server
- **Authentication:** API key if required, managed by MCP server
- **Rate Limits:** Dependent on tier, typically 100 requests/minute for free tier

**Key Endpoints Used:**
- `get_quote` - Current FX pair quotes and prices
- `get_historical` - Historical price data for trend analysis
- `search_symbols` - Find currency pair symbols

**Integration Notes:** MCP server handles rate limiting and caching. Agents should batch requests where possible to minimize API calls.

## Google News API (via MCP)

- **Purpose:** News articles and sentiment for currency markets and central bank communications
- **Documentation:** Accessed through google-news-mcp server configuration
- **Base URL(s):** Handled internally by MCP server
- **Authentication:** API key managed by MCP server
- **Rate Limits:** Varies by plan, typically 1000 requests/day

**Key Endpoints Used:**
- `search_news` - Search for market-specific news
- `get_headlines` - Top financial headlines
- `filter_by_date` - Time-windowed news retrieval

**Integration Notes:** Focus queries on specific currency pairs and central banks. Use date filters to ensure "this week" accuracy.

## Reuters API (via MCP)

- **Purpose:** Authoritative financial news source for validation and fact-checking
- **Documentation:** Accessed through reuters-mcp server configuration
- **Base URL(s):** Handled internally by MCP server
- **Authentication:** Premium API key required, managed by MCP server
- **Rate Limits:** Premium tier dependent, typically 500 requests/hour

**Key Endpoints Used:**
- `get_market_news` - Verified market news and analysis
- `get_central_bank_news` - Official central bank communications
- `verify_story` - Fact-check against Reuters database

**Integration Notes:** Reserved for validation agent to minimize costs. Used as authoritative source for conflict resolution.
