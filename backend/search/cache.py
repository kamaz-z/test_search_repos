import json
import logging

import redis
from django.conf import settings

logger = logging.getLogger(__name__)

# Клієнт створюємо один раз і перевикористовуємо
_redis_client = None


def get_redis_client():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(settings.REDIS_URL)
    return _redis_client


def normalize_query(query):
    return " ".join(query.split()).lower()


def build_cache_key(search_type, query, page):
    return (f"{settings.CACHE_KEY_PREFIX}:search:{search_type}:{normalize_query(query)}"
            f"{normalize_query(query)}:page:{page}")


def get_cached_search(search_type, query, page):
    """Повертає збережений результат або None, якщо його немає."""
    key = build_cache_key(search_type, query, page)
    try:
        raw_value = get_redis_client().get(key)
    except redis.RedisError:
        logger.exception("Не вдалося прочитати кеш для ключа %s", key)
        return None

    if raw_value is None:
        return None
    return json.loads(raw_value)


def set_cached_search(search_type, query, data, page):
    """Зберігає нормалізований результат з TTL."""
    key = build_cache_key(search_type, query, page)
    try:
        get_redis_client().set(
            key,
            json.dumps(data, ensure_ascii=False),
            ex=settings.CACHE_TTL_SECONDS,
        )
    except redis.RedisError:
        logger.exception("Не вдалося записати кеш для ключа %s", key)


def clear_app_cache():
    client = get_redis_client()
    pattern = f"{settings.CACHE_KEY_PREFIX}:*"

    # scan_iter не блокує Redis, на відміну від KEYS
    keys = list(client.scan_iter(match=pattern, count=100))
    if keys:
        client.delete(*keys)
    return len(keys)