"""Redis and RQ connection. Optional: if REDIS_URL not set, job endpoints use sync fallback."""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from redis import Redis
    from rq import Queue

_redis: "Redis | None" = None
_queue: "Queue | None" = None


def get_redis_url() -> str:
    return os.environ.get("REDIS_URL", "redis://localhost:6379/0")


def get_redis():
    global _redis
    if _redis is None:
        try:
            import redis
            _redis = redis.from_url(get_redis_url())
            _redis.ping()
        except Exception:
            _redis = None
    return _redis


def get_queue():
    global _queue
    if _queue is None:
        conn = get_redis()
        if conn is None:
            return None
        try:
            from rq import Queue
            _queue = Queue(connection=conn, default_timeout=300)
        except Exception:
            _queue = None
    return _queue


def queue_available() -> bool:
    return get_queue() is not None
