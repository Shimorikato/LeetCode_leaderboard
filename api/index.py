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
                recentSubmissionList(limit: 20) {
                    title
                    titleSlug
                    timestamp
                    statusDisplay
                    lang
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

    def calculate_weekly_problems(submission_calendar, recent_submissions):
        """Calculate problems solved in the current week."""
        week_start_ts, week_end_ts = get_current_week_bounds()
        
        # Parse submission calendar
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
        
        # Also check recent submissions for this week
        recent_weekly = 0
        if recent_submissions:
            for submission in recent_submissions:
                try:
                    submission_ts = int(submission.get('timestamp', 0))
                    if week_start_ts <= submission_ts <= week_end_ts:
                        recent_weekly += 1
                except:
                    continue
        
        # Use the higher count (calendar data is usually more accurate)
        return max(weekly_submissions, recent_weekly)

    def calculate_advanced_score(easy: int, medium: int, hard: int, ranking: int, recent_activity: int) -> float:
        """Calculate advanced score with performance multipliers."""
        base_score = easy * 1 + medium * 3 + hard * 7
        
        if base_score == 0:
            return 0.0
        
        # Ranking multiplier (better ranking = higher multiplier)
        if ranking <= 0:
            ranking_multiplier = 1.0
        elif ranking <= 1000:
            ranking_multiplier = 2.0
        elif ranking <= 5000:
            ranking_multiplier = 1.8
        elif ranking <= 10000:
            ranking_multiplier = 1.6
        elif ranking <= 50000:
            ranking_multiplier = 1.4
        elif ranking <= 100000:
            ranking_multiplier = 1.2
        else:
            ranking_multiplier = 1.0
        
        # Activity multiplier (more recent activity = higher multiplier)
        if recent_activity >= 10:
            activity_multiplier = 1.5
        elif recent_activity >= 5:
            activity_multiplier = 1.3
        elif recent_activity >= 2:
            activity_multiplier = 1.1
        else:
            activity_multiplier = 1.0
        
        return base_score * ranking_multiplier * activity_multiplier

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
                
                # Parse difficulty stats
                easy = medium = hard = 0
                for stat in submit_stats:
                    difficulty = stat.get("difficulty", "").lower()
                    count = stat.get("count", 0)
                    
                    if difficulty == "easy":
                        easy = count
                    elif difficulty == "medium":
                        medium = count
                    elif difficulty == "hard":
                        hard = count
                
                total_solved = easy + medium + hard
                
                # Get additional data
                profile = user_data.get("profile", {})
                ranking = profile.get("ranking", 0) or 0
                recent_submissions = user_data.get("recentSubmissionList", [])
                submission_calendar = user_data.get("submissionCalendar", "{}")
                
                # Calculate weekly stats
                weekly_total = calculate_weekly_problems(submission_calendar, recent_submissions)
                
                # Estimate weekly breakdown (proportional to total)
                if total_solved > 0:
                    easy_ratio = easy / total_solved
                    medium_ratio = medium / total_solved
                    hard_ratio = hard / total_solved
                    
                    weekly_easy = int(weekly_total * easy_ratio)
                    weekly_medium = int(weekly_total * medium_ratio)
                    weekly_hard = weekly_total - weekly_easy - weekly_medium
                else:
                    weekly_easy = weekly_medium = weekly_hard = 0
                
                # Calculate scores
                base_score = easy * 1 + medium * 3 + hard * 7
                advanced_score = calculate_advanced_score(easy, medium, hard, ranking, len(recent_submissions))
                
                weekly_base_score = weekly_easy * 1 + weekly_medium * 3 + weekly_hard * 7
                weekly_advanced_score = calculate_advanced_score(weekly_easy, weekly_medium, weekly_hard, ranking, weekly_total)
                
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

# This is required for Vercel
app = app