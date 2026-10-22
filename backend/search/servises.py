import requests
from django.conf import settings


GITHUB_API_BASE_URL = "https://api.github.com"

SEARCH_ENDPOINTS = {
    "users": "/search/users",
    "repositories": "/search/repositories",
    "issues": "/search/issues",
}

RESULTS_PER_PAGE = 10


class GitHubAPIError(Exception):
    """Будь-яка помилка GitHub API, яку ми не змогли обробити інакше."""

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


class GitHubRateLimitError(GitHubAPIError):
    """Вичерпано ліміт запитів до GitHub."""


class GitHubTimeoutError(GitHubAPIError):
    """GitHub не відповів вчасно."""


def search_github(search_type, query):
    """
    Виконує пошук у GitHub і повертає сирий JSON (dict).
    Піднімає GitHubAPIError або його нащадків при будь-якій проблемі.
    """
    endpoint = SEARCH_ENDPOINTS[search_type]
    url = f"{GITHUB_API_BASE_URL}{endpoint}"

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

    params = {"q": query, "per_page": RESULTS_PER_PAGE}

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=settings.GITHUB_REQUEST_TIMEOUT,
        )
    except requests.Timeout as exc:
        # Timeout є підкласом RequestException, тому ловимо його першим
        raise GitHubTimeoutError("GitHub не відповів вчасно") from exc
    except requests.RequestException as exc:
        raise GitHubAPIError("Не вдалося зв'язатися з GitHub") from exc

    _raise_for_status(response)

    return response.json()


def _raise_for_status(response):
    """Перетворює HTTP-статус GitHub на наші винятки."""
    # GitHub повертає 403 з remaining=0 або 429, коли ліміт вичерпано
    is_rate_limited = response.status_code == 429 or (
        response.status_code == 403
        and response.headers.get("X-RateLimit-Remaining") == "0"
    )
    if is_rate_limited:
        raise GitHubRateLimitError(
            "Перевищено ліміт запитів до GitHub",
            status_code=response.status_code,
        )

    if response.status_code != 200:
        raise GitHubAPIError(
            f"GitHub повернув помилку {response.status_code}",
            status_code=response.status_code,
        )