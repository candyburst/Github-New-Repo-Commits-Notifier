import requests
import schedule
import time
import os

# Telegram Bot API configuration
TELEGRAM_TOKEN = "YourBotTokenfromBotfather"
TELEGRAM_CHAT_ID = "yourtelegramchatidnumber"
USERNAME_FILE = "usernames.txt"

# Tracking latest commit and repo IDs to avoid duplicate notifications
latest_commit_sha = {}
latest_repo_id = {}

def load_usernames():
    """Load usernames and organizations from file."""
    if not os.path.exists(USERNAME_FILE):
        open(USERNAME_FILE, 'w').close()  # Create file if it does not exist
    with open(USERNAME_FILE, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def update_username_file(entries):
    """Overwrite the username file with updated entries."""
    with open(USERNAME_FILE, 'w') as f:
        f.write("\n".join(entries) + "\n")

def add_entry(entry_type, name):
    """Add a GitHub username or organization to the tracking list."""
    entries = load_usernames()
    entry = f"{entry_type}:{name}"
    if entry not in entries:
        entries.append(entry)
        update_username_file(entries)
        print(f"Added {entry_type} '{name}' to tracking.")
    else:
        print(f"{entry_type.capitalize()} '{name}' is already being tracked.")

def remove_entry(entry_type, name):
    """Remove a GitHub username or organization from the tracking list."""
    entries = load_usernames()
    entry = f"{entry_type}:{name}"
    if entry in entries:
        entries.remove(entry)
        update_username_file(entries)
        print(f"Removed {entry_type} '{name}' from tracking.")
    else:
        print(f"{entry_type.capitalize()} '{name}' is not being tracked.")

def send_telegram_message(message):
    """Send a Telegram message to the specified chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        print("Notification sent successfully.")
    except requests.RequestException as e:
        print(f"Failed to send notification: {e}")

def fetch_github_data(url):
    """Fetch data from the GitHub API and handle errors."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Failed to fetch data from {url}: {e}")
        return None

def get_latest_repo(entry_type, name):
    """Check for the latest repository created by a GitHub user or organization."""
    global latest_repo_id
    url = f"https://api.github.com/{'users' if entry_type == 'user' else 'orgs'}/{name}/repos?sort=created"
    repos = fetch_github_data(url)
    if repos:
        latest_repo = repos[0]
        repo_id = latest_repo['id']
        repo_name = latest_repo['name']
        repo_url = latest_repo['html_url']
        if name not in latest_repo_id or repo_id != latest_repo_id[name]:
            latest_repo_id[name] = repo_id
            send_telegram_message(f"New Repository by {entry_type.capitalize()} '{name}': {repo_name}\n{repo_url}")

def get_latest_commit(entry_type, name):
    """Check for the latest commit by a GitHub user or in an organization's repositories."""
    global latest_commit_sha
    url = f"https://api.github.com/{'users' if entry_type == 'user' else 'orgs'}/{name}/events"
    events = fetch_github_data(url)
    if events:
        for event in events:
            if event['type'] == "PushEvent":
                commit_sha = event['payload']['commits'][-1]['sha']
                repo_name = event['repo']['name']
                commit_message = event['payload']['commits'][-1]['message']
                if name not in latest_commit_sha or commit_sha != latest_commit_sha[name]:
                    latest_commit_sha[name] = commit_sha
                    send_telegram_message(f"New Commit in {entry_type.capitalize()} '{name}/{repo_name}': {commit_message}")
                break

def update_authors():
    """Check for updates for each username or organization every 2 hours."""
    entries = load_usernames()
    for entry in entries:
        entry_type, name = entry.split(":")
        get_latest_commit(entry_type, name)
        get_latest_repo(entry_type, name)

# Schedule repository updates every 2 hours
schedule.every(2).hours.do(update_authors)

def main():
    """Main program loop for managing and running the bot."""
    print("Starting the bot...")
    send_telegram_message("🚀 GitHub Tracker Bot is now running!")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("Bot stopped.")

if __name__ == "__main__":
    main()
