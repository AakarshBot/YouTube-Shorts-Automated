# YouTube Shorts Automated — Project Context

Current source of truth. Read before every edit and replace this file completely after every change; do not append history.

## Rules

- Test first, Live second. Build and approve functionality in Test before Live.
- No wrappers, adapters, compatibility layers, proxy functions or scaffolding. Delete and rewrite code directly when the current approach is wrong.
- ranahaani/GNews is the approved Google News source. Use the maintained gnews package; do not copy its source or build another news client.
- No new runtime dependencies or API services.
- AakarshBot/Final-Shorts is reference material only, not a code source.
- English only for now. Language support comes later.
- Final story selection is manual. CI passing is technical validation, not editorial approval.

## Factory

Formats planned:
- Deep-Dive
- Top-5
- Did You Know
- Other formats later

Deep-Dive is the current format being built.

Seven stages:
Topic Fetcher → Scriptwriter → Audio → Subtitles → Visuals → Renderer → Upload.

Live remains disabled until Test functions are approved.

## Deep-Dive desks

Deep-Dive opens into:
- Sports
- News
- Entertainment
- Technology
- Business & Finance
- Gaming
- Science & Space

Sports is the completed desk. The six non-Sports desks have initial Topic Fetcher coverage.

## Topic Fetcher

The fetcher is pill-based. A selected desk exposes focused top-level pills; each pill expands directly into headline choices with title, publisher, publication time and source URL.

### Sports

Sports opens:
1. Cricket — India / Pakistan / Sri Lanka / Asia
2. Cricket — Global
3. Niche Sports — Global

#### Regional Cricket

Country pills:
- India: up to 20 headlines
- Pakistan: target at least 5
- Sri Lanka: target at least 5
- Bangladesh: include when fresh qualifying stories exist
- Afghanistan: include when fresh qualifying stories exist

Regional Cricket uses one targeted Google News search per country in the first pass. India/Pakistan/Sri Lanka can fall back to a 72-hour search only when their headline targets are not met.

The cricket searches are intentionally specific rather than simply searching for the country plus the word cricket. They target team/board/player/format signals and exclude obvious database/utility phrases inside the Google News query.

This is a retrieval-quality rule, not an article-understanding classifier.

#### Global Cricket

Country pills:
Australia, England, South Africa, New Zealand, Ireland and Zimbabwe.

A country pill exists only when it has fresh qualifying headlines within 24 hours.

#### Niche Sports

Sport pills:
Football, Tennis, Basketball, Athletics, Motorsport, Badminton, Hockey, Golf, Boxing, Wrestling, Swimming, Rugby, Volleyball, Cycling, Baseball and Table Tennis.

Cricket is excluded. Only fresh qualifying stories create sport pills.

### Story-quality filtering

Keep the Python quality filter deliberately small.

Reject obvious utility/reference material such as schedules, fixtures, standings, scorecards, watch guides, predicted lineups, galleries, quizzes, odds, recaps, round-ups and similar pages.

For cricket, also reject clear database-style pages such as “records & stats”, “team records”, “career stats” and “cricket grounds”.

Do not build a semantic classifier, article scraper, publisher allowlist, LLM review step or additional news API.

A cricket keyword alone is not considered sufficient by the retrieval design: the Google News query should provide stronger cricket-story signals before Python sees the result.

A broader story that legitimately reports a cricket development may still be included when Google News associates it with the targeted cricket search; final selection remains manual.

### Common freshness and dedupe

- Freshness target: newest 24 hours.
- Regional Cricket: 72-hour fallback only when India/Pakistan/Sri Lanka misses its target.
- Global Cricket and Niche Sports: no stale-only pills.
- Preserve title, URL, publisher and publication time.
- Normalise URLs before dedupe.
- Search 20 more excludes previously shown URLs and merges unseen headlines into the existing pill.
- First fetch requests up to 20 GNews results per query; Search 20 more can request up to 40.
- At most 8 GNews searches run concurrently.
- GNews rate-limit retries are limited to one.
- No cache, alternate news provider or runtime dependency is introduced.

## Non-Sports Deep-Dive desks

Approved desks and current initial pills:

### News
India; World; Politics & Policy; Major Events.

### Entertainment
Indian Film & OTT; Global Film & TV; Music; Celebrities.

### Technology
AI; Phones & Gadgets; Big Tech & Platforms; Startups & Innovation.

### Business & Finance
India Markets; Global Markets; Companies & Deals; Economy & Policy.

### Gaming
Games & Releases; Esports; Industry & Platforms; Hardware.

### Science & Space
Space; Science & Research; Environment & Climate; Major Discoveries.

Each uses one focused fresh GNews search per pill and the same lightweight filtering/dedupe flow.

## Test dashboard

Flow:
Homepage → Test → Deep-Dive → Desk → Topic Fetcher.

Sports:
Deep-Dive → Sports → Cricket / Global Cricket / Niche Sports → Topic Fetcher.

Non-Sports:
Deep-Dive → News / Entertainment / Technology / Business & Finance / Gaming / Science & Space → Topic Fetcher.

For Sports Topic Fetcher, back returns to Sports. For non-Sports Topic Fetcher, back returns to Deep-Dive.

The dashboard remains light/warm with readable buttons and compact headline cards.

## Tests and CI

tests/test_topic_fetcher.py checks:
- Deep-Dive desk list
- Sports option preservation
- non-Sports pill structure
- cricket query specificity
- cricket reference-page rejection
- niche sports breadth

.github/workflows/test.yml:
- installs runtime dependencies plus pytest
- runs unit tests
- performs a real Regional Cricket fetch and requires India/Pakistan/Sri Lanka
- requires at least 5 Pakistan headlines and 5 Sri Lanka headlines
- prints the returned India cricket headlines for manual quality inspection in the CI log
- performs real Niche Sports, News and Technology fetches
- verifies returned pills belong to configured structures

CI validates technical behaviour and provides a real editorial-quality smoke sample; it does not replace manual QC.

## Current files

- PROJECT_CONTEXT.md — complete current state and rules
- topic_fetcher.py — Topic Fetcher
- app.py — Test dashboard
- tests/test_topic_fetcher.py — focused tests
- .github/workflows/test.yml — CI and real-fetch smoke tests
- requirements.txt — runtime dependencies
