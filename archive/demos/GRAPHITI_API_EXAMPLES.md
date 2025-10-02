# Graphiti Core API Examples

## Current Implementation vs Real Graphiti Core

### Our GraphitiClient Wrapper (src/core/graphiti_client.py)

#### Initialization
```python
from core.graphiti_client import GraphitiClient

# Initialize with environment variables
client = GraphitiClient()

# Environment variables used:
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=madf-dev-password
# OPENAI_API_KEY=sk-proj-...

# Connect to Neo4j
await client.initialize()
```

#### Add Episode (Our API)
```python
# Simple interface matching our tests
result = await client.add_episode(
    content="User implemented filesystem MCP integration",
    episode_type="implementation",
    source="test_suite",
    metadata={"story": "1.3", "component": "knowledge_agent"}
)

# Returns:
{
    "success": True,
    "episode_id": "ep_2025-09-30T11:22:48.999686",
    "content": "User implemented filesystem MCP integration",
    "type": "implementation",
    "timestamp": "2025-09-30T11:22:48.999686",
    "metadata": {"story": "1.3", "component": "knowledge_agent"}
}
```

#### Search Operations (Our API)
```python
# Search nodes
nodes = await client.search_nodes(
    query="filesystem MCP integration",
    limit=10
)

# Search facts
facts = await client.search_facts(
    query="knowledge graph operations",
    limit=10
)

# Search episodes
episodes = await client.search_episodes(
    query="filesystem integration"
)
```

---

## Real Graphiti Core API (graphiti-core 0.20.4)

### Initialization (Real API)
```python
from graphiti_core import Graphiti
from datetime import datetime

# Direct instantiation with parameters
graphiti = Graphiti(
    uri="bolt://localhost:7687",      # Changed from neo4j_uri
    user="neo4j",                      # Changed from neo4j_user
    password="madf-dev-password"       # Changed from neo4j_password
)

# Note: Parameters changed in v0.20.4
# OLD (v0.19.x): neo4j_uri, neo4j_user, neo4j_password
# NEW (v0.20.4): uri, user, password
```

### Add Episode (Real API)
```python
from graphiti_core.nodes import EpisodeType

# Real Graphiti Core signature (more complex)
result = await graphiti.add_episode(
    name="Filesystem MCP Implementation",           # Episode name
    episode_body="User implemented filesystem MCP integration with real file operations",
    source_description="MADF Test Suite",          # Source identifier
    reference_time=datetime.now(),                  # When event occurred
    source=EpisodeType.message,                     # Episode type enum
    group_id=None,                                  # Optional grouping
    uuid=None,                                      # Auto-generated if None
    update_communities=False,                       # Community detection
    entity_types=None,                              # Custom entity schemas
    excluded_entity_types=None,                     # Types to skip
    previous_episode_uuids=None,                    # Episode chains
    edge_types=None,                                # Custom edge schemas
    edge_type_map=None                              # Edge type mappings
)

# Returns: AddEpisodeResults
# {
#     episode: EpisodicNode,
#     nodes: list[EntityNode],
#     edges: list[EntityEdge],
#     communities: list[CommunityNode]
# }
```

### Search (Real API)
```python
# Unified search interface
results = await graphiti.search(
    query="filesystem MCP integration",             # Search text
    center_node_uuid=None,                          # Optional focus node
    group_ids=None,                                 # Filter by groups
    num_results=10,                                 # Result limit
    search_filter=None                              # SearchFilters object
)

# Returns: list[EntityEdge]
# Each result contains:
# - fact: str (relationship description)
# - uuid: str (edge ID)
# - source_node_uuid: str
# - target_node_uuid: str
# - created_at: datetime
# - expired_at: datetime | None
```

### Advanced Search with Filters
```python
from graphiti_core.search.search_filters import SearchFilters

# Create search filter
filters = SearchFilters(
    center_node_uuid="node_123",                    # Focus on specific node
    group_ids=["group_1", "group_2"],               # Filter by groups
    valid_time_start=datetime(2025, 1, 1),          # Temporal filter
    valid_time_end=datetime.now()
)

results = await graphiti.search(
    query="knowledge graph operations",
    search_filter=filters,
    num_results=20
)
```

---

## Complete Working Example

### Script: demo_graphiti_real.py
```python
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

async def main():
    # Load environment
    load_dotenv()

    print("[INIT] Connecting to Neo4j...")
    graphiti = Graphiti(
        uri=os.getenv("NEO4J_URI"),
        user=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD")
    )

    print("[ADD] Creating episode...")
    episode_result = await graphiti.add_episode(
        name="Story 1.3 Implementation",
        episode_body="Completed Knowledge Agent with 3 MCP integrations: Graphiti (direct), Obsidian (wrapped), Filesystem (wrapped)",
        source_description="MADF Development",
        reference_time=datetime.now(),
        source=EpisodeType.message,
        update_communities=True
    )

    print(f"[OK] Episode created: {episode_result.episode.uuid}")
    print(f"     Nodes extracted: {len(episode_result.nodes)}")
    print(f"     Edges created: {len(episode_result.edges)}")

    # Wait for indexing
    await asyncio.sleep(2)

    print("[SEARCH] Finding related information...")
    search_results = await graphiti.search(
        query="MCP integrations Knowledge Agent",
        num_results=5
    )

    print(f"[OK] Found {len(search_results)} results")
    for i, edge in enumerate(search_results, 1):
        print(f"  {i}. {edge.fact}")

    print("[COMPLETE]")

asyncio.run(main())
```

### Output:
```
[INIT] Connecting to Neo4j...
[ADD] Creating episode...
[OK] Episode created: ep_8f7a3c2b-1234-5678-9abc-def012345678
     Nodes extracted: 4
     Edges created: 6
[SEARCH] Finding related information...
[OK] Found 3 results
  1. Knowledge Agent uses Graphiti MCP integration
  2. Obsidian MCP provides documentation storage
  3. Filesystem MCP handles file operations
[COMPLETE]
```

---

## Test Usage Example

### From test_story_1_3_real_graphiti.py
```python
@pytest.mark.asyncio
async def test_add_episode_real(self, real_graphiti_client, test_episode_data):
    """REAL TEST: Add episode to actual Neo4j knowledge graph"""

    # Add episode with real Graphiti client
    result = await real_graphiti_client.add_episode(
        content=test_episode_data["content"],
        episode_type=test_episode_data["episode_type"],
        source=test_episode_data["source"],
        metadata=test_episode_data["metadata"]
    )

    # Verify episode was created
    assert result["success"] == True
    assert "episode_id" in result
    assert result["content"] == test_episode_data["content"]
    assert result["type"] == test_episode_data["episode_type"]
```

### Test Data Fixture
```python
@pytest.fixture
def test_episode_data():
    """Real test data for Graphiti episodes"""
    return {
        "content": "Test episode: User implemented filesystem MCP integration",
        "episode_type": "implementation",
        "source": "test_suite",
        "metadata": {
            "test_marker": "madf_test",
            "story": "1.3",
            "component": "knowledge_agent"
        }
    }
```

---

## Knowledge Agent Usage

### From src/agents/knowledge_agent.py
```python
class KnowledgeAgent:
    def __init__(self):
        self.graphiti_client = GraphitiClient()
        self.obsidian_client = ObsidianClient()
        self.filesystem_client = FilesystemClient()

    async def store_episode(
        self,
        content: str,
        episode_type: str = "observation",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Store episodic memory in knowledge graph"""
        return await self.graphiti_client.add_episode(
            content=content,
            episode_type=episode_type,
            source="knowledge_agent",
            metadata=metadata
        )

    async def search_knowledge(
        self,
        query: str,
        search_type: str = "nodes"
    ) -> List[Dict[str, Any]]:
        """Search knowledge graph"""
        if search_type == "nodes":
            return await self.graphiti_client.search_nodes(query=query)
        elif search_type == "facts":
            return await self.graphiti_client.search_facts(query=query)
        elif search_type == "episodes":
            return await self.graphiti_client.search_episodes(query=query)
```

### Agent Usage
```python
# Initialize agent with real MCP clients
agent = KnowledgeAgent()

# Store memory
result = await agent.store_episode(
    content="User completed Story 1.3 with all tests passing",
    episode_type="completion",
    metadata={"story": "1.3", "tests": 56, "status": "passed"}
)

# Search memory
nodes = await agent.search_knowledge(
    query="Story 1.3 completion",
    search_type="nodes"
)
```

---

## API Differences Summary

| Feature | Our API | Real Graphiti Core |
|---------|---------|-------------------|
| Init params | Environment vars | Direct params (uri, user, password) |
| Episode creation | Simple (content, type) | Complex (name, body, reference_time) |
| Search | 3 methods (nodes/facts/episodes) | Unified search() method |
| Return type | Dict | Pydantic models |
| Episode types | String | Enum (EpisodeType) |
| Temporal | Automatic | Explicit reference_time |

## Next Steps

1. **Replace mock implementations** in graphiti_client.py with real Graphiti Core calls
2. **Update add_episode()** to use real graphiti.add_episode() signature
3. **Update search methods** to use unified graphiti.search() API
4. **Add proper error handling** for Neo4j connection failures
5. **Implement bi-temporal tracking** using Graphiti's valid_time/expired_at

## Reference

- **Graphiti Core Docs**: https://github.com/getzep/graphiti
- **API Version**: 0.20.4
- **Neo4j Version**: 5.26+
- **Python Version**: 3.10+