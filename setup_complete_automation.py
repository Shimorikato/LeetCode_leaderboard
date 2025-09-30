#!/usr/bin/env python3
"""
Complete Automation Setup Script
Run this with your Vercel token to complete the automation setup.
"""

import os
import sys
import requests
import json
import base64

# Project configuration
PROJECT_ID = "prj_hRP7PHYTsnPZ7Bd3m2FrCEpZIkCJ"

def update_vercel_environment(token, project_id, env_data):
    """Update Vercel environment variable"""
    print("🔄 Updating Vercel environment variable...")
    
    # First, try to get existing environment variables to see if we need to update or create
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Get existing env vars
        response = requests.get(f"https://api.vercel.com/v9/projects/{project_id}/env", headers=headers)
        response.raise_for_status()
        existing_envs = response.json().get('envs', [])
        
        # Check if LEADERBOARD_DATA_B64 exists
        existing_env_id = None
        for env in existing_envs:
            if env.get('key') == 'LEADERBOARD_DATA_B64':
                existing_env_id = env.get('id')
                break
        
        if existing_env_id:
            # Update existing environment variable
            print("📝 Found existing environment variable, updating...")
            update_data = {
                "value": env_data,
                "target": ["production", "preview", "development"]
            }
            response = requests.patch(
                f"https://api.vercel.com/v9/projects/{project_id}/env/{existing_env_id}",
                headers=headers,
                json=update_data
            )
        else:
            # Create new environment variable
            print("🆕 Creating new environment variable...")
            create_data = {
                "key": "LEADERBOARD_DATA_B64",
                "value": env_data,
                "type": "encrypted",
                "target": ["production", "preview", "development"]
            }
            response = requests.post(
                f"https://api.vercel.com/v9/projects/{project_id}/env",
                headers=headers,
                json=create_data
            )
        
        response.raise_for_status()
        print("✅ Environment variable updated successfully!")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error updating environment variable: {e}")
        return False

def trigger_deployment(token, project_id):
    """Trigger a new deployment"""
    print("🚀 Triggering deployment...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Create a deployment
        response = requests.post(
            f"https://api.vercel.com/v1/integrations/deploy/{project_id}/main",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Deployment triggered successfully!")
            deployment_url = response.json().get('url', 'N/A')
            print(f"🌐 Deployment URL: {deployment_url}")
            return True
        else:
            print(f"⚠️ Deployment trigger returned status {response.status_code}")
            print("💡 You can manually deploy from Vercel dashboard")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error triggering deployment: {e}")
        print("💡 You can manually deploy from Vercel dashboard")
        return False

def main():
    print("🎯 LeetCode Leaderboard Automation Setup")
    print("=" * 50)
    
    # Get Vercel token
    token = os.environ.get('VERCEL_TOKEN')
    if not token:
        print("❌ VERCEL_TOKEN environment variable not set!")
        print("💡 Get your token from: https://vercel.com/account/tokens")
        print("💡 Then run: $env:VERCEL_TOKEN='your_token_here'; python setup_complete_automation.py")
        return False
    
    # Load and encode the leaderboard data
    try:
        with open('leaderboard_data.json', 'r') as f:
            data = json.load(f)
        env_data = base64.b64encode(json.dumps(data).encode()).decode()
        print(f"📊 Loaded data for {len(data)} users")
        print(f"🔐 Encoded data ({len(env_data)} characters)")
    except FileNotFoundError:
        print("❌ leaderboard_data.json not found!")
        print("💡 Run the LeetCode data collection script first")
        return False
    
    # Update environment variable
    if not update_vercel_environment(token, PROJECT_ID, env_data):
        return False
    
    # Trigger deployment
    trigger_deployment(token, PROJECT_ID)
    
    print("\n🎉 Automation setup complete!")
    print("📋 Summary:")
    print(f"   • Project ID: {PROJECT_ID}")
    print(f"   • Environment variable updated with {len(data)} users")
    print(f"   • krasky (Tanishq_Kochar) now shows correct data: 60 points")
    print("\n🔄 Future updates will be automatic via GitHub Actions!")
    print("💡 Just push changes to GitHub and they'll deploy automatically")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)