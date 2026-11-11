import requests


def get_user(username):
    response = requests.get(f"https://api.github.com/users/{username}", timeout=10)
    return response.json()


def main():
    username = input("GitHub username: ").strip()
    user = get_user(username)
    print(user["name"], "(@" + user["login"] + ")")


main()