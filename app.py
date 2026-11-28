import streamlit as st
import os
import json
import re
from pypdf import PdfReader
import docx
from groq import Groq

st.set_page_config(page_title="TalentLens | AI CV Analyzer", page_icon="✦", layout="wide")

# --- PROFESSIONAL CSS - FIXES WHITE TEXT ISSUE ---
st.markdown("""
<style>
/* Force Light Theme */
.stApp { background: #F4F5FA !important; }
[data-testid="stSidebar"] { background: #FFFFFF !important; border-right: 1px solid #E6E8F0; }

/* All text dark by default */
h1, h2, h3, h4, p, label, span { color: #1A2233 !important; }

/* HERO */
.hero {
    background: linear-gradient(120deg, #0F172A 0%, #2E2A7A 55%, #6D5DF6 100%);
    padding: 36px 32px;
    border-radius: 20px;
    margin-bottom: 24px;
}
.hero small { color: #C7C5FF !important; font-weight: 700; letter-spacing: 2px; font-size: 12px; }
.hero h1 { color: #FFFFFF !important; font-size: 38px; line-height: 1.15; margin: 12px 0; font-weight: 800; }
.hero p { color: #DDE0FF !important; font-size: 16px; max-width: 600px; }

/* CARDS */
.card {
    background: #FFFFFF;
    border: 1px solid #E6E8F0;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.04);
}
.card h3 { font-size: 18px; font-weight: 700; margin-bottom: 6px; }
.card p { color: #6B7280 !important; font-size: 14px; }

/* TAGS */
.tag { display: inline-block; background: #EEEDFF; color: #4F46E5 !important; border-radius: 20px; padding: 6px 12px; margin: 4px 4px 4px 0; font-size: 13px; font-weight: 600; }
.tag-green { background: #E6F7EE; color: #0E7A4B !important; }
.tag-orange { background: #FFF1E0; color: #B45309 !important; }

/* INPUTS - Make Visible */
input, textarea, select { color: #111827 !important; background: #FFFFFF !important; }
div[data-testid="stTextInput"] input { border: 1px solid #D1D5DB !important; border-radius: 10px !important; height: 48px !important; }
div[data-testid="stSelectbox"] > div > div { border: 1px solid #D1D5DB !important; border-radius: 10px !important; background: #FFFFFF !important; }

/* FILE UPLOADER - Professional */
div[data-testid="stFileUploader"] { background: #F8F8FF !important; border: 2px dashed #A5A0F0 !important; border-radius: 14px !important; padding: 14px !important; }
div[data-testid="stFileUploader"] button { background: #111827 !important; color: white !important; border-radius: 10px !important; padding: 8px 18px !important; font-weight: 600 !important; }

/* MAIN BUTTON - Professional Gradient */
div.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #6D5DF6, #4F46E5) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    height: 52px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    box-shadow: 0 8px 20px rgba(79,70,229,0.3) !important;
}
div.stButton > button[kind="primary"]:hover { transform: translateY(-1px); }

/* METRIC */
div[data-testid="stMetric"] { background: white; border: 1px solid #E6E8F0; border-radius: 14px; padding: 12px; }
</style>
""", unsafe_allow_html=True)

def extract_text(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        return "\n".join([(p.extract_text() or "") for p in reader.pages])
    elif name.endswith(".docx"):
        doc = docx.Document(uploaded_file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")
    return ""

def analyze_cv(cv_text, role, level, focus):
    api_key = None
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise Exception("GROQ_API_KEY not found in Secrets.")
    client = Groq(api_key=api_key)
    prompt = f"""
    You are a Senior Career Coach. Analyze CV for Role: {role}, Level: {level}, Focus: {focus}.
    CV: {cv_text[:7000]}
    Return ONLY valid JSON:
    {{
        "score": 78,
        "summary": "summary",
        "skills": {{"technical": ["Python"], "soft": ["Communication"]}},
        "missing_skills": ["Docker"],
        "skills_to_learn": ["Learn Docker"],
        "career_opportunities": ["Backend Developer"],
        "improvements": ["Add achievements"],
        "ats_tips": ["Add keywords"]
    }}
    """
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    txt = re.sub(r"```json|```", "", res.choices[0].message.content).strip()
    return json.loads(txt)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ✦ TalentLens")
    st.caption("AI-powered career intelligence")
    st.divider()
    st.markdown("**WORKSPACE**")
    st.markdown("✦ CV Analysis")
    st.markdown("▤ Skills Overview")
    st.markdown("◎ Career Directions")
    st.divider()
    st.caption("01 Upload CV → 02 Select Role → 03 Get AI Insights")

# --- HERO ---
st.markdown("""
<div class="hero">
<small>CAREER INTELLIGENCE • AI POWERED</small>
<h1>Turn your CV into a<br>clear career direction.</h1>
<p>Discover strengths, fix gaps, and explore career paths that match your experience.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1.25, 0.85], gap="large")

with col1:
    st.markdown('<div class="card"><h3>📄 Upload your CV</h3><p>Add your resume and tell us what role you are working toward.</p></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Choose PDF, DOCX or TXT file", type=["pdf", "docx", "txt"])
    role = st.text_input("Target job title", placeholder="e.g. Python Developer, Data Analyst")
    c1, c2 = st.columns(2)
    with c1:
        level = st.selectbox("Experience level", ["Student / Fresh graduate", "Entry level", "Mid level", "Senior level"])
    with c2:
        focus = st.selectbox("Analysis focus", ["Full CV review", "Technical skills", "Career opportunities", "CV improvement"])
    run = st.button("✦  Analyze My CV", type="primary", use_container_width=True, disabled=uploaded is None)

with col2:
    st.markdown("""
    <div class="card">
    <h3>What you will receive</h3>
    <p>◈ <b style="color:#111827">Skills Profile</b><br>Technical & transferable strengths</p>
    <hr>
    <p>⌁ <b style="color:#111827">Skill Gaps</b><br>Skills worth developing</p>
    <hr>
    <p>◎ <b style="color:#111827">Career Directions</b><br>Roles that fit your background</p>
    <hr>
    <p>↗ <b style="color:#111827">Improvement Plan</b><br>Practical ways to strengthen CV</p>
    </div>
    """, unsafe_allow_html=True)
    st.info("AI suggestions are guidance, not a hiring decision.")

if run and uploaded:
    try:
        with st.spinner("Reading your CV..."):
            text = extract_text(uploaded)
        if len(text.strip()) < 80:
            st.error("Not enough readable text. Try a text-based PDF.")
            st.stop()
        with st.spinner("AI is analyzing..."):
            r = analyze_cv(text, role or "General", level, focus)
        st.success("✅ Analysis Complete!")
        m1, m2, m3 = st.columns(3)
        m1.metric("Overall Score", f"{r.get('score',0)}/100")
        m2.metric("Technical Skills", len(r.get("skills",{}).get("technical",[])))
        m3.metric("Missing Skills", len(r.get("missing_skills",[])))
        st.markdown(f'<div class="card"><h3>Summary</h3><p style="color:#374151 !important">{r.get("summary","")}</p></div>', unsafe_allow_html=True)
        a, b = st.columns(2)
        with a:
            st.markdown('<div class="card"><h3>Technical Skills</h3>', unsafe_allow_html=True)
            for s in r.get("skills",{}).get("technical",[]): st.markdown(f'<span class="tag">{s}</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="card"><h3>🎯 Skills To Learn</h3>', unsafe_allow_html=True)
            for s in r.get("skills_to_learn",[]): st.markdown(f"- {s}")
            st.markdown('</div>', unsafe_allow_html=True)
        with b:
            st.markdown('<div class="card"><h3>Missing Skills</h3>', unsafe_allow_html=True)
            for s in r.get("missing_skills",[]): st.markdown(f'<span class="tag tag-orange">{s}</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="card"><h3>Career Opportunities</h3>', unsafe_allow_html=True)
            for s in r.get("career_opportunities",[]): st.markdown(f"- {s}")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="card"><h3>Improvement Plan</h3>', unsafe_allow_html=True)
        for s in r.get("improvements",[])+r.get("ats_tips",[]): st.markdown(f"- {s}")
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Analysis failed: {e}")
