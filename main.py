import html
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
def save_html(user, repos, filename="card.html"):
    """Save the profile card as a styled HTML page."""
    e = html.escape
    repo_items = "".join(
        f"<li>{e(r['name'])} <span>&#9733; {r['stargazers_count']}</span></li>"
        for r in top_repos(repos)
    )
    lang_items = "".join(
        f"<li>{e(lang)} <span>{count} repos</span></li>"
        for lang, count in language_summary(repos)
    )
    page = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>GitHub Profile Card</title>
<style>
  body {{ background:#0d1117; font-family:Segoe UI,Arial,sans-serif;
         display:flex; justify-content:center; padding:40px; }}
  .card {{ background:#161b22; color:#e6edf3; width:420px; padding:30px;
          border-radius:16px; border:1px solid #30363d; }}
  .top {{ text-align:center; }}
  .top img {{ width:110px; border-radius:50%; border:3px solid #58a6ff; }}
  h1 {{ margin:12px 0 0; font-size:24px; }}
  .user {{ color:#8b949e; }}
  .stats {{ display:flex; justify-content:space-around; margin:20px 0; }}
  .stats div {{ text-align:center; }}
  .stats b {{ display:block; font-size:22px; color:#58a6ff; }}
  h2 {{ font-size:15px; color:#8b949e; text-transform:uppercase; }}
  ul {{ list-style:none; padding:0; }}
  li {{ display:flex; justify-content:space-between; padding:6px 0;
       border-bottom:1px solid #21262d; }}
  li span {{ color:#8b949e; }}
</style>
</head>
<body>
<div class="card">
  <div class="top">
    <img src="{e(user['avatar_url'])}">
    <h1>{e(user['name'] or user['login'])}</h1>
    <div class="user">@{e(user['login'])}</div>
    <p>{e(user['bio'] or '')}</p>
  </div>
  <div class="stats">
    <div><b>{user['followers']}</b>Followers</div>
    <div><b>{user['following']}</b>Following</div>
    <div><b>{user['public_repos']}</b>Repos</div>
  </div>
  <h2>Top repos</h2>
  <ul>{repo_items}</ul>
  <h2>Languages</h2>
  <ul>{lang_items}</ul>
</div>
</body>
</html>"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(page)

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    username = args[0] if args else input("GitHub username: ").strip()
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
    if "--html" in sys.argv:
        save_html(user, repos)
        print("\nSaved card.html (open it in your browser)")


if __name__ == "__main__":
    main()