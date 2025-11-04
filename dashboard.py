# dashboard.py
import streamlit as st
from transformers import pipeline

# Load model
@st.cache_resource
def load_model():
    return pipeline("text-generation", model="distilgpt2")

pipe = load_model()

st.title("📖 Theology Chatbox Box")
st.write("You are a student discussing theology. Present your question or thought, and hear guidance from a wise teacher AI.")

# --- Suggested Questions ---
st.markdown("### Suggested Questions")
suggested_question = st.radio(
    "Click to use a question:",
    [
        "What do you think faith teaches us?",
        "Why do humans seek meaning in life?",
        "How can we reconcile doubt with belief?",
        "What is the purpose of suffering?"
    ]
)

# Store the chosen suggested question in session state
if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""

if st.button("Use this question"):
    st.session_state["user_input"] = suggested_question

# Conversation history
if "history" not in st.session_state:
    st.session_state["history"] = []

# Tone selector
tone = st.selectbox(
    "Teacher Tone",
    ["Gentle", "Direct", "Academic", "Biblical"]
)

# Fixed generation settings
max_tokens = 70
top_k = 20
temperature = 0.3
repetition_penalty = 2.0

# Input box (pre-filled with suggested question if chosen)
user_input = st.text_area(
    "Type your question or reflection here:",
    value=st.session_state.get("user_input", "")
)

# Clear conversation button
if st.button("Clear Conversation"):
    st.session_state["history"].clear()

# Generate response
if st.button("Get Guidance") and user_input:

    # Simplified stable prompt
    prompt = f"Teacher: {user_input}\nTeacher:"

    with st.spinner("Thinking..."):
        response = pipe(
            prompt,
            max_new_tokens=max_tokens,
            do_sample=True,
            top_k=top_k,
            temperature=temperature,
            repetition_penalty=repetition_penalty,
            no_repeat_ngram_size=3
        )[0]["generated_text"]

    # Clean output
    response_clean = response.replace(prompt, "").strip()
    sentences = response_clean.split('.')
    response_clean = '. '.join(sentences[:3]).strip()
    if not response_clean.endswith('.'):
        response_clean += '.'


    entry = f"**You:** {user_input}\n\n**Teacher:** {response_clean}"
    st.session_state["history"].append(entry)
    # reset user_input so text area is empty for next input
    st.session_state["user_input"] = ""

# Show conversation history
for h in st.session_state["history"]:
    st.markdown(h)

# Auto-scroll anchor
st.markdown("----")
