"""A small token-bucket limiter so a single misbehaving loop can't hammer
Riot's API and get the key throttled or revoked."""

from __future__ import annotations

import threading
import time


class TokenBucketLimiter:
    def __init__(self, max_tokens: int, refill_seconds: float):
        self._max_tokens = max_tokens
        self._refill_seconds = refill_seconds
        self._tokens = float(max_tokens)
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._last_refill = now
        self._tokens = min(self._max_tokens, self._tokens + elapsed * (self._max_tokens / self._refill_seconds))

    def acquire(self) -> None:
        while True:
            with self._lock:
                self._refill()
                if self._tokens >= 1:
                    self._tokens -= 1
                    return
                deficit = 1 - self._tokens
                wait = deficit / (self._max_tokens / self._refill_seconds)
            time.sleep(max(wait, 0.01))
