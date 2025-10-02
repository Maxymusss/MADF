# Sample test data for MADF development and testing
# CRITICAL DEVELOPMENT BLOCKER RESOLUTION
# Created: 2025-09-21 | Required for offline development

from datetime import datetime, timedelta
import json

class TestDataGenerator:
    """Generate realistic test data for offline development."""

    @staticmethod
    def get_asia_g10_forex_data():
        """Generate sample Asia/G10 forex data."""
        base_time = datetime.utcnow()
        return {
            "USD/JPY": {
                "bid": 150.22,
                "ask": 150.28,
                "price": 150.25,
                "change": "+0.15%",
                "change_points": "+0.23",
                "high": 150.45,
                "low": 149.87,
                "timestamp": base_time.isoformat(),
                "source": "alpha_vantage",
                "volume": 125000
            },
            "EUR/USD": {
                "bid": 1.0818,
                "ask": 1.0824,
                "price": 1.0821,
                "change": "-0.08%",
                "change_points": "-0.0009",
                "high": 1.0856,
                "low": 1.0809,
                "timestamp": base_time.isoformat(),
                "source": "alpha_vantage",
                "volume": 98000
            },
            "GBP/USD": {
                "bid": 1.2631,
                "ask": 1.2637,
                "price": 1.2634,
                "change": "+0.12%",
                "change_points": "+0.0015",
                "high": 1.2668,
                "low": 1.2615,
                "timestamp": base_time.isoformat(),
                "source": "alpha_vantage",
                "volume": 87000
            },
            "AUD/USD": {
                "bid": 0.6542,
                "ask": 0.6548,
                "price": 0.6545,
                "change": "-0.23%",
                "change_points": "-0.0015",
                "high": 0.6571,
                "low": 0.6532,
                "timestamp": base_time.isoformat(),
                "source": "alpha_vantage",
                "volume": 76000
            },
            "USD/CHF": {
                "bid": 0.8876,
                "ask": 0.8882,
                "price": 0.8879,
                "change": "+0.05%",
                "change_points": "+0.0004",
                "high": 0.8895,
                "low": 0.8867,
                "timestamp": base_time.isoformat(),
                "source": "alpha_vantage",
                "volume": 54000
            },
            "USD/CAD": {
                "bid": 1.3648,
                "ask": 1.3654,
                "price": 1.3651,
                "change": "+0.09%",
                "change_points": "+0.0012",
                "high": 1.3672,
                "low": 1.3634,
                "timestamp": base_time.isoformat(),
                "source": "alpha_vantage",
                "volume": 67000
            }
        }

    @staticmethod
    def get_interest_rates_data():
        """Generate sample interest rates data."""
        return {
            "USD": {
                "current_rate": 5.50,
                "previous_rate": 5.25,
                "change": "+0.25",
                "last_meeting": "2024-12-18",
                "next_meeting": "2025-01-29",
                "bank": "Federal Reserve",
                "policy_stance": "hawkish"
            },
            "EUR": {
                "current_rate": 3.75,
                "previous_rate": 3.75,
                "change": "0.00",
                "last_meeting": "2024-12-14",
                "next_meeting": "2025-01-23",
                "bank": "European Central Bank",
                "policy_stance": "neutral"
            },
            "JPY": {
                "current_rate": 0.25,
                "previous_rate": 0.10,
                "change": "+0.15",
                "last_meeting": "2024-12-19",
                "next_meeting": "2025-01-24",
                "bank": "Bank of Japan",
                "policy_stance": "dovish"
            },
            "GBP": {
                "current_rate": 4.75,
                "previous_rate": 5.00,
                "change": "-0.25",
                "last_meeting": "2024-12-19",
                "next_meeting": "2025-02-06",
                "bank": "Bank of England",
                "policy_stance": "neutral"
            },
            "CHF": {
                "current_rate": 1.25,
                "previous_rate": 1.00,
                "change": "+0.25",
                "last_meeting": "2024-12-12",
                "next_meeting": "2025-03-20",
                "bank": "Swiss National Bank",
                "policy_stance": "hawkish"
            },
            "CAD": {
                "current_rate": 4.25,
                "previous_rate": 4.50,
                "change": "-0.25",
                "last_meeting": "2024-12-11",
                "next_meeting": "2025-01-29",
                "bank": "Bank of Canada",
                "policy_stance": "dovish"
            }
        }

    @staticmethod
    def get_financial_news_data():
        """Generate sample financial news data."""
        base_time = datetime.utcnow()
        return {
            "articles": [
                {
                    "title": "Federal Reserve Signals Potential Pause in Rate Hikes as Inflation Shows Signs of Cooling",
                    "description": "Fed officials indicate they may pause monetary tightening after December meeting if inflation continues downward trend",
                    "content": "Federal Reserve officials signaled on Thursday they are prepared to pause interest rate increases if inflation continues to moderate, marking a potential shift in the central bank's aggressive tightening campaign. Speaking at a financial conference, Fed Governor Sarah Bloom Raskin noted that recent data showing cooling inflation provides room for a more measured approach to monetary policy.",
                    "url": "https://example.com/fed-signals-pause-rate-hikes",
                    "publishedAt": (base_time - timedelta(hours=2)).isoformat(),
                    "source": {"name": "Financial Times", "id": "financial-times"},
                    "author": "James Politi",
                    "relevance_score": 0.95,
                    "sentiment": "neutral",
                    "markets_affected": ["USD", "USD/JPY", "EUR/USD", "interest_rates"],
                    "keywords": ["Federal Reserve", "interest rates", "inflation", "monetary policy"]
                },
                {
                    "title": "Bank of Japan Maintains Ultra-Loose Monetary Policy Despite Global Tightening Trend",
                    "description": "BoJ keeps interest rates near zero while other major central banks continue tightening, widening policy divergence",
                    "content": "The Bank of Japan maintained its ultra-loose monetary policy stance on Friday, keeping short-term interest rates at -0.1% and the 10-year government bond yield target around 0%. The decision comes as other major central banks continue to tighten policy, further widening the divergence in global monetary policies and putting pressure on the yen.",
                    "url": "https://example.com/boj-maintains-loose-policy",
                    "publishedAt": (base_time - timedelta(hours=6)).isoformat(),
                    "source": {"name": "Reuters", "id": "reuters"},
                    "author": "Tetsushi Kajimoto",
                    "relevance_score": 0.88,
                    "sentiment": "dovish",
                    "markets_affected": ["JPY", "USD/JPY", "EUR/JPY"],
                    "keywords": ["Bank of Japan", "monetary policy", "yen", "interest rates"]
                },
                {
                    "title": "EUR/USD Struggles Near Parity as ECB Officials Express Concern Over Economic Outlook",
                    "description": "European Central Bank policymakers voice worries about eurozone growth prospects amid ongoing inflation pressures",
                    "content": "The euro continued to struggle against the dollar on Thursday, trading near parity levels as European Central Bank officials expressed growing concerns about the eurozone's economic outlook. ECB President Christine Lagarde warned that the central bank faces a challenging balancing act between controlling inflation and supporting economic growth.",
                    "url": "https://example.com/eur-usd-parity-ecb-concerns",
                    "publishedAt": (base_time - timedelta(hours=12)).isoformat(),
                    "source": {"name": "Bloomberg", "id": "bloomberg"},
                    "author": "William Horobin",
                    "relevance_score": 0.82,
                    "sentiment": "bearish",
                    "markets_affected": ["EUR", "EUR/USD", "EUR/JPY"],
                    "keywords": ["European Central Bank", "eurozone", "inflation", "economic growth"]
                },
                {
                    "title": "Australian Dollar Weakens on RBA Rate Cut Speculation After Soft Inflation Data",
                    "description": "AUD falls against major currencies as markets price in potential Reserve Bank of Australia policy easing",
                    "content": "The Australian dollar weakened against major currencies following the release of softer-than-expected inflation data, which has sparked speculation that the Reserve Bank of Australia may need to cut interest rates sooner than previously anticipated. The quarterly inflation reading came in at 3.2%, below the 3.5% forecast.",
                    "url": "https://example.com/aud-weakens-rba-rate-cut-speculation",
                    "publishedAt": (base_time - timedelta(hours=18)).isoformat(),
                    "source": {"name": "Financial Review", "id": "financial-review"},
                    "author": "Michael Heath",
                    "relevance_score": 0.76,
                    "sentiment": "bearish",
                    "markets_affected": ["AUD", "AUD/USD", "AUD/JPY"],
                    "keywords": ["Reserve Bank of Australia", "inflation", "interest rates", "Australian dollar"]
                },
                {
                    "title": "Swiss Franc Strengthens as SNB Maintains Hawkish Stance on Inflation",
                    "description": "Swiss National Bank officials reaffirm commitment to fighting inflation, supporting franc strength",
                    "content": "The Swiss franc gained ground against major currencies after Swiss National Bank officials reiterated their commitment to maintaining a hawkish stance on inflation. SNB Chairman Thomas Jordan emphasized that the central bank remains vigilant about inflationary pressures and is prepared to take further action if necessary.",
                    "url": "https://example.com/chf-strengthens-snb-hawkish",
                    "publishedAt": (base_time - timedelta(hours=24)).isoformat(),
                    "source": {"name": "Neue Zürcher Zeitung", "id": "nzz"},
                    "author": "Peter Rohner",
                    "relevance_score": 0.71,
                    "sentiment": "hawkish",
                    "markets_affected": ["CHF", "USD/CHF", "EUR/CHF"],
                    "keywords": ["Swiss National Bank", "inflation", "Swiss franc", "monetary policy"]
                }
            ],
            "metadata": {
                "total_results": 5,
                "query_timestamp": base_time.isoformat(),
                "sources_count": 5,
                "average_relevance": 0.824,
                "timeframe": "this_week"
            }
        }

    @staticmethod
    def get_validation_conflict_scenarios():
        """Generate scenarios for testing validation agent."""
        return [
            {
                "scenario": "conflicting_rate_data",
                "description": "Different sources report different interest rates",
                "source_a": {
                    "data": {"USD_rate": 5.50, "source": "alpha_vantage"},
                    "timestamp": "2024-12-20T10:00:00Z"
                },
                "source_b": {
                    "data": {"USD_rate": 5.25, "source": "iex_cloud"},
                    "timestamp": "2024-12-20T09:45:00Z"
                },
                "expected_resolution": "use_most_recent",
                "confidence_impact": -0.15
            },
            {
                "scenario": "timing_mismatch",
                "description": "News article dated incorrectly",
                "source_a": {
                    "data": {"event": "Fed meeting", "date": "2024-12-18"},
                    "timestamp": "2024-12-20T14:00:00Z"
                },
                "source_b": {
                    "data": {"event": "Fed meeting", "date": "2024-12-19"},
                    "timestamp": "2024-12-20T14:30:00Z"
                },
                "expected_resolution": "flag_for_human_review",
                "confidence_impact": -0.25
            },
            {
                "scenario": "stale_data_detection",
                "description": "One source has significantly older data",
                "source_a": {
                    "data": {"EUR_USD_price": 1.0821},
                    "timestamp": "2024-12-20T15:00:00Z"
                },
                "source_b": {
                    "data": {"EUR_USD_price": 1.0856},
                    "timestamp": "2024-12-19T10:00:00Z"
                },
                "expected_resolution": "use_fresher_data",
                "confidence_impact": -0.10
            }
        ]

    @staticmethod
    def get_agent_communication_examples():
        """Generate sample inter-agent messages."""
        base_time = datetime.utcnow()
        return {
            "task_distribution": {
                "message_id": "pm_task_001",
                "from": "product_manager",
                "to": "research_agent_1",
                "type": "task_assignment",
                "timestamp": base_time.isoformat(),
                "content": {
                    "task_type": "forex_research",
                    "focus_pairs": ["USD/JPY", "EUR/USD", "GBP/USD"],
                    "timeframe": "this_week",
                    "priority": "high",
                    "deadline": (base_time + timedelta(hours=2)).isoformat(),
                    "data_sources": ["alpha_vantage", "newsapi"],
                    "output_format": "structured_json"
                }
            },
            "research_completion": {
                "message_id": "ra1_result_001",
                "from": "research_agent_1",
                "to": "product_manager",
                "type": "research_result",
                "timestamp": (base_time + timedelta(hours=1)).isoformat(),
                "content": {
                    "task_id": "pm_task_001",
                    "status": "completed",
                    "execution_time_minutes": 45,
                    "data_points_collected": 127,
                    "sources_accessed": ["alpha_vantage", "newsapi"],
                    "key_findings": [
                        "USD/JPY showing strength on Fed pause speculation",
                        "EUR/USD under pressure from ECB growth concerns",
                        "GBP/USD stable ahead of BoE decision"
                    ],
                    "confidence_score": 0.87,
                    "data_freshness_hours": 2.3
                }
            },
            "validation_request": {
                "message_id": "pm_validation_001",
                "from": "product_manager",
                "to": "validator_agent",
                "type": "validation_request",
                "timestamp": (base_time + timedelta(hours=2)).isoformat(),
                "content": {
                    "research_results_to_validate": [
                        "ra1_result_001",
                        "ra2_result_001"
                    ],
                    "validation_type": "cross_reference_and_timing",
                    "priority": "high",
                    "sources_for_validation": ["reuters_api", "bloomberg_terminal"],
                    "deadline": (base_time + timedelta(hours=3)).isoformat()
                }
            }
        }

    @staticmethod
    def save_test_data_to_files(base_path: str):
        """Save all test data to JSON files for easy loading."""
        import os
        from pathlib import Path

        base_dir = Path(base_path)
        base_dir.mkdir(parents=True, exist_ok=True)

        test_data = {
            'forex_data.json': TestDataGenerator.get_asia_g10_forex_data(),
            'interest_rates.json': TestDataGenerator.get_interest_rates_data(),
            'news_data.json': TestDataGenerator.get_financial_news_data(),
            'validation_conflicts.json': TestDataGenerator.get_validation_conflict_scenarios(),
            'agent_messages.json': TestDataGenerator.get_agent_communication_examples()
        }

        for filename, data in test_data.items():
            filepath = base_dir / filename
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)

        return list(test_data.keys())

# Quick access functions for common test scenarios
def get_week_timeframe():
    """Get 'this week' timeframe for testing."""
    now = datetime.utcnow()
    # "This week" = Monday 8 days before ask-date including weekends
    days_since_monday = now.weekday()
    start_of_week = now - timedelta(days=days_since_monday + 8)
    end_of_week = start_of_week + timedelta(days=6)
    return {
        'start': start_of_week.isoformat(),
        'end': end_of_week.isoformat(),
        'description': 'Monday 8 days before current date including weekends'
    }

def get_error_scenarios():
    """Common error scenarios for testing."""
    return {
        'api_rate_limit': {
            'error_type': 'RateLimitExceeded',
            'message': 'API rate limit exceeded. Try again in 60 seconds.',
            'retry_after': 60,
            'source': 'alpha_vantage'
        },
        'invalid_api_key': {
            'error_type': 'AuthenticationError',
            'message': 'Invalid API key provided',
            'retry_after': None,
            'source': 'newsapi'
        },
        'network_timeout': {
            'error_type': 'NetworkTimeout',
            'message': 'Request timed out after 30 seconds',
            'retry_after': 5,
            'source': 'iex_cloud'
        },
        'malformed_response': {
            'error_type': 'DataFormatError',
            'message': 'Received malformed JSON response',
            'retry_after': None,
            'source': 'reuters_api'
        }
    }