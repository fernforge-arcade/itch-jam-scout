#!/usr/bin/env python3
"""
jam_scout.py — screen an itch.io jam page for the visibility-algorithm axis
(opportunity p-gje5aa: pick jams whose ranking mechanic rewards rating volume).

Usage:
    python3 jam_scout.py <jam-slug-or-url> [<jam-slug-or-url> ...]

For each jam, fetches the public jam page and reports:
  - submission/voting window (parsed from itch's embedded I.ViewJam JSON — the
    only authoritative source; the human-readable countdown text has been wrong
    on this jam before)
  - current phase (submissions open / voting open / closed) as of now (UTC)
  - whether the host's own description text names itch's Rating Queue system
    (the fairness-floor mechanic — NOT a "rate more to be seen more" multiplier,
    see memory/discovery-backlog.md) — this is host-disclosed, not an API flag,
    so a false "no" just means "not verifiable from the page", not "absent"
  - entry count, when the page exposes it, since a small pool is where an
    agent's own rating activity is a bigger fraction of total votes

No login, no rating, no write actions — read-only reconnaissance only.
"""
import sys
import re
import json
import urllib.request
from datetime import datetime, timezone

UA = "Mozilla/5.0 ArcadeForge/1.0"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="replace")


def normalize_url(arg):
    if arg.startswith("http"):
        return arg
    return f"https://itch.io/jam/{arg}"


def parse_view_jam(html):
    m = re.search(r"I\.ViewJam\('#view_jam_\d+',\s*(\{.*?\})\)", html)
    if not m:
        return None
    return json.loads(m.group(1))


def parse_dt(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)


def phase(meta, now):
    start = parse_dt(meta["start_date"])
    end = parse_dt(meta["end_date"])
    voting_end = meta.get("voting_end_date")
    voting_end = parse_dt(voting_end) if voting_end else None
    if now < start:
        return "not started"
    if now < end:
        return "submissions open"
    if voting_end and now < voting_end:
        return "voting open"
    return "closed"


def rating_queue_signal(html):
    return bool(re.search(r"rating queue", html, re.IGNORECASE))


def entry_count(html):
    # itch shows a "Joined"/"Entries" stat pair in stat_box widgets; entries only
    # appears once submissions have closed, so "Joined" is the best pre-close proxy
    # for pool size (bigger pool = your own ratings move the needle less).
    stats = {label: value for value, label in re.findall(
        r'stat_value">(\d+)</div><div class="stat_label">([^<]+)', html)}
    for label in ("Entries", "Submissions", "Joined"):
        if label in stats:
            return f"{stats[label]} {label.lower()}"
    m = re.search(r'([\d,]+)\s+(?:entries|submissions|games)\b', html, re.IGNORECASE)
    if m:
        return m.group(1)
    return None


def scout(arg, now=None):
    url = normalize_url(arg)
    now = now or datetime.now(timezone.utc)
    html = fetch(url)
    meta = parse_view_jam(html)
    result = {"url": url}
    if meta is None:
        result["error"] = "no I.ViewJam block found (page shape changed or not a jam page)"
        return result
    result["start_date"] = meta.get("start_date")
    result["end_date"] = meta.get("end_date")
    result["voting_end_date"] = meta.get("voting_end_date")
    result["phase"] = phase(meta, now)
    result["rating_queue_disclosed"] = rating_queue_signal(html)
    result["entry_count_hint"] = entry_count(html)
    return result


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    for arg in argv[1:]:
        r = scout(arg)
        print(json.dumps(r, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
