#!/usr/bin/env python3
"""
Complete Automation Setup for LeetCode Leaderboard
This script sets up automated deployment for your leaderboard.
"""        with open('.gitignore', 'a', encoding='utf-8') as f:
            f.write(gitignore_additions)
import json
import os
import sys

def create_automation_guide():
    """Create a comprehensive automation guide"""
    
    guide = """
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
"""
    
    with open('AUTOMATION_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("✅ Created AUTOMATION_GUIDE.md")

def create_env_template():
    """Create environment variable template"""
    template = """# Vercel Automation Environment Variables
# Copy this file to .env and fill in your values

VERCEL_TOKEN=your_vercel_token_here
VERCEL_PROJECT_ID=your_project_id_here

# Get your token: https://vercel.com/account/tokens
# Get your project ID: Vercel Dashboard -> Project -> Settings -> General
"""
    
    with open('.env.template', 'w', encoding='utf-8') as f:
        f.write(template)
    
    print("✅ Created .env.template")

def setup_gitignore():
    """Add automation files to gitignore"""
    gitignore_additions = """
# Automation files
.env
env_output.txt
base64_data.txt
"""
    
    try:
        with open('.gitignore', 'r') as f:
            content = f.read()
        
        if "# Automation files" not in content:
            with open('.gitignore', 'a') as f:
                f.write(gitignore_additions)
            print("✅ Updated .gitignore")
        else:
            print("✅ .gitignore already configured")
    except FileNotFoundError:
        with open('.gitignore', 'w', encoding='utf-8') as f:
            f.write(gitignore_additions)
        print("✅ Created .gitignore")

def main():
    print("🚀 Setting up LeetCode Leaderboard Automation...")
    print("="*60)
    
    # Create all automation files
    create_automation_guide()
    create_env_template() 
    setup_gitignore()
    
    print("\n" + "="*60)
    print("✅ Automation setup completed!")
    print("\n📖 Next steps:")
    print("1. Read AUTOMATION_GUIDE.md")
    print("2. Choose your preferred automation method")
    print("3. Follow the setup instructions")
    print("4. Enjoy automated deployments! 🎉")
    
    # Show current files
    print(f"\n📁 Files created:")
    automation_files = [
        '.github/workflows/auto-deploy.yml',
        'auto_deploy.py', 
        'deploy.ps1',
        'AUTOMATION_GUIDE.md',
        '.env.template'
    ]
    
    for file in automation_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file}")

if __name__ == "__main__":
    main()