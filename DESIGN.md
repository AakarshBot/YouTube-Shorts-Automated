# DESIGN — Topic Fetcher, Scriptwriter, and Audio Maker

**Status:** Design baseline for an experimental repository. This file describes intended behaviour and records the code/history audit. It is not an instruction to deploy this repository as the next production factory.

**Scope:** Three functions only: Topic Fetcher, Scriptwriter, and Audio Maker. The future production factory will be a new repository. This repository is a place to research, prototype, compare and validate individual functions before deliberately transferring approved work.

## 1. Rules for this experiment

- Read this file before changing or building any function. Re-check the linked source files and relevant commit history; do not treat a summary as a substitute for source inspection.
- Do not change the current Audio implementation while designing Topic Fetcher or Scriptwriter. The user reports that audio generation was working well before the global-Python package migration discussed in chat. Preserve that code as the reference implementation unless the user explicitly approves a change.
- Do not run local installation, upgrade, downgrade, uninstall, environment cleanup or rollback commands unless the user explicitly asks. The user is abandoning the current local factory run and does not want further random package installations.
- Do not tell the user to test a live story in this repository just because compilation and mocked tests pass.
- Keep production and experimentation separate. Nothing in this repository should publish or auto-approve content. All editorial and audio approvals remain manual.
- Keep implementations direct and small. Avoid wrappers, compatibility layers, generic frameworks, duplicated passes, helper/dependency bloat, silent fallbacks and unnecessary API providers. Prove a need before proposing an extra dependency, and obtain permission before adding it.
- Use explicit inputs, outputs, failure states and deterministic tests. Never describe a mocked test as proof of live-source quality, live model quality or working local TTS.
- Do not copy whole files or entire architectures from another repository. Compare ideas, then design the smallest system that meets the requirements here.
- Keep secrets out of source control. Do not request, print or commit the user's API keys, .env file, reference audio or generated audio.
- The user's stated preference is a simple, normal launch path. Do not alter the user's shared Python installation to make a project work. Discuss the dependency strategy and its trade-offs before touching any environment.

## 2. Repository audit

The GitHub integration returned these eight user-owned repositories. Source-level review focused on the three Shorts factories and the educational topic-discovery modules. The remaining repositories were checked at the repository-root level and did not show equivalent pipeline modules.

### User's repositories

| Repository | Relevant files inspected | What to use as design input |
|---|---|---|
| [YouTube-Shorts-Automated](https://github.com/AakarshBot/YouTube-Shorts-Automated) | topic_fetcher.py, scriptwriter.py, audio.py, tests, PROJECT_CONTEXT.md, requirements.txt, workflow and Audio history | Current multi-desk handoff, editorial-angle-first writer, selected-source retrieval, exact Audio code baseline and existing user-approved constraints. This is the experiment repo. |
| [Final-Shorts](https://github.com/AakarshBot/Final-Shorts) | topic_fetcher.py, universal_script_writer.py, script_writer.py, audio.py, PROJECT_CONTEXT.md | Mature topic filtering and event grouping; separate all-desk writer versus specialist cricket writer; bounded source research and validation. Its Audio implementation uses Edge-TTS and is **not** the same Chatterbox Turbo implementation in the experiment repo. |
| [viral-shorts-factory](https://github.com/AakarshBot/viral-shorts-factory) | story_ranker.py, event_discovery_runtime.py, research_runtime.py, script_runtime.py, audio_runtime.py, audio_direction_runtime.py, WORKFLOW_SPEC.md | Stronger examples of source quality, freshness, event identity, novelty/history checks, candidate diversity, narrative validation and measured audio timing. The very large ranking/runtime framework should not be transplanted wholesale. |
| [education_factory](https://github.com/AakarshBot/education_factory) | demand_discovery.py, topic_scorer.py, concept_generator.py | Demand-signal collection and explicit weighted topic dimensions can inform a future educational desk. Its exam/subject priorities are domain-specific and must not be applied blindly to news or sports. |
| [val](https://github.com/AakarshBot/val) | Root inventory | Portfolio/site assets; no equivalent factory stages found at the root. |
| [aakars-portfolio](https://github.com/AakarshBot/aakars-portfolio) | Root inventory | Portfolio site; no equivalent factory stages found at the root. |
| [aakars-portfolio-v2](https://github.com/AakarshBot/aakars-portfolio-v2) | Root inventory | Portfolio site; no equivalent factory stages found at the root. |
| [aakars-portfolio-new](https://github.com/AakarshBot/aakars-portfolio-new) | Root inventory | Portfolio site; no equivalent factory stages found at the root. |

### External GitHub references inspected

- [AI-Reel-Factory — news.py](https://github.com/Shaan-alpha/AI-Reel-Factory/blob/main/src/news.py): useful patterns include preserving real feed URLs and publisher names, interleaving RSS sections so one feed does not dominate, bounded retries for temporary feed failures, and using a query-specific search for a selected story. The target channel's genre-specific policy should not be copied as a universal rule.
- [AI-Reel-Factory — scriptwriter.py](https://github.com/Shaan-alpha/AI-Reel-Factory/blob/main/src/scriptwriter.py) and [content-system design](https://github.com/Shaan-alpha/AI-Reel-Factory/blob/main/docs/05-content-system.md): useful principles include building analysis beyond a surface summary, enforcing measurable constraints in code rather than trusting the model, and keeping sources/disclosures out of model control. Its sarcastic impact-news voice is not a default for the user's multi-desk factory.
- [EngineerNV/vox-clone-pipeline — setup.ps1](https://github.com/EngineerNV/vox-clone-pipeline/blob/main/setup.ps1): demonstrates checking Python prerequisites and verifying/preloading Chatterbox explicitly. It is a setup reference, not a request to change the user's environment or force a virtual environment.
- [Chatterbox Turbo Streamlit example](https://github.com/amehrez/Chatterbox-TTS-Streamlit-UI-): useful only as a secondary example of model loading and audio generation. The existing user's working implementation remains authoritative over a third-party demo.

Research is a design comparison, not a claim that each upstream project is bug-free or that its full codebase was audited. If a future implementation depends on a particular external function, inspect that exact file, its tests and its relevant history before relying on it.

## 3. Audio Maker — preserve the known-good code baseline

### Exact source version

The last commit that changed this repository's Audio source file was:

- Commit: [cc0e15434b0dff81c1d9ebf2808cc3829644450e — “Remove unused Audio model state”](https://github.com/AakarshBot/YouTube-Shorts-Automated/commit/cc0e15434b0dff81c1d9ebf2808cc3829644450e)
- The current main-branch Audio source has the same blob as that commit: **4ae4ce5d2db36fe75ea31798217dcb5d8ba10daa**.
- Exact file: [audio.py at the identified commit](https://github.com/AakarshBot/YouTube-Shorts-Automated/blob/cc0e15434b0dff81c1d9ebf2808cc3829644450e/audio.py).
- The project context recorded Audio as **approved, 8/10**, after successful local audio generation and manual QC. That approval predates the global-Python installation work in chat.

The global package installations discussed in chat targeted the normal Python 3.11 interpreter. They were package-environment changes, not commits to audio.py. Keep the identified source file unchanged. The design/code baseline is identified; GitHub by itself cannot guarantee the state of any local Python environment.

### Runtime versions recorded from the existing local project environment

The user previously reported these versions from the project's .venv:

- Chatterbox TTS: **0.1.7**
- PyTorch: **2.6.0+cpu**
- Torchaudio: **2.6.0** (the runtime printed 2.6.0+cpu)
- Librosa: **0.11.0**
- CUDA available: **False**

These are historical observations from the existing project environment, not a new clean-install prescription. The exact original NumPy and Torchvision versions in that environment were not established in this audit. Do not invent them and do not attempt a package migration without the user's permission.

### Current Audio behaviour in audio.py

- Input is the approved Scriptwriter result and its slides. Audio must not rewrite, summarise or otherwise modify the approved narration.
- The Chatterbox Turbo stack is imported only when audio generation is requested, not at normal dashboard import time.
- Load Chatterbox Turbo lazily and reuse the model in-process after loading.
- Use the optional local narrator reference path, defaulting to the repository-root audio_reference.wav; AUDIO_REFERENCE may override it. Prepare reference conditioning at the start of an Audio run. Never commit the reference WAV.
- Generate each slide separately. Reseed by run and slide to let Redo Audio produce a different take; use restrained per-slide temperature variation to give the opening and ending a little emphasis.
- Put slide WAVs and full.wav beneath generated_audio/, with a content-derived directory name; create a short natural gap between slides and normalise the combined waveform.
- Target a Short around 30 seconds. Current behaviour attempts a maximum 1.05 time-stretch when raw narration exceeds 30 seconds and fails if it remains over 30.5 seconds. Do not silently broaden that limit.
- Provide full-track and per-slide previews; require the user to approve audio. Redo Audio may regenerate speech, but must not change the script.
- No music, sound effects, paid/cloud TTS or extra narration calls in the approved path.
- Existing tests cover lazy dependency loading and empty-slide validation. They do **not** prove the complete model can load and generate audio; manual audio generation and listening were the basis for the existing 8/10 approval.

**Audio design decision:** treat this exact code blob as the reference implementation. Do not replace it with Final-Shorts Edge-TTS or the larger multi-provider voice stack from viral-shorts-factory. Improvements to the new factory should copy its minimal, tested behaviour rather than rewrite the function without a demonstrated defect.

## 4. Topic Fetcher — proposed design

### Goal

Show the user a fresh, varied, relevant shortlist of real story candidates for the selected desk. The user selects the story; only then should article-resolution and deeper source-reading work begin. The fetcher proposes stories, not scripts.

### Inputs and output contract

Input should be the actual dashboard desk and, where appropriate, the selected sport/country/profile and the URLs or story IDs already shown. Use the literal handoff values from the dashboard rather than maintaining a second spelling of each desk.

Each selectable result should preserve, at minimum:

- A clear story headline and brief feed summary.
- The original feed URL, publisher/source name and published timestamp when supplied.
- The selected desk/profile context.
- A stable-enough story/event identity for exclusion and duplicate handling across searches.
- An optional concise reason the item qualified/ranked well, if it can be supplied without extra slow model calls.

Return a ranked list of distinct story candidates in the order the UI should display. Keep the contract small; do not introduce a new object framework unless the callers demonstrate a real need.

### Discovery flow

1. **Build desk-specific queries.** Query selection changes with the chosen desk, country and sport. Do not let a sports query or style bleed into Technology, Entertainment, Business & Finance, Gaming, Science & Space or News. Avoid one generic query set for every desk.
2. **Fetch current candidates concurrently with bounded work.** Google News/GNews is the current provider baseline. Preserve titles, descriptions, publishers, timestamps and feed links. Keep per-request timeouts and handle an individual failed query without blocking every other query.
3. **Apply inexpensive eligibility filters first.** Reject unrelated results, stale items, schedules, scorecards, standings, rankings, fixtures, archive/records pages, generic SEO pages and other utility results that do not report a genuine development. Use the title and article context rather than relying only on boilerplate descriptions.
4. **Normalise links and headlines carefully.** Remove exact duplicate URLs and obvious tracking variation without destroying meaningful publisher URL parameters. Never discard the original source URL used for the selected-story handoff.
5. **Cluster at event/story level.** Multiple publishers reporting the same event should not occupy the shortlist as separate choices. Equally, two genuinely different stories about the same person/team/tournament must remain separate. Exact URL matching alone is insufficient; title overlap alone is also insufficient. Use a small, testable event-identity approach informed by Final-Shorts and viral-shorts-factory rather than importing their entire clustering systems.
6. **Rank eligible stories.** Prioritise freshness and a material new development, then source/article usefulness, audience relevance, novelty and story potential. Use deterministic, understandable rules where possible. Ranking should not make up factual claims or hide why a low-quality candidate is being surfaced. Avoid a huge score stack, multiple LLM ranking calls or historical analytics dependencies in the first version.
7. **Diversify the displayed set.** Prevent one player, event, publisher or tournament from taking over the first screen when other good stories exist. Diversity is a reordering/filtering step, not a reason to remove a genuinely important story.
8. **Show the candidates and wait.** Do not resolve every Google News URL or scrape every publisher page during bulk discovery. That work is expensive and is only useful once the user has picked a story.
9. **Search More must produce new candidates.** It should widen/change the query batch and exclude both previously displayed story identities and URLs, then append new stories rather than replacing the first batch. Re-running the same feed limit with only URL exclusion is known to overlap heavily. Keep requests bounded and the response responsive.
10. **Fail transparently.** A provider outage should result in a clear empty/partial result and actionable retry, not fabricated stories. Do not require live GNews access or a minimum story count in CI.

### Desk-specific editorial constraints to preserve

- The current dashboard has Sports with Cricket — India / Pakistan / Sri Lanka / Asia, Cricket — Global, and Niche Sports — Global, plus News, Entertainment, Technology, Business & Finance, Gaming, and Science & Space.
- India cricket discovery may return up to 25 entity/tournament-grouped tiles; grouping helps the user find stories and must not merge separate events.
- Regional profiles should remain relevant to their selected country/profile. A Pakistan or Sri Lanka search should not be crowded out by India-only items.
- Global cricket stories should be genuinely important to the selected country/scope, not arbitrary local results.
- Niche Sports must stay niche-sport-focused and avoid drifting back into cricket.
- Avoid old tournament recaps as current news when the event finished weeks or months ago. A story about an older event is eligible only when there is a new current development.
- The general purpose of the shortlist is editorial opportunity, not just search-volume or name popularity.
- Search More should normally try to add about 20 new candidates, but returning fewer good results is preferable to padding with duplicates or junk. Do not claim 20 results if fewer pass the filters.

### Runtime and test plan

- Target the existing user expectation of a responsive initial search (roughly 20 seconds or less as a design target, not a guarantee across provider outages).
- Unit-test filtering, normalization, event grouping, ranking order, desk handoffs, country/profile separation, utility-page rejection, freshness and Search More exclusion with fixtures and mocked HTTP.
- Include tests where the same entity appears in different stories and must not be over-deduplicated.
- CI must not depend on real current headlines, network access or live provider ranking.
- A live-source review is a separate manual acceptance gate after deterministic tests pass.

## 5. Scriptwriter — proposed design

### Goal

Turn a selected, source-backed story into one short, fact-grounded narrative for the selected desk. The writer must understand the story before choosing the narrative; it must not merely expand the Topic Fetcher headline. Editorial choice remains with the user.

### End-to-end flow

1. **Read the selected source first.** Fetch and extract readable article text only after story selection. Record the source URL, publisher, title and whether the evidence is full article text or a limited summary. Handle HTTP redirects to publisher pages; never treat a Google News landing page as the publisher's article. Preserve the resolved publisher URL exactly.
2. **Label limited evidence honestly.** If article extraction fails, a title plus GNews description may be retained as a labelled fallback, but it must not be passed off as the full article. Do not claim a full source was read when only a feed snippet was available.
3. **Assess evidence sufficiency before drafting.** If the story lacks enough facts or context, conduct one bounded related-source search using the existing provider. Read usable reports and combine them with the original evidence. If still insufficient, offer a field for the user to provide source URLs. If two attempts yield no usable material, stop and explain why; do not invent a story to force the next stage.
4. **Separate evidence from editorial angle.** Generate exactly three meaningfully different story angles based on the collected evidence. Each option includes a short title, a description and its evidence basis. Do not write the script until the user chooses an angle or enters a Custom angle.
5. **Make the chosen angle authoritative.** Write from scratch using the selected angle, not the original headline's most obvious summary framing. Reorder and synthesise facts around that angle. Use the real desk value to choose the editorial approach; do not hard-code the whole Scriptwriter as a cricket writer.
6. **Produce the complete script and packaging.** The initial ready output includes a story-specific 3–4 word opening screen headline, 4–5 narration slides, at least two YouTube title options, a natural description, relevant hashtags and a story-specific first comment. Packaging comes after the story and angle are understood.
7. **Validate objective constraints deterministically.** Reject malformed outputs, missing voiceovers, duplicate/repeated slides, unsupported field types, wrong slide counts, too-long narration or missing packaging. Use a constrained JSON schema, then validate it in Python. Do not trust prompt instructions alone for measurable rules.
8. **Show manual QC.** Every script field must be editable, with the ability to approve as-is. Never hide or silently substitute a failed model result. Keep source insufficiency, article-read errors and model/API/structured-output errors distinct.
9. **Redo deliberately.** Redo starts by proposing three new angles from the current evidence and prior draft. Each subsequent redo is stricter about changing the lead fact, central question and narrative order. Once an angle is selected, regenerate the script only; retain titles, description, hashtags and first comment unchanged and editable. Optional new URLs add evidence but do not trigger a new automatic-search loop merely because Redo was clicked. Keep original and revised versions available for comparison.

### Locked Scriptwriter constraints

- Exactly 4 or 5 slides. The first spoken slide must contain **fewer than 14 words**.
- Total narration must be **65 words or fewer** as the project's practical proxy for a Short under 30 seconds. Audio may slightly speed narration only when it is marginally over target; it is not a substitute for concise writing.
- Every slide contributes meaningful information. No padding, repetition, fake suspense, filler, generic introductions or artificial splitting just to satisfy slide count.
- Include the important named people, teams, organisations, dates, numbers, quotes and factual context needed for the chosen angle. If the source names a person, do not hide their identity behind labels like “legend” or “veteran”.
- Preserve the sense and tone of quoted remarks. Never fabricate a fact, number, quote, response, motive, criticism, controversy, prediction or consequence.
- Opening screen headline is exactly 3 or 4 words and is separate from the spoken opener.
- Titles must be accurate, distinct in framing, natural and concise. Descriptions, hashtags and comments must relate to the actual finished Short.
- No automatic publishing, automatic editorial approval or unlimited rewrite chains.

### Failure behaviour and model calls

- Make the selected desk and evidence explicit inputs.
- Use the existing direct Groq HTTP approach as the current repo baseline; do not add an SDK, generic model router or wrapper without approval.
- Load the Groq API key from the environment or root .env; never commit it.
- Keep retries bounded and purposeful. A validation failure may trigger a single corrective rewrite with the exact failure explained. Do not create a multi-agent critique tower or a stack of scoring systems.
- A failed related-source call must surface as a source-search error, not be silently relabelled “not enough evidence”.
- Do not trigger angle generation repeatedly on ordinary dashboard reruns.
- Tests must exercise all actual desk labels in the dashboard, not made-up fixture labels. Mock the model and web calls in CI; review real outputs manually before changing an approval rating.

### Minimum output shapes

Angle planning should return either:
- Ready: exactly three angle options, each with title, description and evidence basis; or
- Needs more sources: a concise reason and no angle options.

A ready script should carry:
- status and reason;
- selected story angle;
- opening screen headline;
- slide-by-slide voiceover;
- at least two YouTube title options;
- description, hashtags and first comment;
- source evidence/provenance retained for QC.

The exact implementation schema must be reconciled with the actual future dashboard handoff before coding. Do not add extra fields just to satisfy a hypothetical framework.

## 6. Shared contracts and ownership

Keep each function's responsibility narrow:

- **Topic Fetcher:** discovers, filters, groups, ranks and returns selectable candidates. It does not scrape every article or generate a script.
- **Scriptwriter:** reads the selected story, gathers only the needed evidence, proposes editorial angles, writes and validates narration/metadata, and exposes it for human QC. It does not change Audio or publish.
- **Audio Maker:** receives only the approved script, synthesises it, measures the resulting media, previews it and returns audio paths/duration for human approval. It does not select stories or edit narration.

Source URLs, original source metadata, selected desk, chosen angle, spoken slide order and approval state must survive the handoffs. Any future schema change must update the relevant tests and caller together; do not introduce duplicate competing representations.

## 7. Acceptance gates before a future factory adopts a function

A function is not accepted merely because a test suite passes.

1. Read the source-of-truth design and current relevant code first.
2. Compare the actual handoff fields and callers before writing code.
3. Add deterministic tests for success, malformed data, outages, duplicates, retries and relevant desk variations.
4. Run compilation and unit tests in a known test setup. Verify dependency/import checks with the exact interpreter that is intended to run the app.
5. For Topic Fetcher, separately evaluate fresh, representative live results and Search More novelty.
6. For Scriptwriter, separately inspect article evidence, all three angles and a real generated script for accuracy, narrative originality, chosen-angle fidelity, slide constraints and word count.
7. For Audio, separately generate and listen to a real sample, inspect per-slide/full outputs and measured duration, and verify that redo changes the take but not the words.
8. Preserve manual approvals and do not raise a score until the corresponding real-world gate has passed.
9. Update this design only when an intentional design decision changes. Do not append contradictory changelog notes.

## 8. Research links

### User repositories
- [YouTube-Shorts-Automated Topic Fetcher](https://github.com/AakarshBot/YouTube-Shorts-Automated/blob/main/topic_fetcher.py)
- [YouTube-Shorts-Automated Scriptwriter](https://github.com/AakarshBot/YouTube-Shorts-Automated/blob/main/scriptwriter.py)
- [YouTube-Shorts-Automated Audio source](https://github.com/AakarshBot/YouTube-Shorts-Automated/blob/cc0e15434b0dff81c1d9ebf2808cc3829644450e/audio.py)
- [YouTube-Shorts-Automated Audio approval/context](https://github.com/AakarshBot/YouTube-Shorts-Automated/blob/main/PROJECT_CONTEXT.md)
- [Final-Shorts Topic Fetcher](https://github.com/AakarshBot/Final-Shorts/blob/main/topic_fetcher.py)
- [Final-Shorts Universal Scriptwriter](https://github.com/AakarshBot/Final-Shorts/blob/main/universal_script_writer.py)
- [Final-Shorts Audio (Edge-TTS)](https://github.com/AakarshBot/Final-Shorts/blob/main/audio.py)
- [viral-shorts-factory story ranker](https://github.com/AakarshBot/viral-shorts-factory/blob/main/story_ranker.py)
- [viral-shorts-factory event discovery](https://github.com/AakarshBot/viral-shorts-factory/blob/main/event_discovery_runtime.py)
- [viral-shorts-factory script runtime](https://github.com/AakarshBot/viral-shorts-factory/blob/main/script_runtime.py)
- [viral-shorts-factory audio runtime](https://github.com/AakarshBot/viral-shorts-factory/blob/main/audio_runtime.py)
- [education_factory topic scorer](https://github.com/AakarshBot/education_factory/blob/main/topic_scorer.py)
- [education_factory demand discovery](https://github.com/AakarshBot/education_factory/blob/main/demand_discovery.py)

### External repositories
- [AI-Reel-Factory news discovery](https://github.com/Shaan-alpha/AI-Reel-Factory/blob/main/src/news.py)
- [AI-Reel-Factory Scriptwriter](https://github.com/Shaan-alpha/AI-Reel-Factory/blob/main/src/scriptwriter.py)
- [AI-Reel-Factory content system](https://github.com/Shaan-alpha/AI-Reel-Factory/blob/main/docs/05-content-system.md)
- [EngineerNV Chatterbox setup example](https://github.com/EngineerNV/vox-clone-pipeline/blob/main/setup.ps1)
- [Chatterbox Turbo Streamlit example](https://github.com/amehrez/Chatterbox-TTS-Streamlit-UI-)

