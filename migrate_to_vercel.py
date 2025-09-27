#!/usr/bin/env python3
"""
Vercel Data Migration Script
This script helps you upload your local leaderboard data to Vercel via environment variables.
"""

import json
import base64

def compress_and_encode_data():
    """Read local data and prepare it for Vercel environment variables."""
    try:
        # Read the local leaderboard data
        with open('leaderboard_data.json', 'r') as f:
            data = json.load(f)
        
        # Convert to JSON string
        json_str = json.dumps(data)
        
        # Encode to base64 to handle special characters
        encoded_data = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        
        print("=" * 60)
        print("VERCEL ENVIRONMENT VARIABLE SETUP")
        print("=" * 60)
        print("\n1. Go to your Vercel dashboard")
        print("2. Navigate to your project settings")
        print("3. Go to 'Environment Variables' tab")
        print("4. Add a new environment variable:")
        print("   Name: LEADERBOARD_DATA_B64")
        print("   Value: (copy the encoded data below)")
        print("   Environment: Production, Preview, Development")
        print("\n" + "=" * 60)
        print("ENCODED DATA (copy everything between the lines):")
        print("-" * 60)
        print(encoded_data)
        print("-" * 60)
        print(f"\nData contains {len(data)} users")
        print("Users:", ", ".join(data.keys()))
        print("\n5. After adding the environment variable, redeploy your app")
        print("6. Your local data will now be available on Vercel!")
        
    except FileNotFoundError:
        print("Error: leaderboard_data.json not found in current directory")
        print("Make sure you're running this script from the project root")
    except json.JSONDecodeError:
        print("Error: Invalid JSON in leaderboard_data.json")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    compress_and_encode_data()