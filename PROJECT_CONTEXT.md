# YouTube Shorts Automated — Project Context

Current source of truth. Read before every edit and replace this file completely after every change; do not append history.

## Rules

- Test first, Live second. Build and prove new functionality in Test, then reuse it in Live only after approval.
- No wrappers, adapters, compatibility layers, proxy functions or scaffolding. Delete and rewrite code directly when the current approach is wrong.
- ranahaani/GNews is the approved Google News source. Use the maintained gnews package; do not copy its source or build a custom Google News client.
- No new runtime dependencies.
- AakarshBot/Final-Shorts is reference material only, not a code source.
- English only for now. Language support comes later.
- Final story selection is manual; CI success is not editorial approval.

## Factory

The factory will support multiple formats, including Deep-Dive, Top-5 and Did You Know. Deep-Dive is the format currently being built.

Seven production stages:
Topic Fetcher → Scriptwriter → Audio → Subtitles → Visuals → Renderer → Upload.

Live is disabled until Test functions are approved.

## Deep-Dive desks

Approved Deep-Dive desks:
- Sports — implemented.
- News — approved, not yet implemented.
- Entertainment — approved, not yet implemented.
- Technology — approved, not yet implemented.
- Business & Finance — approved, not yet implemented.
- Gaming — approved, not yet implemented.
- Science & Space — approved, not yet implemented.

Each desk will have its own appropriate top-level pills. Do not force every desk into the Sports country/sport structure.

## Sports — Topic Fetcher

Sports is the completed current desk and should be preserved while non-sports desks are added.

### Regional Cricket

Top-level pills are countries:
- India: up to 20 headline pills.
- Pakistan: target at least 5 headline pills.
- Sri Lanka: target at least 5 headline pills.
- Bangladesh and Afghanistan: include qualifying fresh headlines when available.

Each country pill expands directly into headline pills. Do not merge headlines into player/entity topic groups.

The fetcher uses separate country settings for IN, PK, LK, BD and AF. Queries are explicitly cricket-focused, and a cricket-specific title filter prevents niche-sport stories from entering cricket.

### Global Cricket

Top-level pills are countries:
- Australia
- England
- South Africa
- New Zealand
- Ireland
- Zimbabwe

Create a country pill only when it has at least one fresh qualifying headline within 24 hours. Do not manufacture country pills to reach a fixed count.

### Niche Sports

Top-level pills are sports, not countries. Cricket is excluded.

Current coverage:
Football, Tennis, Basketball, Athletics, Motorsport, Badminton, Hockey, Golf, Boxing, Wrestling, Swimming, Rugby, Volleyball, Cycling, Baseball and Table Tennis.

Create a sport pill only when it has fresh qualifying headlines and expand directly into headline pills.

### Filtering and freshness

Remove schedules, fixtures, standings, scorecards, live-score pages, watch guides, predicted lineups, galleries, quizzes, odds, recaps, round-ups, tournament reviews and similar utility material.

Prefer fresh stories from the newest 24 hours.

Regional Cricket may use a 72-hour fallback only when India, Pakistan or Sri Lanka is below its target. Global Cricket and Niche Sports never create pills from stale-only results.

Preserve title, URL, publisher and publication time.

### Runtime design

The previous Sports fetcher made redundant searches and requested a 3-day pool for every query. The current version is deliberately smaller and faster without changing the editorial pill structure.

- Regional Cricket uses one fresh 24-hour query per country, with a conditional 72-hour fallback only for India/Pakistan/Sri Lanka targets.
- Global Cricket uses one fresh query per country.
- Niche Sports uses one fresh query per sport.
- GNews retrieval is bounded to 30 results per search instead of 100; final headline limits remain unchanged.
- At most 8 GNews requests run concurrently.
- GNews retries 429 rate-limit responses once, rather than using the default multi-retry backoff.
- No alternative news client, cache layer or runtime dependency is introduced.
- Search 20 more reuses the same fetcher, excludes already seen URLs and merges new headlines into the existing country/sport pills.

## Test dashboard

app.py currently provides:
Homepage → Test → Deep-Dive → Sports → Topic Fetcher.

The Topic Fetcher screen starts with Fetch stories. After results load it shows Search 20 more.

The dashboard uses a light/warm theme with readable button states and compact headline cards.

## Tests and CI

tests/test_topic_fetcher.py checks:
- the three current Sports desks,
- regional country structure,
- cricket-specific query design,
- non-cricket sports breadth.

.github/workflows/test.yml:
- installs runtime dependencies plus pytest,
- runs pytest,
- performs a real Topic Fetcher smoke test,
- requires India/Pakistan/Sri Lanka regional pills,
- requires at least 5 Pakistan headlines and 5 Sri Lanka headlines,
- allows variable Global Cricket country-pill count,
- requires multiple Niche Sports pills and no Cricket pill.

CI verifies technical behaviour only. Current real stories still require manual QC.

## Current files

- PROJECT_CONTEXT.md — current project rules and state
- topic_fetcher.py — Sports Topic Fetcher
- app.py — Test dashboard
- tests/test_topic_fetcher.py — focused tests
- .github/workflows/test.yml — CI and real-fetch smoke test
- requirements.txt — runtime dependencies
