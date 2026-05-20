"""
Rate-limited API caller to get all student ratings.
This version adds delays between requests to avoid rate limiting.
"""
import time
import json
import csv
import requests
from typing import Dict, Any

API_BASE_URL = "https://alfa-leetcode-api.onrender.com"
MAX_RETRIES = 3

# Load student data
with open('Leetcode-handles.csv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

students = []
for idx, line in enumerate(lines[1:], 1):  # Skip header
    parts = line.strip().split(',')
    if len(parts) >= 10:
        name = parts[4].strip().strip('"')
        roll_number = parts[6].strip().strip('"')
        username = parts[-1].strip().strip('"')
        
        # Handle URLs
        if username.startswith('http') and '/u/' in username:
            username = username.split('/u/')[-1].strip('/').strip()
        
        if username:
            students.append({
                'name': name,
                'roll_number': roll_number,
                'username': username
            })

print(f"Processing {len(students)} students with rate limiting...")
print("This will take approximately {:.1f} minutes".format(len(students) * 3 / 60))

results = []
session = requests.Session()

for i, student in enumerate(students, 1):
    username = student['username']
    print(f"[{i}/{len(students)}] Fetching {username}...", end=' ')
    
    success = False
    for attempt in range(MAX_RETRIES):
        try:
            url = f"{API_BASE_URL}/{username}/contest"
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results.append({
                    'name': student['name'],
                    'roll_number': student['roll_number'],
                    'username': username,
                    'rating': int(data.get('contestRating', 0)),
                    'global_rank': int(data.get('contestGlobalRanking', 0)),
                    'attended': int(data.get('contestAttend', 0)),
                    'top_percentage': float(data.get('contestTopPercentage', 0.0)),
                    'success': True
                })
                print(f"✓ Rating: {data.get('contestRating', 0)}")
                success = True
                break
            elif response.status_code == 429:
                wait_time = 5 * (attempt + 1)
                print(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
            elif response.status_code == 404:
                results.append({
                    'name': student['name'],
                    'roll_number': student['roll_number'],
                    'username': username,
                    'rating': 0,
                    'global_rank': 0,
                    'attended': 0,
                    'top_percentage': 0.0,
                    'success': False,
                    'error': 'Not Found'
                })
                print("✗ Not found")
                success = True
                break
        except Exception as e:
            print(f"Error: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(2)
    
    if not success:
        results.append({
            'name': student['name'],
            'roll_number': student['roll_number'],
            'username': username,
            'rating': 0,
            'global_rank': 0,
            'attended': 0,
            'top_percentage': 0.0,
            'success': False,
            'error': 'Failed'
        })
        print("✗ Failed after retries")
    
    # Rate limiting: wait 3 seconds between requests
    if i < len(students):
        time.sleep(3)

# Sort by rating
results.sort(key=lambda x: (x.get('success', False), x.get('rating', 0)), reverse=True)

# Save to CSV
with open('complete_ratings.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["Rank", "Name", "Roll Number", "Username", "Rating", "Global Rank", "Contests Attended", "Top Percentage", "Status"])
    
    rank = 1
    for student in results:
        status = "Success" if student.get('success', False) else f"Failed - {student.get('error', 'Unknown')}"
        writer.writerow([
            rank if student.get('success', False) and student.get('rating', 0) > 0 else "-",
            student['name'],
            student['roll_number'],
            student['username'],
            student['rating'],
            student['global_rank'],
            student['attended'],
            f"{student['top_percentage']}%",
            status
        ])
        if student.get('success', False) and student.get('rating', 0) > 0:
            rank += 1

successful = len([r for r in results if r.get('success', False) and r.get('rating', 0) > 0])
print(f"\n{'='*60}")
print(f"Complete! Saved to complete_ratings.csv")
print(f"Successful: {successful}/{len(results)}")
print(f"{'='*60}")
