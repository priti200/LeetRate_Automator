import pandas as pd
import requests
import time
import csv
import os
import concurrent.futures
from datetime import datetime
import sys

# Configuration
EXCEL_FILE = "CP handles(1-434).xlsx"
OUTPUT_FILE = "output.csv"
API_BASE_URL = "https://alfa-leetcode-api.onrender.com"
BATCH_SIZE = 5
SLEEP_TIME = 10       # 10 seconds between batches
LONG_SLEEP = 1200     # 20 minutes sleep on rate limit

def clean_handle(handle):
    if pd.isna(handle):
        return None
    handle = str(handle).strip()
    if 'leetcode.com' in handle:
        if '/u/' in handle:
            return handle.split('/u/')[-1].strip('/').strip()
        parts = handle.strip('/').split('/')
        return parts[-1]
    return handle

def fetch_rating(student_data):
    username = student_data['username']
    url = f"{API_BASE_URL}/{username}/contest"
    result = student_data.copy()
    # Reset status for this attempt
    result.update({
        "rating": 0, "global_rank": 0, "attended": 0, "success": False, "error": "Pending"
    })
    
    try:
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            data = response.json()
            result.update({
                "rating": int(data.get("contestRating", 0)),
                "global_rank": int(data.get("contestGlobalRanking", 0)),
                "attended": int(data.get("contestAttend", 0)),
                "success": True,
                "error": ""
            })
        elif response.status_code == 429:
            result["error"] = "429 Rate Limit"
        elif response.status_code == 404:
             result["error"] = "404 Not Found"
             result["success"] = False 
        else:
            result["error"] = f"{response.status_code}"
    except Exception as e:
        result["error"] = str(e)
    
    return result

def main():
    print(f"[{datetime.now()}] Reading {EXCEL_FILE}...", flush=True)
    try:
        df = pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        print(f"Error: {EXCEL_FILE} not found.", flush=True)
        return

    # Identify columns
    possible_handle_cols = [c for c in df.columns if "Leetcode" in str(c) or "LeetCode" in str(c)]
    if not possible_handle_cols:
        print("Error: Could not find LeetCode handle column.", flush=True)
        return
    handle_col = possible_handle_cols[0]
    name_col = next((c for c in df.columns if "Name" in str(c)), df.columns[4] if len(df.columns)>4 else None)
    roll_col = next((c for c in df.columns if "Roll number" in str(c)), df.columns[6] if len(df.columns)>6 else None)

    # Load all students
    all_students = {}
    for _, row in df.iterrows():
        handle = clean_handle(row[handle_col])
        if handle:
            all_students[handle] = {
                "roll_number": str(row[roll_col]).strip() if pd.notna(row[roll_col]) else "",
                "name": str(row[name_col]).strip() if pd.notna(row[name_col]) else "",
                "username": handle,
                "rating": 0, "global_rank": 0, "attended": 0, "success": False, "error": "Pending"
            }
    
    print(f"Total students in Excel: {len(all_students)}", flush=True)

    # Loop forever until done
    while True:
        # Load existing results to update status
        if os.path.exists(OUTPUT_FILE):
             try:
                with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        uname = row['username']
                        if uname in all_students:
                            all_students[uname].update(row)
                            # Handle types and explicit success flag
                            if 'success' in row:
                                all_students[uname]['success'] = (row.get('success') == 'True')
                            else:
                                 # Fallback for old file format
                                all_students[uname]['success'] = (not row.get('error'))
             except Exception as e:
                 print(f"Error reading CSV: {e}", flush=True)

        # Identify pending
        pending_students = []
        for s in all_students.values():
             if s['success']:
                 continue
             # Do not retry 404s
             if '404' in str(s.get('error', '')):
                 continue
             pending_students.append(s)

        if not pending_students:
            print(f"[{datetime.now()}] All students processed (success or 404). Done!", flush=True)
            break
        
        print(f"[{datetime.now()}] Starting pass. Pending: {len(pending_students)}", flush=True)
        
        consecutive_429s = 0
        total = len(pending_students)
        
        for i in range(0, total, BATCH_SIZE):
            batch = pending_students[i:i + BATCH_SIZE]
            print(f"  [{datetime.now()}] Batch {i//BATCH_SIZE + 1} ({i+1}-{min(i+BATCH_SIZE, total)}/{total})...", flush=True)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                future_to_user = {executor.submit(fetch_rating, student): student['username'] for student in batch}
                for future in concurrent.futures.as_completed(future_to_user):
                    res = future.result()
                    all_students[res['username']] = res
                    
                    if "429" in str(res['error']):
                        consecutive_429s += 1
                        print(f"    [429] {res['username']}", flush=True)
                    else:
                        consecutive_429s = 0 # Reset on any non-429 response
                        if res['success']:
                             print(f"    [OK] {res['username']} ({res['rating']})", flush=True)
                        else:
                             print(f"    [FAIL] {res['username']}: {res['error']}", flush=True)
            
            # Save progress
            fieldnames = ["roll_number", "name", "username", "rating", "global_rank", "attended", "success", "error"]
            try:
                with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                    writer.writeheader()
                    writer.writerows(all_students.values())
            except Exception as e:
                print(f"Error writing CSV: {e}", flush=True)

            # Check for blocking
            if consecutive_429s >= 5:
                print(f"[{datetime.now()}] Too many 429s (>=5). Sleeping {LONG_SLEEP}s...", flush=True)
                time.sleep(LONG_SLEEP)
                consecutive_429s = 0 # Reset after long sleep
            else:
                time.sleep(SLEEP_TIME)

        # After full pass, check again
        remaining = [s for s in all_students.values() if not s['success'] and '404' not in str(s.get('error', ''))]
        if remaining:
            print(f"[{datetime.now()}] Pass complete. {len(remaining)} remaining. Sleeping {LONG_SLEEP}s before retry...", flush=True)
            time.sleep(LONG_SLEEP)
        else:
            print("Pass complete. All done.", flush=True)
            break

if __name__ == "__main__":
    main()
