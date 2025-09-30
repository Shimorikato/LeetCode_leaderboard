#!/usr/bin/env python3
"""
Quick script to update Vercel environment variable with the corrected leaderboard data.
"""

import json
import base64

def main():
    print("🚀 Generating updated environment variable for Vercel...")
    
    # Load the current leaderboard data
    try:
        with open('leaderboard_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📊 Loaded data for {len(data)} users")
        
        # Encode to base64
        json_str = json.dumps(data, ensure_ascii=False)
        encoded_data = base64.b64encode(json_str.encode('utf-8')).decode('ascii')
        
        print(f"🔐 Encoded data ({len(encoded_data)} characters)")
        print("\n" + "="*80)
        print("COPY THIS VALUE TO VERCEL DASHBOARD:")
        print("="*80)
        print("Environment Variable Name: LEADERBOARD_DATA_B64")
        print("Environment Variable Value:")
        print(encoded_data)
        print("="*80)
        
        # Show user scores for verification
        print("\n📈 Current scores:")
        for username, user_data in data.items():
            print(f"  • {user_data.get('real_name', username)}: {user_data.get('base_score', 0)} points")
        
        print("\n✅ To complete the setup:")
        print("1. Go to your Vercel dashboard")
        print("2. Select your LeetCode_leaderboard project")
        print("3. Go to Settings → Environment Variables")
        print("4. Add or update LEADERBOARD_DATA_B64 with the value above")
        print("5. Make sure to select all environments (Production, Preview, Development)")
        print("6. Save and redeploy")
        
    except FileNotFoundError:
        print("❌ Error: leaderboard_data.json not found")
        print("   Please run: python leetcode_leaderboard.py first")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()