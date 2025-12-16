import pymupdf4llm

def load_pdf_content(file_path: str) -> str:
    """
    Converts a PDF to Markdown using PyMuPDF4LLM.
    This preserves headers and structural context better than plain text extraction.
    """
    try:
        md_text = pymupdf4llm.to_markdown(file_path)
        return md_text
    except Exception as e:
        print(f"❌ PDF Loading Error: {e}")
        return ""