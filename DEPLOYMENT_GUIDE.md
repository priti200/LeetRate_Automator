# LeetCode Rating Tracker - Complete Deployment Guide

## 🎯 Deployment Strategy

**Web Interface:** Deploy to Render (free, accessible anywhere)  
**Weekly Automation:** Windows Task Scheduler on your local PC (already set up)

This approach gives you:
- ✅ Free online web interface
- ✅ Working weekly automation
- ✅ Zero ongoing costs

---

## 📦 Part 1: Deploy Web Interface to Render

### Step 1: Push to GitHub

1. **Open PowerShell/Command Prompt** and navigate to your project:
   ```powershell
   cd C:\Users\Priti\Desktop\leetcode_Rating_Automater
   ```

2. **Initialize Git** (if not already done):
   ```powershell
   git init
   git add .
   git commit -m "Deploy LeetCode Rating Tracker with student metadata"
   ```

3. **Create GitHub Repository**:
   - Go to https://github.com/new
   - Repository name: `leetcode-rating-tracker`
   - Visibility: Public (or Private if you prefer)
   - **Don't** check "Add README" (we already have one)
   - Click "Create repository"

4. **Push your code**:
   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/leetcode-rating-tracker.git
   git branch -M main
   git push -u origin main
   ```
   
   Replace `YOUR_USERNAME` with your GitHub username.

---

### Step 2: Deploy to Render

1. **Sign up for Render**:
   - Go to https://render.com
   - Click "Get Started" and sign up with GitHub

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub account if prompted
   - Select your `leetcode-rating-tracker` repository

3. **Configure Service**:
   - **Name**: `leetcode-rating-tracker` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn leetcode_tracker:app`
   - **Instance Type**: `Free`
   
4. **Deploy**:
   - Click "Create Web Service"
   - Wait 2-5 minutes for deployment
   - You'll get a URL like: `https://leetcode-rating-tracker.onrender.com`

---

### Step 3: Test Your Deployed App

1. Visit your Render URL
2. Upload your `Leetcode-handles.csv` file
3. Wait for processing (may take 2-5 minutes for 132 students)
4. Verify the leaderboard shows:
   - ✅ Student names
   - ✅ Roll numbers
   - ✅ Ratings (ranked highest to lowest)

---

## ⏰ Part 2: Set Up Weekly Automation (Local)

### Option A: Windows Task Scheduler (Recommended)

1. **Right-click** `setup_task_scheduler.bat`
2. Select **"Run as Administrator"**
3. The task will be created automatically
4. Verify in Task Scheduler: look for "LeetCodeRatingTracker"

**That's it!** Your PC will automatically update ratings every Monday at 10:00 AM.

---

### Option B: Python Background Scheduler

1. **Configure** (optional):
   - Edit `scheduler.py`
   - Change `SCHEDULE_DAY` and `SCHEDULE_TIME` if needed

2. **Run**:
   ```powershell
   python scheduler.py
   ```
   Keep this window open and running.

---

## 📝 Important Notes

### Render Free Tier
- ✅ Free forever
- ⚠️ Spins down after 15 min inactivity
- ⚠️ First request takes ~30-60s to wake up
- ✅ Perfect for student projects

### Local Automation
- ✅ Runs on your PC
- ✅ Updates happen even when web is sleeping
- ⚠️ PC must be on at scheduled time
- ✅ Logs saved to `scheduler.log`

### Data Files
The automation will update:
- `leetcode_data.csv` - Latest ratings with all fields
- `history.json` - Complete historical data

You can manually upload the updated CSV to the web interface if needed.

---

## 🔧 Troubleshooting

### GitHub Push Issues
```powershell
# If you get authentication errors
git config --global user.email "your.email@example.com"
git config --global user.name "Your Name"
```

### Render Build Fails
- Check that `requirements.txt` has all dependencies
- Verify `Procfile` contains: `web: gunicorn leetcode_tracker:app`
- Check Render logs in the dashboard

### Scheduler Not Running
- Ensure PC is on at scheduled time
- Check `scheduler.log` for errors
- Verify `Leetcode-handles.csv` exists in project folder

---

## 🎉 You're Done!

**Web Interface:** Your Render URL  
**Automation:** Running locally via Task Scheduler  
**Data:** Updates automatically every week

Share your Render URL with anyone to view the current rankings!
