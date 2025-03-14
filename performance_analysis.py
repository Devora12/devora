import sys
import requests
import json
from openai import OpenAI

# Bitbucket API details
WORKSPACE = "slttest1"  # Replace with your workspace
REPO_SLUG = "test1"  # Replace with your repository slug
ACCESS_TOKEN = "ATCTT3xFfGN0CFPRsEATPT8GgX-PamvnKrGFjqXKyCC8ZN0ZI2pnsBUS7-7J0Ig1dposHf6UOsHabOffY360mK3z3kOu7iVd0RZxX94s_UK0KqJGO2oGj-ijJChO_c234MsA_0dBNmCInQuS_NSjFb9x83buMcJMCtqbCylR0iGHU5vuH_Ba_9g=676CC7D2"  # Replace with your token
USER_EMAIL = "sewminiweerakkody1004@gmail.com"  # Replace with the user's email

# OpenRouter API details
OPENROUTER_API_KEY = "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"  # Replace with your OpenRouter API key

# Initialize OpenAI client for OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)


# Function to fetch commit data from Bitbucket
def get_commit_data():
    API_URL = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/commits?pagelen=2&author={USER_EMAIL}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

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

        return commit_data
    else:
        print("Error fetching commits:", response.status_code, response.text)
        return None


# **Copied the same function below without any modifications**
def get_commit_data_copy():
    API_URL = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/commits?pagelen=2&author={USER_EMAIL}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

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

        return commit_data
    else:
        print("Error fetching commits:", response.status_code, response.text)
        return None


# Function to analyze commits with LLM
def analyze_commits_with_llm(commit_data):
    # Placeholder function to analyze commits
    # Replace with actual implementation
    print("Analyzing commits with LLM...")
    for commit in commit_data:
        print(f"Commit {commit['commit_hash']}: {commit['message']}")

# Main execution
if __name__ == "__main__":
    # Fetch commit data using the original function
    commit_data = get_commit_data()

    # Analyze commits with LLM (no need to use the copied function)
    analyze_commits_with_llm(commit_data)
