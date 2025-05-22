import streamlit as st
import openai
import os
from dotenv import load_dotenv
import re

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Fraud Job Analyzer", layout="wide")
st.title("Fraud Job Detection")

st.markdown("""
Paste a job description or offer email
""")

user_input = st.text_area("Paste the job offer or email here:", height=300)

def extract_flagged_phrases(text):
    system_prompt = (
        "You are a fraud detection assistant. Read the job description and output only the suspicious or potentially fraudulent parts as they are in the paragraph as bullet points. No explanations. No extra formatting."
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        temperature=0.3,
        max_tokens=500
    )
    return response['choices'][0]['message']['content']

import re

def highlight_text(original, flagged_list):
    highlighted = original
    for phrase in flagged_list:
        cleaned_phrase = phrase.strip("•- \n")
    
        if cleaned_phrase in highlighted:
            highlighted = highlighted.replace(
               cleaned_phrase,
                f"<mark style='background-color:#ffcccc'>{cleaned_phrase}</mark>"
            )
        else:
            pattern = re.compile(re.escape(cleaned_phrase), re.IGNORECASE)
            match = pattern.search(highlighted)
            if match:
                matched_text = match.group()
                highlighted = highlighted.replace(
                    matched_text,
                    f"<mark style='background-color:#ffcccc'>{matched_text}</mark>"
                )
    return highlighted


if st.button("Analyze") and user_input.strip():
    st.subheader("Possible Suspicious Parts")
    
    try:
        raw_phrases = extract_flagged_phrases(user_input)
        flagged_phrases = [line.strip("-• ").strip() for line in raw_phrases.split("\n") if line.strip()]
        if flagged_phrases:
        
            highlighted_result = highlight_text(user_input, flagged_phrases)
            st.markdown(highlighted_result, unsafe_allow_html=True)

        else:
            st.info(" No fraudulent parts detected by the model.")

    except Exception as e:
        st.error(f"Error during analysis:\n{e}")

    st.subheader("LLM Analysis")
    final_prompt = f"""
You are a fraud detector.  Read the following job description and return one line:
- 'Likely Fraudulent' or 'Likely Legitimate'
- Short reasoning about why the job seems fraud (For example '80% fraudulent due to salary and vague qualifications').

Text:
{user_input}
"""
    try:
        final_eval = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert job fraud analyst."},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.2,
            max_tokens=150
        )
        st.success(final_eval['choices'][0]['message']['content'])
    except Exception as e:
        st.error(f"Error generating overall summary:\n{e}")
else:
    st.info("Paste text and click 'Analyze'.")
