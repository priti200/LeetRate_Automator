import csv

INPUT_FILE = 'final_complete_results.csv'
OUTPUT_FILE = 'final_sorted_ratings.csv'

def main():
    print(f"Reading cached data from {INPUT_FILE}...")
    students = []
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        # Header: Student Name,Student Roll Number,Student LeetCode Username,Fetched LeetCode Rating,Fetched LeetCode Global Rank,Fetched LeetCode Level
        for row in reader:
            if len(row) >= 6:
                name = row[0].strip()
                roll = row[1].strip()
                username = row[2].strip()
                
                # Parse rating correctly
                rating_str = row[3].strip()
                try:
                    rating = float(rating_str)
                except ValueError:
                    rating = 0.0
                    
                level = row[5].strip()
                
                students.append({
                    'name': name,
                    'roll': roll,
                    'username': username,
                    'rating': rating,
                    'level': level
                })

    print(f"Total students loaded: {len(students)}")
    
    # Sort by rating (descending)
    sorted_students = sorted(students, key=lambda x: x['rating'], reverse=True)
    
    print(f"Saving sorted output to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Student Name', 'Student Roll Number', 'LeetCode Username', 'LeetCode Ratings', 'LeetCode Level'])
        for s in sorted_students:
            writer.writerow([s['name'], s['roll'], s['username'], s['rating'], s['level']])
            
    print("Done! The beautifully sorted file is ready.")

if __name__ == "__main__":
    main()
