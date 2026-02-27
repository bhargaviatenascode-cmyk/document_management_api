import json
import logging
from typing import Any

import redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self):
        settings = get_settings()
        self._memory: dict[str, Any] = {}
        try:
            self.client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
            self.client.ping()
        except Exception as exc:
            logger.warning("Redis unavailable, falling back to in-memory cache: %s", exc)
            self.client = None

    def get(self, key: str):
        if self.client:
            value = self.client.get(key)
            return json.loads(value) if value else None
        return self._memory.get(key)

    def set(self, key: str, value: Any, ttl: int = 300):
        if self.client:
            self.client.setex(key, ttl, json.dumps(value, default=str))
            return
        self._memory[key] = value

    def delete(self, key: str):
        if self.client:
            self.client.delete(key)
            return
        self._memory.pop(key, None)
