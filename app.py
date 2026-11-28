import streamlit as st
import os, json, re
from pypdf import PdfReader
import docx
from groq import Groq

st.set_page_config(page_title="TalentLens | AI CV Analyzer", page_icon="✦", layout="wide")

# --- PREMIUM BUT SAFE CSS ---
st.markdown("""
<style>
.stApp { background-color: #F8F9FC; }
.hero {
  background: linear-gradient(135deg, #111827 0%, #4338CA 70%, #7C3AED 100%);
  padding: 34px 30px; border-radius: 18px; margin-bottom: 22px;
}
.hero h1 { color: white !important; font-size: 34px; line-height: 1.2; margin: 8px 0; }
.hero p { color: #E0E7FF !important; font-size: 15px; }
.hero span { color: #A5B4FC !important; font-size: 12px; font-weight: 700; letter-spacing: 2px; }
.card { background: white; padding: 22px; border-radius: 16px; border: 1px solid #E5E7EB; margin-bottom: 16px; }
.card h3 { margin-top: 0; font-size: 17px; }
.tag { display: inline-block; background: #EEF2FF; color: #4338CA; padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; margin: 3px; }
.tag-orange { background: #FEF3C7; color: #92400E; }
.tag-green { background: #D1FAE5; color: #065F46; }
div.stButton > button[kind="primary"] {
  background: #4F46E5 !important; color: white !important; height: 50px !important;
  border-radius: 12px !important; font-size: 16px !important; font-weight: 700 !important; border: none !important;
}
</style>
""", unsafe_allow_html=True)

def extract_text(file):
    name = file.name.lower()
    if name.endswith(".pdf"):
        reader = PdfReader(file)
        return "\n".join([(p.extract_text() or "") for p in reader.pages])
    elif name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif name.endswith(".txt"):
        return file.read().decode("utf-8", errors="ignore")
    return ""

def analyze_cv(cv_text, role, level, focus):
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise Exception("GROQ_API_KEY not found in Secrets")
    client = Groq(api_key=api_key)
    prompt = f"""
    You are a Senior Career Coach & ATS Expert. Analyze CV for Role: {role}, Level: {level}, Focus: {focus}.
    CV: {cv_text[:7000]}
    Return ONLY valid JSON:
    {{
        "score": 78,
        "summary": "2-3 lines summary",
        "skills": {{"technical": ["Python"], "soft": ["Communication"]}},
        "missing_skills": ["Docker"],
        "skills_to_learn": ["Learn Docker in 2 weeks"],
        "career_opportunities": ["Backend Developer"],
        "improvements": ["Add numbers to achievements"],
        "ats_tips": ["Add keywords"]
    }}
    """
    res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":prompt}], temperature=0.3, response_format={"type":"json_object"})
    txt = re.sub(r"```json|```","",res.choices[0].message.content).strip()
    return json.loads(txt)

# --- TOP BAR ---
c_top1, c_top2 = st.columns([3,1])
with c_top1:
    st.markdown("**✦ TalentLens** &nbsp; <span style='color:#6B7280'>— AI Career Intelligence</span>", unsafe_allow_html=True)
with c_top2:
    st.markdown("<p style='text-align:right; color:#6B7280; font-size:13px;'>Trusted by Job Seekers</p>", unsafe_allow_html=True)

# --- HERO ---
st.markdown("""
<div class="hero">
<span>CAREER INTELLIGENCE • AI POWERED</span>
<h1>Turn your CV into a clear<br>career direction.</h1>
<p>Upload your CV. Get your score, skills, gaps, and a roadmap to your next job — in seconds.</p>
</div>
""", unsafe_allow_html=True)

# --- TRUST BADGES ---
b1, b2, b3, b4 = st.columns(4)
b1.metric("CVs Analyzed", "2,500+")
b2.metric("Avg. Score Boost", "+32%")
b3.metric("Career Paths", "50+")
b4.metric("Analysis Time", "10 sec")

left, right = st.columns([1.25, 0.85], gap="large")

with left:
    st.markdown('<div class="card"><h3>📄 Analyze Your CV</h3><p style="color:#6B7280; font-size:14px;">Upload your resume and tell us your goal.</p></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload CV (PDF, DOCX, TXT)", type=["pdf","docx","txt"])
    role = st.text_input("Target Job Title", placeholder="e.g. Python Developer, Data Analyst, Designer")
    cc1, cc2 = st.columns(2)
    with cc1:
        level = st.selectbox("Experience Level", ["Student / Fresh Graduate", "Entry Level", "Mid Level", "Senior Level"])
    with cc2:
        focus = st.selectbox("Focus", ["Full CV Review", "Technical Skills", "Career Opportunities", "CV Improvement"])
    run = st.button("✦ Analyze My CV →", type="primary", use_container_width=True)

with right:
    st.markdown("""
    <div class="card">
    <h3>What you will get</h3>
    <p>✅ <b>CV Score</b> <span style="color:#6B7280">— How strong is your CV?</span></p>
    <p>✅ <b>Skills Profile</b> <span style="color:#6B7280">— Technical + Soft Skills</span></p>
    <p>✅ <b>Missing Skills</b> <span style="color:#6B7280">— What recruiters want</span></p>
    <p>✅ <b>Career Opportunities</b> <span style="color:#6B7280">— Roles that fit you</span></p>
    <p>✅ <b>Learning Roadmap</b> <span style="color:#6B7280">— What to learn next</span></p>
    </div>
    <div class="card" style="background:#EEF2FF; border-color:#C7D2FE;">
    <h3>⭐ Client Review</h3>
    <p style="color:#4338CA; font-style:italic;">"This tool showed me exactly what was missing in my CV. I fixed it and got 3 interview calls in one week!"</p>
    <p style="font-size:13px; color:#6B7280;">— Ayesha K., Python Developer</p>
    </div>
    """, unsafe_allow_html=True)

# --- RESULT ---
if run:
    if not uploaded:
        st.warning("Please upload your CV first.")
    elif not role:
        st.warning("Please enter your target job title.")
    else:
        try:
            with st.spinner("AI is reading your CV..."):
                text = extract_text(uploaded)
                if len(text.strip()) < 80:
                    st.error("Could not read CV. Try a text-based file.")
                    st.stop()
                r = analyze_cv(text, role, level, focus)
            st.success("✅ Analysis Complete!")
            st.divider()
            m1, m2, m3 = st.columns(3)
            m1.metric("CV Score", f"{r.get('score',0)} / 100")
            m2.metric("Technical Skills", len(r.get('skills',{}).get('technical',[])))
            m3.metric("Missing Skills", len(r.get('missing_skills',[])))
            st.progress(r.get('score',0)/100)
            st.markdown(f'<div class="card"><h3>📌 Summary</h3><p>{r.get("summary","")}</p></div>', unsafe_allow_html=True)
            a, b = st.columns(2)
            with a:
                st.markdown('<div class="card"><h3>🛠 Technical Skills</h3>', unsafe_allow_html=True)
                for s in r.get('skills',{}).get('technical',[]): st.markdown(f'<span class="tag">{s}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('<div class="card"><h3>📚 Skills To Learn</h3>', unsafe_allow_html=True)
                for s in r.get('skills_to_learn',[]): st.write(f"• {s}")
                st.markdown('</div>', unsafe_allow_html=True)
            with b:
                st.markdown('<div class="card"><h3>⚠️ Missing Skills</h3>', unsafe_allow_html=True)
                for s in r.get('missing_skills',[]): st.markdown(f'<span class="tag tag-orange">{s}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('<div class="card"><h3>🚀 Career Opportunities</h3>', unsafe_allow_html=True)
                for s in r.get('career_opportunities',[]): st.write(f"• {s}")
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="card"><h3>✨ Improvement Plan</h3>', unsafe_allow_html=True)
            for s in r.get('improvements',[])+r.get('ats_tips',[]): st.write(f"• {s}")
            st.markdown('</div>', unsafe_allow_html=True)
            st.caption("Made with ❤️ by TalentLens — AI suggestions are guidance, not a hiring decision.")
        except Exception as e:
            st.error(f"Error: {e}")
