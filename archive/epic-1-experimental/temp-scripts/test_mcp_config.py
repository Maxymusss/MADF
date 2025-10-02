"""Test MCP Bridge configuration loading"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded .env from: {env_path}")
else:
    print(f"WARNING: .env not found at {env_path}")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.mcp_bridge import MCPBridge

print("\n" + "="*80)
print("MCP BRIDGE CONFIGURATION TEST")
print("="*80)

# Check environment variables
print("\nEnvironment Variables:")
print(f"FILESYSTEM_ALLOWED_DIRS = {os.getenv('FILESYSTEM_ALLOWED_DIRS')}")
print(f"OBSIDIAN_VAULT_PATH = {os.getenv('OBSIDIAN_VAULT_PATH')}")

# Initialize bridge
bridge = MCPBridge()

# Check internal config
print("\nMCPBridge Internal Config:")
print(f"_filesystem_allowed_dirs = {bridge._filesystem_allowed_dirs}")
print(f"_obsidian_vault_path = {bridge._obsidian_vault_path}")

# Check generated args
print("\nGenerated Args:")
print(f"Filesystem args: {bridge._get_filesystem_args()}")
print(f"Obsidian args: {bridge._get_obsidian_args()}")

# Check server configs
print("\nServer Configurations:")
print(f"Filesystem config: {bridge.wrapped_mcp_servers['filesystem']}")
print(f"Obsidian config: {bridge.wrapped_mcp_servers['obsidian']}")

print("\n" + "="*80)
print("CONFIG TEST COMPLETE")
print("="*80)
