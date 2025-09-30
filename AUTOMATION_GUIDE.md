
# 🚀 LeetCode Leaderboard - Complete Automation Guide

## Quick Setup (Choose One Method)

### Method 1: GitHub Actions (Recommended)
1. **Set up Vercel API Access:**
   - Go to https://vercel.com/account/tokens
   - Create a new token, copy it
   - Go to your Vercel project → Settings → General
   - Copy your Project ID

2. **Add GitHub Secrets:**
   - Go to your GitHub repo → Settings → Secrets and variables → Actions
   - Add these secrets:
     - `VERCEL_TOKEN`: Your Vercel token
     - `VERCEL_PROJECT_ID`: Your project ID

3. **Automatic Updates:**
   - Any push to main branch automatically updates Vercel
   - Changes to data files trigger deployment
   - No manual intervention needed!

### Method 2: Local Automation Script
1. **Set Environment Variables:**
   ```powershell
   # Windows PowerShell
   $env:VERCEL_TOKEN = "your_vercel_token_here"
   $env:VERCEL_PROJECT_ID = "your_project_id_here"
   ```

2. **Run Automation:**
   ```bash
   python auto_deploy.py
   ```

### Method 3: Manual Batch Script
Run the PowerShell script:
```powershell
./deploy.ps1
```

## 📋 Daily Workflow Options

### Option A: Fully Automated (GitHub Actions)
1. Update user data: `python leetcode_leaderboard.py`
2. Run: `update all`
3. Commit changes: `git add . && git commit -m "Update data" && git push`
4. ✅ **Vercel updates automatically!**

### Option B: Semi-Automated (Local Script)
1. Update data manually
2. Run: `python auto_deploy.py`
3. ✅ **Vercel updates automatically!**

### Option C: Simple PowerShell
1. Run: `./deploy.ps1`
2. ✅ **Everything updates automatically!**

## 🔧 Files Created

- `.github/workflows/auto-deploy.yml` - GitHub Actions workflow
- `auto_deploy.py` - Python automation script
- `deploy.ps1` - PowerShell deployment script
- `AUTOMATION_GUIDE.md` - This guide

## 🚨 Security Notes

- Never commit VERCEL_TOKEN to Git
- Use GitHub Secrets for automation
- Tokens have full project access

## 📞 Troubleshooting

**Issue: "VERCEL_TOKEN not set"**
→ Set environment variables or use GitHub Secrets

**Issue: "Project not found"** 
→ Check VERCEL_PROJECT_ID is correct

**Issue: "Deployment failed"**
→ Check Vercel dashboard for errors

## 🎯 What Gets Automated

✅ Data encoding to base64
✅ Environment variable updates
✅ Vercel deployment triggers
✅ Git commits and pushes
✅ Error handling and notifications

Choose your preferred method and enjoy automated deployments! 🚀
