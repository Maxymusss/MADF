# Graphiti MCP Server Documentation

**Source**: https://github.com/gifflet/graphiti-mcp-server

## Overview
Graphiti MCP Server is a powerful knowledge graph server for AI agents built with Neo4j and Model Context Protocol (MCP). It enables dynamic knowledge graph management through episodic memory, semantic search, and temporal awareness.

## Key Features
- **Dynamic Knowledge Graph Management**: Real-time graph updates without batch recomputation
- **Episodic Memory**: Store and retrieve conversation episodes with temporal context
- **Hybrid Search**: Combines semantic, keyword, and graph-based retrieval
- **Custom Entity Extraction**: Configurable entity types (Requirement, Preference, Procedure)
- **Group-based Organization**: Separate knowledge graphs by group_id
- **Queue-based Processing**: Sequential episode processing per group to avoid race conditions

## Technical Requirements
- Python 3.10+
- Neo4j database (v5.26+)
- OpenAI API key (or Azure OpenAI)
- Docker and Docker Compose (for containerized deployment)
- Minimum 4GB RAM (8GB recommended)
- 2GB free disk space

## Installation

### Option 1: Docker Compose (Recommended)
```bash
git clone https://github.com/gifflet/graphiti-mcp-server
cd graphiti-mcp-server
cp .env.sample .env
# Edit .env with your configuration
docker compose up -d
```

### Option 2: Local Development
```bash
pip install graphiti-core
python graphiti_mcp_server.py
```

## Configuration

### Environment Variables

#### OpenAI Configuration
- `OPENAI_API_KEY`: Required OpenAI API key
- `MODEL_NAME`: Main LLM model (default: `gpt-4.1-mini`)
- `SMALL_MODEL_NAME`: Small LLM model for lighter tasks (default: `gpt-4.1-nano`)
- `EMBEDDER_MODEL_NAME`: Embedding model (default: `text-embedding-3-small`)
- `LLM_TEMPERATURE`: Temperature for LLM responses (default: `0.0`)

#### Azure OpenAI Configuration
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint URL
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Deployment name for main model
- `AZURE_OPENAI_API_VERSION`: API version
- `AZURE_OPENAI_USE_MANAGED_IDENTITY`: Use managed identity authentication (`true`/`false`)
- `AZURE_OPENAI_EMBEDDING_ENDPOINT`: Endpoint for embeddings
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME`: Deployment name for embeddings
- `AZURE_OPENAI_EMBEDDING_API_VERSION`: Embedding API version
- `AZURE_OPENAI_EMBEDDING_API_KEY`: Embedding API key (if not using managed identity)

#### Neo4j Configuration
- `NEO4J_URI`: Database connection URI (default: `bolt://localhost:7687`)
- `NEO4J_USER`: Database username (default: `neo4j`)
- `NEO4J_PASSWORD`: Database password (default: `password`)

#### Performance Settings
- `SEMAPHORE_LIMIT`: Concurrent LLM operations limit (default: `10`)
  - Decrease if experiencing 429 rate limit errors
  - Increase if you have high rate limits

#### Features
- `GRAPHITI_DISABLE_TELEMETRY`: Disable anonymous telemetry (`true`/`false`)

## MCP Transport Options

### 1. Server-Sent Events (SSE)
```
http://localhost:8000/sse
```

### 2. WebSocket
```
ws://localhost:8000/ws
```

### 3. Stdio
Direct process communication for MCP clients.

## MCP Tools

### 1. add_memory
**Primary tool for adding information to the knowledge graph.**

Adds an episode to memory and processes it in the background. Episodes for the same group_id are processed sequentially to avoid race conditions.

**Parameters**:
- `name` (str, required): Name of the episode
- `episode_body` (str, required): Content to persist to memory
  - For `source='text'`: Plain text content
  - For `source='json'`: Properly escaped JSON string (NOT raw dictionary)
  - For `source='message'`: Conversation-style content
- `group_id` (str, optional): Unique ID for this graph (uses default if not provided)
- `source` (str, optional): Source type - `'text'`, `'json'`, or `'message'` (default: `'text'`)
- `source_description` (str, optional): Description of the source
- `uuid` (str, optional): Optional UUID for the episode

**Returns**: `{"message": "Episode 'name' queued for processing (position: N)"}`

**Examples**:
```python
# Plain text
add_memory(
    name="Company News",
    episode_body="Acme Corp announced a new product line today.",
    source="text",
    source_description="news article",
    group_id="company_updates"
)

# Structured JSON (note: must be escaped string)
add_memory(
    name="Customer Profile",
    episode_body="{\\\"company\\\": {\\\"name\\\": \\\"Acme Technologies\\\"}}",
    source="json",
    source_description="CRM data"
)

# Message/conversation
add_memory(
    name="Customer Conversation",
    episode_body="user: What's your return policy?\nassistant: You can return items within 30 days.",
    source="message",
    source_description="chat transcript"
)
```

**Important Notes**:
- Returns immediately; processing happens asynchronously
- JSON must be properly escaped string, not Python dict
- Complex nested JSON structures are supported (minimize nesting depth)
- Entities and relationships are automatically extracted

### 2. search_memory_nodes
**Search for relevant node summaries in the knowledge graph.**

Nodes contain summaries of all relationships with other nodes.

**Parameters**:
- `query` (str, required): Search query
- `group_ids` (list[str], optional): List of group IDs to filter results (uses default if not provided)
- `max_nodes` (int, optional): Maximum nodes to return (default: `10`)
- `center_node_uuid` (str, optional): UUID of node to center search around
- `entity` (str, optional): Single entity type to filter - `"Preference"` or `"Procedure"`

**Returns**:
```json
{
    "message": "Nodes retrieved successfully",
    "nodes": [
        {
            "uuid": "node-uuid",
            "name": "node-name",
            "summary": "summary text",
            "labels": ["label1", "label2"],
            "group_id": "group-id",
            "created_at": "ISO-8601 timestamp",
            "attributes": {}
        }
    ]
}
```

**Search Strategies**:
- With `center_node_uuid`: Uses NODE_HYBRID_SEARCH_NODE_DISTANCE (proximity-based)
- Without `center_node_uuid`: Uses NODE_HYBRID_SEARCH_RRF (reciprocal rank fusion)

### 3. search_memory_facts
**Search for relevant facts (entity edges) in the knowledge graph.**

Facts represent relationships between entities.

**Parameters**:
- `query` (str, required): Search query
- `group_ids` (list[str], optional): List of group IDs to filter results
- `max_facts` (int, optional): Maximum facts to return (default: `10`, must be > 0)
- `center_node_uuid` (str, optional): UUID of node to center search around

**Returns**:
```json
{
    "message": "Facts retrieved successfully",
    "facts": [
        {
            "uuid": "edge-uuid",
            "source_node_uuid": "source-uuid",
            "target_node_uuid": "target-uuid",
            "fact": "relationship description",
            "created_at": "ISO-8601 timestamp",
            "expired_at": "ISO-8601 timestamp or null",
            "attributes": {}
        }
    ]
}
```

### 4. delete_entity_edge
**Delete a specific entity edge (fact) from the graph.**

**Parameters**:
- `uuid` (str, required): UUID of the entity edge to delete

**Returns**: `{"message": "Entity edge with UUID {uuid} deleted successfully"}`

**Error**: `{"error": "Graphiti client not initialized"}` or edge-specific errors

### 5. delete_episode
**Delete a specific episode from the graph.**

**Parameters**:
- `uuid` (str, required): UUID of the episode to delete

**Returns**: `{"message": "Episode with UUID {uuid} deleted successfully"}`

**Error**: `{"error": "Graphiti client not initialized"}` or episode-specific errors

### 6. get_entity_edge
**Retrieve a specific entity edge by UUID.**

**Parameters**:
- `uuid` (str, required): UUID of the entity edge to retrieve

**Returns**: Full entity edge object (dict) with all attributes except embeddings

**Error**: `{"error": "Graphiti client not initialized"}` or retrieval errors

### 7. get_episodes
**Retrieve the most recent episodes for a group.**

**Parameters**:
- `group_id` (str, optional): Group ID to retrieve episodes from (uses default if not provided)
- `last_n` (int, optional): Number of recent episodes to retrieve (default: `10`)

**Returns**: List of episode objects with full metadata
```json
[
    {
        "uuid": "episode-uuid",
        "name": "episode-name",
        "source": "text",
        "source_description": "description",
        "content": "episode content",
        "created_at": "ISO-8601 timestamp",
        "group_id": "group-id",
        "attributes": {}
    }
]
```

### 8. clear_graph
**Clear all data from the graph and rebuild indices.**

**DESTRUCTIVE OPERATION** - Use with extreme caution.

**Parameters**: None

**Returns**: `{"message": "Graph cleared successfully and indices rebuilt"}`

**Error**: `{"error": "Graphiti client not initialized"}` or clearing errors

## Custom Entity Types

The server supports three predefined custom entity types when `use_custom_entities` is enabled:

### Requirement
Represents specific needs, features, or functionality that a product must fulfill.

**Fields**:
- `project_name` (str): Project to which requirement belongs
- `description` (str): Description of the requirement

**Extraction Instructions**:
- Look for explicit statements of needs ("We need X", "X is required")
- Identify functional specifications
- Capture non-functional requirements (performance, security, usability)
- Extract constraints and limitations
- Preserve priority/importance if mentioned
- Include dependencies between requirements

### Preference
Represents user's expressed likes, dislikes, or preferences.

**Fields**:
- `category` (str): Category of preference (e.g., "Brands", "Food", "Music")
- `description` (str): Brief description of the preference

**Extraction Instructions**:
- Look for explicit preference statements ("I like/prefer X")
- Pay attention to comparative statements ("I prefer X over Y")
- Consider emotional tone
- Extract only clearly expressed preferences
- Include relevant qualifiers ("likes spicy food" not just "likes food")

### Procedure
Represents instructions or actions to take in certain scenarios.

**Fields**:
- `description` (str): Brief description of the procedure

**Extraction Instructions**:
- Look for sequential instructions ("First X, then Y")
- Identify explicit directives ("Always do X when Y")
- Pay attention to conditional statements ("If X, then Y")
- Extract procedures with clear beginning/end
- Preserve sequence and dependencies
- Include conditions/triggers
- Capture stated purpose or goal

## MCP Resources

### http://graphiti/status
**Get server and Neo4j connection status.**

**Returns**:
```json
{
    "status": "ok",
    "message": "Graphiti client initialized and Neo4j connection is healthy"
}
```

## Data Structures

### EntityNode
- `uuid`: Unique identifier
- `name`: Entity name
- `summary`: Summary content
- `labels`: Classification tags
- `group_id`: Group identifier
- `created_at`: Creation timestamp
- `attributes`: Additional metadata

### EntityEdge
- `uuid`: Unique identifier
- `fact`: Relationship information
- `source_node_uuid`: Source entity UUID
- `target_node_uuid`: Target entity UUID
- `created_at`: Creation timestamp
- `expired_at`: Expiration timestamp (null if active)
- `attributes`: Additional metadata

### EpisodicNode
- `uuid`: Unique identifier
- `name`: Episode name
- `content`: Episode content
- `source`: Source type (text/json/message)
- `source_description`: Source description
- `group_id`: Group identifier
- `created_at`: Creation timestamp
- `attributes`: Additional metadata

## Graph Database Support
- **Neo4j**: Primary support (v5.26+)
- **FalkorDB**: Alternative graph database
- **Kuzu**: Embedded graph database
- **Amazon Neptune**: Cloud-based graph service

## LLM Provider Support
- **OpenAI**: GPT models
- **Azure OpenAI**: Enterprise OpenAI with managed identity support
- **Google Gemini**: Google's LLM service
- **Custom providers**: Extensible architecture

## Search Capabilities

### Semantic Search
Vector-based similarity search using embeddings for conceptual matching.

### Keyword Search
Traditional text-based search for exact or fuzzy term matching.

### Graph Search
Relationship-based traversal to find connected entities and facts.

### Hybrid Search
Combined approach with result reranking and reciprocal rank fusion (RRF).

## Temporal Awareness
- **Bi-temporal Data Tracking**: Maintains both valid time and transaction time
- **Historical Querying**: Query graph state at any point in time
- **Time-based Relationship Analysis**: Track relationship evolution over time

## Best Practices

### Memory Management
1. **Structured Episodes**: Use consistent naming and group_id schemes
2. **Appropriate Granularity**: Balance episode size vs. searchability
3. **Regular Cleanup**: Use `delete_episode` and `delete_entity_edge` for outdated data
4. **Group Organization**: Separate distinct contexts with unique group_ids

### Performance Optimization
1. **Adjust Concurrency**: Tune `SEMAPHORE_LIMIT` based on rate limits
2. **Efficient Queries**: Use specific group_ids and center_node_uuid when possible
3. **Limit Result Sizes**: Set appropriate max_nodes/max_facts for performance
4. **Monitor Queue Depth**: Watch episode queue positions in add_memory responses

### Search Strategy
1. **Node Search**: Use for entity discovery and relationship summaries
2. **Fact Search**: Use for specific relationship details
3. **Center Nodes**: Leverage center_node_uuid for local graph exploration
4. **Entity Filtering**: Apply entity type filters to narrow results

### Custom Entities
1. **Enable Selectively**: Only use when domain-specific extraction is needed
2. **Provide Context**: Include rich source_description for better extraction
3. **Validate Results**: Review extracted entities and refine episodes as needed
4. **Monitor Costs**: Custom entities increase LLM API usage

## Troubleshooting

### Database Connection Issues
- Verify Neo4j server is running: `docker ps` or check Neo4j service
- Check connection parameters in environment variables
- Test connection: `neo4j-shell` or Neo4j Browser
- Ensure database name matches if using non-default database

### Performance Issues
- Reduce `SEMAPHORE_LIMIT` if hitting rate limits (429 errors)
- Increase `SEMAPHORE_LIMIT` if processing is slow and limits allow
- Check Neo4j memory allocation and query performance
- Monitor episode queue depth for processing bottlenecks

### Search Quality Issues
- Refine queries to be more specific
- Use appropriate search type (nodes vs. facts)
- Experiment with center_node_uuid for focused searches
- Check group_ids are correctly specified
- Verify entities were extracted from episodes (check with get_episodes)

### Custom Entity Extraction Issues
- Ensure `OPENAI_API_KEY` is set when `use_custom_entities=true`
- Provide detailed source_description for context
- Review episode content for entity extraction quality
- Check LLM model has sufficient capability (avoid nano models)

## Privacy & Telemetry
- Anonymous telemetry collected by default
- Disable via `GRAPHITI_DISABLE_TELEMETRY=true`
- No sensitive data transmitted
- Telemetry includes usage patterns and error rates

## IDE Integration

### Cursor IDE
Supports integration with Cursor IDE through MCP protocol. See `graphiti_cursor_rules.mdc` in repository.

### Claude Desktop
Compatible with Claude Desktop for AI assistant functionality.

### Custom MCP Clients
Extensible for custom Model Context Protocol implementations using stdio/SSE/WebSocket transports.

## License
MIT License - Open source and freely available.

## Repository Structure
```
graphiti-mcp-server/
├── graphiti_mcp_server.py          # Main MCP server implementation
├── README.md                        # Project documentation
├── Dockerfile                       # Docker configuration
├── docker-compose.yml               # Docker Compose setup
├── .env.sample                      # Sample environment configuration
├── pyproject.toml                   # Python project configuration
├── LICENSE                          # MIT license
├── graphiti_cursor_rules.mdc        # Cursor IDE integration
├── .python-version                  # Python version specification
├── uv.lock                          # Dependency lock file
└── GRAPHITI.COMMANDS.md             # Command reference
```

## Additional Resources
- Repository: https://github.com/gifflet/graphiti-mcp-server
- Graphiti Core Library: https://github.com/gongrzhe/graphiti
- Model Context Protocol: https://modelcontextprotocol.io
- Neo4j Documentation: https://neo4j.com/docs