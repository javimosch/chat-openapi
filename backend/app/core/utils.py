import functools
import time
from typing import Callable, TypeVar, ParamSpec
from contextlib import contextmanager

from .logging import logger

P = ParamSpec("P")
T = TypeVar("T")

@contextmanager
def log_context(context: str):
    """Context manager for adding context to logs"""
    start_time = time.time()
    logger.debug(f"Starting: {context}")
    try:
        yield
    except Exception as e:
        logger.exception(f"Error in {context}: {str(e)}")
        raise
    finally:
        duration = time.time() - start_time
        logger.debug(
            f"Completed: {context}",
            extra={"duration_seconds": duration}
        )

def log_function(func: Callable[P, T]) -> Callable[P, T]:
    """Decorator to log function entry, exit, and duration"""
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        with log_context(f"{func.__module__}.{func.__name__}"):
            return func(*args, **kwargs)
    return wrapper
