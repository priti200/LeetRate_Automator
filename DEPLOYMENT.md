# LeetCode Rating Automater - Deployment Guide

## 🚀 Deploy to Render

Follow these steps to deploy your LeetCode Rating Automater to Render:

### Prerequisites
- A GitHub account
- A Render account (free - sign up at https://render.com)

### Step 1: Push to GitHub

1. **Initialize Git repository** (if not already done):
   ```bash
   cd c:\Users\Priti\Desktop\leetcode_Rating_Automater
   git init
   git add .
   git commit -m "Initial commit - LeetCode Rating Automater"
   ```

2. **Create a new repository on GitHub**:
   - Go to https://github.com/new
   - Repository name: `leetcode-rating-automater`
   - Keep it Public (or Private if you prefer)
   - Don't initialize with README, .gitignore, or license (we already have these)
   - Click "Create repository"

3. **Push your code to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/leetcode-rating-automater.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy on Render

1. **Go to Render Dashboard**:
   - Visit https://dashboard.render.com
   - Sign in or create a free account

2. **Create a New Web Service**:
   - Click "New +" button → "Web Service"
   - Connect your GitHub account if not already connected
   - Select your `leetcode-rating-automater` repository

3. **Configure the Web Service**:
   - **Name**: `leetcode-rating-automater` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn leetcode_tracker:app`
   - **Instance Type**: `Free`

4. **Deploy**:
   - Click "Create Web Service"
   - Render will automatically deploy your app
   - Wait 2-5 minutes for the build to complete

5. **Access Your App**:
   - Once deployed, you'll get a URL like: `https://leetcode-rating-automater.onrender.com`
   - Visit this URL to use your app!

### ⚠️ Important Notes

1. **Free Tier Limitations**:
   - Render free tier spins down after 15 minutes of inactivity
   - First request after inactivity may take 30-60 seconds to wake up
   - Sufficient for student projects and demos

2. **Rate Limiting**:
   - The app uses 3 concurrent workers to avoid API rate limits
   - Processing 132 students may take 2-5 minutes
   - This is normal and expected

3. **File Size Limits**:
   - CSV files should be under 10MB
   - Most student lists will be well under this limit

### 🔧 Troubleshooting

**Build fails?**
- Check that `requirements.txt` has all dependencies
- Check that `Procfile` exists and is correct

**App crashes?**
- Check the Render logs in the dashboard
- Common issue: PORT environment variable (already handled in code)

**Slow processing?**
- This is normal for large files due to API rate limiting
- Consider reducing concurrent workers if needed

### 📱 Using Your Deployed App

1. Visit your Render URL
2. Upload your `Leetcode-handles.csv` file
3. Wait for processing (check terminal logs in Render dashboard)
4. View results!

---

**Need help?** Check Render's documentation: https://render.com/docs
