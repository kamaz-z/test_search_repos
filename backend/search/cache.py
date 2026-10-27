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
            f":page:{page}")


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
#_________________HISTORY

def save_search_query(search_type: str,query: str,user_id: int,) -> None:
    redis_client = get_redis_client()
    key = f"search:history:user:{user_id}"

    history_item = json.dumps(
        {"query": query, "type": search_type},
        ensure_ascii=False,
        sort_keys=True,
    )

    for existing_item in redis_client.lrange(key, 0, -1):
        if _deserialize_history_item(existing_item) == {
            "query": query,
            "type": search_type,
        }:
            redis_client.lrem(key, 0, existing_item)

    redis_client.lpush(key, history_item)
    redis_client.ltrim(key, 0, 9)

def _deserialize_history_item(raw_item) -> dict[str, str] | None:
    if isinstance(raw_item, bytes):
        raw_item = raw_item.decode("utf-8")
    try:
        item = json.loads(raw_item)
    except json.JSONDecodeError:
        item = None

    if isinstance(item, dict):
        query = item.get("query")
        search_type = item.get("type")
        if isinstance(query, str) and search_type in {"repositories", "users"}:
            return {"query": query, "type": search_type}
        logger.warning("Пропускаємо некоректний запис історії пошуку")
        return None

    if isinstance(raw_item, str) and raw_item:
        return {"query": raw_item, "type": "repositories"}
    return None


def get_search_history(user_id: int) -> list[dict[str, str]]:
    redis_client = get_redis_client()
    key = f"search:history:user:{user_id}"

    history = []

    for raw_item in redis_client.lrange(key, 0, 9):
        item = _deserialize_history_item(raw_item)
        if item is not None:
            history.append(item)

    return history