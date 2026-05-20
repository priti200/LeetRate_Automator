"""
LeetCode Rating Tracker - Automated Weekly Scheduler
Runs continuously and automatically fetches ratings every week.
"""
import schedule
import time
import os
import csv
import datetime
from leetcode_tracker import process_usernames
import sys

# Configuration
CSV_FILE = "Leetcode-handles.csv"
LOG_FILE = "scheduler.log"
SCHEDULE_DAY = "monday"  # Change this to your preferred day
SCHEDULE_TIME = "10:00"  # Change this to your preferred time (24-hour format)

def log_message(message):
    """Log message to file and console."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')

def parse_csv_file():
    """Parse the CSV file to extract usernames and metadata."""
    usernames = []
    student_metadata = {}
    
    if not os.path.exists(CSV_FILE):
        log_message(f"ERROR: CSV file '{CSV_FILE}' not found!")
        return usernames, student_metadata
    
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            content = f.readlines()
            
        for idx, line in enumerate(content):
            # Skip header row
            if idx == 0:
                continue
                
            clean_line = line.strip()
            if clean_line and not clean_line.startswith('#'):
                parts = clean_line.split(',')
                
                if len(parts) >= 10:
                    name = parts[4].strip().strip('"') if len(parts) > 4 else ""
                    roll_number = parts[6].strip().strip('"') if len(parts) > 6 else ""
                    username = parts[-1].strip().strip('"')
                    
                    # Handle URLs
                    if username.startswith('http'):
                        if '/u/' in username:
                            username = username.split('/u/')[-1].strip('/').strip()
                    
                    if username:
                        usernames.append(username)
                        student_metadata[username] = {
                            'name': name,
                            'roll_number': roll_number
                        }
        
        log_message(f"Successfully parsed {len(usernames)} students from CSV file")
    except Exception as e:
        log_message(f"ERROR: Failed to parse CSV file: {e}")
    
    return usernames, student_metadata

def run_tracker():
    """Main function to run the tracker automatically."""
    log_message("="*60)
    log_message("Starting scheduled LeetCode rating update")
    log_message("="*60)
    
    try:
        usernames, student_metadata = parse_csv_file()
        
        if not usernames:
            log_message("No usernames to process. Exiting.")
            return
        
        # Run the tracker
        results, stats = process_usernames(usernames, student_metadata)
        
        log_message(f"Update completed successfully!")
        log_message(f"Total students: {stats.get('total', 0)}")
        log_message(f"Successful: {stats.get('successful', 0)}")
        log_message(f"Average rating: {stats.get('avg', 0):.1f}")
        log_message(f"Top rating: {stats.get('max', 0)}")
        log_message("Data saved to leetcode_data.csv and history.json")
        
    except Exception as e:
        log_message(f"ERROR: Tracker execution failed: {e}")
        import traceback
        log_message(traceback.format_exc())
    
    log_message("="*60)

def main():
    """Main scheduler loop."""
    log_message("LeetCode Tracker Scheduler Started")
    log_message(f"Scheduled to run every {SCHEDULE_DAY.capitalize()} at {SCHEDULE_TIME}")
    log_message("Press Ctrl+C to stop")
    log_message("")
    
    # Schedule the job
    if SCHEDULE_DAY.lower() == "monday":
        schedule.every().monday.at(SCHEDULE_TIME).do(run_tracker)
    elif SCHEDULE_DAY.lower() == "tuesday":
        schedule.every().tuesday.at(SCHEDULE_TIME).do(run_tracker)
    elif SCHEDULE_DAY.lower() == "wednesday":
        schedule.every().wednesday.at(SCHEDULE_TIME).do(run_tracker)
    elif SCHEDULE_DAY.lower() == "thursday":
        schedule.every().thursday.at(SCHEDULE_TIME).do(run_tracker)
    elif SCHEDULE_DAY.lower() == "friday":
        schedule.every().friday.at(SCHEDULE_TIME).do(run_tracker)
    elif SCHEDULE_DAY.lower() == "saturday":
        schedule.every().saturday.at(SCHEDULE_TIME).do(run_tracker)
    elif SCHEDULE_DAY.lower() == "sunday":
        schedule.every().sunday.at(SCHEDULE_TIME).do(run_tracker)
    else:
        log_message(f"ERROR: Invalid day '{SCHEDULE_DAY}'. Using Monday as default.")
        schedule.every().monday.at(SCHEDULE_TIME).do(run_tracker)
    
    # Optional: Run immediately on startup for testing
    if len(sys.argv) > 1 and sys.argv[1] == "--run-now":
        log_message("Running tracker immediately (--run-now flag detected)")
        run_tracker()
    
    # Keep the scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        log_message("Scheduler stopped by user")

if __name__ == "__main__":
    main()
