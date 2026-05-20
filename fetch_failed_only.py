import csv
import requests
import time
import shutil

FILENAME = 'final_ratings_no_status.csv'
API_BASE_URL = "https://alfa-leetcode-api.onrender.com"

def get_rating(username):
    try:
        response = requests.get(f"{API_BASE_URL}/{username}/contest", timeout=15)
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
            print(f"  Rate limited on {username} (429). Waiting 30s...")
            time.sleep(30)
            return None # Signal to retry later if we wanted, or just fail for now
    except Exception as e:
        print(f"  Error fetching {username}: {e}")
    
    return None

def main():
    print("Reading existing data...")
    rows = []
    with open(FILENAME, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    failed_students = []
    for i, row in enumerate(rows):
        # Check if rating is 0 or '-' (some formats might vary)
        try:
            rating = int(row['Rating']) if row['Rating'] != '-' else 0
        except ValueError:
            rating = 0
            
        if rating == 0:
            failed_students.append(i)

    print(f"Found {len(failed_students)} students with missing ratings.")
    print(f"Starting repair process (5s delay between requests)...")
    
    updates_made = 0
    
    # Process failed students
    for count, idx in enumerate(failed_students, 1):
        row = rows[idx]
        username = row['Username']
        print(f"[{count}/{len(failed_students)}] Retrying {username}...", end='', flush=True)
        
        result = get_rating(username)
        
        if result and result['success'] and result['rating'] > 0:
            # Update row data
            rows[idx]['Rating'] = result['rating']
            rows[idx]['Global Rank'] = result['global_rank']
            rows[idx]['Contests'] = result['attended']
            rows[idx]['Top %'] = f"{result['top_percentage']}%"
            # Update rank if appropriate (logic is tricky with mixed data, but we just fill values)
            rows[idx]['Rank'] = "-" # Will need resorting later or just leave as is
            
            print(f" FIXED! ({result['rating']})")
            updates_made += 1
            
            # Save progress every time to be safe
            with open(FILENAME, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
                
        else:
            print(" Still failed.")

        time.sleep(5) # Slow and steady

    # Final Sort to fix ranks
    print("\nSorting and re-ranking...")
    # Helper to parse rating safely
    def get_rating_sort(r):
        try:
            val = r['Rating']
            return int(val) if val != '-' else 0
        except:
            return 0

    rows.sort(key=lambda x: get_rating_sort(x), reverse=True)
    
    # Re-assign ranks
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

    print(f"\nDone! Repaired {updates_made} records.")
    print(f"Total successful now: {len(rows) - (len(failed_students) - updates_made)}")

if __name__ == "__main__":
    main()
