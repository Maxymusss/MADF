#!/usr/bin/env python3
"""
Graphiti MCP Server Launcher
Loads .env and starts gifflet/graphiti-mcp-server with proper configuration
"""
import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment from project .env
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"[OK] Loaded environment from {env_file}")
else:
    print(f"[WARN] No .env file found at {env_file}")

# Verify required environment variables
required_vars = ["NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD", "OPENAI_API_KEY"]
missing = [var for var in required_vars if not os.getenv(var)]
if missing:
    print(f"[FAIL] Missing required environment variables: {', '.join(missing)}")
    sys.exit(1)

# Find graphiti_mcp_server.py in site-packages
import site
server_path = None
for site_dir in site.getsitepackages():
    candidate = Path(site_dir) / "graphiti_mcp_server.py"
    if candidate.exists():
        server_path = candidate
        break

if not server_path:
    print("[FAIL] graphiti_mcp_server.py not found in site-packages")
    print("Run: pip install git+https://github.com/gifflet/graphiti-mcp-server.git")
    sys.exit(1)

print(f"[OK] Found MCP server at {server_path}")

# Parse command line arguments
import argparse
parser = argparse.ArgumentParser(description="Start Graphiti MCP server")
parser.add_argument("--group-id", default="madf-knowledge", help="Graphiti group ID namespace")
parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio", help="Transport mode")
parser.add_argument("--host", default="127.0.0.1", help="Host for SSE mode")
parser.add_argument("--model", default="gpt-4.1-mini", help="OpenAI model")
parser.add_argument("--destroy-graph", action="store_true", help="Destroy existing graph")
args = parser.parse_args()

# Build command
cmd = [
    sys.executable,
    str(server_path),
    "--group-id", args.group_id,
    "--transport", args.transport,
    "--model", args.model,
]

if args.transport == "sse":
    cmd.extend(["--host", args.host])

if args.destroy_graph:
    cmd.append("--destroy-graph")

print(f"[START] {' '.join(cmd)}")
print(f"[INFO] Neo4j: {os.getenv('NEO4J_URI')}")
print(f"[INFO] Group ID: {args.group_id}")
print(f"[INFO] Transport: {args.transport}")
print("")

# Run server
try:
    subprocess.run(cmd, env=os.environ.copy())
except KeyboardInterrupt:
    print("\n[STOP] Server stopped by user")
