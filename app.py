import streamlit as st
from cv_extractor import extract_text_from_uploaded_file
import streamlit as st
from ai_analyzer import analyze_cv

st.set_page_config(page_title="TalentLens | AI CV Analyzer", page_icon="✦", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.stApp{background:#f6f7fb;color:#192238}
.block-container{max-width:1280px;padding-top:1.7rem}
[data-testid="stSidebar"]{background:#fff;border-right:1px solid #e7eaf1}
.brand{font:800 1.25rem Manrope;color:#202943}
.hero{padding:32px 36px;border-radius:22px;color:white;background:linear-gradient(115deg,#17213d,#303b70 62%,#6254d9);margin-bottom:25px;box-shadow:0 15px 35px #26345a20}
.hero small{color:#c9c7ff;font-weight:700;letter-spacing:2px}
.hero h1{font:800 2.3rem Manrope;color:white;line-height:1.16;margin:12px 0}
.hero p{color:#e0e4f5;max-width:680px;font-size:1rem}
.panel{background:white;border:1px solid #e6eaf1;border-radius:17px;padding:22px;margin-bottom:16px;box-shadow:0 5px 18px #1c2a4608}
.panel h3{font:700 1.08rem Manrope;color:#202943}
.sub{color:#8993a5;font-size:.85rem;margin-bottom:16px}
.kicker{font-size:.72rem;letter-spacing:1.5px;color:#818ba0;font-weight:700;margin:8px 0}
.metric{background:white;border:1px solid #e6eaf1;border-radius:14px;padding:16px}
.metric label{font-size:.72rem;color:#8993a5;font-weight:700}
.metric strong{display:block;font:800 1.7rem Manrope;color:#202943;margin-top:5px}
.tag{display:inline-block;background:#f0efff;color:#5144c9;border-radius:7px;padding:6px 10px;margin:3px;font-size:.78rem;font-weight:600}
.tag2{background:#eaf6f1;color:#267457}
div.stButton>button[kind="primary"]{background:linear-gradient(120deg,#7062ed,#5142c9);border:0;border-radius:11px;color:white;font-weight:700;min-height:46px}
.stDownloadButton>button{border-radius:10px;font-weight:600}
div[data-testid="stFileUploader"]{background:#fafaff;border:1px dashed #c9c4f3;border-radius:12px;padding:10px}
.footer{text-align:center;color:#9aa3b2;font-size:.75rem;padding:22px}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="brand">✦ &nbsp; TalentLens</div><div style="color:#929bad;font-size:.8rem">AI-powered career intelligence</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("**WORKSPACE**")
    st.markdown("✦  CV Analysis")
    st.markdown("▤  Skills Overview")
    st.markdown("◎  Career Directions")
    st.divider()
    st.markdown("**HOW IT WORKS**")
    st.caption("01  Upload your CV")
    st.caption("02  Select your target role")
    st.caption("03  Generate AI insights")
    st.caption("04  Review your action plan")
    st.divider()
    st.caption("🔒 CV files are processed in memory by this app.")

st.markdown("""
<div class="hero">
<small>CAREER INTELLIGENCE · AI POWERED</small>
<h1>Turn your CV into a<br>clear career direction.</h1>
<p>Discover the strengths in your profile, identify skills to build, and explore career paths that match your experience.</p>
</div>
""", unsafe_allow_html=True)

a,b=st.columns([1.3,.85],gap="large")
with a:
    st.markdown('<div class="kicker">01 — START YOUR ANALYSIS</div><div class="panel"><h3>Upload your CV</h3><div class="sub">Add your resume and tell us what role you are working toward.</div>',unsafe_allow_html=True)
    uploaded=st.file_uploader("Choose a PDF or DOCX file",type=["pdf","docx"])
    role=st.text_input("Target job title",placeholder="e.g. Python Developer, Data Analyst, UI/UX Designer")
    c1,c2=st.columns(2)
    with c1:
        level=st.selectbox("Experience level",["Not specified","Student / Fresh graduate","Entry level","Mid level","Senior level"])
    with c2:
        focus=st.selectbox("Analysis focus",["Full CV review","Technical skills","Career opportunities","CV improvement"])
    st.markdown('</div>',unsafe_allow_html=True)
    run=st.button("✦  Analyze my CV",type="primary",use_container_width=True,disabled=uploaded is None)
with b:
    st.markdown('<div class="kicker">02 — YOUR CAREER SNAPSHOT</div><div class="panel"><h3>What you will receive</h3><div class="sub">A structured review based on your CV.</div><p>◈ &nbsp; <b>Skills profile</b><br><span class="sub">Technical and transferable strengths</span></p><hr><p>⌁ &nbsp; <b>Potential skill gaps</b><br><span class="sub">Skills worth developing for your target role</span></p><hr><p>◎ &nbsp; <b>Career directions</b><br><span class="sub">Roles that may fit your background</span></p><hr><p>↗ &nbsp; <b>Improvement plan</b><br><span class="sub">Practical ways to strengthen your CV</span></p></div>',unsafe_allow_html=True)
    st.info("AI suggestions are guidance, not a hiring decision or a guarantee of employment.")

if run and uploaded:
    try:
        with st.spinner("Reading your CV..."):
            text=extract_text_from_uploaded_file(uploaded)
        if len(text.strip())<80:
            st.error("Not enough readable text found. Try a text-based PDF or DOCX.")
            st.stop()
        with st.spinner("TalentLens is analyzing your profile..."):
            result=analyze_cv(text,role.strip(),level)
        st.session_state["cv_result"]=result
        st.session_state["cv_name"]=uploaded.name
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        st.info("The Groq API key must be added in Streamlit Secrets before AI analysis can run.")

if "cv_result" in st.session_state:
    r=st.session_state["cv_result"]
    skills=r.get("skills",{}) or {}
    tech=skills.get("technical",[]) or []
    soft=skills.get("soft",[]) or []
    gaps=r.get("missing_skills",[]) or []
    jobs=r.get("career_opportunities",[]) or []
