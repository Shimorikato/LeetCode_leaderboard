#!/usr/bin/env python3
"""
Manual Environment Variable Generator
This script generates the environment variable value that you can copy to Vercel dashboard.
"""

import json
import base64

def main():
    print("🚀 Generating fresh environment variable for Vercel...")
    
    # Check both possible data files
    data_files = ['leaderboard_data.json', 'web_leaderboard_data.json']
    data = None
    
    for file_name in data_files:
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"📊 Loaded data from {file_name} for {len(data)} users")
            break
        except FileNotFoundError:
            continue
    
    if not data:
        print("❌ Error: No data files found. Run: python leetcode_leaderboard.py first")
        return
        
    # Encode to base64
    json_str = json.dumps(data, ensure_ascii=False)
    encoded_data = base64.b64encode(json_str.encode('utf-8')).decode('ascii')
    
    print(f"🔐 Encoded data ({len(encoded_data)} characters)")
    print("\n" + "="*80)
    print("🎯 MANUAL VERCEL UPDATE - COPY THIS VALUE:")
    print("="*80)
    print("Environment Variable Name: LEADERBOARD_DATA_B64")
    print("Environment Variable Value:")
    print(encoded_data)
    print("="*80)
    
    # Show user scores for verification
    print("\n📈 Current scores:")
    for username, user_data in data.items():
        real_name = user_data.get('real_name', username)
        base_score = user_data.get('base_score', 0)
        weekly_score = user_data.get('weekly_base_score', 0)
        print(f"  • {real_name}: {base_score} points (Weekly: {weekly_score})")
    
    print("\n✅ STEPS TO UPDATE VERCEL:")
    print("1. Go to https://vercel.com/dashboard")
    print("2. Select your LeetCode_leaderboard project")
    print("3. Go to Settings → Environment Variables")
    print("4. Find LEADERBOARD_DATA_B64 and click Edit")
    print("5. Replace the value with the encoded data above")
    print("6. Save and redeploy")
    print("\n🔄 This will immediately fix the krasky/Tanishq_Kochar data display!")

if __name__ == "__main__":
    main()