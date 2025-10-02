# Postgres MCP Pro - AI-Enhanced Database Optimization

## Overview
Postgres MCP Pro is an open-source Model Context Protocol (MCP) server designed to help developers and AI agents optimize PostgreSQL database performance throughout the entire development lifecycle.

## Key Philosophy
Combines generative AI with deterministic optimization algorithms to provide principled, repeatable database performance analysis that is more reliable than pure LLM-based approaches.

## Core Features

### 1. Database Health Analysis
**Comprehensive monitoring and analysis capabilities:**

- **Index Health Checks**: Identify unused, duplicate, or inefficient indexes
- **Connection Utilization Monitoring**: Track connection pool usage and patterns
- **Buffer Cache Analysis**: Analyze memory usage and cache hit ratios
- **Vacuum Health Tracking**: Monitor table maintenance and bloat
- **Sequence Limit Monitoring**: Check sequence exhaustion risks
- **Replication Lag Detection**: Monitor replication performance

### 2. Performance Optimization
**Industrial-strength optimization algorithms:**

- **Index Tuning**: Advanced algorithms for index recommendations
- **Query Plan Analysis**: Deep dive into execution plans
- **Hypothetical Index Simulation**: Test index effectiveness without creation
- **Workload Performance Recommendations**: Analyze query patterns for optimization

### 3. Safety and Access Control
**Configurable security and access modes:**

- **Read/Write Access Modes**: Control operation permissions
- **Restricted Mode**: Limited operations for safety
- **Unrestricted Mode**: Full database access for advanced users
- **Safe SQL Execution**: Protected query execution
- **Read-only Transaction Support**: Non-destructive analysis

### 4. Schema Intelligence
**Advanced schema analysis and management:**

- Schema listing and exploration
- Table relationship analysis
- Column statistics and distribution
- Constraint and index mapping

## Installation Options

### Docker Installation
```bash
# Pull the Docker image
docker pull crystaldba/postgres-mcp

# Run with environment variables
docker run -e POSTGRES_CONNECTION_STRING="postgresql://user:pass@host:5432/db" \
           crystaldba/postgres-mcp
```

### Python Installation (pipx)
```bash
# Install using pipx (recommended)
pipx install postgres-mcp

# Run the server
postgres-mcp
```

### Python Installation (uv)
```bash
# Install using uv
uv pip install postgres-mcp

# Alternative installation method
uv add postgres-mcp
```

## Configuration

### Connection Configuration
```bash
# Environment variable method
export POSTGRES_CONNECTION_STRING="postgresql://username:password@localhost:5432/database"

# Configuration file method
postgres-mcp --config /path/to/config.json
```

### Access Modes
```bash
# Restricted mode (safer, limited operations)
postgres-mcp --mode restricted

# Unrestricted mode (full access)
postgres-mcp --mode unrestricted
```

### Transport Options
```bash
# Standard I/O transport (default)
postgres-mcp --transport stdio

# Server-Sent Events transport
postgres-mcp --transport sse --port 8080
```

## MCP Tools

### Core Database Tools

#### `list_schemas`
**Purpose**: List all database schemas
**Access**: Read-only
**Returns**: Schema names and metadata

#### `execute_sql`
**Purpose**: Execute SQL queries safely
**Access**: Configurable (read-only/read-write)
**Safety**: Transaction-protected execution

#### `explain_query`
**Purpose**: Analyze query execution plans
**Features**:
- Cost analysis
- Index usage examination
- Performance bottleneck identification
- Optimization suggestions

#### `analyze_workload_indexes`
**Purpose**: Comprehensive index analysis for workloads
**Features**:
- Index usage statistics
- Duplicate index detection
- Missing index recommendations
- Index efficiency scoring

#### `analyze_db_health`
**Purpose**: Overall database health assessment
**Metrics**:
- Connection statistics
- Buffer cache performance
- Vacuum effectiveness
- Sequence usage
- Replication status

### Advanced Analysis Tools

#### `get_table_stats`
**Purpose**: Detailed table statistics
**Information**:
- Row counts and estimates
- Table size and bloat
- Index usage patterns
- Column statistics

#### `check_index_health`
**Purpose**: Specific index health analysis
**Features**:
- Index bloat detection
- Usage frequency analysis
- Efficiency measurements
- Maintenance recommendations

#### `analyze_slow_queries`
**Purpose**: Identify and analyze slow-performing queries
**Capabilities**:
- Query pattern recognition
- Performance trend analysis
- Optimization recommendations
- Resource usage tracking

## PostgreSQL Version Support

### Supported Versions
- **PostgreSQL 13**: Basic support
- **PostgreSQL 14**: Full support
- **PostgreSQL 15**: Optimized support (primary focus)
- **PostgreSQL 16**: Optimized support (primary focus)
- **PostgreSQL 17**: Latest features support (primary focus)

### Version-Specific Features
- Utilizes version-specific system catalogs
- Leverages latest PostgreSQL optimization features
- Backwards compatibility for older versions

## Use Cases

### Development Lifecycle
**During Development**:
- Schema optimization guidance
- Query performance validation
- Index strategy development
- Connection pattern analysis

**Pre-Production**:
- Performance testing support
- Scalability analysis
- Configuration optimization
- Capacity planning

**Production Monitoring**:
- Health monitoring and alerting
- Performance regression detection
- Optimization opportunity identification
- Maintenance scheduling

### AI Agent Integration
**Autonomous Database Management**:
- Automated health checks
- Intelligent index recommendations
- Query optimization suggestions
- Performance trend analysis

**Development Assistance**:
- Real-time query optimization
- Schema design validation
- Performance impact assessment
- Best practice enforcement

## Advanced Features

### Industrial-Strength Algorithms
**Index Optimization**:
- Classical optimization algorithms
- Deterministic recommendations
- Reproducible results
- Scientific approach to tuning

**Query Analysis**:
- Cost-based optimization
- Statistical analysis
- Pattern recognition
- Performance modeling

### Hypothetical Index Testing
**Safe Testing Environment**:
- Test index effectiveness without creation
- Analyze potential performance impact
- Compare multiple index strategies
- Risk-free optimization exploration

### Workload Analysis
**Comprehensive Workload Understanding**:
- Query pattern identification
- Resource usage analysis
- Performance bottleneck detection
- Optimization priority ranking

## Integration Patterns

### MCP Client Integration
```json
{
  "mcpServers": {
    "postgres-mcp-pro": {
      "command": "postgres-mcp",
      "args": ["--mode", "restricted"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://user:pass@host:5432/db"
      }
    }
  }
}
```

### Docker Compose Integration
```yaml
version: '3.8'
services:
  postgres-mcp:
    image: crystaldba/postgres-mcp
    environment:
      - POSTGRES_CONNECTION_STRING=postgresql://user:pass@postgres:5432/db
    depends_on:
      - postgres
```

### CI/CD Integration
```bash
# Performance testing in CI
postgres-mcp --mode restricted \
             --analyze-schema \
             --output-format json > db-health-report.json
```

## Security Considerations

### Access Control
- **Principle of Least Privilege**: Use restricted mode by default
- **Connection Security**: Encrypted connections recommended
- **Credential Management**: Environment variable configuration
- **Audit Logging**: Track all database operations

### Safe Operation Modes
- **Read-Only Mode**: Analysis without modification
- **Transaction Protection**: Rollback capability for testing
- **Query Validation**: Pre-execution query analysis
- **Resource Limits**: Configurable operation limits

## Performance and Scalability

### Optimization Strategies
- **Connection Pooling**: Efficient connection management
- **Query Caching**: Cache frequently used analysis results
- **Batch Operations**: Minimize database round trips
- **Asynchronous Analysis**: Non-blocking operations

### Resource Management
- **Memory Usage**: Efficient memory utilization
- **CPU Optimization**: Parallel analysis capabilities
- **I/O Efficiency**: Minimized disk access patterns
- **Network Optimization**: Compressed data transfer

## Troubleshooting

### Common Issues
**Connection Problems**:
- Verify connection string format
- Check network connectivity
- Validate credentials
- Test firewall rules

**Permission Issues**:
- Ensure adequate database privileges
- Check schema access permissions
- Validate role assignments
- Review security policies

**Performance Issues**:
- Monitor resource usage
- Check query complexity
- Analyze connection patterns
- Review configuration settings

## Best Practices

### Development Workflow
1. **Start with Health Analysis**: Always begin with `analyze_db_health`
2. **Use Restricted Mode**: Default to restricted mode for safety
3. **Incremental Optimization**: Make changes gradually
4. **Monitor Impact**: Track performance changes
5. **Document Changes**: Maintain optimization history

### Production Deployment
1. **Regular Health Checks**: Schedule periodic analysis
2. **Performance Monitoring**: Continuous performance tracking
3. **Capacity Planning**: Proactive resource management
4. **Change Management**: Controlled optimization rollouts
5. **Backup Strategy**: Ensure recoverability

## Community and Support

### Project Information
- **Developer**: Crystal DBA
- **License**: Open-source
- **Repository**: https://github.com/crystaldba/postgres-mcp
- **Issues**: GitHub issue tracker

### Contributing
- **Code Contributions**: Pull requests welcome
- **Documentation**: Help improve documentation
- **Testing**: Report bugs and performance issues
- **Feature Requests**: Suggest new capabilities

### Resources
- **Documentation**: Comprehensive guides and examples
- **Community Support**: GitHub discussions
- **Professional Support**: Crystal DBA consulting services
- **Training**: Database optimization workshops