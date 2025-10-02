# Epic 1: Multi-Agent Development Framework MVP

**Epic Duration**: 2-3 weeks (Phase 1)
**Epic Status**: Ready for Implementation
**Dependencies**: None (foundational epic)

## Epic Overview

Develop and validate a 4-agent LangGraph system (Planning + Research + Dev + PM) with Pydantic state management, demonstrating prototype multi-agent coordination for research commentary generation using free news APIs.

## Implementation Stories

### Week 1: Foundation Setup

#### [Story 1.1: Basic LangGraph Setup and State Management](./story-1-1-langgraph-setup.md) ✅ 🧪
**Duration**: 3-4 days | **Dependencies**: None | **Status**: ✅ COMPLETE & TESTED

Establish LangGraph orchestration foundation with 4-agent nodes, Pydantic state management, persistence, and observability.

**Key Deliverables**:
- StateGraph with Planning, Research, Dev, PM nodes ✅
- Pydantic WorkflowState model with validation ✅
- LangSmith integration for tracing ✅
- SQLite checkpointing system ✅
- **Test Results**: 100% success rate (21 unit + 9 integration tests)

#### [Story 1.2: Manual BMAD Planning Integration](./story-1-2-bmad-planning.md)
**Duration**: 2-3 days | **Dependencies**: Story 1.1

Integrate manual BMAD planning workflow with LangGraph execution, enabling human-generated plans to drive agent coordination.

**Key Deliverables**:
- BMAD chat to structured plan conversion
- ResearchPlan Pydantic model
- Planning Agent LangGraph node
- Human approval workflow

### Week 2: Data Integration & Processing

#### [Story 1.3: Free News API Integration via mcp-use](./story-1-3-news-api-integration.md)
**Duration**: 4-5 days | **Dependencies**: Story 1.1, 1.2

Implement news collection from multiple free APIs through mcp-use client with HTTP bridge architecture.

**Key Deliverables**:
- Node.js HTTP bridge service with mcp-use
- Research Agent with multi-source news access
- NewsAPI, Yahoo Finance, Alpha Vantage, Google News integration
- Geographic coverage for EM Asia + US markets

#### [Story 1.4: Weekly Market Commentary Generation](./story-1-4-commentary-generation.md)
**Duration**: 3-4 days | **Dependencies**: Story 1.3

Generate weekly market commentary using Dev Agent with 50-80 word summary constraints and professional formatting.

**Key Deliverables**:
- Dev Agent content generation
- LLM integration for commentary creation
- PM Agent quality validation
- File output to hedgemonkey project

### Week 3: Integration & User Interface

#### [Story 1.5: End-to-End Workflow Integration](./story-1-5-end-to-end-integration.md)
**Duration**: 2-3 days | **Dependencies**: All previous stories

Complete workflow integration with performance monitoring, error recovery, and quality assurance.

**Key Deliverables**:
- Complete workflow execution validation
- Performance monitoring with LangSmith
- Error recovery and resilience testing
- Quality assurance and manual validation

#### [Story 1.6: Claude Code Integration and User Interface](./story-1-6-claude-code-integration.md)
**Duration**: 2-3 days | **Dependencies**: Story 1.5

Seamless Claude Code interface integration enabling users to trigger and monitor research workflows.

**Key Deliverables**:
- Claude Code command interface
- Progress tracking and status updates
- Cost reporting and transparency
- Error handling with user-friendly messages

## Technical Architecture Summary

### Core Technologies
- **LangGraph**: Multi-agent orchestration and state management
- **Pydantic**: Type-safe state models and validation
- **mcp-use**: Tool integration via HTTP bridge
- **Claude Sonnet**: Cost-effective LLM for agent operations
- **LangSmith**: Observability and performance monitoring

### Data Sources (Corrected - No Bloomberg Terminal)
- **NewsAPI** (primary): Comprehensive financial news
- **Yahoo Finance**: Market data and financial news
- **Alpha Vantage**: Economic indicators and sentiment
- **Google News**: Supplementary coverage and verification

### Geographic Coverage
- **EM Asia**: CN, TW, KR, HK, SG, TH, MY, PH, ID, IN
- **US Markets**: USD, Fed policy, Treasury yields
- **Focus**: FX & rates, equity/commodities for outsized moves only

### Output Specifications
- **Format**: 50-80 word summaries per major market movement
- **Delivery**: Weekly commentary files to hedgemonkey project
- **Quality**: Professional analysis with quantitative context
- **Attribution**: Data source references separate from content

## Success Criteria

### Technical Success
- [ ] 4-agent LangGraph system operational
- [ ] Free news API data collection functional
- [ ] Multi-agent coordination proven reliable
- [ ] State management with Pydantic validation
- [ ] Error recovery and checkpoint system working

### Performance Success
- [ ] Workflow execution <30 minutes
- [ ] Token usage <50,000 per workflow
- [ ] API costs <$5 per commentary
- [ ] Success rate >90% under normal conditions
- [ ] Geographic coverage 100% for required regions

### Quality Success
- [ ] Generated commentary meets 50-80 word standards
- [ ] Professional tone and market insight demonstrated
- [ ] Human validation confirms output quality
- [ ] File delivery integrates with hedgemonkey project
- [ ] Claude Code interface provides smooth user experience

## Risk Assessment

### **Resolved Risks** (via Technical Alignment)
- ✅ **Data Source Complexity**: Simplified to free APIs
- ✅ **Deployment Complexity**: Local-first approach
- ✅ **Scale Premature Optimization**: Prototype-first focus

### **Monitored Risks**
- **mcp-use Integration**: HTTP bridge complexity managed with testing
- **LangGraph Learning**: Minimal workflow approach reduces complexity
- **API Rate Limits**: Caching and fallback sources implemented
- **Multi-language Coordination**: Clear interfaces and error handling

## Next Steps After Epic 1

### Phase 2: Sophistication Layer (4-5 weeks)
- Bloomberg Terminal API integration
- Advanced validation with ValidationAgent
- HITL dashboard for human oversight
- Enhanced error handling and recovery

### Phase 3: Production Features (ongoing)
- Quantitative analytics integration
- Enterprise monitoring and alerting
- Container deployment and scaling
- Machine learning optimization

## Implementation Notes

This Epic 1 implementation follows the corrected technical alignment established in `docs/prd/technical-alignment.md`, ensuring:

1. **Free news APIs** replace Bloomberg Terminal requirements
2. **Local development** approach instead of cloud deployment
3. **Prototype foundation** with incremental sophistication
4. **Single-user focus** with multi-user capabilities deferred to Phase 2

All stories include detailed acceptance criteria, technical specifications, and testing requirements to ensure successful 2-3 week delivery of the MVP foundation.

## Testing Status Overview 🧪

| Story | Complete | Tested | Test Results |
|-------|----------|--------|--------------|
| 1.1: LangGraph Setup | ✅ | ✅ | 100% (30/30 tests) |
| 1.2: BMAD Planning | ⏳ | 🧪 | Testing Ready |
| 1.3: News API Integration | ⏳ | 🧪 | Testing Ready |
| 1.4: Commentary Generation | ⏳ | 🧪 | Testing Ready |
| 1.5: End-to-End Integration | ⏳ | 🧪 | Testing Ready |
| 1.6: Claude Code Integration | ⏳ | 🧪 | Testing Ready |

**Legend**: ✅ Complete | 🧪 Test Infrastructure Ready | ⏳ Pending Implementation

**Test Results Location**: `D:\BT\madf\` for all completed testing