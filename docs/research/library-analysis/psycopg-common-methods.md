# psycopg (psycopg3) - Commonly Used Methods

**Library**: psycopg (version 3)
**Type**: Direct Python Library
**Purpose**: PostgreSQL database adapter
**Documentation**: https://www.psycopg.org/psycopg3/docs/
**Database**: PostgreSQL 12+

---

## Installation & Setup

```python
import psycopg

# Synchronous connection
conn = psycopg.connect(
    "postgresql://user:password@localhost:5432/dbname"
)

# Or with parameters
conn = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="database",
    user="user",
    password="password"
)

# Async connection (asyncio)
import psycopg_async
conn = await psycopg_async.AsyncConnection.connect(
    "postgresql://user:password@localhost:5432/dbname"
)
```

---

## Core Connection Methods

### 1. psycopg.connect()

**Purpose**: Create database connection

**Signature**:
```python
connect(
    conninfo: str = None,
    *,
    host: str = None,
    port: int = 5432,
    dbname: str = None,
    user: str = None,
    password: str = None,
    **kwargs
) -> Connection
```

**Returns**: Connection object

**Usage Priority**: HIGH - Required for all operations

**Example**:
```python
# Connection string
conn = psycopg.connect("postgresql://localhost/madf_logs")

# Individual parameters
conn = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="madf_logs",
    user="madf",
    password="password"
)

# Context manager (recommended)
with psycopg.connect("postgresql://localhost/madf_logs") as conn:
    # Use connection
    pass
# Auto-closed
```

---

## Connection Object Methods

### 2. conn.execute()

**Purpose**: Execute query directly on connection (convenience method)

**Signature**:
```python
execute(
    query: str | Composable,
    params: tuple | dict = None
) -> Cursor
```

**Returns**: Cursor (can chain fetch methods)

**Usage Priority**: HIGH - Convenient query execution

**Example**:
```python
# Simple query
result = conn.execute("SELECT version()")
print(result.fetchone())

# With parameters (tuple)
result = conn.execute(
    "SELECT * FROM logs WHERE level = %s",
    ("ERROR",)
)

# With named parameters (dict)
result = conn.execute(
    "SELECT * FROM logs WHERE level = %(level)s",
    {"level": "ERROR"}
)

# Chained fetch
row = conn.execute("SELECT * FROM logs LIMIT 1").fetchone()
```

---

### 3. conn.cursor()

**Purpose**: Create cursor for query execution

**Signature**:
```python
cursor(
    *,
    row_factory: RowFactory = None,
    binary: bool = False
) -> Cursor
```

**Returns**: Cursor object

**Usage Priority**: MEDIUM - Explicit cursor control

**Example**:
```python
# Basic cursor
cur = conn.cursor()
cur.execute("SELECT * FROM logs")
rows = cur.fetchall()
cur.close()

# Context manager (recommended)
with conn.cursor() as cur:
    cur.execute("SELECT * FROM logs")
    rows = cur.fetchall()
# Auto-closed

# Named tuples
from psycopg.rows import dict_row
with conn.cursor(row_factory=dict_row) as cur:
    cur.execute("SELECT * FROM logs")
    for row in cur:
        print(row["level"], row["message"])
```

---

### 4. conn.commit()

**Purpose**: Commit current transaction

**Signature**:
```python
commit() -> None
```

**Usage Priority**: HIGH - Transaction management

**Example**:
```python
conn.execute("INSERT INTO logs (level, message) VALUES (%s, %s)", ("INFO", "Test"))
conn.commit()
```

---

### 5. conn.rollback()

**Purpose**: Rollback current transaction

**Signature**:
```python
rollback() -> None
```

**Usage Priority**: HIGH - Error handling

**Example**:
```python
try:
    conn.execute("INSERT INTO logs ...")
    conn.execute("UPDATE settings ...")
    conn.commit()
except Exception:
    conn.rollback()
    raise
```

---

### 6. conn.close()

**Purpose**: Close connection and free resources

**Signature**:
```python
close() -> None
```

**Usage Priority**: HIGH - Resource cleanup

**Example**:
```python
conn = psycopg.connect(...)
try:
    # Use connection
    pass
finally:
    conn.close()

# Better: use context manager
with psycopg.connect(...) as conn:
    pass  # Auto-closed
```

---

## Cursor Object Methods

### 7. cursor.execute()

**Purpose**: Execute SQL query

**Signature**:
```python
execute(
    query: str | Composable,
    params: tuple | dict = None
) -> Cursor
```

**Returns**: self (allows chaining)

**Usage Priority**: HIGH - Core query execution

**Example**:
```python
cur = conn.cursor()

# Simple query
cur.execute("SELECT * FROM logs")

# Parameterized (tuple)
cur.execute("SELECT * FROM logs WHERE level = %s", ("ERROR",))

# Named parameters (dict)
cur.execute(
    "INSERT INTO logs (level, message) VALUES (%(level)s, %(msg)s)",
    {"level": "INFO", "msg": "Test"}
)

# Chaining
rows = cur.execute("SELECT * FROM logs").fetchall()
```

---

### 8. cursor.executemany()

**Purpose**: Execute query for multiple parameter sets (batch insert/update)

**Signature**:
```python
executemany(
    query: str | Composable,
    params_seq: Sequence[tuple | dict]
) -> None
```

**Usage Priority**: MEDIUM - Batch operations

**Example**:
```python
# Batch insert
data = [
    ("INFO", "Message 1"),
    ("ERROR", "Message 2"),
    ("WARN", "Message 3")
]
cur.executemany(
    "INSERT INTO logs (level, message) VALUES (%s, %s)",
    data
)
conn.commit()
```

---

### 9. cursor.fetchone()

**Purpose**: Fetch next row from query result

**Signature**:
```python
fetchone() -> tuple | None
```

**Returns**: Single row or None if no more rows

**Usage Priority**: HIGH - Retrieve single result

**Example**:
```python
cur.execute("SELECT * FROM logs ORDER BY created_at DESC LIMIT 1")
row = cur.fetchone()
if row:
    print(row)
```

---

### 10. cursor.fetchall()

**Purpose**: Fetch all remaining rows

**Signature**:
```python
fetchall() -> list[tuple]
```

**Returns**: List of all rows

**Usage Priority**: HIGH - Retrieve all results

**Example**:
```python
cur.execute("SELECT * FROM logs")
rows = cur.fetchall()
for row in rows:
    print(row)
```

---

### 11. cursor.fetchmany()

**Purpose**: Fetch next N rows

**Signature**:
```python
fetchmany(size: int = None) -> list[tuple]
```

**Parameters**:
- `size`: Number of rows (uses cursor.arraysize if None)

**Returns**: List of up to N rows

**Usage Priority**: MEDIUM - Paginated retrieval

**Example**:
```python
cur.execute("SELECT * FROM logs")
while batch := cur.fetchmany(100):
    process_batch(batch)
```

---

### 12. cursor (iteration)

**Purpose**: Iterate over result rows

**Usage Priority**: HIGH - Memory-efficient iteration

**Example**:
```python
cur.execute("SELECT * FROM logs")
for row in cur:
    print(row)  # Memory efficient, doesn't load all rows
```

---

## Connection Pool

### 13. ConnectionPool

**Purpose**: Manage connection pool for concurrent access

**Signature**:
```python
from psycopg_pool import ConnectionPool

pool = ConnectionPool(
    conninfo: str,
    min_size: int = 4,
    max_size: int = None,
    **kwargs
)
```

**Usage Priority**: MEDIUM - Production deployments

**Example**:
```python
from psycopg_pool import ConnectionPool

# Create pool
pool = ConnectionPool(
    "postgresql://localhost/madf_logs",
    min_size=4,
    max_size=10
)

# Get connection from pool
with pool.connection() as conn:
    conn.execute("INSERT INTO logs ...")
    conn.commit()
# Auto-returned to pool

# Close pool
pool.close()
```

---

## Advanced Features

### 14. Copy Operations

**Purpose**: Fast bulk data loading

**Example**:
```python
# COPY FROM (bulk insert)
with conn.cursor() as cur:
    with cur.copy("COPY logs (level, message) FROM STDIN") as copy:
        copy.write_row(("INFO", "Message 1"))
        copy.write_row(("ERROR", "Message 2"))

# COPY TO (bulk export)
with conn.cursor() as cur:
    with cur.copy("COPY logs TO STDOUT") as copy:
        for row in copy:
            print(row)
```

**Usage Priority**: LOW - Specialized bulk operations

---

### 15. Server-Side Cursors

**Purpose**: Stream large result sets without loading all into memory

**Example**:
```python
with conn.cursor(name="large_query") as cur:
    cur.execute("SELECT * FROM large_table")
    for row in cur:
        process(row)  # Fetches rows in batches from server
```

**Usage Priority**: LOW - Large datasets

---

## Tool Count Summary

**Total psycopg Methods**: 50+ across all classes
**Commonly Used**: 15 methods (80% of use cases)

**Priority Breakdown**:
- **HIGH (8 methods)**: connect(), execute(), cursor(), commit(), rollback(), close(), fetchone(), fetchall()
- **MEDIUM (4 methods)**: executemany(), fetchmany(), ConnectionPool, iteration
- **LOW (3 methods)**: Copy operations, server-side cursors, advanced features

---

## Performance Characteristics

- **Connection**: 10-50ms (local), 50-200ms (remote)
- **Query Execution**: Depends on query complexity
- **Batch Insert** (executemany): 10-100x faster than individual inserts
- **COPY**: Fastest bulk loading (100x+ faster than INSERT)
- **Pool Overhead**: ~1ms connection checkout
- **Memory**: Efficient (streaming via iteration)

---

## Testing Priority

**HIGH Priority** (must test):
1. `connect()` - Database connection
2. `execute()` - Query execution
3. `commit()`, `rollback()` - Transaction management
4. `fetchone()`, `fetchall()` - Result retrieval
5. Parameterized queries (SQL injection protection)

**MEDIUM Priority**:
1. `executemany()` - Batch operations
2. `ConnectionPool` - Connection pooling
3. Cursor iteration - Memory efficiency

**LOW Priority**:
1. COPY operations
2. Server-side cursors
3. Advanced transaction control

---

## Comparison: psycopg vs Postgres MCP Pro vs Direct SQL

| Operation | psycopg | Postgres MCP | Direct SQL | Winner |
|-----------|---------|--------------|------------|--------|
| Execute query | ✓ Native | ✓ MCP bridge | ✓ psql | psycopg (speed) |
| Batch insert | ✓ Fast | ✓ Slower | ✓ Manual | psycopg (executemany) |
| Transaction | ✓ Native | ✓ Limited | ✓ Manual | psycopg (control) |
| Connection pool | ✓ Built-in | ✗ | ✗ | psycopg (only option) |
| Performance | Fast (direct) | Medium (MCP) | Fast (CLI) | psycopg/SQL |
| Type safety | ✓ Python | ✗ | ✗ | psycopg |
| Integration | ✓ Native | ✓ MCP | ✗ | psycopg (Python) |

**psycopg Strengths**:
- Best for Python applications (native integration)
- Connection pooling (production)
- Type safety and IDE autocomplete
- Transaction control
- Batch operations (executemany, COPY)
- Memory efficiency (streaming)

**Postgres MCP Pro Strengths**:
- Best for MCP-based workflows
- Query analysis features
- Optimization suggestions
- Performance insights

**Direct SQL (psql) Strengths**:
- Best for ad-hoc queries
- Interactive exploration
- Administrative tasks
- Debugging

---

## Use Case Recommendations

**Use psycopg when**:
- Building Python applications
- Need connection pooling
- Require transaction control
- Batch operations needed
- LangGraph agent integration
- Production deployment

**Use Postgres MCP when**:
- MCP workflow required
- Need query optimization suggestions
- Want performance analysis
- Non-Python environment

**Use Direct SQL (psql) when**:
- Ad-hoc queries
- Database administration
- Schema exploration
- Debugging

---

## LangGraph Integration Pattern

**Story 1.4**: psycopg for logging infrastructure

```python
import psycopg
from psycopg_pool import ConnectionPool

class LoggingAgent:
    def __init__(self):
        self.pool = ConnectionPool(
            "postgresql://localhost/madf_logs",
            min_size=4,
            max_size=10
        )

    def log_event(self, level: str, message: str, metadata: dict = None):
        """Log agent event to PostgreSQL"""
        with self.pool.connection() as conn:
            conn.execute(
                """
                INSERT INTO agent_logs (level, message, metadata, timestamp)
                VALUES (%s, %s, %s, NOW())
                """,
                (level, message, metadata)
            )
            conn.commit()

    def get_recent_logs(self, limit: int = 100):
        """Retrieve recent logs"""
        with self.pool.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM agent_logs ORDER BY timestamp DESC LIMIT %s",
                (limit,)
            ).fetchall()
            return rows

    def analyze_errors(self):
        """Analyze error patterns"""
        with self.pool.connection() as conn:
            result = conn.execute(
                """
                SELECT message, COUNT(*) as count
                FROM agent_logs
                WHERE level = 'ERROR'
                GROUP BY message
                ORDER BY count DESC
                LIMIT 10
                """
            ).fetchall()
            return result

    def close(self):
        """Close connection pool"""
        self.pool.close()
```

---

## Best Practices

1. **Use context managers**: Auto-closes connections/cursors
2. **Use connection pooling**: For concurrent access
3. **Always parameterize queries**: Prevent SQL injection
4. **Commit explicitly**: Don't rely on auto-commit
5. **Handle transactions**: Use try/except with rollback
6. **Use executemany() for batches**: 10-100x faster
7. **Iterate cursors for large results**: Memory efficient
8. **Use COPY for bulk loading**: Fastest option
9. **Set appropriate pool size**: min_size = CPU cores, max_size = 2-3x
10. **Close pools on shutdown**: Free resources

---

## Error Handling

```python
import psycopg
from psycopg import OperationalError, IntegrityError

try:
    conn = psycopg.connect("postgresql://localhost/madf_logs")
    conn.execute("INSERT INTO logs (level, message) VALUES (%s, %s)", ("INFO", "Test"))
    conn.commit()
except OperationalError as e:
    print(f"Connection error: {e}")
except IntegrityError as e:
    print(f"Constraint violation: {e}")
    conn.rollback()
except Exception as e:
    print(f"Unexpected error: {e}")
    conn.rollback()
finally:
    conn.close()
```

---

## SQL Injection Protection

**ALWAYS use parameterized queries**:

```python
# BAD - SQL injection vulnerable
level = user_input
conn.execute(f"SELECT * FROM logs WHERE level = '{level}'")

# GOOD - parameterized (safe)
conn.execute("SELECT * FROM logs WHERE level = %s", (level,))

# GOOD - named parameters (safe)
conn.execute(
    "SELECT * FROM logs WHERE level = %(level)s",
    {"level": level}
)
```

---

## Transaction Isolation

```python
# Set isolation level
with psycopg.connect(...) as conn:
    conn.isolation_level = psycopg.IsolationLevel.SERIALIZABLE
    conn.execute("SELECT * FROM logs")
    conn.commit()
```

---

## Async Support

**psycopg 3 has full async support**:

```python
import asyncio
from psycopg import AsyncConnection

async def async_query():
    async with await AsyncConnection.connect("postgresql://...") as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM logs")
            rows = await cur.fetchall()
            return rows

asyncio.run(async_query())
```

**Usage Priority**: MEDIUM - Async applications

---

## MADF Configuration

**Connection String** (from Story 1.4):
```python
POSTGRES_CONNECTION_STRING = "postgresql://madf:password@localhost:5433/madf_logs"

# Usage
conn = psycopg.connect(POSTGRES_CONNECTION_STRING)
```

**Schema Example**:
```sql
CREATE TABLE agent_logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(10) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    agent_name VARCHAR(50),
    story_id VARCHAR(20)
);

CREATE INDEX idx_logs_timestamp ON agent_logs(timestamp DESC);
CREATE INDEX idx_logs_level ON agent_logs(level);
CREATE INDEX idx_logs_story_id ON agent_logs(story_id);
```
