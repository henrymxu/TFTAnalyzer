import time

from tft.riot_api.rate_limiter import TokenBucketLimiter


def test_allows_burst_up_to_max_tokens_immediately():
    limiter = TokenBucketLimiter(max_tokens=5, refill_seconds=10)
    start = time.monotonic()
    for _ in range(5):
        limiter.acquire()
    assert time.monotonic() - start < 0.2


def test_blocks_once_bucket_is_exhausted():
    limiter = TokenBucketLimiter(max_tokens=1, refill_seconds=0.2)
    limiter.acquire()  # drains the single token
    start = time.monotonic()
    limiter.acquire()  # must wait for a partial refill
    assert time.monotonic() - start >= 0.1
