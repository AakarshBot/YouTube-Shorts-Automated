# YouTube Shorts Automated — Project Context

This file is the source of truth for this repository.

**Mandatory:** Read this file in full before every edit. Update this file after every improvement so it accurately describes the current build.

## Governing rules

### 1. Test first, Live second

The factory has exactly two pipelines:

- **Test:** every new function is built and proven here first.
- **Live:** only approved functions are stitched together here.

For every change:

1. Build or change the function in Test.
2. Test it independently.
3. Get user approval.
4. Move the approved function into Live.
5. Verify the Live handoff.

Never skip Test or build a separate unapproved Live implementation.

### 2. No wrappers

Never add wrappers, adapters, compatibility layers, proxy functions, or scaffolding around factory code.

When code needs to change, delete the old implementation and rewrite it cleanly when necessary.

Keep implementations direct and compact.

### 3. No code from Final-Shorts

`AakarshBot/Final-Shorts` is reference material only.

Do not copy its code, modules, functions, architecture, runtime imports, schemas, or implementation patterns.

All factory code in this repository is written from scratch.

External open-source packages may be installed and imported when they are the best existing solution. They are dependencies, not copied code.

## Factory flow

The production concept is:

**Choose topic → Script → Audio + subtitles → Choose visuals → Render → Metadata QC → Automatic upload**

The factory will support multiple production formats. Current Test format:

**Deep-Dive**

Planned later: **Top-5, Did You Know, and more.**

Current Test genre:

**Sports**

Planned later: News, Tech, Business, Entertainment, Science and other areas.

Sports genres currently defined:

1. Cricket — India / Pakistan / Sri Lanka / Asia
2. Cricket — Global
3. Niche Sports — Global

When a sports genre is opened, the full factory stage list is shown. Only the function currently under development is active.

## Current development status

### Step 01 — Topic Fetcher

**Status: Test implementation in progress. Not user-approved yet.**

Current goal:

- Return **20 unique topic pills** for each of the three sports genres.
- Fetch substantially more than 20 headlines so filtering and grouping do not shrink the final pool.
- Prefer fresh stories with strong current-news/coverage signals.
- Do not fill the pool with weak or clearly stale material.
- Group multiple headlines around the same entity/topic into one pill.
- A person/entity pill may contain different current stories about that person/entity. Manual QC makes this acceptable.
- Different real-world events involving the same person/team may therefore remain inside the same entity pill.
- Remove obvious utility content such as schedules, fixtures, standings, scorecards, watch guides, predicted lineups, galleries, quizzes and similar non-story pages.
- Avoid stale tournament recap/review material when the underlying competition ended earlier and there is no new development.
- Use English only for the first implementation. Language support will be added later.
- The user manually chooses the final story; Topic Fetcher does not need to make the final editorial decision.

### Topic Fetcher implementation

The implementation is written from scratch in `topic_fetcher.py`.

Current external dependencies:

- **GNews** for Google News discovery and structured article results.
- **gdeltdoc** for GDELT article discovery when the Google News pool is insufficient.
- **rapidfuzz** for lightweight headline similarity.

The code intentionally keeps source access inside these established packages instead of implementing custom RSS/API clients.

Current discovery approach:

**Multiple broad genre queries → large candidate pool → basic cleanup → entity/topic grouping → simple freshness/source/coverage ranking → 20 pills**

The first version deliberately avoids a separate complex trend engine, expensive AI classification stage, or elaborate ranking framework.

The output of Topic Fetcher contains:

- topic/entity heading
- one or more headlines
- publisher
- publication time
- source URL

The source URL returned by Google News may be a Google News redirect URL when using the default RSS backend. Direct URL resolution can be addressed later if testing shows it is required for the downstream Scriptwriter.

### Dashboard — Test shell

`app.py` contains the new Test navigation only:

**Homepage**
→ Test / Live

**Test**
→ Deep-Dive

**Deep-Dive**
→ Sports

**Sports**
→ the three current sports genres

**Genre**
→ Topic Fetcher → Scriptwriter → Audio → Subtitles → Visuals → Renderer → Metadata QC → Upload

Only Topic Fetcher is active.

Live is intentionally disabled and has not been connected to the new function.

### Dashboard UI principles

The dashboard is being rebuilt from scratch.

Do not copy Final-Shorts UI.

UI should be:

- professional
- light/warm
- readable
- compact
- easy to edit
- low in unnecessary visual decoration
- built with straightforward Streamlit components and minimal CSS

## Step 01 handoff

The intended handoff after the user selects a topic is a clean story package for Step 02.

At minimum it must retain the selected headline, source URL, publisher and publication time, plus the topic/entity grouping context when available.

Do not integrate Step 02 until Topic Fetcher has been tested and approved.

## Testing rule

Functional changes should have focused tests.

Before calling Step 01 complete, verify:

- the three sports genres load
- Topic Fetcher imports correctly
- filtering/grouping logic works
- the UI can request and display the returned topic pills
- real fetching is able to produce the intended 20-topic pool

Do not mark Topic Fetcher Approved merely because the code runs. Approval depends on the quality of the actual returned stories.

## Current repository state

This is a clean rebuild.

Do not import anything from Final-Shorts.

Current files:

- `PROJECT_CONTEXT.md`
- `requirements.txt`
- `topic_fetcher.py`
- `app.py`
- `tests/test_topic_fetcher.py`

No Live implementation has been built yet.
