import json
import csv

# Load the latest successful data from history
with open('history.json', 'r') as f:
    history = json.load(f)

# Get the most recent entry with successful data
latest_data = None
for entry in reversed(history):
    successful = [s for s in entry['data'] if s.get('success', False) and s.get('rating', 0) > 0]
    if successful:
        latest_data = entry['data']
        print(f"Found entry from {entry['timestamp']} with {len(successful)} successful students")
        break

if latest_data:
    # Sort by rating (highest first)
    latest_data.sort(key=lambda x: (x.get('success', False), x.get('rating', 0)), reverse=True)
    
    # Generate CSV
    with open('leetcode_ratings_output.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Rank", "Name", "Roll Number", "Username", "Rating", "Global Rank", "Contests Attended", "Top Percentage", "Status"])
        
        rank = 1
        for student in latest_data:
            status = "Success" if student.get('success', False) else "Failed"
            writer.writerow([
                rank if student.get('success', False) else "-",
                student.get('name', ''),
                student.get('roll_number', ''),
                student['username'],
                student['rating'],
                student['global_rank'],
                student['attended'],
                f"{student['top_percentage']}%",
                status
            ])
            if student.get('success', False):
                rank += 1
    
    print("[SUCCESS] Created leetcode_ratings_output.csv with all student data!")
    print(f"Total students: {len(latest_data)}")
    successful_count = len([s for s in latest_data if s.get('success', False)])
    print(f"Successful ratings: {successful_count}")
else:
    print("No successful data found in history!")
