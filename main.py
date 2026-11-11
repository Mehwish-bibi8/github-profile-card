from collections import Counter
import requests


def get_user(username):
    response = requests.get(f"https://api.github.com/users/{username}", timeout=10)
    return response.json()


def get_repos(username):
    response = requests.get(
        f"https://api.github.com/users/{username}/repos",
        params={"per_page": 100},
        timeout=10,
    )
    return response.json()


def top_repos(repos, n=5):
    return sorted(repos, key=lambda r: r["stargazers_count"], reverse=True)[:n]
def language_summary(repos):
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
    username = input("GitHub username: ").strip()
    user = get_user(username)
    repos = get_repos(username)
    print_card(user, repos)


main()