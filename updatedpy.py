import requests
import json
from requests.auth import HTTPBasicAuth

# Credentials
USERNAME = "asakaspunchihewa"
APP_PASSWORD = "ATBBpjajXXHgJVNwzrJcmvmkxBC9A881DD81"
WORKSPACE = "slttest1"
REPO_SLUG = "test1"

# Filter by Email
USER_EMAIL = "2021t01245@stu.cmb.ac.lk"
API_URL = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/commits?pagelen=2&author={USER_EMAIL}"

response = requests.get(API_URL, auth=HTTPBasicAuth(USERNAME, APP_PASSWORD))

if response.status_code == 200:
    commits = response.json()["values"]
    commit_data = []

    for commit in commits:
        commit_hash = commit["hash"]
        author_raw = commit["author"]["raw"]
        date = commit["date"]
        message = commit["message"]

        # Get raw diff content
        raw_diff_url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/diff/{commit_hash}"
        raw_diff_response = requests.get(raw_diff_url, auth=HTTPBasicAuth(USERNAME, APP_PASSWORD))

        added_code = []
        removed_code = []

        if raw_diff_response.status_code == 200:
            # Parse diff to get changed lines
            diff_content = raw_diff_response.text
            for line in diff_content.split('\n'):
                # Skip diff headers
                if line.startswith('+++') or line.startswith('---'):
                    continue
                # Capture added lines
                if line.startswith('+'):
                    added_code.append(line[1:])  # Remove '+' prefix
                # Capture removed lines
                elif line.startswith('-'):
                    removed_code.append(line[1:])  # Remove '-' prefix

        # Collect commit data
        commit_data.append({
            "commit_hash": commit_hash,
            "date": date,
            "message": message,
            "code_changes": {
                "added": added_code,
                "removed": removed_code
            }
        })

    print(json.dumps(commit_data, indent=4))

else:
    print("Error:", response.status_code, response.text)