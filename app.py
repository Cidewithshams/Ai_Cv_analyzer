import streamlit as st
import os
import json
import fitz
import docx
from groq import Groq

st.set_page_config(page_title="TalentLens | AI CV Analyzer", page_icon="✦", layout="wide")

st.title("✦ TalentLens - AI CV Analyzer")
st.write("Apni CV upload karo, AI tumhe skills, gaps aur career direction batayega.")

# --- CV Extract Function (Same File Me) ---
def extract_text(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        return text
    if name.endswith(".docx"):
        doc = docx.Document(uploaded_file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    return ""

# --- AI Analyze Function (Same File Me) ---
def analyze_cv(cv_text, role, level):
    api_key = None
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise Exception("GROQ_API_KEY not found in Secrets")

    client = Groq(api_key=api_key)
    prompt = f"""
    You are a career expert. Analyze this CV for target role: {role}, Level: {level}.
    CV Text: {cv_text[:6000]}
    Return ONLY valid JSON in this exact format:
    {{
        "summary": "short summary",
        "skills": {{"technical": ["skill1"], "soft": ["skill1"]}},
        "missing_skills": ["skill1"],
        "career_opportunities": ["job1"],
        "improvements": ["tip1"],
        "score": 75
    }}
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)

# --- UI ---
uploaded = st.file_uploader("Choose a PDF or DOCX file", type=["pdf", "docx"])
role = st.text_input("Target job title", placeholder="e.g. Python Developer, Data Analyst")
level = st.selectbox("Experience level", ["Student / Fresh graduate", "Entry level", "Mid level", "Senior level"])

run = st.button("✦ Analyze my CV", type="primary", disabled=uploaded is None)

if run and uploaded:
    try:
        with st.spinner("Reading your CV..."):
            text = extract_text(uploaded)
        if len(text.strip()) < 80:
            st.error("Not enough readable text found. Try a text-based PDF or DOCX.")
            st.stop()
        with st.spinner("AI is analyzing your profile..."):
            result = analyze_cv(text, role, level)

        st.success("Analysis Complete!")
        st.subheader("Summary")
        st.write(result.get("summary", ""))
        st.subheader("Technical Skills")
        for s in result.get("skills", {}).get("technical", []):
            st.markdown(f"- {s}")
        st.subheader("Soft Skills")
        for s in result.get("skills", {}).get("soft", []):
            st.markdown(f"- {s}")
        st.subheader("Missing Skills")
        for s in result.get("missing_skills", []):
            st.markdown(f"- {s}")
        st.subheader("Career Opportunities")
        for s in result.get("career_opportunities", []):
            st.markdown(f"- {s}")
        st.subheader("Improvement Plan")
        for s in result.get("improvements", []):
            st.markdown(f"- {s}")

    except Exception as e:
        st.error(f"Analysis failed: {e}")
        st.info("Groq API key Streamlit Secrets me add karna zaroori hai.")
