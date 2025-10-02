# External API Constraints and Limitations

**CRITICAL DEVELOPMENT BLOCKER RESOLUTION**
*Created: 2025-09-21 | Status: Required for Story 1.3 Development*

## 🚨 CRITICAL FINDINGS - DEVELOPMENT IMPACT

### **Yahoo Finance API - MAJOR RISK IDENTIFIED**

**Status:** ❌ **HIGH RISK - UNRELIABLE FOR PRODUCTION**

**Key Constraints:**
- **No Official API**: yfinance library scrapes web endpoints, not official API
- **Unpredictable Rate Limits**: No published limits, frequent blocking/blacklisting
- **Recent Tightening**: Enhanced blocking since early 2024
- **IP-Based Blocking**: Rapid requests trigger temporary/permanent bans
- **Zero Recourse**: Cannot appeal for more quota or unblocking

**Immediate Impact on MADF:**
- Development will be blocked by unpredictable rate limiting
- Testing phase will hit walls with IP bans
- No guaranteed service availability for MVP delivery
- Potential complete development halt mid-project

**CRITICAL RECOMMENDATION: SWITCH TO RELIABLE ALTERNATIVE**

---

### **Alternative Financial Data Sources - EVALUATED**

#### **Alpha Vantage** ✅ **RECOMMENDED PRIMARY**
- **Free Tier**: 500 requests/day, 5 requests/minute
- **Predictable**: Clear published limits
- **Reliable**: Official API with SLA
- **Cost**: $49.99/month for premium (25,000 requests/day)
- **Coverage**: Forex, stocks, crypto, economic indicators

#### **IEX Cloud** ✅ **RECOMMENDED BACKUP**
- **Free Tier**: 500,000 messages/month
- **Pay-as-you-go**: Clear pricing model
- **High Reliability**: Enterprise-grade infrastructure
- **Asia/G10 Coverage**: Comprehensive forex data

---

### **News API Constraints**

#### **NewsAPI.org** ✅ **RECOMMENDED**
- **Free Tier**: 1,000 requests/month for development
- **Developer Friendly**: Clear documentation and limits
- **Rate Limits**: Reasonable for MVP testing
- **Coverage**: Global financial news sources
- **Cost**: $449/month for production (100,000 requests)

#### **Google News via Gemini API** ⚠️ **LIMITED UTILITY**
- **Free Tier**: 1,500 requests/day (Gemini 1.5 Flash)
- **Issue**: Not specifically a news API, general AI service
- **Rate Limits**: Resets midnight Pacific time
- **Coverage**: Indirect news access through AI queries

---

### **Reuters Data Access**

#### **Third-Party Reuters APIs** ⚠️ **EXPENSIVE**
- **RapidAPI**: Custom pricing, unclear limits
- **Zyla API Hub**: Market data focus, premium pricing
- **Rate Limits**: ~6 requests/minute reported
- **Official Thomson Reuters**: £700+/month for real-time data

#### **Reuters Scraper API** ⚠️ **LEGAL RISK**
- **Provider**: Bright Data (web scraping)
- **Legal Risk**: Scraping may violate ToS
- **Reliability**: Subject to anti-scraping measures

---

## 📋 **IMMEDIATE ACTION PLAN**

### **1. SWITCH PRIMARY DATA SOURCE** ⚡ **URGENT**

```yaml
# REVISED MCP Server Configuration
financial_data_sources:
  primary: alpha_vantage  # CHANGED FROM yahoo_finance
  backup: iex_cloud

news_sources:
  primary: newsapi_org    # CHANGED FROM google_news
  validation: reuters_scraper  # RISK ACCEPTED FOR MVP

api_keys_required:
  - ALPHA_VANTAGE_API_KEY    # Free tier available
  - IEX_CLOUD_API_TOKEN      # Free tier available
  - NEWSAPI_ORG_KEY          # Free tier available
```

### **2. UPDATE ARCHITECTURE DOCUMENTATION** ⚡ **URGENT**

- Update `docs/architecture/7-external-apis.md`
- Revise MCP server configurations in Story 1.3
- Update environment variables in development workflow

### **3. COST AND LIMIT PLANNING**

```bash
# Development Phase (48 hours)
Alpha Vantage Free: 500 requests/day × 2 days = 1,000 requests
NewsAPI Free: 1,000 requests/month = sufficient for MVP
IEX Cloud Free: 500,000 messages/month = more than sufficient

# Monthly Production Estimates (if deployed)
Alpha Vantage Premium: $49.99/month (25,000 requests/day)
NewsAPI Production: $449/month (100,000 requests/month)
Total Monthly: ~$500/month for production scale
```

---

## 🛡️ **RISK MITIGATION STRATEGIES**

### **Rate Limit Management**
```python
# Implement in all MCP servers
RATE_LIMITS = {
    'alpha_vantage': {'requests_per_minute': 5, 'daily_limit': 500},
    'newsapi': {'requests_per_day': 33, 'monthly_limit': 1000},  # Conservative
    'iex_cloud': {'burst_limit': 100, 'monthly_limit': 500000}
}

# Exponential backoff implementation
async def api_call_with_backoff(api_func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await api_func()
        except RateLimitError:
            wait_time = 2 ** attempt
            await asyncio.sleep(wait_time)
    raise MaxRetriesExceeded()
```

### **Fallback Strategies**
1. **Cache-First Policy**: Check cache before API calls
2. **Multi-Source Redundancy**: Automatic failover between Alpha Vantage and IEX Cloud
3. **Graceful Degradation**: Continue with cached data during outages
4. **User Communication**: Report data source status in outputs

---

## 📊 **REVISED SUCCESS METRICS**

### **API Reliability Targets**
- **Uptime**: 99.5% during 48-hour MVP development
- **Rate Limit Adherence**: Zero rate limit violations
- **Fallback Activation**: < 5% of requests use fallback data
- **Cost Control**: Stay within free tier limits during development

### **Data Quality Metrics**
- **Freshness**: Data no older than 4 hours for forex
- **Coverage**: All Asia/G10 currency pairs available
- **Accuracy**: Cross-validation between sources when possible

---

## ✅ **VERIFICATION CHECKLIST**

- [ ] Alpha Vantage API key obtained and tested
- [ ] IEX Cloud API key obtained and tested
- [ ] NewsAPI key obtained and tested
- [ ] MCP server configurations updated for new sources
- [ ] Rate limiting implemented in all agents
- [ ] Fallback strategies tested
- [ ] Cost monitoring implemented
- [ ] Documentation updated across all affected files

---

**STATUS**: This document resolves the critical API constraints blocking issue. Development can proceed with reliable, documented alternatives to the problematic Yahoo Finance scraping approach.

**NEXT STEPS**:
1. Obtain API keys for recommended services
2. Update MCP server configurations
3. Implement rate limiting and fallback strategies
4. Test integration with new data sources