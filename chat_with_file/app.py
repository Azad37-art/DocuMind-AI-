import streamlit as st
import html

from project.document_processor import process_uploaded_file
from project.vector_store import create_vector_store
from project.qa_chain import create_qa_chain, ask_question
from project.utils import format_file_size, get_timestamp
from project.config import SUPPORTED_FILE_TYPES, MAX_FILE_SIZE_MB, GEMINI_API_KEY


st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
body {
    background: #0D0D5F !important;
    overflow-x: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
}
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }

/* =====================================================
   FULL APP — deep navy, zero white
===================================================== */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
.main,
.main .block-container {
    background: #0D0D5F !important;
}


.main .block-container {
    background: transparent !important;
    padding: 0 2rem 2rem !important;
    max-width: 920px !important;
}
/* =========================
   SIDEBAR ONLY
========================= */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #14002d 0%,
        #120038 18%,
        #0d0d5f 52%,
        #031a52 78%,
        #00163f 100%
    ) !important;
    border-right: 1px solid rgba(129, 140, 248, 0.18) !important;
    box-shadow: 4px 0 28px rgba(0, 0, 0, 0.35) !important;
}
section[data-testid="stSidebar"] {
    width: 240px !important;
    min-width: 240px !important;
    max-width: 270px !important;
}

section[data-testid="stSidebar"] > div {
    width: 240px !important;
    min-width: 240px !important;
    max-width: 270px !important;
}

[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

/* divider */
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.10) !important;
}

/* section labels */
.sidebar-section {
    font-size: 0.65rem;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.72) !important;
    margin: 1.15rem 0 0.55rem;
    padding-bottom: 0.35rem;
    border-bottom: 1px solid rgba(255,255,255,0.12);
}

/* sidebar title card feel */
[data-testid="stSidebar"] .sidebar-top {
    text-align: center;
    padding: 1rem 0 0.6rem;
}

/* file card */
.file-card {
    background: rgba(99, 102, 241, 0.10);
    border: 1px solid rgba(129, 140, 248, 0.25);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    backdrop-filter: blur(6px);
}

/* uploader outer */
[data-testid="stSidebar"] [data-testid="stFileUploader"],
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"],
[data-testid="stSidebar"] .stFileUploader,
[data-testid="stSidebar"] .stFileUploader > div {
    background: rgba(79, 70, 229, 0.08) !important;
    border: 1.5px dashed rgba(129, 140, 248, 0.38) !important;
    border-radius: 12px !important;
}

/* remove inner white areas */
[data-testid="stSidebar"] [data-testid="stFileUploader"] > div,
[data-testid="stSidebar"] [data-testid="stFileUploader"] div,
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] > div,
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] div {
    background: transparent !important;
}

/* uploader text */
[data-testid="stSidebar"] [data-testid="stFileUploader"] *,
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] *,
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] p,
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] span,
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small {
    color: #dbeafe !important;
}

/* browse files button */
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button,
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button:hover,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"],
[data-testid="stSidebar"] button[kind="secondary"] {
    background: rgba(99, 102, 241, 0.16) !important;
    color: #ffffff !important;
    border: 1px solid rgba(129, 140, 248, 0.42) !important;
    border-radius: 8px !important;
}

/* uploaded file item */
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"],
[data-testid="stSidebar"] [data-testid="stFileUploaderFileName"] {
    background: rgba(99, 102, 241, 0.10) !important;
    border-radius: 8px !important;
    color: #ffffff !important;
}

/* remove file X button */
[data-testid="stSidebar"] [data-testid="stFileUploaderDeleteBtn"] button {
    background: rgba(129, 140, 248, 0.14) !important;
    color: #ffffff !important;
    border: none !important;
}

/* metrics */
[data-testid="stSidebar"] [data-testid="stMetric"] {
    background: rgba(79, 70, 229, 0.10) !important;
    border-radius: 12px !important;
    padding: 0.75rem 1rem !important;
    border: 1px solid rgba(129, 140, 248, 0.22) !important;
}

[data-testid="stSidebar"] [data-testid="stMetric"] label {
    color: rgba(255,255,255,0.72) !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}

[data-testid="stSidebar"] [data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 1.5rem !important;
    font-weight: 800 !important;
}

/* buttons only inside sidebar */
[data-testid="stSidebar"] .stButton > button {
    background: rgba(79, 70, 229, 0.14) !important;
    color: #ffffff !important;
    border: 1px solid rgba(129, 140, 248, 0.32) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.2s ease !important;
    box-shadow: none !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(99, 102, 241, 0.22) !important;
    border-color: rgba(167, 139, 250, 0.34) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.18) !important;
}
/* =====================================================
   MAIN HEADER
===================================================== */
.main-header {
    text-align: center;
    padding: 2.2rem 1rem 1.8rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 1.5rem;
}
.header-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.65rem;
    margin-bottom: 0.5rem;
}
.header-icon {
    width: 44px; height: 44px;
    background: linear-gradient(135deg, #00b4d8, #7c5cfc);
    border-radius: 13px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    box-shadow: 0 4px 18px rgba(0,180,216,0.4);
}
.main-header h1 {
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(95deg, #22d3ee 0%, #7c5cfc 50%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
}
.main-header p {
    color: #FFFFFF;
    font-size: 0.9rem;
    font-weight: 400;
}

/* =====================================================
   DOC BADGES
===================================================== */
.doc-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(0,212,255,0.09);
    border: 1px solid rgba(0,212,255,0.3);
    border-radius: 20px;
    padding: 0.32rem 0.95rem;
    font-size: 0.77rem;
    color: #22d3ee;
    margin: 0.15rem 0.25rem;
    font-weight: 600;
}

/* =====================================================
   USER BUBBLE
===================================================== */
.chat-user {
    display: flex;
    justify-content: flex-end;
    margin: 1.2rem 0 0.4rem;
}
.chat-user-inner {
    max-width: 64%;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.22rem;
}
.chat-user-bubble {
    background: linear-gradient(135deg, #00b4d8 0%, #6c63ff 65%, #a855f7 100%);
    color: #ffffff !important;
    border-radius: 20px 20px 4px 20px;
    padding: 0.95rem 1.3rem;
    font-size: 1.05rem;
    line-height: 1.6;
    font-weight: 500;
    box-shadow: 0 4px 22px rgba(0,180,216,0.35);
    word-wrap: break-word;
}
.chat-timestamp {
    font-size: 0.67rem !important;
    color: #FFFFFF !important;
    letter-spacing: 0.02em !important;
    opacity: 0.55 !important;
}
/* =====================================================
   AI BUBBLE
===================================================== */
.chat-assistant {
    display: flex;
    justify-content: flex-start;
    margin: 0.4rem 0 1.2rem;
    gap: 0.72rem;
    align-items: flex-start;
}
.chat-avatar {
    width: 38px; height: 38px; min-width: 38px;
    background: linear-gradient(135deg, #7c5cfc, #a855f7);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    box-shadow: 0 3px 14px rgba(124,92,252,0.55);
    flex-shrink: 0;
    margin-top: 2px;
}
.chat-assistant-inner {
    max-width: 78%;
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
}
.chat-assistant-bubble {
    background: linear-gradient(135deg, #0a3d47 0%, #0c3545 100%);
    border: 1px solid rgba(0,212,255,0.18);
    color: #e2e8f0 !important;
    border-radius: 4px 20px 20px 20px;
    padding: 1.05rem 1.35rem;
    font-size: 1.05rem;
    line-height: 1.6;
    word-wrap: break-word;
    box-shadow: 0 4px 22px rgba(0,0,0,0.38);
}

/* =====================================================
   SOURCES EXPANDER — orange/rust, NO white bg
===================================================== */
/* SOURCES EXPANDER */
[data-testid="stExpander"] {
    background: rgba(28,12,4,0.95) !important;
    border: 1px solid rgba(249,115,22,0.32) !important;
    border-radius: 12px !important;
    margin-top: 0.05rem !important;
    margin-bottom: 0.15rem !important;
    overflow: hidden !important;
}

/* Only target the structural wrapper divs — NOT source cards */
[data-testid="stExpander"] > div,
[data-testid="stExpander"] > div > div,
[data-testid="stExpander"] [data-testid="stExpanderDetails"],
[data-testid="stExpander"] [data-testid="stExpanderDetails"] > div {
    background: transparent !important;
    background-color: transparent !important;
}

[data-testid="stExpander"] summary {
    background: transparent !important;
    background-color: transparent !important;
    color: #fb923c !important;
    font-weight: 700 !important;
    font-size: 0.79rem !important;
    letter-spacing: 0.09em !important;
    text-transform: uppercase !important;
    padding: 0.8rem 1rem !important;
    border-radius: 12px !important;
}

[data-testid="stExpander"] summary:hover {
    background: rgba(249,115,22,0.05) !important;
}

/* ── Source cards — high specificity, no wildcard override ── */
[data-testid="stExpander"] .source-card,
[data-testid="stExpanderDetails"] .source-card,
div.source-card {
    background: rgba(120,53,15,0.20) !important;
    background-color: rgba(120,53,15,0.20) !important;
    border: 1px solid rgba(251,146,60,0.20) !important;
    border-left: 3px solid #f97316 !important;
    border-radius: 0 10px 10px 0 !important;
    padding: 0.8rem 1rem !important;
    margin-bottom: 0.6rem !important;
}

[data-testid="stExpander"] .source-card .source-title,
[data-testid="stExpanderDetails"] .source-card .source-title,
div.source-card .source-title {
    color: #fdba74 !important;
    font-weight: 700 !important;
    font-size: 0.84rem !important;
    margin-bottom: 0.3rem !important;
    background: transparent !important;
    background-color: transparent !important;
}

[data-testid="stExpander"] .source-card .source-snippet,
[data-testid="stExpanderDetails"] .source-card .source-snippet,
div.source-card .source-snippet {
    color: #cbd5e1 !important;
    font-style: italic !important;
    font-size: 0.8rem !important;
    line-height: 1.6 !important;
    background: transparent !important;
    background-color: transparent !important;
}
/* =====================================================
   WELCOME SCREEN
===================================================== */
.welcome-wrap {
    text-align: center;
    padding: 3rem 1rem 1rem;
}
.welcome-icon {
    width: 80px; height: 80px;
    background: linear-gradient(135deg, rgba(0,180,216,0.2), rgba(124,92,252,0.18));
    border: 1px solid rgba(0,212,255,0.25);
    border-radius: 22px;
    display: flex; align-items: center; justify-content: center;
    font-size: 2.2rem;
    margin: 0 auto 1.4rem;
    box-shadow: 0 0 50px rgba(0,180,216,0.18);
}
.welcome-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 0.6rem;
}
.welcome-sub {
    color: #FFFFFF;
    font-size: 0.9rem;
    max-width: 400px;
    margin: 0 auto;
    line-height: 1.75;
    font-weight: 300;
}
.sect-lbl {
    text-align: center;
    color: #FFFFFF;
    font-size: 0.64rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin: 2rem 0 1rem;
}
.feat-card {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 1.7rem 1.1rem 1.4rem;
    text-align: center;
    transition: all 0.22s ease;
}
.feat-card:hover {
    transform: translateY(-3px);
    border-color: rgba(0,212,255,0.22);
    box-shadow: 0 8px 28px rgba(0,0,0,0.3);
}
.feat-icon {
    width: 50px; height: 50px;
    border-radius: 13px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    margin: 0 auto 0.9rem;
}
.feat-t { font-size: 0.93rem; font-weight: 700; color: #e2e8f0; margin-bottom: 0.4rem; }
.feat-d { font-size: 0.79rem; color: #FFFFFF; line-height: 1.6; font-weight: 300; }


/* =========================
   SUGGESTION QUESTIONS
========================= */
/* =========================
   SUGGESTION BUTTON FINAL FIX
========================= */

/* base */
.suggest-btn .stButton > button {
    background: #111827 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    padding: 0.88rem 1.1rem !important;
    width: 100% !important;
    text-align: left !important;
}

/* force text (normal) */
.suggest-btn .stButton > button,
.suggest-btn .stButton > button div,
.suggest-btn .stButton > button span,
.suggest-btn .stButton > button p {
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
}

/* hover background */
.suggest-btn .stButton > button:hover {
    background: rgba(0,180,216,0.09) !important;
    border-color: rgba(0,212,255,0.38) !important;
}

/* 🔥 THIS IS THE REAL FIX */
.suggest-btn .stButton > button:hover,
.suggest-btn .stButton > button:hover * {
    color: #171F45 !important;
    -webkit-text-fill-color: #171F45 !important;
}
/* =========================
   CHAT INPUT CONTAINER CLEAN
========================= */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div,
[data-testid="stBottom"] > div > div > div,
[data-testid="stBottom"] > div > div > div > div {
    background: #171F45 !important;
    background-color: #171F45 !important;
}
 
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] > div > div,
[data-testid="stChatInput"] > div > div > div {
    background: #171F45 !important;
    background-color: #171F45 !important;
    border: none !important;
    box-shadow: none !important;
}
 
[data-testid="stChatInputContainer"],
[data-testid="stChatInputContainer"] > div,
[data-testid="stChatInputContainer"] > div > div {
    background: #171F45 !important;
    background-color: #171F45 !important;
}


/* =========================
   TEXTAREA (ONLY THIS HAS BORDER)
========================= */
[data-testid="stChatInput"] textarea {
    background: #171F45 !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 14px !important;
    color: #e2e8f0 !important;
    padding: 0.9rem 1.1rem !important;
    caret-color: #ffffff !important;
    font-size: 18px !important;
}

/* remove red border */
[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInput"] textarea:focus-visible,
[data-testid="stChatInput"] textarea:active {
    border: 1px solid rgba(255,255,255,0.12) !important;
    outline: none !important;
    box-shadow: none !important;
    caret-color: #ffffff !important;
}

/* placeholder */
[data-testid="stChatInput"] textarea::placeholder {
    color: #7c88b8 !important;
}
/* Send button */
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #00b4d8, #6c63ff) !important;
    border: none !important;
    border-radius: 10px !important;
    box-shadow: 0 3px 14px rgba(0,180,216,0.4) !important;
    transition: all 0.2s ease !important;
}
[data-testid="stChatInput"] button:hover {
    transform: scale(1.07) !important;
    box-shadow: 0 5px 22px rgba(0,180,216,0.6) !important;
}
[data-testid="stChatInput"] svg {
    fill: #ffffff !important;
    color: #ffffff !important;
}

/* =====================================================
   MISC
===================================================== */
.stProgress > div > div {
    background: linear-gradient(90deg, #00b4d8, #6c63ff) !important;
    border-radius: 999px !important;
}
.stAlert {
    border-radius: 10px !important;
    background: #111827 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    color: #e2e8f0 !important;
}
hr { border-color: rgba(255,255,255,0.06) !important; }
.chat-divider {
    height: 1px;
    background: rgba(255,255,255,0.04);
    margin: 0.15rem 0;
}
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.09); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,212,255,0.3); }
section[data-testid="stSidebar"] > div { background: transparent !important; }
.element-container { background: transparent !important; }
[data-testid="stSpinner"] p { color: #64748b !important; }
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────────────
def initialize_session_state():
    defaults = {
        "messages": [],
        "vector_store": None,
        "qa_chain": None,
        "uploaded_filename": None,
        "doc_chunks": 0,
        "processing": False,
        "total_questions": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def process_document(uploaded_file):
    st.session_state.processing = True
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    with progress_placeholder:
        progress_bar = st.progress(0)
    try:
        with status_placeholder:
            st.info("📖 Reading and parsing document...")
        progress_bar.progress(20)
        chunks = process_uploaded_file(uploaded_file)
        progress_bar.progress(50)
        with status_placeholder:
            st.info("🔮 Generating embeddings...")
        vector_store = create_vector_store(chunks)
        progress_bar.progress(80)
        with status_placeholder:
            st.info("⚙️ Building QA chain...")
        qa_chain = create_qa_chain(vector_store)
        progress_bar.progress(100)
        st.session_state.vector_store = vector_store
        st.session_state.qa_chain = qa_chain
        st.session_state.uploaded_filename = uploaded_file.name
        st.session_state.doc_chunks = len(chunks)
        st.session_state.messages = []
        st.session_state.total_questions = 0
        st.session_state.processing = False
        progress_placeholder.empty()
        status_placeholder.empty()
        st.success(f"✅ Document ready — {len(chunks)} searchable chunks created.")
    except Exception as e:
        progress_placeholder.empty()
        status_placeholder.empty()
        st.session_state.processing = False
        st.error(f"Error processing document: {str(e)}")


# ── Sidebar ───────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("<span class='sb-label'>Upload Document</span>", unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "PDF, TXT, DOCX, CSV, .md",
            type=[ext.lstrip(".") for ext in SUPPORTED_FILE_TYPES],
            help=f"Max file size: {MAX_FILE_SIZE_MB} MB",
            label_visibility="collapsed",
        )

        if uploaded_file:
            file_size = format_file_size(uploaded_file.size)
            st.markdown(f"""
            <div class="file-info-card">
                <div class="file-info-name">📄 {uploaded_file.name}</div>
                <div class="file-info-size">{file_size}</div>
            </div>
            """, unsafe_allow_html=True)

            is_new = uploaded_file.name != st.session_state.uploaded_filename
            label = "⚡ Process Document" if is_new else "🔄 Re-process Document"
            if st.button(label, use_container_width=True):
                process_document(uploaded_file)

        if st.session_state.vector_store is not None:
            st.markdown("<span class='sb-label'>Document Stats</span>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.metric("CHUNKS", st.session_state.doc_chunks)
            with col2:
                st.metric("QUESTIONS", st.session_state.total_questions)

            st.markdown("<span class='sb-label'>Actions</span>", unsafe_allow_html=True)
            if st.button("🗑️  Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.total_questions = 0
                st.rerun()
            if st.button("♻️  Reset Session", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

#____SOURCES______
def render_sources(sources: list):
    if not sources:
        return

    # make sources narrower and aligned with assistant bubble
    left_space, source_col, right_space = st.columns([1.8, 2.2, 4])

    with source_col:
        with st.expander(f"🔗 Sources ({len(sources)} References)", expanded=False):
            st.markdown(
                "<div class='sources-header'><span>📎</span> Document References</div>",
                unsafe_allow_html=True,
            )

            for i, source in enumerate(sources, 1):
                filename = source.get("filename", "Unknown")
                page = source.get("page")
                snippet = source.get("snippet", "")
                page_info = f" — Page {page + 1}" if page is not None else ""

                safe_snippet = html.escape(snippet) if snippet else ""
                snippet_html = (
                    f'<div class="source-snippet">&ldquo;{safe_snippet}&rdquo;</div>'
                    if safe_snippet else ""
                )

                st.markdown(f"""
                <div class="source-card">
                    <div class="source-title">
                        🔗 Source {i}: {filename}{page_info}
                    </div>
                    {snippet_html}
                </div>
                """, unsafe_allow_html=True)

# ── Chat messages ─────────────────────────────────────────────────────
def render_chat_message(message: dict):
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", "")
    sources = message.get("sources", [])

    if role == "user":
        st.markdown(
            f"""
            <div class="chat-user">
                <div class="chat-user-inner">
                    <div class="chat-user-bubble">{content}</div>
                    <div class="chat-timestamp">{timestamp}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:
        # assistant message
        st.markdown(
            f"""
            <div class="chat-assistant">
                <div class="chat-avatar">🧠</div>
                <div class="chat-assistant-inner">
                    <div class="chat-assistant-bubble">{content}</div>
                    <div class="chat-timestamp">{timestamp}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 🔥 render sources immediately AFTER bubble (tight)
        if sources:
            st.markdown(
                "<div style='margin-top:-0.35rem; margin-bottom:0.1rem;'></div>",
                unsafe_allow_html=True,
            )

            # narrow + aligned under bubble
            left, mid, right = st.columns([0.3, 3.0, 6.7])

            with mid:
                with st.expander(f"🔗 Sources ({len(sources)} References)", expanded=False):
                    for i, source in enumerate(sources, 1):
                        filename = source.get("filename", "Unknown")
                        page = source.get("page")
                        snippet = source.get("snippet", "")

                        page_info = f" — Page {page + 1}" if page is not None else ""

                        st.markdown(
                            f"""
                            <div class='source-card'>
                                <b>Source {i}:</b> {filename}{page_info}<br>
                                <small>{snippet}</small>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

    st.markdown("<div class='chat-divider'></div>", unsafe_allow_html=True)
# ── Welcome ───────────────────────────────────────────────────────────
def render_welcome_screen():
    st.markdown("""
    <div class="welcome-wrap">
        <div class="welcome-icon">🧠</div>
        <div class="welcome-title">No Document Loaded</div>
        <p class="welcome-sub">
            Upload a PDF, TXT, DOCX, CSV, or Markdown file from the sidebar,
            then process it to start your intelligent conversation.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='sect-lbl'>What you can do</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class="feat-card">
            <div class="feat-icon" style="background:rgba(0,180,216,0.13);border:1px solid rgba(0,212,255,0.28);">📝</div>
            <div class="feat-t">Summarize</div>
            <div class="feat-d">Get an instant overview of any document's core content.</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="feat-card">
            <div class="feat-icon" style="background:rgba(108,99,255,0.13);border:1px solid rgba(168,85,247,0.28);">🔎</div>
            <div class="feat-t">Deep Search</div>
            <div class="feat-d">Precise questions with fully sourced, verified answers.</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="feat-card">
            <div class="feat-icon" style="background:rgba(52,211,153,0.1);border:1px solid rgba(52,211,153,0.28);">💬</div>
            <div class="feat-t">Follow-up Chat</div>
            <div class="feat-d">Continue conversation with full memory of context.</div>
        </div>""", unsafe_allow_html=True)


# ── Handle input ──────────────────────────────────────────────────────
def handle_user_input(question: str):
    if not st.session_state.qa_chain:
        st.error("Please upload and process a document first.")
        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
            "timestamp": get_timestamp(),
        }
    )
    st.session_state.total_questions += 1

    try:
        with st.spinner("Thinking..."):
            result = ask_question(st.session_state.qa_chain, question)
            answer = result["answer"]
            sources = result["sources"]

    except Exception as e:
        error_text = str(e)

        if "429" in error_text or "quota" in error_text.lower() or "ResourceExhausted" in error_text:
            answer = "Gemini quota exceeded. Your file is processed, but the model cannot answer right now."
        else:
            answer = f"Sorry, I encountered an error: {error_text}"

        sources = []

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "timestamp": get_timestamp(),
            "sources": sources,
        }
    )
# ── Chat area ─────────────────────────────────────────────────────────
def render_chat_area():
    if st.session_state.uploaded_filename:
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:1.5rem;">
            <span class="doc-badge">📄 {st.session_state.uploaded_filename}</span>
            <span class="doc-badge">🧩 {st.session_state.doc_chunks} chunks</span>
        </div>
        """, unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align:center; padding:1.5rem 0 1rem;">
            <p style="color:#FFFFFF; font-size:0.9rem; font-style:italic; font-weight:300;">
                Document ready — ask anything about its content
            </p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        suggestions = [
            "What is the main topic in the file? Tell me in one line.",
            "Summarize this document for me.",
            "What are the key points?",
            "What data or numbers are mentioned?",
        ]
        for idx, suggestion in enumerate(suggestions):
            col = col1 if idx % 2 == 0 else col2
            with col:
                st.markdown("<div class='suggest-btn'>", unsafe_allow_html=True)
                if st.button(suggestion, key=f"sug_{idx}", use_container_width=True):
                    handle_user_input(suggestion)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        for message in st.session_state.messages:
            render_chat_message(message)

    user_input = st.chat_input(
        "Ask a question about your document...",
        disabled=st.session_state.vector_store is None,
    )
    if user_input:
        handle_user_input(user_input)
        st.rerun()


# ── Main ──────────────────────────────────────────────────────────────
def main():
    initialize_session_state()

    if not GEMINI_API_KEY:
        st.error("GEMINI_API_KEY is not set. Please add it to your .env file and restart.")
        st.stop()

    st.markdown("""
    <div class="main-header">
        <div class="header-row">
            <div class="header-icon">🧠</div>
            <h1>DocuMind AI</h1>
        </div>
        <p>Upload any document and have an intelligent conversation about its content</p>
    </div>
    """, unsafe_allow_html=True)

    render_sidebar()

    if st.session_state.vector_store is None:
        render_welcome_screen()
    else:
        render_chat_area()


if __name__ == "__main__":
    main()