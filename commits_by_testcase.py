import sys
import requests
import json

# Set the console encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Bitbucket API configuration
WORKSPACE = "slttest1"  # Replace with your workspace
REPO_SLUG = "test1"     # Replace with your repository slug
ACCESS_TOKEN = "ATCTT3xFfGN0CFPRsEATPT8GgX-PamvnKrGFjqXKyCC8ZN0ZI2pnsBUS7-7J0Ig1dposHf6UOsHabOffY360mK3z3kOu7iVd0RZxX94s_UK0KqJGO2oGj-ijJChO_c234MsA_0dBNmCInQuS_NSjFb9x83buMcJMCtqbCylR0iGHU5vuH_Ba_9g=676CC7D2"  # Replace with your token
USER_EMAIL = "sewminiweerakkody1004@gmail.com"  # Replace with user email
BRANCH_NAME = "TestCase1"    # Replace with target branch name

def get_commit_data():
    """Fetch commits from specific branch with diffs"""
    API_URL = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/commits?&author={USER_EMAIL}&branch={BRANCH_NAME}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    response = requests.get(API_URL, headers=headers)
    if response.status_code != 200:
        print("Error fetching commits:", response.status_code, response.text)
        return None

    commits = response.json().get("values", [])
    commit_data = []

    for commit in commits:
        commit_hash = commit["hash"]
        author = commit["author"]["raw"]  # Get the author's name or email
        branch = commit.get("target", {}).get("branch", {}).get("name", BRANCH_NAME)  # Default to BRANCH_NAME if not available
        raw_diff_url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/diff/{commit_hash}"
        diff_response = requests.get(raw_diff_url, headers=headers)
        
        added = []
        removed = []
        
        if diff_response.status_code == 200:
            for line in diff_response.text.split('\n'):
                if line.startswith('+') and not line.startswith('+++'):
                    added.append(line[1:])
                elif line.startswith('-') and not line.startswith('---'):
                    removed.append(line[1:])

        commit_data.append({
            "commit_hash": commit_hash,
            "author": author,
            "branch": branch,
            "date": commit["date"],
            "message": commit["message"].strip(),
            "code_changes": {
                "added": added,
                "removed": removed
            }
        })

    return commit_data

if __name__ == "__main__":
    commits = get_commit_data()
    if commits:
        print(json.dumps(commits, indent=2, ensure_ascii=False))
    else:
        print("No commits found matching criteria")