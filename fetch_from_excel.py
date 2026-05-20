import pandas as pd
import time
import requests
import csv

INPUT_EXCEL = 'CP handles(1-468).xlsx'
OUTPUT_FILE = 'final_sorted_ratings.csv'

def clean_username(u):
    u = str(u).strip()
    # Remove query string if any
    u = u.split('?')[0]
    if 'leetcode.com/u/' in u:
        return u.split('leetcode.com/u/')[-1].strip('/').split('/')[0]
    if 'leetcode.com/' in u:
        return u.split('leetcode.com/')[-1].strip('/').split('/')[0]
    return u

def fetch_data(username):
    rating = 0
    level = "Unrated"
    query = """
    query userContestRankingInfo($username: String!) {
        userContestRanking(username: $username) {
            rating
            badge { name }
        }
    } 
    """
    for attempt in range(3):
        try:
            r = requests.post(
                'https://leetcode.com/graphql',
                json={'query': query, 'variables': {'username': username}},
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Content-Type': 'application/json'},
                timeout=10
            )
            if r.status_code == 200:
                data = r.json()
                ranking = data.get('data', {}).get('userContestRanking')
                if ranking:
                    rating = round(ranking.get('rating', 0), 2)
                    badge = ranking.get('badge')
                    if badge and badge.get('name'):
                        level = badge.get('name')
                    elif rating > 0:
                        level = "Participant"
                return rating, level
            elif r.status_code == 429:
                print(f"  [429 Rate Limit] Sleeping 30s...")
                time.sleep(30)
            else:
                break
        except Exception as e:
            time.sleep(2)
    return rating, level

def main():
    print(f"Reading input excel file: {INPUT_EXCEL}...")
    try:
        df = pd.read_excel(INPUT_EXCEL)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    # Extract required columns (Indices: 4: Name, 6: Roll, 9: Username)
    students = []
    for index, row in df.iterrows():
        try:
            name = str(row.iloc[4]).strip()
            roll = str(row.iloc[6]).strip()
            username_raw = str(row.iloc[9]).strip()
            
            if name.lower() == 'nan' or not name:
                continue
                
            username = clean_username(username_raw)
            if username and username.lower() not in ['nan', 'none', 'null', '', 'na']:
                students.append({
                    'name': name,
                    'roll': roll,
                    'username': username
                })
        except IndexError:
            # Reached end of valid rows or row is too short
            continue

    total = len(students)
    print(f"Total valid students extracted: {total}")

    results = []
    batch_size = 30
    sleep_between = 5

    for i in range(0, total, batch_size):
        batch = students[i:i+batch_size]
        print(f"Batch {i//batch_size + 1}/{total//batch_size + 1}")
        for idx, student in enumerate(batch):
            username = student['username']
            rating, level = fetch_data(username)
            student['rating'] = rating
            student['level'] = level
            results.append(student)
            print(f"  [{i+idx+1}/{total}] {username} -> Rating: {rating}, Level: {level}")
            time.sleep(0.5)
            
        if i + batch_size < total:
            time.sleep(sleep_between)

    print("\nSorting results by rating descending...")
    sorted_results = sorted(results, key=lambda x: x.get('rating', 0), reverse=True)
    
    print(f"Saving sorted output to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Student Name', 'Student Roll Number', 'LeetCode Username', 'LeetCode Ratings', 'LeetCode Level'])
        for s in sorted_results:
            writer.writerow([s['name'], s['roll'], s['username'], s['rating'], s['level']])
            
    print("Process complete!")

if __name__ == "__main__":
    main()
