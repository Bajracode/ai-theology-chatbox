# dashboard.py
import streamlit as st
from transformers import pipeline
import re
from snowflake.snowpark import Session

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
    # Ensure table exists
    session.sql("""
        CREATE TABLE IF NOT EXISTS theology_chat_history (
            id INTEGER AUTOINCREMENT,
            user_input STRING,
            teacher_response STRING,
            tone STRING,
            timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP
        )
    """).collect()
    return session

sf_session = init_snowflake_session()

# ---------------------
# Model loader
# ---------------------
@st.cache_resource
def load_model(model_name: str):
    return pipeline("text-generation", model=model_name)

# ---- HARD CODED GENERATION SETTINGS ----
model_name = "distilgpt2"
max_new_tokens = 90
temperature = 0.78
top_k = 40
repetition_penalty = 1.9
no_repeat_ngram_size = 3
# ----------------------------------------

pipe = load_model(model_name)

# ---------------------
# Tone Definitions
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
    ),
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
# Dhammapada Knowledge
# ---------------------
VERSE_KNOWLEDGE = {
    # Original 30 keywords (refined)
    "meaning_of_life": "Dhammapada 277 — All things arise and pass away. When one truly sees this truth, suffering ends and wisdom begins.",
    "why_are_we_here": "Dhammapada 276 — The Buddha shows the path; each person must walk it with effort, awareness, and understanding.",
    "suffering": "Dhammapada 216 — Craving gives rise to sorrow and fear; when craving fades, so too do sorrow and fear.",
    "anger": "Dhammapada 223 — Conquer anger with love, evil with goodness, greed with generosity, and lies with truth.",
    "attachment": "Dhammapada 211 — From attachment comes sorrow; free from attachment, the heart rests in lasting peace.",
    "death": "Dhammapada 128 — Not even the swiftest can escape death; it comes to all, wise and foolish alike.",
    "desire": "Dhammapada 216 — Desire gives birth to grief and fear; one who is free from desire knows neither grief nor fear.",
    "mind": "Dhammapada 33 — The mind is restless and hard to control; like a skilled fletcher, the wise straighten it.",
    "peace": "Dhammapada 201 — Victory breeds hatred; the peaceful live with ease, renouncing both victory and defeat.",
    "life": "Dhammapada 85 — Few reach the far shore of liberation; most remain wandering along the banks of illusion.",

    "speech": "Dhammapada 231 — Guard your words carefully; speak only that which brings peace and harmony.",
    "truth": "Dhammapada 224 — Speak truth, live without anger, and give freely; this is the path of the virtuous.",
    "patience": "Dhammapada 184 — Patience and forgiveness are the highest practices; the wise are gentle and disciplined.",
    "effort": "Dhammapada 276 — Strive earnestly; the Buddhas only show the way — you must walk it yourself.",
    "wisdom": "Dhammapada 256 — The wise do not judge by appearances; they discern truth beyond bias and desire.",
    "compassion": "Dhammapada 270 — A noble heart harms no living being and brings compassion to all creatures.",
    "generosity": "Dhammapada 224 — Give freely without expecting reward; generosity purifies the heart and mind.",
    "hatred": "Dhammapada 5 — Hatred never ends through hatred, but only through love; this is the eternal law.",
    "greed": "Dhammapada 355 — Wealth destroys the foolish who crave it, like a flood sweeping away a sleeping village.",
    "envy": "Dhammapada 365 — Conquer envy with contentment and rejoice in the happiness of others.",

    "mindfulness": "Dhammapada 35 — The disciplined mind brings happiness; a wandering mind brings sorrow and confusion.",
    "meditation": "Dhammapada 282 — Through meditation and wisdom, one purifies oneself and finds lasting peace.",
    "self_control": "Dhammapada 103 — Greater than conquering a thousand men is conquering one’s own mind.",
    "focus": "Dhammapada 25 — The wise, focused and resolute, climb the mountain of wisdom and find freedom.",
    "ignorance": "Dhammapada 13 — The fool lives in darkness, counting others’ wealth while ignoring his own path.",
    "awakening": "Dhammapada 21 — The mindful never die; awareness is the path to the deathless state.",
    "awareness": "Dhammapada 23 — The alert and mindful advance like swift horses, leaving the careless far behind.",
    "discipline": "Dhammapada 157 — Discipline purifies the heart; no one can cleanse another’s mind for them.",
    "temptation": "Dhammapada 347 — The craving mind spins its own web, trapping itself until wisdom cuts it free.",
    "ego": "Dhammapada 94 — The awakened one is free from pride and attachment; calm as a still lake.",

    "friendship": "Dhammapada 61 — Better a solitary life than company with the foolish, who lead one astray.",
    "evil": "Dhammapada 117 — Avoid evil, cultivate good, and purify the mind to follow the path of the wise.",
    "good_deeds": "Dhammapada 122 — Do not overlook small good deeds; they accumulate like drops filling a jar.",
    "forgiveness": "Dhammapada 223 — Conquer anger with love and forgiveness; this is the mark of a noble heart.",
    "path": "Dhammapada 183 — Avoid evil, do good, and purify the mind; this is the teaching of all Buddhas.",
    "truth_seeking": "Dhammapada 354 — The gift of truth surpasses all other gifts; cherish it above wealth.",
    "freedom": "Dhammapada 348 — Having abandoned craving and attachment, one is truly free and serene.",
    "contentment": "Dhammapada 204 — Health, contentment, and trust are the greatest treasures one can possess.",
    "discipleship": "Dhammapada 276 — The teacher shows the way; the disciple must walk it diligently and wisely.",
    "purity": "Dhammapada 183 — Purity of thought, word, and deed is the essence of the enlightened path.",

    # 20 new keywords
    "happy": "Dhammapada 204 — Joy arises from contentment and mindfulness; those who cling to desire know little joy.",
    "kindness": "Dhammapada 223 — Kindness to all beings, even enemies, purifies the mind and softens the heart.",
    "humility": "Dhammapada 89 — The humble avoid arrogance; like a tree bending in wind, they endure and flourish.",
    "gratitude": "Dhammapada 212 — Appreciating the blessings of life, no matter how small, leads to lasting peace.",
    "resilience": "Dhammapada 80 — The steadfast endure hardship without complaint, like mountains standing through storms.",
    "clarity": "Dhammapada 33 — A clear mind sees the true nature of all things and avoids illusion.",
    "forbearance": "Dhammapada 184 — Bearing insult and harm without anger is the hallmark of the wise.",
    "truth": "Dhammapada 224 — Living honestly and sincerely is the foundation of virtue and trust.",
    "sincerity": "Dhammapada 224 — Actions in line with sincere intention bring harmony and inner peace.",
    "moderation": "Dhammapada 372 — Excess and indulgence lead to suffering; moderation brings freedom.",
    "die": "Dhammapada 128 — Mindful of death, one lives fully, aware of the fleeting nature of all things.",
    "selflessness": "Dhammapada 94 — Letting go of ego and selfishness allows the heart to be free and compassionate.",
    "patience_in_practice": "Dhammapada 184 — True practice requires patience; sudden haste leads to stumbling.",
    "equanimity": "Dhammapada 201 — Even in success or failure, the mind remains balanced, steady, and calm.",
    "reflection": "Dhammapada 277 — Reflecting on impermanence deepens understanding and lessens attachment.",
    #For the trolls, I added this as a mindful reminder to "grow up"
    "fuck": "Dhammapada 231 — Thoughtful and disciplined speech brings peace to oneself and others. Mind your words; harsh speech harms both speaker and listener.",
    "shit": "Dhammapada 231 — Words can wound; choose carefully. Reflect before speaking, and cultivate restraint in all speech.",
    "bitch": "Dhammapada 223 — Conquer anger with love and patience. Insulting words only feed suffering; speak with compassion instead.",
    "damn": "Dhammapada 5 — Hatred never ends through anger or cursing; only calm, kind speech brings peace.",
    "asshole": "Dhammapada 270 — A noble heart harms no being; consider your words and the impact they have on others.",    
    "learning": "Dhammapada 276 — Learning and applying wisdom steadily leads one along the path to liberation.",
    "preparation": "Dhammapada 103 — Cultivate the mind daily; preparation prevents the pitfalls of desire and distraction.",
    "serenity": "Dhammapada 201 — Serenity arises when the mind is free from craving and rests in the present moment.",
    "understanding": "Dhammapada 256 — Understanding the nature of mind and world is the root of wisdom and compassion."
}


def find_relevant_verse(user_text):
    text_lower = user_text.lower()
    for key, verse in VERSE_KNOWLEDGE.items():
        if key in text_lower:
            return verse
    return None


# ---------------------
# Utilities
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
        result = result + "."
    return result


def build_messages(history_objs, user_text, tone, max_history_items=6):
    verse = find_relevant_verse(user_text)
    system_msg = (
        f"You are a human theology teacher guiding a student. "
        f"You are not AI. Your style must follow this tone specification: {TONE_STYLES[tone]} "
    )
    if verse:
        system_msg += f"Start by reflecting on this verse: {verse}\n"

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
# UI
# ---------------------
st.title("📖 Theology Chatbox")
st.write("You are a student. Ask your teacher and receive spiritual guidance.")

tone = st.selectbox(
    "Teacher Tone",
    ["Gentle", "Direct", "Academic", "Biblical"],
    index=0
)

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

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    clear_btn = st.button("Clear Conversation")
with col2:
    submit_btn = st.button("Get Guidance")
with col3:
    clear_suggested = st.button("Clear Suggested")

if clear_suggested:
    st.session_state["suggested_question"] = ""

if clear_btn:
    st.session_state["history_objs"].clear()
    st.session_state["history_display"].clear()

if submit_btn and user_input.strip():
    verse = find_relevant_verse(user_input)
    if verse:
        st.markdown(f"**Relevant Verse:** {verse}")

    messages = build_messages(st.session_state["history_objs"], user_input, tone)

    text = ""
    for m in messages:
        prefix = "Teacher" if m["role"]!="user" else "Student"
        text += f"{prefix}: {m['content']}\n"
    text += "Teacher:"  # GPT2 continues here

    with st.spinner("Generating guidance..."):
        raw = pipe(
            text,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            top_k=top_k,
            temperature=temperature,
            repetition_penalty=repetition_penalty,
            no_repeat_ngram_size=no_repeat_ngram_size,
        )

    generated_text = raw[0]["generated_text"]

    if generated_text.startswith(text):
        response = generated_text[len(text):].strip()
    else:
        response = re.split(r"Teacher:\s*", generated_text, maxsplit=1)[-1].strip()

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
