# itch-jam-scout

A read-only CLI that answers the two questions that actually matter before you
enter an itch.io game jam: **what phase is it in right now**, and **how big is
the pool you're competing in**.

```
pip install itch-jam-scout
jam-scout trijam-379 codex-game-jam-2026
```

```json
{
  "url": "https://itch.io/jam/trijam-379",
  "start_date": "2026-07-04 00:00:00",
  "end_date": "2026-07-06 00:00:00",
  "voting_end_date": "2026-07-13 00:00:00",
  "phase": "voting open",
  "rating_queue_disclosed": false,
  "coverage_rule_disclosed": false,
  "entry_count_hint": "28 entries"
}
```

No `pip`? It's one file with zero dependencies — `python3 jam_scout.py <jam-slug>` works straight from a clone.

## Why this exists

itch jam pages show a countdown timer in the page header, and that timer is
sometimes wrong — hosts extend deadlines after the page ships, and the
human-readable text doesn't always get updated in step. The one place that
can't lie is the `I.ViewJam(...)` JSON blob itch embeds in every jam page to
drive its own countdown widget. This tool parses that blob directly instead
of trusting the rendered text, so a moved deadline shows up correctly the
first time you run it, not after you've already miscounted.

It also surfaces the join/entry count where itch exposes it. That number
matters more than people give it credit for: in a jam with 800 entries, your
own rating activity is noise. In a jam with 20, it's a meaningful fraction of
total votes — worth knowing before you decide where to spend a Saturday.

## What it checks

- **Phase** — not started / submissions open / voting open / closed, computed
  against the jam's actual start/end/voting-end timestamps, not the countdown
  text.
- **Pool size** — join or entry count, when itch's page markup exposes it.
- **Rating Queue mention** — whether the host's own jam description names
  itch's Rating Queue system in text. This is a text search, not an API flag:
  a `false` means "not mentioned on the page," not "confirmed off." Treat a
  `true` as a real signal and a `false` as no signal either way.
- **Coverage rule mention** — whether the page states a minimum number of
  ratings you have to give or receive to count as a valid entry. Worth
  checking because jam size alone doesn't predict how many entries actually
  get rated: a 65-entry jam with no enforced minimum left 11 entries at zero
  ratings, while a 485-entry jam with one rated 483 of them. In practice most
  hosts don't put this in the page description even when it's true, so
  expect `false` a lot — read it as "not stated here," not "doesn't exist."

## What it doesn't do

No login, no rating, no write actions of any kind — it fetches one public
page and parses it. It can't tell you whether Rating Queue is toggled on for
a jam that doesn't say so in its description; that toggle only becomes
visible to logged-in entrants on the jam's own rate page, which is out of
scope for something meant to run anonymously against any jam slug.

## Usage

```
jam-scout <jam-slug> [<jam-slug> ...]
jam-scout https://itch.io/jam/some-jam-2026
```

Or, without installing anything: `python3 jam_scout.py <jam-slug>`.

Pass as many slugs or full URLs as you want; each prints its own JSON object.

## Requirements

Python 3.8+, standard library only. No dependencies to install.

---

Built autonomously by an AI agent as part of [Arcade Forge](https://fernforge.itch.io), an itch.io distribution experiment.
