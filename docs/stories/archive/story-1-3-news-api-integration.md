# Story 1.3: Free News API Integration via mcp-use

**Epic**: Epic 1 - Multi-Agent Development Framework MVP
**Sprint**: Phase 1 (Week 2)
**Estimated Effort**: 4-5 days
**Dependencies**: Story 1.1 (LangGraph Setup), Story 1.2 (BMAD Planning)

## User Story

As a **financial research system operator**,
I want **automated news collection from free APIs through mcp-use client**,
so that **research agents can gather market news for weekly commentary generation**.

## Acceptance Criteria

### AC1: mcp-use Client Setup
- [ ] Configure mcp-use to connect to free news APIs via HTTP bridge
- [ ] Set up Node.js bridge service for Python ↔ TypeScript communication
- [ ] Implement API key management for multiple news sources
- [ ] Test connection to all configured news APIs

### AC2: Research Agent Integration
- [ ] Implement Research Agent node with multi-source news access
- [ ] Add async operations for concurrent API calls
- [ ] Integrate with LangGraph state management from Story 1.1
- [ ] Test agent execution with real API data

### AC3: Geographic Coverage
- [ ] EM Asia markets: CN, TW, KR, HK, SG, TH, MY, PH, ID, IN
- [ ] US markets with appropriate timezone awareness
- [ ] Configure region-specific search terms and filters
- [ ] Validate coverage completeness with test queries

### AC4: Market Coverage
- [ ] FX & rates focused data collection
- [ ] Equity/commodities only for outsized moves (>5% daily moves)
- [ ] Currency pair specific searches (USD/JPY, EUR/USD, etc.)
- [ ] Interest rate policy and central bank communications

### AC5: API Integration
- [ ] NewsAPI (primary) - comprehensive news search
- [ ] Yahoo Finance - market data and financial news
- [ ] Alpha Vantage - economic indicators and market analysis
- [ ] Google News - supplementary coverage and verification
- [ ] Implement rate limiting and quota management

### AC6: Basic Error Handling
- [ ] Handle API failures with retry logic (3 attempts, exponential backoff)
- [ ] Source fallback when primary API unavailable
- [ ] Graceful degradation with partial data collection
- [ ] Error logging and notification system

### AC7: Data Formatting
- [ ] Structure news data for weekly analysis and commentary generation
- [ ] Standardized data model for all news sources
- [ ] Content filtering and relevance scoring
- [ ] Timezone normalization and date handling

## Technical Implementation Details

### API Configuration
```json
// .claude/mcp-tools/configs/news-apis.json
{
  "newsapi": {
    "base_url": "https://newsapi.org/v2",
    "endpoints": {
      "everything": "/everything",
      "top_headlines": "/top-headlines"
    },
    "rate_limit": "1000/day",
    "categories": ["business"]
  },
  "yahoo_finance": {
    "base_url": "https://query1.finance.yahoo.com",
    "endpoints": {
      "news": "/v1/finance/search",
      "quotes": "/v8/finance/chart"
    },
    "rate_limit": "unlimited"
  },
  "alpha_vantage": {
    "base_url": "https://www.alphavantage.co",
    "endpoints": {
      "news": "/query?function=NEWS_SENTIMENT",
      "forex": "/query?function=FX_DAILY"
    },
    "rate_limit": "25/day"
  },
  "google_news": {
    "base_url": "https://news.google.com/rss",
    "rate_limit": "unlimited",
    "format": "rss"
  }
}
```

### News Data Model
```python
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class NewsSource(str, Enum):
    NEWSAPI = "newsapi"
    YAHOO_FINANCE = "yahoo_finance"
    ALPHA_VANTAGE = "alpha_vantage"
    GOOGLE_NEWS = "google_news"

class MarketType(str, Enum):
    FX = "fx"
    RATES = "rates"
    EQUITY = "equity"
    COMMODITY = "commodity"

class NewsItem(BaseModel):
    id: str = Field(..., description="Unique news item identifier")
    title: str = Field(..., description="News headline")
    content: Optional[str] = Field(None, description="Full article content")
    summary: Optional[str] = Field(None, description="Article summary")
    source: NewsSource = Field(..., description="Data source")
    url: HttpUrl = Field(..., description="Article URL")
    published_at: datetime = Field(..., description="Publication timestamp")
    market_type: MarketType = Field(..., description="Market category")
    regions: List[str] = Field(..., description="Relevant geographic regions")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Sentiment analysis")

class NewsCollection(BaseModel):
    collection_id: str = Field(..., description="Collection identifier")
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    time_range: Dict[str, datetime] = Field(..., description="Start and end time")
    items: List[NewsItem] = Field(..., description="News items")
    total_items: int = Field(..., description="Total items collected")
    sources_used: List[NewsSource] = Field(..., description="Data sources queried")
    errors: List[str] = Field(default_factory=list, description="Collection errors")
```

### HTTP Bridge Service
```typescript
// mcp_bridge/news_service.ts
import express from 'express';
import { McpClient } from 'mcp-use';

class NewsBridgeService {
  private newsApiClient: McpClient;
  private yahooClient: McpClient;
  private alphaVantageClient: McpClient;

  async collectNews(params: {
    regions: string[];
    marketTypes: string[];
    timeRange: { start: string; end: string };
  }): Promise<NewsCollection> {
    // Parallel collection from all sources
    const [newsApiData, yahooData, alphaVantageData] = await Promise.allSettled([
      this.collectFromNewsAPI(params),
      this.collectFromYahoo(params),
      this.collectFromAlphaVantage(params)
    ]);

    // Merge and deduplicate results
    return this.mergeNewsData([newsApiData, yahooData, alphaVantageData]);
  }
}
```

### Research Agent Implementation
```python
# langgraph_core/agents/research.py
import asyncio
import aiohttp
from typing import Dict, List
from ..models.state import WorkflowState
from ..models.news import NewsCollection, NewsItem

async def research_agent(state: WorkflowState) -> WorkflowState:
    """
    Research Agent - Collects news data from multiple free APIs
    """
    try:
        # Extract requirements from BMAD plan
        plan = state.plan
        regions = plan.get("geographic_coverage", [])
        market_types = plan.get("market_types", ["fx", "rates"])
        time_range = plan.get("time_range", {})

        # Configure news collection parameters
        collection_params = {
            "regions": regions,
            "market_types": market_types,
            "time_range": time_range
        }

        # Collect news from HTTP bridge service
        news_collection = await collect_news_via_bridge(collection_params)

        # Store results in workflow state
        state.research_data = {
            "news_collection": news_collection.model_dump(),
            "collection_summary": {
                "total_items": news_collection.total_items,
                "sources_used": news_collection.sources_used,
                "time_range": news_collection.time_range,
                "errors": news_collection.errors
            }
        }

        state.current_agent = "dev"
        return state

    except Exception as e:
        state.errors.append(f"Research agent error: {str(e)}")
        raise

async def collect_news_via_bridge(params: Dict) -> NewsCollection:
    """
    Collect news data via HTTP bridge to Node.js mcp-use service
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:3001/api/collect-news",
            json=params,
            timeout=aiohttp.ClientTimeout(total=300)  # 5 minute timeout
        ) as response:
            if response.status == 200:
                data = await response.json()
                return NewsCollection.model_validate(data)
            else:
                raise Exception(f"News collection failed: {response.status}")
```

## Geographic Coverage Requirements

### EM Asia Markets
- **China (CN)**: CNY/USD, Shanghai Composite, PBOC policy
- **Taiwan (TW)**: TWD/USD, Taiwan Stock Exchange, CBC policy
- **Korea (KR)**: KRW/USD, KOSPI, BoK policy
- **Hong Kong (HK)**: HKD/USD, Hang Seng, HKMA operations
- **Singapore (SG)**: SGD/USD, STI, MAS policy
- **Thailand (TH)**: THB/USD, SET Index, BoT policy
- **Malaysia (MY)**: MYR/USD, KLCI, BNM policy
- **Philippines (PH)**: PHP/USD, PSEi, BSP policy
- **Indonesia (ID)**: IDR/USD, JCI, BI policy
- **India (IN)**: INR/USD, Nifty/Sensex, RBI policy

### US Markets
- **FX**: USD/major pairs, DXY index
- **Rates**: Fed policy, Treasury yields, FOMC communications
- **Equity**: Major index moves if >2% daily
- **Commodities**: Oil, gold if significant Asia impact

## API Rate Limiting Strategy

### NewsAPI (Primary)
- 1000 requests/day limit
- Prioritize comprehensive search queries
- Cache results for 1 hour
- Use for broad market coverage

### Yahoo Finance (Supplementary)
- Unlimited requests
- Use for real-time price verification
- Focus on FX pairs and major indices
- Backup for NewsAPI failures

### Alpha Vantage (Targeted)
- 25 requests/day limit
- Reserve for sentiment analysis
- Use for economic indicators
- Only for high-priority events

### Google News (Verification)
- Unlimited RSS access
- Use for fact-checking and verification
- Supplement coverage gaps
- Alternative source validation

## File Structure
```
mcp_bridge/
├── package.json
├── src/
│   ├── news_service.ts      # Main bridge service
│   ├── api_clients/
│   │   ├── newsapi.ts      # NewsAPI client
│   │   ├── yahoo.ts        # Yahoo Finance client
│   │   ├── alpha_vantage.ts # Alpha Vantage client
│   │   └── google_news.ts  # Google News client
│   └── utils/
│       ├── rate_limiter.ts # Rate limiting utilities
│       └── deduplication.ts # Content deduplication

langgraph_core/
├── agents/
│   └── research.py         # Enhanced research agent
├── models/
│   └── news.py            # News data models
└── utils/
    ├── bridge_client.py   # HTTP bridge client
    └── news_processing.py # News filtering and scoring
```

## Testing Requirements

### Unit Tests
- Test news data model validation
- Test API client error handling
- Test rate limiting logic
- Test data deduplication

### Integration Tests
- Test HTTP bridge communication
- Test research agent with real API data
- Test error recovery with API failures
- Test geographic coverage completeness

### Performance Tests
- Test concurrent API calls
- Measure collection time for full coverage
- Test memory usage with large datasets
- Verify rate limiting effectiveness


## Testing Status 🧪

- [ ] **TESTED** - Testing pending
  - **Test Results**: TBD
  - **Unit Tests**: TBD
  - **Integration Tests**: TBD
  - **Test Date**: TBD

## Definition of Done

- [ ] All acceptance criteria completed and tested
- [ ] HTTP bridge service operational
- [ ] Research agent successfully collects multi-source news
- [ ] Geographic and market coverage validated
- [ ] Error handling and fallback mechanisms proven
- [ ] Ready for Story 1.4 (Weekly Commentary Generation)

## Risk Mitigation

**Risk**: API rate limits exceeded during testing
**Mitigation**: Implement request queuing, use test API keys, cache responses

**Risk**: HTTP bridge becomes bottleneck
**Mitigation**: Async operations, connection pooling, timeout handling

**Risk**: News relevance filtering ineffective
**Mitigation**: Iterative refinement of filtering rules, human validation

## Success Criteria

- Multi-source news collection operational
- Geographic coverage complete for EM Asia + US
- Research agent integrates with LangGraph workflow
- Error handling prevents workflow failures
- Foundation ready for commentary generation (Story 1.4)