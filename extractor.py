import fitz
import docx

def extract_text_from_uploaded_file(uploaded_file):
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
