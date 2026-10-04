# YouTube Shorts Automated — Project Context

Current source of truth. Read before every edit and replace this file completely after every change; do not append history.

## Rules

- Test first, Live second. Build and approve functionality in Test before Live.
- No wrappers, adapters, compatibility layers, proxy functions or scaffolding. Delete and rewrite code directly when the current approach is wrong.
- ranahaani/GNews is the approved Google News source. Use the maintained gnews package; do not copy its source or build another news client.
- No new runtime dependencies or API services unless explicitly approved.
- AakarshBot/Final-Shorts is reference material only, not a code source.
- English only for now. Language support comes later.
- Final story selection is manual. CI passing is technical validation, not editorial approval.
- Keep code as short and direct as practical. Do not add unnecessary abstractions, calls or dependencies.

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

## Stage status

### Topic Fetcher — COMPLETE — 7/10

Topic Fetcher is complete enough to move to Scriptwriter.

The 7/10 rating is the approved manual-QC rating. Do not reopen or broaden Topic Fetcher work unless a later requirement or regression requires it.

### Scriptwriter — NEXT

Scriptwriter is the next active stage. Implementation and Test work start from the rules below.

## Deep-Dive desks

Deep-Dive opens into:
- Sports
- News
- Entertainment
- Technology
- Business & Finance
- Gaming
- Science & Space

Sports is the completed desk for Topic Fetcher. The six non-Sports desks have initial Topic Fetcher coverage.

## Topic Fetcher — completed behaviour

The fetcher is pill-based. A selected desk exposes focused top-level pills; each pill expands directly into headline choices with title, publisher, publication time and source URL.

### Sports

Sports opens:
1. Cricket — India / Pakistan / Sri Lanka / Asia
2. Cricket — Global
3. Niche Sports — Global

#### Regional Cricket

Country pills:
- India: target 25 title/entity pills. Each pill counts as 1 unit toward the 25 target, regardless of how many headlines it contains. India remains the country pill, with the title/entity pills inside it.
- Pakistan: target at least 5 headlines.
- Sri Lanka: target at least 5 headlines.
- Bangladesh: include when fresh qualifying stories exist.
- Afghanistan: include when fresh qualifying stories exist.

Regional Cricket uses one targeted Google News search per country in the first pass. India uses title/entity grouping to measure its 25-pill target; Pakistan/Sri Lanka use their existing headline targets. India/Pakistan/Sri Lanka can fall back to a 72-hour search only when their targets are not met.

India title/entity grouping:
- Group India cricket headlines into simple pills using repeated meaningful words or phrases from the headlines.
- Generic words such as India, cricket and match are not used as standalone grouping keys.
- A grouped India pill can contain multiple different stories about the same player, tournament or other repeated title entity.
- Unmatched stories remain individual title pills for manual QC.
- A pill containing multiple stories still counts as exactly 1 unit toward the 25-unit target.

India retrieval:
- First fetch uses up to 100 GNews results for India to support the 25 title/entity-pill target.
- Search 20 more can request up to 40 and excludes previously shown URLs.
- GNews applies max_results after fetching the RSS feed, so lowering result counts does not materially reduce network runtime.
- At most 8 GNews searches run concurrently. This is the current safe runtime/rate-limit balance.
- GNews rate-limit retries are limited to one.

#### Global Cricket

Country pills:
Australia, England, South Africa, New Zealand, Ireland and Zimbabwe.

A country pill exists only when it has fresh qualifying headlines within 24 hours.

Global Cricket remains unchanged by the India-specific title/entity grouping.

#### Niche Sports

Sport pills:
Football, Tennis, Basketball, Athletics, Motorsport, Badminton, Hockey, Golf, Boxing, Wrestling, Swimming, Rugby, Volleyball, Cycling, Baseball and Table Tennis.

Cricket is excluded. Only fresh qualifying stories create sport pills.

Niche Sports remains unchanged by the India-specific title/entity grouping.

### Story-quality rules

Reject obvious utility/reference pages such as schedules, fixtures, standings, scorecards, watch guides, predicted lineups, galleries, quizzes, odds, recaps, round-ups and similar pages.

For cricket, also reject explicit database/reference pages containing phrases such as “record & stats”, “records & stats”, “team records”, “career stats” and “cricket grounds”.

The cricket blacklist is deterministic and title-based. It must match these reference phrases without requiring quotation marks in the headline.

Do not add an LLM classifier, article scraper, publisher allowlist, alternate news API, cache layer or additional runtime dependency to Topic Fetcher.

A keyword mention alone is not the retrieval strategy. Queries should be specific enough to favour actual current cricket stories while preserving legitimate broader stories connected to a cricket development.

### Freshness and dedupe

- Freshness target: newest 24 hours.
- Regional Cricket: 72-hour fallback only when India/Pakistan/Sri Lanka misses its target.
- Global Cricket and Niche Sports: no stale-only pills.
- Preserve title, URL, publisher and publication time.
- Normalize URLs before dedupe.
- Search 20 more excludes previously shown URLs and merges unseen headlines into the existing pill.
- No cache or alternate news provider was introduced.
- The Topic Fetcher output uses string timestamps for dashboard compatibility.

## Non-Sports Deep-Dive desks

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

## Topic Fetcher tests and CI

tests/test_topic_fetcher.py checks:
- Deep-Dive desk list.
- Sports option preservation.
- Non-Sports pill structure.
- Cricket query specificity.
- Cricket reference-page rejection.
- Niche sports breadth.
- India title/entity grouping.
- Grouped India timestamps remain strings.

.github/workflows/test.yml:
- Installs runtime dependencies plus pytest.
- Runs unit tests.
- Performs a real Regional Cricket fetch and requires India/Pakistan/Sri Lanka.
- Requires at least 25 India title/entity pills, 5 Pakistan headlines and 5 Sri Lanka headlines.
- Prints returned India cricket title/entity pills and their headlines for manual inspection in the CI log.
- Performs real Niche Sports, News and Technology fetches.
- Verifies returned pills belong to configured structures.

CI is technical validation plus a real retrieval smoke sample. It is not editorial approval.

## Scriptwriter rules — next stage

The Scriptwriter takes a manually selected source story from Topic Fetcher and turns it into a YouTube Short script.

### Core rules

- First slide must contain fewer than 14 words.
- The fewer-than-14-word rule applies only to the first slide. It is not a rule for the whole script and is not a speech-duration rule.
- The entire Short must be under 30 seconds.
- Every slide must contain important information. No filler slides.
- Do not invent facts, context, quotes, events, statistics or conclusions that are not supported by the source material.
- Do not simply repeat or stretch the headline.
- The script must capture the actual facts of the story.
- Four slides should cover roughly 90% of the important information in the source article.
- Four to five slides are acceptable. Do not force the script into unnecessarily compact or tiny slides.
- A single source article is acceptable.
- Related current/trending information may be added when it materially helps explain the story and is reliable.
- An AI/API coverage step may be used when it materially improves factual coverage, but it must not add unnecessary calls, cost, runtime or complexity.
- Slightly exceeding 30 seconds is not acceptable as a target; if audio later runs only slightly over because of natural speech timing, a modest speed-up is acceptable.
- Do not use generic AI-style framing, filler hooks or manufactured commentary such as “this changes the game”, “the sports world is reacting”, “a moment fans won't forget” or similar language unless the source itself supports it.
- The output must be factual, direct and useful to a sports/news audience.
- Manual QC remains the final editorial gate.

### Required Scriptwriter output

For each selected story, output:
- Slide-by-slide script.
- YouTube title.
- YouTube description.
- Hashtags.

The title and description should describe the actual story. Do not manufacture clickbait or add claims not supported by the source.

### Script structure

Preferred shape:
- Slide 1: concise factual hook, fewer than 14 words.
- Slides 2–4: the core facts, covering the bulk of the article.
- Slide 5: optional only when it adds a necessary fact and still keeps the full Short under 30 seconds.

Every slide needs a fact or meaningful piece of context.

### Scriptwriter validation

Validation should check:
- First slide word count is below 14.
- Total script duration/estimated speech stays below 30 seconds.
- Every slide contains substantive narration.
- The script does not merely echo the source headline.
- The script covers the key facts from the source.
- No unsupported facts are introduced.
- Required title, description and hashtags are present.

Do not add scene-duration rules that are unrelated to the first-slide word-count rule. The first-slide limit is a word-count constraint, not a “first scene under X seconds” constraint.

## Top-5

Top-5 is planned but not the next active stage.

Current approved direction:
- Cricket-only for the current version.
- Select 5 headlines with URLs/titles/articles.
- Script exactly 6 slide headlines.
- Slide 1 fewer than 14 words.
- Slides 2–6 each limited to 15 seconds of speech.
- Do not use generic filler such as “5 stories you need to see…”.
- Existing cricket audio generation code is the intended audio path when Top-5 work resumes.

## Audio, Subtitles, Visuals, Renderer and Upload

These stages are not the current active task. Preserve existing functions and handovers unless explicitly requested.

## Current files

- PROJECT_CONTEXT.md — complete current state and next-stage rules.
- topic_fetcher.py — completed Topic Fetcher.
- app.py — Test dashboard.
- tests/test_topic_fetcher.py — Topic Fetcher tests.
- .github/workflows/test.yml — CI and real-fetch smoke tests.
- requirements.txt — runtime dependencies.
