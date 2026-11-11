# GitHub Profile Card

A Python tool that shows a GitHub user's profile summary
using live data from the public GitHub REST API.

## Preview
![Compare two developers](preview.png)

## What it does
- Shows name, bio, followers, following and public repo count
- Lists the top 5 repositories by stars
- Shows the most-used programming languages with percentage bars
- Web interface built with Flask: search a user, compare two users, dark/light theme
- Handles invalid usernames and API rate limits

## Installation
1. Install Python 3
2. Clone this repository:
   ```
   git clone https://github.com/Mehwish-bibi8/github-profile-card.git
   cd github-profile-card
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Command line
```
python main.py USERNAME
```
Or run `python main.py` and type a username when asked.

### Web app
```
python app.py
```
Open http://127.0.0.1:5000 in your browser.
- **Search:** type any GitHub username to see their live profile card
- **Compare:** compare two developers side by side
- **Theme:** switch between dark and light mode

## Sample output
```
========================================
Linus Torvalds  (@torvalds)
No bio
========================================
Followers:    331558
Following:    0
Public repos: 12

Top repos by stars:
  * linux (255328 stars)
  * AudioNoise (4532 stars)
  * GuitarPedal (2492 stars)
  * uemacs (2198 stars)
  * test-tlb (1083 stars)

Most-used languages:
  - C: 10 repos
  - C++: 1 repos
  - OpenSCAD: 1 repos
```

## API used
[GitHub REST API](https://docs.github.com/en/rest) (no API key needed, limit of 60 requests per hour).
Data is fetched live from the public API.