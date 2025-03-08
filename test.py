import requests
import json
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

    

    # Initialize a list to store commit details in JSON format
    commit_data = []

    for commit in commits:
        commit_hash = commit["hash"]
        author_raw = commit["author"]["raw"]  # Format: "John Doe <john.doe@example.com>"
        date = commit["date"]
        message = commit["message"]

        # Extract Name & Email
        if "<" in author_raw and ">" in author_raw:
            author_name = author_raw.split("<")[0].strip()
            author_email = author_raw.split("<")[1].replace(">", "").strip()
        else:
            author_name = author_raw
            author_email = "Not Available"

        # Fetch commit diff to get lines added/deleted
        diff_url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/diffstat/{commit_hash}"
        diff_response = requests.get(diff_url, auth=HTTPBasicAuth(USERNAME, APP_PASSWORD))

        if diff_response.status_code == 200:
            diff_data = diff_response.json()["values"]

            lines_added = sum(item.get("lines_added", 0) for item in diff_data)
            lines_deleted = sum(item.get("lines_removed", 0) for item in diff_data)
            total_changes = lines_added + lines_deleted

            # Track removed and added lines to detect superficial changes
            removed_lines = []
            added_lines = []

            for item in diff_data:
                # Safely check for 'old' and 'new' keys and their 'lines' values
                if item.get("old") is not None and "lines" in item["old"]:
                    removed_lines.extend(item["old"]["lines"])

                if item.get("new") is not None and "lines" in item["new"]:
                    added_lines.extend(item["new"]["lines"])

            # Check for superficial changes (removed code added back in a different line)
            superficial_change = False
            for removed_line in removed_lines:
                if removed_line.strip() in added_lines:
                    superficial_change = True
                    break

            # Collect the commit data in a dictionary
            commit_data.append({
                "commit_hash": commit_hash,
                "author_name": author_name,
                "author_email": author_email,
                "date": date,
                "message": message,
                "lines_added": lines_added,
                "lines_deleted": lines_deleted,
                "total_changes": total_changes,
                "superficial_change": "Yes" if superficial_change else "No"
            })

        else:
            print(f"⚠️ Could not fetch diff for commit {commit_hash}")

    # Print the commit data as a JSON object
    print(json.dumps(commit_data, indent=4))

else:
    print("❌ Error Fetching Commits:", response.status_code, response.text)