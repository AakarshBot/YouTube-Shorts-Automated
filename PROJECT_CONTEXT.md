# YouTube Shorts Automated — Project Context

This file is the current source of truth. Read it before every edit and rewrite it after each change; do not append stale history.

## Rules

Test first, Live second. New functionality is built and proven in Test, then reused by Live after approval. Never create separate unapproved implementations.

No wrappers, adapters, compatibility layers, proxy functions or scaffolding. Replace code directly when a rewrite is needed.

`ranahaani/GNews` is the approved Google News source. Use the maintained `gnews` package; do not copy its source or build a custom Google News client.

`AakarshBot/Final-Shorts` is reference material only, not a code source.

## Factory

Seven stages:
1. Topic Fetcher
2. Scriptwriter
3. Audio
4. Subtitles
5. Visuals
6. Renderer
7. Upload

Current Test line: Deep-Dive → Sports.
Current sports desks: Cricket — India / Pakistan / Sri Lanka / Asia; Cricket — Global; Niche Sports — Global.
Live remains disabled until Test functions are approved.

## Step 01 — Topic Fetcher

Status: **Test / not approved**.

Requirements:
- Return 20 unique topic pills per desk when the source pool supports it.
- Over-fetch so filtering/grouping does not shrink the useful pool.
- Prefer current stories; use the newest 24 hours when it can supply 20 distinct groups, otherwise retain the 72-hour discovery pool.
- Remove utility pages: schedules, fixtures, standings, scorecards, watch guides, predicted lineups, galleries, quizzes, odds and similar pages.
- Avoid stale recap/review material without a new development.
- Group related headlines under an entity/topic while leaving final editorial choice to manual QC.
- Keep multiple current stories about the same person/entity in that entity's pill when appropriate.
- Preserve title, URL, publisher and publication time for every headline.
- English only for now; language support comes later.

Implementation:
- `topic_fetcher.py` is factory-specific logic around the maintained `gnews` package.
- `GNews.get_news()` is called directly and concurrently across the configured query set.
- Local logic only: cleanup, URL dedupe, freshness selection, entity grouping, related-story dedupe and simple ranking.
- No AI classification, GDELT, custom RSS client or retrieval wrapper.

Handoff:
- `topic`
- selected headline
- source URL
- publisher
- publication time
- grouped headline context when available

## Test shell

`app.py` provides Homepage → Test → Deep-Dive → Sports → Genre → Topic Fetcher. The seven stages are displayed; only Topic Fetcher is active.

UI: light/warm, readable, compact, minimal CSS, straightforward Streamlit.

## Tests and CI

`tests/test_topic_fetcher.py` covers the three desks, entity extraction and related-story detection.

`.github/workflows/test.yml` installs dependencies, runs pytest, then performs a real fetch for all three desks and requires 20 returned topic pills per desk.

CI/runtime success is not editorial approval; the returned stories still require manual QC.

## Current files

- `PROJECT_CONTEXT.md` — current build rules and state
- `topic_fetcher.py` — Topic Fetcher
- `app.py` — Test dashboard
- `tests/test_topic_fetcher.py` — focused tests
- `.github/workflows/test.yml` — CI and live-fetch smoke test
- `requirements.txt` — runtime dependencies