#!/usr/bin/env python3
"""Refreshes data/github.json from the GitHub GraphQL API. Keeps old data on any failure."""
import json
import os
import sys
import urllib.request
from datetime import date
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "github.json"
QUERY = """query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) {
      totalCount
      nodes { stargazerCount }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}"""


def to_data(payload):
    user = payload["data"]["user"]
    cal = user["contributionsCollection"]["contributionCalendar"]
    weeks = []
    for wk in cal["weeks"]:
        days = wk["contributionDays"]
        counts = [d["contributionCount"] for d in days]
        weeks.append({"start": days[0]["date"], "total": sum(counts), "days": counts})
    return {
        "source": "graphql",
        "updated": date.today().isoformat(),
        "active_days": sum(1 for w in weeks for c in w["days"] if c),
        "total_contributions": cal["totalContributions"],
        "stars": sum(n["stargazerCount"] for n in user["repositories"]["nodes"]),
        "public_repos": user["repositories"]["totalCount"],
        "weeks": weeks,
    }


def main():
    token, login = os.environ.get("GH_TOKEN"), os.environ.get("GH_USER", "BhuwanJoshi-01")
    if not token:
        print("GH_TOKEN not set, keeping existing data")
        return
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            payload = json.load(res)
        if payload.get("errors"):
            raise RuntimeError(payload["errors"])
        DATA.write_text(json.dumps(to_data(payload), indent=0))
        print("data/github.json refreshed")
    except Exception as exc:  # a failed refresh must never break the profile
        print(f"refresh failed, keeping existing data: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
