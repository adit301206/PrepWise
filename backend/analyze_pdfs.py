import os
import re
from pypdf import PdfReader

def extract_questions_from_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return {}

    print(f"📄 Analyzing: {pdf_path}...")
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    # Normalize patterns
    # Look for question patterns like "1. ", "1)", etc. followed by text
    # This is a rough heuristic to count potential questions
    
    # We will try to group by Units if possible, but first let's just count total questions
    # Identifying clusters
    
    # Updated regex based on text sample
    # Pattern: Start of line -> digits -> space -> digits -> space -> text
    # e.g., "1 1 Which..."
    question_pattern = r'\n\s*(\d+)\s+(\d+)\s+'
    matches = re.findall(question_pattern, text)
    
    # Also try to print the FIRST and LAST match to verify range
    if matches:
        first_q = matches[0] # (Sr, Unit)
        last_q = matches[-1]
        print(f"   Matches found: {len(matches)}. Range: {first_q} to {last_q}")
    else:
        print("   No match found.")
        
    print(f"   Found ~{len(matches)} matches for question numbering.")
    
    # Debug: Save sample text
    with open(f"backend/pdf_sample_{os.path.basename(pdf_path)}.txt", "w", encoding="utf-8") as debug_f:
        debug_f.write(text[:5000]) # First 5000 chars
        
    return len(matches), text

def main():
    files = [
        "e:/PrepWise/ETC_PB_NEW SYLLABUS_UNIT 01 to 05_PART 01.pdf",
        "e:/PrepWise/ETC_PB_NEW SYLLABUS_PART02_V02.pdf"
    ]
    
    with open("backend/pdf_analysis_results.txt", "w", encoding="utf-8") as f:
        total_found = 0
        for pdf in files:
            count, _ = extract_questions_from_pdf(pdf)
            total_found += count
            f.write(f"File: {os.path.basename(pdf)} -> Found {count} questions\n")
            
        f.write(f"\nTotal Estimated Questions in PDFs: {total_found}\n")
        f.write(f"Current DB Count for Subject: ~393\n")
        
    print("Analysis complete. Check backend/pdf_analysis_results.txt")

if __name__ == "__main__":
    main()
