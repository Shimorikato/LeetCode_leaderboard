@echo off
echo 🚀 Starting Advanced LeetCode Leaderboard Web App...
echo.
echo 📋 Checking requirements...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo ❌ Flask not found. Installing requirements...
    pip install -r requirements.txt
) else (
    echo ✅ Flask is installed
)
echo.
echo 🌐 Starting web server...
echo 📱 Open your browser and go to: http://localhost:5000
echo 🔥 Press Ctrl+C to stop the server
echo.
python web_app.py
pause