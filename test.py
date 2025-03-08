import requests
from requests.auth import HTTPBasicAuth

# Bitbucket credentials (replace with yours)
USERNAME = "asakaspunchihewa"
APP_PASSWORD = "ATBBpjajXXHgJVNwzrJcmvmkxBC9A881DD81"
WORKSPACE = "slttest1"
REPO_SLUG = "test1"

# API endpoint to get commits
api_url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/commits"

# Fetch data from API
response = requests.get(api_url, auth=HTTPBasicAuth(USERNAME, APP_PASSWORD))

if response.status_code == 200:
    commits = response.json()["values"]
    
    for commit in commits[:5]:  # Get the latest 5 commits
        commit_hash = commit["hash"]
        author = commit["author"]["raw"]
        date = commit["date"]
        message = commit["message"]

        # Get commit diff (line changes)
        diff_url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/diff/{commit_hash}"
        diff_response = requests.get(diff_url, auth=HTTPBasicAuth(USERNAME, APP_PASSWORD))
        
        if diff_response.status_code == 200:
            diff_text = diff_response.text
            added_lines = diff_text.count("\n+")
            removed_lines = diff_text.count("\n-")

            print(f"Commit: {commit_hash}")
            print(f"Author: {author}")
            print(f"Date: {date}")
            print(f"Message: {message}")
            print(f"Lines Added: {added_lines}, Lines Removed: {removed_lines}")
            print("-" * 50)
else:
    print("Failed to fetch commits:", response.json())
