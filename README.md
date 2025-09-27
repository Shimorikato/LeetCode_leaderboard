# Advanced LeetCode Leaderboard 🏆

A sophisticated Python application to create and manage a LeetCode leaderboard with **advanced scoring system** to compare your progress with friends!

## 🎯 Advanced Features

### 🏆 **Smart Scoring System**

- **Easy Problems**: 1 point each
- **Medium Problems**: 3 points each
- **Hard Problems**: 7 points each
- **Performance Multiplier**: Based on LeetCode ranking and recent activity
- **Advanced Score**: Base score × Performance multiplier for fair comparison

### 📊 **Comprehensive Analytics**

- **Multiple Users**: Track unlimited friends' progress
- **Time-based Analysis**: Daily, weekly, yearly submission tracking
- **Language Distribution**: See which programming languages everyone uses
- **Topic Analysis**: Track problem categories and algorithmic topics
- **Recent Activity**: Monitor latest submissions and streaks
- **Performance Metrics**: Advanced scoring considers consistency and difficulty

### 🎨 **Enhanced Display**

- **Beautiful Leaderboards**: Multiple sorting options with rich formatting
- **Detailed Profiles**: Individual user analysis with progress bars
- **Activity Indicators**: Visual representation of recent performance
- **Champion Tracking**: Separate leaders for Easy, Medium, Hard problems
- **Real-time Updates**: Fresh data whenever you need it

## Installation

1. **Clone or Download** this repository
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Quick Start

Run the application:

```bash
python leetcode_leaderboard.py
```

### 🎮 Available Commands

#### User Management

| Command             | Description                 | Example           |
| ------------------- | --------------------------- | ----------------- |
| `add <username>`    | Add a friend to leaderboard | `add john_doe`    |
| `remove <username>` | Remove a friend             | `remove john_doe` |
| `update`            | Update all users' stats     | `update`          |
| `update <username>` | Update specific user        | `update john_doe` |

#### Leaderboard Views

| Command                 | Description                          | Example        |
| ----------------------- | ------------------------------------ | -------------- |
| `show`                  | Display leaderboard (advanced score) | `show`         |
| `show score`            | Sort by advanced score               | `show score`   |
| `show base`             | Sort by base score (E×1+M×3+H×7)     | `show base`    |
| `show total`            | Sort by total problems               | `show total`   |
| `show easy/medium/hard` | Sort by difficulty                   | `show hard`    |
| `show ranking`          | Sort by LeetCode ranking             | `show ranking` |

#### Analysis & Info

| Command              | Description                     | Example            |
| -------------------- | ------------------------------- | ------------------ |
| `details <username>` | Show comprehensive user profile | `details john_doe` |
| `list`               | List all users in leaderboard   | `list`             |
| `help`               | Show detailed help              | `help`             |
| `exit`               | Exit program                    | `exit`             |

### 🎯 Advanced Scoring Example

```bash
💻 Enter command: add your_username
🔍 Fetching data for your_username...
📊 Base Score: 876
🎯 Advanced Score: 1051.2
✅ Added your_username to leaderboard!

💻 Enter command: add coding_master
🔍 Fetching data for coding_master...
📊 Base Score: 1456
🎯 Advanced Score: 1747.2
✅ Added coding_master to leaderboard!

💻 Enter command: show
========================================================================================================================
                                           🏆 ADVANCED LEETCODE LEADERBOARD 🏆
========================================================================================================================
Sorted by: Advanced Score (Difficulty × Performance)
------------------------------------------------------------------------------------------------------------------------
Pos  Username           Adv Score  Base   Total  E/M/H    Week   Rank       Activity     Updated
------------------------------------------------------------------------------------------------------------------------
🥇   coding_master      1747.2     1456   680    200/350/130  12     #25,432    🔥 Very Active  09/28
🥈   your_username      1051.2     876    420    150/220/50   8      #89,567    ✅ Active      09/28
========================================================================================================================
📊 Total users: 2 | Total problems solved: 1100 | Avg advanced score: 1399.2
🏆 Leader: coding_master | Score: 1747.2 | Problems: 680
🎯 Easy Champion: coding_master (200 problems)
🎯 Medium Champion: coding_master (350 problems)
🎯 Hard Champion: coding_master (130 problems)
========================================================================================================================
--------------------------------------------------------------------------------
Pos  Username             Total    Easy   Med    Hard   Rank       Last Updated
--------------------------------------------------------------------------------
🥇   your_username        1250     400    650    200    5,432      09/28 14:30
🥈   friend1              890      350    400    140    12,567     09/28 14:31
================================================================================
📊 Total users: 2
🏆 Leader: your_username with 1250 problems
📈 Average problems solved: 1070.0
🔢 Total problems solved by group: 2140
```

## Features Explained

### 🎯 Leaderboard Sorting

- **Total Problems**: Default view showing overall progress
- **By Difficulty**: Compare easy, medium, or hard problem counts
- **LeetCode Ranking**: Sort by official LeetCode global ranking

### 👤 User Details

Get detailed stats for any user including:

- Problem breakdown by difficulty
- Visual progress bars showing difficulty distribution
- LeetCode ranking and real name (if public)
- Last update timestamp

### 💾 Data Persistence

- User data is automatically saved to `leaderboard_data.json`
- No need to re-fetch data every time you run the program
- Use `update` commands to refresh stats when needed

## Tips

1. **Be Respectful**: Don't update too frequently to avoid overwhelming LeetCode's servers
2. **Check Usernames**: Make sure usernames are correct - the tool will let you know if a user isn't found
3. **Update Regularly**: Run `update` periodically to keep stats current
4. **Backup Data**: The `leaderboard_data.json` file contains all your data

## Troubleshooting

### User Not Found

- Double-check the username spelling
- Make sure the LeetCode profile is public
- Try visiting `https://leetcode.com/<username>` to verify the profile exists

### Network Issues

- Check your internet connection
- LeetCode's API might be temporarily unavailable
- The tool includes retry logic and error handling

### Data Issues

- If data seems corrupted, delete `leaderboard_data.json` and re-add users
- Use `update <username>` to refresh specific user data

## How It Works

The application uses LeetCode's GraphQL API to fetch user statistics including:

- Total problems solved
- Problems by difficulty (Easy/Medium/Hard)
- Global ranking
- Profile information

Data is cached locally to minimize API calls and provide faster access to your leaderboard.

## Contributing

Feel free to enhance this tool! Some ideas:

- Web interface using Flask/Django
- Database storage instead of JSON
- Additional statistics and metrics
- Notifications for progress updates
- Export to CSV/Excel

---

**Happy coding and may the best problem solver win! 🚀**
