# Coding Criteria and Best Practices

## Core Principles

1. **Simplicity Over Complexity**
   - Prefer simple, readable solutions over complex abstractions
   - Keep code straightforward and maintainable
   - Avoid premature optimization

2. **Code Organization**
   - Maximum file size: 300 lines
   - Split large files into logical, focused modules
   - Group related functionality into dedicated directories

## Library Usage Guidelines

### When to Build vs When to Import

1. **Build It Yourself When**:
   - Implementation requires < 100 lines of code
   - Functionality is specific to our use case
   - No complex edge cases to handle
   - Performance requirements are basic

2. **Use a Library When**:
   - Implementation would exceed 100 lines
   - Dealing with complex protocols or standards
   - Security is a critical concern
   - Performance optimization is crucial
   - The library is a de-facto standard (e.g., FastAPI, Vue)

### Examples for This Project

Build Yourself:
- Simple text chunking utilities
- Basic configuration management
- HTTP response formatters
- Simple validation helpers

Use Library:
- FastAPI (web framework)
- Qdrant (vector database)
- Vue.js (frontend framework)
- OpenRouter API client (security critical)

## Code Organization

### File Structure
```
src/
├── utils/           # Shared utilities
├── services/        # Core business logic
├── models/          # Data models
└── api/             # API endpoints
```

### File Size Rules
1. Maximum 300 lines per file
2. When approaching limit:
   - Extract utilities to `utils/`
   - Split into smaller, focused modules
   - Create new service classes

### Naming Conventions
- Files: lowercase with hyphens (e.g., `text-processor.py`)
- Classes: PascalCase (e.g., `TextProcessor`)
- Functions: snake_case (e.g., `process_text`)
- Constants: UPPERCASE (e.g., `MAX_CHUNK_SIZE`)

## Documentation Guidelines

### When to Document

1. **Always Document**:
   - Complex algorithms
   - Non-obvious business logic
   - Configuration options
   - Public APIs
   - Side effects

2. **Focus on Why, Not What**:
```python
# BAD:
# This function splits the text
def split_text(text):

# GOOD:
# We split text into 1000-char chunks with 200-char overlap
# to maintain context while keeping chunks processable by the LLM
def split_text(text):
```

3. **Document Architecture Decisions**:
   - Create ADR (Architecture Decision Record) for major choices
   - Explain trade-offs and alternatives considered

## Configuration Management

### Environment Variables

1. **Always Use ENV Vars For**:
   - API keys
   - Service URLs
   - Port numbers
   - Feature flags
   - Performance tuning parameters

2. **Configuration Structure**:
```
├── .env.example     # Template with all possible vars
├── .env            # Local development vars (gitignored)
└── config/
    ├── default.py  # Default values
    └── schema.py   # Configuration schema
```

3. **Make It Customizable**:
   - Use sensible defaults
   - Allow override via ENV vars
   - Document all configuration options

### Example Configuration:
```python
# config/schema.py
class AppConfig:
    CHUNK_SIZE: int = Field(
        default=1000,
        description="Size of text chunks for processing"
    )
    CHUNK_OVERLAP: int = Field(
        default=200,
        description="Overlap between consecutive chunks"
    )
```

## Testing Strategy for MVP

1. **No Unit Tests Unless Specified**
   - Focus on core functionality
   - Manual testing of critical paths
   - Document test scenarios

2. **What to Test Manually**:
   - File upload flow
   - Text processing
   - Chat functionality
   - API responses
   - Error handling

3. **Test Documentation**:
   - Create test scenarios document
   - List manual test cases
   - Document known limitations

## Code Review Checklist

- [ ] File is under 300 lines
- [ ] No hardcoded values
- [ ] Complex logic is documented
- [ ] Utilities are extracted
- [ ] Configuration is flexible
- [ ] Error handling is in place
- [ ] No unnecessary dependencies
- [ ] Follows naming conventions

## Refactoring Triggers

1. **When to Refactor**:
   - File exceeds 300 lines
   - Function exceeds 50 lines
   - Duplicate code appears
   - Complex logic is hard to follow

2. **Refactoring Priorities**:
   - Extract shared utilities
   - Split large files
   - Remove duplicate code
   - Simplify complex logic

## Security Practices

1. **Always**:
   - Validate user input
   - Sanitize file uploads
   - Use environment variables for secrets
   - Implement rate limiting
   - Set proper CORS policies

2. **Never**:
   - Hardcode credentials
   - Trust user input
   - Expose internal errors
   - Store secrets in code

## Performance Guidelines

1. **Early Stage**:
   - Focus on clean, maintainable code
   - Avoid premature optimization
   - Use async where it makes sense
   - Monitor basic metrics

2. **Optimize When**:
   - Clear performance bottleneck
   - Measurable user impact
   - Simple solutions don't work
