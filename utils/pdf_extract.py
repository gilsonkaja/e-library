"""PDF text extraction utilities."""

import io
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF bytes using pdfminer.six.
    
    Args:
        pdf_bytes: PDF file as bytes
        
    Returns:
        Extracted text from PDF
    """
    try:
        output = io.StringIO()
        extract_text_to_fp(io.BytesIO(pdf_bytes), output, laparams=LAParams())
        text = output.getvalue()
        output.close()
        return text.strip()
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""
