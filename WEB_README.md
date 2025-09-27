# 🌐 Advanced LeetCode Leaderboard - Web Edition

A beautiful, modern web application for managing and comparing LeetCode progress with friends using an advanced scoring system.

## 🎯 Features

### 🏆 **Advanced Scoring System**

- **Easy Problems**: 1 point each
- **Medium Problems**: 3 points each
- **Hard Problems**: 7 points each
- **Performance Multiplier**: Based on LeetCode ranking and recent activity
- **Advanced Score**: Base score × Performance multiplier for fair comparison

### 🎨 **Modern Web Interface**

- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Dark Theme**: Beautiful gradient backgrounds and modern styling
- **Interactive Elements**: Hover effects, animations, and smooth transitions
- **Real-time Updates**: Dynamic content loading and progress tracking
- **Bootstrap 5**: Professional UI components and responsive grid

### 📊 **Comprehensive Analytics**

- **Leaderboard Views**: Multiple sorting options (score, difficulty, ranking)
- **User Profiles**: Detailed stats with progress bars and metrics
- **Activity Tracking**: Recent submissions and time-based analytics
- **Champion Categories**: Separate leaders for each difficulty level
- **Visual Progress**: Interactive charts and progress indicators

### 🚀 **Enhanced User Experience**

- **Search Functionality**: Find users quickly
- **Auto-refresh**: Optional automatic data updates
- **Keyboard Shortcuts**: Power user features
- **Toast Notifications**: Real-time feedback
- **Confirmation Dialogs**: Safe destructive actions

## 📦 Installation & Setup

### Prerequisites

- Python 3.7 or higher
- Internet connection (for LeetCode API)

### Quick Start

1. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Web Application**:

   **Option A - Command Line:**

   ```bash
   python web_app.py
   ```

   **Option B - Windows Batch File:**

   ```cmd
   run_web.bat
   ```

   **Option C - PowerShell Script:**

   ```powershell
   .\run_web.ps1
   ```

3. **Open in Browser**:
   ```
   http://localhost:5000
   ```

## 🎮 How to Use

### Adding Users

1. Click "Add User" in the navigation
2. Enter a LeetCode username
3. Wait for data to be fetched
4. User appears in leaderboard with calculated scores

### Viewing Leaderboard

- **Default View**: Sorted by Advanced Score
- **Sort Options**: Use dropdown to sort by different metrics
- **Search**: Type in search box to filter users
- **User Details**: Click on username for detailed profile

### Managing Users

- **Update Individual**: Click update button next to user
- **Update All**: Use "Update All" in navigation
- **Remove User**: Click trash icon (with confirmation)
- **View Profile**: Click username for detailed stats

### Advanced Features

- **Auto-refresh**: Toggle in navigation for automatic updates
- **Keyboard Shortcuts**:
  - `Ctrl+R`: Refresh page
  - `Ctrl+A`: Go to add user
  - `Escape`: Close modals
- **Responsive**: Works on all device sizes

## 🎯 Scoring System Explained

### Base Score Calculation

```
Base Score = (Easy Problems × 1) + (Medium Problems × 3) + (Hard Problems × 7)
```

### Advanced Score Calculation

```
Advanced Score = Base Score × Performance Multiplier

Performance Multiplier factors:
- LeetCode global ranking (better rank = higher multiplier)
- Recent activity (more submissions = bonus)
- Consistency (regular solving patterns)
```

### Example Scoring

```
User A: 100 Easy + 50 Medium + 20 Hard = 290 Base Score
- Good ranking (#50,000) = 1.2× multiplier
- Recent activity bonus = +10 points
- Advanced Score: 290 × 1.2 + 10 = 358 points

User B: 50 Easy + 100 Medium + 50 Hard = 700 Base Score
- Average ranking (#500,000) = 0.9× multiplier
- No recent activity = +0 points
- Advanced Score: 700 × 0.9 + 0 = 630 points
```

## 📱 Screenshots & Interface

### Main Leaderboard

- **Statistics Cards**: Total users, problems solved, average score, current leader
- **Ranking Table**: Comprehensive user comparison with all metrics
- **Champion Section**: Category leaders for Easy/Medium/Hard problems

### User Profile

- **Score Metrics**: Advanced and base scores with explanations
- **Problem Statistics**: Breakdown by difficulty with progress bars
- **Recent Activity**: Submission patterns and activity indicators
- **Language Analysis**: Programming language distribution

### Add User

- **Simple Form**: Clean interface for adding new users
- **Instructions**: Helpful tips for finding valid usernames
- **Scoring Guide**: Explanation of the scoring system

## 🔧 Technical Details

### File Structure

```
LeetCode_leaderboard/
├── web_app.py              # Flask application
├── leetcode_leaderboard.py # Core functionality
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Main leaderboard
│   ├── user_details.html  # User profile
│   └── add_user.html      # Add user form
├── static/                # Static assets
│   ├── css/style.css      # Custom styling
│   └── js/app.js          # JavaScript functionality
├── requirements.txt       # Python dependencies
└── run_web.*             # Launch scripts
```

### API Endpoints

- `GET /`: Main leaderboard page
- `GET /user/<username>`: User profile page
- `GET /add_user`: Add user form
- `POST /add_user`: Process new user
- `GET /api/leaderboard`: JSON leaderboard data
- `GET /api/user/<username>`: JSON user data
- `GET /api/stats`: JSON summary statistics

### Technologies Used

- **Backend**: Flask (Python web framework)
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Data**: JSON file storage
- **API**: LeetCode GraphQL API
- **Styling**: Custom CSS with gradients and animations

## 🔄 Data Management

### Data Storage

- Uses JSON file for persistent storage
- Separate files for CLI (`leaderboard_data.json`) and web (`web_leaderboard_data.json`)
- Automatic backup on updates

### Update Strategy

- **Manual Updates**: Click update buttons
- **Auto-refresh**: Optional 5-minute intervals
- **Smart Caching**: Avoids unnecessary API calls

### Data Migration

- Easy to export/import between instances
- Compatible with command-line version
- Backup-friendly JSON format

## 🚀 Deployment Options

### Local Development

```bash
python web_app.py
# Runs on http://localhost:5000
```

### Production Deployment

```bash
# Using Gunicorn (recommended for production)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app

# Using Waitress (Windows-friendly)
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 web_app:app
```

### Cloud Deployment

- Compatible with Heroku, Railway, PythonAnywhere
- Requires `Procfile` for deployment platforms
- Environment variables for configuration

## 🎨 Customization

### Themes

- Built-in dark theme with gradient backgrounds
- Easy to customize colors in `style.css`
- Bootstrap variables for consistent theming

### Branding

- Modify navigation title and footer
- Add custom logo or branding elements
- Customize color scheme and styling

### Features

- Add new sorting options
- Implement additional statistics
- Create custom user badges or achievements

## ⚡ Performance Tips

### Optimization

- Enable auto-refresh only when needed
- Update users individually rather than all at once
- Use browser caching for static assets

### Scaling

- Consider database storage for large user bases
- Implement API rate limiting for LeetCode requests
- Add pagination for large leaderboards

## 🐛 Troubleshooting

### Common Issues

**"User not found"**

- Check username spelling
- Verify profile is public
- Try the LeetCode URL directly

**"Slow loading"**

- LeetCode API may be slow
- Check internet connection
- Consider updating users individually

**"Flask not found"**

- Install requirements: `pip install -r requirements.txt`
- Check Python version compatibility

### Debug Mode

- Application runs in debug mode by default
- Check console for detailed error messages
- Restart application after code changes

## 📈 Future Enhancements

### Planned Features

- **Database Integration**: PostgreSQL/MySQL support
- **User Authentication**: Personal dashboards
- **Advanced Analytics**: Progress charts and trends
- **Social Features**: Comments and achievements
- **Mobile App**: React Native companion app

### Community

- Open source and community-driven
- Contributions welcome
- Feature requests via GitHub issues

---

## 🎉 Get Started Now!

1. **Install**: `pip install -r requirements.txt`
2. **Run**: `python web_app.py`
3. **Browse**: Open `http://localhost:5000`
4. **Add Friends**: Click "Add User" and start competing!

**Happy coding and may the best problem solver win!** 🏆🚀
