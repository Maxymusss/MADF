# 9. Database Schema

Since we're using file-based JSON storage instead of a traditional database, our "schema" is defined by directory structures and JSON document formats:

## File System Database Structure

```plaintext
data/
├── messages/                        # Message queue "tables"
│   ├── inbox/                      # Active messages
│   │   ├── pm-agent/
│   │   ├── research-agent-1/
│   │   ├── research-agent-2/
│   │   └── validator-agent/
│   ├── outbox/                     # Processed messages
│   │   └── 2025-09-21/
│   ├── broadcast/                  # System-wide messages
│   └── dead-letter/               # Failed messages
│
├── logs/                           # Logging "tables"
│   ├── agents/
│   │   ├── pm-agent/
│   │   │   ├── errors/
│   │   │   └── decisions/
│   │   ├── research-agent-1/
│   │   │   ├── errors/
│   │   │   ├── queries/
│   │   │   └── results/
│   │   ├── research-agent-2/
│   │   │   ├── errors/
│   │   │   ├── queries/
│   │   │   └── results/
│   │   └── validator-agent/
│   │       ├── errors/
│   │       ├── conflicts/
│   │       └── resolutions/
│   └── learning/
│       ├── error-patterns.json
│       └── improvement-metrics.json
│
├── cache/                          # Response cache "tables"
│   ├── yahoo-finance/
│   │   └── {date}/
│   ├── google-news/
│   │   └── {date}/
│   └── reuters/
│       └── {date}/
│
├── reports/                        # Report storage
│   ├── weekly/
│   │   └── 2025-W38-asia-g10-fx.md
│   ├── drafts/
│   └── templates/
│
└── state/                          # Agent state persistence
    ├── pm-agent-state.json
    ├── research-agent-1-state.json
    ├── research-agent-2-state.json
    └── validator-agent-state.json
```

## Data Retention Policies

```python
RETENTION_POLICIES = {
    "messages": {
        "inbox": "24 hours",      # Active messages
        "outbox": "7 days",        # Processed messages
        "dead-letter": "30 days"   # Failed messages for analysis
    },
    "logs": {
        "errors": "90 days",       # Error logs for learning
        "queries": "7 days",       # Query logs for optimization
        "results": "30 days"       # Results for validation
    },
    "cache": {
        "yahoo-finance": "5 minutes",  # Real-time data
        "google-news": "15 minutes",   # News updates
        "reuters": "10 minutes"         # Authoritative data
    },
    "reports": {
        "weekly": "1 year",        # Historical reports
        "drafts": "7 days"         # Temporary drafts
    }
}
```
