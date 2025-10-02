"""Test KnowledgeAgent with direct Graphiti library integration"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.knowledge_agent import KnowledgeAgent

async def test_knowledge_agent():
    print("="*80)
    print("TESTING KNOWLEDGE AGENT WITH DIRECT GRAPHITI INTEGRATION")
    print("="*80)

    # Initialize agent
    print("\n[1/5] Initializing KnowledgeAgent...")
    agent = KnowledgeAgent()
    print(f"Agent: {agent.name} - {agent.role}")
    print(f"Graphiti available: {agent.graphiti.is_available}")
    print(f"Graphiti is mock: {agent.graphiti.is_mock}")

    # Test store_episode
    print("\n[2/5] Testing store_episode...")
    result = await agent.store_episode(
        content="Story 1.3 refactoring completed with direct Graphiti integration",
        episode_type="implementation",
        source="test_script",
        metadata={"test": True, "story": "1.3"}
    )
    print(f"Result: {result}")
    assert result["success"], f"store_episode failed: {result}"
    print("[OK] store_episode successful")

    # Test search_knowledge - nodes
    print("\n[3/5] Testing search_knowledge (nodes)...")
    results = await agent.search_knowledge(
        query="Story 1.3",
        search_type="nodes",
        limit=5
    )
    print(f"Found {len(results)} nodes")
    if results:
        print(f"First result: {results[0]}")
    print("[OK] search_knowledge (nodes) successful")

    # Test search_knowledge - facts
    print("\n[4/5] Testing search_knowledge (facts)...")
    results = await agent.search_knowledge(
        query="refactoring",
        search_type="facts",
        limit=5
    )
    print(f"Found {len(results)} facts")
    if results:
        print(f"First result: {results[0]}")
    print("[OK] search_knowledge (facts) successful")

    # Test search_knowledge - episodes
    print("\n[5/5] Testing search_knowledge (episodes)...")
    results = await agent.search_knowledge(
        query="implementation",
        search_type="episodes",
        limit=5
    )
    print(f"Found {len(results)} episodes")
    if results:
        print(f"First result: {results[0]}")
    print("[OK] search_knowledge (episodes) successful")

    # Close agent
    await agent.close()

    print("\n" + "="*80)
    print("ALL TESTS PASSED")
    print("="*80)

    if agent.graphiti.is_mock:
        print("\nNOTE: Tests used mock Graphiti implementation")
        print("For real Graphiti testing, run on Linux/WSL/Docker")

if __name__ == "__main__":
    asyncio.run(test_knowledge_agent())
