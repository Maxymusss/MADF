# 16. Error Handling Strategy

## Error Response Format
```python
class ApiError(BaseModel):
    error: Dict[str, Any] = {
        "code": str,          # Error code
        "message": str,       # Human-readable message
        "details": dict,      # Additional context
        "timestamp": str,     # ISO timestamp
        "agent_id": str,      # Agent that errored
        "correlation_id": str # Related task ID
    }
```
