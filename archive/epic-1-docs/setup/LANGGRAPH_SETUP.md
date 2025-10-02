# LangGraph Course Setup Guide

This guide will help you set up everything needed for the LangGraph course from LangChain Academy.

## Prerequisites

- Python 3.8+
- An Anthropic API key (get one at https://console.anthropic.com/settings/keys)

## Quick Setup

### 1. Install Dependencies

All required packages are already installed in your environment:

```bash
pip install -U langgraph langsmith langchain[anthropic]
```

Or use the requirements file:

```bash
pip install -r requirements_langgraph.txt
```

### 2. Set Environment Variables

**Option A: Set environment variable directly**
```bash
# Windows (Command Prompt)
set ANTHROPIC_API_KEY=sk-your-api-key-here

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="sk-your-api-key-here"

# Mac/Linux
export ANTHROPIC_API_KEY=sk-your-api-key-here
```

**Option B: Create a .env file**
1. Copy `.env.example` to `.env`
2. Add your Anthropic API key to the `.env` file
3. Install python-dotenv: `pip install python-dotenv`
4. Load the environment in your Python script:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

### 3. Run the Basic Chatbot

```bash
python langgraph_basic_chatbot.py
```

## What's Included

- `langgraph_basic_chatbot.py` - Complete basic chatbot implementation
- `.env.example` - Environment variables template
- `requirements_langgraph.txt` - All required dependencies
- This setup guide

## Course Tutorial Structure

The course follows this progression:
1. ✅ **Build a basic chatbot** (implemented in `langgraph_basic_chatbot.py`)
2. Add tools (web search capabilities)
3. Add memory (conversation persistence)
4. Add human-in-the-loop controls
5. Customize state management
6. Time travel functionality

## Key Concepts Covered

- **StateGraph**: The core structure for LangGraph applications
- **Nodes**: Functions that process and update state
- **Edges**: Define the flow between nodes
- **State Management**: How data flows through your graph
- **Message Handling**: Built-in message list management

## Optional: LangSmith Integration

For enhanced debugging and monitoring, set up LangSmith:

1. Sign up at https://smith.langchain.com/
2. Get your API key
3. Add to environment:
   ```bash
   export LANGCHAIN_API_KEY=ls__your-key-here
   export LANGCHAIN_TRACING_V2=true
   export LANGCHAIN_PROJECT=langgraph-tutorial
   ```

## Troubleshooting

**API Key Issues:**
- Make sure your Anthropic API key starts with `sk-`
- Verify the environment variable is set correctly
- Check that you have sufficient API credits

**Import Errors:**
- Ensure all packages are installed: `pip install -U langgraph langsmith langchain[anthropic]`
- Try restarting your Python environment

**Connection Issues:**
- Check your internet connection
- Verify your API key has the correct permissions

## Next Steps

Once your basic chatbot is working:
1. Experiment with different prompts and conversations
2. Review the LangSmith traces (if configured) to understand execution flow
3. Move on to the next tutorial: "Add tools"

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Academy](https://academy.langchain.com/)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [LangSmith Documentation](https://docs.smith.langchain.com/)