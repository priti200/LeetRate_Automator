import csv
import requests
import time

FILENAME = 'new_batch_ratings.csv'
API_BASE_URL = "https://alfa-leetcode-api.onrender.com"

def check_status(username):
    try:
        # Check contest endpoint
        response = requests.get(f"{API_BASE_URL}/{username}/contest", timeout=10)
        return response.status_code
    except Exception as e:
        return "Error"

def main():
    print("Reading new_batch_ratings.csv...")
    rows = []
    try:
        with open(FILENAME, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print("File not found")
        return

    failed_students = []
    for i, row in enumerate(rows):
        try:
            rating = int(row['Rating']) if row.get('Rating') and row['Rating'] != '-' else 0
        except ValueError:
            rating = 0
            
        if rating == 0:
            failed_students.append(row)

    print(f"Diagnosing {len(failed_students)} failed students...")
    print(f"{'Username':<30} | {'Status':<10} | {'Diagnosis'}")
    print("-" * 60)

    count_404 = 0
    count_429 = 0
    count_other = 0

    for i, s in enumerate(failed_students):
        username = s['Username']
        status = check_status(username)
        
        diagnosis = ""
        if status == 200:
            diagnosis = "Actually Valid? (Retry needed)"
        elif status == 404:
            diagnosis = "INVALID USERNAME"
            count_404 += 1
        elif status == 429:
            diagnosis = "Rate Limited"
            count_429 += 1
        else:
            diagnosis = "Other Error"
            count_other += 1
            
        print(f"{username:<30} | {str(status):<10} | {diagnosis}")
        
        # Small delay to be polite
        time.sleep(1)

    print("-" * 60)
    print("SUMMARY")
    print(f"Invalid Usernames (404): {count_404}")
    print(f"Rate Limited (429):      {count_429}")
    print(f"Other Errors:            {count_other}")

if __name__ == "__main__":
    main()
