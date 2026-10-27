from fnmatch import fnmatch

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from search.services import GitHubRateLimitError, GitHubTimeoutError


class FakeRedis:
    """Імітує частину методів redis.Redis, яку використовує cache.py."""

    def __init__(self):
        self.storage = {}
        self.ttl = {}
        self.lists = {}

    def get(self, key):
        return self.storage.get(key)

    def set(self, key, value, ex=None):
        self.storage[key] = value
        self.ttl[key] = ex

    def scan_iter(self, match=None, count=None):
        for key in list(self.storage):
            if match is None or fnmatch(key, match):
                yield key

    def delete(self, *keys):
        for key in keys:
            self.storage.pop(key, None)
            self.ttl.pop(key, None)

    def lrange(self, key, start, end):
        values = self.lists.get(key, [])
        return values[start:] if end == -1 else values[start : end + 1]

    def lrem(self, key, count, value):
        values = self.lists.get(key, [])
        self.lists[key] = [item for item in values if item != value]

    def lpush(self, key, value):
        self.lists.setdefault(key, []).insert(0, value)

    def ltrim(self, key, start, end):
        self.lists[key] = self.lrange(key, start, end)


RAW_GITHUB_RESPONSE = {
    "total_count": 1,
    "items": [
        {
            "id": 1,
            "name": "django",
            "full_name": "django/django",
            "html_url": "https://github.com/django/django",
            "description": "Web framework",
            "stargazers_count": 10,
            "forks_count": 2,
            "language": "Python",
            "owner": {"login": "django"},
        }
    ],
}


@pytest.fixture
def api_client(db):
    user = get_user_model().objects.create_user(
        username="user", password="password"
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def unauthenticated_api_client():
    return APIClient()


@pytest.fixture
def staff_api_client(db):
    user = get_user_model().objects.create_user(
        username="admin", password="password", is_staff=True
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def fake_redis(monkeypatch):
    redis_stub = FakeRedis()
    monkeypatch.setattr("search.cache.get_redis_client", lambda: redis_stub)
    return redis_stub


@pytest.fixture
def github_calls(monkeypatch):
    """Рахує, скільки разів view справді ходив до GitHub."""
    calls = []

    def fake_search(search_type, query):
        calls.append((search_type, query))
        if search_type == "users":
            return {"total_count": 0, "items": []}
        return RAW_GITHUB_RESPONSE

    monkeypatch.setattr("search.views.search_github", fake_search)
    return calls


def post_search(api_client, search_type="repositories", query="django"):
    return api_client.post(
        "/api/search/", {"type": search_type, "query": query}, format="json"
    )


def test_login_returns_token_and_role_for_regular_user(db):
    user = get_user_model().objects.create_user(
        username="regular", password="password"
    )

    response = APIClient().post(
        "/api/auth/login",
        {"username": user.username, "password": "password"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["token"]
    assert response.data["username"] == user.username
    assert response.data["is_staff"] is False


# --- Пошук і кеш ---

def test_first_request_is_miss_second_is_hit(api_client, fake_redis, github_calls):
    first = post_search(api_client)
    second = post_search(api_client)

    assert first.status_code == 200
    assert first.data["cached"] is False
    assert second.data["cached"] is True
    assert len(github_calls) == 1


def test_equivalent_queries_share_one_cache_key(api_client, fake_redis, github_calls):
    post_search(api_client, query="  DJANGO  ")
    response = post_search(api_client, query="django")

    assert response.data["cached"] is True
    assert len(github_calls) == 1


def test_different_search_types_use_separate_keys(api_client, fake_redis, github_calls):
    post_search(api_client, search_type="repositories")
    response = post_search(api_client, search_type="users")

    assert response.data["cached"] is False
    assert len(github_calls) == 2


def test_search_history_includes_query_and_type_even_for_cached_search(
    api_client, fake_redis, github_calls
):
    post_search(api_client, search_type="repositories", query="django")
    post_search(api_client, search_type="users", query="django")
    post_search(api_client, search_type="repositories", query="django")

    response = api_client.get("/api/history/")

    assert response.status_code == 200
    assert len(github_calls) == 2
    assert response.data["history"] == [
        {"query": "django", "type": "repositories"},
        {"query": "django", "type": "users"},
    ]


def test_search_history_supports_legacy_queries(fake_redis):
    fake_redis.lists["search:history"] = ["django"]

    from search.cache import get_search_history

    assert get_search_history() == [
        {"query": "django", "type": "repositories"}
    ]


def test_cache_entry_gets_configured_ttl(api_client, fake_redis, github_calls, settings):
    settings.CACHE_TTL_SECONDS = 7200
    post_search(api_client)

    assert fake_redis.ttl["gsa:search:repositories:django:page:1"] == 7200


@pytest.mark.parametrize(
    "error, expected_status",
    [
        (GitHubTimeoutError("timeout"), 504),
        (GitHubRateLimitError("limit"), 429),
    ],
)
def test_github_errors_are_returned_and_not_cached(
    api_client, fake_redis, monkeypatch, error, expected_status
):
    def failing_search(search_type, query):
        raise error

    monkeypatch.setattr("search.views.search_github", failing_search)

    response = post_search(api_client)

    assert response.status_code == expected_status
    assert fake_redis.storage == {}


# --- Валідація ---

def test_invalid_type_returns_400(api_client, fake_redis, github_calls):
    response = post_search(api_client, search_type="bad")

    assert response.status_code == 400
    assert github_calls == []


def test_too_short_query_returns_400(api_client, fake_redis, github_calls):
    response = post_search(api_client, query="ab")

    assert response.status_code == 400
    assert github_calls == []


# --- Очищення кешу ---

def test_clear_cache_without_token_is_unauthorized(
    unauthenticated_api_client, fake_redis
):
    response = unauthenticated_api_client.post("/api/clear-cache/")

    assert response.status_code == 401


def test_non_staff_user_cannot_clear_cache(api_client, fake_redis):
    response = api_client.post("/api/clear-cache/")

    assert response.status_code == 403


def test_staff_user_can_clear_only_app_keys(staff_api_client, fake_redis):
    fake_redis.storage = {
        "gsa:search:repositories:django": "{}",
        "other_service:key": "keep me",
    }

    response = staff_api_client.post("/api/clear-cache/")

    assert response.status_code == 200
    assert response.data["deleted_keys"] == 1
    assert "other_service:key" in fake_redis.storage
    assert "gsa:search:repositories:django" not in fake_redis.storage