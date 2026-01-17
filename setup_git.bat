@echo off
echo ============================================================
echo Git Setup for Deployment
echo ============================================================
echo.
echo This will configure Git and prepare your code for GitHub.
echo.
set /p email="Enter your email address: "
set /p name="Enter your name: "
echo.
echo Configuring Git...
git config --global user.email "%email%"
git config --global user.name "%name%"
echo.
echo Committing changes...
git add .
git commit -m "Add student name and roll number fields + weekly automation + deployment setup"
echo.
echo ============================================================
echo SUCCESS! Your code is ready to push to GitHub.
echo ============================================================
echo.
echo Next steps:
echo 1. Create a repository on GitHub: https://github.com/new
echo 2. Name it: leetcode-rating-tracker
echo 3. Run these commands (replace YOUR_USERNAME):
echo.
echo    git remote add origin https://github.com/YOUR_USERNAME/leetcode-rating-tracker.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo Full instructions in DEPLOYMENT_GUIDE.md
echo.
pause
