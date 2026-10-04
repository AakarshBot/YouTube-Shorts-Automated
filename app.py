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
.meta{color:var(--muted);font-size:.78rem;margin-top:5px}
.stButton button{border-radius:999px}
</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state: st.session_state.page = "home"
if "genre" not in st.session_state: st.session_state.genre = None
if "topics" not in st.session_state: st.session_state.topics = []

def go(page, genre=None):
    st.session_state.page, st.session_state.genre = page, genre
    if page != "topics": st.session_state.topics = []
    st.rerun()

if st.session_state.page == "home":
    st.title("YouTube Shorts Automated")
    st.markdown('<div class="sub">Build, test and publish Shorts through a controlled production pipeline.</div>', unsafe_allow_html=True)
    a,b=st.columns(2)
    with a:
        st.subheader("Test")
        st.caption("Build and approve functions one stage at a time.")
        if st.button("Enter Test →", type="primary", use_container_width=True): go("formats")
    with b:
        st.subheader("Live")
        st.caption("Production pipeline will be enabled after Test approval.")
        st.button("Live — coming later", disabled=True, use_container_width=True)

elif st.session_state.page == "formats":
    st.button("← Home", on_click=go, args=("home",))
    st.title("Choose a format")
    if st.button("Deep-Dive", type="primary", use_container_width=True): go("sports")
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

    if st.button("Fetch 20 stories", type="primary"):
        with st.spinner("Finding current stories…"):
            st.session_state.topics = fetch_topics(st.session_state.genre)

    topics = st.session_state.topics
    if topics:
        st.caption(f"{len(topics)} topic pills")
        for item in topics:
            with st.expander(f"{item['topic']}  ·  {len(item['headlines'])} headlines"):
                for h in item["headlines"]:
                    st.markdown(f"**{h['title']}**")
                    st.markdown(f"<div class='meta'>{h['publisher']} · {h['published_at'][:16].replace('T',' ')} · <a href='{h['url']}' target='_blank'>Source</a></div>", unsafe_allow_html=True)
    else:
        st.info("Run Topic Fetcher to load the current 20-topic pool.")
