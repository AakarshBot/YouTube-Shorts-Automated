# YouTube Shorts Automated — Project Context

This file is the source of truth for this repository.

**Mandatory:** Read this file in full before every edit. Update it after every improvement so it describes the current build accurately.

## Governing rules

### Test first, Live second
The factory has exactly two pipelines:
- **Test:** new functions are built and proven here first.
- **Live:** only approved functions are stitched together.

For every change:
1. Build or change the function in Test.
2. Test it independently.
3. Get user approval.
4. Move the approved function into Live.
5. Verify the Live handoff.

Never skip Test or build a separate unapproved Live implementation.

### No wrappers
Never add wrappers, adapters, compatibility layers, proxy functions or scaffolding around factory code.
When code needs to change, replace the old implementation cleanly. Keep the implementation direct and compact.

### Source and dependency rule
`ranahaani/GNews` is the approved source package for Google News retrieval.

Use the maintained **GNews Python package** through normal imports such as:
```python
from gnews import GNews
```

Do not copy the GNews repository's implementation into this repository. Do not build a custom Google News RSS/API client when the package already provides the required retrieval.

`AakarshBot/Final-Shorts` is reference material only. Do not copy its code, modules or architecture.

## Factory flow

**Choose topic → Script → Audio + subtitles → Choose visuals → Render → Metadata QC → Automatic upload**

All production lines use the same seven factory stages. New behaviour is built in Test before Live.

Current Test production line:
**Deep-Dive**

Planned later:
**Top-5, OTD, and other lines**

Current sports desks:
1. Cricket — India / Pakistan / Sri Lanka / Asia
2. Cricket — Global
3. Niche Sports — Global

## Current development status

### Step 01 — Topic Fetcher
**Status: Test implementation in progress. Not user-approved yet.**

Requirements:
- Return **20 unique topic pills** for each current sports desk when the source pool supports it.
- Fetch substantially more than 20 headlines so filtering and grouping do not unnecessarily shrink the pool.
- Prefer fresh stories with strong current coverage.
- Prefer the most recent 24 hours when that can supply 20 distinct topic groups; otherwise use the full 72-hour discovery pool.
- Remove obvious utility content such as schedules, fixtures, standings, scorecards, watch guides, predicted lineups, galleries, quizzes and similar non-story pages.
- Avoid stale recap/review material when it adds no new development.
- Group related headlines under an entity/topic pill without making the final editorial choice.
- A person/entity pill may contain multiple different current stories about that person/entity because final selection is manual.
- Preserve for each headline: title, source URL, publisher and publication time.
- English only for the first implementation. Language support comes later.
- The Topic Fetcher is a discovery tool; manual QC chooses the actual story.

### Topic Fetcher implementation
`topic_fetcher.py` is a compact factory-specific consumer of the maintained `ranahaani/GNews` package.

Architecture:
**GNews → concurrent query discovery → cleanup → freshness selection → entity grouping/deduplication → simple ranking → 20 topic pills**

Current implementation:
- Uses `GNews(language="en", country="IN", max_results=100)`; the 3-day window is expressed in each discovery query..
- Runs the configured genre queries concurrently.
- Uses the package's `get_news()` method directly; there is no `_google()` or equivalent retrieval wrapper.
- Uses only lightweight local Python logic for cleanup, entity extraction, related-headline detection and ranking.
- Runtime dependencies for Topic Fetcher are only `gnews` plus the dashboard's `streamlit` dependency.
- Does not make an AI classification call.
- Does not use GDELT.
- Does not implement a custom Google News client.
- Keeps one direct `fetch_topics()` entry point for the dashboard handoff.

Current query coverage deliberately over-fetches across:
- India / Asia cricket
- global cricket
- global niche sports

The result contract is:
```
{
  "topic": "...",
  "headlines": [
    {
      "title": "...",
      "url": "...",
      "publisher": "...",
      "published_at": "..."
    }
  ]
}
```

## Dashboard — Test shell
`app.py` contains the Test navigation:
**Homepage → Test → Deep-Dive → Sports → Genre → Topic Fetcher**
The genre page shows the complete production-stage list, while only Topic Fetcher is active.
Live is intentionally disabled until approved.

## Dashboard UI principles
The dashboard should be:
- professional
- light / warm
- readable
- compact
- minimal decoration
- straightforward Streamlit
- minimal CSS
- easy to edit

Do not copy Final-Shorts UI.

## Step 01 handoff
After manual topic selection, Step 02 must receive at least:
- selected topic/entity
- selected headline
- source URL
- publisher
- publication time
- grouped headline context when available

Do not integrate Step 02 until Topic Fetcher is tested and approved.

## Testing
Focused tests currently cover:
- all three sports genres exist
- entity extraction recognises a named subject such as Virat Kohli
- related headlines can be recognised as the same story

The intended CI checks are:
1. install runtime dependencies
2. run focused pytest tests
3. run a real smoke test for all three sports desks
4. assert each desk can return 20 topic pills

The environment available to ChatGPT cannot perform the public-news fetch itself, so the real-fetch smoke result must be verified by GitHub Actions.

Passing tests alone is not editorial approval. The returned stories must still be manually inspected.

## Repository state
This is a clean rebuild.

Current files:
- `PROJECT_CONTEXT.md`
- `requirements.txt`
- `topic_fetcher.py`
- `app.py`
- `tests/test_topic_fetcher.py`
- `.github/workflows/test.yml`

No Live implementation has been built.

## Current cleanup baseline
- Topic Fetcher was rewritten cleanly instead of patched.
- The previous custom GDELT fallback was removed.
- The previous `_google()` and `_gdelt()` retrieval wrappers were removed.
- Unused dashboard CSS and the duplicate GNews period argument were removed.
- The implementation now depends directly on the maintained `gnews` package for Google News retrieval.
- `requirements.txt` contains only the dependencies currently needed by the rebuilt Test shell: `streamlit` and `gnews`.
- No copied code from `ranahaani/GNews` is present.
- No new compatibility layer or wrapper was introduced.