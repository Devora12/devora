import requests
import json
from requests.auth import HTTPBasicAuth

# Bitbucket credentials (replace with yours)
USERNAME = "asakaspunchihewa"
APP_PASSWORD = "ATBBpjajXXHgJVNwzrJcmvmkxBC9A881DD81"
WORKSPACE = "slttest1"
REPO_SLUG = "test1"

# API endpoint to get commits
API_URL = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/commits?pagelen=2"

response = requests.get(API_URL, auth=HTTPBasicAuth(USERNAME, APP_PASSWORD))

if response.status_code == 200:
    commits = response.json()["values"]
    commit_data = []

    for commit in commits:
        commit_hash = commit["hash"]
        author_raw = commit["author"]["raw"]
        date = commit["date"]
        message = commit["message"]

        # Extract author info
        if "<" in author_raw and ">" in author_raw:
            author_name = author_raw.split("<")[0].strip()
            author_email = author_raw.split("<")[1].replace(">", "").strip()
        else:
            author_name = author_raw
            author_email = "Not Available"

        # Get diff statistics
        diff_url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/diffstat/{commit_hash}"
        diff_response = requests.get(diff_url, auth=HTTPBasicAuth(USERNAME, APP_PASSWORD))

        if diff_response.status_code == 200:
            diff_data = diff_response.json()["values"]
            
            # Calculate basic metrics
            # lines_added = sum(item.get("lines_added", 0) for item in diff_data)
            # lines_deleted = sum(item.get("lines_removed", 0) for item in diff_data)
            # total_changes = lines_added + lines_deleted

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

            # Quality analysis
            # stripped_removed = set(line.strip() for line in removed_code)
            # stripped_added = set(line.strip() for line in added_code)
            # superficial_lines = len(stripped_removed.intersection(stripped_added))
            
            # whitespace_lines = sum(
            #     1 for line in removed_code + added_code 
            #     if not line.strip()
            # )

            # Meaningfulness check
            # is_meaningful = True
            # if total_changes < 5:
            #     is_meaningful = False
            # elif (superficial_lines / total_changes) > 0.5 if total_changes > 0 else False:
            #     is_meaningful = False
            # elif (whitespace_lines / total_changes) > 0.5 if total_changes > 0 else False:
            #     is_meaningful = False

            # Collect commit data
            commit_data.append({
                "commit_hash": commit_hash,
                "author_name": author_name,
                "author_email": author_email,
                "date": date,
                "message": message,
                # "lines_added": lines_added,
                # "lines_deleted": lines_deleted,
                # "total_changes": total_changes,
                "code_changes": {
                    "added": added_code,
                    "removed": removed_code
                },
                # "quality_metrics": {
                #     "superficial_lines": superficial_lines,
                #     "whitespace_lines": whitespace_lines,
                #     "is_meaningful": is_meaningful
                # }
            })

        else:
            print(f"Could not fetch diff for commit {commit_hash}")

    print(json.dumps(commit_data, indent=4))

else:
    print("Error Fetching Commits:", response.status_code, response.text)