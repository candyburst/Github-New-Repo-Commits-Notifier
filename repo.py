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
        with open(USERNAME_FILE, 'w') as f:
            pass  # Create file if it does not exist
    with open(USERNAME_FILE, 'r') as f:
        entries = [line.strip() for line in f if line.strip()]
    return entries

def add_entry(entry_type, name):
    """Add a GitHub username or organization to the tracking list."""
    entries = load_usernames()
    entry = f"{entry_type}:{name}"
    if entry not in entries:
        with open(USERNAME_FILE, 'a') as f:
            f.write(f"{entry}\n")
        print(f"Added {entry_type} '{name}' to tracking.")
    else:
        print(f"{entry_type.capitalize()} '{name}' is already being tracked.")

def remove_entry(entry_type, name):
    """Remove a GitHub username or organization from the tracking list."""
    entries = load_usernames()
    entry = f"{entry_type}:{name}"
    if entry in entries:
        entries.remove(entry)
        with open(USERNAME_FILE, 'w') as f:
            for item in entries:
                f.write(f"{item}\n")
        print(f"Removed {entry_type} '{name}' from tracking.")
    else:
        print(f"{entry_type.capitalize()} '{name}' is not being tracked.")

def get_latest_commit_for_user(user):
    """Check for the latest commit by a GitHub user."""
    global latest_commit_sha
    url = f"https://api.github.com/users/{user}/events"
    response = requests.get(url)
    if response.status_code == 200:
        events = response.json()
        for event in events:
            if event['type'] == "PushEvent":
                commit_sha = event['payload']['commits'][-1]['sha']
                repo_name = event['repo']['name']
                commit_message = event['payload']['commits'][-1]['message']
                if user not in latest_commit_sha or commit_sha != latest_commit_sha[user]:
                    latest_commit_sha[user] = commit_sha
                    send_telegram_message(f"New Commit by {user} in {repo_name}: {commit_message}")
                break
    else:
        print(f"Failed to fetch GitHub events for user {user}: {response.status_code}")

def get_latest_commit_for_org(org):
    """Check for the latest commit in an organization's repositories."""
    global latest_commit_sha
    url = f"https://api.github.com/orgs/{org}/events"
    response = requests.get(url)
    if response.status_code == 200:
        events = response.json()
        for event in events:
            if event['type'] == "PushEvent":
                repo_name = event['repo']['name']
                commit_sha = event['payload']['commits'][-1]['sha']
                commit_message = event['payload']['commits'][-1]['message']
                if org not in latest_commit_sha or commit_sha != latest_commit_sha[org]:
                    latest_commit_sha[org] = commit_sha
                    send_telegram_message(f"New Commit in {org}/{repo_name}: {commit_message}")
                break
    else:
        print(f"Failed to fetch GitHub events for org {org}: {response.status_code}")

def get_latest_repo(entry_type, name):
    """Check for the latest repository created by a GitHub user or organization."""
    global latest_repo_id
    if entry_type == "user":
        url = f"https://api.github.com/users/{name}/repos?sort=created"
    elif entry_type == "org":
        url = f"https://api.github.com/orgs/{name}/repos?sort=created"
    response = requests.get(url)
    if response.status_code == 200:
        repos = response.json()
        if repos:
            latest_repo = repos[0]
            repo_id = latest_repo['id']
            repo_name = latest_repo['name']
            repo_url = latest_repo['html_url']
            if name not in latest_repo_id or repo_id != latest_repo_id[name]:
                latest_repo_id[name] = repo_id
                send_telegram_message(f"New Repository by {entry_type.capitalize()} '{name}': {repo_name}\n{repo_url}")
    else:
        print(f"Failed to fetch GitHub repositories for {entry_type} {name}: {response.status_code}")

def send_telegram_message(message):
    """Send a Telegram message to the specified chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("Notification sent successfully.")
    else:
        print(f"Failed to send notification: {response.status_code}")

def send_welcome_message():
    """Send a welcome message to confirm the bot is running."""
    welcome_message = "🚀 GitHub Tracker Bot is now running! You’ll receive updates for tracked users and organizations."
    send_telegram_message(welcome_message)

def check_updates():
    """Check for updates for each username or organization in the list."""
    entries = load_usernames()
    for entry in entries:
        entry_type, name = entry.split(":")
        if entry_type == "user":
            get_latest_commit_for_user(name)
            get_latest_repo("user", name)
        elif entry_type == "org":
            get_latest_commit_for_org(name)
            get_latest_repo("org", name)

# Schedule the bot to run every 3 hours
schedule.every(3).hours.do(check_updates)

def main():
    """Main program loop for managing and running the bot."""
    while True:
        print("\nOptions:")
        print("1. Start bot")
        print("2. Add GitHub user")
        print("3. Add GitHub organization")
        print("4. Remove GitHub user")
        print("5. Remove GitHub organization")
        print("6. Quit")

        choice = input("Choose an option: ")
        if choice == '1':
            print("Starting the bot...")
            send_welcome_message()  # Send the welcome message
            try:
                while True:
                    schedule.run_pending()
                    time.sleep(1)
            except KeyboardInterrupt:
                print("Bot stopped.")
                break
        elif choice == '2':
            username = input("Enter the GitHub username to add: ")
            add_entry("user", username)
        elif choice == '3':
            org_name = input("Enter the GitHub organization to add: ")
            add_entry("org", org_name)
        elif choice == '4':
            username = input("Enter the GitHub username to remove: ")
            remove_entry("user", username)
        elif choice == '5':
            org_name = input("Enter the GitHub organization to remove: ")
            remove_entry("org", org_name)
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
