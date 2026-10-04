# YouTube Shorts Automated — Project Context

Current source of truth. Read before every edit and rewrite after every change; do not append history.

## Rules

- Test first, Live second. Build and prove new functionality in Test, then reuse it in Live only after approval.
- No wrappers, adapters, compatibility layers, proxy functions or scaffolding. Replace code directly when needed.
- `ranahaani/GNews` is the approved Google News source. Use the maintained `gnews` package; do not copy its source or build a custom Google News client.
- `AakarshBot/Final-Shorts` is reference material only, not a code source.

## Current factory

Seven stages: Topic Fetcher → Scriptwriter → Audio → Subtitles → Visuals → Renderer → Upload.
Current Test line: Deep-Dive → Sports.
Current desks: Cricket — India / Pakistan / Sri Lanka / Asia; Cricket — Global; Niche Sports — Global.
Live is disabled until Test functions are approved.

## Step 01 — Topic Fetcher

Status: **Test / not approved**.

Requirements:
- Produce 20 topic pills per desk when the available source pool supports it.
- Over-fetch so filtering does not unnecessarily shrink the useful pool.
- Prefer current stories, using the newest 24 hours when 20 distinct groups are available; otherwise retain the 72-hour pool.
- Remove utility pages such as schedules, fixtures, standings, scorecards, watch guides, predicted lineups, galleries, quizzes, odds and similar pages.
- Avoid stale recap/review material without a new development.
- Group aggressively by entity/topic so multiple distinct current headlines about the same person/entity stay inside one pill.
- Treat obvious name variants such as a full name and surname as the same group when the strings overlap.
- Do not discard different headlines merely because they describe the same event; each unique source URL can remain as a separate headline in its group.
- Preserve title, URL, publisher and publication time.
- Final story choice is manual.
- English only for now; language support comes later.

Implementation:
- `topic_fetcher.py` calls `GNews.get_news()` directly and concurrently.
- Local processing is limited to cleanup, URL dedupe, freshness selection, entity grouping and simple ranking.
- No AI classification, GDELT, custom RSS client or retrieval wrapper.
- `fetch_topics()` accepts `exclude_topics` and `exclude_urls` so the Test UI can request another batch without repeating visible/previous groups, including overlapping entity-name variants.

## Test dashboard

`app.py` provides Homepage → Test → Deep-Dive → Sports → Genre → Topic Fetcher.
The Topic Fetcher screen has `Fetch 20 stories` for the first batch and `Find 20 more` after results appear.
`Find 20 more` keeps session-level topic/URL exclusions, replaces the visible batch with the new results, and accumulates exclusions so repeated searches do not immediately recycle prior choices.

UI target: light/warm, readable, compact, minimal CSS and straightforward Streamlit.

## Tests and CI

`tests/test_topic_fetcher.py` covers the three desks and entity extraction; the query-count assertion protects the minimum discovery pool.

`.github/workflows/test.yml` installs dependencies, runs pytest, then performs a real fetch for all three desks and requires 20 returned topic pills per desk.
CI success is not editorial approval; returned stories still require manual QC.

## Current files

- `PROJECT_CONTEXT.md` — current rules and state
- `topic_fetcher.py` — Topic Fetcher
- `app.py` — Test dashboard
- `tests/test_topic_fetcher.py` — focused tests
- `.github/workflows/test.yml` — CI and live-fetch smoke test
- `requirements.txt` — runtime dependencies