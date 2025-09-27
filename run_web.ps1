# Advanced LeetCode Leaderboard Web App Launcher
Write-Host "🚀 Starting Advanced LeetCode Leaderboard Web App..." -ForegroundColor Green
Write-Host ""

# Check if Flask is installed
Write-Host "📋 Checking requirements..." -ForegroundColor Yellow
try {
    python -c "import flask" 2>$null
    Write-Host "✅ Flask is installed" -ForegroundColor Green
}
catch {
    Write-Host "❌ Flask not found. Installing requirements..." -ForegroundColor Red
    pip install -r requirements.txt
}

Write-Host ""
Write-Host "🌐 Starting web server..." -ForegroundColor Cyan
Write-Host "📱 Open your browser and go to: " -NoNewline -ForegroundColor White
Write-Host "http://localhost:5000" -ForegroundColor Yellow
Write-Host "🔥 Press Ctrl+C to stop the server" -ForegroundColor Magenta
Write-Host ""

# Start the web application
python web_app.py