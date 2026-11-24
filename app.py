import streamlit as st
from cv_extractor import extract_text_from_uploaded_file
from ai_analyzer import analyze_cv

st.set_page_config(
    page_title="AI CV Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 1200px;}
    .hero {padding: 1.5rem 1.7rem; border-radius: 18px;
           background: linear-gradient(120deg, #14213d, #263b68); color: white; margin-bottom: 1.2rem;}
    .hero h1 {color: white; margin-bottom: .35rem;}
    .hero p {color: #e4eaf5; margin-bottom: 0;}
    .metric-card {padding: 1rem; border: 1px solid rgba(128,128,128,.25);
                  border-radius: 14px; min-height: 110px;}
    .muted {color: #7b8494; font-size: .9rem;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("📄 CV Analyzer")
    st.caption("AI-powered career insights")
    st.divider()
    st.markdown("### How it works")
    st.markdown(
        "1. Upload your CV\n"
        "2. Select your target role\n"
        "3. Run the AI analysis\n"
        "4. Review your career insights"
    )
    st.divider()
    st.caption("Your uploaded file is processed in memory and is not saved by this app.")

st.markdown("""
<div class="hero">
  <h1>AI CV Analyzer</h1>
  <p>Understand your skills, identify skill gaps, and explore career directions.</p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1.15, 0.85], gap="large")

with left:
    st.subheader("1. Upload your CV")
    uploaded_file = st.file_uploader(
        "Choose a PDF or DOCX file",
        type=["pdf", "docx"],
        help="For best results, upload a text-based PDF or a DOCX document.",
    )
    st.subheader("2. Choose your career target")
    target_role = st.text_input(
        "Target job role (optional)",
        placeholder="e.g. Junior Python Developer, Data Analyst, UI/UX Designer",
    )
    experience_level = st.selectbox(
        "Your experience level",
        ["Not specified", "Student / Fresh graduate", "Entry level", "Mid level", "Senior level"],
    )
    analyze_button = st.button(
        "✨ Analyze my CV",
        type="primary",
        use_container_width=True,
        disabled=uploaded_file is None,
    )

with right:
    st.subheader("What you'll receive")
    st.markdown("""
    - **Skill profile:** technical and soft skills found in your CV
    - **Skill gaps:** useful skills to develop for your target role
    - **Career directions:** job roles that may fit your background
    - **CV feedback:** practical improvements to strengthen your CV
    - **Action plan:** suggested next learning steps
    """)
    st.info("AI suggestions are guidance, not a hiring decision or a guarantee of employment.")

if analyze_button and uploaded_file is not None:
    try:
        with st.spinner("Reading your CV..."):
            cv_text = extract_text_from_uploaded_file(uploaded_file)

        if len(cv_text.strip()) < 80:
            st.error(
                "Not enough readable text was found. If this is a scanned PDF, "
                "try a text-based PDF or a DOCX file."
            )
            st.stop()

        with st.spinner("AI is reviewing your CV. This may take a few moments..."):
            result = analyze_cv(
                cv_text=cv_text,
                target_role=target_role.strip(),
                experience_level=experience_level,
            )

        st.session_state["cv_analysis"] = result
        st.session_state["cv_target_role"] = target_role.strip()

    except Exception as exc:
        st.error(f"Analysis failed: {exc}")
        st.caption("Check your Groq API key, model name, internet connection, and uploaded file.")

if "cv_analysis" in st.session_state:
    result = st.session_state["cv_analysis"]
    st.divider()
    st.header("Your CV analysis")

    score = result.get("overall_profile_score")
    summary = result.get("profile_summary", "No summary was returned.")
    if isinstance(score, (int, float)):
        st.metric("Profile readiness score", f"{max(0, min(100, int(score)))}/100")
    st.write(summary)

    skills = result.get("skills", {})
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Technical skills")
        technical = skills.get("technical", [])
        if technical:
            st.write(" · ".join(str(x) for x in technical))
        else:
            st.write("No technical skills identified.")
    with c2:
        st.subheader("Soft skills")
        soft = skills.get("soft", [])
        if soft:
            st.write(" · ".join(str(x) for x in soft))
        else:
            st.write("No soft skills identified.")

    st.subheader("Potential skill gaps")
    gaps = result.get("missing_skills", [])
    if gaps:
        for item in gaps:
            if isinstance(item, dict):
                st.markdown(f"**{item.get('skill', 'Skill')}** — {item.get('why_it_matters', '')}")
                if item.get("priority"):
                    st.caption(f"Priority: {item['priority']}")
            else:
                st.write(f"• {item}")
    else:
        st.write("No specific skill gaps were returned.")

    st.subheader("Career opportunities to explore")
    opportunities = result.get("career_opportunities", [])
    if opportunities:
        for item in opportunities:
            if isinstance(item, dict):
                with st.expander(item.get("job_title", "Suggested role")):
                    st.write(item.get("why_it_fits", ""))
                    if item.get("skills_to_build"):
                        st.markdown("**Skills to build:** " + ", ".join(item["skills_to_build"]))
            else:
                st.write(f"• {item}")
    else:
        st.write("No career suggestions were returned.")

    st.subheader("CV improvement suggestions")
    suggestions = result.get("cv_improvements", [])
    for suggestion in suggestions:
        st.markdown(f"- {suggestion}")

    st.subheader("Suggested action plan")
    action_plan = result.get("action_plan", [])
    for step in action_plan:
        st.markdown(f"- {step}")

    st.caption(result.get("limitations", "This analysis is based only on the text available in the uploaded CV."))
    report_text = "# AI CV Analyzer Report\n\n"
    report_text += f"## Profile summary\n{summary}\n\n"
    report_text += f"## Technical skills\n{', '.join(map(str, skills.get('technical', [])))}\n\n"
    report_text += f"## Soft skills\n{', '.join(map(str, skills.get('soft', [])))}\n\n"
    report_text += "## Missing skills\n" + "\n".join(
        f"- {x.get('skill')}: {x.get('why_it_matters', '')}" if isinstance(x, dict) else f"- {x}"
        for x in gaps
    ) + "\n\n"
    report_text += "## Career opportunities\n" + "\n".join(
        f"- {x.get('job_title')}: {x.get('why_it_fits', '')}" if isinstance(x, dict) else f"- {x}"
        for x in opportunities
    ) + "\n\n"
    report_text += "## CV improvements\n" + "\n".join(f"- {x}" for x in suggestions)
    report_text += "\n\n## Action plan\n" + "\n".join(f"- {x}" for x in action_plan)

    st.download_button(
        "⬇️ Download analysis report",
        data=report_text,
        file_name="cv_analysis_report.md",
        mime="text/markdown",
        use_container_width=True,
    )

st.divider()
st.caption("Privacy note: Avoid uploading CVs containing information you do not want processed by an AI service. The CV text is sent to Groq to generate the analysis. This starter app does not store uploaded CVs or analysis results in a database.")
