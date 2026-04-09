"""
CineStats — Rate Limiter
Per-domain token-bucket queue singleton.
Section 19 of the v1.0 specification.

Each source (Jikan, AniList, TMDB, TVMaze, BOM, Sacnilk, Wikipedia) has its
own independent queue.  Sources are throttled independently — a slow Jikan
queue does NOT block TMDB requests.
"""
import time
import threading
from collections import defaultdict
from typing import Optional


class _TokenBucket:
    """Simple token-bucket rate limiter."""

    def __init__(self, max_tokens: int, refill_period_s: float):
        self.max_tokens = max_tokens
        self.refill_period = refill_period_s
        self.tokens = max_tokens
        self.last_refill = time.monotonic()
        self.lock = threading.Lock()

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self.last_refill
        new_tokens = elapsed * (self.max_tokens / self.refill_period)
        self.tokens = min(self.max_tokens, self.tokens + new_tokens)
        self.last_refill = now

    def acquire(self, timeout_s: float = 30.0) -> bool:
        """Wait until a token is available, up to timeout_s seconds.
        Returns True if acquired, False on timeout."""
        deadline = time.monotonic() + timeout_s
        while True:
            with self.lock:
                self._refill()
                if self.tokens >= 1:
                    self.tokens -= 1
                    return True
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            # Sleep a fraction of the refill interval
            time.sleep(min(0.05, remaining))


class _DelayLimiter:
    """Simple delay-based rate limiter (for scrapers: min N seconds between requests)."""

    def __init__(self, min_delay_s: float):
        self.min_delay = min_delay_s
        self.last_request = 0.0
        self.lock = threading.Lock()

    def acquire(self, timeout_s: float = 30.0) -> bool:
        with self.lock:
            now = time.monotonic()
            elapsed = now - self.last_request
            if elapsed < self.min_delay:
                wait = self.min_delay - elapsed
                if wait > timeout_s:
                    return False
                time.sleep(wait)
            self.last_request = time.monotonic()
            return True


class RateLimiter:
    """Singleton rate limiter managing independent per-domain queues."""

    _instance: Optional['RateLimiter'] = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_queues()
            return cls._instance

    def _init_queues(self):
        """Initialise per-domain rate limit queues from rate_limits.py."""
        self._buckets: dict[str, list[_TokenBucket]] = {}
        self._delays: dict[str, _DelayLimiter] = {}

        # Jikan: 3/sec AND 60/min (dual bucket)
        self._buckets["api.jikan.moe"] = [
            _TokenBucket(3, 1),     # 3 req/sec
            _TokenBucket(60, 60),   # 60 req/min
        ]

        # AniList: 90/min
        self._buckets["graphql.anilist.co"] = [
            _TokenBucket(90, 60),
        ]

        # TVMaze: 20/10sec
        self._buckets["api.tvmaze.com"] = [
            _TokenBucket(20, 10),
        ]

        # TMDB: ~40/10sec
        self._buckets["api.themoviedb.org"] = [
            _TokenBucket(40, 10),
        ]

        # Scrapers: delay-based
        self._delays["www.boxofficemojo.com"] = _DelayLimiter(2.0)
        self._delays["www.sacnilk.com"] = _DelayLimiter(2.0)
        self._delays["en.wikipedia.org"] = _DelayLimiter(2.0)

    def wait(self, domain: str, timeout_s: float = 30.0) -> bool:
        """Wait until the domain's rate limit allows a request.

        Args:
            domain: the domain string (e.g. 'api.jikan.moe')
            timeout_s: max seconds to wait

        Returns:
            True if approved, False if timed out.

        Raises:
            FetchException if timeout.
        """
        # Check token buckets first
        if domain in self._buckets:
            for bucket in self._buckets[domain]:
                if not bucket.acquire(timeout_s):
                    return False
            return True

        # Check delay-based limiters
        if domain in self._delays:
            return self._delays[domain].acquire(timeout_s)

        # Unknown domain: no throttling
        return True

    def reset(self):
        """Reset all limiters (useful for testing)."""
        self._init_queues()


class FetchException(Exception):
    """Raised when a data fetch fails (network, parsing, rate limit, etc.)."""
    def __init__(self, source: str, entity_key: str = "", message: str = ""):
        self.source = source
        self.entity_key = entity_key
        super().__init__(f"[{source}] {message}" + (f" (entity: {entity_key})" if entity_key else ""))
