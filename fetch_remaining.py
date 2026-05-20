import time
import csv
import requests

API_BASE_URL = "https://alfa-leetcode-api.onrender.com"

print("Fetching remaining students with 0 ratings")
print("="*60)

# Load students who currently have 0 ratings
students_with_zero = []
try:
    with open('final_complete_ratings.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row['Rating']) == 0:
                students_with_zero.append({
                    'name': row['Name'],
                    'roll_number': row['Roll Number'],
                    'username': row['Username']
                })
    print(f"Found {len(students_with_zero)} students with 0 ratings to check")
except Exception as e:
    print(f"Error: {e}")
    exit(1)

if len(students_with_zero) == 0:
    print("All students already have ratings!")
    exit(0)

print(f"Estimated time: {len(students_with_zero) * 3 / 60:.1f} minutes\n")

# Fetch data for these students
session = requests.Session()
updated_students = []

for i, s in enumerate(students_with_zero, 1):
    print(f"[{i}/{len(students_with_zero)}] {s['username']}... ", end='', flush=True)
    
    try:
        r = session.get(f"{API_BASE_URL}/{s['username']}/contest", timeout=10)
        if r.status_code == 200:
            d = r.json()
            rating = int(d.get('contestRating', 0))
            updated_students.append({
                **s,
                'rating': rating,
                'global_rank': int(d.get('contestGlobalRanking', 0)),
                'attended': int(d.get('contestAttend', 0)),
                'top_percentage': float(d.get('contestTopPercentage', 0.0)),
                'success': True
            })
            if rating > 0:
                print(f"FOUND! Rating: {rating}")
            else:
                print("Still 0 (no contests)")
        else:
            updated_students.append({**s, 'rating': 0, 'global_rank': 0, 'attended': 0, 'top_percentage': 0.0, 'success': False})
            print(f"Failed ({r.status_code})")
    except Exception as e:
        updated_students.append({**s, 'rating': 0, 'global_rank': 0, 'attended': 0, 'top_percentage': 0.0, 'success': False})
        print("Error")
    
    time.sleep(3)

# Load all existing data and merge
all_students = {}
with open('final_complete_ratings.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        all_students[row['Username']] = {
            'name': row['Name'],
            'roll_number': row['Roll Number'],
            'username': row['Username'],
            'rating': int(row['Rating']),
            'global_rank': int(row['Global Rank']),
            'attended': int(row['Contests']),
            'top_percentage': float(row['Top %'].rstrip('%')),
            'success': row['Status'] == 'Success'
        }

# Update with new data
for student in updated_students:
    all_students[student['username']] = student

# Sort and save
all_results = list(all_students.values())
all_results.sort(key=lambda x: (x.get('success', False), x.get('rating', 0)), reverse=True)

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

newly_found = len([s for s in updated_students if s.get('rating', 0) > 0])
total_with_ratings = len([r for r in all_results if r.get('rating', 0) > 0])
still_zero = len([r for r in all_results if r.get('rating', 0) == 0])

print(f"\n{'='*60}")
print(f"COMPLETE!")
print(f"Newly found with ratings: {newly_found}/{len(students_with_zero)}")
print(f"Total students with ratings: {total_with_ratings}/132")
print(f"Students with 0 ratings: {still_zero}")
print(f"Updated: final_complete_ratings.csv")
print(f"{'='*60}")
