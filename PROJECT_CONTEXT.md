# YouTube Shorts Automated — Project Context

Current source of truth. Replace this file completely after every project change. Never append history.

## Rules

- Test first, Live second.
- No wrappers, adapters, compatibility layers, proxy functions or scaffolding.
- Delete and rewrite code directly when the current approach is wrong.
- No new runtime dependencies or API services unless explicitly approved.
- Groq is called directly from Scriptwriter. Do not add a Groq SDK or generic request wrapper.
- The local Groq key is read directly from the repo-root .env as GROQ_API_KEY when it is not already in the environment. Never store the key itself in code or CI. Groq requests use a browser-style User-Agent because the API edge can reject bare Python urllib clients with Cloudflare error 1010.
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

## Scriptwriter — SPEC LOCKED / IMPLEMENTATION UNDER TEST

The selected Topic Fetcher headline is sent to Scriptwriter as the story to investigate.

### Core editorial rule

**Understand the full story first. Rewrite the Short from scratch second. Package it third.**

The writer must:
- Read the available source material.
- Understand what actually happened.
- Find the most interesting part of the story that can genuinely become a Short.
- Choose one strongest editorial angle.
- Rewrite the narration from scratch after understanding the story.
- Never simply expand, paraphrase or prolong the Topic Fetcher headline.
- Use the Topic Fetcher headline as the starting subject, not as a finished script or approved YouTube title.

### Source workflow

Primary run:
1. Read the exact Topic Fetcher source URL.
2. Use readable article text when available; fall back to the Topic Fetcher GNews description when necessary.
3. Ask the model whether the available evidence is enough to make a genuine Short.
4. If enough, generate the complete Short and all packaging.
5. If not enough, return status=needs_more_sources with a concise reason and no script/packaging.

Automatic additional-source run:
- Only happens when the primary evidence is not enough.
- Uses the existing GNews dependency already used by Topic Fetcher.
- Searches for related reporting from the selected headline.
- Reads the usable results and combines them with the primary evidence.
- Generates the Short from the combined sources.
- Does not perform another automatic search after this pass.

Manual additional-source run:
- If the combined primary + automatic sources are still insufficient, the dashboard asks the user for additional source URLs.
- The dashboard accepts multiple URLs, one per line.
- The writer reads usable manual URLs and combines them with all previously collected sources.
- This is the second and final additional-source run.
- If the combined evidence is still insufficient, stop and tell the user that there is not enough information to create a genuine Short.
- Do not invent a script, titles, description, hashtags or comment just to produce an output.

If the primary source itself is unreadable, the automatic related-source run still happens rather than failing immediately.
- Source-reading failures are distinct from Groq/generation failures. API, structured-output and generation errors must surface as actual errors; they must never be treated as evidence that the story is insufficient.
- A failed automatic related-source request must also surface as an actual error; it must not be silently converted into a “not enough story” state.

### Story rules

- The final Short can use one source or multiple supporting sources.
- Multiple sources may be synthesised when they support the same story.
- Choose one strongest angle rather than combining unrelated angles.
- Use as many slides as the story needs. There is no fixed slide count.
- Every slide must add important information.
- Do not create filler, repetition or artificial sentence splits just to increase slide count.
- Slide 1 spoken narration must contain fewer than 14 words.
- Total spoken narration must be 65 words or fewer. This is the Scriptwriter proxy for a Short under 30 seconds.
- The Audio stage may slightly speed the final voice when the finished audio is only marginally above 30 seconds.
- Retention should come from real facts, context, contrast, consequence, significance or surprise in the sources.
- Capture the important facts, context, names, teams, organisations, events, numbers and remarks needed to understand the story.
- Reorder and synthesise facts as needed; do not mechanically follow article paragraphs.
- Do not invent facts, statistics, quotes, reactions, motives, criticism, controversy, pressure, predictions or consequences.
- Preserve the meaning and tone of important remarks.
- If a person is identified in the source, use their proper name.
- If a source calls someone a legend, icon, veteran or similar and the identity is known, the writer must still name the person properly in the Short. Never replace a known person's name with a generic label.

### Opening screen headline

- Exactly 3 or 4 words.
- Story-specific.
- Separate from the spoken Slide 1 narration.

### Packaging

When the status is ready, the same Scriptwriter generation also produces:
- At least two YouTube title options.
- One natural description.
- Relevant hashtags.
- One story-specific first/creator comment.

Packaging is written only after the completed Short is understood.

Titles must:
- Accurately represent the completed Short.
- Use genuinely different packaging angles.
- Put important names and story terms early.
- Remain concise and natural.
- Contain no clickbait, fake curiosity, excessive capitals or unnecessary emoji.
- Introduce no unsupported facts.

Description:
- Explain the actual story naturally.
- Add no unsupported facts.

Hashtags:
- Relevant only.

First comment:
- Specific to the story.
- Invites a genuine response.
- No generic CTA boilerplate.

### Improve / Re-run

- Manual only.
- Available before approval.
- Uses the same source evidence already collected.
- The previous version is supplied to the writer for comparison.
- The new version must use a genuinely different editorial angle or narrative spine.
- It must not merely swap words, reorder sentences or lightly rephrase the same script.
- The improved version follows all normal story, timing, slide, factual and packaging rules.
- Original and improved versions remain visible for manual QC.
- Approved title/version is never supplied to story generation.

### Output

A ready result contains:
- opening_headline
- slide-by-slide voiceover
- multiple YouTube title options
- description
- hashtags
- first/creator comment

A non-ready result contains:
- status=needs_more_sources
- a concise reason
- no script or packaging.

### Deterministic validation

Python enforces only the rules that are objective:
- Ready output has at least one slide.
- Slide 1 has fewer than 14 words.
- Total narration is 65 words or fewer.
- Every slide has spoken narration.
- Opening headline has 3 or 4 words.
- Duplicate spoken slides are rejected.
- At least two title options exist.
- Description, hashtags and first comment exist.
- status=needs_more_sources requires a reason.
- Malformed output is rejected.

Do not add hook scores, angle scores, source-coverage scores, critic passes, claim graphs, personas, automatic rewrite chains, title-ranking systems, provider routers or other large validation frameworks.

## Test dashboard

The Scriptwriter test flow is:

1. Manually select a Topic Fetcher headline.
2. Scriptwriter reads the primary source and builds the Short from scratch.
3. If the primary source is insufficient, Scriptwriter automatically searches related GNews sources once.
4. If the combined evidence is still insufficient, dashboard asks for additional source URLs.
5. User can paste multiple URLs, one per line.
6. Scriptwriter performs the manual-source run using the new URLs plus all previously collected evidence.
7. If the story is still not sufficient after that second additional-source run, dashboard stops with a clear Not enough information to create a Short message and the writer's reason.
8. When ready, dashboard shows only the completed script and packaging needed for QC; raw article text is not displayed.
9. Dashboard shows opening headline, every slide, total source count, title options, description, hashtags and first comment.
10. User manually chooses a title and approves the version.
11. Improve / Re-run is available before approval.

The selected Topic Fetcher headline remains the starting story input. The approved title is stored for later handoff only and is never passed into Scriptwriter generation.

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
- app.py — Test dashboard and Scriptwriter flow. Dashboard logic is kept direct; no Scriptwriter wrapper/helper functions.
- scriptwriter.py — source-first Scriptwriter under test.
- tests/test_topic_fetcher.py — Topic Fetcher tests.
- tests/test_scriptwriter.py — Scriptwriter tests.
- .github/workflows/test.yml — deterministic CI.
- requirements.txt — runtime dependencies.

## CI

CI must not depend on live GNews availability or a minimum current-story count.
Do not merge a red commit.
