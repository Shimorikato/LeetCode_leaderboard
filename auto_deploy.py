#!/usr/bin/env python3
"""
Automated Vercel Deployment Script
Automatically syncs local data to Vercel environment variables and triggers deployment.
"""

import json
import base64
import requests
import os
import sys
from datetime import datetime

class VercelAutoDeployer:
    def __init__(self):
        self.vercel_token = os.getenv('VERCEL_TOKEN')
        self.project_id = os.getenv('VERCEL_PROJECT_ID')
        self.base_url = "https://api.vercel.com"
        
    def load_local_data(self):
        """Load data from web_leaderboard_data.json"""
        try:
            with open('web_leaderboard_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ web_leaderboard_data.json not found!")
            return None
    
    def encode_data(self, data):
        """Encode data to base64"""
        json_str = json.dumps(data, separators=(',', ':'))
        encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        return encoded
    
    def get_existing_env_vars(self):
        """Get existing environment variables from Vercel"""
        if not self.vercel_token or not self.project_id:
            return None
            
        url = f"{self.base_url}/v9/projects/{self.project_id}/env"
        headers = {
            "Authorization": f"Bearer {self.vercel_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Error fetching environment variables: {e}")
            return None
    
    def update_env_var(self, key, value):
        """Update or create environment variable in Vercel"""
        if not self.vercel_token or not self.project_id:
            print("❌ VERCEL_TOKEN and VERCEL_PROJECT_ID must be set!")
            return False
        
        # First, try to delete existing variable
        self.delete_env_var(key)
        
        # Create new variable
        url = f"{self.base_url}/v9/projects/{self.project_id}/env"
        headers = {
            "Authorization": f"Bearer {self.vercel_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "key": key,
            "value": value,
            "type": "encrypted",
            "target": ["production", "preview", "development"]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            print(f"✅ Updated environment variable: {key}")
            return True
        except requests.RequestException as e:
            print(f"❌ Error updating environment variable: {e}")
            return False
    
    def delete_env_var(self, key):
        """Delete existing environment variable"""
        env_vars = self.get_existing_env_vars()
        if not env_vars:
            return
        
        # Find existing variable
        for env_var in env_vars.get('envs', []):
            if env_var.get('key') == key:
                env_id = env_var.get('id')
                url = f"{self.base_url}/v9/projects/{self.project_id}/env/{env_id}"
                headers = {"Authorization": f"Bearer {self.vercel_token}"}
                
                try:
                    response = requests.delete(url, headers=headers)
                    response.raise_for_status()
                    print(f"🗑️ Deleted old environment variable: {key}")
                except requests.RequestException:
                    pass  # Ignore deletion errors
                break
    
    def trigger_deployment(self):
        """Trigger a new deployment"""
        if not self.vercel_token or not self.project_id:
            return False
            
        url = f"{self.base_url}/v13/deployments"
        headers = {
            "Authorization": f"Bearer {self.vercel_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "name": "leetcode-leaderboard",
            "gitSource": {
                "type": "github",
                "ref": "main"
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            deployment = response.json()
            deployment_url = deployment.get('url', 'unknown')
            print(f"🚀 Triggered deployment: https://{deployment_url}")
            return True
        except requests.RequestException as e:
            print(f"⚠️ Could not trigger deployment: {e}")
            print("   Deployment will happen automatically via Git push")
            return False
    
    def deploy(self):
        """Main deployment function"""
        print("🚀 Starting automated Vercel deployment...")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Load local data
        data = self.load_local_data()
        if not data:
            return False
        
        print(f"📊 Loaded data for {len(data)} users")
        
        # Encode data
        encoded_data = self.encode_data(data)
        print(f"🔐 Encoded data ({len(encoded_data)} characters)")
        
        # Check if we have Vercel credentials
        if not self.vercel_token or not self.project_id:
            print("\n📋 MANUAL SETUP REQUIRED:")
            print("="*60)
            print("Environment Variable Name: LEADERBOARD_DATA_B64")
            print("Environment Variable Value:")
            print(encoded_data)
            print("="*60)
            
            # Show user scores for verification
            print("\n� Current scores:")
            for username, user_data in data.items():
                real_name = user_data.get('real_name', username)
                base_score = user_data.get('base_score', 0)
                weekly_score = user_data.get('weekly_base_score', 0)
                print(f"  • {real_name}: {base_score} points (Weekly: {weekly_score})")
            
            print("\n�📝 To automate this process:")
            print("1. Get your Vercel token: https://vercel.com/account/tokens")
            print("2. Get your project ID from Vercel dashboard")
            print("3. Set environment variables:")
            print("   export VERCEL_TOKEN=your_token_here")
            print("   export VERCEL_PROJECT_ID=your_project_id_here")
            print("4. Run this script again")
            
            # For GitHub Actions, this is still considered success since data was updated
            if os.getenv('GITHUB_ACTIONS'):
                print("\n🔄 Running in GitHub Actions - manual Vercel update required")
                print("✅ LeetCode data updated successfully! Manual Vercel update needed.")
                return True
            return False
        
        # Update environment variable
        success = self.update_env_var("LEADERBOARD_DATA_B64", encoded_data)
        if not success:
            return False
        
        # Trigger deployment
        self.trigger_deployment()
        
        print("✅ Automated deployment completed!")
        return True

def main():
    deployer = VercelAutoDeployer()
    success = deployer.deploy()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()