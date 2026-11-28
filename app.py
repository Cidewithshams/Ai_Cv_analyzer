import streamlit as st
from cv_extractor import extract_text_from_uploaded_file
from ai_analyzer import analyze_cv

st.set_page_config(page_title="TalentLens | AI CV Analyzer", page_icon="✦", layout="wide")

st.title("✦ TalentLens - AI CV Analyzer")
st.write("Apni CV upload karo, AI tumhe skills, gaps aur career direction batayega.")

uploaded = st.file_uploader("Choose a PDF or DOCX file", type=["pdf", "docx"])
role = st.text_input("Target job title", placeholder="e.g. Python Developer, Data Analyst")
level = st.selectbox("Experience level", ["Student / Fresh graduate", "Entry level", "Mid level", "Senior level"])

run = st.button("✦ Analyze my CV", type="primary", disabled=uploaded is None)

if run and uploaded:
    try:
        with st.spinner("Reading your CV..."):
            text = extract_text_from_uploaded_file(uploaded)

        if len(text.strip()) < 80:
            st.error("Not enough readable text found. Try a text-based PDF or DOCX.")
            st.stop()

        with st.spinner("AI is analyzing your profile..."):
            result = analyze_cv(text, role, level)

        st.success("Analysis Complete!")

        st.subheader("Summary")
        st.write(result.get("summary", "No summary found"))

        st.subheader("Technical Skills")
        for skill in result.get("skills", {}).get("technical", []):
            st.markdown(f"- {skill}")

        st.subheader("Soft Skills")
        for skill in result.get("skills", {}).get("soft", []):
            st.markdown(f"- {skill}")

        st.subheader("Missing Skills")
        for gap in result.get("missing_skills", []):
            st.markdown(f"- {gap}")

        st.subheader("Career Opportunities")
        for job in result.get("career_opportunities", []):
            st.markdown(f"- {job}")

        st.subheader("Improvement Plan")
        for item in result.get("improvements", []):
            st.markdown(f"- {item}")

    except Exception as e:
        st.error(f"Analysis failed: {e}")
        st.info("Groq API key Streamlit Secrets me add karna zaroori hai.")
