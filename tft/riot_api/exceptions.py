class RiotAPIError(Exception):
    """Raised for any non-2xx response from the Riot API."""

    def __init__(self, status_code: int, message: str, url: str):
        self.status_code = status_code
        self.url = url
        super().__init__(f"Riot API error {status_code} for {url}: {message}")


class RateLimitError(RiotAPIError):
    """Raised on HTTP 429, after retries (if any) are exhausted."""

    def __init__(self, message: str, url: str, retry_after: float | None):
        self.retry_after = retry_after
        super().__init__(429, message, url)
