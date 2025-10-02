#!/bin/bash
# One-time setup for hybrid mode

set -e

echo "🚀 Setting up Sonnet + Ollama Hybrid Mode"

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Install from https://ollama.com"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found"
    exit 1
fi

# Check ANTHROPIC_API_KEY
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not set. Please set in .env"
    exit 1
fi

echo "✅ Prerequisites OK"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install anthropic

# Pull base Ollama model
echo "🔽 Pulling Ollama base model..."
ollama pull qwen2.5:7b

# Create custom Ollama model with embedded rules
echo "🏗️  Creating custom Ollama model (qwen2.5-mcp)..."
ollama create qwen2.5-mcp -f ollama_mcp_modelfile

# Verify custom model
echo "✅ Verifying custom model..."
ollama show qwen2.5-mcp

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install mcp-use @langchain/ollama @langchain/core

echo ""
echo "✅ Hybrid mode setup complete!"
echo ""
echo "Test with:"
echo "  node run_hybrid.js 'List allowed directories'"
echo ""
echo "Models available:"
echo "  - qwen2.5:7b (base)"
echo "  - qwen2.5-mcp (with embedded rules)"