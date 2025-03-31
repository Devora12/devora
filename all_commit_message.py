import sys
import requests
import json
import re

# Set the console encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Bitbucket API configuration
WORKSPACE = "slttest1"
REPO_SLUG = "bitbucket_project"
ACCESS_TOKEN = "ATCTT3xFfGN0CFPRsEATPT8GgX-PamvnKrGFjqXKyCC8ZN0ZI2pnsBUS7-7J0Ig1dposHf6UOsHabOffY360mK3z3kOu7iVd0RZxX94s_UK0KqJGO2oGj-ijJChO_c234MsA_0dBNmCInQuS_NSjFb9x83buMcJMCtqbCylR0iGHU5vuH_Ba_9g=676CC7D2"

def find_commits_by_testcase(testcase_id):
    """Find all commits that include the given testcase ID"""
    API_URL = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/commits"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    matching_commits = []

    # Handle pagination
    while API_URL:
        response = requests.get(API_URL, headers=headers)

        if response.status_code == 200:
            data = response.json()
            commits = data.get("values", [])

            for commit in commits:
                # Check if testcase ID is in commit message
                if str(testcase_id) in commit["message"]:
                    matching_commits.append({
                        "hash": commit["hash"],
                        "date": commit["date"],
                        "message": commit["message"].strip(),
                        "author": commit["author"]["raw"]
                    })

            # Get the next page URL
            API_URL = data.get("next")
        else:
            print(f"Error fetching commits: {response.status_code}")
            break

    return matching_commits

def print_matching_commits(commits, testcase_id):
    """Print commits that match the testcase ID"""
    if not commits:
        print(f"No commits found containing testcase ID: {testcase_id}")
        return

    print(f"\n🔍 Found {len(commits)} commits containing testcase ID: {testcase_id}")
    print("=" * 60)
    
    for commit in commits:
        print(f"📌 Commit Hash: {commit['hash']}")
        print(f"📅 Date: {commit['date']}")
        print(f"👤 Author: {commit['author']}")
        print(f"💬 Message:\n{commit['message']}")
        print("-" * 60)

if __name__ == "__main__":
    # Example usage
    testcase_id = "202503002"  # Replace with your testcase ID
    
    print(f"🔎 Searching for commits containing testcase ID: {testcase_id}")
    matching_commits = find_commits_by_testcase(testcase_id)
    print_matching_commits(matching_commits, testcase_id)