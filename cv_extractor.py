from io import BytesIO
import fitz  # PyMuPDF
from docx import Document


def extract_text_from_uploaded_file(uploaded_file) -> str:
    """Extract readable text from an uploaded PDF or DOCX file."""
    filename = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()

    if filename.endswith(".pdf"):
        return _extract_pdf(file_bytes)
    if filename.endswith(".docx"):
        return _extract_docx(file_bytes)

    raise ValueError("Unsupported file type. Please upload a PDF or DOCX file.")


def _extract_pdf(file_bytes: bytes) -> str:
    try:
        text_parts = []
        with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
            for page in pdf:
                text_parts.append(page.get_text("text"))
        return "\n".join(text_parts).strip()
    except Exception as exc:
        raise ValueError(f"Could not read this PDF: {exc}") from exc


def _extract_docx(file_bytes: bytes) -> str:
    try:
        document = Document(BytesIO(file_bytes))
        paragraphs = [p.text for p in document.paragraphs if p.text.strip()]

        # Also extract text from tables, which are common in CV templates.
        for table in document.tables:
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if cells:
                    paragraphs.append(" | ".join(cells))

        return "\n".join(paragraphs).strip()
    except Exception as exc:
        raise ValueError(f"Could not read this DOCX file: {exc}") from exc
