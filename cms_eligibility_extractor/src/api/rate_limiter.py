"""
Rate limiter for CMS API requests with exponential backoff.
Handles 429 responses and implements smart retry logic.
"""

import time
import asyncio
import logging
from typing import Optional, Callable, Any
from dataclasses import dataclass
from threading import Lock
import random


logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_second: float = 2.0
    burst_requests: int = 5
    retry_delay: float = 1.0
    max_retry_delay: float = 8.0
    backoff_factor: float = 2.0
    max_retries: int = 3
    jitter: bool = True  # Add random jitter to prevent thundering herd


class RateLimiter:
    """
    Token bucket rate limiter with exponential backoff for 429 responses.
    Thread-safe implementation for concurrent requests.
    """
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.tokens = config.burst_requests
        self.last_refill = time.time()
        self.lock = Lock()
        
        # Statistics tracking
        self.total_requests = 0
        self.rate_limited_requests = 0
        self.total_wait_time = 0.0
        
    def acquire(self, timeout: Optional[float] = None) -> bool:
        """
        Acquire a token for making a request.
        
        Args:
            timeout: Maximum time to wait for a token (None = wait forever)
            
        Returns:
            True if token acquired, False if timeout exceeded
        """
        start_time = time.time()
        
        while True:
            with self.lock:
                self._refill_tokens()
                
                if self.tokens >= 1:
                    self.tokens -= 1
                    self.total_requests += 1
                    return True
                
                # Calculate wait time until next token
                time_until_token = 1.0 / self.config.requests_per_second
                
            # Check timeout
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed + time_until_token > timeout:
                    return False
                    
            # Wait for next token
            self.total_wait_time += time_until_token
            time.sleep(time_until_token)
    
    def _refill_tokens(self):
        """Refill tokens based on elapsed time (called with lock held)."""
        now = time.time()
        time_passed = now - self.last_refill
        
        # Add tokens based on rate
        tokens_to_add = time_passed * self.config.requests_per_second
        self.tokens = min(self.config.burst_requests, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics."""
        with self.lock:
            return {
                'total_requests': self.total_requests,
                'rate_limited_requests': self.rate_limited_requests,
                'total_wait_time': self.total_wait_time,
                'current_tokens': self.tokens,
                'requests_per_second': self.config.requests_per_second
            }


class ExponentialBackoff:
    """
    Exponential backoff handler for 429 responses and other retryable errors.
    """
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        
    def calculate_delay(self, attempt: int, base_delay: Optional[float] = None) -> float:
        """
        Calculate delay for retry attempt.
        
        Args:
            attempt: Retry attempt number (0-based)
            base_delay: Base delay override (uses config default if None)
            
        Returns:
            Delay in seconds
        """
        if base_delay is None:
            base_delay = self.config.retry_delay
            
        # Exponential backoff: delay = base_delay * (backoff_factor ^ attempt)
        delay = base_delay * (self.config.backoff_factor ** attempt)
        delay = min(delay, self.config.max_retry_delay)
        
        # Add jitter to prevent thundering herd
        if self.config.jitter:
            jitter_range = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_range, jitter_range)
            
        return max(0, delay)
    
    def should_retry(self, attempt: int, status_code: Optional[int] = None, 
                    exception: Optional[Exception] = None) -> bool:
        """
        Determine if request should be retried.
        
        Args:
            attempt: Current attempt number (0-based)
            status_code: HTTP status code (if available)
            exception: Exception that occurred (if any)
            
        Returns:
            True if should retry, False otherwise
        """
        if attempt >= self.config.max_retries:
            return False
            
        # Retry on 429 (rate limited)
        if status_code == 429:
            return True
            
        # Retry on 5xx server errors
        if status_code and 500 <= status_code < 600:
            return True
            
        # Retry on connection errors
        if exception and isinstance(exception, (
            ConnectionError, 
            TimeoutError,
            OSError
        )):
            return True
            
        return False


def with_rate_limit_and_retry(rate_limiter: RateLimiter, 
                             backoff: ExponentialBackoff):
    """
    Decorator that adds rate limiting and retry logic to API calls.
    
    Args:
        rate_limiter: Rate limiter instance
        backoff: Exponential backoff handler
        
    Returns:
        Decorated function with rate limiting and retry logic
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            attempt = 0
            last_exception = None
            
            while attempt <= backoff.config.max_retries:
                # Acquire rate limit token
                if not rate_limiter.acquire(timeout=30.0):  # 30 second timeout
                    raise TimeoutError("Rate limiter timeout - could not acquire token")
                
                try:
                    result = func(*args, **kwargs)
                    
                    # If we get a result, check if it indicates rate limiting
                    if hasattr(result, 'status_code'):
                        status_code = result.status_code
                        
                        if status_code == 429:
                            rate_limiter.rate_limited_requests += 1
                            
                            if backoff.should_retry(attempt, status_code):
                                delay = backoff.calculate_delay(attempt)
                                logger.warning(
                                    f"Rate limited (429), retrying in {delay:.2f}s "
                                    f"(attempt {attempt + 1}/{backoff.config.max_retries + 1})"
                                )
                                time.sleep(delay)
                                attempt += 1
                                continue
                            else:
                                logger.error(f"Rate limited and max retries exceeded")
                                return result
                        
                        # Success or non-retryable error
                        return result
                    
                    # Function returned without status code, assume success
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    if backoff.should_retry(attempt, exception=e):
                        delay = backoff.calculate_delay(attempt)
                        logger.warning(
                            f"Request failed with {type(e).__name__}: {e}, "
                            f"retrying in {delay:.2f}s "
                            f"(attempt {attempt + 1}/{backoff.config.max_retries + 1})"
                        )
                        time.sleep(delay)
                        attempt += 1
                        continue
                    else:
                        logger.error(f"Request failed and not retryable: {e}")
                        raise e
            
            # Max retries exceeded
            if last_exception:
                logger.error(f"Max retries exceeded, last error: {last_exception}")
                raise last_exception
            else:
                raise RuntimeError("Max retries exceeded")
                
        return wrapper
    return decorator


class AsyncRateLimiter:
    """
    Async version of rate limiter for future async implementations.
    """
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.tokens = config.burst_requests
        self.last_refill = time.time()
        self.lock = asyncio.Lock()
        
    async def acquire(self, timeout: Optional[float] = None) -> bool:
        """Async version of token acquisition."""
        start_time = time.time()
        
        while True:
            async with self.lock:
                self._refill_tokens()
                
                if self.tokens >= 1:
                    self.tokens -= 1
                    return True
                    
                time_until_token = 1.0 / self.config.requests_per_second
                
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed + time_until_token > timeout:
                    return False
                    
            await asyncio.sleep(time_until_token)
    
    def _refill_tokens(self):
        """Refill tokens (same logic as sync version)."""
        now = time.time()
        time_passed = now - self.last_refill
        tokens_to_add = time_passed * self.config.requests_per_second
        self.tokens = min(self.config.burst_requests, self.tokens + tokens_to_add)
        self.last_refill = now