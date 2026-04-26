import fitz  # pymupdf 
import io 

def extract_text_from_pdf(file_bytes: bytes) -> str: 
    """ 
    Extract text from PDF bytes using PyMuPDF. 
    Handles both text-based and basic scanned PDFs. 
    """ 
    try: 
        doc = fitz.open(stream=file_bytes, filetype="pdf") 
        text_parts = [] 
        
        for page_num in range(len(doc)): 
            page = doc.load_page(page_num) 
            text = page.get_text("text") 
            if text.strip(): 
                text_parts.append(text) 
        
        doc.close() 
        full_text = "\n".join(text_parts).strip() 
        
        if not full_text: 
            raise ValueError("PDF appears to be scanned or image-based. No text found.") 
            
        return full_text 
        
    except Exception as e: 
        raise ValueError(f"Could not extract text from PDF: {str(e)}")
