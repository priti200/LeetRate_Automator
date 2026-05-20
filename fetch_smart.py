import time
import csv
import requests

API_BASE_URL = "https://alfa-leetcode-api.onrender.com"

print("Smart Fetcher - Only fetches missing data")
print("="*60)

# Step 1: Load existing successful data from complete_ratings.csv
successful_cache = {}
try:
    with open('complete_ratings.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Status'] == 'Success' and int(row['Rating']) > 0:
                successful_cache[row['Username']] = {
                    'name': row['Name'],
                    'roll_number': row['Roll Number'],
                    'username': row['Username'],
                    'rating': int(row['Rating']),
                    'global_rank': int(row['Global Rank']),
                    'attended': int(row['Contests']),
                    'top_percentage': float(row['Top %'].rstrip('%')),
                    'success': True
                }
    print(f"Loaded {len(successful_cache)} students from cache with valid ratings")
except:
    print("No cache found, will fetch all students")

# Step 2: Load all students from CSV
with open('Leetcode-handles.csv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

all_students = []
for line in lines[1:]:
    parts = line.strip().split(',')
    if len(parts) >= 10:
        name = parts[4].strip().strip('"')
        roll = parts[6].strip().strip('"')
        user = parts[-1].strip().strip('"')
        if user.startswith('http') and '/u/' in user:
            user = user.split('/u/')[-1].strip('/').strip()
        if user:
            all_students.append({'name': name, 'roll_number': roll, 'username': user})

# Step 3: Identify students who need fetching
students_to_fetch = []
for s in all_students:
    if s['username'] not in successful_cache:
        students_to_fetch.append(s)

print(f"Total students: {len(all_students)}")
print(f"Already have ratings: {len(successful_cache)}")
print(f"Need to fetch: {len(students_to_fetch)}")
print(f"Estimated time: {len(students_to_fetch) * 3 / 60:.1f} minutes")
print()

if len(students_to_fetch) == 0:
    print("All students already have ratings!")
    exit(0)

# Step 4: Fetch missing data
session = requests.Session()
newly_fetched = []

for i, s in enumerate(students_to_fetch, 1):
    print(f"[{i}/{len(students_to_fetch)}] {s['username']}... ", end='', flush=True)
    
    try:
        r = session.get(f"{API_BASE_URL}/{s['username']}/contest", timeout=10)
        if r.status_code == 200:
            d = r.json()
            newly_fetched.append({
                **s,
                'rating': int(d.get('contestRating', 0)),
                'global_rank': int(d.get('contestGlobalRanking', 0)),
                'attended': int(d.get('contestAttend', 0)),
                'top_percentage': float(d.get('contestTopPercentage', 0.0)),
                'success': True
            })
            print(f"OK ({d.get('contestRating', 0)})")
        else:
            newly_fetched.append({**s, 'rating': 0, 'global_rank': 0, 'attended': 0, 'top_percentage': 0.0, 'success': False})
            print(f"Failed ({r.status_code})")
    except Exception as e:
        newly_fetched.append({**s, 'rating': 0, 'global_rank': 0, 'attended': 0, 'top_percentage': 0.0, 'success': False})
        print("Error")
    
    time.sleep(3)

# Step 5: Merge cached + newly fetched data
all_results = list(successful_cache.values()) + newly_fetched
all_results.sort(key=lambda x: (x.get('success', False), x.get('rating', 0)), reverse=True)

# Step 6: Save complete results
with open('final_complete_ratings.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(["Rank", "Name", "Roll Number", "Username", "Rating", "Global Rank", "Contests", "Top %", "Status"])
    rank = 1
    for r in all_results:
        w.writerow([
            rank if r.get('rating', 0) > 0 else "-",
            r['name'],
            r['roll_number'],
            r['username'],
            r['rating'],
            r['global_rank'],
            r['attended'],
            f"{r['top_percentage']}%",
            "Success" if r.get('success') else "Failed"
        ])
        if r.get('rating', 0) > 0:
            rank += 1

cached_with_ratings = len([r for r in successful_cache.values() if r.get('rating', 0) > 0])
newly_successful = len([r for r in newly_fetched if r.get('rating', 0) > 0])
total_with_ratings = len([r for r in all_results if r.get('rating', 0) > 0])

print(f"\n{'='*60}")
print(f"COMPLETE!")
print(f"From cache: {cached_with_ratings} students")
print(f"Newly fetched: {newly_successful}/{len(students_to_fetch)} students")
print(f"Total with ratings: {total_with_ratings}/{len(all_results)}")
print(f"Saved to: final_complete_ratings.csv")
print(f"{'='*60}")
