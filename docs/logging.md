# Logging System Documentation

## Overview

The Chat with OpenAPI application uses a flexible, configurable logging system that supports multiple output formats, destinations, and log levels. The system is designed to be both developer-friendly and production-ready, with support for structured logging and performance tracking.

## Configuration

The logging system is configured through environment variables:

```env
# Logging Settings
LOG_LEVEL=INFO     # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=text    # text, json
LOG_OUTPUT=stdout  # stdout, file
LOG_FILE_PATH=/var/log/app.log  # Required if LOG_OUTPUT=file
```

### Log Levels

- `DEBUG`: Detailed information for debugging
- `INFO`: General operational information
- `WARNING`: Warning messages for potentially problematic situations
- `ERROR`: Error messages for failures that don't halt the application
- `CRITICAL`: Critical errors that may lead to application failure

### Output Formats

#### Text Format
Default human-readable format:
```
2024-01-01 12:00:00,000 - chat-openapi - INFO - Application starting up
```

#### JSON Format
Structured format for machine processing:
```json
{
    "timestamp": "2024-01-01 12:00:00,000",
    "level": "INFO",
    "message": "Application starting up",
    "module": "main",
    "function": "startup_event",
    "extra": {
        "log_level": "INFO",
        "log_format": "json",
        "log_output": "stdout"
    }
}
```

### Output Destinations

- `stdout`: Logs to standard output (default)
- `file`: Logs to the specified file path

## Usage

### Basic Logging

```python
from app.core.logging import logger

# Different log levels
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")

# Adding extra context
logger.info("User action", extra={
    "user_id": "123",
    "action": "upload",
    "file_size": 1024
})

# Logging exceptions
try:
    raise ValueError("Something went wrong")
except Exception as e:
    logger.exception("Error processing request")
```

### Context Manager

Use the `log_context` context manager to automatically log operation duration and handle exceptions:

```python
from app.core.utils import log_context

with log_context("file_processing"):
    # Your code here
    process_file()

# Output:
# DEBUG - Starting: file_processing
# DEBUG - Completed: file_processing - duration_seconds: 0.123
```

### Function Decorator

Use the `log_function` decorator to automatically log function entry, exit, and duration:

```python
from app.core.utils import log_function

@log_function
def process_data(data_id: str):
    # Your code here
    pass

# Output:
# DEBUG - Starting: app.module.process_data
# DEBUG - Completed: app.module.process_data - duration_seconds: 0.456
```

## Best Practices

1. **Log Levels**
   - Use `DEBUG` for detailed troubleshooting
   - Use `INFO` for general operational events
   - Use `WARNING` for unexpected but handled situations
   - Use `ERROR` for failures that need attention
   - Use `CRITICAL` for severe failures

2. **Context**
   - Always include relevant context in extra fields
   - Use structured data when possible
   - Include operation duration for performance tracking

3. **Security**
   - Never log sensitive information (passwords, tokens)
   - Mask or truncate potentially sensitive data
   - Be careful with exception details in production

4. **Performance**
   - Use `debug` level judiciously
   - Avoid logging large objects
   - Consider log rotation for file output

## Example Log Outputs

### Application Startup
```json
{
    "timestamp": "2024-01-01 12:00:00,000",
    "level": "INFO",
    "message": "Application starting up",
    "module": "main",
    "function": "startup_event"
}
```

### Request Processing
```json
{
    "timestamp": "2024-01-01 12:00:01,000",
    "level": "INFO",
    "message": "Processing OpenAPI spec",
    "module": "processor",
    "function": "process_spec",
    "extra": {
        "file_name": "api.yaml",
        "file_size": 1024,
        "duration_seconds": 0.789
    }
}
```

### Error Handling
```json
{
    "timestamp": "2024-01-01 12:00:02,000",
    "level": "ERROR",
    "message": "Failed to process OpenAPI spec",
    "module": "processor",
    "function": "process_spec",
    "exception": "ValueError: Invalid YAML format at line 10",
    "extra": {
        "file_name": "api.yaml",
        "error_line": 10
    }
}
```

## Integration Points

The logging system is integrated with:

1. **FastAPI Application**
   - Startup/shutdown events
   - Request/response cycle
   - Exception handling

2. **OpenAPI Processing**
   - File upload events
   - Processing stages
   - Validation results

3. **Vector Database Operations**
   - Query performance
   - Storage operations
   - Index updates

4. **LLM Integration**
   - API calls
   - Response times
   - Token usage

## Monitoring and Analysis

The JSON log format enables easy integration with log aggregation and analysis tools:

- **ELK Stack**: Elasticsearch, Logstash, Kibana
- **Grafana Loki**: Log aggregation
- **Datadog**: APM and log management
- **CloudWatch**: AWS log management

## Future Enhancements

1. Log rotation configuration
2. Structured logging schema validation
3. Custom log formatters for specific use cases
4. Performance metric aggregation
5. Real-time log streaming for development
