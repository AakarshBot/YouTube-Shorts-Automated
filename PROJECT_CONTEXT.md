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
- Dashboard startup must not eagerly import stage modules that are not needed for the current page. Keep stage imports direct and local to the page/action that uses them.
- Same-page widget actions must not trigger an unnecessary second full Streamlit rerun. Keep `st.rerun()` only where the state change requires a new page or a genuinely new generation cycle.

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
- Every selectable headline carries its title, Google News result URL, publisher, published_at and GNews description.
- Topic Fetcher does not resolve article URLs during bulk search. URL resolution happens only after the user selects a story, immediately before Scriptwriter source reading.
- Selected-story resolution uses GNews's existing `resolve_url(url)` directly on the stored URL. Do not pass the already-normalised Topic Fetcher headline object through GNews `process_url()`; that function expects the raw feed shape (`source.href` and `link`) and is not the handoff format used by Topic Fetcher.
- Once resolved, preserve the selected story's exact publisher URL; do not lowercase or strip query parameters.
- Do not add Playwright, another news service, a custom Google News client, copied GNews code or another dependency merely to reduce runtime.
- The bulk search path is the performance-sensitive path; avoid per-article network work after GNews returns its RSS results.

## Scriptwriter — SPEC LOCKED / APPROVED — 6/10 — PENDING MULTIPLE TEST CASES

The selected Topic Fetcher headline is sent to Scriptwriter as the story to investigate. The selected Topic Fetcher desk/genre is passed directly to Scriptwriter so the writer's editorial context matches the selected desk.


### Desk-aware editorial context

- The existing selected Topic Fetcher desk/genre is passed directly into every Scriptwriter generation run.
- The Groq system instruction identifies the writer as an experienced editor for the selected desk/genre.
- This applies to Sports subdesks and non-sports desks alike.
- Desk awareness changes editorial context only; the core source-first story, factual, slide, timing and packaging rules remain shared across desks.
- Do not create separate Scriptwriter pipelines, wrappers, desk routers or desk-specific generation functions unless a later requirement explicitly requires different rules.

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
- The final Short must contain exactly 4 or 5 slides: minimum 4, maximum 5.
- Every slide must add important information.
- Do not create filler, repetition or artificial sentence splits just to reach 4 or 5 slides.
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

On an initial generation, Scriptwriter creates both the completed narration and its packaging. On a script redo, only the opening screen headline and slide-by-slide voiceover are regenerated; the previous draft's titles, description, hashtags and first/creator comment are preserved exactly for manual QC.

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

### Script redo

- Available manually before approval.
- The user may optionally provide additional source URLs specifically for the redo, one per line.
- When URLs are supplied, the writer reads the usable sources and adds them to the existing source evidence for that redo.
- If the user provides no URLs, the redo uses the source evidence already collected.
- No new automatic related-source search is performed just because the user clicked Redo Script.
- The previous version is supplied to the writer for comparison.
- The new version must use a genuinely different editorial angle or narrative spine.
- It must not merely swap words, reorder sentences or lightly rephrase the same script.
- A redo regenerates only the opening screen headline and slide-by-slide voiceover.
- The previous version's YouTube titles, description, hashtags and first/creator comment are preserved exactly and remain editable in the new QC version.
- If the evidence is still insufficient, the dashboard tells the user why and keeps the redo source-URL field available for another user-supplied source attempt.
- Original and redo versions remain visible for manual QC.
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
- Ready output has 4 or 5 slides.
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
9. Dashboard shows the editable QC package in a fixed editorial order: opening headline, slide-by-slide voiceover, YouTube title options, strongest-title selection, description, hashtags, first comment, then approval.
10. Voiceover slides are visually separated and explicitly labelled by slide number; packaging fields are kept in their own sections so the QC page does not visually mix script and metadata.
11. Scriptwriter QC text inputs, text areas and title-selection controls use the light dashboard surface with dark readable text; do not use black/dark field contrast in the test dashboard.
12. User can edit any of those fields, choose the strongest title, and approve the edited version or approve the generated version unchanged.
13. Approval validates the edited package before the version becomes the Audio input.
14. Redo Script is available before approval and shows an optional additional-source URL field.
15. Redo Script regenerates only the opening screen headline and slide voiceovers; the previous packaging fields are carried into the new version unchanged for manual editing.
16. If a redo says more source information is needed, the dashboard shows the reason and keeps the user-provided source URL field available instead of hiding it because a prior draft already exists.
17. Same-page actions render from the state mutated during the current Streamlit interaction; do not add an extra `st.rerun()` just to refresh the same page. Full reruns remain for page transitions and actions such as retrying or starting a new generation cycle that cannot continue correctly in the current execution.

The selected Topic Fetcher headline and selected desk/genre remain the starting story inputs. The approved title is stored for later handoff only and is never passed into Scriptwriter generation.

### Scriptwriter QC editing

- Every editorial output field in a ready Scriptwriter result is editable during manual QC before approval: opening headline, every slide voiceover, every title option, description, hashtags and first comment.
- The generated values are the starting values; the user may edit them or approve them unchanged.
- Approval validates the edited package with the same deterministic Scriptwriter rules before saving it as the approved version.
- The approved edited version, including the selected edited title, is the exact input passed to Audio.
- The Scriptwriter status and source evidence are not manual QC fields; they remain controlled by the pipeline.
- Once a version is approved, the dashboard shows it as approved rather than allowing further QC edits in that approved state.

## Top-5 — PLANNED

- Cricket-only in the current version.
- Select 5 headlines with URLs/titles/articles.
- Exactly 6 slide headlines.
- Slide 1 under 14 words.
- Slides 2–6 each limited to 15 seconds of speech.
- No generic “5 stories you need to see…” opener.

## Audio — IMPLEMENTED — PENDING LOCAL GENERATION/QC

Stage 3 is narration only. No music, sound effects or other audio layers.

### Audio engine
- Chatterbox is the approved local TTS engine.
- The code uses the installed ChatterboxTurboTTS model on the available device. The current local installation exposes the Turbo class without a nano argument, so the factory does not pass an unsupported Nano flag.
- The model runs locally; there is no paid TTS API or cloud audio generation in the factory.
- A single channel narrator is preferred for long-term identity.
- If `audio_reference.wav` exists in the repo root, it is used as the narrator reference. `AUDIO_REFERENCE` may override that path. If no reference exists, the model's built-in voice is used.
- The reference recording is optional for the first test but recommended for the long-term channel voice.
- Reference conditioning is prepared once at the start of an Audio generation run and reused for all slides. Do not re-process the reference for every slide.
- Reference audio must not be committed. It is ignored by git.

### Delivery
- Generate audio separately for every approved Scriptwriter slide.
- Prepare any narrator reference conditioning once per run, then generate all slides from the prepared conditioning.
- Keep the narrator identity consistent while varying delivery modestly by slide.
- Slide 1 receives a stronger opening delivery.
- Final slides receive a small payoff emphasis.
- Questions/exclamations receive slightly more expression.
- Numeric/factual slides receive slightly slower pacing.
- Chatterbox randomness is reseeded per run and slide so Redo Audio produces a genuinely new take.
- Do not insert fake emotions, SFX, music or invented spoken content.
- Preserve the Scriptwriter words exactly; Audio does not rewrite the story.

### Timing and output
- Add a small natural pause between slides.
- Use the Scriptwriter 65-word limit as the primary protection for a Short under 30 seconds.
- If the generated narration is only marginally above 30 seconds, apply at most a slight time-stretch before failing.
- Reject narration that remains too long after the allowed slight speed adjustment.
- Generate one complete `full.wav` plus one `slide_XX.wav` for each slide.
- Local generated files live under `generated_audio/` and are not committed.
- Output paths are derived from the script content so Redo Audio replaces the current take for that Short rather than creating uncontrolled file growth.
- The reference conditioning optimisation is required for acceptable local Audio runtime; re-running reference preparation per slide is not allowed.
- Chatterbox model loading must call the installed from_pretrained(device=...) API directly; do not pass unsupported arguments such as nano=True.
- Audio output remains available as the handoff for Subtitles and later stages.

### Test dashboard
1. User approves the Scriptwriter version.
2. Dashboard moves to Audio immediately without blocking the page on TTS generation.
3. User clicks Generate Audio to start local Chatterbox narration from the approved slide voiceovers.
4. Dashboard previews the complete Short.
5. Dashboard previews every slide separately.
6. User can listen and manually approve the Audio.
7. Redo Audio regenerates a new take without changing the approved Scriptwriter text.
8. Subtitles remain disabled until Stage 4 is built.

### Local installation
- Chatterbox is installed manually into the same existing project virtual environment.
- It is intentionally not added to CI's lightweight `requirements.txt`; CI validates factory code without downloading the TTS model stack.
- First local generation downloads/caches the Chatterbox model weights.

## Later stages

Subtitles, Visuals, Renderer and Upload are not active. Preserve their existing functions and handovers unless explicitly requested.

## Current files

- PROJECT_CONTEXT.md — current source of truth.
- topic_fetcher.py — completed Topic Fetcher.
- app.py — Test dashboard through Audio. Pipeline modules are loaded only when their stage is needed; Scriptwriter QC fields are edited directly in the page in a fixed editorial order with separated slide cards and packaging sections; Audio generation is explicitly started from the Audio page. Script redo accepts optional user-supplied source URLs, regenerates only the opening headline and slides, and preserves the previous packaging fields unchanged. Same-page actions avoid redundant second full reruns; full reruns are retained for page transitions and actions that genuinely require a new execution. Dashboard logic is kept direct; no stage wrapper/helper functions.
- scriptwriter.py — source-first, desk-aware Scriptwriter approved at 6/10; pending multiple test cases across desks. Supports script-only redo mode, preserving the previous packaging fields when generating a replacement script.
- audio.py — local Chatterbox narration for approved Scriptwriter slides; implemented and pending local generation/QC.
- tests/test_topic_fetcher.py — Topic Fetcher tests.
- tests/test_scriptwriter.py — Scriptwriter tests.
- tests/test_audio.py — Audio dependency-loading and input validation tests.
- .github/workflows/test.yml — deterministic CI.
- requirements.txt — lightweight factory dependencies; Chatterbox is installed manually in the local project environment.
- .gitignore — excludes local Audio outputs and narrator reference audio.

## CI

CI must not depend on live GNews availability or a minimum current-story count.
Do not merge a red commit.
