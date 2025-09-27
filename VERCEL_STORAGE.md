# Vercel KV Storage for Leaderboard Data

This project uses Vercel KV for persistent storage in the serverless environment.

## Setup Instructions:

1. Go to your Vercel dashboard
2. Navigate to your project settings
3. Go to "Storage" tab
4. Create a new KV Database
5. Add the connection details as environment variables:
   - `KV_REST_API_URL`
   - `KV_REST_API_TOKEN`

## Alternative: Use Environment Variables (Temporary)

For quick testing, you can add users directly via environment variables in Vercel dashboard:
- Go to Settings > Environment Variables
- Add: `LEADERBOARD_DATA` with your JSON data

## Database Migration

Run the migration script to upload your current local data to Vercel KV.