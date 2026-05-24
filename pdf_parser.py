import fitz  # PyMuPDF
import re

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file"""
    doc = fitz.open(pdf_path)
    full_text = ""
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        full_text += page.get_text()
    
    doc.close()
    
    # Clean up extra whitespace
    full_text = re.sub(r'\n+', '\n', full_text)
    full_text = full_text.strip()
    
    return full_text

def extract_text_from_bytes(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes (for file upload)"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = ""
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        full_text += page.get_text()
    
    doc.close()
    return full_text.strip()

# Test it
if __name__ == "__main__":
    # Test with any PDF on your computer
    text = extract_text_from_pdf("test_resume.pdf")
    print(text[:500])  # Print first 500 chars
    print("✅ PDF parser working!")