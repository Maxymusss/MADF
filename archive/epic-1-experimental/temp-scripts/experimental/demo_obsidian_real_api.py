"""
Demo: Real Obsidian REST API connection test

Tests actual Obsidian Local REST API plugin connectivity
"""

import asyncio
import os
import random
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OBSIDIAN_API_KEY = os.getenv("OBSIDIAN_API_KEY")
OBSIDIAN_HOST = os.getenv("OBSIDIAN_HOST", "127.0.0.1")
OBSIDIAN_PORT = os.getenv("OBSIDIAN_PORT", "27124")
BASE_URL = f"http://{OBSIDIAN_HOST}:{OBSIDIAN_PORT}"


async def test_connection():
    """Test basic Obsidian REST API connection"""

    print("=" * 60)
    print("Obsidian REST API Connection Test")
    print("=" * 60)
    print(f"\nBase URL: {BASE_URL}")
    print(f"API Key: {OBSIDIAN_API_KEY[:20]}...")

    headers = {
        "Authorization": f"Bearer {OBSIDIAN_API_KEY}",
        "Content-Type": "application/vnd.olrapi.note+json"
    }

    connector = aiohttp.TCPConnector(force_close=True)
    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        # Test multiple endpoint formats
        endpoints = [
            "/",
            "/vault/",
            "/active/",
            "/vault",
            "/periodic/daily/"
        ]

        print("\n[1] Testing endpoints...")
        for endpoint in endpoints:
            try:
                url = f"{BASE_URL}{endpoint}"
                print(f"\n    Testing: {url}")
                async with session.get(url, headers=headers) as resp:
                    print(f"    Status: {resp.status}")
                    if resp.status == 200:
                        try:
                            data = await resp.json()
                            print(f"    Success! Data type: {type(data)}")
                            if isinstance(data, dict) and 'files' in data:
                                print(f"    Found {len(data['files'])} files")
                                return data['files']
                            elif isinstance(data, list):
                                print(f"    Found {len(data)} items")
                                return data
                            else:
                                print(f"    Data keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
                        except:
                            text = await resp.text()
                            print(f"    Response (text): {text[:200]}")
                    else:
                        text = await resp.text()
                        print(f"    Error: {text[:200]}")
            except asyncio.TimeoutError:
                print(f"    Timeout")
            except Exception as e:
                print(f"    Exception: {type(e).__name__}: {e}")

        print("\n    [!] No working endpoint found")
        print("    [!] Plugin may need configuration or restart")
        return None


async def get_random_file(files):
    """Get content of a random file from vault"""

    if not files:
        print("\n[!] No files available")
        return

    # Filter for markdown files only
    md_files = [f for f in files if f.endswith('.md')]

    if not md_files:
        print("\n[!] No markdown files found")
        return

    random_file = random.choice(md_files)

    print(f"\n[3] Selected random file: {random_file}")

    headers = {
        "Authorization": f"Bearer {OBSIDIAN_API_KEY}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        try:
            # Get file content
            async with session.get(
                f"{BASE_URL}/vault/{random_file}",
                headers=headers
            ) as resp:
                if resp.status == 200:
                    content = await resp.text()

                    print("\n" + "=" * 60)
                    print("FILE CONTENT")
                    print("=" * 60)
                    print(f"File: {random_file}")
                    print(f"Size: {len(content)} characters")
                    print("\n" + "-" * 60)

                    # Show first 500 characters
                    if len(content) > 500:
                        print(content[:500] + "\n... (truncated)")
                    else:
                        print(content)

                    print("-" * 60)
                else:
                    text = await resp.text()
                    print(f"    Error ({resp.status}): {text}")
        except Exception as e:
            print(f"    Failed to get file: {e}")


async def main():
    """Main demo function"""

    if not OBSIDIAN_API_KEY:
        print("[ERROR] OBSIDIAN_API_KEY not found in .env")
        return

    # Test connection and list files
    files = await test_connection()

    if files:
        # Get random file content
        await get_random_file(files)
        print("\n[OK] Demo completed successfully")
    else:
        print("\n[FAIL] Could not connect to Obsidian REST API")
        print("\nTroubleshooting:")
        print("1. Open Obsidian")
        print("2. Go to Settings > Community Plugins")
        print("3. Enable 'Local REST API' plugin")
        print("4. Configure API key in plugin settings")
        print(f"5. Verify API key matches .env: {OBSIDIAN_API_KEY[:20]}...")


if __name__ == "__main__":
    asyncio.run(main())