import os
import json
from groq import Groq

def analyze_cv(cv_text, role, level):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            api_key = None

    if not api_key:
        raise Exception("GROQ_API_KEY not found in Secrets")

    client = Groq(api_key=api_key)

    prompt = f"""
    You are a career expert. Analyze this CV for the target role: {role}, Level: {level}.
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
