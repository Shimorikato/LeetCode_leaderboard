from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from leetcode_leaderboard import LeetCodeLeaderboard, get_user_stats, calculate_advanced_score

app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')
app.secret_key = 'leetcode_leaderboard_secret_key_2025'

# Global leaderboard instance
leaderboard = LeetCodeLeaderboard("web_leaderboard_data.json")

@app.route('/')
def index():
    """Main weekly leaderboard page."""
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
            'total_problems': sum(user['total_solved'] for user in leaderboard_data),
            'weekly_problems': total_weekly_problems,
            'weekly_score': total_weekly_score,
            'avg_weekly_score': avg_weekly_score,
            'total_advanced_score': sum(user.get('advanced_score', 0) for user in leaderboard_data),
            'avg_score': sum(user.get('advanced_score', 0) for user in leaderboard_data) / len(leaderboard_data),
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
    
    return render_template('user_details.html', user=user_data, username=username)

@app.route('/add_user')
def add_user_page():
    """Add user page."""
    return render_template('add_user.html')

@app.route('/api/add_user', methods=['POST'])
def api_add_user():
    """API endpoint to add a new user."""
    try:
        username = request.json.get('username', '').strip()
        if not username:
            return jsonify({'success': False, 'message': 'Username is required'}), 400
        
        success = leaderboard.add_user(username)
        if success:
            return jsonify({'success': True, 'message': f'User {username} added successfully!'})
        else:
            return jsonify({'success': False, 'message': f'Failed to add user {username}. Please check the username.'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

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