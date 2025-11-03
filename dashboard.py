# dashboard.py
import streamlit as st
from transformers import pipeline

# Load the text-generation model
@st.cache_resource
def load_model():
    return pipeline("text-generation", model="distilgpt2")

pipe = load_model()

# Streamlit interface
st.title("📖 Theology chatbox Box")
st.write("You are a student discussing theology. Present your question or thought, and hear guidance from a wise teacher AI.")

# Input your question or thought
user_input = st.text_area("Type your question or reflection here:")

# Generate the teacher's response
if st.button("Get Guidance") and user_input:
    prompt = f"A wise theological teacher responds to the student's reflection: {user_input}"

    response = pipe(
        prompt,
        max_new_tokens=80,  # roughly 3-4 sentences
        do_sample=True,
        top_k=30
    )[0]["generated_text"]

    # Clean the output: remove prompt, take first 3 sentences
    response_clean = response.replace(prompt, "").strip()
    sentences = response_clean.split('.')
    response_clean = '. '.join(sentences[:3]).strip()
    if not response_clean.endswith('.'):
        response_clean += '.'

    st.markdown(f"**Teacher:** {response_clean}")