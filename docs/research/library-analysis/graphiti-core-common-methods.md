# graphiti_core - Commonly Used Methods

**Library**: graphiti_core
**Type**: Direct Python Library
**Purpose**: Temporal knowledge graph for AI agents
**Documentation**: https://github.com/getzep/graphiti
**Database**: Requires Neo4j (v5.26+)

---

## Installation & Setup

```python
from graphiti_core import Graphiti
from graphiti_core.llm import OpenAIClient
from graphiti_core.embedder import OpenAIEmbedder

# Initialize
llm_client = OpenAIClient(api_key="your_key")
embedder = OpenAIEmbedder(api_key="your_key")

graphiti = Graphiti(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    llm_client=llm_client,
    embedder=embedder
)

# Initialize database (first time)
await graphiti.build_indices()
```

---

## Core Methods

### 1. add_episode()

**Purpose**: Add knowledge episode to graph (primary ingestion method)

**Signature**:
```python
async def add_episode(
    name: str,
    episode_body: str,
    source: str = "text",  # "text", "json", "message"
    source_description: str = None,
    group_id: str = None,
    uuid: str = None,
    **kwargs
) -> Episode
```

**Parameters**:
- `name` (required): Episode identifier
- `episode_body` (required): Content to add
  - `source='text'`: Plain text
  - `source='json'`: Structured JSON string (must be escaped)
  - `source='message'`: Conversation format
- `source`: Content type
- `source_description`: Context description
- `group_id`: Namespace for separate graphs
- `uuid`: Optional episode UUID

**Returns**: Episode object with UUID

**Usage Priority**: HIGH - Primary data ingestion

**Example**:
```python
# Plain text
episode = await graphiti.add_episode(
    name="Project Update",
    episode_body="MADF framework reached Story 1.3 completion",
    source="text",
    source_description="project status",
    group_id="madf_project"
)

# JSON structured data
episode = await graphiti.add_episode(
    name="Agent Config",
    episode_body='{"agent": "Analyst", "tools": ["Serena", "Context7"]}',
    source="json",
    group_id="madf_project"
)

# Conversation
episode = await graphiti.add_episode(
    name="User Chat",
    episode_body="user: How do I use LangGraph?\nassistant: LangGraph enables...",
    source="message"
)
```

**Processing**: Asynchronous - returns immediately, processes in background

---

### 2. search() [Hybrid Search]

**Purpose**: Search knowledge graph with fusion of semantic + keyword + graph methods

**Signature**:
```python
async def search(
    query: str,
    group_ids: list[str] = None,
    num_results: int = 10,
    **kwargs
) -> SearchResults
```

**Parameters**:
- `query` (required): Search query
- `group_ids`: Filter by group IDs
- `num_results`: Maximum results

**Returns**: Unified search results (nodes + facts)

**Usage Priority**: HIGH - Primary search interface

**Example**:
```python
results = await graphiti.search(
    query="LangGraph agent architecture",
    group_ids=["madf_project"],
    num_results=10
)
```

**Note**: Uses reciprocal rank fusion (RRF) combining semantic, BM25, and graph distance

---

### 3. search_nodes()

**Purpose**: Search for entity nodes with summaries

**Signature**:
```python
async def search_nodes(
    query: str,
    group_ids: list[str] = None,
    max_nodes: int = 10,
    center_node_uuid: str = None,
    entity_type: str = None  # Filter by entity type
) -> list[Node]
```

**Parameters**:
- `query` (required): Search query
- `group_ids`: Filter by groups
- `max_nodes`: Maximum nodes
- `center_node_uuid`: Center search around specific node
- `entity_type`: Filter (e.g., "Preference", "Procedure", "Requirement")

**Returns**:
```python
[
    {
        "uuid": "node-uuid",
        "name": "entity-name",
        "summary": "relationship summary",
        "labels": ["Entity", "Requirement"],
        "group_id": "madf_project",
        "created_at": "2025-01-15T10:30:00Z",
        "attributes": {}
    }
]
```

**Usage Priority**: HIGH - Entity discovery

**Example**:
```python
nodes = await graphiti.search_nodes(
    query="LangGraph agents",
    group_ids=["madf_project"],
    max_nodes=10,
    entity_type="Requirement"
)
```

---

### 4. search_facts() [Entity Edges]

**Purpose**: Search for relationships (facts) between entities

**Signature**:
```python
async def search_facts(
    query: str,
    group_ids: list[str] = None,
    max_facts: int = 10,
    center_node_uuid: str = None
) -> list[EntityEdge]
```

**Parameters**:
- `query` (required): Search query
- `group_ids`: Filter by groups
- `max_facts`: Maximum facts
- `center_node_uuid`: Center search around node

**Returns**:
```python
[
    {
        "uuid": "edge-uuid",
        "source_node_uuid": "source-uuid",
        "target_node_uuid": "target-uuid",
        "fact": "Analyst agent uses Serena MCP",
        "created_at": "2025-01-15T10:30:00Z",
        "expired_at": null,  # null if still valid
        "attributes": {}
    }
]
```

**Usage Priority**: HIGH - Relationship discovery

**Example**:
```python
facts = await graphiti.search_facts(
    query="agent tool usage",
    group_ids=["madf_project"],
    max_facts=10
)
```

---

### 5. get_episodes()

**Purpose**: Retrieve recent episodes from group

**Signature**:
```python
async def get_episodes(
    group_id: str = None,
    last_n: int = 10
) -> list[Episode]
```

**Parameters**:
- `group_id`: Target group (uses default if None)
- `last_n`: Number of recent episodes

**Returns**: List of Episode objects

**Usage Priority**: MEDIUM - Episode history

**Example**:
```python
episodes = await graphiti.get_episodes(
    group_id="madf_project",
    last_n=10
)
```

---

### 6. get_episode_by_id()

**Purpose**: Retrieve specific episode by UUID

**Signature**:
```python
async def get_episode_by_id(uuid: str) -> Episode
```

**Usage Priority**: LOW - Specific retrieval

---

### 7. delete_episode()

**Purpose**: Remove episode from graph

**Signature**:
```python
async def delete_episode(uuid: str) -> dict
```

**Usage Priority**: LOW - Cleanup operations

**Example**:
```python
result = await graphiti.delete_episode(uuid="episode-uuid")
# Returns: {"message": "Episode deleted successfully"}
```

---

### 8. delete_entity_edge()

**Purpose**: Remove specific fact/relationship

**Signature**:
```python
async def delete_entity_edge(uuid: str) -> dict
```

**Usage Priority**: LOW - Cleanup operations

---

### 9. get_entity_edge()

**Purpose**: Retrieve specific edge by UUID

**Signature**:
```python
async def get_entity_edge(uuid: str) -> EntityEdge
```

**Usage Priority**: LOW - Specific inspection

---

### 10. build_indices()

**Purpose**: Initialize database indices (setup only)

**Signature**:
```python
async def build_indices() -> None
```

**Usage Priority**: LOW - One-time setup

---

## Tool Count Summary

**Total graphiti_core Methods**: 10+ core methods
**Commonly Used**: 5 methods (80% of use cases)

**Priority Breakdown**:
- **HIGH (5 methods)**: add_episode(), search(), search_nodes(), search_facts(), get_episodes()
- **MEDIUM (2 methods)**: get_episode_by_id(), get_entity_edge()
- **LOW (3 methods)**: delete_episode(), delete_entity_edge(), build_indices()

---

## Performance Characteristics

- **Search Speed**: <100ms (excluding external API calls)
- **Latency Factors**:
  - Embedding API: 50-200ms
  - Neo4j query: 10-50ms
  - Graph complexity: O(log n) with indices
- **Real-time Updates**: Immediate integration (no batch recomputation)
- **Temporal Awareness**: Automatic time-based edge metadata
- **Database**: Requires Neo4j (local or cloud)

---

## Key Features

### Temporal Operations
- Automatically extracts timestamps from content
- Tracks relationship validity periods (`created_at`, `expired_at`)
- Queries support temporal filtering

### Entity Extraction
- Automatic entity and relationship extraction
- Custom entity types (Requirement, Preference, Procedure)
- Configurable via Pydantic models

### Search Fusion
- **Semantic**: Vector similarity (embeddings)
- **BM25**: Keyword matching
- **Graph**: Node distance and connectivity
- **RRF**: Reciprocal rank fusion for result merging

### Group-based Isolation
- Separate knowledge graphs via `group_id`
- Multi-tenant support
- Per-group episodic memory

---

## Testing Priority

**HIGH Priority** (must test):
1. `add_episode()` - Knowledge ingestion
2. `search()` - Unified hybrid search
3. `search_nodes()` - Entity discovery
4. `search_facts()` - Relationship discovery
5. Integration with Neo4j database

**MEDIUM Priority**:
1. `get_episodes()` - Episode retrieval
2. Custom entity types
3. Group-based isolation

**LOW Priority**:
1. Delete operations
2. Specific UUID lookups
3. Index management

---

## Comparison: graphiti_core vs Graphiti MCP vs Obsidian MCP

| Operation | graphiti_core | Graphiti MCP | Obsidian MCP | Winner |
|-----------|---------------|--------------|--------------|--------|
| Add knowledge | ✓ add_episode | ✓ add_memory | ✓ create_file | graphiti (structured) |
| Search | ✓ Hybrid | ✓ Hybrid | ✓ Basic | graphiti (fusion) |
| Relationships | ✓ Graph-based | ✓ Graph-based | ✓ Links | graphiti (temporal) |
| Speed | Fast (direct) | Medium (MCP) | Fast (files) | graphiti_core |
| Setup | Complex (Neo4j) | Complex (Neo4j) | Simple (vault) | Obsidian |
| Temporal | ✓ Native | ✓ Native | ✗ | graphiti |
| Cost | Neo4j + LLM | Neo4j + LLM | Free | Obsidian |

**graphiti_core Strengths**:
- Best for complex knowledge graphs
- Temporal relationship tracking
- Hybrid search (semantic + keyword + graph)
- Real-time updates
- Custom entity types
- Multi-tenant via groups

**Graphiti MCP Strengths**:
- Same as graphiti_core but via MCP protocol
- Better for non-Python environments
- Async queue-based processing

**Obsidian MCP Strengths**:
- Best for simple note linking
- No database setup
- Low cost
- Human-readable markdown

---

## Use Case Recommendations

**Use graphiti_core when**:
- Building AI agents with memory
- Need temporal relationship tracking
- Complex entity extraction required
- Multi-agent coordination (group_id isolation)
- RAG with structured knowledge
- Python-native integration (LangGraph)

**Use Obsidian MCP when**:
- Simple note management
- Human-readable format priority
- Low setup complexity
- No database infrastructure
- Basic linking sufficient

**Use Context7 MCP when**:
- Need library documentation
- External API references
- Up-to-date framework docs

---

## LangGraph Integration Pattern

**Knowledge Agent** (Story 1.3) uses graphiti_core:

```python
from graphiti_core import Graphiti

class KnowledgeAgent:
    def __init__(self):
        self.graphiti = Graphiti(...)

    async def store_knowledge(self, content: str, context: str):
        """Store new knowledge"""
        episode = await self.graphiti.add_episode(
            name=f"Knowledge_{datetime.now().isoformat()}",
            episode_body=content,
            source="text",
            source_description=context,
            group_id="madf_knowledge"
        )
        return episode.uuid

    async def retrieve_knowledge(self, query: str):
        """Retrieve relevant knowledge"""
        results = await self.graphiti.search(
            query=query,
            group_ids=["madf_knowledge"],
            num_results=10
        )
        return results

    async def find_related_entities(self, entity: str):
        """Find related entities"""
        nodes = await self.graphiti.search_nodes(
            query=entity,
            group_ids=["madf_knowledge"],
            max_nodes=5
        )
        return nodes
```

---

## Error Handling

```python
from graphiti_core import Graphiti
from graphiti_core.errors import GraphitiError

try:
    graphiti = Graphiti(uri="bolt://localhost:7687", ...)
    await graphiti.add_episode(name="test", episode_body="content")
except GraphitiError as e:
    print(f"Graphiti error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Best Practices

1. **Use group_id for isolation**: Separate graphs per project/user
2. **Async operations**: Always use `await` for all methods
3. **Initialize indices once**: Run `build_indices()` on first setup
4. **Batch episodes**: Process related content together
5. **Use search() for general queries**: Hybrid search automatically optimizes
6. **Use search_nodes() for entities**: When looking for specific entities
7. **Use search_facts() for relationships**: When relationship-focused
8. **Clean up old data**: Use delete methods to manage graph size
9. **Monitor Neo4j**: Watch database performance and memory
10. **Handle embeddings cost**: OpenAI embedding API calls add up

---

## Neo4j Setup

**Required** for graphiti_core:

```bash
# Docker (recommended)
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.26

# Access: http://localhost:7474
# Bolt: bolt://localhost:7687
```

**Minimum Requirements**:
- Neo4j 5.26+
- 4GB RAM (8GB recommended)
- 2GB disk space
