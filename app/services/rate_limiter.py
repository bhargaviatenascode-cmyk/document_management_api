from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone


class SimpleRateLimiter:
    def __init__(self, limit: int, window_seconds: int = 60):
        self.limit = limit
        self.window = timedelta(seconds=window_seconds)
        self.hits = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = datetime.now(timezone.utc)
        q = self.hits[key]
        while q and (now - q[0]) > self.window:
            q.popleft()
        if len(q) >= self.limit:
            return False
        q.append(now)
        return True
