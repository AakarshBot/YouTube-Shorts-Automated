# YouTube Shorts Automated — Project Context

Current source of truth. Read before every edit and replace this file completely after every change; do not append history.

## Rules

- Test first, Live second. Build and approve new functionality in Test before Live.
- No wrappers, adapters, compatibility layers, proxy functions or scaffolding. Delete and rewrite code directly when the current approach is wrong.
- ranahaani/GNews is the approved Google News source. Use the maintained gnews package; do not copy its source or build another news client.
- No new runtime dependencies.
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

## Deep-Dive

Deep-Dive opens into these desks:
- Sports
- News
- Entertainment
- Technology
- Business & Finance
- Gaming
- Science & Space

Sports is the completed desk. The other six desks now have initial Topic Fetcher coverage.

## Topic Fetcher

The fetcher is pill-based. A desk exposes focused top-level pills and each pill expands directly into headline choices.

### Sports

Sports opens three Topic Fetcher choices:
1. Cricket — India / Pakistan / Sri Lanka / Asia
2. Cricket — Global
3. Niche Sports — Global

#### Regional Cricket

Top-level pills are countries:
- India: up to 20 headlines
- Pakistan: target at least 5
- Sri Lanka: target at least 5
- Bangladesh: include when fresh qualifying stories exist
- Afghanistan: include when fresh qualifying stories exist

Each country expands directly to headlines. No player/entity grouping.

Separate GNews country settings are used for IN, PK, LK, BD and AF. Cricket title filtering prevents non-cricket stories from entering these desks.

Regional Cricket prefers the newest 24 hours and may use a 72-hour fallback only when India/Pakistan/Sri Lanka is below target.

#### Global Cricket

Country pills:
Australia, England, South Africa, New Zealand, Ireland and Zimbabwe.

A country pill is created only when it has a fresh qualifying headline within 24 hours.

#### Niche Sports

Sport pills:
Football, Tennis, Basketball, Athletics, Motorsport, Badminton, Hockey, Golf, Boxing, Wrestling, Swimming, Rugby, Volleyball, Cycling, Baseball and Table Tennis.

Cricket is excluded. Only fresh qualifying stories create sport pills.

### News

Four top-level pills:
- India
- World
- Politics & Policy
- Major Events

Queries are one fresh GNews search per pill, run concurrently. India-focused pills use IN; global pills use US localisation.

### Entertainment

Four top-level pills:
- Indian Film & OTT
- Global Film & TV
- Music
- Celebrities

One fresh GNews search per pill, run concurrently.

### Technology

Four top-level pills:
- AI
- Phones & Gadgets
- Big Tech & Platforms
- Startups & Innovation

One fresh GNews search per pill, run concurrently.

### Business & Finance

Four top-level pills:
- India Markets
- Global Markets
- Companies & Deals
- Economy & Policy

One fresh GNews search per pill, run concurrently.

### Gaming

Four top-level pills:
- Games & Releases
- Esports
- Industry & Platforms
- Hardware

One fresh GNews search per pill, run concurrently.

### Science & Space

Four top-level pills:
- Space
- Science & Research
- Environment & Climate
- Major Discoveries

One fresh GNews search per pill, run concurrently.

## Common Topic Fetcher rules

- Freshness target is the newest 24 hours for all desks except the documented Regional Cricket fallback.
- Remove schedules, fixtures, standings, scorecards, watch guides, predicted lineups, galleries, photos, quizzes, odds, recaps, round-ups, reviews and similar utility material.
- Preserve title, URL, publisher and publication time.
- English only.
- Final story selection is manual.
- Search 20 more excludes URLs already shown and merges unseen headlines back into the existing pills.
- First fetch uses up to 20 results per GNews search; Search 20 more can request up to 40 to expose unseen results.
- At most 8 GNews requests run concurrently.
- GNews retries rate-limit responses once.
- No cache, alternate news service or extra runtime dependency is used.

## Test dashboard

Flow:
Homepage → Test → Deep-Dive → Desk → Topic Fetcher.

Sports:
Deep-Dive → Sports → Cricket / Global Cricket / Niche Sports → Topic Fetcher.

Non-Sports:
Deep-Dive → News / Entertainment / Technology / Business & Finance / Gaming / Science & Space → Topic Fetcher.

The Topic Fetcher screen starts with Fetch stories and then shows Search 20 more.

The dashboard remains light/warm with readable buttons and compact headline cards.

## Tests and CI

tests/test_topic_fetcher.py checks:
- Deep-Dive desk list
- Sports option preservation
- non-Sports pill structure
- cricket query design
- niche sports breadth

.github/workflows/test.yml:
- installs runtime dependencies plus pytest
- runs the unit tests
- performs real fetch checks for Regional Cricket and Niche Sports
- performs representative real fetch checks for News and Technology
- verifies returned pills belong to the configured desk structures

CI is technical validation only. Stories still require manual QC.

## Current files

- PROJECT_CONTEXT.md — complete current project state and rules
- topic_fetcher.py — Topic Fetcher
- app.py — Test dashboard
- tests/test_topic_fetcher.py — focused tests
- .github/workflows/test.yml — CI and real-fetch smoke tests
- requirements.txt — runtime dependencies
