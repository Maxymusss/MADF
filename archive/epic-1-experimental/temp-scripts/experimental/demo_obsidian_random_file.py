"""
Demo: Retrieve random file content from Obsidian vault

This script demonstrates:
1. Initialize ObsidianClient
2. List all files in vault
3. Select one random file
4. Display file content
"""

import asyncio
import random
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.obsidian_client import ObsidianClient


async def demo_random_file():
    """Demonstrate random file retrieval from Obsidian vault"""

    print("=" * 60)
    print("Obsidian Random File Demo")
    print("=" * 60)

    # 1. Initialize client
    print("\n[1] Initializing ObsidianClient...")
    client = ObsidianClient()
    await client.initialize()
    print("    Client initialized successfully")

    # 2. List all files
    print("\n[2] Listing files in vault...")
    files = await client.list_files_in_vault()
    print(f"    Found {len(files)} items in vault:")
    for item in files:
        print(f"    - {item['name']} ({item['type']})")

    # 3. Filter for files only (exclude directories)
    file_items = [f for f in files if f.get('type') == 'file']

    if not file_items:
        print("\n    No files found in vault!")
        return

    # 4. Select random file
    random_file = random.choice(file_items)
    print(f"\n[3] Selected random file: {random_file['name']}")
    print(f"    Path: {random_file['path']}")

    # 5. Get file content
    print(f"\n[4] Retrieving content...")
    content_data = await client.get_file_contents(random_file['path'])

    print("\n" + "=" * 60)
    print("FILE CONTENT")
    print("=" * 60)
    print(f"Path: {content_data.get('path')}")
    print(f"Size: {content_data.get('size')} bytes")
    print(f"Modified: {content_data.get('modified')}")
    print("\n" + "-" * 60)
    print(content_data.get('content', 'No content available'))
    print("-" * 60)

    # 6. Close client
    await client.close()
    print("\n[5] Client closed successfully")


async def demo_search_example():
    """Bonus: Demonstrate search functionality"""

    print("\n\n" + "=" * 60)
    print("BONUS: Search Demo")
    print("=" * 60)

    client = ObsidianClient()
    await client.initialize()

    query = "Graphiti"
    print(f"\nSearching for: '{query}'")

    results = await client.search(query)
    print(f"Found {len(results)} matching documents:")

    for result in results:
        print(f"\n  File: {result['file']}")
        print(f"  Score: {result['score']}")
        for match in result['matches']:
            print(f"    Line {match['line']}: {match['content']}")

    await client.close()


if __name__ == "__main__":
    print("\nRunning Obsidian Random File Demo...")
    asyncio.run(demo_random_file())

    # Uncomment to run search demo
    # asyncio.run(demo_search_example())