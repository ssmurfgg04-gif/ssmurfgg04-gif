#!/usr/bin/env python3
"""
Self-hosted stats card renderer — arctic chrome edition.
Replaces the flaky github-readme-stats shared instance.
Pure stdlib. Renders dark + light SVG cards from public GitHub REST data.

Usage: python3 render_stats.py <out-dark.svg> <out-light.svg>
Env:   GH_TOKEN (optional — raises rate limits when run in Actions)
"""
import json, os, sys, urllib.request
from datetime import datetime, timezone

USER = "ssmurfgg04-gif"

def get(url):
    headers = {"User-Agent": "arctic-telemetry", "Accept": "application/vnd.github+json"}
    tok = os.environ.get("GH_TOKEN")
    if tok:
        headers["Authorization"] = f"Bearer {tok}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

# ---------- gather metrics from public REST endpoints ----------
user = get(f"https://api.github.com/users/{USER}")
followers = user["followers"]

commits = get(f"https://api.github.com/search/commits?q=author:{USER}&per_page=1")["total_count"]

own_repos, stars = 0, 0
page = 1
while True:
    batch = get(f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}&type=owner")
    if not batch:
        break
    for r in batch:
        if not r["fork"]:
            own_repos += 1
            stars += r["stargazers_count"]
    page += 1

METRICS = [
    ("commits", "COMMITS", f"{commits:,}"),
    ("stars", "STARS EARNED", f"{stars:,}"),
    ("followers", "FOLLOWERS", f"{followers:,}"),
    ("repos", "PUBLIC REPOS", f"{own_repos:,}"),
]
STAMP = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

# ---------- icons (16x16 hand-drawn paths) ----------
ICONS = {
    "commits": '<circle cx="4.5" cy="12" r="3"/><circle cx="11.5" cy="4" r="3"/><path d="M11.5 7 v1.5 a3 3 0 0 1 -3 3 H7.5" fill="none" stroke="{c}" stroke-width="1.6"/>',
    "stars": '<path d="M8 1.5 l1.9 4.1 4.4 .5 -3.3 3 1 4.4 L8 11.3 4 13.5 5 9.1 1.7 6.1 6.1 5.6 Z"/>',
    "followers": '<circle cx="8" cy="4.5" r="3.2"/><path d="M1.8 15.5 a6.2 6.2 0 0 1 12.4 0 Z"/>',
    "repos": '<path d="M2.5 2.5 h7 a2 2 0 0 1 2 2 v9 h-9 a2 2 0 0 1 -2 -2 Z M11.5 4.5 h2 v9 h-2" fill="none" stroke="{c}" stroke-width="1.7"/>',
}

def icon(name, color):
    return ICONS[name].replace("{c}", color)

def render(theme):
    if theme == "dark":
        bg, title_c, label_c, value_c, icon_c, dim, line = \
            "#0B0F1A", "#05D9E8", "#9CCFD8", "#F2F8FF", "#FF2A6D", "#6E6A86", "#1C2740"
    else:
        bg, title_c, label_c, value_c, icon_c, dim, line = \
            "#EAF0F6", "#0891B2", "#39516B", "#0F172A", "#BE185D", "#8296A8", "#C9D7E2"

    W, H = 500, 195
    rows = []
    y = 84
    for key, label, value in METRICS:
        rows.append(f'''
  <g transform="translate(30,{y - 12})"><g fill="{icon_c}" stroke="none">{icon(key, icon_c)}</g></g>
  <text x="58" y="{y}" font-size="14" fill="{label_c}" letter-spacing="1.2">{label}</text>
  <text x="{W - 30}" y="{y}" font-size="15" font-weight="700" fill="{value_c}" text-anchor="end">{value}</text>''')
        y += 28

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Segoe UI, Ubuntu, Helvetica, Arial, sans-serif">
  <rect width="{W}" height="{H}" rx="6" fill="{bg}"/>
  <text x="30" y="44" font-size="18" font-weight="700" fill="{title_c}">{USER}</text>
  <text x="{W - 30}" y="42" font-size="11" fill="{dim}" text-anchor="end" letter-spacing="1">ARCTIC TELEMETRY</text>
  <line x1="30" y1="58" x2="{W - 30}" y2="58" stroke="{line}" stroke-width="1"/>
  {''.join(rows)}
  <text x="{W - 30}" y="{H - 12}" font-size="9.5" fill="{dim}" text-anchor="end">self-hosted · auto-refreshed 02:00 UTC · {STAMP}</text>
</svg>
'''

if __name__ == "__main__":
    dark, light = sys.argv[1], sys.argv[2]
    open(dark, "w").write(render("dark"))
    open(light, "w").write(render("light"))
    print(f"rendered {dark} + {light}: " + ", ".join(f"{lbl}={val}" for _, lbl, val in METRICS))
