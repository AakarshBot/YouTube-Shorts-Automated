import streamlit as st
from topic_fetcher import GENRES, fetch_topics

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
.headline{border:1px solid var(--line);padding:10px 12px;border-radius:12px;background:var(--card);margin:6px 0}
.meta{color:var(--muted);font-size:.78rem;margin-top:5px}
div.stButton>button{background:#fffdf8;color:#171915;border:1px solid #cfcabe;border-radius:999px;box-shadow:none}
div.stButton>button:hover{background:#f0ede5;color:#171915;border-color:#aaa599}
div.stButton>button[kind="primary"]{background:#e8e3d8;color:#171915;border-color:#bdb6a8}
div.stButton>button[kind="primary"]:hover{background:#ddd7ca;color:#171915}
div.stButton>button:disabled{background:#efede8;color:#8a877f;border-color:#ddd9d0;opacity:1}
</style>
""", unsafe_allow_html=True)

st.session_state.setdefault("page", "home")
st.session_state.setdefault("genre", None)
st.session_state.setdefault("topics", [])
st.session_state.setdefault("seen_urls", set())

def go(page, genre=None):
    st.session_state.page, st.session_state.genre = page, genre
    if page != "topics":
        st.session_state.topics = []
        st.session_state.seen_urls = set()
    st.rerun()

if st.session_state.page == "home":
    st.title("YouTube Shorts Automated")
    st.markdown('<div class="sub">Build, test and publish Shorts through a controlled production pipeline.</div>', unsafe_allow_html=True)
    a, b = st.columns(2)
    with a:
        st.subheader("Test")
        st.caption("Build and approve functions one stage at a time.")
        if st.button("Enter Test →", type="primary", use_container_width=True):
            go("formats")
    with b:
        st.subheader("Live")
        st.caption("Production pipeline will be enabled after Test approval.")
        st.button("Live — coming later", disabled=True, use_container_width=True)

elif st.session_state.page == "formats":
    st.button("← Home", on_click=go, args=("home",))
    st.title("Choose a format")
    if st.button("Deep-Dive", type="primary", use_container_width=True):
        go("sports")
    st.caption("More formats — Top-5, Did You Know and others — will be added later.")

elif st.session_state.page == "sports":
    st.button("← Formats", on_click=go, args=("formats",))
    st.title("Choose a genre")
    for genre in GENRES:
        if st.button(genre, use_container_width=True):
            go("topics", genre)

else:
    st.button("← Genres", on_click=go, args=("sports",))
    st.title(st.session_state.genre)
    st.markdown('<div class="stage"><span class="active">01 Topic Fetcher</span><span>02 Scriptwriter</span><span>03 Audio</span><span>04 Subtitles</span><span>05 Visuals</span><span>06 Renderer</span><span>07 Upload</span></div>', unsafe_allow_html=True)

    topics = st.session_state.topics
    if not topics:
        if st.button("Fetch stories", type="primary"):
            with st.spinner("Finding current stories…"):
                st.session_state.topics = fetch_topics(st.session_state.genre)
            st.session_state.seen_urls = {
                headline["url"]
                for item in st.session_state.topics
                for headline in item["headlines"]
            }
        topics = st.session_state.topics

    if topics:
        if st.button("Search 20 more", type="primary", use_container_width=True):
            with st.spinner("Searching for more stories…"):
                more = fetch_topics(st.session_state.genre, exclude_urls=st.session_state.seen_urls)
            by_topic = {item["topic"]: item for item in topics}
            for item in more:
                if item["topic"] in by_topic:
                    by_topic[item["topic"]]["headlines"].extend(item["headlines"])
                else:
                    topics.append(item)
            st.session_state.topics = topics
            st.session_state.seen_urls.update(
                headline["url"]
                for item in more
                for headline in item["headlines"]
            )

        st.caption(f"{len(topics)} {('country' if 'Cricket' in st.session_state.genre else 'sport')} pills")
        for item in topics:
            with st.expander(f"{item['topic']} · {len(item['headlines'])} headlines"):
                for h in item["headlines"]:
                    st.markdown(f'<div class="headline">{h["title"]}</div>', unsafe_allow_html=True)
                    st.markdown(f"<div class='meta'>{h['publisher']} · {h['published_at'][:16].replace('T',' ')} · <a href='{h['url']}' target='_blank'>Source</a></div>", unsafe_allow_html=True)
    else:
        st.info("Run Topic Fetcher to load current stories.")
