#!/usr/bin/env python3
"""
Example script showing how to use the Advanced LeetCode Leaderboard programmatically.
Demonstrates the new scoring system and enhanced features.
"""

from leetcode_leaderboard import LeetCodeLeaderboard, get_user_stats, calculate_advanced_score

def example_usage():
    """Example of how to use the advanced leaderboard programmatically."""
    
    print("🚀 Advanced LeetCode Leaderboard Example")
    print("="*50)
    
    # Create a leaderboard instance
    leaderboard = LeetCodeLeaderboard("example_leaderboard.json")
    
    # Example usernames (replace with real ones)
    example_users = [
        "leetcode",  # LeetCode's official account
        # Add your friends' usernames here
    ]
    
    print(f"\n📋 Adding {len(example_users)} example users...")
    
    # Add users to leaderboard
    for username in example_users:
        print(f"\n🔍 Adding {username}...")
        if leaderboard.add_user(username):
            # Show user details with new scoring
            leaderboard.display_user_details(username)
        else:
            print(f"❌ Could not add {username} (user may not exist or be private)")
    
    print("\n" + "="*80)
    print("📊 Advanced Leaderboard (Default: Advanced Score):")
    leaderboard.display_leaderboard("advanced_score")
    
    print("\n" + "="*80)
    print("🎯 Different Sorting Options:")
    
    # Demonstrate different sorting options
    sort_options = [
        ("advanced_score", "🏆 Advanced Score (Performance-based)"),
        ("base_score", "📊 Base Score (Easy×1 + Medium×3 + Hard×7)"),
        ("total_solved", "🔢 Total Problems Solved"),
        ("hard", "💪 Hard Problems Champion"),
        ("ranking", "🥇 Best LeetCode Ranking")
    ]
    
    for sort_key, description in sort_options:
        print(f"\n{description}:")
        leaderboard.display_leaderboard(sort_key)
        print("="*80)


def test_single_user():
    """Test fetching a single user's stats with advanced scoring."""
    print("\n🧪 Testing Advanced User Stats Fetch...")
    
    # Test with LeetCode's official account
    stats = get_user_stats("leetcode")
    if stats:
        print("✅ Successfully fetched enhanced user stats:")
        
        # Show basic stats
        print(f"📊 Username: {stats['username']}")
        print(f"📚 Total Problems: {stats['total_solved']}")
        print(f"🟢 Easy: {stats['easy']} (×1 = {stats['easy']} pts)")
        print(f"🟡 Medium: {stats['medium']} (×3 = {stats['medium'] * 3} pts)")
        print(f"🔴 Hard: {stats['hard']} (×7 = {stats['hard'] * 7} pts)")
        print(f"⭐ Base Score: {stats.get('base_score', 0)} pts")
        
        # Calculate and show advanced score
        adv_score = calculate_advanced_score(stats)
        print(f"🎯 Advanced Score: {adv_score} pts")
        
        # Show additional data
        languages = stats.get('languages', {})
        if languages:
            print(f"💻 Languages: {', '.join(list(languages.keys())[:3])}")
        
        topics = stats.get('topics', {})
        if topics:
            print(f"🏷️ Top Topics: {', '.join(list(topics.keys())[:3])}")
            
        recent_subs = stats.get('recent_submissions', [])
        print(f"🕐 Recent Submissions: {len(recent_subs)}")
        
    else:
        print("❌ Could not fetch user stats")


if __name__ == "__main__":
    # Test single user fetch first
    test_single_user()
    
    # Run example usage
    example_usage()
    
    print("\n" + "="*80)
    print("🎉 Advanced Leaderboard Example Complete!")
    print("💡 To run the interactive version: python leetcode_leaderboard.py")
    print("📖 Check README.md for full documentation")
    print("\n🏆 New Scoring System Features:")
    print("   • Easy problems = 1 point each")
    print("   • Medium problems = 3 points each") 
    print("   • Hard problems = 7 points each")
    print("   • Advanced score includes performance multiplier")
    print("   • Time-based analytics (daily/weekly/yearly)")
    print("   • Language and topic analysis")
    print("   • Recent submission tracking")