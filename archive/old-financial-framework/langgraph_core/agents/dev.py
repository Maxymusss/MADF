"""
Dev Agent - Commentary generation and file output
"""

import logging
from typing import Dict, Any
from datetime import datetime
from ..models.state import WorkflowState

logger = logging.getLogger(__name__)


async def dev_agent(state: WorkflowState) -> WorkflowState:
    """
    Dev Agent LangGraph node - Generates weekly commentary from research data

    Responsibilities:
    - Generate 50-80 word summaries from research data
    - Format content for weekly commentary
    - Save output files to hedgemonkey project
    - Validate word count and format requirements

    Args:
        state: Current workflow state with research data

    Returns:
        Updated workflow state with generated content
    """
    try:
        logger.info(f"Dev agent starting for workflow {state.workflow_id}")

        # Update current agent
        state.set_current_agent("dev")

        # Validate research data exists
        if not state.research_data:
            error_msg = "Dev agent requires research data from research agent"
            state.add_error(error_msg)
            logger.error(error_msg)
            return state

        # Extract research data
        research_data = state.research_data
        items = research_data.get("items", [])
        geographic_coverage = research_data.get("geographic_coverage", [])

        logger.info(f"Generating commentary from {len(items)} news items")

        # TODO: In Story 1.4, implement actual LLM-based content generation
        # For now, create mock commentary for testing
        mock_commentary = {
            "commentary_id": f"weekly_{datetime.now().strftime('%Y%m%d')}",
            "week_ending": "2025-01-27",
            "generated_at": state.timestamp.isoformat(),

            # Main content sections (50-80 words each)
            "fx_highlights": [
                "CNY strengthened 0.8% vs USD following PBOC's liquidity injection and improved manufacturing PMI. "
                "JPY declined 1.2% on BoJ dovish signals, while KRW gained 0.5% on export optimism. "
                "Regional currencies benefited from risk-on sentiment and China stimulus measures."
            ],
            "rates_highlights": [
                "US 10Y Treasury yields fell 8bp to 4.15% amid dovish Fed rhetoric and softer inflation expectations. "
                "JGB yields compressed following BoJ's yield curve adjustments, while Chinese bonds rallied on policy easing expectations. "
                "Asian rate markets showed broad decline in yields."
            ],
            "cross_market_themes": [
                "Risk appetite improved across EM Asia as China's stimulus measures and US-China trade dialogue progress supported sentiment. "
                "Oil price stability and tech sector resilience aided broader market confidence across the region."
            ],
            "week_ahead": [
                "Key events: FOMC meeting (Wed), China PMI data (Fri), BoJ policy decision (Thu). "
                "Watch for US GDP impact on Fed expectations and China policy announcements during Lunar New Year preparation."
            ]
        }

        # Calculate word count
        all_content = (
            " ".join(mock_commentary["fx_highlights"]) +
            " ".join(mock_commentary["rates_highlights"]) +
            " ".join(mock_commentary["cross_market_themes"]) +
            " ".join(mock_commentary["week_ahead"])
        )
        word_count = len(all_content.split())

        # Store generated content
        state.generated_content = {
            "commentary": mock_commentary,
            "word_count": word_count,
            "format_valid": True,
            "content_sections": 4,
            "generation_timestamp": state.timestamp.isoformat()
        }

        state.word_count = word_count

        # TODO: In Story 1.4, implement actual file output to hedgemonkey project
        # For now, set mock output path
        output_filename = f"2025-01-27-weekly-commentary.md"
        state.output_path = f"projects/hedgemonkey/reports/weekly/{output_filename}"

        # Update metadata
        state.metadata.update({
            "dev_complete": True,
            "dev_timestamp": state.timestamp.isoformat(),
            "word_count": word_count,
            "output_path": state.output_path,
            "content_sections": 4
        })

        # Set next agent
        state.set_current_agent("pm")

        logger.info(f"Dev agent completed - generated {word_count} words, output: {state.output_path}")
        return state

    except Exception as e:
        error_msg = f"Dev agent error: {str(e)}"
        state.add_error(error_msg)
        logger.error(error_msg, exc_info=True)
        return state