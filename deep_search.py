import csv
import requests
import time
import random

FILENAME = 'new_batch_ratings.csv'
API_BASE_URL = "https://alfa-leetcode-api.onrender.com"

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
]

def check_profile_exists(username):
    try:
        # Check basic profile endpoint
        # Using a fresh session or requests to avoid persistent 429s
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        r = requests.get(f"{API_BASE_URL}/{username}", headers=headers, timeout=10)
        
        if r.status_code == 200:
            return True, None
        elif r.status_code == 404:
            return False, "Invalid Username"
        elif r.status_code == 429:
            return False, "Rate Limited"
        else:
            return False, f"Error {r.status_code}"
    except Exception as e:
        return False, str(e)

def fetch_rating(username):
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        r = requests.get(f"{API_BASE_URL}/{username}/contest", headers=headers, timeout=15)
        if r.status_code == 200:
            d = r.json()
            return {
                'rating': int(d.get('contestRating', 0)),
                'global_rank': int(d.get('contestGlobalRanking', 0)),
                'attended': int(d.get('contestAttend', 0)),
                'top_percentage': float(d.get('contestTopPercentage', 0.0)),
                'success': True
            }
        return None
    except:
        return None

def main():
    print("Beginning DEEP SEARCH (Profile Check)...")
    
    # Load
    rows = []
    fieldnames = []
    try:
        with open(FILENAME, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
    except:
        print("File not found.")
        return

    failed_indices = []
    for i, row in enumerate(rows):
        # Identify failure candidates
        try:
            rating = int(row['Rating']) if row.get('Rating') and row['Rating'] != '-' else 0
        except:
            rating = 0
            
        if rating == 0:
            failed_indices.append(i)

    print(f"Checking {len(failed_indices)} students...")

    for count, idx in enumerate(failed_indices, 1):
        row = rows[idx]
        username = row['Username']
        print(f"[{count}/{len(failed_indices)}] {username}...", end='', flush=True)

        # 1. Check Profile
        exists, status_msg = check_profile_exists(username)
        
        if not exists:
            if status_msg == "Invalid Username":
                print(" INVALID USERNAME (404)")
                rows[idx]['Status'] = "Invalid Username"
            elif status_msg == "Rate Limited":
                print(" Rate Limited (429) - Sleeping 30s...")
                time.sleep(30)
                # Retry once?
            else:
                print(f" {status_msg}")
        else:
            # 2. Profile Exists -> Fetch Rating
            print(" Exists. Fetching Rating...", end='', flush=True)
            res = fetch_rating(username)
            if res and res['success'] and res['rating'] > 0:
                print(f" FIXED! ({res['rating']})")
                rows[idx]['Rating'] = res['rating']
                rows[idx]['Global Rank'] = res['global_rank']
                rows[idx]['Contests'] = res['attended']
                rows[idx]['Top %'] = f"{res['top_percentage']}%"
                rows[idx]['Status'] = "Success"
                rows[idx]['Rank'] = "-"
            else:
                print(" No Data/Fail.")
                # If profile exists but no rating, maybe they never did a contest
                rows[idx]['Status'] = "No Contest Data"

        # Save updates as we go
        saved = False
        attempts = 0
        while not saved and attempts < 3:
            try:
                with open(FILENAME, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
                saved = True
            except PermissionError:
                print(f" [Save Failed: Permission Denied. Retrying...]")
                time.sleep(2)
                attempts += 1
            except Exception as e:
                print(f" [Save Failed: {e}]")
                break

            
        time.sleep(5) 

    print("\nDeep Search Complete.")

if __name__ == "__main__":
    main()
