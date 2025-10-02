"""
Test Tavily search through mcp-use for NFL scores
"""

import asyncio
import os
import subprocess
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

async def search_nfl_scores():
    """Search for yesterday's NFL scores using Tavily"""

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%B %d, %Y")
    query = f"NFL scores {yesterday}"

    print("=" * 60)
    print(f"Searching: {query}")
    print("=" * 60)

    env = os.environ.copy()
    env['TAVILY_API_KEY'] = os.getenv('TAVILY_API_KEY')

    proc = subprocess.Popen(
        ['C:\\Program Files\\nodejs\\npx.cmd', '-y', 'tavily-mcp'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
        encoding='utf-8',
        errors='replace',
        shell=True
    )

    # Initialize
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
    }
    proc.stdin.write(json.dumps(init_request) + "\n")
    proc.stdin.flush()
    proc.stdout.readline()  # Read init response

    # Search
    print(f"\n[1] Calling tavily-search...")
    search_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "tavily-search",
            "arguments": {
                "query": query,
                "max_results": 5
            }
        }
    }

    proc.stdin.write(json.dumps(search_request) + "\n")
    proc.stdin.flush()

    # Wait for response
    print("[2] Waiting for results...")

    # Read response (with manual timeout)
    import time
    start = time.time()
    timeout = 20
    response = None

    while time.time() - start < timeout:
        response = proc.stdout.readline()
        if response:
            break
        time.sleep(0.1)

    if response:
        print(f"[3] Processing response...")

        try:
            data = json.loads(response)

            if 'result' in data:
                result = data['result']

                # Extract content
                if isinstance(result, list) and len(result) > 0:
                    content_item = result[0]
                    if 'text' in content_item:
                        content = content_item['text']
                    elif 'content' in content_item:
                        content = content_item['content']
                    else:
                        content = str(content_item)

                    # Try to parse as JSON if it's a string
                    if isinstance(content, str):
                        try:
                            content_data = json.loads(content)
                            if 'results' in content_data:
                                print(f"\n{'='*60}")
                                print("NFL SCORES RESULTS")
                                print(f"{'='*60}\n")

                                for i, item in enumerate(content_data['results'], 1):
                                    print(f"{i}. {item.get('title', 'N/A')}")
                                    print(f"   URL: {item.get('url', 'N/A')}")
                                    print(f"   {item.get('content', 'N/A')[:200]}...")
                                    print()
                            else:
                                print(f"\nContent: {content}")
                        except:
                            print(f"\nRaw content: {content[:500]}")
                elif isinstance(result, dict):
                    print(f"\nResult keys: {result.keys()}")
                    print(f"Result: {json.dumps(result, indent=2)[:1000]}")
                else:
                    print(f"\nResult type: {type(result)}")
                    print(f"Result: {result}")
            else:
                print(f"No result in response: {data}")

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Raw response: {response[:500]}")
        except Exception as e:
            print(f"Error: {e}")
            print(f"Response: {response[:500]}")
    else:
        print(f"[!] Timeout after {timeout}s")

    proc.terminate()
    try:
        proc.wait(timeout=2)
    except:
        proc.kill()

    print("\n" + "="*60)
    print("[OK] Search complete")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(search_nfl_scores())