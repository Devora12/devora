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
    commit_data = []  # List to store commit details

    for commit in commits:
        commit_hash = commit["hash"]
        author_raw = commit["author"]["raw"]  # Format: "John Doe <john.doe@example.com>"
        date = commit["date"]
        message = commit["message"]

        # Extract author name and email
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

            # Calculate lines added, deleted, and total changes
            lines_added = sum(item.get("lines_added", 0) for item in diff_data)
            lines_deleted = sum(item.get("lines_removed", 0) for item in diff_data)
            total_changes = lines_added + lines_deleted

            # Track removed and added lines for superficial change detection
            removed_lines = []
            added_lines = []

            for item in diff_data:
                if item.get("old") is not None and "lines" in item["old"]:
                    removed_lines.extend(item["old"]["lines"])
                if item.get("new") is not None and "lines" in item["new"]:
                    added_lines.extend(item["new"]["lines"])

            # Detect superficial changes (removed code added back in a different line)
            stripped_removed = {line.strip() for line in removed_lines}
            stripped_added = {line.strip() for line in added_lines}
            superficial_lines = len(stripped_removed.intersection(stripped_added))

            # Detect whitespace-only changes
            whitespace_removed = sum(1 for line in removed_lines if not line.strip())
            whitespace_added = sum(1 for line in added_lines if not line.strip())
            whitespace_lines = whitespace_removed + whitespace_added

            # Calculate ratios and net changes
            superficial_ratio = superficial_lines / total_changes if total_changes > 0 else 0
            whitespace_ratio = whitespace_lines / total_changes if total_changes > 0 else 0
            net_changes = lines_added - lines_deleted
            files_changed = len(diff_data)

            # Determine if the commit is meaningful
            is_meaningful = True
            if total_changes < 5:  # Minor changes
                is_meaningful = False
            elif superficial_ratio > 0.5:  # Mostly superficial
                is_meaningful = False
            elif whitespace_ratio > 0.5:  # Mostly whitespace
                is_meaningful = False

            # Collect commit data
            commit_data.append({
                "commit_hash": commit_hash,
                "author_name": author_name,
                "author_email": author_email,
                "date": date,
                "message": message,
                "lines_added": lines_added,
                "lines_deleted": lines_deleted,
                "total_changes": total_changes,
                "superficial_lines": superficial_lines,
                "whitespace_lines": whitespace_lines,
                "superficial_ratio": round(superficial_ratio, 2),
                "whitespace_ratio": round(whitespace_ratio, 2),
                "net_changes": net_changes,
                "files_changed": files_changed,
                "is_meaningful": is_meaningful
            })

        else:
            print(f"5 Could not fetch diff for commit {commit_hash}")

    # Print the commit data as a JSON object
    print(json.dumps(commit_data, indent=4))

else:
    print(" Error Fetching Commits:", response.status_code, response.text)