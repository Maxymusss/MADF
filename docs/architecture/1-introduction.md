# 1. Introduction

This document outlines the complete architecture for **Multi-Agent Development Framework (MADF)**, a multiagent coding assistance system using LangGraph orchestration with 5 specialized agents. It serves as the single source of truth for AI-driven development, ensuring consistency across the entire technology stack.

## Project Overview

MADF implements a hybrid MCP integration architecture where performance-critical operations use direct Python MCP SDK while all other tools route through an intelligent mapping_mcp_bridge.js with calibrated per-tool query strategies.

**Core System**: 5 specialized LangGraph agents (Orchestrator, Analyst, Knowledge, Developer, Validator) coordinated via Pydantic state models with comprehensive MCP tool integration.

## Starter Template or Existing Project

**Current Project State:** Brownfield - Existing MADF Infrastructure

The Multi-Agent Development Framework (MADF) foundation includes:
- LangGraph StateGraph with 5-agent architecture (Epic 1, Story 1.1)
- Hybrid MCP integration: Direct Python SDK + mapping_mcp_bridge.js
- MCP configuration in `mcp-use/` directory
- Python agents in `src/agents/` with specialized tool assignments
- Testing infrastructure with real MCP integration (NO MOCKS policy)

**Architectural Constraints:**
- **Primary MCP Access**: `mapping_mcp_bridge.js` for all tools except Serena/Graphiti
- **Direct Python MCP SDK**: Serena (semantic search) and Graphiti (knowledge graphs) only
- **Strategy Mapping**: `mcp-use/mcp-strategy-mapping.json` provides per-tool calibration
- **3-Tier Selection**: Tool mapping → Parameter analysis → Fallback chain
- **Pydantic V2**: All state models and inter-agent communication
- **LangGraph**: StateGraph orchestration with checkpointing

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2025-09-21 | v1.0 | Initial fullstack architecture for Phase 1 financial research agents | Winston (Architect) |
| 2025-10-01 | v2.0 | Updated for MADF multiagent coding framework with mapping_mcp_bridge.js | Winston (Architect) |
