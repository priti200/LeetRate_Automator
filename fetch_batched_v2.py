import time
import json
import csv
import requests
import os

API_BASE_URL = "https://alfa-leetcode-api.onrender.com"
OUTPUT_FILE = 'final_ratings_no_status.csv'
INPUT_FILE = 'Leetcode-handles.csv'
BATCH_COUNT = 3
BATCH_WAIT_SECONDS = 300  # 5 minutes wait between batches
REQUEST_DELAY = 3  # 3 seconds between requests

def load_students(filename):
    students = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[1:]: # Skip header
                parts = line.strip().split(',')
                if len(parts) >= 10:
                    name = parts[4].strip().strip('"')
                    roll = parts[6].strip().strip('"')
                    user = parts[-1].strip().strip('"')
                    if user.startswith('http') and '/u/' in user:
                        user = user.split('/u/')[-1].strip('/').strip()
                    if user:
                        students.append({'name': name, 'roll_number': roll, 'username': user})
    except Exception as e:
        print(f"Error loading students: {e}")
    return students

def fetch_student_data(session, student):
    username = student['username']
    try:
        r = session.get(f"{API_BASE_URL}/{username}/contest", timeout=10)
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
        else:
            return {**student, 'rating': 0, 'global_rank': 0, 'attended': 0, 'top_percentage': 0.0, 'success': False}
    except Exception:
        return {**student, 'rating': 0, 'global_rank': 0, 'attended': 0, 'top_percentage': 0.0, 'success': False}

def save_results(results):
    # Sort: Successful first, then by rating (descending)
    sorted_results = sorted(results, key=lambda x: (x.get('success', False), x.get('rating', 0)), reverse=True)
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        # Header without Status
        w.writerow(["Rank", "Name", "Roll Number", "Username", "Rating", "Global Rank", "Contests", "Top %"])
        
        rank = 1
        for r in sorted_results:
            # Only give rank if they have a rating > 0
            current_rank = rank if r.get('rating', 0) > 0 else "-"
            
            w.writerow([
                current_rank, 
                r['name'], 
                r['roll_number'], 
                r['username'],
                r['rating'], 
                r['global_rank'], 
                r['attended'], 
                f"{r['top_percentage']}%"
            ])
            
            if r.get('rating', 0) > 0:
                rank += 1
    print(f"Results saved to {OUTPUT_FILE}")

def main():
    print(f"Starting LeetCode Rating Fetcher...")
    students = load_students(INPUT_FILE)
    if not students:
        print("No students found. Exiting.")
        return

    # Batch logic
    batch_size = (len(students) + BATCH_COUNT - 1) // BATCH_COUNT
    batches = [students[i:i + batch_size] for i in range(0, len(students), batch_size)]
    
    print(f"Total students: {len(students)}")
    print(f"Split into {len(batches)} batches.")
    
    all_results = []
    session = requests.Session()
    
    for batch_idx, batch in enumerate(batches):
        print(f"\nProcessing Batch {batch_idx + 1}/{len(batches)} ({len(batch)} students)...")
        
        for i, student in enumerate(batch):
            print(f"  [{i+1}/{len(batch)}] {student['username']}...", end='', flush=True)
            result = fetch_student_data(session, student)
            all_results.append(result)
            
            if result['success']:
                print(f" OK ({result['rating']})")
            else:
                print(f" Failed")
            
            # Save incrementally after every student (robustness)
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
