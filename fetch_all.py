import time
import json
import csv
import requests

API_BASE_URL = "https://alfa-leetcode-api.onrender.com"

# Load students
with open('Leetcode-handles.csv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

students = []
for line in lines[1:]:
    parts = line.strip().split(',')
    if len(parts) >= 10:
        name = parts[4].strip().strip('"')
        roll = parts[6].strip().strip('"')
        user = parts[-1].strip().strip('"')
        if user.startswith('http') and '/u/' in user:
            user = user.split('/u/')[-1].strip('/').strip()
        if user:
            students.append({'name': name, 'roll_number': roll, 'username': user})

print(f"Fetching ratings for {len(students)} students...")
print(f"Estimated time: {len(students) * 3 / 60:.1f} minutes")
print()

results = []
session = requests.Session()

for i, s in enumerate(students, 1):
    print(f"[{i}/{len(students)}] {s['username']}... ", end='', flush=True)
    
    try:
        r = session.get(f"{API_BASE_URL}/{s['username']}/contest", timeout=10)
        if r.status_code == 200:
            d = r.json()
            results.append({**s, 'rating': int(d.get('contestRating', 0)), 'global_rank': int(d.get('contestGlobalRanking', 0)), 
                          'attended': int(d.get('contestAttend', 0)), 'top_percentage': float(d.get('contestTopPercentage', 0.0)), 'success': True})
            print(f"OK ({d.get('contestRating', 0)})")
        else:
            results.append({**s, 'rating': 0, 'global_rank': 0, 'attended': 0, 'top_percentage': 0.0, 'success': False})
            print(f"Failed ({r.status_code})")
    except:
        results.append({**s, 'rating': 0, 'global_rank': 0, 'attended': 0, 'top_percentage': 0.0, 'success': False})
        print("Error")
    
    time.sleep(3)

results.sort(key=lambda x: (x.get('success', False), x.get('rating', 0)), reverse=True)

with open('complete_ratings.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(["Rank", "Name", "Roll Number", "Username", "Rating", "Global Rank", "Contests", "Top %", "Status"])
    rank = 1
    for r in results:
        w.writerow([rank if r.get('rating', 0) > 0 else "-", r['name'], r['roll_number'], r['username'],
                   r['rating'], r['global_rank'], r['attended'], f"{r['top_percentage']}%",
                   "Success" if r.get('success') else "Failed"])
        if r.get('rating', 0) > 0:
            rank += 1

print(f"\nDone! {len([r for r in results if r.get('rating',0)>0])}/{len(results)} students with ratings")
print("Saved to: complete_ratings.csv")
