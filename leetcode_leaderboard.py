import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import calendar

def get_user_stats(username: str) -> Optional[Dict]:
    """
    Fetch comprehensive LeetCode user statistics via GraphQL API.
    
    Args:
        username: LeetCode username
        
    Returns:
        Dictionary with detailed user stats or None if user not found
    """
    url = "https://leetcode.com/graphql"
    query = """
    query getUserProfile($username: String!) {
      matchedUser(username: $username) {
        username
        submitStatsGlobal {
          acSubmissionNum {
            difficulty
            count
          }
        }
        profile {
          realName
          ranking
          userAvatar
          aboutMe
        }
        submissionCalendar
        languageProblemCount {
          languageName
          problemsSolved
        }
        tagProblemCounts {
          advanced {
            tagName
            problemsSolved
          }
          intermediate {
            tagName
            problemsSolved
          }
          fundamental {
            tagName
            problemsSolved
          }
        }
      }
      recentSubmissionList(username: $username) {
        title
        titleSlug
        timestamp
        statusDisplay
        lang
        runtime
        memory
        url
      }
    }
    """
    
    try:
        variables = {"username": username}
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'LeetCode-Leaderboard/1.0'
        }
        
        response = requests.post(
            url, 
            json={"query": query, "variables": variables},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Check if user exists
        if not data.get("data") or not data["data"].get("matchedUser"):
            print(f"❌ User '{username}' not found on LeetCode")
            return None
            
        user = data["data"]["matchedUser"]
        
        # Parse submission stats
        solved = {}
        if user.get("submitStatsGlobal") and user["submitStatsGlobal"].get("acSubmissionNum"):
            for item in user["submitStatsGlobal"]["acSubmissionNum"]:
                solved[item["difficulty"]] = item["count"]
        
        # Get profile info
        profile = user.get("profile", {})
        
        # Parse recent submissions for advanced scoring
        recent_submissions = data["data"].get("recentSubmissionList", [])
        
        # Parse language distribution
        languages = {}
        if user.get("languageProblemCount"):
            for lang_data in user["languageProblemCount"]:
                languages[lang_data["languageName"]] = lang_data["problemsSolved"]
        
        # Parse topic/tag distribution
        topics = {}
        if user.get("tagProblemCounts"):
            tag_counts = user["tagProblemCounts"]
            for level in ["fundamental", "intermediate", "advanced"]:
                if tag_counts.get(level):
                    for tag_data in tag_counts[level]:
                        topics[tag_data["tagName"]] = topics.get(tag_data["tagName"], 0) + tag_data["problemsSolved"]
        
        # Calculate weekly problems from submission calendar
        submission_calendar = user.get("submissionCalendar", "")
        weekly_problems = calculate_weekly_problems(submission_calendar, solved)
        
        # Calculate scores - both total and weekly
        total_base_score = (solved.get("Easy", 0) * 1 + 
                           solved.get("Medium", 0) * 3 + 
                           solved.get("Hard", 0) * 7)
        
        weekly_base_score = (weekly_problems.get("Easy", 0) * 1 + 
                            weekly_problems.get("Medium", 0) * 3 + 
                            weekly_problems.get("Hard", 0) * 7)
        
        # Get current week info
        week_start_ts, week_end_ts = get_current_week_bounds()
        week_start_date = datetime.fromtimestamp(week_start_ts).strftime("%Y-%m-%d")
        week_end_date = datetime.fromtimestamp(week_end_ts).strftime("%Y-%m-%d")
        
        return {
            "username": user["username"],
            "real_name": profile.get("realName", ""),
            "ranking": profile.get("ranking", 0),
            
            # Total (all-time) stats
            "total_solved": solved.get("All", 0),
            "easy": solved.get("Easy", 0),
            "medium": solved.get("Medium", 0),
            "hard": solved.get("Hard", 0),
            "base_score": total_base_score,
            
            # Weekly stats
            "weekly_total": weekly_problems.get("All", 0),
            "weekly_easy": weekly_problems.get("Easy", 0),
            "weekly_medium": weekly_problems.get("Medium", 0),
            "weekly_hard": weekly_problems.get("Hard", 0),
            "weekly_base_score": weekly_base_score,
            "current_week": f"{week_start_date} to {week_end_date}",
            
            # Additional data
            "languages": languages,
            "topics": topics,
            "recent_submissions": recent_submissions[:10],
            "submission_calendar": submission_calendar,
            "last_updated": datetime.now().isoformat()
        }
        
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout while fetching data for {username}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"🌐 Network error for {username}: {e}")
        return None
    except (KeyError, TypeError) as e:
        print(f"📊 Data parsing error for {username}: {e}")
        return None
    except Exception as e:
        print(f"💥 Unexpected error for {username}: {e}")
        return None


def get_current_week_bounds():
    """
    Get the start and end timestamps for the current week (Monday to Sunday).
    
    Returns:
        tuple: (week_start_timestamp, week_end_timestamp)
    """
    now = datetime.now()
    # Get the Monday of current week
    days_since_monday = now.weekday()
    week_start = now - timedelta(days=days_since_monday)
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get the Sunday of current week
    week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    
    return int(week_start.timestamp()), int(week_end.timestamp())


def parse_submission_calendar(submission_calendar_str: str) -> Dict[str, int]:
    """
    Parse LeetCode submission calendar JSON string.
    
    Args:
        submission_calendar_str: JSON string containing submission data
        
    Returns:
        Dictionary mapping date timestamps to submission counts
    """
    try:
        if submission_calendar_str:
            return json.loads(submission_calendar_str)
        return {}
    except (json.JSONDecodeError, TypeError):
        return {}


def calculate_weekly_problems(submission_calendar: str, solved_problems: Dict[str, int]) -> Dict[str, int]:
    """
    Calculate problems solved in the current week based on submission calendar.
    
    Args:
        submission_calendar: LeetCode submission calendar JSON string
        solved_problems: Dictionary with total solved problems by difficulty
        
    Returns:
        Dictionary with weekly problems by difficulty
    """
    week_start_ts, week_end_ts = get_current_week_bounds()
    calendar_data = parse_submission_calendar(submission_calendar)
    
    # Count submissions in current week
    weekly_submissions = 0
    for timestamp_str, count in calendar_data.items():
        try:
            timestamp = int(timestamp_str)
            if week_start_ts <= timestamp <= week_end_ts:
                weekly_submissions += count
        except (ValueError, TypeError):
            continue
    
    if weekly_submissions == 0:
        return {"Easy": 0, "Medium": 0, "Hard": 0, "All": 0}
    
    # Estimate weekly distribution based on overall difficulty ratios
    total_solved = solved_problems.get("All", 0)
    if total_solved == 0:
        return {"Easy": 0, "Medium": 0, "Hard": 0, "All": weekly_submissions}
    
    # Calculate ratios from total problems
    easy_ratio = solved_problems.get("Easy", 0) / total_solved
    medium_ratio = solved_problems.get("Medium", 0) / total_solved
    hard_ratio = solved_problems.get("Hard", 0) / total_solved
    
    # Apply ratios to weekly submissions (with some randomization for realism)
    weekly_easy = int(weekly_submissions * easy_ratio)
    weekly_medium = int(weekly_submissions * medium_ratio)
    weekly_hard = int(weekly_submissions * hard_ratio)
    
    # Adjust for rounding discrepancies
    total_estimated = weekly_easy + weekly_medium + weekly_hard
    if total_estimated < weekly_submissions:
        # Add remainder to most common difficulty
        max_difficulty = max([("Easy", weekly_easy), ("Medium", weekly_medium), ("Hard", weekly_hard)], key=lambda x: x[1])
        if max_difficulty[0] == "Easy":
            weekly_easy += (weekly_submissions - total_estimated)
        elif max_difficulty[0] == "Medium":
            weekly_medium += (weekly_submissions - total_estimated)
        else:
            weekly_hard += (weekly_submissions - total_estimated)
    
    return {
        "Easy": weekly_easy,
        "Medium": weekly_medium, 
        "Hard": weekly_hard,
        "All": weekly_submissions
    }


def get_problem_difficulty(title_slug: str) -> str:
    """
    Get problem difficulty by title slug.
    This is a simplified approach - in practice you'd need a problem database.
    """
    # This would ideally query LeetCode's problem database
    # For now, return "Medium" as default
    return "Medium"


def analyze_time_frames(submission_calendar: str, recent_submissions: List) -> Dict:
    """
    Analyze user activity across different time frames.
    
    Args:
        submission_calendar: LeetCode submission calendar data
        recent_submissions: List of recent submissions
        
    Returns:
        Dictionary with daily, weekly, yearly stats
    """
    now = datetime.now()
    
    # Parse submission calendar (it's usually a JSON string)
    calendar_data = {}
    try:
        if submission_calendar:
            calendar_data = json.loads(submission_calendar)
    except:
        calendar_data = {}
    
    # Calculate daily activity (last 7 days)
    daily_count = 0
    for i in range(7):
        date_key = str(int((now - timedelta(days=i)).timestamp()))
        daily_count += calendar_data.get(date_key, 0)
    
    # Calculate weekly activity (last 30 days)
    weekly_count = 0
    for i in range(30):
        date_key = str(int((now - timedelta(days=i)).timestamp()))
        weekly_count += calendar_data.get(date_key, 0)
    
    # Calculate yearly activity (last 365 days)
    yearly_count = 0
    for i in range(365):
        date_key = str(int((now - timedelta(days=i)).timestamp()))
        yearly_count += calendar_data.get(date_key, 0)
    
    return {
        "daily_submissions": daily_count,
        "weekly_submissions": weekly_count,
        "yearly_submissions": yearly_count,
        "recent_activity_count": len(recent_submissions)
    }


class LeetCodeLeaderboard:
    """
    A LeetCode leaderboard to track and compare friend's progress.
    """
    
    def __init__(self, data_file: str = "leaderboard_data.json"):
        self.data_file = data_file
        self.users = {}
        self.load_data()
    
    def load_data(self) -> None:
        """Load existing user data from JSON file."""
        try:
            with open(self.data_file, 'r') as f:
                self.users = json.load(f)
            print(f"📁 Loaded data for {len(self.users)} users")
        except FileNotFoundError:
            print("📁 No existing data file found, starting fresh")
            self.users = {}
        except json.JSONDecodeError:
            print("❌ Error reading data file, starting fresh")
            self.users = {}
    
    def save_data(self) -> None:
        """Save current user data to JSON file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.users, f, indent=2)
            print(f"💾 Data saved successfully")
        except Exception as e:
            print(f"❌ Error saving data: {e}")
    
    def add_user(self, username: str) -> bool:
        """
        Add a new user to the leaderboard.
        
        Args:
            username: LeetCode username to add
            
        Returns:
            True if user added successfully, False otherwise
        """
        print(f"🔍 Fetching data for {username}...")
        user_stats = get_user_stats(username)
        
        if user_stats:
            # Calculate time analytics
            user_stats["time_analytics"] = analyze_time_frames(
                user_stats.get("submission_calendar", ""),
                user_stats.get("recent_submissions", [])
            )
            
            self.users[username.lower()] = user_stats
            self.save_data()
            print(f"✅ Added {username} to leaderboard!")
            print(f"📊 Weekly Score: {user_stats.get('weekly_base_score', 0)} pts")
            print(f"📈 Total Score: {user_stats.get('base_score', 0)} pts")
            print(f"🗓️ Current Week: {user_stats.get('current_week', 'Unknown')}")
            return True
        else:
            print(f"❌ Could not add {username}")
            return False
    
    def remove_user(self, username: str) -> bool:
        """Remove a user from the leaderboard."""
        username_lower = username.lower()
        if username_lower in self.users:
            del self.users[username_lower]
            self.save_data()
            print(f"🗑️ Removed {username} from leaderboard")
            return True
        else:
            print(f"❌ User {username} not found in leaderboard")
            return False
    
    def update_all_users(self) -> None:
        """Update stats for all users in the leaderboard."""
        print(f"🔄 Updating stats for {len(self.users)} users...")
        updated = 0
        
        for username in list(self.users.keys()):
            print(f"🔍 Updating {username}...")
            user_stats = get_user_stats(username)
            
            if user_stats:
                # Calculate time analytics
                user_stats["time_analytics"] = analyze_time_frames(
                    user_stats.get("submission_calendar", ""),
                    user_stats.get("recent_submissions", [])
                )
                
                self.users[username] = user_stats
                updated += 1
                print(f"   📊 {username}: Weekly {user_stats.get('weekly_base_score', 0)} | Total {user_stats.get('base_score', 0)}")
                time.sleep(1)  # Be nice to LeetCode's servers
            else:
                print(f"⚠️ Could not update {username}")
        
        self.save_data()
        print(f"✅ Updated {updated}/{len(self.users)} users")
    
    def update_user(self, username: str) -> bool:
        """Update stats for a specific user."""
        username_lower = username.lower()
        if username_lower not in self.users:
            print(f"❌ User {username} not in leaderboard")
            return False
        
        print(f"🔍 Updating {username}...")
        user_stats = get_user_stats(username)
        
        if user_stats:
            # Calculate time analytics
            user_stats["time_analytics"] = analyze_time_frames(
                user_stats.get("submission_calendar", ""),
                user_stats.get("recent_submissions", [])
            )
            
            self.users[username_lower] = user_stats
            self.save_data()
            print(f"✅ Updated {username}")
            print(f"📊 Weekly Score: {user_stats.get('weekly_base_score', 0)} pts")
            print(f"📈 Total Score: {user_stats.get('base_score', 0)} pts")
            return True
        else:
            print(f"❌ Could not update {username}")
            return False
    
    def get_leaderboard(self, sort_by: str = "weekly_base_score") -> List[Dict]:
        """
        Get sorted leaderboard data with weekly scoring support.
        
        Args:
            sort_by: Field to sort by (weekly_base_score, weekly_total, 
                    base_score, total_solved, easy, medium, hard, ranking)
            
        Returns:
            List of user data sorted by specified field
        """
        if not self.users:
            return []
        
        # Ensure all users have time analytics calculated
        for user_data in self.users.values():
            if 'time_analytics' not in user_data:
                user_data['time_analytics'] = analyze_time_frames(
                    user_data.get("submission_calendar", ""),
                    user_data.get("recent_submissions", [])
                )
        
        # Sort users by specified field (descending for scores/problems, ascending for ranking)
        reverse_sort = sort_by != "ranking"
        sorted_users = sorted(
            self.users.values(),
            key=lambda x: x.get(sort_by, 0),
            reverse=reverse_sort
        )
        
        # Add position numbers
        for i, user in enumerate(sorted_users, 1):
            user['position'] = i
            
        return sorted_users
    
    def display_leaderboard(self, sort_by: str = "weekly_base_score") -> None:
        """Display the weekly leaderboard with weekly scoring metrics."""
        leaderboard = self.get_leaderboard(sort_by)
        
        if not leaderboard:
            print("📊 No users in leaderboard yet!")
            print("   Use 'add <username>' to add friends")
            return
        
        # Get current week info
        week_start_ts, week_end_ts = get_current_week_bounds()
        week_start_date = datetime.fromtimestamp(week_start_ts).strftime("%b %d")
        week_end_date = datetime.fromtimestamp(week_end_ts).strftime("%b %d, %Y")
        
        # Header
        print("\n" + "="*130)
        print("🗓️ WEEKLY LEETCODE LEADERBOARD 🗓️".center(130))
        print(f"Week of {week_start_date} - {week_end_date}".center(130))
        print("="*130)
        
        # Sort indicator
        sort_names = {
            "weekly_base_score": "Weekly Score",
            "weekly_total": "Weekly Problems Solved",
            "base_score": "Total Score",
            "total_solved": "Total Problems Solved",
            "easy": "Total Easy Problems",
            "medium": "Total Medium Problems", 
            "hard": "Total Hard Problems",
            "ranking": "LeetCode Ranking"
        }
        print(f"Sorted by: {sort_names.get(sort_by, sort_by)}")
        print("-"*130)
        
        # Enhanced table header for weekly view
        print(f"{'Pos':<4} {'Username':<16} {'Week Score':<11} {'Week E/M/H':<12} "
              f"{'Total Score':<12} {'Total E/M/H':<12} {'Rank':<10} {'Activity':<12} {'Updated'}")
        print("-"*130)
        
        # User rows with weekly metrics
        for user in leaderboard:
            pos_emoji = "🥇" if user['position'] == 1 else "🥈" if user['position'] == 2 else "🥉" if user['position'] == 3 else f"{user['position']:2d}."
            
            # Weekly scores
            weekly_base_score = user.get('weekly_base_score', 0)
            
            # Weekly difficulty breakdown
            weekly_easy = user.get('weekly_easy', 0)
            weekly_medium = user.get('weekly_medium', 0) 
            weekly_hard = user.get('weekly_hard', 0)
            weekly_emh_str = f"{weekly_easy}/{weekly_medium}/{weekly_hard}"
            
            # Total scores and breakdown  
            total_base_score = user.get('base_score', 0)
            total_easy = user.get('easy', 0)
            total_medium = user.get('medium', 0)
            total_hard = user.get('hard', 0)
            total_emh_str = f"{total_easy}/{total_medium}/{total_hard}"
            
            # Format last updated
            try:
                last_updated = datetime.fromisoformat(user['last_updated'])
                time_str = last_updated.strftime("%m/%d")
            except:
                time_str = "Unknown"
            
            # Format ranking
            ranking_str = f"#{user['ranking']:,}" if user['ranking'] > 0 else "N/A"
            
            # Weekly activity indicator
            weekly_total = user.get('weekly_total', 0)
            if weekly_total >= 10:
                activity = "🔥 Very Active"
            elif weekly_total >= 5:
                activity = "✅ Active"
            elif weekly_total >= 1:
                activity = "⚡ Some"
            else:
                activity = "😴 Quiet"
            
            # Format scores for display
            week_score_str = f"{weekly_base_score:.0f}"
            total_score_str = f"{total_base_score:.0f}"
            
            print(f"{pos_emoji:<4} {user['username']:<16} {week_score_str:<11} {weekly_emh_str:<12} "
                  f"{total_score_str:<12} {total_emh_str:<12} {ranking_str:<10} {activity:<12} {time_str}")
        
        print("="*130)
        
        # Weekly statistics
        if leaderboard:
            leader = leaderboard[0]
            
            # Weekly stats
            total_weekly_problems = sum(user.get('weekly_total', 0) for user in leaderboard)
            total_weekly_score = sum(user.get('weekly_base_score', 0) for user in leaderboard)
            avg_weekly_score = total_weekly_score / len(leaderboard)
            
            # Overall stats
            total_problems = sum(user['total_solved'] for user in leaderboard)
            
            print(f"📊 This Week: {total_weekly_problems} problems solved | Avg weekly score: {avg_weekly_score:.1f}")
            print(f"🏆 Weekly Leader: {leader['username']} | Weekly Score: {leader.get('weekly_base_score', 0):.0f} | Weekly Problems: {leader.get('weekly_total', 0)}")
            
            # Weekly champions by difficulty
            weekly_easy_leader = max(leaderboard, key=lambda x: x.get('weekly_easy', 0))
            weekly_medium_leader = max(leaderboard, key=lambda x: x.get('weekly_medium', 0))
            weekly_hard_leader = max(leaderboard, key=lambda x: x.get('weekly_hard', 0))
            
            if weekly_easy_leader.get('weekly_easy', 0) > 0:
                print(f"🟢 Weekly Easy Champion: {weekly_easy_leader['username']} ({weekly_easy_leader.get('weekly_easy', 0)} problems)")
            if weekly_medium_leader.get('weekly_medium', 0) > 0:
                print(f"🟡 Weekly Medium Champion: {weekly_medium_leader['username']} ({weekly_medium_leader.get('weekly_medium', 0)} problems)")
            if weekly_hard_leader.get('weekly_hard', 0) > 0:
                print(f"🔴 Weekly Hard Champion: {weekly_hard_leader['username']} ({weekly_hard_leader.get('weekly_hard', 0)} problems)")
            
            print(f"📈 Total Problems Ever: {total_problems} | Total Users: {len(leaderboard)}")
            
        print("="*130)
    
    def display_user_details(self, username: str) -> None:
        """Display detailed stats for a specific user with advanced metrics."""
        username_lower = username.lower()
        if username_lower not in self.users:
            print(f"❌ User {username} not found in leaderboard")
            return
        
        user = self.users[username_lower]
        
        print("\n" + "="*80)
        print(f"👤 {user['username']} - Advanced Profile".center(80))
        print("="*80)
        
        if user.get('real_name'):
            print(f"Real Name: {user['real_name']}")
        
        # Scoring Information
        print("\n🎯 Scoring Metrics:")
        base_score = user.get('base_score', 0)
        weekly_score = user.get('weekly_base_score', 0)
        print(f"├─ Total Score: {base_score} pts (Easy×1 + Medium×3 + Hard×7)")
        print(f"└─ Weekly Score: {weekly_score} pts")
        
        # Problem Breakdown  
        print(f"\n📚 Problem Breakdown:")
        print(f"├─ Total Solved: {user['total_solved']}")
        print(f"├─ Easy: {user['easy']} (×1 = {user['easy']} pts)")
        print(f"├─ Medium: {user['medium']} (×3 = {user['medium'] * 3} pts)")
        print(f"└─ Hard: {user['hard']} (×7 = {user['hard'] * 7} pts)")
        
        if user['ranking'] > 0:
            print(f"\n🏅 LeetCode Ranking: #{user['ranking']:,}")
        
        # Time Analytics
        time_analytics = user.get('time_analytics', {})
        if time_analytics:
            print(f"\n⏰ Activity Analysis:")
            print(f"├─ Last 7 days: {time_analytics.get('daily_submissions', 0)} submissions")
            print(f"├─ Last 30 days: {time_analytics.get('weekly_submissions', 0)} submissions")
            print(f"├─ Last 365 days: {time_analytics.get('yearly_submissions', 0)} submissions")
            print(f"└─ Recent activity: {len(user.get('recent_submissions', []))} recent submissions")
        
        # Languages Used
        languages = user.get('languages', {})
        if languages:
            print(f"\n💻 Programming Languages:")
            sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
            for i, (lang, count) in enumerate(sorted_langs[:5]):  # Top 5 languages
                symbol = "├─" if i < len(sorted_langs[:5]) - 1 else "└─"
                print(f"{symbol} {lang}: {count} problems")
        
        # Topics/Tags
        topics = user.get('topics', {})
        if topics:
            print(f"\n🏷️ Top Problem Topics:")
            sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
            for i, (topic, count) in enumerate(sorted_topics[:5]):  # Top 5 topics
                symbol = "├─" if i < len(sorted_topics[:5]) - 1 else "└─"
                print(f"{symbol} {topic}: {count} problems")
        
        # Recent Submissions
        recent_subs = user.get('recent_submissions', [])
        if recent_subs:
            print(f"\n🕐 Recent Submissions ({len(recent_subs)}):")
            for i, sub in enumerate(recent_subs[:3]):  # Show last 3
                status_emoji = "✅" if sub.get('statusDisplay') == 'Accepted' else "❌"
                symbol = "├─" if i < min(len(recent_subs), 3) - 1 else "└─"
                print(f"{symbol} {status_emoji} {sub.get('title', 'Unknown')} ({sub.get('lang', 'N/A')})")
        
        # Progress bars
        if user['total_solved'] > 0:
            print("\n📊 Difficulty Distribution:")
            total = user['total_solved']
            easy_pct = (user['easy'] / total) * 100
            medium_pct = (user['medium'] / total) * 100
            hard_pct = (user['hard'] / total) * 100
            
            print(f"Easy   [{self._create_progress_bar(easy_pct, 30)}] {easy_pct:.1f}%")
            print(f"Medium [{self._create_progress_bar(medium_pct, 30)}] {medium_pct:.1f}%")
            print(f"Hard   [{self._create_progress_bar(hard_pct, 30)}] {hard_pct:.1f}%")
        
        try:
            last_updated = datetime.fromisoformat(user['last_updated'])
            print(f"\n🕒 Last Updated: {last_updated.strftime('%Y-%m-%d %H:%M:%S')}")
        except:
            print("\n🕒 Last Updated: Unknown")
            
        print("="*80)
    
    def _create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """Create a visual progress bar."""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return bar


def main():
    """Main application with command-line interface."""
    import sys
    
    # Check for batch mode (for GitHub Actions)
    if len(sys.argv) > 1 and '--update-all' in sys.argv and '--batch' in sys.argv:
        print("🔄 Running in batch mode for automation...")
        leaderboard = LeetCodeLeaderboard()
        leaderboard.update_all_users()
        return
    
    leaderboard = LeetCodeLeaderboard()
    
    print("🛝️ Welcome to Weekly LeetCode Leaderboard!")
    print("   Compare your weekly progress with friends")
    
    while True:
        print("\n" + "="*65)
        print("🏆 Weekly LeetCode Leaderboard Commands:")
        print("  add <username>     - Add a friend to weekly leaderboard")
        print("  remove <username>  - Remove a friend") 
        print("  update [username]  - Update weekly stats (all or specific user)")
        print("  show [sort_by]     - Show weekly leaderboard")
        print("  details <username> - Show detailed user stats")
        print("  list               - List all users")
        print("  help               - Show detailed help")
        print("  exit               - Exit program")
        print("="*65)
        
        try:
            command = input("\n💻 Enter command: ").strip().lower()
            
            if not command:
                continue
            
            parts = command.split()
            cmd = parts[0]
            
            if cmd == "exit" or cmd == "quit":
                print("👋 Goodbye! Keep solving those problems!")
                break
            
            elif cmd == "help":
                print("\n📖 Weekly LeetCode Leaderboard Help")
                print("="*55)
                print("🔧 User Management:")
                print("  add <username>     : Add a LeetCode user to weekly competition")
                print("  remove <username>  : Remove a user from leaderboard")  
                print("  update             : Update all users' weekly stats")
                print("  update <username>  : Update specific user's weekly stats")
                print("\n📊 Weekly Leaderboard Views:")
                print("  show               : Display weekly leaderboard (sorted by weekly score)")
                print("  show weekly        : Sort by weekly advanced score (default)")
                print("  show weekly_base   : Sort by weekly base score")
                print("  show weekly_total  : Sort by weekly problems solved")
                print("  show total         : Sort by total problems solved")
                print("  show score         : Sort by total advanced score")
                print("  show easy          : Sort by total easy problems")
                print("  show medium        : Sort by total medium problems") 
                print("  show hard          : Sort by total hard problems")
                print("  show ranking       : Sort by LeetCode ranking")
                print("\n🔍 Analysis:")
                print("  details <username> : Show detailed stats for a user")
                print("  list               : List all users in leaderboard")
                print("\n🎯 Weekly Scoring System:")
                print("  • Easy problems = 1 point each")
                print("  • Medium problems = 3 points each")
                print("  • Hard problems = 7 points each")
                print("  • Weekly score = Problems solved THIS WEEK only")
                print("  • Pure difficulty-based scoring (no multipliers)")
                print("  • Competition resets every Monday!")
                print("\n📅 Current Week: Monday to Sunday scoring period")
            
            elif cmd == "add":
                if len(parts) < 2:
                    print("❌ Please specify a username: add <username>")
                else:
                    username = parts[1]
                    leaderboard.add_user(username)
            
            elif cmd == "remove":
                if len(parts) < 2:
                    print("❌ Please specify a username: remove <username>")
                else:
                    username = parts[1]
                    leaderboard.remove_user(username)
            
            elif cmd == "update":
                if len(parts) == 1:
                    leaderboard.update_all_users()
                else:
                    username = parts[1]
                    leaderboard.update_user(username)
            
            elif cmd == "show":
                sort_by = "weekly_base_score"  # Default to weekly base score
                if len(parts) > 1:
                    sort_options = {
                        "weekly": "weekly_base_score",
                        "weekly_base": "weekly_base_score", 
                        "weekly_total": "weekly_total",
                        "score": "base_score",
                        "base": "base_score",
                        "easy": "easy",
                        "medium": "medium", 
                        "hard": "hard",
                        "ranking": "ranking",
                        "total": "total_solved"
                    }
                    sort_by = sort_options.get(parts[1], "weekly_base_score")
                
                leaderboard.display_leaderboard(sort_by)
            
            elif cmd == "details":
                if len(parts) < 2:
                    print("❌ Please specify a username: details <username>")
                else:
                    username = parts[1]
                    leaderboard.display_user_details(username)
            
            elif cmd == "list":
                users = list(leaderboard.users.keys())
                if users:
                    print(f"\n👥 Users in leaderboard ({len(users)}):")
                    for i, username in enumerate(users, 1):
                        user_data = leaderboard.users[username]
                        print(f"  {i}. {user_data['username']} ({user_data['total_solved']} problems)")
                else:
                    print("📊 No users in leaderboard yet!")
            
            else:
                print(f"❌ Unknown command: {cmd}")
                print("   Type 'help' for available commands")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"💥 Error: {e}")
            print("   Please try again")


if __name__ == "__main__":
    main()
