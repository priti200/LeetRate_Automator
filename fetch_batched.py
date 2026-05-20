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

# Divide into 3 batches
batch_size = len(students) // 3
batches = [
    students[0:batch_size],
    students[batch_size:batch_size*2],
    students[batch_size*2:]
]

print(f"Total students: {len(students)}")
print(f"Batch 1: {len(batches[0])} students")
print(f"Batch 2: {len(batches[1])} students")
print(f"Batch 3: {len(batches[2])} students")
print(f"\nThis will take approximately {len(students) * 3 / 60:.1f} minutes total")
print(f"With 10-minute breaks between batches\n")

all_results = []
session = requests.Session()

for batch_num, batch in enumerate(batches, 1):
    print(f"{'='*60}")
    print(f"BATCH {batch_num}/{len(batches)} - {len(batch)} students")
    print(f"{'='*60}")
    
    for i, s in enumerate(batch, 1):
        global_idx = (batch_num - 1) * batch_size + i
        print(f"[{global_idx}/{len(students)}] {s['username']}... ", end='', flush=True)
        
        try:
            r = session.get(f"{API_BASE_URL}/{s['username']}/contest", timeout=10)
            if r.status_code == 200:
                d = r.json()
                all_results.append({
                    **s, 
                    'rating': int(d.get('contestRating', 0)), 
                    'global_rank': int(d.get('contestGlobalRanking', 0)), 
                    'attended': int(d.get('contestAttend', 0)), 
                    'top_percentage': float(d.get('contestTopPercentage', 0.0)), 
                    'success': True
                })
                print(f"OK ({d.get('contestRating', 0)})")
            else:
                all_results.append({**s, 'rating': 0, 'global_rank': 0, 'attended': 0, 'top_percentage': 0.0, 'success': False})
                print(f"Failed ({r.status_code})")
        except Exception as e:
            all_results.append({**s, 'rating': 0, 'global_rank': 0, 'attended': 0, 'top_percentage': 0.0, 'success': False})
            print(f"Error")
        
        time.sleep(3)
    
    # Wait between batches (except after last batch)
    if batch_num < len(batches):
        print(f"\n>>> Waiting 10 minutes before batch {batch_num + 1}...")
        print(f">>> This lets the API rate limit reset")
        for remaining in range(600, 0, -30):
            mins, secs = divmod(remaining, 60)
            print(f">>> Time remaining: {mins}:{secs:02d}", end='\r', flush=True)
            time.sleep(30)
        print(f">>> Resuming...                        \n")

# Sort by rating
all_results.sort(key=lambda x: (x.get('success', False), x.get('rating', 0)), reverse=True)

# Save to CSV
with open('all_students_ratings.csv', 'w', newline='', encoding='utf-8') as f:
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

successful = len([r for r in all_results if r.get('rating', 0) > 0])
print(f"\n{'='*60}")
print(f"COMPLETE!")
print(f"Successful: {successful}/{len(all_results)} students with ratings")
print(f"Failed: {len(all_results) - successful}")
print(f"Saved to: all_students_ratings.csv")
print(f"{'='*60}")
