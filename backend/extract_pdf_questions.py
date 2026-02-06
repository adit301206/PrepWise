import pdfplumber
import os
import re

def clean_text(text):
    if text:
        return text.strip().replace("\n", " ")
    return ""

def extract_questions(pdf_path):
    questions = []
    print(f"📄 Processing {os.path.basename(pdf_path)}...")
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            tables = page.extract_table()
            if tables:
                for row in tables:
                    # Filter out header rows or empty rows
                    # Row structure based on visual inspection: 
                    # [SrNo, Unit, Question, Answer, Marks, Opt1, Opt2, Opt3, Opt4]
                    # Sometimes None or empty strings
                    
                    # Heuristic: Column 0 should be a number (SrNo) or column 1 (Unit)
                    if not row or len(row) < 5: continue
                    
                    # Check if header
                    if str(row[0]).lower().startswith("sr"): continue
                    
                    # Clean Row
                    cleaned_row = [clean_text(cell) for cell in row]
                    
                    # We expect mostly 9 columns, but let's handle variations
                    # (Unit_num, Question, Ans, Opt1...Opt4)
                    
                    # Our seed expectation: (Unit, Question, Ans, Opt1, Opt2, Opt3, Opt4)
                    # Maps to indices:
                    # Unit -> 1
                    # Question -> 2
                    # Ans -> 3
                    # Opt1 -> 5
                    # Opt2 -> 6
                    # Opt3 -> 7
                    # Opt4 -> 8
                    
                    if len(cleaned_row) >= 9:
                        unit = cleaned_row[1]
                        q_text = cleaned_row[2]
                        ans_text = cleaned_row[3]
                        opt1 = cleaned_row[5]
                        opt2 = cleaned_row[6]
                        opt3 = cleaned_row[7]
                        opt4 = cleaned_row[8]
                        
                        # Validate
                        if unit and q_text and ans_text:
                            # Sometimes Unit is just "1"
                            questions.append((unit, q_text, ans_text, opt1, opt2, opt3, opt4))
                            
    return questions

def main():
    files = [
        "e:/PrepWise/ETC_PB_NEW SYLLABUS_UNIT 01 to 05_PART 01.pdf",
        "e:/PrepWise/ETC_PB_NEW SYLLABUS_PART02_V02.pdf"
    ]
    
    all_questions = []
    for f in files:
        if os.path.exists(f):
            q_list = extract_questions(f)
            print(f"   Found {len(q_list)} questions in {os.path.basename(f)}")
            all_questions.extend(q_list)
        else:
            print(f"❌ File not found: {f}")

    print(f"\n📊 Total Extracted: {len(all_questions)}")
    
    # Write to a Python file for seeding
    output_file = "e:/PrepWise/backend/seed_data_extracted.py"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Automatically extracted from PDFs\n")
        f.write("extracted_data = [\n")
        for q in all_questions:
            # Escape quotes
            safe_q = [str(item).replace('"', "'").replace('\\', '\\\\') for item in q]
            f.write(f'    ("{safe_q[0]}", "{safe_q[1]}", "{safe_q[2]}", "{safe_q[3]}", "{safe_q[4]}", "{safe_q[5]}", "{safe_q[6]}"),\n')
        f.write("]\n")
        
    print(f"✅ Saved to {output_file}")

if __name__ == "__main__":
    main()
