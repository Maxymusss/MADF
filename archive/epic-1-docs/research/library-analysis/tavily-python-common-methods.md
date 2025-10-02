# tavily-python - Commonly Used Methods

**Library**: tavily-python
**Type**: Direct Python Library
**Purpose**: AI-powered web search API
**Documentation**: https://docs.tavily.com/

---

## Installation & Authentication

```python
from tavily import TavilyClient

# Authentication
client = TavilyClient(api_key="your_api_key_here")
# Or use TAVILY_API_KEY environment variable
```

---

## Core Methods

### 1. search()

**Purpose**: Comprehensive web search with advanced options

**Signature**:
```python
search(
    query: str,
    max_results: int = 5,
    search_depth: str = "basic",  # "basic" or "advanced"
    include_answer: bool = False,
    include_raw_content: bool = False,
    include_images: bool = False,
    include_domains: list[str] = None,
    exclude_domains: list[str] = None,
    **kwargs
) -> dict
```

**Parameters**:
- `query` (required): Search query string
- `max_results`: Number of results (default 5)
- `search_depth`: "basic" (faster) or "advanced" (comprehensive)
- `include_answer`: Return AI-generated answer
- `include_raw_content`: Include full page content
- `include_images`: Include relevant images
- `include_domains`: Whitelist domains
- `exclude_domains`: Blacklist domains

**Returns**:
```python
{
    "query": "original query",
    "answer": "AI-generated answer (if requested)",
    "results": [
        {
            "title": "Page title",
            "url": "https://...",
            "content": "Relevant snippet",
            "raw_content": "Full content (if requested)",
            "score": 0.95
        }
    ],
    "images": ["url1", "url2"]  # if requested
}
```

**Usage Priority**: HIGH - Primary search method

**Example**:
```python
result = client.search(
    query="Python async best practices",
    max_results=5,
    search_depth="advanced",
    include_answer=True
)
print(result["answer"])
for r in result["results"]:
    print(f"{r['title']}: {r['url']}")
```

---

### 2. qna_search()

**Purpose**: Q&A optimized search returning direct answer

**Signature**:
```python
qna_search(query: str, **kwargs) -> dict
```

**Parameters**:
- `query` (required): Question string

**Returns**:
```python
{
    "query": "original question",
    "answer": "Direct answer to question",
    "results": [...]  # Supporting sources
}
```

**Usage Priority**: HIGH - Quick answers

**Example**:
```python
result = client.qna_search("What is the capital of France?")
print(result["answer"])  # "Paris"
```

---

### 3. get_search_context()

**Purpose**: RAG-optimized context retrieval for LLM prompts

**Signature**:
```python
get_search_context(
    query: str,
    max_results: int = 5,
    search_depth: str = "basic",
    max_tokens: int = 4000,
    **kwargs
) -> str
```

**Parameters**:
- `query` (required): Search query
- `max_results`: Number of sources
- `search_depth`: "basic" or "advanced"
- `max_tokens`: Maximum context tokens

**Returns**:
- String of concatenated, relevant context optimized for RAG

**Usage Priority**: HIGH - LangGraph agent integration

**Example**:
```python
context = client.get_search_context(
    query="LangGraph best practices",
    max_results=5,
    search_depth="advanced",
    max_tokens=4000
)
# Use context in LLM prompt
prompt = f"Context: {context}\n\nQuestion: How to use LangGraph?"
```

---

### 4. extract()

**Purpose**: Extract content from specific URLs

**Signature**:
```python
extract(
    urls: list[str],
    extract_depth: str = "basic",  # "basic" or "advanced"
    format: str = "markdown",  # "markdown" or "html"
    include_images: bool = False,
    **kwargs
) -> dict
```

**Parameters**:
- `urls` (required): List of URLs to extract
- `extract_depth`: "basic" (main content) or "advanced" (comprehensive)
- `format`: Output format
- `include_images`: Include image URLs

**Returns**:
```python
{
    "results": [
        {
            "url": "https://...",
            "content": "Extracted content",
            "images": ["url1", "url2"]  # if requested
        }
    ]
}
```

**Usage Priority**: MEDIUM - Targeted content extraction

**Example**:
```python
result = client.extract(
    urls=["https://docs.python.org/3/library/asyncio.html"],
    extract_depth="advanced",
    format="markdown"
)
print(result["results"][0]["content"])
```

---

### 5. crawl()

**Purpose**: Multi-page crawling from seed URL

**Signature**:
```python
crawl(
    url: str,
    max_depth: int = 3,
    max_breadth: int = 10,
    instructions: str = None,
    **kwargs
) -> dict
```

**Parameters**:
- `url` (required): Starting URL
- `max_depth`: Maximum crawl depth
- `max_breadth`: Maximum pages per level
- `instructions`: AI guidance for crawling

**Returns**:
```python
{
    "pages": [
        {
            "url": "https://...",
            "content": "Page content",
            "depth": 1
        }
    ]
}
```

**Usage Priority**: LOW - Specialized use cases

**Example**:
```python
result = client.crawl(
    url="https://docs.python.org/3/",
    max_depth=2,
    max_breadth=5,
    instructions="Focus on asyncio documentation"
)
```

---

## MADF Implementation

**File**: [src/integrations/tavily_client.py](../../src/integrations/tavily_client.py)

**Implemented Methods** (4):
1. `search(query, max_results, search_depth, ...)` - Comprehensive search
2. `qna_search(query)` - Q&A optimized
3. `get_search_context(query, max_results, max_tokens)` - RAG context
4. `extract(urls, extract_depth, format)` - URL extraction

**Not Implemented**:
- `crawl()` - Not needed for current use cases

---

## Tool Count Summary

**Total tavily-python Methods**: 5
**Commonly Used**: 4 methods (80% of use cases)
**MADF Implementation**: 4 methods

**Priority Breakdown**:
- **HIGH (3 methods)**: search(), qna_search(), get_search_context()
- **MEDIUM (1 method)**: extract()
- **LOW (1 method)**: crawl()

---

## Performance Characteristics

- **Speed**: Fast (optimized API, typically <2s)
- **Search Depth**:
  - "basic": Faster, fewer sources
  - "advanced": Comprehensive, slower (3-5s)
- **Rate Limits**: Depends on plan (check API dashboard)
- **Caching**: Server-side (recent queries cached)
- **Cost**: Per API call (check pricing)

---

## Testing Priority

**HIGH Priority** (must test):
1. `search()` - Core web search functionality
2. `get_search_context()` - RAG integration for LangGraph
3. `qna_search()` - Quick answers

**MEDIUM Priority**:
1. `extract()` - Targeted URL extraction
2. Search with domain filters

**LOW Priority**:
1. `crawl()` - Multi-page crawling
2. Image extraction

---

## Comparison: tavily-python vs Claude Code WebSearch vs Claude Code WebFetch

| Operation | tavily-python | WebSearch | WebFetch | Winner |
|-----------|---------------|-----------|----------|--------|
| Web search | ✓ Advanced | ✓ Basic | ✗ | tavily (depth) |
| Direct answer | ✓ qna_search | ✗ | ✗ | tavily (only option) |
| RAG context | ✓ Optimized | ✗ | ✗ | tavily (only option) |
| URL extraction | ✓ extract | ✗ | ✓ | Tie |
| Domain filter | ✓ | ✓ | ✗ | Tie |
| Multi-source | ✓ | ✓ | ✗ | Tie |
| Speed | Medium (2-5s) | Fast (<1s) | Medium (1-3s) | WebSearch |
| Cost | Paid API | Free (built-in) | Free (built-in) | WebSearch/WebFetch |
| Quality | High (AI-optimized) | Medium | Medium | tavily |

**tavily-python Strengths**:
- Best for comprehensive research (multiple sources)
- AI-generated answers (qna_search)
- RAG-optimized context (get_search_context)
- Domain filtering
- Content quality scoring

**Claude Code WebSearch Strengths**:
- Best for quick lookups
- No API costs
- Built-in integration
- Simple domain filtering

**Claude Code WebFetch Strengths**:
- Best for single URL extraction
- AI-powered content analysis
- 15-minute cache
- No API costs

---

## Use Case Recommendations

**Use tavily-python when**:
- Need comprehensive multi-source research
- Want AI-generated answers
- Building RAG pipelines for LangGraph agents
- Need content quality scoring
- Require advanced domain filtering

**Use Claude Code WebSearch when**:
- Quick lookups for current info
- Simple searches without analysis
- Cost-conscious operations
- Built-in integration preferred

**Use Claude Code WebFetch when**:
- Extracting from single known URL
- Need AI-powered content analysis
- Repeated access to same URLs (cache benefit)
- Documentation retrieval

---

## LangGraph Integration Pattern

**Analyst Agent** (Story 1.2) uses tavily-python for research:

```python
from tavily import TavilyClient

# Initialize
tavily = TavilyClient()

# Research workflow
def research_topic(topic: str) -> str:
    # Get RAG context
    context = tavily.get_search_context(
        query=topic,
        max_results=5,
        search_depth="advanced",
        max_tokens=4000
    )
    return context

# Q&A workflow
def quick_answer(question: str) -> str:
    result = tavily.qna_search(question)
    return result["answer"]

# Comprehensive research
def deep_research(query: str) -> dict:
    result = tavily.search(
        query=query,
        max_results=10,
        search_depth="advanced",
        include_answer=True,
        include_raw_content=True
    )
    return result
```

---

## Error Handling

```python
from tavily import TavilyClient

try:
    client = TavilyClient(api_key="your_key")
    result = client.search("query")
except ValueError as e:
    # API key missing
    print(f"Auth error: {e}")
except Exception as e:
    # API errors
    print(f"Search failed: {e}")
```

---

## Best Practices

1. **Use get_search_context() for RAG**: Optimized for LLM prompts
2. **Use qna_search() for quick answers**: Faster than full search
3. **Cache results client-side**: Reduce API calls
4. **Use search_depth="basic" for speed**: Unless comprehensive results needed
5. **Set max_tokens appropriately**: Balance context vs. cost
6. **Use domain filters**: Improve result quality
7. **Handle rate limits**: Implement backoff/retry logic
