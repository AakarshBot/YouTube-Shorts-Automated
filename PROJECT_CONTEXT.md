# YouTube Shorts Automated — Project Context

This file is the complete current source of truth for the repository. Replace the entire file after every completed project change. Never append a changelog or leave contradictory historical instructions.

## Working agreement

- Treat this repository as the Shorts factory being actively optimised.
- Work one bounded step at a time. After reporting a completed step, continue only after the user says “yes, continue”, unless a decision or manual action is genuinely required from the user.
- Before changing code, read this context and inspect the current implementation and relevant tests.
- Test first, Live second. Do not enable Live before Test approvals are complete.
- No wrappers, adapters, compatibility layers, proxy functions, scaffolding, or unnecessary helper layers.
- Prefer deleting and rewriting the relevant code directly when the current approach is wrong.
- No extra code, runtime dependencies, or API services unless the need is demonstrated and the user explicitly approves them.
- Keep the implementation as small and editable as possible. Do not copy whole systems from Final-Shorts.
- Groq is called directly from Scriptwriter. Do not add a Groq SDK or generic request wrapper.
- Read GROQ_API_KEY from the environment or the repo-root .env when it is not already set. Never put the key in code or CI.
- Groq requests use a browser-style User-Agent because the API edge can reject bare Python urllib clients with Cloudflare error 1010.
- English only for now.
- Final editorial approval is manual.
- Dashboard startup must not eagerly import stage modules that are not needed for the current page. Keep stage imports direct and local to the page/action that uses them.
- Same-page widget actions must not trigger an unnecessary second full Streamlit rerun. Keep st.rerun() for page transitions or genuinely new generation cycles that cannot continue in the current execution.
- After each completed code change, run the relevant tests, check GitHub Actions, and completely rewrite this context to reflect the repository's actual state. Do not describe planned work as completed.
- CI must not depend on live GNews availability or a minimum current-story count.
- Do not merge or leave a red commit.

## Factory and stage status

Formats:
- Deep-Dive — active.
- Top-5 — planned.
- Did You Know — planned.
- Other formats later.

Seven stages:
Topic Fetcher → Scriptwriter → Audio → Subtitles → Visuals → Renderer → Upload.

The dashboard is Test-only through Audio. Live remains disabled until Test approvals are complete. Subtitles, Visuals, Renderer and Upload remain disabled; preserve their current functions and handovers unless a future approved step explicitly requires a change.

Current assessments:
- Topic Fetcher — 7/10. Step 1 source/repeat-search reliability and Step 2 basic event deduplication/ranking are implemented and CI-verified. Broader discovery after the finite RSS pool and real-world editorial-quality review remain open.
- Scriptwriter — 6/10. The editorial specification remains locked. The insufficient-evidence angle-schema correction and nine desk-contract cases passed CI (48 tests total); live Groq-generated editorial output still needs manual review.
- Audio — approved at 8/10 after successful local generation and manual QC.
- Subtitles, Visuals, Renderer and Upload — not active in the current Test flow.

## Optimisation plan — do these steps in order

The first audit reviewed this repository's context, code, tests and GitHub Actions, and compared relevant functions and tests in Final-Shorts. No application code was changed during that audit. The latest observed Actions run was on 7 October 2026: Python compilation passed and all 30 tests passed. That verifies the existing offline suite only; it does not prove live Google News URL resolution or real-story editorial quality.

Work on one step at a time. Do not jump ahead or broaden the scope without a concrete finding.

### Step 1 — Topic Fetcher reliability: selected-source resolution and Search More

Status: STEP 1 COMPLETE. The implementation and regression tests are committed; the full GitHub Actions workflow passed compilation and all 33 tests.

The scope is limited to selected-source/article-text reliability and successive Search More batches within the currently fetched RSS result pool. No new dependencies, news providers or code wrappers are introduced.

#### A. Selected Google News URL and source-reading reliability

- Topic Fetcher must not resolve URLs during bulk search. Bulk fetching is performance-sensitive, and article reading should only begin after the user chooses a story.
- The dashboard calls GNews resolve_url() only after the user selects a headline. GNews resolve_url() relies on optional Playwright; without it, the Google News URL can remain unresolved. The lightweight requirements.txt lists Streamlit and GNews, not Playwright, so a clean install does not guarantee a publisher URL.
- article_text() checks the final response URL from urlopen(). If an unresolved Google News URL redirects to a publisher page, it records that exact publisher URL on the selected story and can use readable article text. If the final response remains on news.google.com, Google News page content is not accepted as publisher article text.
- When article extraction fails or a Google News landing page remains unresolved, article_text() labels the permitted title + GNews-description fallback with [GNEWS DESCRIPTION FALLBACK — ARTICLE TEXT UNAVAILABLE]. The angle planner and script-generation prompt explicitly treat this as limited evidence, not a complete article.
- Tests distinguish unresolved Google News content, a redirect to an exact publisher URL, readable article text, and a labelled summary fallback.
- Keep the selected publisher URL exactly as resolved. Do not lowercase it or strip query parameters.
- Do not pass the already-normalised Topic Fetcher headline object through GNews process_url(); it expects a raw GNews feed item, not the current handoff object.
- Do not add Playwright, another news service, a custom Google News client, copied GNews code or another dependency without demonstrating necessity and obtaining explicit approval.
- Do not add network work to the Topic Fetcher bulk-search path to solve this problem.

#### B. Search More / exclude-seen reliability

- The current fetcher runs its configured queries concurrently and removes exact URLs from the supplied exclude_urls set.
- The current “Search 20 more” action reruns the same query definitions with a larger result limit and excludes previously seen URLs; it does not use a feed offset or explicit pagination token.
- The next batch can overlap heavily with the first batch, particularly in India cricket, and return too few new stories.
- Add deterministic regression tests for the repeated-search/exclude-seen handoff. Tests must demonstrate what happens to previously seen URLs and whether returned stories are genuinely new under the code's selection rules.
- Do not make CI depend on current GNews results, network availability, or a minimum number of live stories.
- Preserve the current initial-search speed. URL resolution and article extraction must remain selected-story operations, not bulk Topic Fetcher work.

### Step 1 results — verified

The selected-source and Search More reliability changes are implemented and verified:

- `scriptwriter.article_text()` checks the final HTTP response URL. If a stored Google News URL reaches a publisher URL through an HTTP redirect, the selected story is updated to that exact publisher URL, preserving its spelling and query parameters.
- If the response remains on `news.google.com`, the page content is not accepted as publisher article text, even if it contains enough incidental HTML text to pass the old length check.
- When article text is unavailable, the allowed headline + GNews-description fallback is labelled `[GNEWS DESCRIPTION FALLBACK — ARTICLE TEXT UNAVAILABLE]`. Both angle planning and script generation are instructed to treat it as limited evidence, not as a complete article, and to ask for more sources when the available evidence cannot support a substantive Short.
- Topic Fetcher keeps bulk fetching free of per-article resolution work. India cricket retains its 100-result cap on Search More; other searches grow the result cap from 40 based on the already-seen URL count, up to 100. Seen URLs are filtered before selection, so successive batches can advance through the currently available RSS result pool.
- Regression tests cover an unresolved Google News landing page, redirecting to an exact publisher URL, labelled summary fallback, and successive Search More batches with no duplicate URLs.
- GitHub Actions passed Python compilation and the full pytest suite: **33 passed in 0.31 seconds**. [Actions run](https://github.com/AakarshBot/YouTube-Shorts-Automated/actions/runs/38168877364).
- No new dependency, provider, wrapper, or extra service was added.

Known limitation retained for Step 2: the current RSS query path has no explicit page token or offset and the result pool is finite. Search More advances through that pool up to the cap; it does not guarantee unlimited results. Improving query diversity after the current pool is exhausted remains part of Step 2.

Step 2 is active after the user approved proceeding.
### Step 2 — Topic discovery quality: event duplicates and story prioritisation

Status: STEP 2 COMPLETE. The implementation and regression tests are committed; the full GitHub Actions workflow passed.

#### Verified implementation

- The Topic Fetcher preserves its existing desk queries, freshness windows, filters, grouping, URL fields and output handoff.
- Every desk/category bucket is now passed through a conservative duplicate-event pass and a soft candidate-ordering pass before the existing freshness fallbacks and output limits are applied.
- Same-event coverage from multiple publishers is collapsed conservatively by meaningful-title-token overlap. A publisher suffix is ignored only when it matches the separately supplied publisher name.
- The rule requires substantial overlap. Sharing a player, organisation, broad event type or generic boilerplate alone is insufficient. Separate stories about the same player and generic appointment stories remain eligible.
- Ranking uses an explainable score based on publication freshness, title specificity, concrete development-signal terms and the presence of a number. These are ordering signals only: a story is never discarded solely because it lacks them.
- After duplicate removal, near-tied candidates receive a modest repeat-publisher penalty to improve publisher variety when choosing from the larger Search More pool.
- Ranking and semantic deduplication happen within each existing desk/category bucket. This intentionally preserves the current dashboard shape and handoff rather than attempting cross-desk clustering.
- The implementation uses Python standard-library code only; no RapidFuzz, wrapper, service or runtime dependency was added.
- Tests cover paraphrased reports of the same event, different events involving the same person, unrelated boilerplate stories, specificity beating a newer generic headline, source suffix handling, publisher variety, and the existing repeated Search More behavior.
- GitHub Actions passed Python compilation and the full pytest suite: **38 passed in 3.85 seconds**. [Actions run](https://github.com/AakarshBot/YouTube-Shorts-Automated/actions/runs/38169649933).

#### Known limitations

- Ranking is a lightweight heuristic for human editorial prioritisation, not a viral predictor. Its story-signal vocabulary may need adjustment after manual use; it is not a claim that each top-ranked story is objectively best.
- Event matching uses title-token overlap. It can still miss paraphrases with little shared wording, and unusually similar but unrelated headlines may occasionally be grouped. The conservative threshold and regression tests reduce, but cannot eliminate, these errors.
- The pass ranks and deduplicates within categories, not across separate desk/category buckets.
- Search More still uses a finite Google News RSS result pool without an explicit page token or offset. It cannot provide unlimited new results; broader query diversity after pool exhaustion remains future work.
- Existing publication-time filters remain the main freshness guard. A recent article can still describe an older development.

### Step 3 — Scriptwriter real-story and multi-desk validation

Status: IN PROGRESS. The automated component is verified: Python compilation passed and all 48 tests passed in 3.83 seconds on commit `192fcf3024871fd1a3aa4a35845710aa6b702566`. [GitHub Actions run](https://github.com/AakarshBot/YouTube-Shorts-Automated/actions/runs/38170661262 ). Scriptwriter remains 6/10 because live generated editorial output has not been manually reviewed.

- Run representative stories from regional cricket, global cricket, niche sports, News/Politics, Technology, Entertainment, Business & Finance, Gaming, and Science & Space through the existing Test workflow.
- Inspect source evidence, angle choices, generated narration, titles and QC fields—not only schema validity.
- Confirm that the three angles are genuinely different in narrative focus and grounded in different supported facts where the evidence allows it.
- Confirm the selected angle actually controls the narration, rather than the writer reverting to the obvious event/result summary.
- Confirm inaccessible or thin source material cannot quietly produce a script that implies stronger research than was available.
- Confirm the completed narration is substantive, accurate, non-repetitive and within the hard format limits.
- Keep manual QC as the principal editorial safety valve. Do not add a large set of subjective hard-rejection rules, extra judge/critic passes, angle scores, claim graphs, personas, automatic rewrite chains or another editorial framework.
- Keep Scriptwriter at 6/10 until multiple representative desk outputs have been manually reviewed. Update the rating only when the evidence supports it.

#### Step 3 work currently in the repository

- The angle output JSON schema no longer forces `minItems=3` and `maxItems=3` on every status. This removes the conflict with `status=needs_more_sources` requiring an empty `angles` array. Ready outputs still have exactly three angles enforced by `validate_editorial_angles()`.
- A regression test confirms the structured schema can represent an insufficient-evidence response with an empty angle list.
- Nine deterministic desk-contract fixtures cover regional cricket, global cricket, niche sports, Politics & Policy, AI, Indian Film & OTT, Companies & Deals, Games & Releases, and Space. Each checks that desk and source evidence reach both model prompts, the chosen angle reaches generation, the angle is retained, and the result passes objective script validation.
- These fixtures use mocked Groq responses. They verify routing, prompt assembly and contract validation; they do **not** prove that live model-generated angles are substantively different or that live narration is factually correct. Real-source retrieval and manual review of generated output remain open. Do not raise the rating or claim editorial approval based on mocked tests alone.

## Topic Fetcher — implementation contract

- Approved source dependency: maintained ranahaani/GNews.
- Independent GNews searches run concurrently; no artificial 8-worker ceiling.
- Existing desk/query configuration and grouping are preserved unless a regression or measured defect justifies a change.
- Every selectable headline carries its title, stored Google News result URL, publisher, published_at timestamp and GNews description.
- Bulk search must not resolve individual article URLs.
- Resolve/read a story only after the user selects it.
- If GNews resolve_url() leaves a news.google.com URL unchanged, article_text() checks the final HTTP response URL. A publisher redirect can yield readable article text and updates the selected story to that exact URL; a response that remains on news.google.com is not treated as article-body evidence.
- Summary fallback is labelled in the returned text so the LLM can distinguish it from a full article. The angle planner and script-generation prompts treat it as limited evidence and must request more sources rather than invent missing details.
- Preserve resolved publisher URL spelling and query parameters exactly.
- Do not change the Topic Fetcher handoff structure as a side effect of an unrelated improvement.
- Do not introduce Playwright or another dependency merely to resolve URLs.
- Search More increases its result cap to 100 based on the already-seen URL count; India cricket always requests up to 100. Seen URLs are filtered before selection, allowing successive batches through the available RSS pool without claiming unlimited pagination.
- The current RSS path still lacks a page token or offset. Broader query diversity after the feed pool is exhausted is deferred to Step 2.
- The India cricket topic grouping currently uses repeated title phrases as an approximation of player/event grouping. It is not guaranteed to represent true event identity; Step 2 is where that is addressed.

## Scriptwriter — specification locked, implementation under validation — 6/10

The selected Topic Fetcher headline is the starting subject. The selected Topic Fetcher desk/genre is passed directly into every Scriptwriter run so the editorial context matches the selection.

### Desk-aware editorial context

- One shared Scriptwriter implementation serves Sports and all current non-sports Deep-Dive desks.
- The selected desk/genre is passed directly into every Scriptwriter run.
- The Groq system instruction identifies the writer as an experienced editor for the selected desk.
- Desk awareness changes editorial context only; the source, angle, factual, slide, timing and packaging rules remain shared.
- Do not create separate Scriptwriter pipelines, wrappers, desk routers or desk-specific generation functions.

### Channel editorial fingerprint

The channel should feel like a smart, human-edited explainer: clear, confident, conversational and informed.

Every Short should:
- Go beyond “what happened” by explaining the most interesting supported detail, connection, context or implication.
- Prefer specific facts, numbers, named people, meaningful remarks, consequences, contrasts, process and useful context.
- Use a real story hook, then build a tight explanation and payoff around the selected editorial angle.
- Avoid manufactured outrage, fake curiosity, generic filler, forced opinions and AI-sounding phrasing.
- Treat this fingerprint as a consistency target, not a fixed template. Hooks, pacing, evidence leads and structure should vary by story and angle.

Rejection remains deliberately light:
- Do not reject a story because it is ordinary or lacks a flashy hook.
- Ask for more sources only when available evidence cannot support a factual, substantive 4–5 slide Short.
- Manual QC remains the main editorial safety valve.

### Editorial architecture

Source evidence → three editorial angles → human selection → Scriptwriter → editable QC.

- The angle planner reads the evidence already collected by Scriptwriter. It does not perform a separate research pass.
- Insufficient evidence returns status=needs_more_sources, a concise reason and no angles.
- Sufficient evidence returns exactly three research-backed choices.
- Each angle contains title, description and evidence_basis.
- Angle titles are 2–5 words, story-specific and unique.
- The three choices must materially differ in the story's editorial spine, not just rephrase the same summary.
- Possible lenses include event/result, a meaningful statement or reaction, consequence/why it matters, performance/process, an unusual person or detail, comparison/timeline, or another lens supported by the sources.
- Do not force categories when the story does not support them.
- Do not invent quotes, motives, consequences, criticism, controversy or interpretation.
- The user can choose one of the three angles or enter a Custom angle.
- The selected angle is authoritative. The complete narration must be built around it rather than reverting to the obvious event/result summary.
- A ready result stores the selected angle as story_angle and retains it through QC and downstream handoff.
- Initial writing and Script Redo both use the angle planner.
- Redo generates three new angle choices from the current evidence and previous-draft context. Passes become progressively stricter about changing the lead evidence, central question and narrative structure.
- Angle planning and script generation use the same collected evidence. Do not add duplicate article-reading passes.
- Do not add angle scoring, hook scores, source-coverage scores, critic passes, claim graphs, personas, automatic rewrite chains, title-ranking systems, provider routers or another editorial framework.

### Core editorial rule

Understand the full story first. Choose the editorial lens second. Rewrite the Short from scratch third. Package it last.

The writer must read available sources, understand what happened, use the selected angle to decide what matters, and write fresh narration. It must never merely expand, paraphrase or prolong the Topic Fetcher headline. The headline is a starting subject, not an approved script or final YouTube title.

### Source workflow

Initial run:
1. Read the selected source URL and try to obtain readable article text.
2. If article extraction fails, the GNews description may be used as fallback evidence. It is labelled `[GNEWS DESCRIPTION FALLBACK — ARTICLE TEXT UNAVAILABLE]` and must not be mistaken for a full article.
3. Pass collected evidence to the angle planner.
4. If sufficient, show exactly three angles for human selection.
5. If insufficient, return needs_more_sources and do not write a thin Short.

Automatic additional-source run:
- Occurs only if the primary evidence is insufficient.
- Uses the existing GNews dependency.
- Searches for related reporting on the selected story.
- Reads usable results and combines them with the existing primary evidence.
- Feeds the combined evidence to the angle planner.
- Runs no second automatic related-source search after this pass.

Manual additional-source run:
- If primary plus automatic evidence remains insufficient, ask for source URLs, one per line.
- Combine every usable manual source with all previously collected evidence.
- Feed the combined evidence to the angle planner.
- If evidence remains insufficient, clearly tell the user there is not enough information to make a genuine Short.
- Never invent a script or packaging to force an output.

Failure handling:
- Source-reading failures must be distinct from Groq/generation failures.
- API, structured-output and generation errors must surface as actual errors, not as evidence insufficiency.
- A failed automatic related-source request must surface as an actual error rather than silently converting into needs_more_sources.
- The Scriptwriter retry path must be able to retry angle generation after evidence has already been collected.

### Editorial angle output and validation

Ready output:
- status = ready
- exactly 3 angle objects
- each has title, description and evidence_basis

Insufficient output:
- status = needs_more_sources
- concise reason
- empty angles

Python validates angle output for correct status, exactly three angles when ready, object shape, required fields, title length of 2–5 words, unique titles and a reason when more sources are needed.

### Story rules

- A Short may synthesise one or multiple sources supporting the same story.
- One selected editorial angle governs the Short.
- Exactly 4 or 5 slides; minimum 4, maximum 5.
- Every slide must add important information; no filler, repetition or artificial splits to reach the slide count.
- Slide 1 spoken narration must contain fewer than 14 words.
- Total narration must be 65 words or fewer as the proxy for a Short under 30 seconds.
- Audio may slightly speed narration only when the finished audio is marginally over 30 seconds.
- Retention should come from real facts, context, contrast, consequence, significance or surprise supported by sources.
- Include the important facts, context, names, teams, organisations, events, numbers and remarks needed to understand the selected angle.
- Reorder and synthesise facts rather than following article paragraphs mechanically.
- Do not invent facts, statistics, quotes, reactions, motives, criticism, controversy, pressure, predictions or consequences.
- Preserve the meaning and tone of important remarks.
- Use people's proper names when identified by sources. Do not hide a known person's identity behind labels such as “legend”, “icon” or “veteran”.

### Opening screen headline

- Exactly 3 or 4 words.
- Specific to the story.
- Separate from the spoken Slide 1 narration.

### Packaging

Ready initial generation also produces:
- At least two YouTube title options.
- One natural description.
- Relevant hashtags.
- One story-specific first/creator comment.

Packaging comes after the completed Short and selected angle are understood.

Titles must be accurate to the finished Short, genuinely different in packaging angle, concise and natural, with important names/story terms early. No clickbait, fake curiosity, excessive capitals, unnecessary emoji or unsupported facts.

The description explains the actual story naturally and adds no unsupported facts. Hashtags are relevant only. The first comment is story-specific and invites genuine discussion rather than using generic CTA boilerplate.

### Script Redo

- Available manually before approval.
- Manual QC is the straightforward edit-and-approve path: every script field can be changed or approved unchanged.
- Redo begins by offering exactly three new editorial angles based on current evidence and the previous script.
- Pass 1 must materially change the editorial spine, use a different lead fact where supported and avoid repeating the previous opening premise or slide progression.
- Pass 2 must more strongly avoid the previous angle's central emphasis, opening claim and evidence order unless the sources leave no defensible alternative.
- Pass 3 and later should change the central question, evidence lead and narrative structure. Do not produce cosmetic rewrites for the sake of appearing different.
- Only after repeated redos, when sources genuinely offer no defensible alternative treatment, may the angle planner return needs_more_sources rather than force novelty.
- The user can choose a new angle or enter a Custom angle.
- The user may optionally supply additional source URLs for the redo, one per line. Usable sources are added to existing evidence before the new angle plan.
- Clicking Redo alone does not trigger another automatic related-source search.
- After angle selection, the writer receives the same evidence, selected angle and previous draft.
- Redo is script-only: Groq returns status, reason, opening_headline and slides.
- The dashboard carries forward the previous titles, description, hashtags and first comment unchanged. These remain editable in the new QC version.
- story_angle is replaced with the selected redo angle.
- Original and redo versions remain visible for human QC.
- Each successful redo uses the latest draft as the previous version and increases strictness.
- If redo evidence is insufficient, keep the manual source-URL field available for another user-supplied attempt.
- An approved title/version must never be supplied to story generation.

### Script output and deterministic validation

Ready initial generation contains story_angle, opening_headline, slide-by-slide voiceover, at least two YouTube title options, description, hashtags and first/creator comment. Ready redo returns the script fields from Groq and the dashboard attaches the preserved packaging. A non-ready result contains needs_more_sources and a concise reason, with no script or packaging.

Python enforces objective rules only:
- Ready output has 4 or 5 slides.
- Slide 1 has fewer than 14 words.
- Total narration is 65 words or fewer.
- Every slide has spoken narration.
- Opening headline has 3 or 4 words.
- Every ready result has story_angle.
- Duplicate spoken slides are rejected.
- At least two title options exist.
- Description, hashtags and first comment exist.
- needs_more_sources requires a reason.
- Malformed output is rejected.

### Test dashboard flow

1. User manually selects a Topic Fetcher headline.
2. Scriptwriter attempts to read the selected source.
3. The angle planner decides whether the available evidence is sufficient.
4. If insufficient, related GNews sources are searched once and added to the existing evidence.
5. If still insufficient, the dashboard asks for manual source URLs.
6. Manual URLs are added to all existing evidence.
7. If evidence remains insufficient, the dashboard shows a clear Not enough information message and the reason.
8. If ready, the dashboard shows exactly three evidence-backed editorial angles.
9. The user chooses an angle or enters a Custom angle.
10. Scriptwriter generates the full Short around that angle.
11. Dashboard shows the QC package in fixed editorial order.
12. Every QC editorial field remains editable before approval.
13. Approval validates the edited package before it becomes Audio input.
14. Before approval, Redo Script presents three new angle choices; redo strictness increases on each pass.
15. Redo preserves previous packaging until the user edits it in the new QC version.
16. Same-page actions use state mutated during the current Streamlit interaction; do not add a redundant second rerun only to refresh a picker or generation result.

### Scriptwriter QC editing

- Editable fields: opening headline, every slide voiceover, every title option, strongest-title selection, description, hashtags and first comment.
- Generated values are initial values; user can edit them or approve unchanged.
- story_angle is visible as context but is not a manual QC field in this stage.
- Approval validates the edited package against the same deterministic rules.
- The approved edited version, including the selected edited title and story_angle, is the exact input passed to Audio.
- Once approved, the version is read-only.
- Another redo is available only while no version is approved.

## Top-5 — PLANNED

- Cricket-only in the current future design.
- Select 5 headlines with URLs/titles/articles.
- Exactly 6 slide headlines.
- Slide 1 under 14 words.
- Slides 2–6 each limited to 15 seconds of speech.
- No generic “5 stories you need to see…” opening.

## Audio — APPROVED — 8/10

Stage 3 is approved after successful local generation and manual QC. Narration only; no music or sound effects.

### Audio engine

- Chatterbox is the approved local TTS engine and uses the installed ChatterboxTurboTTS model on the available device.
- Do not pass unsupported arguments such as nano=True.
- Audio runs locally; no paid TTS API or cloud audio generation.
- If audio_reference.wav exists in the repo root, use it as the narrator reference. AUDIO_REFERENCE may override that path.
- Prepare reference-audio conditioning once at the start of an Audio run and reuse it for every slide.
- Reference audio is local-only and must not be committed.

### Delivery and timing

- Generate audio separately for each approved Scriptwriter slide.
- Keep narrator identity consistent while varying delivery modestly by slide.
- Slide 1 receives stronger opening delivery; final slides receive a small payoff emphasis.
- Questions/exclamations get slightly more expression; numeric/factual slides get slightly slower pacing.
- Reseed Chatterbox randomness per run and slide so Redo Audio produces a genuinely new take.
- Preserve Scriptwriter words exactly. Audio does not rewrite the story.
- Add a small natural pause between slides.
- Use the 65-word Scriptwriter limit as the primary protection for a Short under 30 seconds.
- If generated narration is only marginally above 30 seconds, apply at most a slight time-stretch before failing.
- Generate full.wav and one slide_XX.wav per slide.
- Local outputs live under generated_audio/ and are not committed.
- Derive output paths from script content so Redo Audio replaces the current take instead of creating uncontrolled file growth.

### Audio test flow and current environment

1. User approves the Scriptwriter version.
2. Dashboard moves to Audio.
3. User clicks Generate Audio to start local Chatterbox narration.
4. Dashboard previews the complete Short and every slide.
5. User manually approves Audio.
6. Redo Audio regenerates narration without changing Scriptwriter text.
7. Subtitles remain disabled until Stage 4 is built.

- Chatterbox is installed manually in the same local project environment and is intentionally not added to lightweight CI requirements.
- Turbo model weights are cached locally after successful first generation.
- Windows Hugging Face symlink warning does not block use. No Hugging Face token is required by the factory.
- A local startup issue caused by the Perth watermarker dependency was resolved in the environment before Audio approval. Do not add a project wrapper or extra factory service for it.
- Audio is approved at 8/10. Reopen only for a later requirement, quality issue or regression.

## Current files

- PROJECT_CONTEXT.md — complete source of truth, replaced after each completed project change.
- topic_fetcher.py — concurrent GNews Topic Fetcher with desk-specific queries, freshness/utility filtering, conservative title-overlap event deduplication, explainable candidate ranking/publisher variety, India cricket phrase grouping and the existing headline handoff.
- scriptwriter.py — source-first, desk-aware Scriptwriter with the editorial fingerprint, explicit three-choice angle planning, selected-angle-authoritative writing, Custom angle support, and progressively stricter script redo passes.
- app.py — Test dashboard through Audio. Stage imports are local; editorial angles are presented before each Scriptwriter generation; selected story_angle is retained through QC and Audio handoff.
- audio.py — local Chatterbox narration for approved Scriptwriter slides.
- tests/test_topic_fetcher.py — deterministic Topic Fetcher tests, including multi-batch Search More/exclude-seen coverage, event-deduplication, generic-story preservation, specificity-ranking and publisher-variety tests. The Step 2 run passed with 38 tests before Step 3 tests were added.
- tests/test_scriptwriter.py — Scriptwriter source-handling, angle/script contract and redo tests; includes empty-angle insufficiency schema coverage and nine mocked desk-contract fixtures. Live real-story output review remains outstanding.
- tests/test_audio.py — Audio dependency-loading and input-validation tests.
- .github/workflows/test.yml — deterministic CI.
- requirements.txt — lightweight dependencies; Chatterbox is installed manually in the local environment.
- .gitignore — excludes local Audio outputs and narrator reference audio.

## CI contract

- CI checks Python compilation and runs pytest.
- CI must use deterministic mocks for Topic Fetcher and Scriptwriter source-handling tests; do not require live GNews results or a minimum number of current stories.
- Step 1 CI verification passed: Python compilation succeeded and 33 tests passed in 0.31 seconds on commit `8172021f3b49431925f21c7e6f43d09c5ce55f7a`. [Run 135](https://github.com/AakarshBot/YouTube-Shorts-Automated/actions/runs/38168877364).
- Step 2 CI verification passed: Python compilation succeeded and 38 tests passed in 3.85 seconds on commit `15a3fa00e38ccc0b4fa84d269c8f4176273b61c1`. [Run 137](https://github.com/AakarshBot/YouTube-Shorts-Automated/actions/runs/38169649933).
- Step 3 automated verification passed on commit `192fcf3024871fd1a3aa4a35845710aa6b702566`: Python compilation succeeded and **48 tests passed in 3.83 seconds**. [Run 139](https://github.com/AakarshBot/YouTube-Shorts-Automated/actions/runs/38170661262). This includes a mocked nine-desk contract suite and empty-angle insufficiency coverage; it does not replace manual review of live Groq-generated story output.
- Do not merge a red commit.
