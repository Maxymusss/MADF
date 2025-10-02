# MADF Project Overview

## Purpose
Multi-Agent Development Framework (MADF) is a financial research platform designed for:
- Quantitative finance factor research (primary focus: alphaseek project - 80% allocation)
- Multi-agent coordination across portfolio of projects
- FX and interest rates market analysis for Asia/G10 regions
- Bloomberg API integration for financial data

## Project Classification
- **alphaseek**: Growth Stage (sophisticated quant platform, 70-80k LOC, 80% test coverage)
- **TotoRich**: Growth Stage (mature full-stack financial platform)
- **Prototypes**: 5 active projects (1clickman, citybadge, etc.)

## Architecture
Hybrid two-layer system:
- **Layer 1 (LangGraph)**: Strategic coordination, event routing, agent lifecycle
- **Layer 2 (Claude Code)**: Tactical execution, specialized tools, direct code manipulation
- **MCP Bridge**: Bi-directional communication between layers

## Key Features
- Event-driven development model with trigger-based task assignment
- Component sharing strategy with maturity gates
- Error tracking and learning capabilities for agents
- 48-hour MVP framework for financial markets research