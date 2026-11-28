import streamlit as st
import os
import json
import re
import fitz  # PyMuPDF
import docx
from groq import Groq

# --- PAGE CONFIG ---
st.set_page_config(page_title="TalentLens | AI CV Analyzer", page_icon="✦", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
.stApp{background:#f6f7fb}
.hero{padding:32px 36px;border-radius:22px;color:white;background:linear-gradient(115deg,#17213d,#303b70 62%,#6254d9);margin-bottom:25px}
.hero small{color:#c9c7ff;font-weight:700;letter-spacing:2px}
.hero h1{font-size:2.3rem;line-height:1.16;margin:12px 0;color:white}
.hero p{color:#e0e4f5}
.panel{background:white;border:1px solid #e6eaf1;border-radius:17px;padding:22px;margin-bottom:16px}
.tag{display:inline-block;background:#f0efff;color:#5144c9;border-radius:7px;padding:6px 10px;margin:3px;font-size:.82rem;font-weight:600}
.tag2{background:#eaf6f1;color:#267457}
.tag3{background:#fff3e0;color:#b45309}
div.stButton>button[kind="primary"]{background:linear-gradient(120deg,#7062ed,#5142c9);border:0;border-radius:11px;color:white;font-weight:700;min-height:46px}
</style>
""", unsafe_allow_html=True)

# --- 1. CV EXTRACTOR (PDF / DOCX / TXT) ---
def extract_text(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        return text
    elif name.endswith(".docx"):
        doc = docx.Document(uploaded_file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")
    else:
        return ""

# --- 2. GROQ AI ANALYZER ---
def analyze_cv(cv_text, role, level, focus):
    # Get API Key from Secrets (Cloud) or Env (Local)
    api_key = None
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise Exception("GROQ_API_KEY not found. Add it in Streamlit Secrets.")

    client = Groq(api_key=api_key)

    prompt = f"""
    You are a Senior Career Coach and ATS Expert.
    Analyze the CV below for Target Role: {role}, Experience Level: {level}, Focus: {focus}.

    CV TEXT:
    {cv_text[:7000]}

    Return ONLY valid JSON. No markdown, no explanation. Use this exact structure:
    {{
        "score": 78,
        "summary": "2-3 lines professional summary",
        "skills": {{"technical": ["Python", "SQL"], "soft": ["Communication"]}},
        "missing_skills": ["Docker", "System Design"],
        "skills_to_learn": ["Learn FastAPI in 2 weeks", "Build 2 projects"],
        "career_opportunities": ["Backend Developer", "Data Analyst"],
        "improvements": ["Add quantifiable achievements", "Add GitHub link"],
        "ats_tips": ["Use keywords from job description"]
    }}
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content.strip()
    # Clean if model adds markdown
    content = re.sub(r"```json|```", "", content).strip()
    return json.loads(content)

# --- 3. UI ---
st.markdown("""
<div class="hero">
<small>CAREER INTELLIGENCE · AI POWERED</small>
<h1>Turn your CV into a<br>clear career direction.</h1>
<p>Upload your CV, get skills, gaps, opportunities & a learning roadmap in seconds.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1.2, 0.8], gap="large")

with col1:
    st.markdown('<div class="panel"><h3>Upload your CV</h3>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Choose PDF, DOCX or TXT", type=["pdf", "docx", "txt"])
    role = st.text_input("Target job title", placeholder="e.g. Python Developer, Data Analyst")
    c1, c2 = st.columns(2)
    with c1:
        level = st.selectbox("Experience level", ["Student / Fresh graduate", "Entry level", "Mid level", "Senior level"])
    with c2:
        focus = st.selectbox("Analysis focus", ["Full CV review", "Technical skills", "Career opportunities", "CV improvement"])
    st.markdown('</div>', unsafe_allow_html=True)
    run = st.button("✦ Analyze my CV", type="primary", use_container_width=True, disabled=uploaded is None)

with col2:
    st.markdown('<div class="panel"><h3>What you will get</h3><p>◈ <b>Skills Profile</b> - Technical + Soft</p><p>⌁ <b>Missing Skills</b> - Gaps for your target role</p><p>◎ <b>Career Opportunities</b> - Roles that fit you</p><p>↗ <b>Learn Skills Roadmap</b> - What to learn next</p></div>', unsafe_allow_html=True)
    st.info("AI suggestions are guidance, not a hiring decision.")

# --- 4. RUN ANALYSIS ---
if run and uploaded:
    try:
        with st.spinner("Reading your CV..."):
            text = extract_text(uploaded)
        if len(text.strip()) < 80:
            st.error("Not enough readable text. Please upload a text-based PDF/DOCX.")
            st.stop()
        with st.spinner("AI is analyzing your profile..."):
            r = analyze_cv(text, role.strip() or "General", level, focus)

        st.success("Analysis Complete!")

        m1, m2, m3 = st.columns(3)
        m1.metric("Overall Score", f"{r.get('score', 0)}/100")
        m2.metric("Technical Skills", len(r.get("skills", {}).get("technical", [])))
        m3.metric("Missing Skills", len(r.get("missing_skills", [])))

        st.markdown(f'<div class="panel"><h3>Summary</h3><p>{r.get("summary","")}</p></div>', unsafe_allow_html=True)

        cA, cB = st.columns(2)
        with cA:
            st.markdown('<div class="panel"><h3>Technical Skills</h3>', unsafe_allow_html=True)
            for s in r.get("skills", {}).get("technical", []):
                st.markdown(f'<span class="tag">{s}</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="panel"><h3>Skills To Learn</h3>', unsafe_allow_html=True)
            for s in r.get("skills_to_learn", []):
                st.markdown(f"- {s}")
            st.markdown('</div>', unsafe_allow_html=True)

        with cB:
            st.markdown('<div class="panel"><h3>Missing Skills</h3>', unsafe_allow_html=True)
            for s in r.get("missing_skills", []):
                st.markdown(f'<span class="tag tag3">{s}</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="panel"><h3>Career Opportunities</h3>', unsafe_allow_html=True)
            for s in r.get("career_opportunities", []):
                st.markdown(f"- {s}")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel"><h3>Improvement Plan & ATS Tips</h3>', unsafe_allow_html=True)
        for s in r.get("improvements", []) + r.get("ats_tips", []):
            st.markdown(f"- {s}")
        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Analysis failed: {e}")
        st.info("Make sure GROQ_API_KEY is added in Streamlit Secrets.")
