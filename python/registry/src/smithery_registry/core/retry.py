"""Retry configuration and implementation."""

import asyncio
import random
from dataclasses import dataclass
from typing import List, Optional, Callable, TypeVar, Awaitable
from enum import Enum


class RetryStrategy(str, Enum):
    """Retry strategy types."""
    
    NONE = "none"
    BACKOFF = "backoff"
    FIXED = "fixed"


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    
    strategy: RetryStrategy = RetryStrategy.BACKOFF
    max_attempts: int = 3
    initial_interval: float = 0.5
    max_interval: float = 60.0
    exponent: float = 1.5
    max_elapsed_time: float = 3600.0
    retry_codes: List[str] = None
    retry_connection_errors: bool = True
    
    def __post_init__(self):
        if self.retry_codes is None:
            self.retry_codes = ["5XX", "429"]


T = TypeVar("T")


class RetryHandler:
    """Handles retry logic with exponential backoff."""
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    async def execute_with_retry(
        self,
        func: Callable[[], Awaitable[T]],
        should_retry: Callable[[Exception], bool]
    ) -> T:
        """Execute a function with retry logic."""
        if self.config.strategy == RetryStrategy.NONE:
            return await func()
        
        attempt = 0
        start_time = asyncio.get_event_loop().time()
        
        while attempt < self.config.max_attempts:
            try:
                return await func()
            except Exception as e:
                if not should_retry(e):
                    raise
                
                attempt += 1
                if attempt >= self.config.max_attempts:
                    raise
                
                # Calculate delay based on strategy
                if self.config.strategy == RetryStrategy.FIXED:
                    delay = self.config.initial_interval
                else:  # BACKOFF
                    delay = min(
                        self.config.initial_interval * (self.config.exponent ** attempt),
                        self.config.max_interval
                    )
                    # Add jitter
                    delay *= (0.5 + random.random())
                
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed + delay > self.config.max_elapsed_time:
                    raise
                
                await asyncio.sleep(delay)
        
        raise RuntimeError("Retry loop failed unexpectedly")