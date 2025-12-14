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

    def get_env_var_value(self, key: str):
        """Return the value of a specific environment variable by key.
        Vercel's env list doesn't return decrypted values; for comparison,
        we store our last-deployed value in a dedicated checksum env var.

        Fallback approach:
        - Look for an env var named f"{key}_CHECKSUM" which stores a short hash.
        - If present, return that hash; else return None.

        This avoids trying to read encrypted values which Vercel won't expose.
        """
        envs = self.get_existing_env_vars() or {}
        for env in envs.get('envs', []):
            if env.get('key') == f"{key}_CHECKSUM":
                # The value is not returned; but for checksums, we store as 'plain'
                # If Vercel masks values, we cannot fetch it; in that case, skip
                # comparison and proceed to update. However, if type is 'plain',
                # we can read it via a separate API. To keep it simple, rely on presence.
                # Since the API does not expose values, we cannot retrieve it here.
                # We return a sentinel indicating checksum exists, prompting comparison
                # using local cache file instead (implemented below).
                return "exists"
        return None

    def compute_checksum(self, encoded_data: str) -> str:
        """Compute a short checksum for the encoded data for change detection."""
        import hashlib
        return hashlib.sha256(encoded_data.encode('utf-8')).hexdigest()[:16]

    def read_local_checksum(self) -> str | None:
        """Read last deployed checksum from a local cache file if present."""
        cache_path = ".vercel_data_checksum"
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def write_local_checksum(self, checksum: str) -> None:
        """Write checksum to a local cache file for subsequent comparisons."""
        cache_path = ".vercel_data_checksum"
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(checksum)
        except Exception:
            pass
    
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

    def update_plain_env_var(self, key, value):
        """Create a non-encrypted env var (for checksum tracking)."""
        if not self.vercel_token or not self.project_id:
            return False

        # Delete then recreate
        self.delete_env_var(key)

        url = f"{self.base_url}/v9/projects/{self.project_id}/env"
        headers = {
            "Authorization": f"Bearer {self.vercel_token}",
            "Content-Type": "application/json"
        }
        data = {
            "key": key,
            "value": value,
            "type": "plain",
            "target": ["production", "preview", "development"]
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return True
        except requests.RequestException:
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

        # Compute checksum and check local cache to avoid redundant updates
        checksum = self.compute_checksum(encoded_data)
        prev_checksum = self.read_local_checksum()
        if prev_checksum == checksum:
            print("⏱️ No changes detected (checksum match). Skipping Vercel update.")
            return True
        
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

        # Store checksum both locally and in Vercel (plain env var)
        self.write_local_checksum(checksum)
        self.update_plain_env_var("LEADERBOARD_DATA_B64_CHECKSUM", checksum)
        
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