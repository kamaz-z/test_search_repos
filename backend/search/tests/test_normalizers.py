from search.normalizers import (
    normalize_issue,
    normalize_repository,
    normalize_search_response,
    normalize_user,
)


# Скорочений приклад того, що повертає GitHub. Реальний об'єкт має набагато більше полів.
RAW_REPOSITORY = {
    "id": 27193779,
    "name": "django",
    "full_name": "django/django",
    "html_url": "https://github.com/django/django",
    "description": "The Web framework for perfectionists with deadlines.",
    "stargazers_count": 80000,
    "forks_count": 32000,
    "language": "Python",
    "owner": {"login": "django", "id": 27804, "type": "Organization"},
    # Поле, яке ми не маємо брати в результат
    "topics": ["python", "web"],
}

RAW_USER = {
    "id": 1,
    "login": "mojombo",
    "avatar_url": "https://avatars.githubusercontent.com/u/1?v=4",
    "html_url": "https://github.com/mojombo",
    "score": 1.0,
}

RAW_ISSUE = {
    "id": 999,
    "title": "Fix bug",
    "html_url": "https://github.com/django/django/issues/999",
    "state": "open",
    "user": {"login": "someone"},
    "comments": 3,
    "created_at": "2026-10-01T12:00:00Z",
}


def test_normalize_user_keeps_only_needed_fields():
    result = normalize_user(RAW_USER)

    assert result == {
        "id": 1,
        "login": "mojombo",
        "avatar_url": "https://avatars.githubusercontent.com/u/1?v=4",
        "html_url": "https://github.com/mojombo",
    }
    assert "score" not in result


def test_normalize_repository_renames_fields():
    result = normalize_repository(RAW_REPOSITORY)

    assert result["stars"] == 80000
    assert result["forks"] == 32000
    assert result["owner_login"] == "django"
    assert result["language"] == "Python"
    assert "stargazers_count" not in result
    assert "topics" not in result


def test_normalize_repository_handles_null_owner_and_description():
    raw = {**RAW_REPOSITORY, "owner": None, "description": None, "language": None}

    result = normalize_repository(raw)

    assert result["owner_login"] == ""
    assert result["description"] is None
    assert result["language"] is None


def test_normalize_issue_handles_missing_user():
    raw = {**RAW_ISSUE, "user": None}

    result = normalize_issue(raw)

    assert result["author_login"] is None


def test_normalize_search_response_for_repositories():
    raw_response = {"total_count": 1, "incomplete_results": False, "items": [RAW_REPOSITORY]}

    result = normalize_search_response("repositories", raw_response)

    assert result["total_count"] == 1
    assert len(result["items"]) == 1
    assert result["items"][0]["full_name"] == "django/django"


def test_normalize_search_response_empty_items():
    result = normalize_search_response("users", {"total_count": 0, "items": []})

    assert result == {"total_count": 0, "items": []}


def test_normalize_search_response_missing_items_key():
    result = normalize_search_response("users", {})

    assert result == {"total_count": 0, "items": []}