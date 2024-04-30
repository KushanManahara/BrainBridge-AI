import streamlit as st
from main import extract_pdf_pages, model_calling

st.title("AI Research Supporter")

file = st.file_uploader("Choose a file")
history = []
question = st.empty()

counter = 0
if file:
    prompt_parts = extract_pdf_pages(file)

    current_question = question.text_input(
        "What do you want to know about this paper?", key=counter
    )
    current_response = st.empty()

    counter += 1
    if current_question:
        q_and_a = {}
        prompt_parts.append(current_question)
        response_text = model_calling(prompt=prompt_parts)

        q_and_a[current_question] = response_text
        history.append(q_and_a)
        current_response.write(response_text)

        while current_question:
            question.empty()
            current_response.empty()

            for q_and_a in history:
                for idx, (ques, response) in enumerate(q_and_a.items()):
                    st.write(ques)
                    st.write(response)

            new_btn = st.button("New Question", key=counter)

            new_question = question.text_input("Ask Followup", key="followup_question")
            if new_question:
                q_and_a = {}
                prompt_parts.clear()
                prompt_parts = extract_pdf_pages(file)
                prompt_parts.append(new_question)
                response_text = model_calling(prompt=prompt_parts)
                st.write(response_text)
