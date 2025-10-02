"""
Demo: Sequential Thinking MCP via MCP-use Wrapper

Demonstrates complex reasoning chains for architectural analysis
"""

from src.agents.analyst_agent import AnalystAgent


def demo_sequential_thinking():
    """Demonstrate Sequential Thinking MCP-use integration"""

    print("=" * 70)
    print("Sequential Thinking MCP-use Integration Demo")
    print("=" * 70)
    print()

    agent = AnalystAgent()
    bridge = agent.mcp_bridge

    # Example 1: Simple reasoning chain
    print("[Example 1] Reasoning about agent communication patterns...")
    print("-" * 70)

    result1 = agent.reason_about_architecture(
        question="How do agents communicate in the MADF framework?"
    )

    print(f"Tool Used: {result1['tool_used']}")
    print(f"Question: {result1['question']}")
    print(f"Success: {result1['success']}")
    print()
    print("Reasoning Chain:")

    for step in result1.get('reasoning_steps', []):
        print(f"  Step {step['step']}: {step['reasoning']}")

    print()
    print(f"Conclusion: {result1.get('conclusion')}")
    print()

    # Example 2: Complex architectural analysis
    print("[Example 2] Analyzing multi-agent coordination complexity...")
    print("-" * 70)

    result2 = bridge.call_sequential_thinking_tool(
        "analyze_complex_problem",
        {
            "problem": "Design decision: Should we use direct MCP or MCP-use wrapper?",
            "context": {
                "direct_mcp": "Serena, Graphiti - performance critical",
                "mcp_use_wrapper": "Context7, Sequential Thinking - external services",
                "considerations": ["performance", "maintainability", "flexibility"]
            }
        }
    )

    print(f"Success: {result2['success']}")
    print()
    print("Reasoning Steps:")

    for step in result2.get('reasoning_steps', []):
        print(f"\n  Step {step['step']}:")
        print(f"    Thought: {step['thought']}")
        print(f"    Conclusion: {step['conclusion']}")

    print()
    print(f"Final Analysis: {result2.get('final_analysis')}")
    print()

    # Example 3: Multi-step reasoning workflow
    print("[Example 3] Complex workflow: Debugging agent integration issues...")
    print("-" * 70)

    result3 = bridge.call_sequential_thinking_tool(
        "reason",
        {
            "query": "Why might the Analyst Agent fail to retrieve documentation?",
            "context": {
                "symptoms": ["timeout errors", "empty results", "cache misses"],
                "components": ["AnalystAgent", "MCPBridge", "Context7 MCP", "API rate limits"]
            }
        }
    )

    print(f"Success: {result3['success']}")
    print()
    print("Diagnostic Reasoning Chain:")

    for step in result3.get('reasoning_chain', []):
        print(f"\n  Step {step['step']}:")
        print(f"    {step['reasoning']}")

    print()
    print(f"Root Cause: {result3.get('conclusion')}")
    print()

    # Example 4: Comparing architectural patterns
    print("[Example 4] Architectural trade-off analysis...")
    print("-" * 70)

    result4 = bridge.call_sequential_thinking_tool(
        "analyze_complex_problem",
        {
            "problem": "Should we implement token efficiency tracking at agent or bridge level?",
            "context": {
                "agent_level": "More granular control, per-agent metrics",
                "bridge_level": "Centralized tracking, consistent across all tools",
                "requirements": ["accuracy", "performance overhead", "maintainability"]
            }
        }
    )

    print(f"Success: {result4['success']}")
    print()
    print("Trade-off Analysis:")

    for step in result4.get('reasoning_steps', []):
        print(f"\n  Step {step['step']}:")
        print(f"    Analysis: {step['thought']}")
        print(f"    Decision Point: {step['conclusion']}")

    print()
    print(f"Recommendation: {result4.get('final_analysis')}")
    print()

    # Show MCP configuration
    print("=" * 70)
    print("Sequential Thinking MCP Configuration")
    print("=" * 70)
    print()

    print(f"MCP Server: sequential_thinking")
    print(f"Type: {bridge.wrapped_mcp_servers['sequential_thinking']['type']}")
    print(f"Package: {bridge.wrapped_mcp_servers['sequential_thinking']['package']}")
    print()

    seq_tools = bridge.load_mcp_tools("sequential_thinking")
    print("Available Tools:")
    for tool_name, description in seq_tools.items():
        print(f"  - {tool_name}: {description}")

    print()
    print("=" * 70)
    print("Tool Usage Patterns from Analyst Agent")
    print("=" * 70)
    print()

    usage_patterns = agent.get_tool_usage_patterns()
    seq_pattern = usage_patterns.get('sequential_thinking_mcp', {})

    print(f"Description: {seq_pattern.get('description')}")
    print(f"Example: {seq_pattern.get('example_usage')}")
    print(f"When to Use: {seq_pattern.get('when_to_use')}")

    print()
    print("=" * 70)
    print("Real-world Use Cases")
    print("=" * 70)
    print()

    use_cases = [
        {
            "scenario": "Code Review Analysis",
            "question": "Should we refactor this module or rewrite it?",
            "reasoning_needed": "Cost-benefit analysis, technical debt assessment"
        },
        {
            "scenario": "Architecture Decision",
            "question": "Microservices vs Monolith for this feature?",
            "reasoning_needed": "Scalability requirements, team structure, deployment complexity"
        },
        {
            "scenario": "Debugging Strategy",
            "question": "Why is the agent workflow hanging?",
            "reasoning_needed": "Trace execution flow, identify bottlenecks, check dependencies"
        },
        {
            "scenario": "Performance Optimization",
            "question": "Where should we optimize first?",
            "reasoning_needed": "Profiling data analysis, impact assessment, implementation effort"
        }
    ]

    for i, use_case in enumerate(use_cases, 1):
        print(f"{i}. {use_case['scenario']}")
        print(f"   Question: {use_case['question']}")
        print(f"   Reasoning: {use_case['reasoning_needed']}")
        print()

    print("=" * 70)
    print("Demo complete!")
    print("=" * 70)


if __name__ == "__main__":
    demo_sequential_thinking()