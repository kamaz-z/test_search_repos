def normalize_user(raw_user):
    return {
        "id": raw_user["id"],
        "login": raw_user["login"],
        "avatar_url": raw_user["avatar_url"],
        "html_url": raw_user["html_url"],
    }


def normalize_repository(raw_repo):
    # owner може бути null, тому підставляємо порожній словник
    owner = raw_repo.get("owner") or {}

    return {
        "id": raw_repo["id"],
        "name": raw_repo["name"],
        "full_name": raw_repo["full_name"],
        "owner_login": owner.get("login", ""),
        "html_url": raw_repo["html_url"],
        "description": raw_repo.get("description"),
        # Перейменування: GitHub називає поля довго, ми коротко
        "stars": raw_repo.get("stargazers_count", 0),
        "forks": raw_repo.get("forks_count", 0),
        "language": raw_repo.get("language"),
    }


def normalize_issue(raw_issue):
    user = raw_issue.get("user") or {}

    return {
        "id": raw_issue["id"],
        "title": raw_issue["title"],
        "html_url": raw_issue["html_url"],
        "state": raw_issue["state"],
        "author_login": user.get("login"),
        "comments": raw_issue.get("comments", 0),
        "created_at": raw_issue["created_at"],
    }


NORMALIZERS = {
    "users": normalize_user,
    "repositories": normalize_repository,
    "issues": normalize_issue,
}


def normalize_search_response(search_type, raw_response, page, per_page):
    normalize_item = NORMALIZERS[search_type]

    raw_items = raw_response.get("items", [])
    total_count = raw_response.get("total_count", 0)

    return {
        "total_count": total_count,
        "page": page,
        # Якщо ця сторінка закриває всі результати, далі нічого немає
        "has_more": page * per_page < total_count,
        "items": [normalize_item(item) for item in raw_items],
    }