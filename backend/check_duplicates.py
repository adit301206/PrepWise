import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("DATABASE_URL")
if url and url.startswith("postgres://"): url = url.replace("postgres://", "postgresql://", 1)

try:
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    
    print("🔍 Checking for Duplicates (Fuzzy/Normalized)...")
    
    cur.execute("SELECT question_id, question_text FROM questions ORDER BY question_text")
    rows = cur.fetchall()
    
    seen_texts = {} # normalized_text -> [ids]
    duplicates = []
    
    import re
    
    # Method 1: Advanced Normalization (Remove leading numbers, lower, strip)
    # Regex to remove "1. ", "10 ", "Q1.", etc.
    clean_pattern = re.compile(r'^[\d\.\)\s]+')
    
    for q_id, q_text in rows:
        # 1. Lowercase and strip
        norm = q_text.strip().lower()
        # 2. Remove leading numbering
        norm = clean_pattern.sub('', norm)
        
        if norm in seen_texts:
            seen_texts[norm].append((q_id, q_text))
        else:
            seen_texts[norm] = [(q_id, q_text)]
            
    print(f"\n--- Method 1: regex-clean Normalization ---")
    
    total_redundant = 0
    ids_to_delete = []
    
    for norm, items in seen_texts.items():
        if len(items) > 1:
            print(f"\nMatch: '{norm[:50]}...'")
            # Keep the one with the shortest text? Or longest?
            # Usually the one WITHOUT numbers is better? Or the one with 'cleaner' look.
            # Let's assume we keep the one that looks "best" or just the first one ID-wise.
            # Maybe keep the one that matches the "new" seed format?
            
            # Sort by length (shortest might be cleaner if numbers are stripped? No, "1. What" is longer than "What")
            # Sort by ID (keep latest?)
            
            items.sort(key=lambda x: x[0]) # Low ID to High ID
            
            original = items[0]
            redundant = items[1:]
            
            print(f"   KEEP: [{original[0]}] {original[1][:60]}...")
            for r in redundant:
                print(f"   DEL : [{r[0]}] {r[1][:60]}...")
                ids_to_delete.append(r[0])
            
            total_redundant += len(redundant)

    print(f"\nTotal duplicates found: {total_redundant}")
    
    if ids_to_delete:
         print(f"Deleting {len(ids_to_delete)} records...")
         # Uncomment to execute deletion
         cur.execute("DELETE FROM questions WHERE question_id = ANY(%s)", (ids_to_delete,))
         conn.commit()
         print("✅ Deletion Complete.")
    else:
         print("No deletion needed.")

    conn.close()

except Exception as e:
    print(f"Error: {e}")
