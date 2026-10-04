# YouTube Shorts Automated — Project Context

Current source of truth. Read before every edit and rewrite after every change; do not append history.

## Rules

- Test first, Live second. Build and prove new functionality in Test, then reuse it in Live only after approval.
- No wrappers, adapters, compatibility layers, proxy functions or scaffolding. Delete and rewrite code directly when the current approach is wrong.
- ranahaani/GNews is the approved Google News source. Use the maintained gnews package; do not copy its source or build a custom Google News client.
- No new runtime dependencies for the Topic Fetcher.
- AakarshBot/Final-Shorts is reference material only, not a code source.

## Current factory

Seven stages: Topic Fetcher → Scriptwriter → Audio → Subtitles → Visuals → Renderer → Upload.

Current Test line: Deep-Dive → Sports.
Current desks: Cricket — India / Pakistan / Sri Lanka / Asia; Cricket — Global; Niche Sports — Global.
Live is disabled until Test functions are approved.

## Step 01 — Topic Fetcher

Status: Test / not approved.

### Regional Cricket

Top-level pills are countries, not player/entity groups.
- India: up to 20 headline pills.
- Pakistan: target at least 5 headline pills.
- Sri Lanka: target at least 5 headline pills.
- Bangladesh and Afghanistan: include qualifying headlines when available.

Each country pill expands directly into headline pills. Headlines are not merged into player/entity topic groups.

The fetcher uses separate GNews country settings for IN, PK, LK, BD and AF. Queries are explicitly cricket-focused and a cricket-specific title filter prevents niche-sport stories from spilling into cricket.

### Global Cricket

Top-level pills are countries.
- Use separate country-specific GNews searches for major cricket nations.
- Create a country pill only when that country has at least one fresh qualifying headline within 24 hours.
- Each country pill expands directly into headline pills.
- Do not manufacture 20 country pills.

### Niche Sports

Top-level pills are sports, not countries.
- Cricket is excluded.
- Current search coverage includes Football, Tennis, Basketball, Athletics, Motorsport, Badminton, Hockey, Golf, Boxing, Wrestling, Swimming, Rugby, Volleyball, Cycling, Baseball and Table Tennis.
- A sport pill is created only from fresh qualifying headlines and expands directly into headline pills.

### Common filtering and freshness

- Remove schedules, fixtures, standings, scorecards, live-score pages, watch guides, predicted lineups, galleries, quizzes, odds, recaps, round-ups, tournament reviews and similar utility material.
- Prefer the newest 24 hours.
- Regional cricket can fall back to the 72-hour pool to reach country targets.
- Global Cricket and Niche do not create pills from stale-only results.
- Preserve title, URL, publisher and publication time.
- Final story selection is manual.
- English only for now; language support comes later.
- Search 20 more fetches unseen URLs and merges new headlines into the existing country or sport pills.

## Test dashboard

app.py provides Homepage → Test → Deep-Dive → Sports → Topic Fetcher.
The Topic Fetcher screen starts with Fetch stories. After results load it shows Search 20 more.
The dashboard uses a light/warm theme with explicit readable button states and compact headline pills.

## Tests and CI

tests/test_topic_fetcher.py checks desk structure, cricket-specific query design and non-cricket sports breadth.

.github/workflows/test.yml installs dependencies, runs pytest, then performs a real fetch:
- Regional Cricket must contain India, Pakistan and Sri Lanka pills, with at least 5 headlines under Pakistan and Sri Lanka.
- Global Cricket has variable country-pill count; there is no exact 20-pill assertion.
- Niche must return multiple sport pills and no cricket pill.

CI success is a technical check, not editorial approval. Stories still require manual QC.

## Current files

- PROJECT_CONTEXT.md — current rules and state
- topic_fetcher.py — Topic Fetcher
- app.py — Test dashboard
- tests/test_topic_fetcher.py — focused tests
- .github/workflows/test.yml — CI and live-fetch smoke test
- requirements.txt — runtime dependencies
