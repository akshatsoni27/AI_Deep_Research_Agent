"""Modern Streamlit interface for the multi-agent research pipeline."""

import re
import time
import traceback
import html
import textwrap

import streamlit as st

from Pipeline import run_research_pipeline


# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Signal — AI Research Desk",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================================
# HTML HELPER
# ----------------------------------------------------------------------------
# IMPORTANT: st.markdown(unsafe_allow_html=True) parses its input as Markdown
# first, then passes recognized HTML blocks through untouched. A blank line
# inside that string ends the "raw HTML" block, so anything after it gets
# re-parsed as Markdown — and any line indented 4+ spaces becomes a literal
# code block. That's what was causing HTML/CSS to print as text everywhere.
#
# render_html() fixes this by (1) dedenting so nothing starts at 4+ spaces,
# and (2) collapsing blank lines so the whole snippet stays one continuous
# HTML block.
# ============================================================================

def render_html(content: str) -> None:
    cleaned = textwrap.dedent(content).strip("\n")
    cleaned = "\n".join(line for line in cleaned.splitlines() if line.strip() != "")
    st.markdown(cleaned, unsafe_allow_html=True)


# ============================================================================
# MODERN DARK UI
# ============================================================================

render_html(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root {
        --bg: #070A12;
        --bg-soft: #0A0F1B;
        --card: #0D1220;
        --card-hover: #111827;
        --border: #1C2638;
        --border-light: #263247;
        --text: #F8FAFC;
        --text-soft: #CBD5E1;
        --muted: #8290A5;
        --purple: #8B5CF6;
        --purple-light: #A78BFA;
        --cyan: #22D3EE;
        --green: #34D399;
        --red: #FB7185;
        --gradient: linear-gradient(135deg, #8B5CF6 0%, #6366F1 45%, #22D3EE 100%);
    }
    html, body, [class*="css"] { font-family: "DM Sans", sans-serif; }
    .stApp {
        background:
            radial-gradient(circle at 85% 5%, rgba(139, 92, 246, 0.14), transparent 32%),
            radial-gradient(circle at 15% 30%, rgba(34, 211, 238, 0.06), transparent 26%),
            var(--bg);
        color: var(--text);
    }
    .block-container { max-width: 1450px; padding: 3.5rem 4rem 6rem; }
    h1, h2, h3, h4 { font-family: "Space Grotesk", sans-serif !important; color: var(--text) !important; }
    h1 {
        font-size: clamp(3rem, 6vw, 6.5rem) !important;
        line-height: 0.92 !important;
        letter-spacing: -0.055em !important;
        max-width: 900px;
        margin-bottom: 1.5rem !important;
    }
    h2 { letter-spacing: -0.025em; }
    p { color: var(--text-soft); }
    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        color: var(--purple-light);
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }
    .eyebrow::before {
        content: "";
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--cyan);
        box-shadow: 0 0 12px rgba(34, 211, 238, 0.85);
    }
    .hero-title {
        background: linear-gradient(120deg, #FFFFFF 0%, #D8CCFF 45%, #8BE8F5 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .lede { color: var(--muted); font-size: 1.05rem; line-height: 1.75; max-width: 680px; margin-bottom: 2rem; }
    .hero-rule { height: 1px; background: linear-gradient(90deg, transparent, var(--border-light), transparent); margin: 2.5rem 0 2rem; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #080C15 0%, #0A0F19 100%); border-right: 1px solid var(--border); }
    [data-testid="stSidebar"] * { color: var(--text-soft); }
    [data-testid="stSidebar"] h3 { color: white !important; }
    [data-testid="stSidebar"] .eyebrow { color: var(--purple-light); }
    [data-testid="stSidebar"] hr { border-color: var(--border); }
    [data-testid="stSidebar"] .stButton button {
        background: transparent;
        border: 1px solid transparent;
        color: var(--muted);
        text-align: left;
        border-radius: 8px;
        transition: background 0.2s ease, border 0.2s ease, color 0.2s ease;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background: rgba(139, 92, 246, 0.08);
        border-color: rgba(139, 92, 246, 0.25);
        color: white !important;
    }
    .stage-rail { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 1.5rem 0 2.8rem; }
    .stage {
        position: relative;
        padding: 1rem 1.1rem;
        background: linear-gradient(145deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
        border: 1px solid var(--border);
        border-radius: 10px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .stage:hover { transform: translateY(-2px); border-color: rgba(139, 92, 246, 0.45); }
    .stage-number { color: var(--purple-light); font-size: 0.68rem; font-weight: 700; letter-spacing: 0.12em; margin-bottom: 0.45rem; }
    .stage strong { display: block; color: white; font-family: "Space Grotesk", sans-serif; font-size: 0.95rem; margin-bottom: 0.25rem; }
    .stage span { color: var(--muted); font-size: 0.75rem; }
    div[data-testid="stTextInput"] label { color: var(--muted) !important; font-size: 0.78rem; font-weight: 600; letter-spacing: 0.05em; }
    div[data-testid="stTextInput"] input {
        background: #0C111D !important;
        color: white !important;
        border: 1px solid var(--border-light) !important;
        border-radius: 10px !important;
        padding: 1rem 1.1rem !important;
        min-height: 3.3rem;
        font-size: 0.95rem;
        transition: border 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: var(--purple) !important;
        box-shadow: 0 0 0 1px var(--purple), 0 0 30px rgba(139, 92, 246, 0.14) !important;
    }
    div[data-testid="stTextInput"] input::placeholder { color: #526078 !important; }
    .stButton button, .stDownloadButton button {
        border-radius: 9px !important;
        min-height: 3.1rem;
        font-weight: 700;
        border: 1px solid var(--border-light);
        background: var(--card);
        color: var(--text);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border 0.2s ease;
    }
    .stButton button:hover, .stDownloadButton button:hover {
        transform: translateY(-1px);
        border-color: rgba(139, 92, 246, 0.5);
        box-shadow: 0 10px 30px rgba(0,0,0,0.28);
    }
    .stButton button[kind="primary"] {
        background: var(--gradient) !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.28);
    }
    .stButton button[kind="primary"]:hover { box-shadow: 0 12px 35px rgba(139, 92, 246, 0.45); }
    .metric-strip { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 1.5rem 0 2rem; }
    .metric {
        position: relative;
        overflow: hidden;
        background: linear-gradient(145deg, #0D1321, #0A0F1A);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.25rem 1.35rem;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    .metric:hover { border-color: rgba(139, 92, 246, 0.35); transform: translateY(-2px); }
    .metric::after {
        content: "";
        position: absolute;
        width: 100px;
        height: 100px;
        right: -45px;
        bottom: -55px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(139,92,246,0.2), transparent 70%);
    }
    .metric-label { color: var(--muted); font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em; }
    .metric-value { color: white; font-family: "Space Grotesk", sans-serif; font-size: 1.45rem; font-weight: 600; margin-top: 0.4rem; }
    .result-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 1rem; }
    .result-topic { font-family: "Space Grotesk", sans-serif; color: white; font-size: 1.8rem; font-weight: 600; letter-spacing: -0.025em; word-break: break-word; }
    div[data-testid="stTabs"] { margin-top: 1.5rem; }
    div[data-testid="stTabs"] [role="tablist"] { gap: 5px; border-bottom: 1px solid var(--border); }
    div[data-testid="stTabs"] button {
        color: var(--muted) !important;
        font-size: 0.85rem;
        font-weight: 600;
        border-radius: 7px 7px 0 0;
        padding: 0.8rem 1rem;
        transition: color 0.2s ease, background 0.2s ease;
    }
    div[data-testid="stTabs"] button:hover { color: white !important; background: rgba(139,92,246,0.07); }
    div[data-testid="stTabs"] button[aria-selected="true"] { color: white !important; }
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background: var(--purple) !important; }
    [data-testid="stMarkdownContainer"] { color: var(--text-soft); }
    [data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 { color: white !important; }
    [data-testid="stMarkdownContainer"] code { background: #111827; color: #C4B5FD; border-radius: 5px; padding: 0.15rem 0.35rem; }
    [data-testid="stMarkdownContainer"] pre { background: #080C14 !important; border: 1px solid var(--border); border-radius: 10px; }
    div[data-testid="stCodeBlock"] { border-radius: 10px; border: 1px solid var(--border); }
    .empty-state {
        position: relative;
        overflow: hidden;
        border: 1px dashed #27344A;
        border-radius: 14px;
        padding: 4.5rem 2rem;
        text-align: center;
        background: radial-gradient(circle at 50% 0%, rgba(139,92,246,0.1), transparent 45%), #0A0F19;
        color: var(--muted);
    }
    .empty-icon {
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(139,92,246,0.18), rgba(34,211,238,0.12));
        border: 1px solid rgba(139,92,246,0.3);
        color: var(--purple-light);
        font-size: 1.4rem;
    }
    .empty-title { color: white; font-family: "Space Grotesk", sans-serif; font-size: 1.05rem; font-weight: 600; margin-bottom: 0.3rem; }
    [data-testid="stAlert"] { border-radius: 10px; border: 1px solid var(--border); }
    [data-testid="stProgressBar"] > div { background: #141C2B; }
    [data-testid="stProgressBar"] > div > div { background: linear-gradient(90deg, var(--purple), var(--cyan)); }
    hr { border-color: var(--border) !important; }
    @media (max-width: 800px) {
        .block-container { padding: 2rem 1.1rem 3rem; }
        h1 { font-size: 3.4rem !important; }
        .stage-rail { grid-template-columns: 1fr 1fr; }
        .metric-strip { grid-template-columns: 1fr; }
        .result-topic { font-size: 1.4rem; }
    }
    </style>
    """
)


# ============================================================================
# SESSION STATE
# ============================================================================

if "state" not in st.session_state:
    st.session_state.state = None

if "topic" not in st.session_state:
    st.session_state.topic = ""

if "history" not in st.session_state:
    st.session_state.history = []


# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:

    render_html('<p class="eyebrow">Signal / Desk</p>')
    st.markdown("### Research workspace")
    st.caption(
        "A multi-agent research system that turns open questions "
        "into structured, sourced briefs."
    )
    st.divider()
    st.markdown("**PIPELINE**")

    stages = [
        ("01", "Search", "Find sources"),
        ("02", "Read", "Extract signal"),
        ("03", "Write", "Build brief"),
        ("04", "Critique", "Challenge result"),
    ]

    for number, label, description in stages:
        render_html(
            f"""
            <div style="display:flex;gap:12px;padding:9px 0;align-items:flex-start;">
                <div style="color:#8B5CF6;font-size:11px;font-weight:700;padding-top:2px;">{number}</div>
                <div>
                    <div style="color:#F8FAFC;font-size:13px;font-weight:600;">{label}</div>
                    <div style="color:#64748B;font-size:11px;margin-top:2px;">{description}</div>
                </div>
            </div>
            """
        )

    if st.session_state.history:

        st.divider()
        st.markdown("**RECENT BRIEFS**")

        for i, item in enumerate(reversed(st.session_state.history)):
            if st.button(item["topic"][:35], key=f"hist_{i}", use_container_width=True):
                st.session_state.state = item["state"]
                st.session_state.topic = item["topic"]
                st.rerun()

        if st.button("Clear recent briefs", use_container_width=True):
            st.session_state.history = []
            st.rerun()


# ============================================================================
# HERO
# ============================================================================

render_html('<p class="eyebrow">Multi-agent intelligence</p>')
render_html('<h1 class="hero-title">From open question<br>to useful brief.</h1>')
render_html(
    """
    <p class="lede">
        Ask the desk to investigate a topic, discover strong sources,
        extract the important signal, draft a report, and pressure-test
        the result before you read it.
    </p>
    """
)
render_html('<div class="hero-rule"></div>')


# ============================================================================
# INPUT
# ============================================================================

col_input, col_button = st.columns([5, 1], vertical_alignment="bottom")

with col_input:
    topic = st.text_input(
        "Research topic",
        placeholder="What should the desk investigate?  e.g. quantum computing and cryptography",
        label_visibility="visible",
    )

with col_button:
    run_clicked = st.button("Run research  →", use_container_width=True, type="primary")


# ============================================================================
# PIPELINE VISUAL
# ============================================================================

render_html(
    """
    <div class="stage-rail">
        <div class="stage">
            <div class="stage-number">01 / SEARCH</div>
            <strong>Discover</strong>
            <span>Find relevant sources</span>
        </div>
        <div class="stage">
            <div class="stage-number">02 / READ</div>
            <strong>Extract</strong>
            <span>Read and summarize signal</span>
        </div>
        <div class="stage">
            <div class="stage-number">03 / WRITE</div>
            <strong>Synthesize</strong>
            <span>Build the research brief</span>
        </div>
        <div class="stage">
            <div class="stage-number">04 / CRITIQUE</div>
            <strong>Pressure-test</strong>
            <span>Challenge the result</span>
        </div>
    </div>
    """
)


# ============================================================================
# PIPELINE EXECUTION
# ============================================================================

def run_with_progress(topic: str):

    progress_placeholder = st.empty()

    with progress_placeholder.container():
        st.info("The research desk is working through Search → Read → Write → Critique.")
        bar = st.progress(8, text="Researching sources...")

    started = time.perf_counter()

    try:
        result = run_research_pipeline(topic)
    except Exception as e:
        progress_placeholder.empty()
        st.error(f"Pipeline failed: {e}")
        with st.expander("Show full traceback"):
            st.code(traceback.format_exc())
        return None

    elapsed = time.perf_counter() - started
    progress_placeholder.empty()
    st.success(f"Research complete · {elapsed:.1f}s")

    return result


# ============================================================================
# RUN
# ============================================================================

if run_clicked:

    if not topic.strip():
        st.warning("Enter a research topic to begin.")
    else:
        result = run_with_progress(topic.strip())

        if result is not None:
            st.session_state.state = result
            st.session_state.topic = topic.strip()
            st.session_state.history.append(
                {
                    "topic": topic.strip(),
                    "state": result,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M"),
                }
            )
            st.rerun()


# ============================================================================
# RESULTS
# ============================================================================

state = st.session_state.state

if state:

    st.divider()

    report_text = getattr(state.get("report", ""), "content", state.get("report", ""))
    feedback_text = getattr(state.get("feedback", ""), "content", state.get("feedback", ""))

    sources = re.findall(
        r"https?://[^\s)\]}>,]+",
        str(state.get("search_results", "")),
    )

    render_html('<p class="eyebrow">Desk output</p>')

    safe_topic = html.escape(st.session_state.topic)

    render_html(
        f"""
        <div class="result-head">
            <div>
                <div class="result-topic">{safe_topic}</div>
                <p class="lede">A researched brief with source notes and critical review.</p>
            </div>
        </div>
        """
    )

    # ------------------------------------------------------------------------
    # METRICS
    # ------------------------------------------------------------------------

    render_html(
        f"""
        <div class="metric-strip">
            <div class="metric">
                <div class="metric-label">Brief</div>
                <div class="metric-value">Ready</div>
            </div>
            <div class="metric">
                <div class="metric-label">Sources found</div>
                <div class="metric-value">{len(set(sources))}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Review</div>
                <div class="metric-value">Included</div>
            </div>
        </div>
        """
    )

    # ------------------------------------------------------------------------
    # TABS
    # ------------------------------------------------------------------------

    tab_report, tab_feedback, tab_search, tab_scraped = st.tabs(
        ["◈  Brief", "✦  Critique", "⌁  Search trail", "≡  Reading notes"]
    )

    with tab_report:
        st.markdown(report_text)
        st.download_button(
            "Download brief  ↓",
            data=str(report_text),
            file_name=f"{st.session_state.topic[:40].strip().replace(' ', '_')}_report.md",
            mime="text/markdown",
        )

    with tab_feedback:
        st.markdown(feedback_text)

    with tab_search:
        st.code(state.get("search_results", "No search results."), language="text")

    with tab_scraped:
        st.markdown(state.get("scraped_content", "No reading notes."))


# ============================================================================
# EMPTY STATE
# ============================================================================

else:

    render_html(
        """
        <div class="empty-state">
            <div class="empty-icon">◈</div>
            <div class="empty-title">Your next brief starts here.</div>
            <div>Enter a question above to activate the research desk.</div>
        </div>
        """
    )