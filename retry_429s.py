import csv
import requests
import time
import random

FILENAME = 'new_batch_ratings.csv'
API_BASE_URL = "https://alfa-leetcode-api.onrender.com"

# List of user agents to rotate (helps avoid 429)
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
]

def get_rating(username):
    headers = {
        'User-Agent': random.choice(USER_AGENTS)
    }
    try:
        response = requests.get(f"{API_BASE_URL}/{username}/contest", headers=headers, timeout=20)
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
            print(f"  Still 429 on {username}. Waiting 45s...")
            time.sleep(45)
            return None 
    except Exception as e:
        print(f"  Error fetching {username}: {e}")
    
    return None

def main():
    print("="*60)
    print("RETRYING 429s - EXTREME CAUTION MODE")
    print("="*60)
    
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

    if not failed_indices:
        print("No failed students found to retry.")
        return

    print(f"Targeting {len(failed_indices)} students.")
    print("Step 1: 120s Cooldown to reset API limits...")
    for i in range(120, 0, -10):
        print(f"  {i}s remaining...", end='\r', flush=True)
        time.sleep(10)
    print("\nStarting now (20s delay between requests).")

    updates_made = 0
    
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
            
            # Save immediately
            with open(FILENAME, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        else:
            print(" Failed.")

        # Long delay
        time.sleep(20)

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

    print(f"\nretry_429s Completed. Repaired: {updates_made}")

if __name__ == "__main__":
    main()
