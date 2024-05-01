import streamlit as st
from main import extract_pdf_pages, model_calling

st.set_page_config(
    page_title="ExploraAi",
    page_icon="🔬",
)

st.title("🔬 ExploraAi | Your AI Researcher")

file = st.file_uploader("Choose a file")
history = []
question = st.empty()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


if file:
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        prompt_parts = extract_pdf_pages(file)
        prompt_parts.append(st.session_state.messages[-1]["content"])

        with st.spinner("Processing..."):
            response = model_calling(prompt=prompt_parts)

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)
