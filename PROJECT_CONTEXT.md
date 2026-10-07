# YouTube Shorts Automated — Project Context

Current source of truth. Replace this file completely after every project change. Never append history.

## Rules

- Test first, Live second.
- No wrappers, adapters, compatibility layers, proxy functions or scaffolding.
- Delete and rewrite code directly when the current approach is wrong.
- No new runtime dependencies or API services unless explicitly approved.
- Groq is called directly from Scriptwriter. Do not add a Groq SDK or generic request wrapper.
- The local Groq key is read directly from the repo-root .env as GROQ_API_KEY when it is not already in the environment. Never store the key itself in code or CI.
- Groq requests use a browser-style User-Agent because the API edge can reject bare Python urllib clients with Cloudflare error 1010.
- English only for now.
- Final editorial approval is manual.
- Dashboard startup must not eagerly import stage modules that are not needed for the current page. Keep stage imports direct and local to the page/action that uses them.
- Same-page widget actions must not trigger an unnecessary second full Streamlit rerun. Keep st.rerun() for page transitions or genuinely new generation cycles that cannot continue in the current execution.

## Factory

Formats:
- Deep-Dive — active.
- Top-5 — planned.
- Did You Know — planned.
- Others later.

Seven stages:
Topic Fetcher → Scriptwriter → Audio → Subtitles → Visuals → Renderer → Upload.

Live remains disabled until Test approvals are complete.

## Topic Fetcher — COMPLETE — 7/10

Do not reopen unless a later requirement or regression requires it.

- Maintained ranahaani/GNews is the approved news source.
- Independent GNews searches run concurrently with no artificial 8-worker ceiling.
- Existing queries, filters, grouping, story counts, handovers and output fields remain unchanged.
- Every selectable headline carries its title, Google News result URL, publisher, published_at and GNews description.
- Topic Fetcher does not resolve article URLs during bulk search. Resolution happens only after the user selects a story, immediately before Scriptwriter source reading.
- Selected-story resolution uses GNews's existing resolve_url(url) directly on the stored URL.
- Do not pass the already-normalised Topic Fetcher headline object through GNews process_url(); that function expects the raw feed shape and is not the handoff format used here.
- Once resolved, preserve the selected publisher URL exactly. Do not lowercase or strip query parameters.
- Do not add Playwright, another news service, a custom Google News client, copied GNews code or another dependency merely to reduce runtime.
- The bulk search path is the performance-sensitive path; avoid per-article network work after GNews returns its RSS results.

## Scriptwriter — SPEC LOCKED / APPROVED — 6/10 — PENDING MULTIPLE DESK TEST CASES

The selected Topic Fetcher headline is the starting subject. The selected Topic Fetcher desk/genre is passed directly into every Scriptwriter run so the editorial context matches the selected desk.

### Desk-aware editorial context

- One shared Scriptwriter implementation serves Sports and every current non-sports Deep-Dive desk.
- The selected Topic Fetcher desk/genre is passed directly into every Scriptwriter run so the editorial context matches the user's selection.
- The Groq system instruction identifies the writer as an experienced editor for the selected desk/genre.
- Desk awareness changes editorial context only; source, angle, factual, slide, timing and packaging rules remain shared.
- Do not create separate Scriptwriter pipelines, wrappers, desk routers or desk-specific generation functions.

### Channel editorial fingerprint

The channel should feel like a smart, human-edited explainer: clear, confident, conversational and informed.

Every Short should:
- Go beyond "what happened" by making the most interesting supported detail, connection, context or implication understandable.
- Prefer specific facts, numbers, named people, meaningful remarks, consequences, contrasts, process and useful context.
- Use a real story hook, then build a tight explanation and payoff around the selected editorial angle.
- Avoid manufactured outrage, fake curiosity, generic filler, forced opinions and AI-sounding phrasing.
- Treat the fingerprint as a consistency target, not a fixed template. Hooks, pacing, evidence leads and structure should vary by story and angle.

The rejection rule remains deliberately light:
- Do not reject a story because it is ordinary or lacks a flashy hook.
- Ask for more sources only when the evidence cannot support a factual, substantive 4–5 slide Short.
- Manual QC remains the main editorial safety valve.

### Editorial architecture

The Scriptwriter uses an explicit human-selected editorial-angle step:

Source evidence → three editorial angles → human selection → Scriptwriter → editable QC.

- The angle planner reads the source evidence already collected by Scriptwriter. It does not perform a second research pass.
- When the evidence is insufficient, the angle planner returns status=needs_more_sources with a concise reason and no angles.
- When the evidence is sufficient, the angle planner returns exactly 3 research-backed choices.
- Each choice contains title, description and evidence_basis.
- Angle titles are 2–5 words, story-specific and unique.
- The three choices must materially change the story's editorial spine, not merely rephrase the same summary.
- Useful lenses can include the event/result, a meaningful statement or reaction, consequence/why it matters, performance/process, an unusual person or detail, comparison/timeline or another evidence-backed lens.
- Do not force generic categories when the story does not support them.
- Do not invent quotes, motives, consequences, criticism, controversy or interpretation.
- The user can choose one of the three or enter a Custom angle.
- The selected angle is authoritative for Scriptwriter. The writer must build the complete narration around it rather than reverting to the obvious event/result summary.
- The selected angle is stored on each ready Scriptwriter result as story_angle and is retained through QC and downstream handoff.
- The angle planner is used for initial generation and Script Redo.
- Redo generates three new angle choices using current evidence and the previous draft context so the user can deliberately change the story perspective rather than asking for a vague rewrite.
- Redo passes become progressively stricter. The first redo must materially change the editorial spine; later redos must move the lead evidence, central question and narrative structure further away from the previous draft.
- The angle planner and Scriptwriter use the same collected evidence object. No duplicate article-reading or hidden research layer is introduced.
- Do not add angle scoring, hook scores, source-coverage scores, critic passes, claim graphs, personas, automatic rewrite chains, title-ranking systems, provider routers or another editorial framework.

### Core editorial rule

Understand the full story first. Choose the editorial lens second. Rewrite the Short from scratch third. Package it last.

The writer must:
- Read the available source material.
- Understand what actually happened.
- Use the selected editorial angle to decide what matters most.
- Rewrite the narration from scratch after understanding the story.
- Never simply expand, paraphrase or prolong the Topic Fetcher headline.
- Treat the Topic Fetcher headline as the starting subject, not a finished script or approved YouTube title.

### Source workflow

Initial source run:
1. Read the exact Topic Fetcher source URL.
2. Use readable article text when available; fall back to the Topic Fetcher GNews description when necessary.
3. Feed that evidence to the editorial-angle planner.
4. If the evidence is enough, show 3 editorial angles for human selection.
5. If the evidence is not enough, return needs_more_sources and do not write a thin Short.

Automatic additional-source run:
- Only happens when the primary evidence is not enough.
- Uses the existing GNews dependency already used by Topic Fetcher.
- Searches for related reporting from the selected headline.
- Reads the usable results and combines them with the primary evidence.
- Feeds the combined evidence to the angle planner.
- Does not perform another automatic related-source search after this pass.

Manual additional-source run:
- If the combined primary + automatic evidence is still insufficient, the dashboard asks for additional source URLs.
- Multiple URLs are accepted, one per line.
- Usable manual sources are combined with all previously collected evidence.
- The combined evidence is fed to the angle planner.
- If the evidence is still insufficient, stop and tell the user there is not enough information to create a genuine Short.
- Do not invent a script, titles, description, hashtags or comment just to produce an output.

Failure handling:
- Source-reading failures are distinct from Groq/generation failures.
- API, structured-output and generation errors must surface as actual errors; never treat them as evidence insufficiency.
- A failed automatic related-source request must surface as an actual error; it must not be silently converted into needs_more_sources.
- The Scriptwriter retry path must be able to retry an angle-generation failure even when source evidence was already collected.

### Editorial angle output

Ready angle planner output:
- status = ready
- exactly 3 angles
- each angle has title, description, evidence_basis

Insufficient angle planner output:
- status = needs_more_sources
- concise reason
- empty angles

Python deterministically validates:
- exactly 3 angles when ready
- each angle is an object
- title, description and evidence basis are present
- title is 2–5 words
- angle titles are unique
- needs-more-sources has a reason

Do not add angle scoring, hook scores, source-coverage scores, critic passes, claim graphs, personas, automatic rewrite chains, title-ranking systems, provider routers or another editorial framework.

### Story rules

- The final Short can use one source or multiple supporting sources.
- Multiple sources may be synthesised when they support the same story.
- One selected editorial angle governs the Short.
- The final Short must contain exactly 4 or 5 slides: minimum 4, maximum 5.
- Every slide must add important information.
- Do not create filler, repetition or artificial sentence splits just to reach 4 or 5 slides.
- Slide 1 spoken narration must contain fewer than 14 words.
- Total spoken narration must be 65 words or fewer. This is the Scriptwriter proxy for a Short under 30 seconds.
- The Audio stage may slightly speed the final voice when the finished audio is only marginally above 30 seconds.
- Retention should come from real facts, context, contrast, consequence, significance or surprise in the sources.
- Capture the important facts, context, names, teams, organisations, events, numbers and remarks needed to understand the story through the selected angle.
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

Packaging is written only after the completed Short and selected editorial angle are understood.

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
- Existing manual QC remains the simple rewrite path: every script field can be edited and approved unchanged.
- Redo is the stronger regeneration path and always starts by creating exactly 3 new editorial-angle choices from the current evidence and the previous script.
- Pass 1 must materially change the editorial spine, use a different lead fact where the evidence supports it, and avoid repeating the previous opening premise or slide progression.
- Pass 2 is stricter: avoid the previous angle's central emphasis, opening claim and evidence order unless the sources leave no defensible alternative; prefer a less-obvious supported detail, reaction, consequence, comparison or process insight.
- Pass 3 and later use the strongest difference rule: change the central question, evidence lead and narrative structure. Do not create cosmetic rewrites just to appear different.
- Only after repeated redos, when the sources genuinely offer no defensible alternative treatment, the angle planner may return needs_more_sources instead of forcing novelty.
- The user can select one of the three new angles or enter a Custom angle.
- The user may optionally provide additional source URLs specifically for the redo, one per line. Those usable sources are added to the current evidence before the new angle planner run.
- No automatic related-source search is performed just because the user clicks Redo.
- After the user selects an angle, the writer receives the same evidence plus the selected angle and previous draft.
- Redo generation is script-only: Groq returns only status, reason, opening_headline and slides.
- The previous version's YouTube titles, description, hashtags and first/creator comment are carried forward unchanged by the dashboard, then remain editable in the new QC version.
- story_angle is replaced with the selected redo angle.
- Original and redo versions remain visible for manual QC.
- The user can redo again before approval; each successful redo uses the latest version as the previous draft and increases the redo strictness level.
- If redo evidence is insufficient, the dashboard keeps the redo source-URL field available for another user-supplied source attempt.
- Approved title/version is never supplied to story generation.

### Script output

Ready initial generation contains:
- story_angle
- opening_headline
- slide-by-slide voiceover
- multiple YouTube title options
- description
- hashtags
- first/creator comment

Ready redo generation contains the same final fields after the dashboard attaches preserved packaging. Groq itself is asked only for:
- status
- reason
- opening_headline
- slides

A non-ready result contains:
- status = needs_more_sources
- concise reason
- no script or packaging.

### Deterministic Scriptwriter validation

Python enforces only objective rules:
- Ready output has 4 or 5 slides.
- Slide 1 has fewer than 14 words.
- Total narration is 65 words or fewer.
- Every slide has spoken narration.
- Opening headline has 3 or 4 words.
- A selected story_angle exists on every ready result.
- Duplicate spoken slides are rejected.
- At least two title options exist.
- Description, hashtags and first comment exist.
- status = needs_more_sources requires a reason.
- Malformed output is rejected.

### Test dashboard flow

1. Manually select a Topic Fetcher headline.
2. Scriptwriter reads the primary source.
3. Scriptwriter/angle planner decides whether that evidence is sufficient.
4. If insufficient, related GNews sources are searched once and added to the evidence.
5. If still insufficient, dashboard asks for manual source URLs.
6. The manual-source run uses the new URLs plus all existing evidence.
7. If still insufficient, dashboard stops with a clear Not enough information message and the writer's reason.
8. If ready, dashboard shows exactly three research-backed editorial angles before script generation.
9. User chooses one angle or writes a Custom angle.
10. Scriptwriter generates the full Short around that selected angle.
11. Dashboard shows the completed Scriptwriter QC package in fixed editorial order.
12. Every QC editorial field remains editable before approval.
13. Approval validates the edited package before it becomes the Audio input.
14. Before approval, Redo Script presents three new editorial-angle choices; each redo pass is stricter than the previous pass, and the user then generates the new script from the chosen angle.
15. Redo preserves previous packaging unchanged until the user edits it in the new QC version.
16. Same-page actions render from state mutated during the current Streamlit interaction; no redundant second rerun is added just to refresh a picker or generation result.

### Scriptwriter QC editing

- Editable fields: opening headline, every slide voiceover, every title option, strongest-title selection, description, hashtags and first comment.
- The generated values are the starting values; the user can edit them or approve unchanged.
- story_angle is displayed as context but is not a manual QC field in this stage.
- Approval validates the edited package with the same deterministic Scriptwriter rules.
- The approved edited version, including the selected edited title and preserved story_angle, is the exact input passed to Audio.
- Once approved, the dashboard shows the approved version as read-only.
- The user can create another redo only while no version is approved.

## Top-5 — PLANNED

- Cricket-only in the current future design.
- Select 5 headlines with URLs/titles/articles.
- Exactly 6 slide headlines.
- Slide 1 under 14 words.
- Slides 2–6 each limited to 15 seconds of speech.
- No generic “5 stories you need to see…” opener.

## Audio — APPROVED — 8/10

Stage 3 is approved after successful local generation and manual QC. Narration only: no music or sound effects.

### Audio engine

- Chatterbox is the approved local TTS engine.
- The code uses the installed ChatterboxTurboTTS model on the available device.
- Do not pass unsupported arguments such as nano=True.
- The model runs locally; there is no paid TTS API or cloud audio generation.
- If audio_reference.wav exists in the repo root, it is used as the narrator reference. AUDIO_REFERENCE may override that path.
- Reference audio conditioning is prepared once at the start of an Audio run and reused for all slides.
- Reference audio is local-only and must not be committed.

### Delivery and timing

- Generate audio separately for every approved Scriptwriter slide.
- Keep narrator identity consistent while varying delivery modestly by slide.
- Slide 1 receives a stronger opening delivery.
- Final slides receive a small payoff emphasis.
- Questions/exclamations receive slightly more expression.
- Numeric/factual slides receive slightly slower pacing.
- Chatterbox randomness is reseeded per run and slide so Redo Audio produces a genuinely new take.
- Preserve Scriptwriter words exactly; Audio does not rewrite the story.
- Add a small natural pause between slides.
- Use the 65-word Scriptwriter limit as the primary protection for a Short under 30 seconds.
- If generated narration is only marginally above 30 seconds, apply at most a slight time-stretch before failing.
- Generate full.wav plus one slide_XX.wav per slide.
- Local generated files live under generated_audio/ and are not committed.
- Output paths are derived from script content so Redo Audio replaces the current take rather than creating uncontrolled file growth.

### Audio test flow

1. User approves the Scriptwriter version.
2. Dashboard moves to Audio.
3. User clicks Generate Audio to start local Chatterbox narration.
4. Dashboard previews the complete Short and every slide.
5. User manually approves Audio.
6. Redo Audio regenerates narration without changing Scriptwriter text.
7. Subtitles remain disabled until Stage 4 is built.

### Current status

- Chatterbox is installed manually in the same existing local project environment.
- It is intentionally not added to CI's lightweight requirements.txt.
- Turbo model weights are cached locally after the successful first generation.
- The Windows Hugging Face symlink warning does not block use.
- No Hugging Face token is required by the factory.
- A local startup issue caused by the Perth watermarker dependency was resolved in the environment before Audio approval. No project wrapper or extra factory service was added.
- Audio is approved at 8/10. Reopen only for a later requirement, quality issue or regression.

## Later stages

Subtitles, Visuals, Renderer and Upload are disabled. Preserve their existing functions and handovers unless explicitly requested.

## Current files

- PROJECT_CONTEXT.md — current source of truth.
- topic_fetcher.py — completed Topic Fetcher.
- scriptwriter.py — source-first, desk-aware Scriptwriter with the channel editorial fingerprint, explicit three-choice editorial-angle selection, selected-angle-authoritative generation, Custom angle support and progressively stricter script redo passes.
- app.py — Test dashboard through Audio; stage imports remain local; editorial angles are presented before each Scriptwriter generation; selected story_angle is retained through QC and Audio handoff.
- audio.py — local Chatterbox narration for approved Scriptwriter slides; approved 8/10.
- tests/test_topic_fetcher.py — Topic Fetcher tests; the raw-GNews-URL test uses a current-time fixture so it cannot expire merely because the calendar date changes.
- tests/test_scriptwriter.py — Scriptwriter and editorial-angle tests.
- tests/test_audio.py — Audio dependency-loading and input validation tests.
- .github/workflows/test.yml — deterministic CI.
- requirements.txt — lightweight factory dependencies; Chatterbox is installed manually in the local environment.
- .gitignore — excludes local Audio outputs and narrator reference audio.

## CI

CI must not depend on live GNews availability or a minimum current-story count.

Do not merge a red commit.
