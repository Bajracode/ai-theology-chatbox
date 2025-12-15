# dashboard.py
import streamlit as st
from transformers import pipeline
import re
from snowflake.snowpark import Session
import pandas as pd

st.set_page_config(page_title="Theology Chatbox", layout="centered")

# ---------------------
# Snowflake Connection
# ---------------------
@st.cache_resource
def init_snowflake_session():
    connection_parameters = {
        "account": st.secrets["snowflake"]["account"],
        "user": st.secrets["snowflake"]["user"],
        "password": st.secrets["snowflake"]["password"],
        "role": "ACCOUNTADMIN",
        "warehouse": "COMPUTE_WH",
        "database": "SNOWFLAKE_LEARNING_DB",
        "schema": "PUBLIC",
    }
    session = Session.builder.configs(connection_parameters).create()

    # Ensure chat history table exists
    session.sql("""
        CREATE TABLE IF NOT EXISTS theology_chat_history (
            id INTEGER AUTOINCREMENT,
            user_input STRING,
            teacher_response STRING,
            tone STRING,
            timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP
        )
    """).collect()

    ### --- NEW CODE ---
    # Table to track keyword searches
    session.sql("""
        CREATE TABLE IF NOT EXISTS keyword_searches (
            id INTEGER AUTOINCREMENT,
            keyword STRING,
            timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP
        )
    """).collect()
    ### -----------------

    return session

sf_session = init_snowflake_session()

# ---------------------
# Log keyword usage
# ---------------------
### --- NEW CODE ---
def log_keyword(keyword):
    try:
        sf_session.sql(f"""
            INSERT INTO keyword_searches (keyword)
            VALUES ('{keyword}')
        """).collect()
    except:
        pass
### ------------------


# ---------------------
# Model loader (SAFE – FLAN-T5)
# ---------------------

@st.cache_resource
def load_model():
    return pipeline(
        "text2text-generation",
        model="google/flan-t5-large"
    )

# Generation settings (ONE place only)
max_new_tokens = 120
temperature = 0.2

pipe = load_model()

# ---------------------
# Tone definitions
# ---------------------
TONE_STYLES = {
    "Gentle": (
        "Speak with kindness, patience, and warmth. "
        "Offer emotional reassurance and gentle reflection. "
        "Use soft, calm phrasing. Avoid being sharp or blunt."
    ),
    "Direct": (
        "Speak crisply and briefly. Deliver clear conclusions. "
        "Do not decorate your language. Provide concise truths."
    ),
    "Academic": (
        "Speak like a theology professor in a university. "
        "Use structured reasoning, definitions, and doctrinal comparisons. "
        "Avoid emotional language. Focus on conceptual clarity."
    ),
    "Biblical": (
        "Speak in a poetic cadence similar to Scripture. "
        "Use imagery, metaphors, and parable-like turns of phrase. "
        "Write in a solemn, reverent tone."
    )
}

SUGGESTED_BY_TONE = {
    "Gentle": [
        "How do I find peace when my mind is troubled?",
        "Why does God still love us even when we fail?",
        "How can I learn to be kinder to myself?",
        "How do I heal spiritually after pain?"
    ],
    "Direct": [
        "What is the point of faith?",
        "Why do people avoid spiritual responsibility?",
        "How do I stop wasting time on meaningless things?",
        "Is belief a decision or a feeling?"
    ],
    "Academic": [
        "What is the difference between faith and epistemic justification?",
        "How has theological interpretation of suffering changed historically?",
        "Is there a coherent definition of the soul in doctrine?",
        "How do different denominations define grace?"
    ],
    "Biblical": [
        "Why is the wilderness a recurring theme in Scripture?",
        "What does it mean to walk the narrow path?",
        "How do parables illuminate divine truth?",
        "Why does the heart appear more than the mind in Biblical language?"
    ],
}

# ---------------------
# Verse Lookup
# ---------------------
def find_verse_db(user_text):
    text_lower = user_text.lower()
    rows = sf_session.sql("SELECT keyword, verse, tag, keywords, theme FROM theology_verses").collect()

    for r in rows:
        kw = r.KEYWORD.lower()
        if kw in text_lower:
            log_keyword(kw)  # log keyword being used
            return {
                "verse": r.VERSE,
                "tag": r.TAG,
                "keywords": r.KEYWORDS,
                "theme": r.THEME
            }
    return None


# ---------------------
# Utils
# ---------------------
def split_sentences(text: str, limit: int = 4) -> str:
    if not text:
        return ""
    pieces = re.split(r'(?<=[\.\?\!])\s+', text.strip())
    if len(pieces) == 1:
        pieces = [p for p in re.split(r'\n+', text) if p.strip()]
    chosen = pieces[:limit]
    result = " ".join(p.strip() for p in chosen).strip()
    if result and result[-1] not in ".!?":
        result += "."
    return result

def build_messages(history_objs, user_text, tone, max_history_items=6):
    verse = find_verse_db(user_text)
    system_msg = (
        f"You are a theology teacher responding directly to a student's question. "
        f"Your style must follow this tone specification: {TONE_STYLES[tone]} "
        )
    # Do NOT inject verse into the generation prompt
    # # Verse is displayed to the user separately for context
    pass

    msgs = [{"role": "system", "content": system_msg}]
    for turn in history_objs[-max_history_items:]:
        r = "user" if turn["role"]=="student" else "teacher"
        msgs.append({"role": r, "content": turn["text"]})
    msgs.append({"role": "user", "content": user_text})
    return msgs

# ---------------------
# Session state
# ---------------------
if "history_objs" not in st.session_state:
    st.session_state["history_objs"] = []
if "history_display" not in st.session_state:
    st.session_state["history_display"] = []
if "suggested_question" not in st.session_state:
    st.session_state["suggested_question"] = ""

# ---------------------
# Sidebar Navigation
# ---------------------
### --- NEW CODE ---
st.sidebar.title("📘 Navigation")
page = st.sidebar.radio("Go to:", ["Chatbox", "Analytics Dashboard"])
### -----------------

# =========================================================
# PAGE 1 — CHATBOX (your original app)
# =========================================================
if page == "Chatbox":

    st.title("📖 Theology Chatbox")
    st.write("You are a student. Ask your teacher and receive spiritual guidance.")

    tone = st.selectbox("Teacher Tone", ["Gentle", "Direct", "Academic", "Biblical"], index=0)

    st.markdown("### Suggested Questions (based on tone)")
    suggested_question = st.radio(
        "Click to use a question:",
        SUGGESTED_BY_TONE[tone],
        index=0
    )

    if st.button("Use this question"):
        st.session_state["suggested_question"] = suggested_question

    user_input = st.text_area(
        "Type your question or reflection here:",
        value=st.session_state.get("suggested_question", ""),
        placeholder="Type your question or reflection here..."
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        clear_btn = st.button("Clear Conversation")
    with col2:
        submit_btn = st.button("Get Guidance")

    if clear_btn:
        st.session_state["history_objs"].clear()
        st.session_state["history_display"].clear()

    if submit_btn and user_input.strip():
        verse_info = find_verse_db(user_input)
        if verse_info:
            st.markdown(f"**Relevant Verse:** {verse_info['verse']}")
            if verse_info.get("tag"):
                st.markdown(f"**Tag:** {verse_info['tag']}")
            if verse_info.get("theme"):
                st.markdown(f"**Theme:** {verse_info['theme']}")
            if verse_info.get("keywords"):
                st.markdown(f"**Keywords:** {verse_info['keywords']}")

        messages = build_messages(st.session_state["history_objs"], user_input, tone)

        text = ""
        for m in messages:
            prefix = "Teacher" if m["role"]!="user" else "Student"
            text += f"{prefix}: {m['content']}\n"
        text += (
            "\nProvide a direct answer to the student's question below. "
            "Do NOT explain how to answer the question. "
            "Do NOT ask questions or use rhetorical questions. "
            "Do NOT give teaching advice or instructions. "
            "Speak directly as the teacher, giving the answer itself. "
            "Write ONE cohesive paragraph using varied sentence structure. "
            "Avoid repeating sentence openings (e.g., do not start multiple sentences with the same words). "
            "Explain the idea with at least two distinct reasons:\n"
            )

        with st.spinner("Generating guidance..."):
            raw = pipe(
                text,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                repetition_penalty=1.2,
                no_repeat_ngram_size=4,
                min_length=60
                )

        response = raw[0]["generated_text"].strip()
        # Ensure response ends cleanly
        if response.endswith(":") or response.endswith("following"):
            response += (
                " slowing your breathing to calm your body, and gently redirecting your attention "
                "to the present moment rather than fighting your thoughts."
            )
        response_clean = split_sentences(response, limit=4)

        st.session_state["history_objs"].append({"role":"student","text":user_input})
        st.session_state["history_objs"].append({"role":"teacher","text":response_clean})

        display_entry = f"**You:** {user_input}\n\n**Teacher ({tone}):** {response_clean}"
        st.session_state["history_display"].append(display_entry)

        st.session_state["suggested_question"] = ""

    if st.session_state["history_display"]:
        st.markdown("----")
        st.markdown("### Conversation")
        for md in st.session_state["history_display"]:
            st.markdown(md)
        st.markdown("----")

# =========================================================
# PAGE 2 — ANALYTICS DASHBOARD
# =========================================================
### --- NEW CODE ---
elif page == "Analytics Dashboard":
    st.title("📊 Keyword Analytics")

    # Top keywords
    st.subheader("🏆 Most Searched Keywords")

    df_keywords = sf_session.sql("""
        SELECT keyword, COUNT(*) AS total
        FROM keyword_searches
        GROUP BY keyword
        ORDER BY total DESC
    """).to_pandas()

    st.dataframe(df_keywords)

    # Daily trend
    st.subheader("📈 Daily Search Trend")

    df_daily = sf_session.sql("""
        SELECT DATE(timestamp) AS day, COUNT(*) AS searches
        FROM keyword_searches
        GROUP BY day
        ORDER BY day
    """).to_pandas()

    if df_daily.empty:
        st.info("No search data yet.")
    else:
        df_daily = df_daily.set_index("DAY")
        st.line_chart(df_daily["SEARCHES"])
### -----------------
