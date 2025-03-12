import requests
import json

# Repository details
WORKSPACE = "slttest1"  # Replace with your workspace
REPO_SLUG = "test1"     # Replace with your repository slug
ACCESS_TOKEN = "ATCTT3xFfGN0CFPRsEATPT8GgX-PamvnKrGFjqXKyCC8ZN0ZI2pnsBUS7-7J0Ig1dposHf6UOsHabOffY360mK3z3kOu7iVd0RZxX94s_UK0KqJGO2oGj-ijJChO_c234MsA_0dBNmCInQuS_NSjFb9x83buMcJMCtqbCylR0iGHU5vuH_Ba_9g=676CC7D2"  # Replace with your token

# Filter by Email
USER_EMAIL = "2021t01245@stu.cmb.ac.lk"  # Replace with the user's email
API_URL = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/commits?pagelen=2&author={USER_EMAIL}"

# Headers for authentication
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

# Fetch commits
response = requests.get(API_URL, headers=headers)

if response.status_code == 200:
    commits = response.json()["values"]
    commit_data = []

    for commit in commits:
        commit_hash = commit["hash"]
        date = commit["date"]
        message = commit["message"]

        # Get raw diff content
        raw_diff_url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/diff/{commit_hash}"
        raw_diff_response = requests.get(raw_diff_url, headers=headers)

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