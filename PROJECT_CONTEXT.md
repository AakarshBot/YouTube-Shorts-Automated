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

Current requirements:

- Return **20 unique topic pills** for each of the three sports genres.
- Fetch substantially more than 20 headlines so filtering and grouping do not shrink the final pool.
- Prefer new stories with strong current coverage and viral potential.
- Use freshness and publisher/story coverage as simple proxies; do not add a complicated trend system.
- Group headlines under an entity/topic pill where practical.
- A person/entity pill may contain different current stories about that person/entity because final selection is manual.
- Remove obvious utility content such as schedules, fixtures, standings, scorecards, watch guides, predicted lineups, galleries, quizzes and similar non-story pages.
- Avoid stale tournament recap/review material when the competition finished earlier and there is no genuinely new development.
- Use a dynamic freshness window rather than one rigid publication-age cutoff, while strongly favouring recent stories.
- Use English only for the first implementation. Language support will be added later.
- The user manually chooses the final story; Topic Fetcher does not make the final editorial decision.

### Topic Fetcher implementation

The implementation is written from scratch in `topic_fetcher.py`.

External packages:

- **GNews** for Google News discovery and structured article results.
- **gdeltdoc** for GDELT article discovery when the Google News pool is insufficient.
- **rapidfuzz** for lightweight headline similarity.

The source-access work is intentionally delegated to established packages rather than custom RSS/API clients.

Current discovery:

**Multiple genre queries → large candidate pool → cleanup → entity/topic grouping → simple ranking → 20 pills**

The ranking intentionally stays small and editable. It favours:

- number of relevant headlines in the group
- number of distinct publishers
- freshness of the newest headline

No separate AI classification stage is currently used.

Output contains:

- topic/entity heading
- one or more headlines
- publisher
- publication time
- source URL

Google News may return Google News redirect URLs when using its default RSS backend. Direct URL resolution can be added later only if downstream use shows it is necessary.

## Dashboard — Test shell

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

## Dashboard UI principles

The dashboard is rebuilt from scratch and must not copy Final-Shorts UI.

UI target:

- professional
- light/warm
- readable
- compact
- minimal decoration
- straightforward Streamlit components
- minimal CSS
- easy to edit

## Step 01 handoff

The eventual Topic Fetcher handoff to Step 02 must retain at least:

- selected topic/entity
- selected headline
- source URL
- publisher
- publication time
- grouped headline context when available

Do not integrate Step 02 until Topic Fetcher has been tested and approved.

## Testing

Focused tests currently cover:

- all three sports genres exist
- entity extraction recognises a named subject such as Virat Kohli
- loose headline similarity can recognise closely related headlines as the same story

Before Topic Fetcher can be marked Approved, verify the actual UI and real fetching for all three genres and confirm that each can produce 20 useful, distinct pills.

Code passing tests is not sufficient for approval; actual story quality is the approval criterion.

## Repository state

This is a clean rebuild.

Files currently present:

- `PROJECT_CONTEXT.md`
- `requirements.txt`
- `topic_fetcher.py`
- `app.py`
- `tests/test_topic_fetcher.py`

No Live implementation has been built.
