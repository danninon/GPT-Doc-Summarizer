import streamlit as st
import os
import tempfile

from langchain.chat_models import ChatOpenAI


from utils import doc_loader, auto_summary_builder, check_key_validity, summary_prompt_creator, check_gpt_4, token_limit
from my_prompts import map_prompt, combine_prompt
from file_conversions import pdf_to_text

st.title("Document Summarizer")
uploaded_file = st.file_uploader("Upload a document to summarize, 10k to 100k tokens works best!", type=['txt',  'pdf'])
api_key = st.text_input("Leave this box empty to use the webapp for free. If running locally or this webapp hits its limit, you can enter your own API key here.")
use_gpt_4 = st.checkbox("Use GPT-4 for the final prompt (STRONGLY recommended, requires GPT-4 API access)", value=True)


st.sidebar.markdown('# Made by: [Ethan](https://github.com/e-johnstonn)')
st.sidebar.markdown('# Git link: [Docsummarizer](https://github.com/e-johnstonn/docsummarizer)')


if st.button('Summarize (click once and wait)'):
    st.session_state.summarize_button_clicked = True
    valid = check_key_validity(api_key)
    valid_gpt_4 = True
    if use_gpt_4:
        valid_gpt_4 = check_gpt_4(api_key)
    if uploaded_file is not None and valid is True and valid_gpt_4 is True:
        with st.spinner("Summarizing... please wait..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt',) as temp_file:
                if uploaded_file.type == 'application/pdf':
                    temp_file.write(pdf_to_text(uploaded_file))
                    temp_file_path = temp_file.name
                else:
                    temp_file.write(uploaded_file.getvalue())
                    temp_file_path = temp_file.name
            if use_gpt_4:
                llm = ChatOpenAI(openai_api_key=api_key, temperature=0, max_tokens=500, model_name='gpt-3.5-turbo')
            else:
                llm = ChatOpenAI(openai_api_key=api_key, temperature=0, max_tokens=250, model_name='gpt-3.5-turbo')

            initial_chain = summary_prompt_creator(map_prompt, 'text', llm)
            final_prompt_list = summary_prompt_creator(combine_prompt, 'text', llm)
            doc = doc_loader(temp_file_path)
            limit_check = token_limit(doc, 120000)
            if limit_check:
                summary = auto_summary_builder(doc, 10, initial_chain, final_prompt_list, api_key, use_gpt_4)
                st.markdown(summary, unsafe_allow_html=True)
                os.unlink(temp_file_path)
            else:
                st.warning('File too big!')
    elif uploaded_file is None:
        st.warning("Please upload a file.")
    elif valid is True:
        st.warning(check_gpt_4(api_key))
    else:
        st.warning(check_key_validity(api_key))

