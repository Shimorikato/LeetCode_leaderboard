#!/usr/bin/env python3
"""
GitHub Data Updater
Updates the JSON files in the GitHub repository when called from Vercel.
"""

import json
import os
import subprocess
import sys
from datetime import datetime


def update_github_files():
    """Update GitHub repository with fresh data."""
    try:
        # Check if we're in a git repository
        if not os.path.exists('.git'):
            print("❌ Not in a git repository")
            return False
        
        # Check if there are any changes
        result = subprocess.run(['git', 'status', '--porcelain'], 
                               capture_output=True, text=True, timeout=10)
        
        if not result.stdout.strip():
            print("ℹ️ No changes to commit")
            return True
        
        print("📝 Detected changes, committing to GitHub...")
        
        # Configure git user (required for commits)
        subprocess.run(['git', 'config', 'user.email', 'action@github.com'], 
                      capture_output=True, text=True, timeout=5)
        subprocess.run(['git', 'config', 'user.name', 'Leaderboard Auto-Update'], 
                      capture_output=True, text=True, timeout=5)
        
        # Add the JSON files
        subprocess.run(['git', 'add', 'leaderboard_data.json', 'web_leaderboard_data.json'], 
                      capture_output=True, text=True, timeout=10)
        
        # Create commit message with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        commit_msg = f"🔄 Auto-update leaderboard data ({timestamp})"
        
        # Commit the changes
        commit_result = subprocess.run(['git', 'commit', '-m', commit_msg], 
                                     capture_output=True, text=True, timeout=10)
        
        if commit_result.returncode == 0:
            print("✅ Changes committed successfully")
            
            # Try to push
            push_result = subprocess.run(['git', 'push', 'origin', 'main'], 
                                       capture_output=True, text=True, timeout=20)
            
            if push_result.returncode == 0:
                print("🚀 Changes pushed to GitHub successfully")
                return True
            else:
                print(f"❌ Push failed: {push_result.stderr}")
                return False
        else:
            print(f"❌ Commit failed: {commit_result.stderr}")
            return False
            
    except Exception as e:
        print(f"💥 Error updating GitHub: {e}")
        return False


def main():
    """Main function."""
    print("🔄 Starting GitHub data update...")
    success = update_github_files()
    
    if success:
        print("✅ GitHub update completed successfully")
        sys.exit(0)
    else:
        print("❌ GitHub update failed")
        sys.exit(1)


if __name__ == "__main__":
    main()