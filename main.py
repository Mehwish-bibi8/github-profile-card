import requests


def get_user(username):
    response = requests.get(f"https://api.github.com/users/{username}", timeout=10)
    return response.json()


def print_card(user):
    print("=" * 40)
    print(f"{user['name'] or user['login']}  (@{user['login']})")
    print(user["bio"] or "No bio")
    print("=" * 40)
    print(f"Followers:    {user['followers']}")
    print(f"Following:    {user['following']}")
    print(f"Public repos: {user['public_repos']}")


def main():
    username = input("GitHub username: ").strip()
    user = get_user(username)
    print_card(user)


main()