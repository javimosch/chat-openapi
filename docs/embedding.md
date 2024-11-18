# Running Sentence Transformers on CPU

This guide provides recommendations for efficiently running sentence-transformers without GPU acceleration in the Chat-OpenAPI project.

## Model Selection

### Recommended Models

1. **all-MiniLM-L6-v2**
   - Size: ~80MB
   - Performance: Fast, good for general purpose
   - Dimension: 384
   - Best balance of speed and quality for CPU usage

2. **paraphrase-MiniLM-L3-v2**
   - Size: ~60MB
   - Performance: Very fast, slightly lower quality
   - Dimension: 384
   - Ideal for resource-constrained environments

3. **all-MiniLM-L12-v2**
   - Size: ~120MB
   - Performance: Moderate speed, better quality
   - Dimension: 384
   - Use when quality is more important than speed

### Model Comparison

| Model                    | Size  | Speed (CPU) | Quality | Memory Usage |
|-------------------------|-------|-------------|---------|--------------|
| all-MiniLM-L6-v2        | 80MB  | Fast       | Good    | ~200MB       |
| paraphrase-MiniLM-L3-v2 | 60MB  | Very Fast  | Fair    | ~150MB       |
| all-MiniLM-L12-v2       | 120MB | Moderate   | Better  | ~300MB       |

## Optimization Techniques

### 1. Batch Processing

```python
# Recommended batch sizes for different CPU configurations
BATCH_SIZES = {
    'low_end': 16,    # 1-2 cores
    'medium': 32,     # 4 cores
    'high_end': 64    # 8+ cores
}
```

Benefits:
- Reduces memory allocation overhead
- Improves CPU utilization
- More efficient processing of large datasets

### 2. Model Loading Optimization

```python
from sentence_transformers import SentenceTransformer

# Load model with optimized settings
model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
```

Configuration options:
```python
# Environment variables
EMBEDDING_MODEL=all-MiniLM-L6-v2
USE_CUDA=false
BATCH_SIZE=32
MAX_SEQUENCE_LENGTH=128  # Limit sequence length for faster processing
```

### 3. Memory Management

Best practices:
- Clear unused variables
- Use context managers for large operations
- Implement garbage collection when needed
- Monitor memory usage during batch processing

Example implementation:
```python
import gc
from typing import List

def process_large_dataset(texts: List[str], batch_size: int = 32):
    batches = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]
    embeddings = []
    
    for batch in batches:
        batch_embeddings = model.encode(batch)
        embeddings.extend(batch_embeddings)
        
        # Force garbage collection after each batch
        gc.collect()
    
    return embeddings
```

## Performance Monitoring

### Key Metrics to Monitor

1. Processing Speed
   - Embeddings per second
   - Batch processing time
   - Total processing time

2. Memory Usage
   - Peak memory consumption
   - Memory usage per batch
   - Memory leaks

3. CPU Utilization
   - Core usage
   - Processing bottlenecks
   - Thread distribution

Example monitoring setup:
```python
import time
import psutil
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        print(f"Processing time: {end_time - start_time:.2f} seconds")
        print(f"Memory usage: {end_memory - start_memory:.2f} MB")
        
        return result
    return wrapper
```

## Troubleshooting

Common issues and solutions:

1. **High Memory Usage**
   - Reduce batch size
   - Implement memory monitoring
   - Clear cache between large operations

2. **Slow Processing**
   - Increase batch size (if memory allows)
   - Reduce maximum sequence length
   - Use a lighter model

3. **Out of Memory Errors**
   - Implement batch processing
   - Use memory-efficient data types
   - Clear unused variables and cache

## Configuration Example

`.env` file configuration:
```bash
# Model Settings
EMBEDDING_MODEL=all-MiniLM-L6-v2
USE_CUDA=false
BATCH_SIZE=32
MAX_SEQUENCE_LENGTH=128

# Performance Monitoring
ENABLE_PERFORMANCE_MONITORING=true
MEMORY_THRESHOLD_MB=1000
```

## Best Practices

1. **Development Environment**
   - Test with representative data volumes
   - Monitor memory usage during development
   - Profile code for bottlenecks

2. **Production Environment**
   - Set appropriate batch sizes
   - Implement error handling
   - Monitor system resources
   - Log performance metrics

3. **Maintenance**
   - Regularly update sentence-transformers
   - Monitor for memory leaks
   - Adjust configurations based on usage patterns
