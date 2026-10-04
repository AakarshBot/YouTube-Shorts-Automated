# YouTube Shorts Automated — Project Context

Current source of truth. Read before every edit and replace this file completely after every change; do not append history.

## Rules

- Test first, Live second. Build and approve functionality in Test before Live.
- No wrappers, adapters, compatibility layers, proxy functions or scaffolding. Delete and rewrite code directly when the current approach is wrong.
- ranahaani/GNews is the approved Google News source. Use the maintained gnews package; do not copy its source or build another news client.
- No new runtime dependencies or API services unless explicitly approved. The local Groq key is read directly from the repo-root `.env` as `GROQ_API_KEY` when it is not already present in the environment; normal `.env` spacing, optional `export` and UTF-8 BOM are accepted; never store the key itself in code or CI. Groq calls use only the API's required `Authorization` and `Content-Type` headers.
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

#### Runtime optimisation

- Editorial behaviour remains unchanged: the same queries, filters, grouping, story counts, handovers and output fields are retained.
- Independent GNews pill searches now run concurrently with no artificial 8-worker ceiling.
- The main remaining runtime cost is inside maintained GNews 0.8.2: RSS result processing attempts Google News URL resolution for returned articles, including an HTTP HEAD request per article when Playwright is unavailable.
- Do not add Playwright, another news service, a custom Google News client or copied GNews code merely to reduce runtime.
- A sub-20-second first fetch cannot be guaranteed from application-side concurrency alone while those constraints remain.

### Scriptwriter — ACTIVE

The current Scriptwriter work is limited to the Scriptwriter Test page.

The Test dashboard is sequential: manually selecting a headline in Topic Fetcher is the Scriptwriter trigger. Standalone Scriptwriter tests will only be added when explicitly requested.

The Test page first generates title options for the selected story and presents them in a dropdown. The user manually approves one title. Only after that approval is the opening screen headline and spoken script generated.

Groq requests are made directly inside the two generation functions; no generic API wrapper or Groq client dependency is used.

### Non-negotiable editorial rules

- The first spoken slide must contain fewer than 14 words.
- The fewer-than-14-word rule applies only to the first spoken slide. It is a word-count rule, not a scene-duration rule.
- The Short uses 4 or 5 slides. Choose 4 when the story can be told completely in 4; use 5 only when the fifth slide adds necessary information.
- The Scriptwriter must target a total narration time at or below 30 seconds. A 1-second technical buffer is acceptable. A script that lands roughly 2 seconds over may be rescued later with a modest TTS speed-up, but exceeding 30 seconds is never the intended writer output.
- Every slide must add important information. No filler, repetition or slides that exist only to bridge time.
- The source article is evidence, not the script. Do not simply rephrase, compress or follow the article paragraph-by-paragraph.
- Write the story from scratch using the supported facts. Reorder information, choose a stronger editorial angle, synthesise related details and decide what matters most to the viewer.
- Editorial value must come from factual selection, synthesis, context, contrast, consequence, significance or a useful human angle. Do not invent facts, motives, quotes, statistics, predictions, reactions or conclusions to make the story more interesting.
- Slide 1 must function as the retention opening: immediately give the strongest supported fact, tension, surprise, result, consequence or other compelling angle.
- Later slides must continue retention by introducing new, useful information and creating forward momentum. Retention must never depend on withholding the answer or using fake curiosity.
- Four slides should normally cover roughly 90% of the important information in the source. A fifth slide is only for necessary information that cannot be cleanly included earlier.
- The writing should have personality without becoming casual or unprofessional: confident, sharp, human, natural, varied and editorially distinctive.
- Prefer strong verbs, clean spoken phrasing and specific language over generic AI-news wording.
- Avoid generic AI-style framing, manufactured hype, clickbait, empty superlatives, forced jokes and phrases such as “this changes the game”, “the sports world is reacting” or “a moment fans won't forget” unless the supplied evidence genuinely supports the statement.
- Curiosity should come from a real supported detail, not from telling the viewer to wait for a reveal.
- Do not copy complete sentences from the source. Paraphrase and synthesise while preserving the actual meaning.
- A single source article is acceptable. Related current information may be used only when it materially improves understanding and is reliable; it must not become an unnecessary research or API chain.
- The writer must make the strongest complete first draft in one generation. Do not design the factory around automatic rewrite/repair loops.
- Manual QC remains the final editorial gate.

### Required output

Every first-run Scriptwriter result must contain all of these:

- Opening screen headline: exactly 3–4 words, strictly about the selected story, zero filler words. It is large screen text shown during the first second of Slide 1 and is separate from the spoken narration.
- Slide-by-slide spoken script: 4 or 5 slides.
- Multiple YouTube title options in meaningfully different editorial angles, with each title accurate, concise, Shorts-appropriate and based on the actual story.
- One YouTube description that explains the actual story clearly and naturally.
- Relevant hashtags only; no filler hashtags.
- One first/creator comment designed to start a genuine conversation about this specific story.

### YouTube title options

The Scriptwriter must generate multiple title options rather than one title.

- Each option must accurately represent the selected story and must not add unsupported claims.
- Options should use genuinely different packaging angles rather than superficial word swaps.
- The model should consider a mix of strong Shorts-friendly approaches such as direct factual/result-led, consequence-led, and intrigue-led framing where the story supports them.
- Titles should remain concise and put the most important story words early.
- Avoid clickbait, misleading framing, excessive ALL CAPS and unnecessary emoji.
- The dashboard will show all generated title options so the user can choose the strongest one during QC.
- There is no fixed number of title options. Generate and show as many as make editorial sense for the story, then let manual QC choose one.

### First/creator comment

The first comment is an editorial output, not a generic CTA.

- It should be based on the actual story and give viewers an easy reason to respond.
- Prefer a specific question, judgement call, comparison or implication that arises naturally from the facts.
- It must not default to generic prompts such as “What do you think?” or “What do you make of this?” when a stronger story-specific question is possible.
- Do not automatically append “subscribe for more” or similar boilerplate.
- The comment should sound like a human editor opening a conversation, not an automated engagement prompt.
- Generate a story-specific first/creator comment. Do not use a mechanical fallback or generic engagement boilerplate.

### Improve Script behaviour

The dashboard will provide an Improve/Re-run option after the first draft.

- Improve is a user-requested second editorial version, not an automatic response to a validation failure and not a correction loop.
- The original draft and the improved draft must both remain visible on the dashboard.
- The user selects which version to keep.
- A re-run must re-read the same source evidence and produce a genuinely different editorial angle or narrative spine.
- Avoid simply changing words while preserving the same structure and opening.
- Preserve the same factual, slide-count, headline, packaging and duration requirements.
- Keep the previous draft only as context for what should not be repeated; the original source remains the factual authority.
- Valid angle changes can include result-led, pressure-led, consequence-led, conflict/response-led, comparison-led, human-angle-led or another evidence-backed approach that materially changes the storytelling.
- Title options and the first comment should also be regenerated to fit the new angle rather than copied from the original version.

### Scriptwriter intelligence and validation

The model should satisfy the editorial brief before returning the first result. Python should enforce only a small set of objective requirements:

- Valid structured output.
- 4 or 5 spoken slides.
- First spoken slide under 14 words.
- Total estimated narration at or below the writer's 30-second target.
- Every slide contains substantive narration.
- Opening screen headline is exactly 3–4 story-specific words with no filler.
- Multiple title options, description, hashtags and first comment are present.
- Basic obvious-quality checks such as empty fields, gross slide duplication, clear retention-bait phrasing and unsupported numeric details may be rejected.

Do not add hook-scoring systems, editorial-angle scoring systems, title-ranking systems, personas, critic passes, automatic rewrite chains, provider routers, source-claim graphs or other large validation frameworks unless a later requirement proves one is necessary.

The Scriptwriter should not constantly fail on secondary factory rules after generation. The prompt and structured output contract should be strong enough that the normal first run already satisfies the intended editorial product.

### Source handling

Topic Fetcher is the source-of-truth handoff for Scriptwriter. Each selected headline must carry:
- title
- URL
- publisher
- published_at
- GNews description/summary

The complete source URL is preserved for navigation and fetching. Query parameters and URL casing must not be stripped or normalised away. Topic Fetcher stores that exact URL on the selected headline.

Scriptwriter does not depend on Google News URL decoding and does not require a publisher page to be reachable. On selection:
1. Try the supplied source URL with a normal direct HTTP request.
2. Use the page's article element when available; otherwise use readable page text from the page.
3. If the publisher returns an HTTP/network error, the URL is malformed, or the page contains insufficient readable text, use the Topic Fetcher's GNews description together with the selected headline as the factual source evidence.
4. Do not impose an arbitrary minimum character count on the GNews description. Any non-empty GNews description is usable fallback evidence.
5. Only fail when there is no readable publisher text and no usable GNews description.

This makes source handling universal across desks without adding Playwright, a URL-decoder package, an article-extraction dependency or another API service. A publisher blocking automated requests must not stop the Scriptwriter from producing a factual first draft from the evidence already supplied by Topic Fetcher.

### Scriptwriter architecture for the current Test page

Selected Topic Fetcher headline + GNews description → attempt publisher page → use article/page text when readable or GNews evidence when not → title options → manual title approval → one structured Scriptwriter generation → minimal deterministic validation → Test-page preview.

If the title model returns no usable options, show an error and require a user-triggered retry; do not loop automatically.

Improve/Re-run uses the same selected story/source and approved title, produces a genuinely different editorial angle, and keeps the original and improved versions available for manual selection.

The current Test page generates and previews only the approved title, opening screen headline and spoken script. Description, hashtags and first/creator comment are deferred to Upload QC.

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
- tests/test_scriptwriter.py — Scriptwriter objective validation tests.
- .github/workflows/test.yml — CI with deterministic syntax and unit checks.
- requirements.txt — runtime dependencies.


### CI notes for current Scriptwriter work

- Scriptwriter objective tests cover the first-slide word limit, slide count, duration target, headline format and duplicate-slide rejection.
- Source-handling tests cover successful publisher reads, HTTP 400 fallback, pages without an article element, malformed source URLs and missing-evidence failure.
- The current universal source handoff does not decode Google News redirects and does not depend on publisher access succeeding.
- Do not add publisher-specific parsers, Google News-specific redirect logic, Playwright, trafilatura or other runtime dependencies unless explicitly approved.
- Topic Fetcher must pass title, URL, publisher, published_at and GNews description for every selectable headline on every desk.
- Source URLs must not be lowercased or stripped of query parameters because the exact URL can be required to reach the intended page.
- The previous failure caused by an arbitrary 80-character fallback-description threshold has been removed.
- The last successful CI run was before this cleanup commit; CI must pass the current `main` commit before this state is considered technically approved.
- The dashboard keeps only state required for navigation, source handoff, title approval, script versions and manual QC; duplicate `desk` and `title_choice` state has been removed.
- Title-generation retry reuses an already-fetched source when available, and script-generation errors retain the approved title so the user-triggered retry remains usable.
- Do not add browser-spoofing headers, a Groq SDK dependency or retry/repair layers solely to work around Cloudflare error 1010; treat an HTTP 403/1010 as an edge access problem unless the exact request failure proves otherwise.
- CI must not depend on live GNews availability or minimum current-story counts. Live news volume is volatile and belongs to manual QA, not the correctness gate.
- Do not merge to main while the required CI workflow remains red.
