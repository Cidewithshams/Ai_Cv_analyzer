import json
import os
import re
import streamlit as st
from groq import Groq


def _get_secret(name: str, default=None):
    """Read a value from Streamlit secrets, then environment variables."""
    try:
        value = st.secrets.get(name)
        if value:
            return value
    except Exception:
        pass
    return os.getenv(name, default)


def _extract_json(content: str) -> dict:
    """Parse JSON returned by the model, including fenced JSON responses."""
    cleaned = content.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end > start:
            return json.loads(cleaned[start:end + 1])
        raise ValueError("The AI returned an unreadable response. Please try again.")


def analyze_cv(cv_text: str, target_role: str = "", experience_level: str = "Not specified") -> dict:
    api_key = _get_secret("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "Groq API key not found. Add GROQ_API_KEY to Streamlit Secrets "
            "or your local .streamlit/secrets.toml file."
        )

    model = _get_secret("GROQ_MODEL", "llama-3.3-70b-versatile")
    client = Groq(api_key=api_key)

    # Keep the request bounded to avoid sending an excessively large CV.
    cv_text = cv_text[:18000]

    system_prompt = """
You are a careful career coach and CV reviewer. Analyze only information supported by the CV.
Do not invent qualifications, employers, dates, achievements, or skills.
Distinguish skills explicitly stated in the CV from reasonable suggestions.
A skill being absent from a CV does not prove the person does not have it.
Explain that missing_skills are potential gaps to consider for the target role, not confirmed deficiencies.
Suggest realistic career directions based on the person's evidence and experience.
Return ONLY valid JSON using exactly this structure:
{
  "overall_profile_score": 0,
  "profile_summary": "short balanced summary",
  "skills": {
    "technical": ["skill"],
    "soft": ["skill"]
  },
  "missing_skills": [
    {"skill": "skill name", "why_it_matters": "short explanation", "priority": "High/Medium/Low"}
  ],
  "career_opportunities": [
    {"job_title": "role", "why_it_fits": "evidence-based reason", "skills_to_build": ["skill"]}
  ],
  "cv_improvements": ["specific suggestion"],
  "action_plan": ["practical next step"],
  "limitations": "brief note about uncertainty and the fact that this is AI-generated guidance"
}
Use 0-100 for overall_profile_score as a broad CV presentation/readiness estimate, not a prediction of hiring success.
Keep the response concise, useful, respectful, and appropriate for a student or job seeker.
If there is not enough information, say so rather than guessing.
"""

    user_prompt = f"""
Target role: {target_role or "Not specified"}
Experience level selected by user: {experience_level}

CV TEXT:
---
{cv_text}
---

Analyze this CV and return the JSON object requested.
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=2200,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        return _extract_json(content)
    except Exception as exc:
        # Some model deployments may not support JSON mode.
        if "response_format" in str(exc).lower() or "json" in str(exc).lower():
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.2,
                    max_tokens=2200,
                )
                return _extract_json(response.choices[0].message.content or "{}")
            except Exception as retry_exc:
                raise RuntimeError(f"Groq request failed: {retry_exc}") from retry_exc
        raise RuntimeError(f"Groq request failed: {exc}") from exc
