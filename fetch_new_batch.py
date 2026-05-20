import time
import json
import csv
import requests
import os

API_BASE_URL = "https://alfa-leetcode-api.onrender.com"
OUTPUT_FILE = 'new_batch_ratings.csv'
INPUT_FILE = 'CP handles(1-234).csv'
BATCH_COUNT = 4
BATCH_WAIT_SECONDS = 300  # 5 minutes wait
REQUEST_DELAY = 3  # 3 seconds between requests

def load_students(filename):
    students = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Skip header (row 1 and 2 seem to be header/empty based on the preview)
            # Line 1 is header, Line 2 is empty quote maybe? Let's inspect first valid line
            start_idx = 1
            if len(lines) > 1 and lines[1].strip() == '"': 
                start_idx = 2
            
            for line in lines[start_idx:]:
                if not line.strip(): continue # Skip empty lines
                
                # CSV parsing can be tricky with quoted fields containing commas
                # We'll use csv module to be safe but manual split is also fine if simple
                # Let's use csv.reader for robust parsing
                reader = csv.reader([line])
                parts = next(reader)
                
                if len(parts) >= 10:
                    # Index 4: Name
                    # Index 6: Roll Number
                    # Index 9: Leetcode handle
                    name = parts[4].strip()
                    roll = parts[6].strip()
                    user = parts[9].strip()
                    
                    # Clean username (remove URL)
                    if 'leetcode.com' in user or '/u/' in user:
                         # Handle https://leetcode.com/u/username/ or leetcode.com/u/username
                         try:
                             if '/u/' in user:
                                user = user.split('/u/')[-1].strip('/').strip()
                             else:
                                 # Fallback cleanup
                                 user = user.split('/')[-1].strip()
                         except:
                             pass
                    
                    # Remove query params if any
                    if '?' in user:
                        user = user.split('?')[0]

                    if user and user.lower() not in ['na', 'nil', 'null', 'none', '-', '_', 'n/a']:
                        students.append({'name': name, 'roll_number': roll, 'username': user})
    except Exception as e:
        print(f"Error loading students: {e}")
    return students

def fetch_student_data(session, student, retry=False):
    username = student['username']
    try:
        # Increased timeout
        r = session.get(f"{API_BASE_URL}/{username}/contest", timeout=15)
        if r.status_code == 200:
            d = r.json()
            return {
                **student, 
                'rating': int(d.get('contestRating', 0)), 
                'global_rank': int(d.get('contestGlobalRanking', 0)), 
                'attended': int(d.get('contestAttend', 0)), 
                'top_percentage': float(d.get('contestTopPercentage', 0.0)), 
                'success': True
            }
        elif r.status_code == 429 and not retry:
             # Simple retry once for rate limit
             time.sleep(10)
             return fetch_student_data(session, student, retry=True)
        else:
            return {**student, 'rating': 0, 'global_rank': 0, 'attended': 0, 'top_percentage': 0.0, 'success': False}
    except Exception:
        return {**student, 'rating': 0, 'global_rank': 0, 'attended': 0, 'top_percentage': 0.0, 'success': False}

def save_results(results):
    # Sort: Successful first, then by rating (descending)
    sorted_results = sorted(results, key=lambda x: (x.get('success', False), x.get('rating', 0)), reverse=True)
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        # Header MATCHING final_complete_ratings.csv
        w.writerow(["Rank", "Name", "Roll Number", "Username", "Rating", "Global Rank", "Contests", "Top %", "Status"])
        
        rank = 1
        for r in sorted_results:
            current_rank = rank if r.get('rating', 0) > 0 else "-"
            status = "Success" if r.get('success') else "Failed"
            
            w.writerow([
                current_rank, 
                r['name'], 
                r['roll_number'], 
                r['username'],
                r['rating'], 
                r['global_rank'], 
                r['attended'], 
                f"{r['top_percentage']}%",
                status
            ])
            
            if r.get('rating', 0) > 0:
                rank += 1
    print(f"Results saved to {OUTPUT_FILE}")

def main():
    print(f"Starting LeetCode Rating Fetcher (New Batch)...")
    students = load_students(INPUT_FILE)
    if not students:
        print("No students found. Exiting.")
        return

    # Batch logic
    batch_size = (len(students) + BATCH_COUNT - 1) // BATCH_COUNT
    batches = [students[i:i + batch_size] for i in range(0, len(students), batch_size)]
    
    print(f"Total valid students found: {len(students)}")
    print(f"Split into {len(batches)} batches (approx {batch_size} per batch).")
    
    all_results = []
    session = requests.Session()
    
    for batch_idx, batch in enumerate(batches):
        print(f"\nProcessing Batch {batch_idx + 1}/{len(batches)} ({len(batch)} students)...")
        
        for i, student in enumerate(batch):
            print(f"  [{i+1}/{len(batch)}] {student['username']}...", end='', flush=True)
            result = fetch_student_data(session, student)
            all_results.append(result)
            
            if result['success'] and result['rating'] > 0:
                print(f" OK ({result['rating']})")
            else:
                print(f" Failed/No Rating")
            
            # Save incrementally
            save_results(all_results)
            
            time.sleep(REQUEST_DELAY)
            
        # Waiting between batches
        if batch_idx < len(batches) - 1:
            print(f"\nBatch {batch_idx + 1} complete. Waiting {BATCH_WAIT_SECONDS} seconds to avoid rate limits...")
            for remaining in range(BATCH_WAIT_SECONDS, 0, -10):
                print(f"  Waiting... {remaining}s remaining", end='\r', flush=True)
                time.sleep(10)
            print("  Resuming...                        ")

    print(f"\nCompleted! Processed {len(all_results)} students.")

if __name__ == "__main__":
    main()
