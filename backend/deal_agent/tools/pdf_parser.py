from langchain_core.tools import tool
from pdfminer.high_level import extract_text
from typing import Any

@tool
def parse_pdf_document(file_path: str) -> str:
    """
    Parse a PDF document and extract its text content.
    Useful for ingesting CIMs, NDAs, or financial reports.
    
    Args:
        file_path: The absolute path to the PDF file.
    """
    try:
        # Using pdfminer.six directly to avoid unstructured dependency issues
        text_content = extract_text(file_path)
        
        # Truncate if too long for a single tool output (optional safety)
        if len(text_content) > 10000:
            return text_content[:10000] + "... (truncated)"
            
        return text_content
    except Exception as e:
        return f"Error parsing PDF: {str(e)}"
