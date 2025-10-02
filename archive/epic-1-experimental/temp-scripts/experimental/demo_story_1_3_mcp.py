"""
Story 1.3 MCP Integration Demo
Demonstrates Graphiti, Obsidian, and Filesystem MCP integrations
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.graphiti_client import GraphitiClient
from core.obsidian_client import ObsidianClient
from core.mcp_bridge import MCPBridge
from agents.knowledge_agent import KnowledgeAgent


async def demo_graphiti_mcp():
    """Demo 1: Graphiti MCP - Knowledge Graph Operations"""
    print("\n" + "="*60)
    print("DEMO 1: Graphiti MCP - Knowledge Graph")
    print("="*60)

    client = GraphitiClient()

    # Add episode
    print("\n[1] Adding episode to knowledge graph...")
    result = await client.add_episode(
        content="Story 1.3 implementation completed with Graphiti, Obsidian, and Filesystem integration",
        episode_type="milestone",
        source="demo_script",
        metadata={"story": "1.3", "timestamp": "2025-09-30"}
    )
    print(f"Result: {result}")

    # Search nodes
    print("\n[2] Searching knowledge graph nodes...")
    nodes = await client.search_nodes("Story 1.3", limit=3)
    print(f"Found {len(nodes)} nodes:")
    for node in nodes:
        print(f"  - {node['name']}: {node['content'][:50]}...")

    # Search episodes
    print("\n[3] Searching episodes...")
    episodes = await client.search_episodes("integration", limit=3)
    print(f"Found {len(episodes)} episodes:")
    for ep in episodes:
        print(f"  - {ep['episode_id']}: {ep['content'][:50]}...")

    await client.close()
    print("\n[OK] Graphiti MCP demo complete")


async def demo_obsidian_mcp():
    """Demo 2: Obsidian MCP - Documentation Management"""
    print("\n" + "="*60)
    print("DEMO 2: Obsidian MCP - Documentation")
    print("="*60)

    client = ObsidianClient()

    # List vault files
    print("\n[1] Listing Obsidian vault files...")
    files = await client.list_files_in_vault()
    print(f"Found {len(files)} items in vault:")
    for item in files[:5]:
        print(f"  - {item['name']} ({item['type']})")

    # Search vault
    print("\n[2] Searching vault for 'MADF'...")
    results = await client.search("MADF")
    print(f"Found {len(results)} matches:")
    for result in results[:3]:
        print(f"  - {result['file']}: score {result['score']}")

    # Append content (mock)
    print("\n[3] Appending content to note...")
    result = await client.append_content(
        "/Projects/MADF-Story-1.3.md",
        "\n## Story 1.3 Complete\nAll integrations working: Graphiti, Obsidian, Filesystem"
    )
    print(f"Result: {result}")

    await client.close()
    print("\n[OK] Obsidian MCP demo complete")


def demo_filesystem_mcp():
    """Demo 3: Filesystem MCP via Serena - File Operations"""
    print("\n" + "="*60)
    print("DEMO 3: Filesystem MCP (Serena) - File Operations")
    print("="*60)

    bridge = MCPBridge()

    # Find files
    print("\n[1] Finding Python files in src/...")
    result = bridge.call_serena_tool(
        "find_file",
        {"relative_path": "src", "pattern": "*.py"}
    )
    print(f"Result: {result}")

    # List directory
    print("\n[2] Listing src/agents directory...")
    result = bridge.call_serena_tool(
        "list_dir",
        {"relative_path": "src/agents"}
    )
    print(f"Result: {result}")

    # Search for pattern
    print("\n[3] Searching for 'KnowledgeAgent' pattern...")
    result = bridge.call_serena_tool(
        "search_for_pattern",
        {"substring_pattern": "class KnowledgeAgent", "relative_path": "src"}
    )
    print(f"Result: Success={result.get('success')}, Matches={len(result.get('matches', []))}")

    print("\n[OK] Filesystem MCP demo complete")


async def demo_knowledge_agent():
    """Demo 4: Knowledge Agent - Integrated Operations"""
    print("\n" + "="*60)
    print("DEMO 4: Knowledge Agent - All Integrations")
    print("="*60)

    agent = KnowledgeAgent()

    # Show available tools
    print("\n[1] Knowledge Agent tools:")
    tools = agent.get_available_tools()
    for tool in tools:
        print(f"  - {tool}")

    # Store episode via agent
    print("\n[2] Storing episode via Knowledge Agent...")
    result = await agent.store_episode(
        content="Demo completed successfully for all MCP integrations",
        episode_type="demo",
        metadata={"demo": "story_1.3"}
    )
    print(f"Episode stored: {result.get('episode_id')}")

    # Persist cross-session memory
    print("\n[3] Persisting cross-session memory...")
    result = await agent.persist_cross_session_memory(
        session_id="demo-session-1",
        memory_data={"demo_complete": True, "all_tests_passed": True}
    )
    print(f"Memory persisted: {result.get('success')}")

    # Query filesystem via agent
    print("\n[4] Querying filesystem via agent...")
    result = await agent.query_filesystem(
        tool_name="find_file",
        parameters={"relative_path": "src/core", "pattern": "graphiti*"}
    )
    print(f"Filesystem query result: {result.get('success')}")

    await agent.close()
    print("\n[OK] Knowledge Agent demo complete")


async def main():
    """Run all MCP integration demos"""
    print("\n" + "="*60)
    print("Story 1.3: MCP Integration Demo")
    print("Graphiti + Obsidian + Filesystem MCPs")
    print("="*60)

    try:
        # Demo 1: Graphiti MCP
        await demo_graphiti_mcp()

        # Demo 2: Obsidian MCP
        await demo_obsidian_mcp()

        # Demo 3: Filesystem MCP
        demo_filesystem_mcp()

        # Demo 4: Knowledge Agent with all integrations
        await demo_knowledge_agent()

        print("\n" + "="*60)
        print("[SUCCESS] All MCP integrations demonstrated successfully!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())