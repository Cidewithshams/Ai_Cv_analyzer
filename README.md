# AI CV Analyzer

A Streamlit application that uses Groq AI to review a CV and provide skills insights, potential skill gaps, career directions, CV improvement suggestions, and an action plan.

## Features

- Upload a CV in PDF or DOCX format
- Extract text from the uploaded document
- Identify technical and soft skills
- Suggest potential skill gaps for a target role
- Recommend career directions to explore
- Provide CV improvement suggestions and a learning action plan
- Download the analysis as a Markdown report

## Tech stack

- Python
- Streamlit
- Groq API
- PyMuPDF
- python-docx

## Run locally

1. Clone this repository:

   ```bash
   git clone https://github.com/YOUR-USERNAME/AI-CV-Analyzer.git
   cd AI-CV-Analyzer
   ```

2. Create and activate a virtual environment (recommended):

   ```bash
   python -m venv .venv
   ```

   Windows:

   ```bash
   .venv\Scripts\activate
   ```

   macOS/Linux:

   ```bash
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create `.streamlit/secrets.toml` using `.streamlit/secrets.toml.example` as a guide:

   ```toml
   GROQ_API_KEY = "your_real_groq_api_key"
   GROQ_MODEL = "llama-3.3-70b-versatile"
   ```

5. Start the app:

   ```bash
   streamlit run app.py
   ```

## Deploy on Streamlit Community Cloud

1. Push this project to a GitHub repository.
2. Open https://share.streamlit.io/ and sign in with GitHub.
3. Create a new app and select this repository.
4. Set the main file path to `app.py`.
5. Open the app's **Advanced settings / Secrets** section.
6. Add your secrets in TOML format:

   ```toml
   GROQ_API_KEY = "your_real_groq_api_key"
   GROQ_MODEL = "llama-3.3-70b-versatile"
   ```

7. Deploy the app.

Do not put your API key in `app.py`, `README.md`, GitHub commits, screenshots, or public messages.

## Privacy and limitations

- The app does not intentionally save uploaded CV files to a database or disk.
- CV text is sent to Groq to generate the analysis. Do not upload a CV unless you have permission to share its contents with the AI service.
- The analysis is AI-generated guidance. It can be incomplete or incorrect and must not be treated as a hiring decision.
- A skill missing from the CV may still be a skill the applicant has; it may simply not be documented.
- Scanned/image-only PDFs may not produce readable text. Use a text-based PDF or DOCX file.

## Project structure

```text
AI-CV-Analyzer/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── secrets.toml.example
└── utils/
    ├── __init__.py
    ├── ai_analyzer.py
    └── cv_extractor.py
```

## License

You may add a license file if you plan to publish or distribute this project.
