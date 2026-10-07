import streamlit as st

st.set_page_config(page_title="YouTube Shorts Automated", page_icon="▶", layout="wide")

st.markdown("""
<style>
:root{--bg:#f6f4ef;--card:#fffdf8;--ink:#171915;--muted:#6b7068;--line:#dedbd1}
.stApp{background:var(--bg);color:var(--ink)}
.block-container{max-width:1100px;padding:42px 34px 64px}
h1{font-size:2.5rem;letter-spacing:-.04em}
.sub{color:var(--muted);margin-top:-10px}
.stage{display:flex;gap:8px;flex-wrap:wrap;margin:24px 0}
.stage span{border:1px solid var(--line);padding:8px 12px;border-radius:999px;background:var(--card);font-size:.82rem}
.stage .active{background:var(--ink);color:white;border-color:var(--ink)}
.stage .done{background:#e8e3d8}
.headline{border:1px solid var(--line);padding:10px 12px;border-radius:12px;background:var(--card);margin:6px 0}
.meta{color:var(--muted);font-size:.78rem;margin-top:5px}
.script-card{border:1px solid var(--line);padding:18px;border-radius:16px;background:var(--card);margin:10px 0}
.script-card h4{margin:0 0 8px}
.screen-headline{font-size:2rem;font-weight:700;letter-spacing:-.03em}
.angle-card{border:1px solid var(--line);padding:16px;border-radius:16px;background:var(--card);min-height:235px}
.angle-card.selected{border-color:var(--ink);box-shadow:inset 0 0 0 1px var(--ink)}
.angle-title{font-size:1.15rem;font-weight:700;margin-bottom:8px}
.angle-evidence{color:var(--muted);font-size:.84rem;margin-top:10px}
div.stButton>button{background:#fffdf8;color:#171915;border:1px solid #cfcabe;border-radius:999px;box-shadow:none}
div.stButton>button:hover{background:#f0ede5;color:#171915;border-color:#aaa599}
div.stButton>button[kind="primary"]{background:#e8e3d8;color:#171915;border-color:#bdb6a8}
div.stButton>button[kind="primary"]:hover{background:#ddd7ca;color:#171915}
div.stButton>button:disabled{background:#efede8;color:#8a877f;border-color:#ddd9d0;opacity:1}
.stTextInput input,.stTextArea textarea{background:#fffdf8 !important;color:#171915 !important;border-color:#cfcabe !important}
.stTextInput input:focus,.stTextArea textarea:focus{background:#fffdf8 !important;color:#171915 !important;border-color:#aaa599 !important;box-shadow:none !important}
.stTextInput input::placeholder,.stTextArea textarea::placeholder{color:#8a877f !important}
.stSelectbox [data-baseweb="select"]>div{background:#fffdf8 !important;color:#171915 !important;border-color:#cfcabe !important}
.stSelectbox [data-baseweb="select"] span{color:#171915 !important}
.stSelectbox label,.stTextInput label,.stTextArea label{color:#171915 !important}
</style>
""", unsafe_allow_html=True)

for key, value in {
    "page": "home",
    "genre": None,
    "topics": [],
    "seen_urls": set(),
    "selected_story": None,
    "source_evidence": [],
    "script_versions": [],
    "approved_title": None,
    "approved_version": None,
    "script_error": None,
    "writer_status": None,
    "writer_reason": None,
    "auto_sources_attempted": False,
    "manual_sources_attempted": False,
    "editorial_angles": [],
    "selected_editorial_angle": None,
    "custom_editorial_angle": "",
    "angle_mode": None,
    "angle_error": None,
    "angle_reason": None,
    "audio_result": None,
    "audio_error": None,
    "audio_approved": False,
    "audio_run": 1,
}.items():
    st.session_state.setdefault(key, value)


if st.session_state.page == "home":
    st.title("YouTube Shorts Automated")
    st.markdown('<div class="sub">Build, test and publish Shorts through a controlled production pipeline.</div>', unsafe_allow_html=True)
    a, b = st.columns(2)
    with a:
        st.subheader("Test")
        st.caption("Build and approve functions one stage at a time.")
        if st.button("Enter Test →", type="primary", use_container_width=True):
            st.session_state.page = "formats"
            st.rerun()
    with b:
        st.subheader("Live")
        st.caption("Production pipeline will be enabled after Test approval.")
        st.button("Live — coming later", disabled=True, use_container_width=True)

elif st.session_state.page == "formats":
    if st.button("← Home"):
        st.session_state.page = "home"
        st.rerun()
    st.title("Choose a format")
    if st.button("Deep-Dive", type="primary", use_container_width=True):
        st.session_state.page = "deep-dive"
        st.rerun()
    st.caption("More formats — Top-5, Did You Know and others — will be added later.")

elif st.session_state.page == "deep-dive":
    from topic_fetcher import DESKS

    if st.button("← Formats"):
        st.session_state.page = "formats"
        st.rerun()
    st.title("Deep-Dive")
    for desk in DESKS:
        if st.button(desk, use_container_width=True):
            st.session_state.topics = []
            st.session_state.seen_urls = set()
            if desk == "Sports":
                st.session_state.page = "sports"
            else:
                st.session_state.genre = desk
                st.session_state.page = "topics"
            st.rerun()

elif st.session_state.page == "sports":
    from topic_fetcher import DESKS

    if st.button("← Deep-Dive"):
        st.session_state.page = "deep-dive"
        st.rerun()
    st.title("Sports")
    for genre in DESKS["Sports"]:
        if st.button(genre, use_container_width=True):
            st.session_state.genre = genre
            st.session_state.topics = []
            st.session_state.seen_urls = set()
            st.session_state.page = "topics"
            st.rerun()

elif st.session_state.page == "topics":
    from topic_fetcher import GENRES, fetch_topics

    if st.session_state.genre in GENRES:
        if st.button("← Sports"):
            st.session_state.page = "sports"
            st.rerun()
    else:
        if st.button("← Deep-Dive"):
            st.session_state.page = "deep-dive"
            st.rerun()

    st.title(st.session_state.genre)
    st.markdown('<div class="stage"><span class="active">01 Topic Fetcher</span><span>02 Scriptwriter</span><span>03 Audio</span><span>04 Subtitles</span><span>05 Visuals</span><span>06 Renderer</span><span>07 Upload</span></div>', unsafe_allow_html=True)

    if not st.session_state.topics:
        if st.button("Fetch stories", type="primary"):
            with st.spinner("Finding current stories…"):
                st.session_state.topics = fetch_topics(st.session_state.genre)
            st.session_state.seen_urls = {h["url"] for item in st.session_state.topics for h in item["headlines"]}

    topics = st.session_state.topics
    if not topics:
        st.info("No fresh qualifying stories found.")
    else:
        pill = "country" if st.session_state.genre in GENRES else "topic"
        if st.button("Search 20 more", type="primary", use_container_width=True):
            with st.spinner("Searching for more stories…"):
                more = fetch_topics(st.session_state.genre, exclude_urls=st.session_state.seen_urls)
            by_topic = {item["topic"]: item for item in topics}
            for item in more:
                if item["topic"] in by_topic:
                    target = by_topic[item["topic"]]
                    target["headlines"].extend(item["headlines"])
                    if "groups" in item:
                        groups = {group["topic"]: group for group in target.get("groups", [])}
                        for group in item["groups"]:
                            if group["topic"] in groups:
                                groups[group["topic"]]["headlines"].extend(group["headlines"])
                            else:
                                target.setdefault("groups", []).append(group)
                else:
                    topics.append(item)
            st.session_state.topics = topics
            st.session_state.seen_urls.update(h["url"] for item in more for h in item["headlines"])

        st.caption(f"{len(topics)} {pill} pills")
        for item in topics:
            grouped = "groups" in item
            count = len(item["groups"]) if grouped else len(item["headlines"])
            label = "title pills" if grouped else "headlines"
            with st.expander(f"{item['topic']} · {count} {label}"):
                sections = item["groups"] if grouped else [item]
                for section in sections:
                    panel = st.expander(f"{section['topic']} · {len(section['headlines'])} headlines") if grouped else st.container()
                    with panel:
                        for index, h in enumerate(section["headlines"]):
                            st.markdown(f'<div class="headline">{h["title"]}</div>', unsafe_allow_html=True)
                            st.markdown(f"<div class='meta'>{h['publisher']} · {h['published_at'][:16].replace('T',' ')} · <a href='{h['url']}' target='_blank'>Source</a></div>", unsafe_allow_html=True)
                            if st.button("Use this story →", key=f"pick-{h['url']}-{index}"):
                                from gnews.utils.utils import resolve_url

                                selected = dict(h)
                                selected["url"] = resolve_url(selected["url"])
                                st.session_state.selected_story = selected
                                st.session_state.source_evidence = []
                                st.session_state.script_versions = []
                                st.session_state.approved_title = None
                                st.session_state.approved_version = None
                                st.session_state.script_error = None
                                st.session_state.writer_status = None
                                st.session_state.writer_reason = None
                                st.session_state.auto_sources_attempted = False
                                st.session_state.manual_sources_attempted = False
                                st.session_state.editorial_angles = []
                                st.session_state.selected_editorial_angle = None
                                st.session_state.custom_editorial_angle = ""
                                st.session_state.angle_mode = None
                                st.session_state.angle_error = None
                                st.session_state.angle_reason = None
                                st.session_state.audio_result = None
                                st.session_state.audio_error = None
                                st.session_state.audio_approved = False
                                st.session_state.audio_run = 1
                                st.session_state.page = "scriptwriter"
                                st.rerun()

elif st.session_state.page == "scriptwriter":
    from scriptwriter import article_text, find_related_sources, generate_script, manual_sources, suggest_editorial_angles, validate_editorial_angles, validate_script

    if st.button("← Topic Fetcher"):
        st.session_state.page = "topics"
        st.rerun()

    st.title("Scriptwriter")
    st.markdown('<div class="stage"><span class="done">01 Topic Fetcher</span><span class="active">02 Scriptwriter</span><span>03 Audio</span><span>04 Subtitles</span><span>05 Visuals</span><span>06 Renderer</span><span>07 Upload</span></div>', unsafe_allow_html=True)

    story = st.session_state.selected_story
    if not story:
        st.info("Select a headline in Topic Fetcher first.")
    else:
        st.subheader("Selected story")
        st.markdown(f'<div class="headline">{story["title"]}</div>', unsafe_allow_html=True)
        st.markdown(f"<div class='meta'>{story['publisher']} · <a href='{story['url']}' target='_blank'>Source</a></div>", unsafe_allow_html=True)

        if not st.session_state.script_versions and not st.session_state.editorial_angles and not st.session_state.script_error:
            with st.spinner("Reading the source and finding three editorial angles…"):
                try:
                    primary_error = None
                    if not st.session_state.source_evidence:
                        try:
                            primary = {
                                "title": story["title"],
                                "url": story["url"],
                                "publisher": story.get("publisher", ""),
                                "text": article_text(story),
                            }
                        except (RuntimeError, ValueError) as exc:
                            primary = None
                            primary_error = str(exc)
                        if primary:
                            st.session_state.source_evidence = [primary]

                    if st.session_state.source_evidence:
                        stage = "manual" if st.session_state.manual_sources_attempted else "automatic" if st.session_state.auto_sources_attempted else "primary"
                        result = suggest_editorial_angles(
                            story,
                            st.session_state.source_evidence,
                            st.session_state.genre,
                            source_stage=stage,
                        )
                        errors = validate_editorial_angles(result)
                        if errors:
                            raise RuntimeError(" · ".join(errors))
                        st.session_state.writer_status = result["status"]
                        st.session_state.writer_reason = result.get("reason") or None
                        if result["status"] == "ready":
                            st.session_state.editorial_angles = result["angles"]
                            st.session_state.angle_mode = "initial"

                    if (
                        primary_error
                        or (
                            st.session_state.writer_status == "needs_more_sources"
                            and not st.session_state.auto_sources_attempted
                        )
                    ):
                        st.session_state.auto_sources_attempted = True
                        with st.spinner("The story needs more context. Finding related sources…"):
                            related = find_related_sources(story)
                        if st.session_state.source_evidence:
                            st.session_state.source_evidence.extend(related)
                        else:
                            st.session_state.source_evidence = related
                        if related:
                            result = suggest_editorial_angles(
                                story,
                                st.session_state.source_evidence,
                                st.session_state.genre,
                                source_stage="automatic",
                            )
                            errors = validate_editorial_angles(result)
                            if errors:
                                raise RuntimeError(" · ".join(errors))
                            st.session_state.writer_status = result["status"]
                            st.session_state.writer_reason = result.get("reason") or None
                            if result["status"] == "ready":
                                st.session_state.editorial_angles = result["angles"]
                                st.session_state.angle_mode = "initial"
                        else:
                            st.session_state.writer_status = "needs_more_sources"
                            st.session_state.writer_reason = (
                                st.session_state.writer_reason
                                or primary_error
                                or "More source information is needed."
                            )
                except Exception as exc:
                    st.session_state.script_error = str(exc)

        if st.session_state.script_error and not st.session_state.script_versions:
            st.error(st.session_state.script_error)
            if st.button("Try again", type="primary"):
                st.session_state.script_error = None
                st.session_state.angle_error = None
                st.rerun()

        if st.session_state.writer_status == "needs_more_sources" and not st.session_state.editorial_angles and not st.session_state.script_versions:
            st.warning("Not enough of a story yet")
            st.write(st.session_state.writer_reason or "More source information is needed to build a genuine Short.")
            urls = st.text_area("Additional source URLs", placeholder="Paste one or more URLs, one per line", key="initial-source-urls")
            if not st.session_state.manual_sources_attempted and st.button("Add sources and build editorial angles", type="primary", use_container_width=True):
                st.session_state.manual_sources_attempted = True
                with st.spinner("Reading the additional sources and finding three editorial angles…"):
                    added = manual_sources(urls.splitlines())
                    st.session_state.source_evidence.extend(added)
                    if added:
                        try:
                            result = suggest_editorial_angles(
                                story,
                                st.session_state.source_evidence,
                                st.session_state.genre,
                                source_stage="manual",
                            )
                            errors = validate_editorial_angles(result)
                            if errors:
                                raise RuntimeError(" · ".join(errors))
                            st.session_state.writer_status = result["status"]
                            st.session_state.writer_reason = result.get("reason") or None
                            if result["status"] == "ready":
                                st.session_state.editorial_angles = result["angles"]
                                st.session_state.angle_mode = "initial"
                        except Exception as exc:
                            st.session_state.script_error = str(exc)
                    else:
                        st.session_state.writer_status = "needs_more_sources"
                        st.session_state.writer_reason = "The additional URLs could not provide readable source information."

        if st.session_state.editorial_angles and st.session_state.angle_mode in {"initial", "redo"} and not st.session_state.script_error:
            mode_label = "Choose what this Short is actually about" if st.session_state.angle_mode == "initial" else "Choose a new editorial angle"
            st.markdown(f"### {mode_label}")
            st.caption("Three research-backed choices. They are deliberately different story lenses, not three versions of the same summary.")

            columns = st.columns(3)
            for index, angle in enumerate(st.session_state.editorial_angles):
                selected = st.session_state.selected_editorial_angle == angle
                with columns[index]:
                    st.markdown(
                        f'<div class="angle-card {"selected" if selected else ""}">'
                        f'<div class="angle-title">{angle["title"]}</div>'
                        f'<div>{angle["description"]}</div>'
                        f'<div class="angle-evidence"><strong>Evidence:</strong> {angle["evidence_basis"]}</div>'
                        '</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button("Selected" if selected else "Choose", key=f"choose-angle-{st.session_state.angle_mode}-{index}", use_container_width=True):
                        st.session_state.selected_editorial_angle = angle
                        st.session_state.custom_editorial_angle = ""

            custom = st.text_area(
                "Custom angle",
                value=st.session_state.custom_editorial_angle,
                placeholder="Enter a specific editorial direction for the Short instead.",
                key=f"custom-angle-{st.session_state.angle_mode}",
                height=90,
            )
            st.session_state.custom_editorial_angle = custom
            chosen_angle = None
            if custom.strip():
                chosen_angle = {
                    "title": "Custom angle",
                    "description": custom.strip(),
                    "evidence_basis": "User supplied editorial direction.",
                }
            elif st.session_state.selected_editorial_angle:
                chosen_angle = st.session_state.selected_editorial_angle

            if st.session_state.angle_error:
                st.error(st.session_state.angle_error)

            if st.button(
                "Generate Script from selected angle",
                type="primary",
                use_container_width=True,
                disabled=chosen_angle is None,
                key=f"generate-script-from-angle-{st.session_state.angle_mode}",
            ):
                st.session_state.angle_error = None
                previous = st.session_state.script_versions[-1] if st.session_state.angle_mode == "redo" and st.session_state.script_versions else None
                stage = "manual" if st.session_state.manual_sources_attempted else "automatic" if st.session_state.auto_sources_attempted else "primary"
                with st.spinner("Writing the Short around the selected editorial angle…"):
                    try:
                        result = generate_script(
                            story,
                            st.session_state.source_evidence,
                            st.session_state.genre,
                            previous=previous,
                            source_stage=stage,
                            script_only=st.session_state.angle_mode == "redo",
                            angle=chosen_angle,
                            redo_level=len(st.session_state.script_versions),
                        )
                        if result["status"] == "ready" and previous:
                            result["titles"] = list(previous["titles"])
                            result["description"] = previous["description"]
                            result["hashtags"] = list(previous["hashtags"])
                            result["first_comment"] = previous["first_comment"]
                        errors = validate_script(result)
                        if errors:
                            raise RuntimeError(" · ".join(errors))
                        if result["status"] == "ready":
                            st.session_state.script_versions.append(result)
                            st.session_state.writer_status = "ready"
                            st.session_state.writer_reason = None
                            st.session_state.angle_mode = None
                            st.session_state.editorial_angles = []
                            st.session_state.selected_editorial_angle = None
                            st.session_state.custom_editorial_angle = ""
                        else:
                            st.session_state.writer_status = result["status"]
                            st.session_state.writer_reason = result.get("reason") or "More source information is needed."
                            st.session_state.editorial_angles = []
                            st.session_state.angle_reason = st.session_state.writer_reason
                            if st.session_state.angle_mode == "initial":
                                st.session_state.angle_mode = None
                    except Exception as exc:
                        st.session_state.script_error = str(exc)

        if st.session_state.script_versions:
            st.caption(f"Sources used: {len(st.session_state.source_evidence)}")
            for index, version in enumerate(st.session_state.script_versions):
                st.subheader(f"Version {index + 1}")
                angle = version.get("story_angle")
                st.markdown("### Editorial angle")
                if isinstance(angle, dict):
                    st.markdown(f'<div class="script-card"><strong>{angle.get("title", "Editorial angle")}</strong><br>{angle.get("description", "")}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="script-card">{angle}</div>', unsafe_allow_html=True)

                if st.session_state.approved_version == index:
                    st.markdown("### Opening headline")
                    st.markdown(
                        f'<div class="script-card"><div class="screen-headline">{version["opening_headline"]}</div></div>',
                        unsafe_allow_html=True,
                    )

                    st.markdown("### Voiceover")
                    for number, slide in enumerate(version["slides"], 1):
                        st.markdown(
                            f'<div class="script-card"><h4>Slide {number}</h4><div>{slide["voiceover"]}</div></div>',
                            unsafe_allow_html=True,
                        )

                    st.markdown("### YouTube titles")
                    for number, title in enumerate(version["titles"], 1):
                        st.markdown(f"**Title {number}**")
                        st.write(title)

                    st.markdown("### Description")
                    st.write(version["description"])

                    st.markdown("### Hashtags")
                    st.write(" ".join(version["hashtags"]))

                    st.markdown("### First comment")
                    st.write(version["first_comment"])

                    st.success(f"Version {index + 1} approved · {st.session_state.approved_title}")
                    continue

                st.markdown("### 1. Opening headline")
                opening_headline = st.text_input(
                    "Opening headline (3–4 words)",
                    value=version["opening_headline"],
                    key=f"qc-headline-{index}",
                )

                st.markdown("### 2. Voiceover")
                edited_slides = []
                for number, slide in enumerate(version["slides"], 1):
                    with st.container(border=True):
                        st.markdown(f"**Slide {number}**")
                        edited_slides.append({
                            "voiceover": st.text_area(
                                "Voiceover",
                                value=slide["voiceover"],
                                key=f"qc-slide-{index}-{number}",
                                height=100,
                                label_visibility="collapsed",
                            )
                        })

                st.markdown("### 3. YouTube titles")
                edited_titles = []
                for number, title in enumerate(version["titles"], 1):
                    edited_titles.append(
                        st.text_input(
                            f"Title {number}",
                            value=title,
                            key=f"qc-title-{index}-{number}",
                        )
                    )

                selected_title = st.selectbox(
                    "Strongest title to publish",
                    range(len(edited_titles)),
                    format_func=lambda number: edited_titles[number],
                    key=f"qc-choice-{index}",
                )

                st.markdown("### 4. Description")
                description = st.text_area(
                    "Description",
                    value=version["description"],
                    key=f"qc-description-{index}",
                    height=120,
                )

                st.markdown("### 5. Hashtags")
                hashtags_text = st.text_area(
                    "Hashtags",
                    value="\n".join(version["hashtags"]),
                    key=f"qc-hashtags-{index}",
                    height=90,
                    help="Use one hashtag per line.",
                )

                st.markdown("### 6. First comment")
                first_comment = st.text_area(
                    "First comment",
                    value=version["first_comment"],
                    key=f"qc-comment-{index}",
                    height=100,
                )

                st.markdown("### 7. Approval")
                if st.button(
                    f"Approve Version {index + 1}",
                    key=f"approve-script-{index}",
                    type="primary",
                    use_container_width=True,
                ):
                    edited = {
                        "status": version["status"],
                        "reason": version.get("reason", ""),
                        "story_angle": version.get("story_angle"),
                        "opening_headline": opening_headline,
                        "slides": edited_slides,
                        "titles": edited_titles,
                        "description": description,
                        "hashtags": [
                            item.strip()
                            for item in hashtags_text.replace(",", "\n").splitlines()
                            if item.strip()
                        ],
                        "first_comment": first_comment,
                    }
                    errors = validate_script(edited)
                    if errors:
                        st.error(" · ".join(errors))
                    else:
                        version.clear()
                        version.update(edited)
                        st.session_state.approved_version = index
                        st.session_state.approved_title = edited_titles[selected_title]
                        st.session_state.script_error = None
                        st.session_state.audio_result = None
                        st.session_state.audio_error = None
                        st.session_state.audio_approved = False
                        st.session_state.audio_run = 1
                        st.session_state.page = "audio"
                        st.rerun()

            if st.session_state.script_error:
                st.error(st.session_state.script_error)

            if st.session_state.approved_version is None:
                latest = st.session_state.script_versions[-1]
                redo_level = len(st.session_state.script_versions)
                st.markdown(f"### Redo script · pass {redo_level}")
                st.caption(
                    "Every redo is stricter than the previous one: it must move the editorial spine, lead and structure further away from the last version."
                )
                redo_urls = st.text_area(
                    "Additional source URLs (optional)",
                    placeholder="Paste one or more URLs, one per line. Leave blank to use the current sources.",
                    key="redo-source-urls",
                )

                if st.session_state.angle_mode != "redo":
                    if st.button("Build 3 stricter editorial angles", type="primary", use_container_width=True):
                        st.session_state.angle_error = None
                        with st.spinner("Finding three new editorial angles from the existing evidence…"):
                            try:
                                if redo_urls.strip():
                                    added = manual_sources(redo_urls.splitlines())
                                    if not added:
                                        raise RuntimeError("The additional URLs did not provide readable source information.")
                                    st.session_state.source_evidence.extend(added)
                                    stage = "manual"
                                else:
                                    stage = "manual" if st.session_state.manual_sources_attempted else "automatic" if st.session_state.auto_sources_attempted else "primary"
                                result = suggest_editorial_angles(
                                    story,
                                    st.session_state.source_evidence,
                                    st.session_state.genre,
                                    source_stage=stage,
                                    previous=latest,
                                    redo_level=redo_level,
                                )
                                errors = validate_editorial_angles(result)
                                if errors:
                                    raise RuntimeError(" · ".join(errors))
                                st.session_state.angle_mode = "redo"
                                st.session_state.editorial_angles = result["angles"] if result["status"] == "ready" else []
                                st.session_state.selected_editorial_angle = None
                                st.session_state.custom_editorial_angle = ""
                                st.session_state.angle_reason = result.get("reason") or None
                                st.session_state.writer_status = result["status"]
                                st.session_state.writer_reason = result.get("reason") or None
                            except Exception as exc:
                                st.session_state.angle_error = str(exc)

                if st.session_state.angle_mode == "redo" and st.session_state.angle_reason and not st.session_state.editorial_angles:
                    st.warning(st.session_state.angle_reason)
                    if st.button("Add sources and rebuild 3 stricter angles", type="primary", use_container_width=True):
                        st.session_state.angle_error = None
                        with st.spinner("Reading the new sources and finding three new editorial angles…"):
                            try:
                                added = manual_sources(redo_urls.splitlines())
                                if not added:
                                    raise RuntimeError("The additional URLs did not provide readable source information.")
                                st.session_state.source_evidence.extend(added)
                                result = suggest_editorial_angles(
                                    story,
                                    st.session_state.source_evidence,
                                    st.session_state.genre,
                                    source_stage="manual",
                                    previous=latest,
                                    redo_level=redo_level,
                                )
                                errors = validate_editorial_angles(result)
                                if errors:
                                    raise RuntimeError(" · ".join(errors))
                                st.session_state.editorial_angles = result["angles"] if result["status"] == "ready" else []
                                st.session_state.angle_reason = result.get("reason") or None
                                st.session_state.writer_status = result["status"]
                                st.session_state.writer_reason = result.get("reason") or None
                            except Exception as exc:
                                st.session_state.angle_error = str(exc)

elif st.session_state.page == "audio":
    if st.button("← Scriptwriter"):
        st.session_state.page = "scriptwriter"
        st.rerun()

    st.title("Audio")
    st.markdown('<div class="stage"><span class="done">01 Topic Fetcher</span><span class="done">02 Scriptwriter</span><span class="active">03 Audio</span><span>04 Subtitles</span><span>05 Visuals</span><span>06 Renderer</span><span>07 Upload</span></div>', unsafe_allow_html=True)

    approved_index = st.session_state.approved_version
    if approved_index is None or approved_index >= len(st.session_state.script_versions):
        st.error("Approve a Scriptwriter version first.")
    else:
        version = st.session_state.script_versions[approved_index]
        st.markdown(f'<div class="headline">{version["opening_headline"]}</div>', unsafe_allow_html=True)
        st.caption("Narration only. The approved script is the only Audio input.")

        if st.session_state.audio_result is None and st.session_state.audio_error is None:
            st.info("Audio is ready to generate locally from the approved Scriptwriter version.")
            if st.button("Generate Audio", type="primary", use_container_width=True):
                from audio import generate_audio

                with st.spinner("Generating narration locally…"):
                    try:
                        st.session_state.audio_result = generate_audio(version, st.session_state.audio_run)
                    except Exception as exc:
                        st.session_state.audio_error = str(exc)

        if st.session_state.audio_error:
            st.error(st.session_state.audio_error)
            if st.button("Try Audio Again", type="primary", use_container_width=True):
                st.session_state.audio_error = None
                st.rerun()

        result = st.session_state.audio_result
        if result:
            st.subheader("Full Short")
            st.audio(result["full_path"], format="audio/wav")
            st.caption(f'{result["model"]} · {result["reference"]} · {result["duration"]:.1f}s')

            st.subheader("Slide previews")
            for number, (slide, path) in enumerate(zip(version["slides"], result["slide_paths"]), 1):
                st.markdown(f'<div class="script-card"><h4>Slide {number}</h4><div>{slide["voiceover"]}</div></div>', unsafe_allow_html=True)
                st.audio(path, format="audio/wav")

            if st.session_state.audio_approved:
                st.success("Audio approved.")
            else:
                approve, redo = st.columns(2)
                with approve:
                    if st.button("Approve Audio", type="primary", use_container_width=True):
                        st.session_state.audio_approved = True
                with redo:
                    if st.button("Redo Audio", use_container_width=True):
                        st.session_state.audio_result = None
                        st.session_state.audio_error = None
                        st.session_state.audio_approved = False
                        st.session_state.audio_run += 1
                        st.rerun()

            if st.session_state.audio_approved:
                if st.button("Redo Audio", use_container_width=True):
                    st.session_state.audio_result = None
                    st.session_state.audio_error = None
                    st.session_state.audio_approved = False
                    st.session_state.audio_run += 1
                    st.rerun()
                st.button("Subtitles — coming later", disabled=True, use_container_width=True)
