import csv
import requests
import time
import sys

FILENAME = 'new_batch_ratings.csv'
API_BASE_URL = "https://alfa-leetcode-api.onrender.com"

def get_rating(username):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(f"{API_BASE_URL}/{username}/contest", headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return {
                'rating': int(data.get('contestRating', 0)),
                'global_rank': int(data.get('contestGlobalRanking', 0)),
                'attended': int(data.get('contestAttend', 0)),
                'top_percentage': float(data.get('contestTopPercentage', 0.0)),
                'success': True
            }
        elif response.status_code == 429:
            print(f"  Rate limited (429). Waiting 60s...")
            time.sleep(60)
            return None 
    except Exception as e:
        print(f"  Error fetching {username}: {e}")
    
    return None

def main():
    print("="*60)
    print("FINAL DEEP SWEEP - REPAIR MODE")
    print("="*60)
    print("Step 1: Cooling down API restrictions...")
    print("Waiting 2 minutes before starting requests...")
    
    # Initial Wait as requested
    for i in range(120, 0, -10):
        print(f"  {i} seconds remaining...", end='\r', flush=True)
        time.sleep(10)
    print("\nStarting fetch process now.")

    # Load Data
    rows = []
    try:
        with open(FILENAME, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
    except FileNotFoundError:
        print(f"File {FILENAME} not found!")
        return

    # Identify failures
    failed_indices = []
    for i, row in enumerate(rows):
        try:
            rating = int(row['Rating']) if row.get('Rating') and row['Rating'] != '-' else 0
        except ValueError:
            rating = 0
            
        if rating == 0:
            failed_indices.append(i)

    print(f"Found {len(failed_indices)} students to repair out of {len(rows)}.")
    
    if not failed_indices:
        print("All done! No repairs needed.")
        return

    updates_made = 0
    
    # Process
    for count, idx in enumerate(failed_indices, 1):
        row = rows[idx]
        username = row['Username']
        print(f"[{count}/{len(failed_indices)}] Fetching {username}...", end='', flush=True)
        
        result = get_rating(username)
        
        if result and result['success'] and result['rating'] > 0:
            rows[idx]['Rating'] = result['rating']
            rows[idx]['Global Rank'] = result['global_rank']
            rows[idx]['Contests'] = result['attended']
            rows[idx]['Top %'] = f"{result['top_percentage']}%"
            rows[idx]['Status'] = "Success"
            rows[idx]['Rank'] = "-" 
            
            print(f" FIXED! ({result['rating']})")
            updates_made += 1
            
            # Save
            with open(FILENAME, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        else:
            print(" Still failed.")

        # Very slow delay
        time.sleep(10)

    # Final Sort
    print("\nSorting...")
    def get_rating_sort(r):
        try:
            val = r['Rating']
            return int(val) if val != '-' else 0
        except:
            return 0

    rows.sort(key=lambda x: get_rating_sort(x), reverse=True)
    
    # Re-rank
    rank = 1
    for row in rows:
        r_val = get_rating_sort(row)
        if r_val > 0:
            row['Rank'] = rank
            rank += 1
        else:
            row['Rank'] = "-"

    # Final Save
    with open(FILENAME, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nCompleted. Final Fixes: {updates_made}")
    print(f"Total Successful in File: {len(rows) - (len(failed_indices) - updates_made)}")

if __name__ == "__main__":
    main()
