import csv
import time
import requests

INPUT_FILE = 'students_input.csv'
OUTPUT_FILE = 'final_output.csv'

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
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Content-Type': 'application/json'},
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
    print("Reading input file...")
    students = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) >= 3:
                name = row[0].strip()
                roll = row[1].strip()
                username = row[2].strip()
                if username and username.lower() not in ['nan', 'none', 'null', '']:
                    students.append({'name': name, 'roll': roll, 'username': username})

    total = len(students)
    print(f"Total students: {total}")

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

    sorted_results = sorted(results, key=lambda x: x.get('rating', 0), reverse=True)
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Student Name', 'Student Roll Number', 'LeetCode Username', 'LeetCode Ratings', 'LeetCode Level'])
        for s in sorted_results:
            writer.writerow([s['name'], s['roll'], s['username'], s['rating'], s['level']])
    print("Done!")

if __name__ == "__main__":
    main()
