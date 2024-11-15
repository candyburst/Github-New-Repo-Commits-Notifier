# 🚀 GitHub Tracker Bot

**GitHub Tracker Bot** is a Python script that monitors GitHub activity for specified users and organizations. Receive instant notifications on Telegram whenever a new commit is pushed or a repository is created, helping you stay up-to-date with your favorite projects and developers!

---

### 🌟 Features
- **Real-time Tracking**: Monitors GitHub users and organizations for new commits and repository creations.
- **Instant Notifications**: Sends updates directly to a Telegram chat of your choice.
- **Easy Management**: Add or remove GitHub usernames and organizations through a user-friendly CLI menu.

---

### 📥 Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/github-tracker-bot.git
   cd github-tracker-bot
   ```

2. **Install Required Libraries**:
   ```bash
   pip install requests schedule
   ```

3. **Configure Telegram Bot**:
   - Replace `TELEGRAM_TOKEN` with your bot’s token (from BotFather on Telegram).
   - Replace `TELEGRAM_CHAT_ID` with the chat ID where notifications should be sent.

4. **Add GitHub Accounts to Track**:
   - List usernames and organizations in `usernames.txt` or use the CLI menu to add them.

5. **Run the Bot**:
   ```bash
   python github_tracker_bot.py
   ```

---

### 🔧 Usage
Once running, select an option:
- **1**: Start tracking GitHub activity and receive updates on Telegram.
- **2**: Add a GitHub user.
- **3**: Add a GitHub organization.
- **4**: Remove a GitHub user.
- **5**: Remove a GitHub organization.
- **6**: Quit the bot.

### 🕰️ Automated Checks
The bot runs every 3 hours, checking for updates and notifying you when there’s new activity.

---

### 📄 License
This project is licensed under the MIT License.

👀 Stay connected to your GitHub projects in real-time!