# YouTube Shorts Automated — Project Context

Current source of truth. Replace this file completely after every project change. Never append history.

## Rules

- Test first, Live second.
- No wrappers, adapters, compatibility layers, proxy functions or scaffolding.
- Delete and rewrite code directly when the current approach is wrong.
- No new runtime dependencies or API services unless explicitly approved.
- Groq is called directly from Scriptwriter. Do not add a Groq SDK or generic request wrapper.
- The local Groq key is read directly from the repo-root .env as GROQ_API_KEY when it is not already in the environment. Never store the key itself in code or CI.
- English only for now.
- Final editorial approval is manual.

## Factory

Formats:
- Deep-Dive
- Top-5
- Did You Know
- Others later.

Seven stages:
Topic Fetcher → Scriptwriter → Audio → Subtitles → Visuals → Renderer → Upload.

Deep-Dive is active. Live remains disabled.

## Topic Fetcher — COMPLETE — 7/10

Do not reopen unless a later requirement or regression requires it.

- Maintained ranahaani/GNews is the approved news source.
- Independent GNews searches run concurrently with no artificial 8-worker ceiling.
- Queries, filters, grouping, story counts, handovers and output fields remain unchanged.
- Every selectable headline carries title, exact source URL, publisher, published_at and GNews description.
- Exact source URLs are preserved; do not lowercase or strip query parameters.
- Do not add Playwright, another news service, a custom Google News client, copied GNews code or another dependency merely to reduce runtime.
- The remaining GNews URL-resolution cost is accepted; sub-20-second first-fetch time is not guaranteed under these constraints.

## Scriptwriter — ACTIVE

The previous Scriptwriter was deleted because it let a chosen YouTube title influence the story.

Core rule:

**Story first. Packaging second.**

The selected Topic Fetcher headline and source evidence are the inputs. No approved YouTube title is supplied to story generation.

### Workflow

Selected Topic Fetcher headline
→ direct publisher-page attempt
→ GNews description fallback when needed
→ one direct Groq generation of the complete Short
→ deterministic validation
→ manual title/version approval.

The generation prompt is explicitly ordered to understand the story first, write the Short second, then package the completed story.

### Story requirements

- Read all available source evidence.
- Determine what actually happened.
- Identify the important facts, people, teams, organisations, events and context.
- Choose the strongest evidence-backed editorial angle independently.
- Write 4 slides normally; use 5 only when necessary.
- Slide 1 spoken narration: fewer than 14 words.
- Total narration: 30-second target, maximum 75 words.
- Every slide adds important information.
- Four slides normally cover roughly 90% of the important source.
- Reorder and synthesise facts; do not mechanically follow source paragraphs.
- Preserve important names, teams, organisations, events and numbers.
- Name central people explicitly.
- If a person's remark is central, identify that person and preserve the remark's meaning and tone.
- Never replace an available name with vague labels such as “a legend”, “a star”, “the veteran” or “the player”.
- Do not let the Topic Fetcher headline dictate the angle.
- Do not turn praise into criticism, advice into a demand, possibility into certainty or a detail into a wider narrative without evidence.
- Do not invent controversy, criticism, pressure, doubts about form, legacy concerns, retirement implications, motives, reactions, stakes or consequences.
- Do not invent facts, statistics, quotes, predictions or conclusions.
- Retention must come from actual facts, context, contrast, consequence, significance or surprise.
- No filler, repetition, generic AI-news language or clickbait.

### Opening screen headline

- Exactly 3 or 4 words.
- Story-specific.
- No filler.
- Separate from spoken narration.

### Packaging

Packaging is created from the completed Short in the same generation.

Every result contains:
- at least two YouTube title options
- one natural description
- relevant hashtags
- one story-specific first/creator comment.

Titles must:
- accurately represent the completed Short
- use genuinely different packaging angles
- put important names and story terms early
- remain concise and natural
- contain no clickbait, fake curiosity, excessive capitals or unnecessary emoji
- introduce no facts absent from the source/story.

The first comment must be specific to the actual story and invite a genuine response. No generic CTA boilerplate.

### Improve / Re-run

- Manual only.
- Never automatic.
- Uses the same source evidence.
- Must create a genuinely different editorial angle or narrative spine.
- Must not merely swap words.
- Original and improved versions stay visible.
- Packaging is regenerated with the improved Short.
- Both versions follow the same factual, slide-count, headline and duration requirements.

### Validation

Python enforces only:
- 4 or 5 slides
- first spoken slide under 14 words
- narration at or below 75 words
- every slide has narration
- opening headline has 3 or 4 words
- duplicate spoken slides rejected
- at least two title options
- description, hashtags and first comment present
- malformed output rejected

Do not add hook scores, angle scores, title-ranking systems, critic passes, claim graphs, personas, automatic rewrite chains, provider routers or other large validation frameworks.

### Source handling

Each selected Topic Fetcher headline carries title, exact URL, publisher, published_at and GNews description.

Scriptwriter:
1. Attempts the exact publisher URL directly.
2. Uses the article element when available; otherwise readable page text.
3. Falls back to the headline plus any non-empty GNews description when the publisher page is blocked, malformed or unreadable.
4. Fails only when no usable publisher text and no usable GNews description exist.
5. Does not decode Google News redirects or add article-extraction dependencies.

### Test dashboard

- Manually select a Topic Fetcher headline.
- Generate the Short first from the source.
- Show the completed script and its generated title options/metadata.
- Manually choose the title.
- Manually approve the version.
- Improve/Re-run is available before approval.
- The approved title is stored for later handoff only. It is never passed into story generation.

## Top-5 — PLANNED

- Cricket-only in the current version.
- Select 5 headlines with URLs/titles/articles.
- Exactly 6 slide headlines.
- Slide 1 under 14 words.
- Slides 2–6 each limited to 15 seconds of speech.
- No generic “5 stories you need to see…” opener.

## Later stages

Audio, Subtitles, Visuals, Renderer and Upload are not active. Preserve their existing functions and handovers unless explicitly requested.

## Current files

- PROJECT_CONTEXT.md — current source of truth.
- topic_fetcher.py — completed Topic Fetcher.
- app.py — Test dashboard.
- scriptwriter.py — source-first Scriptwriter.
- tests/test_topic_fetcher.py — Topic Fetcher tests.
- tests/test_scriptwriter.py — Scriptwriter tests.
- .github/workflows/test.yml — deterministic CI.
- requirements.txt — runtime dependencies.

## CI

CI must not depend on live GNews availability or a minimum current-story count.
Do not merge a red commit.
