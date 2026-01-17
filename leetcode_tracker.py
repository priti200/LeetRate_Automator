from flask import Flask, render_template, request
import requests
import concurrent.futures
import time
import json
import csv
import os
import datetime
from typing import List, Dict, Any

app = Flask(__name__)

# --- Configuration ---
API_BASE_URL = "https://alfa-leetcode-api.onrender.com"
STUDENTS_FILE = "students.txt"
DATA_FILE = "history.json"
CSV_EXPORT_FILE = "leetcode_data.csv"
MAX_RETRIES = 2

def load_students_from_file(filepath: str) -> List[str]:
    students = []
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    students.append(line)
    return students

# Create a session for connection pooling (reuses connections)
session = requests.Session()

def fetch_student_data(username: str, name: str = "", roll_number: str = "") -> Dict[str, Any]:
    """Fetch student contest data from LeetCode API, including metadata."""
    url = f"{API_BASE_URL}/{username}/contest"
    for attempt in range(MAX_RETRIES):
        try:
            response = session.get(url, timeout=8)
            if response.status_code == 200:
                data = response.json()
                return {
                    "username": username,
                    "name": name,
                    "roll_number": roll_number,
                    "rating": int(data.get("contestRating", 0)),
                    "global_rank": int(data.get("contestGlobalRanking", 0)),
                    "attended": int(data.get("contestAttend", 0)),
                    "top_percentage": float(data.get("contestTopPercentage", 0.0)),
                    "success": True
                }
            elif response.status_code == 404:
                return {"username": username, "name": name, "roll_number": roll_number, "success": False, "error": "Not Found", "rating": 0, "global_rank": 0, "attended": 0, "top_percentage": 0.0}
            elif response.status_code == 429:
                # Rate limited - shorter wait time
                wait_time = 1 * (attempt + 1)  # 1s, 2s
                time.sleep(wait_time)
                continue
        except requests.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(0.5)
    return {"username": username, "name": name, "roll_number": roll_number, "success": False, "error": "Failed", "rating": 0, "global_rank": 0, "attended": 0, "top_percentage": 0.0}

def save_history(data: List[Dict]):
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "data": data
    }
    history = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                history = json.load(f)
        except json.JSONDecodeError:
            pass
    history.append(entry)
    with open(DATA_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def generate_csv(data: List[Dict]):
    """Generate CSV export with student metadata."""
    with open(CSV_EXPORT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Rank", "Name", "Roll Number", "Username", "Rating", "Global Rank", "Contests Attended", "Top Percentage"])
        for i, student in enumerate(data, 1):
            writer.writerow([
                i,
                student.get('name', ''),
                student.get('roll_number', ''),
                student['username'],
                student['rating'],
                student['global_rank'],
                student['attended'],
                f"{student['top_percentage']}%"
            ])


def process_usernames(usernames: List[str], student_metadata: Dict[str, Dict] = None) -> Dict[str, Any]:
    """Process usernames and fetch their LeetCode data with optional metadata."""
    results = []
    total_users = len(usernames)
    start_time = time.time()
    student_metadata = student_metadata or {}
    print(f"\n{'='*60}")
    print(f"Processing {total_users} usernames...")
    print(f"{'='*60}")
    
    # Use ThreadPoolExecutor for parallel fetching
    # Optimized to 6 workers for better speed while managing rate limits
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        future_to_user = {}
        for user in usernames:
            metadata = student_metadata.get(user, {})
            name = metadata.get('name', '')
            roll_number = metadata.get('roll_number', '')
            future_to_user[executor.submit(fetch_student_data, user, name, roll_number)] = user
            
        completed = 0
        successful = 0
        for future in concurrent.futures.as_completed(future_to_user):
            completed += 1
            try:
                data = future.result()
                results.append(data)
                if data.get('success', False):
                    successful += 1
                
                # Progress every 5 users
                if completed % 5 == 0 or completed == total_users:
                    elapsed = time.time() - start_time
                    rate = completed / elapsed if elapsed > 0 else 0
                    eta = (total_users - completed) / rate if rate > 0 else 0
                    print(f"  [{completed}/{total_users}] {successful} successful | {rate:.1f}/s | ETA: {eta:.0f}s")
            except Exception as e:
                print(f"  Error: {e}")
    
    elapsed_total = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"[DONE] Completed in {elapsed_total:.1f}s ({total_users/elapsed_total:.1f} users/sec)")
    print(f"{'='*60}\n")
    
    # Sort by rating, successful first
    results.sort(key=lambda x: (x.get('success', False), x.get('rating', 0)), reverse=True)
    
    stats = {}
    if results:
        save_history(results)
        generate_csv(results)
        successful_results = [r for r in results if r.get('success', False)]
        if successful_results:
            ratings = [r['rating'] for r in successful_results]
            stats = {
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total": len(results),
                "successful": len(successful_results),
                "avg": sum(ratings) / len(ratings) if ratings else 0,
                "max": max(ratings) if ratings else 0
            }
        else:
            stats = {
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total": len(results),
                "successful": 0,
                "avg": 0,
                "max": 0
            }
    return results, stats

@app.route('/', methods=['GET'])
def index():
    default_users = load_students_from_file(STUDENTS_FILE)
    if default_users:
        return render_template('index.html', current_input=", ".join(default_users))
    return render_template('index.html')

@app.route('/track', methods=['POST'])
def track():
    user_input = request.form.get('usernames', '').strip()
    if not user_input:
        return render_template('index.html', error="Please enter usernames.")
    
    usernames = [u.strip() for u in user_input.split(',') if u.strip()]
    results, stats = process_usernames(usernames)
    
    return render_template('index.html', students=results, stats=stats, current_input=user_input)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload with student metadata extraction."""
    if 'file' not in request.files:
        return render_template('index.html', error="No file part")
    
    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', error="No selected file")

    if file:
        usernames = []
        student_metadata = {}  # Store name and roll number by username
        try:
            content = file.read().decode('utf-8').splitlines()
            for idx, line in enumerate(content):
                # Skip header row (first line)
                if idx == 0:
                    continue
                    
                clean_line = line.strip()
                if clean_line and not clean_line.startswith('#'):
                    parts = clean_line.split(',')
                    # Extract data from CSV columns
                    # Column 5: Name, Column 7: Roll number, Column 10: LeetCode handle
                    if len(parts) >= 10:
                        name = parts[4].strip().strip('"') if len(parts) > 4 else ""
                        roll_number = parts[6].strip().strip('"') if len(parts) > 6 else ""
                        username = parts[-1].strip().strip('"')
                        
                        # Handle cases where people put full URLs like https://leetcode.com/u/username/
                        if username.startswith('http'):
                            # Extract username from URL
                            if '/u/' in username:
                                username = username.split('/u/')[-1].strip('/').strip()
                        
                        # Only add if not empty
                        if username:
                            usernames.append(username)
                            student_metadata[username] = {
                                'name': name,
                                'roll_number': roll_number
                            }
        except Exception as e:
            return render_template('index.html', error=f"Error reading file: {e}")

        results, stats = process_usernames(usernames, student_metadata)
        
        return render_template('index.html', students=results, stats=stats, current_input=f"File: {file.filename}")


if __name__ == "__main__":
    print("Starting LeetCode Tracker Web Interface...")
    port = int(os.environ.get("PORT", 5000))
    print(f"Running on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
