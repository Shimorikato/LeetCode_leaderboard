from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
from datetime import datetime
from leetcode_leaderboard import LeetCodeLeaderboard, get_user_stats

app = Flask(__name__)
app.secret_key = 'leetcode_leaderboard_secret_key_2025'

# Global leaderboard instance
leaderboard = LeetCodeLeaderboard("web_leaderboard_data.json")

@app.route('/')
def index():
    """Main weekly leaderboard page."""
    sort_by = request.args.get('sort_by', 'weekly_base_score')
    leaderboard_data = leaderboard.get_leaderboard(sort_by)
    
    # Calculate summary stats including weekly metrics
    stats = {}
    if leaderboard_data:
        # Weekly stats
        total_weekly_problems = sum(user.get('weekly_total', 0) for user in leaderboard_data)
        total_weekly_score = sum(user.get('weekly_base_score', 0) for user in leaderboard_data)
        avg_weekly_score = total_weekly_score / len(leaderboard_data) if leaderboard_data else 0
        
        # Overall stats
        stats = {
            'total_users': len(leaderboard_data),
            'total_problems': sum(user['total_solved'] for user in leaderboard_data),
            'weekly_problems': total_weekly_problems,
            'weekly_score': total_weekly_score,
            'avg_weekly_score': avg_weekly_score,
            'total_base_score': sum(user.get('base_score', 0) for user in leaderboard_data),
            'avg_score': sum(user.get('base_score', 0) for user in leaderboard_data) / len(leaderboard_data),
            'leader': leaderboard_data[0] if leaderboard_data else None,
            'easy_champion': max(leaderboard_data, key=lambda x: x.get('easy', 0)),
            'medium_champion': max(leaderboard_data, key=lambda x: x.get('medium', 0)),
            'hard_champion': max(leaderboard_data, key=lambda x: x.get('hard', 0)),
            # Weekly champions
            'weekly_easy_champion': max(leaderboard_data, key=lambda x: x.get('weekly_easy', 0)),
            'weekly_medium_champion': max(leaderboard_data, key=lambda x: x.get('weekly_medium', 0)),
            'weekly_hard_champion': max(leaderboard_data, key=lambda x: x.get('weekly_hard', 0))
        }
    
    return render_template('index.html', 
                         leaderboard=leaderboard_data, 
                         stats=stats, 
                         current_sort=sort_by)

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
    
    return render_template('user_details.html', user=user_data)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """Add user page."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if not username:
            flash("Please enter a username", "error")
            return render_template('add_user.html')
        
        # Add user (this might take a while)
        success = leaderboard.add_user(username)
        
        if success:
            flash(f"Successfully added {username} to leaderboard!", "success")
            return redirect(url_for('index'))
        else:
            flash(f"Could not add {username}. User may not exist or profile may be private.", "error")
    
    return render_template('add_user.html')

@app.route('/remove_user/<username>')
def remove_user(username):
    """Remove user from leaderboard."""
    success = leaderboard.remove_user(username)
    
    if success:
        flash(f"Removed {username} from leaderboard", "success")
    else:
        flash(f"User {username} not found in leaderboard", "error")
    
    return redirect(url_for('index'))

@app.route('/update_user/<username>')
def update_user_route(username):
    """Update specific user's data."""
    success = leaderboard.update_user(username)
    
    if success:
        flash(f"Updated {username}'s data", "success")
    else:
        flash(f"Could not update {username}", "error")
    
    return redirect(url_for('user_details', username=username))

@app.route('/update_all')
def update_all():
    """Update all users' data."""
    flash("Updating all users... This may take a while.", "info")
    leaderboard.update_all_users()
    flash("Finished updating all users", "success")
    return redirect(url_for('index'))

@app.route('/api/leaderboard')
def api_leaderboard():
    """API endpoint for leaderboard data."""
    sort_by = request.args.get('sort_by', 'base_score')
    leaderboard_data = leaderboard.get_leaderboard(sort_by)
    return jsonify(leaderboard_data)

@app.route('/api/user/<username>')
def api_user(username):
    """API endpoint for user data."""
    username_lower = username.lower()
    if username_lower not in leaderboard.users:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(leaderboard.users[username_lower])

@app.route('/api/stats')
def api_stats():
    """API endpoint for summary statistics."""
    leaderboard_data = leaderboard.get_leaderboard()
    
    if not leaderboard_data:
        return jsonify({})
    
    stats = {
        'total_users': len(leaderboard_data),
        'total_problems': sum(user['total_solved'] for user in leaderboard_data),
        'total_base_score': sum(user.get('base_score', 0) for user in leaderboard_data),
        'avg_score': sum(user.get('base_score', 0) for user in leaderboard_data) / len(leaderboard_data),
        'leader': leaderboard_data[0]['username'] if leaderboard_data else None
    }
    
    return jsonify(stats)

if __name__ == '__main__':
    print("🚀 Starting LeetCode Leaderboard Web App...")
    print("📱 Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)