import requests
from flask import Flask, render_template_string, request

from main import get_user, get_repos, top_repos, language_summary

app = Flask(__name__)

EXAMPLES = ["torvalds", "gvanrossum", "Mehwish-bibi8"]


def build_profile(username):
    """Fetch live data from the GitHub API and shape it for the page."""
    user = get_user(username)
    repos = get_repos(username)
    langs = language_summary(repos)
    total = sum(c for _, c in langs) or 1
    return {
        "name": user["name"] or user["login"],
        "login": user["login"],
        "bio": user["bio"] or "No bio",
        "avatar": user["avatar_url"],
        "url": user["html_url"],
        "followers": user["followers"],
        "repos": user["public_repos"],
        "stars": sum(r["stargazers_count"] for r in repos),
        "top": top_repos(repos),
        "langs": [(l, c, round(c * 100 / total)) for l, c in langs],
    }


def safe_profile(username):
    """Return (profile, error_message)."""
    if not username:
        return None, None
    try:
        return build_profile(username), None
    except (ValueError, RuntimeError) as err:
        return None, str(err)
    except requests.exceptions.RequestException:
        return None, "Network error. Check your internet connection."


PAGE = """
<!DOCTYPE html>
<html data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GitHub Profile Card</title>
<style>
  :root { --bg:linear-gradient(135deg,#0d1117,#1b2a4a); --card:#161b22; --text:#e6edf3;
          --muted:#8b949e; --line:#30363d; --accent:#58a6ff; --green:#238636; }
  [data-theme="light"] { --bg:linear-gradient(135deg,#eef3ff,#dbe7ff); --card:#ffffff;
          --text:#1f2328; --muted:#59636e; --line:#d0d7de; --accent:#0969da; }
  * { box-sizing:border-box; }
  body { margin:0; min-height:100vh; background:var(--bg); color:var(--text);
         font-family:Segoe UI,Arial,sans-serif; padding:24px 16px 50px; }
  header { text-align:center; }
  h1 { margin:0; font-size:34px; }
  .sub { color:var(--muted); margin:6px 0 18px; }
  nav { display:flex; justify-content:center; gap:10px; margin-bottom:18px; flex-wrap:wrap; }
  nav a, .btn { padding:10px 18px; border-radius:8px; border:1px solid var(--line);
         color:var(--text); text-decoration:none; background:var(--card); cursor:pointer;
         font-size:15px; }
  nav a.active { background:var(--accent); color:#fff; border-color:var(--accent); }
  form { display:flex; justify-content:center; gap:8px; flex-wrap:wrap; }
  input { padding:12px 16px; font-size:16px; width:230px; border-radius:8px;
          border:1px solid var(--line); background:var(--card); color:var(--text); }
  button.go { padding:12px 22px; font-size:16px; border-radius:8px; background:var(--green);
          color:#fff; border:none; cursor:pointer; }
  .chips { text-align:center; margin:14px 0; color:var(--muted); font-size:14px; }
  .chips a { display:inline-block; margin:4px; padding:5px 12px; border-radius:20px;
          background:var(--card); border:1px solid var(--line); color:var(--accent);
          text-decoration:none; }
  .error { text-align:center; color:#f85149; margin:14px 0; font-weight:600; }
  .tools { text-align:center; margin-top:8px; display:flex; gap:8px; justify-content:center; }
  .grid { display:flex; justify-content:center; gap:24px; flex-wrap:wrap; margin-top:20px; }
  .card { background:var(--card); border:1px solid var(--line); border-radius:16px;
          width:400px; max-width:100%; padding:26px; }
  .top { text-align:center; }
  .top img { width:110px; height:110px; border-radius:50%; border:3px solid var(--accent); }
  .top h2 { margin:10px 0 0; font-size:22px; }
  .top a { color:var(--muted); text-decoration:none; }
  .bio { color:var(--muted); font-size:14px; }
  .stats { display:flex; justify-content:space-around; margin:18px 0; text-align:center;
           font-size:13px; color:var(--muted); }
  .stat b { display:block; font-size:21px; color:var(--accent); }
  .stat.win b::after { content:" \\1F3C6"; font-size:16px; }
  h3 { font-size:13px; color:var(--muted); text-transform:uppercase; margin:18px 0 6px; }
  .row { display:flex; justify-content:space-between; padding:7px 0;
         border-bottom:1px solid var(--line); font-size:14px; }
  .row a { color:var(--text); text-decoration:none; }
  .row a:hover { color:var(--accent); }
  .row span { color:var(--muted); }
  .bar { height:8px; background:var(--line); border-radius:6px; overflow:hidden; margin-top:4px; }
  .bar i { display:block; height:100%; background:var(--accent); }
  .lang { margin:9px 0; font-size:14px; }
  .lang span { float:right; color:var(--muted); }
  .hint { text-align:center; color:var(--muted); margin-top:40px; }
</style>
</head>
<body>

{% macro card(p, wins=[]) %}
<div class="card">
  <div class="top">
    <img src="{{ p.avatar }}" alt="avatar">
    <h2>{{ p.name }}</h2>
    <a href="{{ p.url }}" target="_blank">@{{ p.login }}</a>
    <p class="bio">{{ p.bio }}</p>
  </div>
  <div class="stats">
    {% for key, label in [('followers','Followers'), ('repos','Repos'), ('stars','Total stars')] %}
    <div class="stat {{ 'win' if key in wins }}"><b>{{ '{:,}'.format(p[key]) }}</b>{{ label }}</div>
    {% endfor %}
  </div>
  <h3>Top repos</h3>
  {% for r in p.top %}
  <div class="row"><a href="{{ r.html_url }}" target="_blank">{{ r.name }}</a>
    <span>&#9733; {{ '{:,}'.format(r.stargazers_count) }}</span></div>
  {% else %}
  <div class="row"><span>No public repos yet</span></div>
  {% endfor %}
  <h3>Languages</h3>
  {% for lang, count, pct in p.langs %}
  <div class="lang">{{ lang }} <span>{{ count }} repos ({{ pct }}%)</span>
    <div class="bar"><i style="width:{{ pct }}%"></i></div></div>
  {% else %}
  <div class="row"><span>No language data</span></div>
  {% endfor %}
</div>
{% endmacro %}

<header>
  <h1>GitHub Profile Card</h1>
  <p class="sub">Live stats from the GitHub API. Search a developer or compare two.</p>
  <nav>
    <a href="/" class="{{ 'active' if mode == 'single' }}">Search</a>
    <a href="/compare" class="{{ 'active' if mode == 'compare' }}">Compare</a>
    <a class="btn" onclick="toggleTheme()">Theme</a>
  </nav>
</header>

{% if mode == 'single' %}
  <form method="get" action="/" onsubmit="loading(this)">
    <input name="username" placeholder="e.g. torvalds" value="{{ q1 }}" required>
    <button class="go">Show card</button>
  </form>
  <div class="chips">Try:
    {% for e in examples %}<a href="/?username={{ e }}">{{ e }}</a>{% endfor %}
  </div>
{% else %}
  <form method="get" action="/compare" onsubmit="loading(this)">
    <input name="a" placeholder="First username" value="{{ q1 }}" required>
    <input name="b" placeholder="Second username" value="{{ q2 }}" required>
    <button class="go">Compare</button>
  </form>
  <div class="chips">Try:
    <a href="/compare?a=torvalds&b=gvanrossum">torvalds vs gvanrossum</a>
  </div>
{% endif %}

{% for err in errors %}<div class="error">{{ err }}</div>{% endfor %}

<div class="grid">
  {% if mode == 'single' and p1 %}{{ card(p1) }}{% endif %}
  {% if mode == 'compare' and p1 and p2 %}
    {{ card(p1, wins1) }}{{ card(p2, wins2) }}
  {% endif %}
</div>

{% if p1 and (mode == 'single' or p2) %}
<div class="tools"><a class="btn" id="copy" onclick="copyLink()">Copy link</a></div>
{% elif not errors %}
<p class="hint">Enter a username above to get started.</p>
{% endif %}

<script>
  function loading(form) {
    var b = form.querySelector("button");
    b.textContent = "Loading...";
  }
  function copyLink() {
    navigator.clipboard.writeText(location.href);
    document.getElementById("copy").textContent = "Copied!";
  }
  function toggleTheme() {
    var t = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", t);
    try { localStorage.setItem("theme", t); } catch (e) {}
  }
  try {
    var saved = localStorage.getItem("theme");
    if (saved) document.documentElement.setAttribute("data-theme", saved);
  } catch (e) {}
</script>
</body>
</html>
"""


def render(**kwargs):
    defaults = dict(mode="single", q1="", q2="", p1=None, p2=None, errors=[],
                    wins1=[], wins2=[], examples=EXAMPLES)
    defaults.update(kwargs)
    return render_template_string(PAGE, **defaults)


@app.route("/")
def home():
    q = request.args.get("username", "").strip()
    p, err = safe_profile(q)
    return render(mode="single", q1=q, p1=p, errors=[err] if err else [])


@app.route("/compare")
def compare():
    a = request.args.get("a", "").strip()
    b = request.args.get("b", "").strip()
    p1, e1 = safe_profile(a)
    p2, e2 = safe_profile(b)
    errors = [e for e in (e1, e2) if e]
    wins1, wins2 = [], []
    if p1 and p2:
        for key in ("followers", "repos", "stars"):
            if p1[key] > p2[key]:
                wins1.append(key)
            elif p2[key] > p1[key]:
                wins2.append(key)
    return render(mode="compare", q1=a, q2=b, p1=p1, p2=p2, errors=errors,
                  wins1=wins1, wins2=wins2)


if __name__ == "__main__":
    app.run(debug=True)