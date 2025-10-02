"""
Research Agent - Financial Markets Research with MCP-use Integration
Uses MCP-use to access multiple tools for FX/rates market data collection
"""

import os
import json
import asyncio
import logging
import subprocess
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResearchAgent:
    """
    Research Agent that uses MCP-use to access financial data sources
    Specializes in FX/rates market research with error tracking and learning
    """

    def __init__(self, agent_id: str, workspace_dir: str = "agent_workspace"):
        self.agent_id = agent_id
        self.workspace_dir = Path(workspace_dir)

        # Communication directories
        self.tasks_dir = self.workspace_dir / "tasks"
        self.results_dir = self.workspace_dir / "results"
        self.logs_dir = self.workspace_dir / "logs"

        # Error tracking for learning
        self.error_log_file = self.logs_dir / f"{agent_id}_errors.json"

        # MCP-use configuration
        self.mcp_tools = {
            "web_search": {
                "server": "search",
                "capabilities": ["WebSearch", "WebFetch"]
            },
            "financial_data": {
                "server": "finance",
                "capabilities": ["yahoo_finance", "xe_currency"]
            }
        }

        logger.info(f"Research Agent {agent_id} initialized")

    async def execute_mcp_search(self, query: str, tool_type: str = "WebSearch") -> Dict[str, Any]:
        """
        Execute web search using MCP-use
        """
        try:
            # Create temporary script for MCP-use
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mjs', delete=False) as f:
                mcp_script = f"""
import {{ Client }} from 'mcp-use';

async function searchWeb() {{
    const client = new Client();

    try {{
        await client.connect();

        const searchResults = await client.callTool('{tool_type}', {{
            query: `{query}`,
            max_results: 10
        }});

        console.log(JSON.stringify(searchResults, null, 2));

    }} catch (error) {{
        console.error('MCP search failed:', error);
        console.log(JSON.stringify({{ error: error.message }}, null, 2));
    }} finally {{
        await client.disconnect();
    }}
}}

searchWeb();
"""
                f.write(mcp_script)
                script_path = f.name

            # Execute MCP-use script
            result = subprocess.run(
                ['node', script_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Clean up
            os.unlink(script_path)

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.error(f"MCP search failed: {result.stderr}")
                return {"error": result.stderr}

        except Exception as e:
            logger.error(f"MCP search execution failed: {e}")
            return {"error": str(e)}

    def parse_timeframe(self, start_date: str, end_date: str) -> tuple[datetime, datetime]:
        """
        Parse timeframe strings to datetime objects
        """
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        return start, end

    def build_search_queries(self, regions: List[str], markets: List[str],
                           start_date: datetime, end_date: datetime) -> List[str]:
        """
        Build targeted search queries for FX/rates research
        """
        queries = []

        # Base date range for queries
        date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

        # Regional currency queries
        region_currencies = {
            "Asia": ["USD/JPY", "USD/CNY", "AUD/USD", "NZD/USD", "USD/SGD", "USD/HKD"],
            "G10": ["EUR/USD", "GBP/USD", "USD/CHF", "USD/CAD", "SEK/USD", "NOK/USD"]
        }

        for region in regions:
            if region in region_currencies:
                currencies = region_currencies[region]
                for currency in currencies:
                    queries.append(f"{currency} exchange rate movement {date_range}")

        # Central bank queries
        central_banks = {
            "Asia": ["Bank of Japan", "People's Bank of China", "Reserve Bank of Australia"],
            "G10": ["Federal Reserve", "European Central Bank", "Bank of England", "Swiss National Bank"]
        }

        for region in regions:
            if region in central_banks:
                for bank in central_banks[region]:
                    queries.append(f"{bank} interest rate decision {date_range}")
                    queries.append(f"{bank} monetary policy {date_range}")

        # Market-specific queries
        if "currencies" in markets:
            queries.extend([
                f"foreign exchange market volatility {date_range}",
                f"currency market news {date_range}"
            ])

        if "interest_rates" in markets:
            queries.extend([
                f"interest rate changes {date_range}",
                f"bond market movements {date_range}"
            ])

        logger.info(f"Generated {len(queries)} search queries")
        return queries

    def extract_financial_events(self, search_results: List[Dict[str, Any]],
                                start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Extract and categorize financial events from search results
        """
        events = {
            "currency_movements": [],
            "interest_rate_changes": [],
            "central_bank_actions": [],
            "market_events": [],
            "sources": []
        }

        for result in search_results:
            if "error" in result:
                continue

            # Extract basic information
            title = result.get("title", "")
            content = result.get("content", "")
            url = result.get("url", "")
            published_date = result.get("published_date", "")

            # Verify timing - this is critical for accuracy
            if not self.is_within_timeframe(published_date, start_date, end_date):
                continue

            # Categorize content
            text = f"{title} {content}".lower()

            # Currency movements
            if any(term in text for term in ["exchange rate", "currency", "usd", "eur", "jpy", "gbp"]):
                movement = self.extract_currency_movement(title, content, url)
                if movement:
                    events["currency_movements"].append(movement)

            # Interest rate changes
            if any(term in text for term in ["interest rate", "monetary policy", "fed", "ecb", "boj"]):
                rate_change = self.extract_rate_change(title, content, url)
                if rate_change:
                    events["interest_rate_changes"].append(rate_change)

            # Central bank actions
            if any(term in text for term in ["central bank", "federal reserve", "ecb", "bank of japan"]):
                cb_action = self.extract_central_bank_action(title, content, url)
                if cb_action:
                    events["central_bank_actions"].append(cb_action)

            # Track sources for reliability scoring
            if url:
                source_domain = self.extract_domain(url)
                events["sources"].append({
                    "domain": source_domain,
                    "url": url,
                    "title": title,
                    "date": published_date
                })

        return events

    def is_within_timeframe(self, published_date: str, start_date: datetime, end_date: datetime) -> bool:
        """
        Verify if content is within the specified timeframe
        Critical for preventing timing errors
        """
        if not published_date:
            return False

        try:
            # Parse various date formats
            pub_date = None
            for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
                try:
                    pub_date = datetime.strptime(published_date[:19], fmt)
                    break
                except ValueError:
                    continue

            if pub_date is None:
                return False

            return start_date <= pub_date <= end_date

        except Exception as e:
            logger.warning(f"Date parsing failed for {published_date}: {e}")
            return False

    def extract_currency_movement(self, title: str, content: str, url: str) -> Optional[Dict[str, Any]]:
        """Extract currency movement information"""
        # Look for currency pairs and movements
        currency_pattern = r'(USD|EUR|GBP|JPY|CHF|CAD|AUD|NZD|CNY|SGD|HKD)[/\\-](USD|EUR|GBP|JPY|CHF|CAD|AUD|NZD|CNY|SGD|HKD)'
        movement_pattern = r'(rises?|falls?|gains?|loses?|strengthens?|weakens?|up|down|higher|lower)\s*(\d+\.?\d*%?)'

        currencies = re.findall(currency_pattern, title + " " + content, re.IGNORECASE)
        movements = re.findall(movement_pattern, title + " " + content, re.IGNORECASE)

        if currencies and movements:
            return {
                "type": "currency_movement",
                "currency_pairs": [f"{c[0]}/{c[1]}" for c in currencies],
                "movement_description": movements[0] if movements else "",
                "source": url,
                "title": title
            }
        return None

    def extract_rate_change(self, title: str, content: str, url: str) -> Optional[Dict[str, Any]]:
        """Extract interest rate change information"""
        rate_pattern = r'(\d+\.?\d*%?)\s*(basis points|bps|percent|%)'
        action_pattern = r'(raises?|cuts?|holds?|maintains?|increases?|decreases?)\s*(?:by\s*)?(\d+\.?\d*%?|bps|basis points)'

        rates = re.findall(rate_pattern, title + " " + content, re.IGNORECASE)
        actions = re.findall(action_pattern, title + " " + content, re.IGNORECASE)

        if rates or actions:
            return {
                "type": "interest_rate_change",
                "rate_info": rates,
                "action_info": actions,
                "source": url,
                "title": title
            }
        return None

    def extract_central_bank_action(self, title: str, content: str, url: str) -> Optional[Dict[str, Any]]:
        """Extract central bank action information"""
        cb_pattern = r'(Federal Reserve|Fed|ECB|European Central Bank|Bank of Japan|BOJ|Reserve Bank of Australia|RBA|People\'s Bank of China|PBOC)'
        action_pattern = r'(announces?|decides?|signals?|hints?|warns?|expects?)'

        banks = re.findall(cb_pattern, title + " " + content, re.IGNORECASE)
        actions = re.findall(action_pattern, title + " " + content, re.IGNORECASE)

        if banks:
            return {
                "type": "central_bank_action",
                "bank": banks[0],
                "actions": actions,
                "source": url,
                "title": title
            }
        return None

    def extract_domain(self, url: str) -> str:
        """Extract domain from URL for source reliability tracking"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return url

    def assess_source_reliability(self, sources: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Assess reliability of sources based on known financial news sources
        """
        reliable_sources = {
            "reuters.com": 0.95,
            "bloomberg.com": 0.95,
            "wsj.com": 0.90,
            "ft.com": 0.90,
            "cnbc.com": 0.85,
            "marketwatch.com": 0.80,
            "yahoo.com": 0.75,
            "investing.com": 0.70
        }

        source_scores = {}
        for source in sources:
            domain = source.get("domain", "")
            # Check for exact match or subdomain
            score = 0.5  # Default score
            for reliable_domain, reliability in reliable_sources.items():
                if reliable_domain in domain:
                    score = reliability
                    break
            source_scores[domain] = score

        return source_scores

    def log_error(self, error_type: str, description: str, context: Dict[str, Any] = None):
        """Log errors for learning and improvement"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "error_type": error_type,
            "description": description,
            "context": context or {}
        }

        errors = []
        if self.error_log_file.exists():
            with open(self.error_log_file, 'r') as f:
                errors = json.load(f)

        errors.append(error_entry)

        # Keep only last 500 errors per agent
        if len(errors) > 500:
            errors = errors[-500:]

        with open(self.error_log_file, 'w') as f:
            json.dump(errors, f, indent=2)

        logger.warning(f"Agent {self.agent_id} logged error: {error_type}")

    async def execute_research_task(self) -> Dict[str, Any]:
        """
        Main research execution method
        Reads task from shared file system and produces results
        """
        try:
            # Read task specification
            task_file = self.tasks_dir / f"agent_{self.agent_id}.json"
            if not task_file.exists():
                raise FileNotFoundError(f"Task file not found: {task_file}")

            with open(task_file, 'r') as f:
                task_spec = json.load(f)

            # Read main task details
            task_id = task_spec["task_id"]
            main_task_file = self.tasks_dir / f"{task_id}.json"

            with open(main_task_file, 'r') as f:
                main_task = json.load(f)

            logger.info(f"Agent {self.agent_id} starting research for task {task_id}")

            # Extract research parameters
            timeframe = main_task["timeframe"]
            scope = main_task["scope"]
            strategy = task_spec["strategy"]

            start_date, end_date = self.parse_timeframe(
                timeframe["start_date"],
                timeframe["end_date"]
            )

            # Build search queries based on strategy
            queries = self.build_search_queries(
                scope["regions"],
                scope["markets"],
                start_date,
                end_date
            )

            # Execute searches using MCP-use
            all_results = []
            for query in queries[:10]:  # Limit queries for MVP
                logger.info(f"Searching: {query}")
                search_result = await self.execute_mcp_search(query)
                if "error" not in search_result:
                    all_results.extend(search_result.get("results", []))
                else:
                    self.log_error("search_failed", f"Query failed: {query}",
                                 {"error": search_result["error"]})

            # Extract financial events
            events = self.extract_financial_events(all_results, start_date, end_date)

            # Assess source reliability
            source_scores = self.assess_source_reliability(events["sources"])

            # Compile results
            research_result = {
                "agent_id": self.agent_id,
                "task_id": task_id,
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "strategy_used": strategy["name"],
                "findings": events,
                "quality_metrics": {
                    "total_sources": len(events["sources"]),
                    "events_found": sum([
                        len(events["currency_movements"]),
                        len(events["interest_rate_changes"]),
                        len(events["central_bank_actions"])
                    ]),
                    "avg_source_reliability": sum(source_scores.values()) / len(source_scores) if source_scores else 0,
                    "queries_executed": len(queries)
                },
                "source_reliability_scores": source_scores,
                "timeframe_verified": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            }

            # Save results to shared file system
            result_file = self.results_dir / f"{self.agent_id}_result.json"
            with open(result_file, 'w') as f:
                json.dump(research_result, f, indent=2)

            logger.info(f"Agent {self.agent_id} completed research successfully")
            return research_result

        except Exception as e:
            error_result = {
                "agent_id": self.agent_id,
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }

            # Save error result
            result_file = self.results_dir / f"{self.agent_id}_result.json"
            with open(result_file, 'w') as f:
                json.dump(error_result, f, indent=2)

            self.log_error("execution_failed", str(e))
            logger.error(f"Agent {self.agent_id} execution failed: {e}")
            return error_result


async def main():
    """Example usage of Research Agent"""

    # Initialize research agent
    agent = ResearchAgent("research_agent_test_001")

    # Create a test task
    test_task = {
        "task_id": "test_fx_research",
        "timeframe": {
            "start_date": (datetime.now() - timedelta(days=7)).isoformat(),
            "end_date": datetime.now().isoformat()
        },
        "scope": {
            "regions": ["G10"],
            "markets": ["currencies", "interest_rates"]
        }
    }

    # Save test task
    os.makedirs("agent_workspace/tasks", exist_ok=True)
    with open("agent_workspace/tasks/test_fx_research.json", 'w') as f:
        json.dump(test_task, f, indent=2)

    # Create agent task
    agent_task = {
        "agent_id": "research_agent_test_001",
        "task_id": "test_fx_research",
        "strategy": {
            "name": "comprehensive_search",
            "tools": ["WebSearch"]
        }
    }

    with open("agent_workspace/tasks/agent_research_agent_test_001.json", 'w') as f:
        json.dump(agent_task, f, indent=2)

    # Execute research
    result = await agent.execute_research_task()

    print("Research Results:")
    print(f"Status: {result.get('status')}")
    print(f"Events Found: {result.get('quality_metrics', {}).get('events_found', 0)}")
    print(f"Sources: {result.get('quality_metrics', {}).get('total_sources', 0)}")


if __name__ == "__main__":
    asyncio.run(main())