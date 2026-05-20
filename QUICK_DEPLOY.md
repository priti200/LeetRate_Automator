## Quick Deployment Commands

Copy and paste these commands into PowerShell one by one:

### 1. Configure Git (one-time setup)
```powershell
git config --global user.email "your.email@example.com"
git config --global user.name "Priti"
```

### 2. Commit Your Code
```powershell
cd C:\Users\Priti\Desktop\leetcode_Rating_Automater
git add .
git commit -m "Add student name and roll number fields with weekly automation"
```

### 3. Push to GitHub
```powershell
git remote add origin https://github.com/priti200/LC_Rating_Automator.git
git branch -M main
git push -u origin main
```

---

## After Pushing to GitHub:

### Deploy to Render:

1. Go to **https://render.com** and sign up/login
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account
4. Select **"LC_Rating_Automator"** repository
5. Configure:
   - **Name**: `lc-rating-automator`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn leetcode_tracker:app`
   - **Plan**: `Free`
6. Click **"Create Web Service"**
7. Wait 2-5 minutes for deployment

### Your app will be live at:
```
https://lc-rating-automator.onrender.com
```

---

## Test Your Deployed App:
1. Visit your Render URL
2. Upload `Leetcode-handles.csv`
3. Verify rankings show Name and Roll Number columns
4. Share the URL with anyone!
