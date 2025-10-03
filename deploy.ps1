#!/usr/bin/env pwsh
# PowerShell script for automated deployment

param(
    [string]$Message = "Automated update: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
)

Write-Host "🚀 Starting automated LeetCode Leaderboard deployment..." -ForegroundColor Green
Write-Host "⏰ Time: $(Get-Date)" -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "web_leaderboard_data.json")) {
    Write-Host "❌ web_leaderboard_data.json not found! Make sure you're in the project directory." -ForegroundColor Red
    exit 1
}

# Step 1: Update user data (optional)
Write-Host "`n📊 Updating user data..." -ForegroundColor Yellow
try {
    python leetcode_leaderboard.py -c "update"  # If you add command line support
    Write-Host "✅ User data updated" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Could not update user data automatically" -ForegroundColor Yellow
}

# Step 2: Sync web data
Write-Host "`n🔄 Syncing web leaderboard data..." -ForegroundColor Yellow
if (Test-Path "leaderboard_data.json") {
    Copy-Item "leaderboard_data.json" "web_leaderboard_data.json" -Force
    Write-Host "✅ Data synced" -ForegroundColor Green
}

# Step 3: Run automated deployment
Write-Host "`n🚀 Running automated deployment..." -ForegroundColor Yellow
python auto_deploy.py

# Step 4: Commit and push changes
Write-Host "`n📝 Committing changes to Git..." -ForegroundColor Yellow
git add .
git commit -m $Message
git push origin main

Write-Host "`n✅ Deployment process completed!" -ForegroundColor Green
Write-Host "🌐 Check your Vercel dashboard for deployment status" -ForegroundColor Cyan