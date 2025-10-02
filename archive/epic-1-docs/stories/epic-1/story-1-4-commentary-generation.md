# Story 1.4: Weekly Market Commentary Generation

**Epic**: Epic 1 - Multi-Agent Development Framework MVP
**Sprint**: Phase 1 (Week 2-3)
**Estimated Effort**: 3-4 days
**Dependencies**: Story 1.3 (News API Integration)

## User Story

As a **financial research system operator**,
I want **automated weekly commentary generation using multi-agent coordination**,
so that **I receive concise 50-80 word summaries of major market movements**.

## Acceptance Criteria

### AC1: Research Agent Execution
- [ ] Research Agent node collects weekly news data per BMAD plan
- [ ] Integrate with news collection from Story 1.3
- [ ] Process and filter news for relevance and importance
- [ ] Extract key market events and movements

### AC2: Dev Agent Processing
- [ ] Dev Agent formats news into weekly commentary structure
- [ ] Implement content generation using LLM integration
- [ ] Apply 50-80 word summary constraints
- [ ] Generate structured commentary with consistent format

### AC3: Content Generation
- [ ] Generate 50-80 word summaries per major movement/event
- [ ] Maintain professional, objective tone
- [ ] Include quantitative details (percentages, basis points)
- [ ] Provide context and causal analysis

### AC4: Geographic Focus
- [ ] EM Asia + US markets with appropriate timezone awareness
- [ ] Currency-specific analysis (CNY, KRW, JPY, etc.)
- [ ] Regional economic policy impacts
- [ ] Cross-regional correlation analysis

### AC5: File Output Management
- [ ] Save weekly commentary to hedgemonkey project directory
- [ ] Implement structured file naming (YYYY-MM-DD-weekly-commentary.md)
- [ ] Create backup copies in MADF docs directory
- [ ] Generate metadata files with generation parameters

### AC6: PM Agent Coordination
- [ ] PM Agent validates completion and manages final delivery
- [ ] Quality checks for content completeness
- [ ] Final formatting and presentation
- [ ] Delivery confirmation and archival

### AC7: Reference Attribution
- [ ] Append data source attribution separate from commentary text
- [ ] Include data collection timestamps
- [ ] List API sources used
- [ ] Add disclaimer about data limitations

## Weekly Commentary Features

### WCF1: Major FX & Rates Analysis
- **Driver Analysis**: Policy decisions, geopolitical events, sentiment shifts
- **Quantitative Context**: Percentage moves, volatility measures
- **Forward Looking**: Key events in coming week
- **Regional Focus**: EM Asia currency performance vs USD

### WCF2: Equity/Commodities Coverage
- **Threshold**: Only mention if >5% daily moves or significant Asia impact
- **Brief Mentions**: 1-2 sentences maximum
- **Linkage**: Connect to FX/rates implications
- **Context**: Broader market sentiment indicators

### WCF3: Future Events Integration
- **Central Bank Meetings**: FOMC, BoJ, PBOC, etc.
- **Economic Releases**: GDP, inflation, employment data
- **Geopolitical Events**: Trade negotiations, elections
- **Market Events**: IPOs, earnings that impact currencies

### WCF4: Time Period Definition
- **7-day Coverage**: Monday 8 days before report generation to current date
- **Weekend Inclusion**: Saturday/Sunday events included
- **Timezone Handling**: Asian market hours properly captured
- **Cutoff Clarity**: Clear statement of data collection cutoff

### WCF5: Reference Appendix Format
```markdown
## Data Sources & Attribution
- **Collection Period**: [start_date] to [end_date] UTC
- **Primary Sources**: NewsAPI, Yahoo Finance, Alpha Vantage
- **Data Freshness**: Collected at [timestamp]
- **Geographic Coverage**: EM Asia (CN,TW,KR,HK,SG,TH,MY,PH,ID,IN) + US
- **Limitations**: Free API rate limits, English-language sources only
```

## Technical Implementation Details

### Content Generation Models
```python
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime, date

class MarketEvent(BaseModel):
    event_id: str = Field(..., description="Unique event identifier")
    market: str = Field(..., description="Market/currency affected")
    event_type: str = Field(..., description="policy|geopolitical|economic|technical")
    magnitude: float = Field(..., description="Impact magnitude 0-10")
    direction: str = Field(..., description="positive|negative|neutral")
    summary: str = Field(..., max_length=80, description="Event summary")
    drivers: List[str] = Field(..., description="Key causal factors")
    impact_regions: List[str] = Field(..., description="Affected regions")

class WeeklyCommentary(BaseModel):
    commentary_id: str = Field(..., description="Unique commentary identifier")
    week_ending: date = Field(..., description="Week ending date")
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    # Main content sections
    fx_highlights: List[str] = Field(..., description="FX market highlights")
    rates_highlights: List[str] = Field(..., description="Rates market highlights")
    cross_market_themes: List[str] = Field(..., description="Cross-market themes")
    week_ahead: List[str] = Field(..., description="Key events next week")

    # Supporting data
    major_events: List[MarketEvent] = Field(..., description="Key events analyzed")
    data_sources: Dict[str, Any] = Field(..., description="Source attribution")
    word_count: int = Field(..., description="Total word count")

    # Quality metrics
    geographic_coverage: List[str] = Field(..., description="Regions covered")
    market_coverage: List[str] = Field(..., description="Markets analyzed")
    completeness_score: float = Field(..., ge=0.0, le=1.0, description="Coverage completeness")
```

### Dev Agent Implementation
```python
# langgraph_core/agents/dev.py
from langchain_anthropic import ChatAnthropic
from ..models.commentary import WeeklyCommentary, MarketEvent

async def dev_agent(state: WorkflowState) -> WorkflowState:
    """
    Dev Agent - Generates weekly commentary from research data
    """
    try:
        # Extract research data
        news_collection = state.research_data["news_collection"]

        # Analyze news for major events
        major_events = await extract_major_events(news_collection)

        # Generate commentary sections
        llm = ChatAnthropic(model="claude-3-sonnet-20240229")

        commentary = await generate_weekly_commentary(
            major_events=major_events,
            llm=llm,
            geographic_focus=["EM_Asia", "US"],
            word_limit=80
        )

        # Format and save output
        output_path = await save_commentary_to_hedgemonkey(commentary)

        # Update state
        state.generated_content = {
            "commentary": commentary.model_dump(),
            "output_path": output_path,
            "word_count": commentary.word_count,
            "completeness_score": commentary.completeness_score
        }

        state.current_agent = "pm"
        return state

    except Exception as e:
        state.errors.append(f"Dev agent error: {str(e)}")
        raise

async def generate_weekly_commentary(
    major_events: List[MarketEvent],
    llm: ChatAnthropic,
    geographic_focus: List[str],
    word_limit: int
) -> WeeklyCommentary:
    """
    Generate structured weekly commentary using LLM
    """

    # Prepare context for LLM
    context = prepare_commentary_context(major_events, geographic_focus)

    # Generate each section with specific prompts
    fx_highlights = await generate_fx_section(context, llm, word_limit)
    rates_highlights = await generate_rates_section(context, llm, word_limit)
    cross_market_themes = await generate_themes_section(context, llm, word_limit)
    week_ahead = await generate_forward_section(context, llm, word_limit)

    # Compile commentary
    commentary = WeeklyCommentary(
        commentary_id=f"weekly_{datetime.now().strftime('%Y%m%d')}",
        week_ending=get_week_ending_date(),
        fx_highlights=fx_highlights,
        rates_highlights=rates_highlights,
        cross_market_themes=cross_market_themes,
        week_ahead=week_ahead,
        major_events=major_events,
        word_count=calculate_total_words([fx_highlights, rates_highlights, cross_market_themes, week_ahead])
    )

    return commentary
```

### PM Agent Validation
```python
# langgraph_core/agents/pm.py
async def pm_agent(state: WorkflowState) -> WorkflowState:
    """
    PM Agent - Validates and delivers weekly commentary
    """
    try:
        commentary_data = state.generated_content["commentary"]
        commentary = WeeklyCommentary.model_validate(commentary_data)

        # Quality validation checks
        validation_results = await validate_commentary_quality(commentary)

        if validation_results["passed"]:
            # Final delivery
            await deliver_commentary(commentary, state.generated_content["output_path"])
            state.validation_status = "approved"
        else:
            # Quality issues identified
            state.validation_status = "rejected"
            state.errors.extend(validation_results["issues"])

        # Archive and log completion
        await archive_workflow_completion(state)

        return state

    except Exception as e:
        state.errors.append(f"PM agent error: {str(e)}")
        raise

async def validate_commentary_quality(commentary: WeeklyCommentary) -> Dict[str, Any]:
    """
    Validate commentary meets quality standards
    """
    issues = []

    # Word count validation
    if commentary.word_count > 320:  # 4 sections × 80 words
        issues.append(f"Exceeds word limit: {commentary.word_count}/320 words")

    # Geographic coverage validation
    required_regions = ["CN", "US"]  # Minimum coverage
    covered_regions = commentary.geographic_coverage
    missing_regions = [r for r in required_regions if r not in covered_regions]
    if missing_regions:
        issues.append(f"Missing geographic coverage: {missing_regions}")

    # Content completeness validation
    if not commentary.fx_highlights:
        issues.append("Missing FX highlights section")
    if not commentary.rates_highlights:
        issues.append("Missing rates highlights section")

    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "quality_score": 1.0 - (len(issues) * 0.2)
    }
```

## Output File Structure

### Hedgemonkey Project Integration
```
projects/hedgemonkey/
├── reports/
│   ├── weekly/
│   │   ├── 2025-01-27-weekly-commentary.md
│   │   ├── 2025-01-20-weekly-commentary.md
│   │   └── archive/
│   └── templates/
│       └── weekly-template.md
└── data/
    ├── sources/
    │   ├── 2025-01-27-news-collection.json
    │   └── metadata/
    └── cache/
```

### Commentary File Format
```markdown
# Weekly Market Commentary - Week Ending Jan 27, 2025

## FX Markets
**EM Asia**: CNY strengthened 0.8% vs USD following PBOC's liquidity injection and improved manufacturing PMI. JPY declined 1.2% on BoJ dovish signals, while KRW gained 0.5% on export optimism. Regional currencies benefited from risk-on sentiment.

## Interest Rates
**US**: 10Y Treasury yields fell 8bp to 4.15% amid dovish Fed rhetoric and softer inflation expectations. **Asia**: JGB yields compressed following BoJ's yield curve control adjustments, while Chinese bonds rallied on policy easing expectations.

## Cross-Market Themes
Risk appetite improved across EM Asia as China's stimulus measures and US-China trade dialogue progress supported regional sentiment. Oil price stability (+2.1%) and tech sector resilience aided broader market confidence.

## Week Ahead
Key events: FOMC meeting (Wed), China PMI data (Fri), BoJ policy decision (Thu). Watch for US GDP revision impact on Fed expectations and any China policy announcements during Lunar New Year preparation.

---
*Generated: 2025-01-27 14:30 UTC | Word count: 156*

## Data Sources & Attribution
- **Collection Period**: 2025-01-20 00:00 to 2025-01-27 14:00 UTC
- **Primary Sources**: NewsAPI, Yahoo Finance, Alpha Vantage
- **Geographic Coverage**: EM Asia (CN,TW,KR,HK,SG,TH,MY,PH,ID,IN) + US
- **Limitations**: Free API rate limits, English-language sources only
```

## Testing Requirements

### Unit Tests
- Test commentary generation with sample events
- Test word count validation and limits
- Test file output formatting
- Test PM agent quality validation

### Integration Tests
- Test complete workflow from research to delivery
- Test error handling during content generation
- Test file delivery to hedgemonkey project
- Test multi-agent coordination

### Quality Tests
- Human review of generated commentary samples
- Validate geographic coverage completeness
- Test factual accuracy with known market events
- Verify professional tone and readability


## Testing Status 🧪

- [ ] **TESTED** - Testing pending
  - **Test Results**: TBD
  - **Unit Tests**: TBD
  - **Integration Tests**: TBD
  - **Test Date**: TBD

## Definition of Done

- [ ] All acceptance criteria completed and tested
- [ ] Commentary generation produces 50-80 word summaries
- [ ] File delivery to hedgemonkey project operational
- [ ] PM agent quality validation functional
- [ ] Multi-agent coordination proven end-to-end
- [ ] Ready for Story 1.5 (End-to-End Integration)

## Risk Mitigation

**Risk**: Generated content lacks market insight or accuracy
**Mitigation**: Human review process, fact-checking against multiple sources

**Risk**: Word count limits too restrictive for meaningful analysis
**Mitigation**: Iterative refinement based on initial outputs, flexible limits

**Risk**: File delivery conflicts with existing hedgemonkey structure
**Mitigation**: Coordinate with hedgemonkey project requirements, test integration

## Success Criteria

- Weekly commentary generation operational
- Content meets quality and format standards
- File delivery integrates with hedgemonkey project
- Multi-agent workflow coordination proven
- Foundation ready for end-to-end integration testing (Story 1.5)