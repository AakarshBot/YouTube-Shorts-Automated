import streamlit as st

from scriptwriter import article_text, generate_script, validate_script
from topic_fetcher import DESKS, GENRES, fetch_topics

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
div.stButton>button{background:#fffdf8;color:#171915;border:1px solid #cfcabe;border-radius:999px;box-shadow:none}
div.stButton>button:hover{background:#f0ede5;color:#171915;border-color:#aaa599}
div.stButton>button[kind="primary"]{background:#e8e3d8;color:#171915;border-color:#bdb6a8}
div.stButton>button[kind="primary"]:hover{background:#ddd7ca;color:#171915}
div.stButton>button:disabled{background:#efede8;color:#8a877f;border-color:#ddd9d0;opacity:1}
</style>
""", unsafe_allow_html=True)

for key, value in {
    "page":"home","genre":None,"topics":[],"seen_urls":set(),
    "selected_story":None,"source_text":"","title_options":[],
    "approved_title":None,"script_versions":[],"script_approved":None,
    "title_error":None,"script_error":None,
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
            st.session_state.seen_urls = {
                h["url"] for item in st.session_state.topics for h in item["headlines"]
            }
            st.rerun()

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
            st.session_state.seen_urls.update(
                h["url"] for item in more for h in item["headlines"]
            )
            st.rerun()

        st.caption(f"{len(topics)} {pill} pills")
        for item in topics:
            grouped = "groups" in item
            count = len(item["groups"]) if grouped else len(item["headlines"])
            label = "title pills" if grouped else "headlines"
            with st.expander(f"{item['topic']} · {count} {label}"):
                sections = item["groups"] if grouped else [item]
                for section in sections:
                    panel = (
                        st.expander(
                            f"{section['topic']} · {len(section['headlines'])} headlines"
                        )
                        if grouped
                        else st.container()
                    )
                    with panel:
                        for index, h in enumerate(section["headlines"]):
                            st.markdown(
                                f'<div class="headline">{h["title"]}</div>',
                                unsafe_allow_html=True,
                            )
                            st.markdown(
                                f"<div class='meta'>{h['publisher']} · {h['published_at'][:16].replace('T',' ')} · <a href='{h['url']}' target='_blank'>Source</a></div>",
                                unsafe_allow_html=True,
                            )
                            if st.button(
                                "Use this story →",
                                key=f"pick-{h['url']}-{index}",
                            ):
                                st.session_state.selected_story = h
                                st.session_state.source_text = ""
                                    st.session_state.approved_title = None
                            st.session_state.approved_version = None
                                    st.session_state.approved_version = None
                                st.session_state.script_versions = []
                                        st.session_state.script_error = None
                                st.session_state.page = "scriptwriter"
                                st.rerun()

elif st.session_state.page == "scriptwriter":
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
        st.markdown(
            f"<div class='meta'>{story['publisher']} · <a href='{story['url']}' target='_blank'>Source</a></div>",
            unsafe_allow_html=True,
        )

        if not st.session_state.script_versions and not st.session_state.script_error:
            with st.spinner("Reading the source and writing the Short…"):
                try:
                    source = st.session_state.source_text or article_text(story)
                    st.session_state.source_text = source
                    result = generate_script(story, source)
                    errors = validate_script(result)
                    if errors:
                        raise RuntimeError(" · ".join(errors))
                    st.session_state.script_versions = [result]
                except Exception as exc:
                    st.session_state.script_error = str(exc)

        if st.session_state.script_error and not st.session_state.script_versions:
            st.error(st.session_state.script_error)
            if st.button("Try again", type="primary"):
                st.session_state.script_error = None
                st.rerun()

        if st.session_state.script_versions:
            for index, version in enumerate(st.session_state.script_versions):
                st.subheader(f"Version {index + 1}")
                st.markdown(
                    f'<div class="script-card"><div class="screen-headline">{version["opening_headline"]}</div></div>',
                    unsafe_allow_html=True,
                )
                for number, slide in enumerate(version["slides"], 1):
                    st.markdown(
                        f'<div class="script-card"><h4>Slide {number}</h4><div>{slide["voiceover"]}</div></div>',
                        unsafe_allow_html=True,
                    )

                st.subheader("Title options")
                choice = st.selectbox(
                    "Choose the strongest title",
                    version["titles"],
                    index=0,
                    key=f"title-{index}",
                )
                st.markdown("**Description**")
                st.write(version["description"])
                st.markdown("**Hashtags**")
                st.write(" ".join(version["hashtags"]))
                st.markdown("**First comment**")
                st.write(version["first_comment"])

                if st.session_state.approved_version == index:
                    st.success(
                        f"Version {index + 1} approved · {st.session_state.approved_title}"
                    )
                elif st.button(
                    f"Approve Version {index + 1}",
                    key=f"approve-script-{index}",
                    type="primary",
                    use_container_width=True,
                ):
                    st.session_state.approved_version = index
                    st.session_state.approved_title = choice
                    st.session_state.script_error = None
                    st.rerun()

            if st.session_state.script_error:
                st.error(st.session_state.script_error)

            if (
                st.session_state.approved_version is None
                and len(st.session_state.script_versions) == 1
            ):
                if st.button(
                    "Improve / Re-run",
                    type="primary",
                    use_container_width=True,
                ):
                    previous = st.session_state.script_versions[0]
                    st.session_state.script_error = None
                    with st.spinner("Writing a different version…"):
                        try:
                            result = generate_script(
                                story,
                                st.session_state.source_text,
                                previous=previous,
                            )
                            errors = validate_script(result)
                            if errors:
                                raise RuntimeError(" · ".join(errors))
                            st.session_state.script_versions.append(result)
                        except Exception as exc:
                            st.session_state.script_error = str(exc)
                    st.rerun()

