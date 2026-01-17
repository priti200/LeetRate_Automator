# LeetCode Contest Tracker

Automated system to track and visualize LeetCode contest ratings for a group of students.

## Features
- 📊 **Automated Tracking**: Fetches contest ratings, global ranks, and participation stats.
- 👤 **Student Metadata**: Tracks student names and roll numbers from CSV file.
- 📈 **Beautiful Dashboard**: Generates a responsive HTML leaderboard with dark mode.
- 💾 **Data Export**: Exports data to CSV for Excel analysis.
- 🕒 **History Tracking**: Keeps a JSON history of all runs.
- ⏰ **Weekly Automation**: Automatic weekly updates with two scheduling options.

## Installation

1. **Prerequisites**: Python 3.7+
2. **Setup**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Manual Tracking (Web Interface)

1. **Start the Interface**:
   ```bash
   python leetcode_tracker.py
   ```

2. **Open Dashboard**:
   - The script will start a local web server (typically `http://127.0.0.1:5000`).
   - Open this URL in your web browser.

3. **Track Students**:
   - **CSV File Upload**:
     - Upload your `Leetcode-handles.csv` file (must contain Name, Roll Number, and LeetCode handle columns).
     - The system will extract student names, roll numbers, and usernames automatically.
     - Click "Process File".
      
   - The system will fetch live data and display the leaderboard with student names and roll numbers.
   - Results are automatically saved to `leetcode_data.csv` with all metadata.

## Automation

You have two options for weekly automatic updates:

### Option 1: Windows Task Scheduler (Recommended)

1. **Run the setup script**:
   - Right-click `setup_task_scheduler.bat` and select "Run as Administrator"
   - The script will create a scheduled task to run every Monday at 10:00 AM

2. **Customize schedule** (optional):
   - Edit `setup_task_scheduler.bat` before running
   - Change `SCHEDULE_DAY` (MONDAY, TUESDAY, etc.)
   - Change `SCHEDULE_TIME` (24-hour format, e.g., "14:30")

3. **Verify**:
   - Open Windows Task Scheduler
   - Look for "LeetCodeRatingTracker" task

### Option 2: Python Background Scheduler

1. **Configure the scheduler**:
   - Edit `scheduler.py`
   - Set `SCHEDULE_DAY` (e.g., "monday", "friday")
   - Set `SCHEDULE_TIME` (e.g., "10:00", "18:30")

2. **Run the scheduler**:
   ```bash
   python scheduler.py
   ```
   - Leave this running in the background
   - It will automatically run weekly at the configured time
   - Logs are saved to `scheduler.log`

3. **Test immediately**:
   ```bash
   python scheduler.py --run-now
   ```

## CSV File Format

Your CSV file should have the following columns (in order):
1. ID
2. Start time
3. Completion time
4. Email
5. **Name** (student name)
6. Last modified time
7. **Roll number** (e.g., AM.SC.U4CSE23018)
8. Name (as it appears in AUMS)
9. Programme
10. **Leetcode handle/userid** (LeetCode username or URL)

## Output Files

- **`leetcode_data.csv`**: Latest ratings with Name, Roll Number, Username, Rating, Global Rank, Contests Attended, Top Percentage
- **`history.json`**: Complete historical data of all runs
- **`scheduler.log`**: Automation execution logs (when using scheduler)

## Troubleshooting
- **API Errors**: The system uses a public third-party API. If it fails, wait a few minutes and try again.
- **Missing Data**: Ensure usernames are correct and profiles are public.
- **Scheduler not running**: Check `scheduler.log` for error messages.

