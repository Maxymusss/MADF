"""
Validator Agent - Financial Research Fact-Checking and Cross-Reference
Uses MCP-use to verify research findings from multiple research agents
"""

import os
import json
import asyncio
import logging
import subprocess
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import re
from difflib import SequenceMatcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidatorAgent:
    """
    Validator Agent that fact-checks and cross-references research findings
    Uses MCP-use to access verification sources and detect conflicts
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
        self.validation_log_file = self.logs_dir / f"{agent_id}_validations.json"

        # Validation thresholds
        self.similarity_threshold = 0.7  # For detecting similar claims
        self.confidence_threshold = 0.8  # For source reliability
        self.conflict_threshold = 0.5    # For detecting conflicts

        logger.info(f"Validator Agent {agent_id} initialized")

    async def execute_mcp_verification(self, query: str, sources: List[str] = None) -> Dict[str, Any]:
        """
        Execute verification search using MCP-use with focus on authoritative sources
        """
        try:
            # Build verification query with site-specific searches
            verification_queries = [query]

            # Add source-specific queries for authoritative verification
            if sources:
                authoritative_sources = [
                    "reuters.com", "bloomberg.com", "wsj.com", "ft.com",
                    "federalreserve.gov", "ecb.europa.eu", "boj.or.jp"
                ]
                for source in authoritative_sources[:3]:  # Limit to 3 for efficiency
                    verification_queries.append(f"site:{source} {query}")

            all_results = []
            for vq in verification_queries:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                    mcp_script = f"""
const {{ Client }} = require('mcp-use');

async function verifyInfo() {{
    const client = new Client();

    try {{
        await client.connect();

        const searchResults = await client.callTool('WebSearch', {{
            query: `{vq}`,
            max_results: 5
        }});

        console.log(JSON.stringify(searchResults, null, 2));

    }} catch (error) {{
        console.error('MCP verification failed:', error);
        console.log(JSON.stringify({{ error: error.message }}, null, 2));
    }} finally {{
        await client.disconnect();
    }}
}}

verifyInfo();
"""
                    f.write(mcp_script)
                    script_path = f.name

                # Execute MCP-use script
                result = subprocess.run(
                    ['node', script_path],
                    capture_output=True,
                    text=True,
                    timeout=20
                )

                # Clean up
                os.unlink(script_path)

                if result.returncode == 0:
                    search_result = json.loads(result.stdout)
                    if "results" in search_result:
                        all_results.extend(search_result["results"])

            return {"results": all_results, "query": query}

        except Exception as e:
            logger.error(f"MCP verification failed: {e}")
            return {"error": str(e), "query": query}

    def extract_claims_from_research(self, research_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract verifiable claims from research agent findings
        """
        claims = []

        findings = research_results.get("findings", {})

        # Extract currency movement claims
        for movement in findings.get("currency_movements", []):
            claims.append({
                "type": "currency_movement",
                "claim": f"{movement.get('currency_pairs', [])} {movement.get('movement_description', '')}",
                "source": movement.get("source", ""),
                "title": movement.get("title", ""),
                "category": "market_data"
            })

        # Extract interest rate claims
        for rate_change in findings.get("interest_rate_changes", []):
            claims.append({
                "type": "interest_rate",
                "claim": f"Interest rate {rate_change.get('action_info', '')} {rate_change.get('rate_info', '')}",
                "source": rate_change.get("source", ""),
                "title": rate_change.get("title", ""),
                "category": "monetary_policy"
            })

        # Extract central bank action claims
        for cb_action in findings.get("central_bank_actions", []):
            claims.append({
                "type": "central_bank_action",
                "claim": f"{cb_action.get('bank', '')} {cb_action.get('actions', '')}",
                "source": cb_action.get("source", ""),
                "title": cb_action.get("title", ""),
                "category": "policy_announcement"
            })

        return claims

    def detect_claim_conflicts(self, research_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect conflicting claims between different research agents
        """
        conflicts = []
        all_claims = []

        # Collect claims from all research agents
        for agent_id, result in research_results.items():
            if result.get("status") == "completed":
                agent_claims = self.extract_claims_from_research(result)
                for claim in agent_claims:
                    claim["source_agent"] = agent_id
                    all_claims.append(claim)

        # Compare claims for conflicts
        for i, claim1 in enumerate(all_claims):
            for j, claim2 in enumerate(all_claims[i+1:], i+1):
                # Only compare claims of same type
                if claim1["type"] == claim2["type"] and claim1["source_agent"] != claim2["source_agent"]:
                    similarity = self.calculate_claim_similarity(claim1["claim"], claim2["claim"])

                    # If claims are similar but from different sources, check for conflicts
                    if similarity > self.similarity_threshold:
                        conflict_detected = self.analyze_claim_conflict(claim1, claim2)
                        if conflict_detected:
                            conflicts.append({
                                "conflict_id": f"conflict_{i}_{j}",
                                "claim1": claim1,
                                "claim2": claim2,
                                "similarity_score": similarity,
                                "conflict_type": conflict_detected["type"],
                                "severity": conflict_detected["severity"]
                            })

        return conflicts

    def calculate_claim_similarity(self, claim1: str, claim2: str) -> float:
        """
        Calculate similarity between two claims using sequence matching
        """
        return SequenceMatcher(None, claim1.lower(), claim2.lower()).ratio()

    def analyze_claim_conflict(self, claim1: Dict[str, Any], claim2: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """
        Analyze if two similar claims actually conflict
        """
        text1 = claim1["claim"].lower()
        text2 = claim2["claim"].lower()

        # Look for opposing direction words
        opposing_pairs = [
            (["rises", "gains", "strengthens", "up", "higher", "increases"],
             ["falls", "loses", "weakens", "down", "lower", "decreases"]),
            (["cuts", "reduces", "lowers"],
             ["raises", "increases", "hikes"]),
            (["dovish", "accommodative"],
             ["hawkish", "restrictive"])
        ]

        for positive_words, negative_words in opposing_pairs:
            has_positive_1 = any(word in text1 for word in positive_words)
            has_negative_1 = any(word in text1 for word in negative_words)
            has_positive_2 = any(word in text2 for word in positive_words)
            has_negative_2 = any(word in text2 for word in negative_words)

            # Conflict if one claim is positive and another is negative
            if (has_positive_1 and has_negative_2) or (has_negative_1 and has_positive_2):
                return {
                    "type": "directional_conflict",
                    "severity": "high"
                }

        # Look for different numerical values
        numbers1 = re.findall(r'\d+\.?\d*', text1)
        numbers2 = re.findall(r'\d+\.?\d*', text2)

        if numbers1 and numbers2:
            try:
                val1 = float(numbers1[0])
                val2 = float(numbers2[0])
                if abs(val1 - val2) > 0.25:  # Significant difference
                    return {
                        "type": "numerical_conflict",
                        "severity": "medium"
                    }
            except ValueError:
                pass

        return None

    async def verify_specific_claim(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify a specific claim using authoritative sources
        """
        # Build verification query
        verification_query = self.build_verification_query(claim)

        # Execute verification search
        verification_results = await self.execute_mcp_verification(verification_query)

        if "error" in verification_results:
            return {
                "claim_id": claim.get("type", "unknown"),
                "verified": False,
                "error": verification_results["error"],
                "confidence": 0.0
            }

        # Analyze verification results
        verification_analysis = self.analyze_verification_results(
            claim, verification_results["results"]
        )

        return verification_analysis

    def build_verification_query(self, claim: Dict[str, Any]) -> str:
        """
        Build targeted verification query for a specific claim
        """
        claim_text = claim["claim"]
        claim_type = claim["type"]

        # Extract key terms for verification
        if claim_type == "currency_movement":
            # Extract currency pairs and movements
            currency_pairs = re.findall(r'[A-Z]{3}/[A-Z]{3}', claim_text)
            movement_words = re.findall(r'(rises?|falls?|gains?|loses?|up|down)', claim_text.lower())

            if currency_pairs and movement_words:
                return f"{currency_pairs[0]} exchange rate {movement_words[0]} today"

        elif claim_type == "interest_rate":
            # Extract central bank and rate action
            rate_words = re.findall(r'(raises?|cuts?|holds?|maintains?)', claim_text.lower())
            bank_words = re.findall(r'(fed|federal reserve|ecb|boj|bank)', claim_text.lower())

            if rate_words:
                bank_term = bank_words[0] if bank_words else "central bank"
                return f"{bank_term} interest rate {rate_words[0]}"

        elif claim_type == "central_bank_action":
            # Extract bank name and action
            return claim_text

        # Fallback to original claim
        return claim_text

    def analyze_verification_results(self, original_claim: Dict[str, Any],
                                   verification_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze verification search results against original claim
        """
        if not verification_results:
            return {
                "claim_id": original_claim.get("type", "unknown"),
                "verified": False,
                "confidence": 0.0,
                "reason": "no_verification_sources_found"
            }

        # Count supporting vs conflicting evidence
        supporting_evidence = 0
        conflicting_evidence = 0
        authoritative_sources = 0

        for result in verification_results:
            source_url = result.get("url", "")
            title = result.get("title", "")
            content = result.get("content", "")

            # Check if source is authoritative
            is_authoritative = any(domain in source_url for domain in [
                "reuters.com", "bloomberg.com", "wsj.com", "ft.com",
                "federalreserve.gov", "ecb.europa.eu", "boj.or.jp"
            ])

            if is_authoritative:
                authoritative_sources += 1

            # Simple content analysis (would be enhanced with NLP in production)
            verification_text = f"{title} {content}".lower()
            original_text = original_claim["claim"].lower()

            # Look for supporting keywords
            original_keywords = set(re.findall(r'\w+', original_text))
            verification_keywords = set(re.findall(r'\w+', verification_text))

            keyword_overlap = len(original_keywords.intersection(verification_keywords))
            total_keywords = len(original_keywords)

            if keyword_overlap / total_keywords > 0.3:  # 30% keyword overlap
                supporting_evidence += 1
            else:
                conflicting_evidence += 1

        # Calculate confidence score
        total_evidence = supporting_evidence + conflicting_evidence
        if total_evidence == 0:
            confidence = 0.0
        else:
            base_confidence = supporting_evidence / total_evidence
            # Boost confidence if authoritative sources present
            authority_boost = min(authoritative_sources * 0.1, 0.3)
            confidence = min(base_confidence + authority_boost, 1.0)

        return {
            "claim_id": original_claim.get("type", "unknown"),
            "verified": confidence > self.confidence_threshold,
            "confidence": confidence,
            "supporting_evidence": supporting_evidence,
            "conflicting_evidence": conflicting_evidence,
            "authoritative_sources": authoritative_sources,
            "verification_summary": {
                "total_sources_checked": len(verification_results),
                "authoritative_sources_found": authoritative_sources,
                "confidence_threshold": self.confidence_threshold
            }
        }

    def log_validation_metrics(self, task_id: str, validation_results: Dict[str, Any]):
        """
        Log validation metrics for learning and improvement
        """
        metrics = {
            "task_id": task_id,
            "validator_id": self.agent_id,
            "timestamp": datetime.now().isoformat(),
            "claims_verified": len(validation_results.get("claim_verifications", [])),
            "conflicts_detected": len(validation_results.get("conflicts", [])),
            "avg_confidence": validation_results.get("avg_confidence", 0),
            "verification_rate": validation_results.get("verification_rate", 0)
        }

        # Read existing metrics
        all_metrics = []
        if self.validation_log_file.exists():
            with open(self.validation_log_file, 'r') as f:
                all_metrics = json.load(f)

        all_metrics.append(metrics)

        # Save updated metrics
        with open(self.validation_log_file, 'w') as f:
            json.dump(all_metrics, f, indent=2)

        logger.info(f"Validator {self.agent_id} logged metrics for task {task_id}")

    async def execute_validation_task(self) -> Dict[str, Any]:
        """
        Main validation execution method
        Reads research results and produces validation report
        """
        try:
            # Read validator task specification
            task_file = self.tasks_dir / f"validator_{self.agent_id}.json"
            if not task_file.exists():
                raise FileNotFoundError(f"Validator task file not found: {task_file}")

            with open(task_file, 'r') as f:
                validator_task = json.load(f)

            task_id = validator_task["task_id"]
            research_agent_ids = validator_task["research_agents_to_validate"]

            logger.info(f"Validator {self.agent_id} starting validation for task {task_id}")

            # Read research results from all agents
            research_results = {}
            for agent_id in research_agent_ids:
                result_file = self.results_dir / f"{agent_id}_result.json"
                if result_file.exists():
                    with open(result_file, 'r') as f:
                        research_results[agent_id] = json.load(f)

            if not research_results:
                raise ValueError("No research results found to validate")

            # Step 1: Detect conflicts between research agents
            conflicts = self.detect_claim_conflicts(research_results)

            # Step 2: Extract all claims for verification
            all_claims = []
            for agent_id, result in research_results.items():
                if result.get("status") == "completed":
                    claims = self.extract_claims_from_research(result)
                    for claim in claims:
                        claim["source_agent"] = agent_id
                        all_claims.append(claim)

            # Step 3: Verify critical claims (limit to 10 for MVP)
            claim_verifications = []
            high_priority_claims = [claim for claim in all_claims if claim["category"] in ["monetary_policy", "policy_announcement"]]
            claims_to_verify = high_priority_claims[:5] + all_claims[:5]  # Mix of high priority and general

            for claim in claims_to_verify[:10]:  # Limit for performance
                verification_result = await self.verify_specific_claim(claim)
                verification_result["original_claim"] = claim
                claim_verifications.append(verification_result)

            # Step 4: Calculate overall validation metrics
            verified_claims = [v for v in claim_verifications if v.get("verified", False)]
            total_verifications = len(claim_verifications)

            avg_confidence = sum(v.get("confidence", 0) for v in claim_verifications) / total_verifications if total_verifications > 0 else 0
            verification_rate = len(verified_claims) / total_verifications if total_verifications > 0 else 0

            # Compile validation results
            validation_result = {
                "agent_id": self.agent_id,
                "task_id": task_id,
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "validation_summary": {
                    "total_claims_analyzed": len(all_claims),
                    "claims_verified": len(claim_verifications),
                    "conflicts_detected": len(conflicts),
                    "avg_confidence": avg_confidence,
                    "verification_rate": verification_rate,
                    "high_confidence_claims": len([v for v in claim_verifications if v.get("confidence", 0) > 0.8])
                },
                "conflicts": conflicts,
                "claim_verifications": claim_verifications,
                "research_agents_validated": research_agent_ids,
                "quality_assessment": {
                    "overall_reliability": "high" if verification_rate > 0.7 else "medium" if verification_rate > 0.4 else "low",
                    "conflict_severity": "high" if len(conflicts) > 3 else "medium" if len(conflicts) > 1 else "low",
                    "recommendation": "proceed" if verification_rate > 0.6 and len(conflicts) < 3 else "review_required"
                }
            }

            # Save validation results
            result_file = self.results_dir / f"{self.agent_id}_result.json"
            with open(result_file, 'w') as f:
                json.dump(validation_result, f, indent=2)

            # Log validation metrics
            self.log_validation_metrics(task_id, validation_result)

            logger.info(f"Validator {self.agent_id} completed validation successfully")
            return validation_result

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

            logger.error(f"Validator {self.agent_id} execution failed: {e}")
            return error_result


async def main():
    """Example usage of Validator Agent"""

    # Initialize validator agent
    validator = ValidatorAgent("validator_test_001")

    # Create test research results (simulating research agent outputs)
    test_research = {
        "research_agent_1": {
            "status": "completed",
            "findings": {
                "currency_movements": [
                    {
                        "currency_pairs": ["EUR/USD"],
                        "movement_description": "rises 0.5%",
                        "source": "https://reuters.com/test",
                        "title": "EUR/USD rises on ECB comments"
                    }
                ],
                "interest_rate_changes": [
                    {
                        "action_info": ["raises", "25 basis points"],
                        "source": "https://bloomberg.com/test",
                        "title": "Fed raises rates by 25 bps"
                    }
                ]
            }
        }
    }

    # Create test validator task
    os.makedirs("agent_workspace/tasks", exist_ok=True)
    os.makedirs("agent_workspace/results", exist_ok=True)

    # Save mock research results
    with open("agent_workspace/results/research_agent_1_result.json", 'w') as f:
        json.dump(test_research["research_agent_1"], f, indent=2)

    validator_task = {
        "agent_id": "validator_test_001",
        "task_id": "test_validation",
        "research_agents_to_validate": ["research_agent_1"]
    }

    with open("agent_workspace/tasks/validator_validator_test_001.json", 'w') as f:
        json.dump(validator_task, f, indent=2)

    # Execute validation
    result = await validator.execute_validation_task()

    print("Validation Results:")
    print(f"Status: {result.get('status')}")
    print(f"Claims Verified: {result.get('validation_summary', {}).get('claims_verified', 0)}")
    print(f"Conflicts: {result.get('validation_summary', {}).get('conflicts_detected', 0)}")
    print(f"Confidence: {result.get('validation_summary', {}).get('avg_confidence', 0):.2f}")


if __name__ == "__main__":
    asyncio.run(main())