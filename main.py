import sys
from collections import Counter

import requests

BASE_URL = "https://api.github.com"


def get_user(username):
    """Fetch basic profile info for a GitHub user."""
    response = requests.get(f"{BASE_URL}/users/{username}", timeout=10)
    if response.status_code == 404:
        raise ValueError(f"User '{username}' not found.")
    if response.status_code == 403:
        raise RuntimeError("Rate limit reached (60 requests/hour). Try again later.")
    response.raise_for_status()
    return response.json()


def get_repos(username):
    """Fetch the user's public repositories."""
    response = requests.get(
        f"{BASE_URL}/users/{username}/repos",
        params={"per_page": 100, "sort": "updated"},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def top_repos(repos, n=5):
    """Return the n most-starred repos."""
    return sorted(repos, key=lambda r: r["stargazers_count"], reverse=True)[:n]


def language_summary(repos):
    """Count how often each language is used across repos."""
    counts = Counter(r["language"] for r in repos if r["language"])
    return counts.most_common(5)


def print_card(user, repos):
    print("=" * 40)
    print(f"{user['name'] or user['login']}  (@{user['login']})")
    print(user["bio"] or "No bio")
    print("=" * 40)
    print(f"Followers:    {user['followers']}")
    print(f"Following:    {user['following']}")
    print(f"Public repos: {user['public_repos']}")

    print("\nTop repos by stars:")
    for repo in top_repos(repos):
        print(f"  * {repo['name']} ({repo['stargazers_count']} stars)")

    print("\nMost-used languages:")
    for lang, count in language_summary(repos):
        print(f"  - {lang}: {count} repos")


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else input("GitHub username: ").strip()
    try:
        user = get_user(username)
        repos = get_repos(username)
    except (ValueError, RuntimeError) as err:
        print(f"Error: {err}")
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print(f"Network error: {err}")
        sys.exit(1)
    print_card(user, repos)


if __name__ == "__main__":
    main()