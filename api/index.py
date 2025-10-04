from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
import os
import sys
from datetime import datetime, timedelta
import requests

# Add the parent directory to the path so we can import our modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import or define the functions we need
try:
    from leetcode_leaderboard import LeetCodeLeaderboard, get_user_stats, calculate_advanced_score
except ImportError:
    # Define the functions directly if import fails
    def get_current_week_bounds():
        """Get the start and end timestamps for the current week (Monday to Sunday)."""
        now = datetime.now()
        days_since_monday = now.weekday()  # Monday is 0, Sunday is 6
        
        # Calculate start of week (Monday 00:00:00)
        week_start = now - timedelta(days=days_since_monday, 
                                   hours=now.hour, 
                                   minutes=now.minute, 
                                   seconds=now.second, 
                                   microseconds=now.microsecond)
        
        # Calculate end of week (Sunday 23:59:59)  
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        return int(week_start.timestamp()), int(week_end.timestamp())

    def get_user_stats(username: str):
        """Fetch user statistics from LeetCode GraphQL API."""
        url = "https://leetcode.com/graphql"
        
        query = """
        query getUserStats($username: String!) {
            allQuestionsCount {
                difficulty
                count
            }
            matchedUser(username: $username) {
                username
                submitStats {
                    acSubmissionNum {
                        difficulty
                        count
                    }
                    totalSubmissionNum {
                        difficulty
                        count
                    }
                }
                profile {
                    ranking
                    realName
                    aboutMe
                    userAvatar
                    reputation
                    githubUrl
                    websites
                }
                submissionCalendar
                recentSubmissionList(limit: 50) {
                    title
                    titleSlug
                    timestamp
                    statusDisplay
                    lang
                    __typename
                }
                recentAcSubmissionList(limit: 50) {
                    id
                    title
                    titleSlug
                    timestamp
                }
            }
        }
        """
        
        variables = {"username": username}
        headers = {
            "Content-Type": "application/json",
            "Referer": "https://leetcode.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        try:
            response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                return None
                
            return data.get("data")
        except Exception as e:
            print(f"Error fetching data for {username}: {e}")
            return None

    def get_problem_difficulty(title_slug):
        """Get the difficulty of a specific problem from LeetCode API."""
        url = "https://leetcode.com/graphql"
        query = """
        query questionData($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                difficulty
                title
            }
        }
        """
        
        try:
            response = requests.post(url, json={
                "query": query, 
                "variables": {"titleSlug": title_slug}
            }, headers={
                "Content-Type": "application/json",
                "Referer": "https://leetcode.com"
            })
            
            if response.status_code == 200:
                data = response.json()
                question = data.get('data', {}).get('question', {})
                return question.get('difficulty', 'Medium').lower()
        except:
            pass
        
        # Default fallback
        return 'medium'
    
    def calculate_weekly_problems_accurate(recent_submissions, submission_calendar):
        """Calculate problems solved in the current week with difficulty breakdown."""
        week_start_ts, week_end_ts = get_current_week_bounds()
        
        # Track unique problems solved this week with their difficulties
        weekly_problems = {}  # title_slug -> difficulty
        
        if recent_submissions:
            for submission in recent_submissions:
                try:
                    submission_ts = int(submission.get('timestamp', 0))
                    status = submission.get('statusDisplay', '')
                    title_slug = submission.get('titleSlug', '')
                    
                    # Only count accepted submissions in current week
                    if (week_start_ts <= submission_ts <= week_end_ts and 
                        status == 'Accepted' and title_slug):
                        
                        # Avoid duplicate API calls
                        if title_slug not in weekly_problems:
                            difficulty = get_problem_difficulty(title_slug)
                            weekly_problems[title_slug] = difficulty
                except:
                    continue
        
        # Count by difficulty
        weekly_easy = sum(1 for d in weekly_problems.values() if d == 'easy')
        weekly_medium = sum(1 for d in weekly_problems.values() if d == 'medium')
        weekly_hard = sum(1 for d in weekly_problems.values() if d == 'hard')
        weekly_total = len(weekly_problems)
        
        # Fallback if no recent submissions found
        if weekly_total == 0:
            calendar_data = {}
            try:
                if submission_calendar:
                    calendar_data = json.loads(submission_calendar)
            except:
                calendar_data = {}
            
            # Count submissions in current week from calendar
            weekly_submissions = 0
            current_ts = week_start_ts
            while current_ts <= week_end_ts:
                date_key = str(current_ts)
                weekly_submissions += calendar_data.get(date_key, 0)
                current_ts += 86400  # Add one day in seconds
            
            # Rough estimate with typical difficulty distribution
            estimated_problems = int(weekly_submissions * 0.7)  # 70% acceptance rate
            weekly_easy = int(estimated_problems * 0.5)    # 50% easy
            weekly_medium = int(estimated_problems * 0.4)  # 40% medium  
            weekly_hard = estimated_problems - weekly_easy - weekly_medium  # 10% hard
            weekly_total = estimated_problems
        
        return {
            'total': weekly_total,
            'easy': weekly_easy,
            'medium': weekly_medium,
            'hard': weekly_hard
        }

    def calculate_advanced_score(easy: int, medium: int, hard: int, ranking: int, recent_activity: int) -> float:
        """Calculate score based purely on difficulty and number of questions."""
        # Simple scoring: Easy=1, Medium=3, Hard=7 (no multipliers)
        score = easy * 1 + medium * 3 + hard * 7
        
        # Debug output
        print(f"Debug - Score calculation: Easy={easy}×1 + Medium={medium}×3 + Hard={hard}×7 = {score}")
        
        return float(score)

    class LeetCodeLeaderboard:
        """A LeetCode leaderboard to track and compare friend's progress."""
        
        def __init__(self, data_file: str = "leaderboard_data.json"):
            self.data_file = data_file
            self.users = {}
            # In serverless environment, we'll use environment variables or start fresh
            self.load_data()
        
        def load_data(self) -> None:
            """Load existing user data from JSON file or environment."""
            try:
                import os
                import base64
                
                # Try to load from base64 encoded environment variable first
                encoded_data = os.environ.get('LEADERBOARD_DATA_B64')
                if encoded_data:
                    try:
                        decoded_data = base64.b64decode(encoded_data).decode('utf-8')
                        self.users = json.loads(decoded_data)
                        print(f"Loaded {len(self.users)} users from environment variables")
                        return
                    except Exception as e:
                        print(f"Error decoding environment data: {e}")
                
                # Try to load from plain JSON environment variable
                data_str = os.environ.get('LEADERBOARD_DATA')
                if data_str:
                    self.users = json.loads(data_str)
                    print(f"Loaded {len(self.users)} users from JSON environment variable")
                    return
                
                # Try to load from file (might not work in serverless)
                with open(self.data_file, 'r') as f:
                    self.users = json.load(f)
                    print(f"Loaded {len(self.users)} users from local file")
            except (FileNotFoundError, json.JSONDecodeError, PermissionError):
                # Start with empty data in serverless environment
                print("Starting with empty leaderboard")
                self.users = {}
        
        def save_data(self) -> None:
            """Save current user data to JSON file."""
            try:
                # Try to save to local file (works locally, fails in serverless)
                with open(self.data_file, 'w') as f:
                    json.dump(self.users, f, indent=2)
                print(f"Saved {len(self.users)} users to local file")
            except Exception as e:
                # In serverless environment, we can't persist files
                # Data will be lost between requests unless stored in external database
                print(f"Cannot save to file in serverless environment: {e}")
                print("Note: Data will be lost between requests. Use environment variables or database for persistence.")
        
        def add_user(self, username: str) -> bool:
            """Add a new user to the leaderboard."""
            try:
                data = get_user_stats(username)
                if not data or not data.get("matchedUser"):
                    return False
                
                user_data = data["matchedUser"]
                submit_stats = user_data.get("submitStats", {}).get("acSubmissionNum", [])
                
                # Parse difficulty stats with better error handling
                easy = medium = hard = 0
                
                print(f"Debug - Submit stats for {username}: {submit_stats}")
                
                for stat in submit_stats:
                    difficulty = stat.get("difficulty", "").strip().lower()
                    count = int(stat.get("count", 0))
                    
                    print(f"Debug - Processing: difficulty='{difficulty}', count={count}")
                    
                    if difficulty == "easy":
                        easy = count
                    elif difficulty == "medium":
                        medium = count
                    elif difficulty == "hard":
                        hard = count
                    else:
                        print(f"Warning: Unknown difficulty '{difficulty}' with count {count}")
                
                print(f"Debug - Final counts for {username}: Easy={easy}, Medium={medium}, Hard={hard}")
                
                total_solved = easy + medium + hard
                
                # Get additional data
                profile = user_data.get("profile", {})
                ranking = profile.get("ranking", 0) or 0
                recent_submissions = user_data.get("recentSubmissionList", [])
                submission_calendar = user_data.get("submissionCalendar", "{}")
                
                # Calculate accurate weekly stats with proper difficulty detection
                weekly_stats = calculate_weekly_problems_accurate(recent_submissions, submission_calendar)
                weekly_total = weekly_stats['total']
                weekly_easy = weekly_stats['easy']
                weekly_medium = weekly_stats['medium']
                weekly_hard = weekly_stats['hard']
                
                # Calculate scores (simple difficulty-based scoring)
                base_score = easy * 1 + medium * 3 + hard * 7
                advanced_score = calculate_advanced_score(easy, medium, hard, 0, 0)  # Pure difficulty scoring
                
                weekly_base_score = weekly_easy * 1 + weekly_medium * 3 + weekly_hard * 7
                weekly_advanced_score = calculate_advanced_score(weekly_easy, weekly_medium, weekly_hard, 0, 0)  # Pure difficulty scoring
                
                # Store user data
                user_info = {
                    "username": user_data.get("username", username),
                    "total_solved": total_solved,
                    "easy": easy,
                    "medium": medium,
                    "hard": hard,
                    "base_score": base_score,
                    "advanced_score": advanced_score,
                    "weekly_total": weekly_total,
                    "weekly_easy": weekly_easy,
                    "weekly_medium": weekly_medium,
                    "weekly_hard": weekly_hard,
                    "weekly_base_score": weekly_base_score,
                    "weekly_advanced_score": weekly_advanced_score,
                    "ranking": ranking,
                    "last_updated": datetime.now().isoformat(),
                    "recent_submissions": recent_submissions[:10]
                }
                
                self.users[username.lower()] = user_info
                self.save_data()
                return True
                
            except Exception as e:
                print(f"Error adding user {username}: {e}")
                return False
        
        def get_leaderboard(self, sort_by: str = "weekly_advanced_score"):
            """Get sorted leaderboard data."""
            if not self.users:
                return []
            
            # Convert to list and add positions
            leaderboard = []
            for user_data in self.users.values():
                leaderboard.append(dict(user_data))
            
            # Sort by specified field
            reverse_sort = True
            if sort_by == "ranking":
                reverse_sort = False
                # Handle 0 rankings (put them at the end)
                leaderboard.sort(key=lambda x: x.get(sort_by, float('inf') if reverse_sort else 0), reverse=reverse_sort)
            else:
                leaderboard.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse_sort)
            
            # Add positions
            for i, user in enumerate(leaderboard):
                user['position'] = i + 1
            
            return leaderboard

def update_vercel_env_var(token: str, project_id: str, key: str, value: str) -> bool:
    """Update Vercel environment variable."""
    try:
        # First, try to delete existing variable
        delete_vercel_env_var(token, project_id, key)
        
        # Create new variable
        url = f"https://api.vercel.com/v9/projects/{project_id}/env"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "key": key,
            "value": value,
            "type": "encrypted",
            "target": ["production", "preview", "development"]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return True
        
    except Exception as e:
        print(f"Error updating Vercel env var: {e}")
        return False

def delete_vercel_env_var(token: str, project_id: str, key: str):
    """Delete existing Vercel environment variable."""
    try:
        # Get existing environment variables
        url = f"https://api.vercel.com/v9/projects/{project_id}/env"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        env_vars = response.json()
        
        # Find and delete existing variable
        for env_var in env_vars.get('envs', []):
            if env_var.get('key') == key:
                env_id = env_var.get('id')
                delete_url = f"https://api.vercel.com/v9/projects/{project_id}/env/{env_id}"
                
                delete_response = requests.delete(delete_url, headers=headers, timeout=10)
                delete_response.raise_for_status()
                print(f"🗑️ Deleted old environment variable: {key}")
                break
                
    except Exception:
        pass  # Ignore deletion errors

app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')
app.secret_key = 'leetcode_leaderboard_secret_key_2025'

# Add error handling
@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong on our end'
    }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404

# Global leaderboard instance
try:
    leaderboard = LeetCodeLeaderboard("web_leaderboard_data.json")
except Exception as e:
    print(f"Error initializing leaderboard: {e}")
    leaderboard = LeetCodeLeaderboard("web_leaderboard_data.json")

@app.route('/test')
def test():
    """Test route to verify the app is working."""
    return jsonify({
        'status': 'OK',
        'message': 'Weekly LeetCode Leaderboard API is working!',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/')
def index():
    """Main weekly leaderboard page."""
    try:
        sort_by = request.args.get('sort_by', 'weekly_advanced_score')
        leaderboard_data = leaderboard.get_leaderboard(sort_by)
        
        # Calculate summary stats including weekly metrics
        stats = {}
        if leaderboard_data:
            # Weekly stats
            total_weekly_problems = sum(user.get('weekly_total', 0) for user in leaderboard_data)
            total_weekly_score = sum(user.get('weekly_advanced_score', 0) for user in leaderboard_data)
            avg_weekly_score = total_weekly_score / len(leaderboard_data) if leaderboard_data else 0
            
            # Overall stats
            stats = {
                'total_users': len(leaderboard_data),
                'total_problems': sum(user.get('total_solved', 0) for user in leaderboard_data),
                'weekly_problems': total_weekly_problems,
                'weekly_score': total_weekly_score,
                'avg_weekly_score': avg_weekly_score,
                'total_advanced_score': sum(user.get('advanced_score', 0) for user in leaderboard_data),
                'avg_score': sum(user.get('advanced_score', 0) for user in leaderboard_data) / len(leaderboard_data) if leaderboard_data else 0,
                'leader': leaderboard_data[0] if leaderboard_data else None,
                'easy_champion': max(leaderboard_data, key=lambda x: x.get('easy', 0)) if leaderboard_data else None,
                'medium_champion': max(leaderboard_data, key=lambda x: x.get('medium', 0)) if leaderboard_data else None,
                'hard_champion': max(leaderboard_data, key=lambda x: x.get('hard', 0)) if leaderboard_data else None,
                # Weekly champions
                'weekly_easy_champion': max(leaderboard_data, key=lambda x: x.get('weekly_easy', 0)) if leaderboard_data else None,
                'weekly_medium_champion': max(leaderboard_data, key=lambda x: x.get('weekly_medium', 0)) if leaderboard_data else None,
                'weekly_hard_champion': max(leaderboard_data, key=lambda x: x.get('weekly_hard', 0)) if leaderboard_data else None
            }
        
        return render_template('index.html', 
                             leaderboard=leaderboard_data, 
                             stats=stats, 
                             current_sort=sort_by)
    except Exception as e:
        # Return a simple HTML page with error for debugging
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Weekly LeetCode Leaderboard - Error</title></head>
        <body>
            <h1>Weekly LeetCode Leaderboard</h1>
            <h2>Temporarily Unavailable</h2>
            <p><strong>Error:</strong> {str(e)}</p>
            <p><a href="/test">Test API Status</a></p>
            <p>Please try again later or contact support.</p>
        </body>
        </html>
        """, 500

@app.route('/user/<username>')
def user_details(username):
    """User details page."""
    username_lower = username.lower()
    if username_lower not in leaderboard.users:
        flash(f"User {username} not found in leaderboard", "error")
        return redirect(url_for('index'))
    
    user_data = leaderboard.users[username_lower]
    
    # Calculate additional metrics for display
    total_solved = user_data.get('total_solved', 0)
    if total_solved > 0:
        user_data['easy_percentage'] = (user_data.get('easy', 0) / total_solved) * 100
        user_data['medium_percentage'] = (user_data.get('medium', 0) / total_solved) * 100
        user_data['hard_percentage'] = (user_data.get('hard', 0) / total_solved) * 100
    else:
        user_data['easy_percentage'] = user_data['medium_percentage'] = user_data['hard_percentage'] = 0
    
    return render_template('user_details.html', user=user_data, username=username)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """Add user page and form submission."""
    if request.method == 'POST':
        # Handle form submission
        try:
            username = request.form.get('username', '').strip()
            if not username:
                flash('Username is required', 'error')
                return redirect(url_for('add_user'))
            
            success = leaderboard.add_user(username)
            if success:
                flash(f'User {username} added successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash(f'Failed to add user {username}. Please check the username.', 'error')
                return redirect(url_for('add_user'))
        
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('add_user'))
    
    # Handle GET request - show the form
    try:
        return render_template('add_user.html')
    except Exception as e:
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Add User - Weekly LeetCode Leaderboard</title></head>
        <body>
            <h1>Add User</h1>
            <form method="POST">
                <input type="text" name="username" placeholder="LeetCode Username" required>
                <button type="submit">Add User</button>
            </form>
            <p><a href="/">Back to Leaderboard</a></p>
        </body>
        </html>
        """

@app.route('/api/add_user', methods=['POST'])
def api_add_user():
    """API endpoint to add a new user."""
    try:
        # Handle both JSON and form data
        if request.is_json:
            username = request.json.get('username', '').strip()
        else:
            username = request.form.get('username', '').strip()
        
        if not username:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Username is required'}), 400
            else:
                return redirect(url_for('index'))
        
        success = leaderboard.add_user(username)
        if success:
            if request.is_json:
                return jsonify({'success': True, 'message': f'User {username} added successfully!'})
            else:
                flash(f'User {username} added successfully!', 'success')
                return redirect(url_for('index'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'message': f'Failed to add user {username}. Please check the username.'}), 400
            else:
                flash(f'Failed to add user {username}. Please check the username.', 'error')
                return redirect(url_for('index'))
    
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
        else:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('index'))

@app.route('/api/refresh_user/<username>', methods=['POST'])
def api_refresh_user(username):
    """API endpoint to refresh a user's data."""
    try:
        success = leaderboard.add_user(username)  # This updates existing users
        if success:
            return jsonify({'success': True, 'message': f'User {username} refreshed successfully!'})
        else:
            return jsonify({'success': False, 'message': f'Failed to refresh user {username}'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/update_all')
def update_all():
    """Update all users page/redirect."""
    try:
        updated_count = 0
        failed_users = []
        
        for username in leaderboard.users.keys():
            success = leaderboard.add_user(username)
            if success:
                updated_count += 1
            else:
                failed_users.append(username)
        
        message = f'Updated {updated_count} users successfully!'
        if failed_users:
            message += f' Failed to update: {", ".join(failed_users)}'
        
        flash(message, 'success' if not failed_users else 'warning')
        return redirect(url_for('index'))
    
    except Exception as e:
        flash(f'Error updating users: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/refresh_all', methods=['POST'])
def api_refresh_all():
    """API endpoint to refresh all users' data."""
    try:
        updated_count = 0
        failed_users = []
        
        for username in leaderboard.users.keys():
            success = leaderboard.add_user(username)
            if success:
                updated_count += 1
            else:
                failed_users.append(username)
        
        result = {
            'success': True,
            'updated_count': updated_count,
            'total_users': len(leaderboard.users),
            'message': f'Updated {updated_count} users successfully!'
        }
        
        if failed_users:
            result['failed_users'] = failed_users
            result['message'] += f' Failed to update: {", ".join(failed_users)}'
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/live-data')
def api_live_data():
    """API endpoint to get fresh LeetCode data - refreshes on every call and saves to JSON files."""
    try:
        # Get all existing usernames from the leaderboard instead of hardcoded list
        global leaderboard
        
        # Get all usernames from existing data
        usernames = list(leaderboard.users.keys()) if leaderboard.users else []
        
        if not usernames:
            return jsonify({
                'success': False,
                'message': 'No users found in leaderboard',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        # Fetch fresh data for each user and save to files
        updated_users = []
        failed_users = []
        
        for username in usernames:
            print(f"Fetching fresh data for {username}...")
            success = leaderboard.add_user(username)  # This will save to both JSON files
            if success:
                updated_users.append(username)
                print(f"✅ Updated {username}")
            else:
                failed_users.append(username)
                print(f"❌ Failed to update {username}")
        
        # Force save to ensure data is persisted
        leaderboard.save_data()
        
        # Trigger GitHub Action to update repository files
        try:
            github_token = os.environ.get('GITHUB_TOKEN')
            if github_token:
                print("🔄 Triggering GitHub Action to update repository...")
                
                # Trigger repository_dispatch event
                dispatch_url = "https://api.github.com/repos/Shimorikato/LeetCode_leaderboard/dispatches"
                headers = {
                    "Authorization": f"Bearer {github_token}",
                    "Accept": "application/vnd.github.v3+json",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "event_type": "update-leaderboard",
                    "client_payload": {
                        "updated_users": updated_users,
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                response = requests.post(dispatch_url, headers=headers, json=payload, timeout=10)
                if response.status_code == 204:
                    print("✅ GitHub Action triggered successfully")
                else:
                    print(f"⚠️ GitHub Action trigger failed: {response.status_code}")
            else:
                print("ℹ️ GitHub token not available, skipping repository update")
                
        except Exception as github_error:
            print(f"⚠️ GitHub Action trigger failed: {github_error}")
        
        # Update Vercel environment variable if tokens are available
        try:
            import base64
            vercel_token = os.environ.get('VERCEL_TOKEN')
            project_id = os.environ.get('VERCEL_PROJECT_ID')
            
            if vercel_token and project_id:
                print("🔄 Updating Vercel environment variable...")
                
                # Encode the fresh data
                json_str = json.dumps(leaderboard.users, separators=(',', ':'))
                encoded_data = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
                
                # Update Vercel environment variable
                update_success = update_vercel_env_var(vercel_token, project_id, 'LEADERBOARD_DATA_B64', encoded_data)
                if update_success:
                    print("✅ Vercel environment variable updated successfully")
                else:
                    print("⚠️ Failed to update Vercel environment variable")
            else:
                print("ℹ️ Vercel credentials not available, skipping environment update")
                
        except Exception as vercel_error:
            print(f"⚠️ Vercel update failed: {vercel_error}")
        
        # Get the updated leaderboard data
        leaderboard_data = leaderboard.get_leaderboard('weekly_base_score')
        
        # Calculate summary stats
        stats = {}
        if leaderboard_data:
            total_weekly_problems = sum(user.get('weekly_total', 0) for user in leaderboard_data)
            total_weekly_score = sum(user.get('weekly_base_score', 0) for user in leaderboard_data)
            avg_weekly_score = total_weekly_score / len(leaderboard_data) if leaderboard_data else 0
            
            stats = {
                'total_users': len(leaderboard_data),
                'total_problems': sum(user.get('total_solved', 0) for user in leaderboard_data),
                'weekly_problems': total_weekly_problems,
                'weekly_score': total_weekly_score,
                'avg_weekly_score': round(avg_weekly_score, 1),
                'leader': leaderboard_data[0] if leaderboard_data else None,
                'last_updated': datetime.now().isoformat()
            }
        
        return jsonify({
            'success': True,
            'leaderboard': leaderboard_data,
            'stats': stats,
            'updated_users': updated_users,
            'failed_users': failed_users,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error in live data endpoint: {e}")
        return jsonify({
            'success': False, 
            'message': f'Error fetching live data: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/trigger-update', methods=['POST'])
def api_trigger_github_update():
    """API endpoint to trigger GitHub Action workflow for leaderboard update."""
    try:
        # Check if GitHub token is available
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            return jsonify({
                'success': False,
                'message': 'GitHub token not configured. Update will happen automatically every 2 hours.',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        print("🚀 Manual trigger: Starting GitHub Action workflow...")
        
        # Trigger repository_dispatch event to start the workflow
        dispatch_url = "https://api.github.com/repos/Shimorikato/LeetCode_leaderboard/dispatches"
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        payload = {
            "event_type": "update-leaderboard",
            "client_payload": {
                "trigger": "manual_button",
                "timestamp": datetime.now().isoformat(),
                "source": "vercel_refresh_button"
            }
        }
        
        response = requests.post(dispatch_url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 204:
            print("✅ GitHub Action workflow triggered successfully!")
            return jsonify({
                'success': True,
                'message': 'GitHub Action triggered! Leaderboard data will be updated in ~2-3 minutes.',
                'timestamp': datetime.now().isoformat(),
                'workflow_status': 'triggered'
            })
        else:
            print(f"❌ GitHub Action trigger failed: {response.status_code} - {response.text}")
            return jsonify({
                'success': False,
                'message': f'Failed to trigger GitHub Action: HTTP {response.status_code}',
                'timestamp': datetime.now().isoformat(),
                'error_details': response.text
            }), 500
            
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'message': 'Request timed out. Please try again.',
            'timestamp': datetime.now().isoformat()
        }), 408
        
    except Exception as e:
        print(f"Error triggering GitHub Action: {e}")
        return jsonify({
            'success': False,
            'message': f'Error triggering update: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/refresh_all', methods=['POST'])
def api_refresh_all_old():
    """API endpoint to refresh all users' data."""
    try:
        updated_count = 0
        failed_users = []
        
        for username in leaderboard.users.keys():
            success = leaderboard.add_user(username)
            if success:
                updated_count += 1
            else:
                failed_users.append(username)
        
        message = f'Updated {updated_count} users successfully!'
        if failed_users:
            message += f' Failed to update: {", ".join(failed_users)}'
        
        return jsonify({
            'success': True, 
            'message': message,
            'updated_count': updated_count,
            'failed_users': failed_users
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/remove_user/<username>')
def remove_user(username):
    """Remove user route."""
    try:
        username_lower = username.lower()
        if username_lower in leaderboard.users:
            del leaderboard.users[username_lower]
            leaderboard.save_data()
            flash(f'User {username} removed successfully!', 'success')
        else:
            flash(f'User {username} not found', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error removing user: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/update_user/<username>')
def update_user_route(username):
    """Update specific user route."""
    try:
        success = leaderboard.add_user(username)
        if success:
            flash(f'User {username} updated successfully!', 'success')
        else:
            flash(f'Failed to update user {username}', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error updating user: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/remove_user/<username>', methods=['DELETE'])
def api_remove_user(username):
    """API endpoint to remove a user."""
    try:
        username_lower = username.lower()
        if username_lower in leaderboard.users:
            del leaderboard.users[username_lower]
            leaderboard.save_data()
            return jsonify({'success': True, 'message': f'User {username} removed successfully!'})
        else:
            return jsonify({'success': False, 'message': f'User {username} not found'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/leaderboard')
def api_leaderboard():
    """API endpoint to get leaderboard data."""
    try:
        sort_by = request.args.get('sort_by', 'weekly_advanced_score')
        leaderboard_data = leaderboard.get_leaderboard(sort_by)
        return jsonify({'success': True, 'data': leaderboard_data})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/api/debug')
def debug_env():
    """Debug endpoint to check environment variables and data loading."""
    import base64
    
    debug_info = {
        'env_var_exists': 'LEADERBOARD_DATA_B64' in os.environ,
        'env_var_length': len(os.environ.get('LEADERBOARD_DATA_B64', '')),
        'users_count': len(leaderboard.users),
        'users_list': list(leaderboard.users.keys()),
        'sample_user_data': {}
    }
    
    # Get sample data from first user if exists
    if leaderboard.users:
        first_user = list(leaderboard.users.keys())[0]
        user_data = leaderboard.users[first_user]
        debug_info['sample_user_data'] = {
            'username': user_data.get('username'),
            'total_score': user_data.get('base_score', 0),
            'weekly_score': user_data.get('weekly_base_score', 0),
            'last_updated': user_data.get('last_updated')
        }
    
    # Try to decode env var
    if debug_info['env_var_exists']:
        try:
            encoded_data = os.environ.get('LEADERBOARD_DATA_B64')
            decoded_data = base64.b64decode(encoded_data).decode('utf-8')
            decoded_json = json.loads(decoded_data)
            debug_info['env_decode_success'] = True
            debug_info['env_users_count'] = len(decoded_json)
            debug_info['env_users_list'] = list(decoded_json.keys())
        except Exception as e:
            debug_info['env_decode_success'] = False
            debug_info['env_decode_error'] = str(e)
    
    return jsonify(debug_info)


# This is required for Vercel
app = app