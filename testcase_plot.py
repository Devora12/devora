import sys
import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime
from openai import OpenAI

# Set the console encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Bitbucket API configuration
WORKSPACE = "slttest1"  # Replace with your workspace
REPO_SLUG = "test1"     # Replace with your repository slug
ACCESS_TOKEN = "ATCTT3xFfGN0CFPRsEATPT8GgX-PamvnKrGFjqXKyCC8ZN0ZI2pnsBUS7-7J0Ig1dposHf6UOsHabOffY360mK3z3kOu7iVd0RZxX94s_UK0KqJGO2oGj-ijJChO_c234MsA_0dBNmCInQuS_NSjFb9x83buMcJMCtqbCylR0iGHU5vuH_Ba_9g=676CC7D2"  # Replace with your token
USER_EMAIL = "sewminiweerakkody1004@gmail.com"  # Replace with user email
BRANCH_NAME = "TestCase1"    # Replace with target branch name

# OpenRouter API details
OPENROUTER_API_KEY = "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"  # Replace with your OpenRouter API key

# Initialize OpenAI client for OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def get_commit_data():
    """Fetch commits from specific branch with diffs"""
    API_URL = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/commits/{BRANCH_NAME}?exclude=main"
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
        date = commit["date"]
        commit_data.append({
            "commit_hash": commit_hash,
            "author": author,
            "branch": branch,
            "date": date,
            "message": commit["message"].strip(),
        })

    return commit_data

def calculate_time_differences(commit_data):
    """Calculate time differences between commits"""
    commit_data.sort(key=lambda x: datetime.fromisoformat(x["date"].replace("Z", "+00:00")))
    time_differences = []
    for i in range(1, len(commit_data)):
        time1 = datetime.fromisoformat(commit_data[i - 1]["date"].replace("Z", "+00:00"))
        time2 = datetime.fromisoformat(commit_data[i]["date"].replace("Z", "+00:00"))
        time_diff = (time2 - time1).total_seconds() / 3600  # Convert to hours
        time_differences.append(time_diff)
    return time_differences

def plot_time_analysis(user_times, average_times):
    """Plot user times vs industrial average times"""
    plt.figure(figsize=(10, 6))
    x = range(1, len(user_times) + 1)
    plt.plot(x, user_times, label="User Time Taken", marker="o")
    plt.plot(x, average_times, label="Industrial Average Time", marker="x")
    plt.xlabel("Commit Index")
    plt.ylabel("Time Taken (hours)")
    plt.title("Time Analysis: User vs Industrial Average")
    plt.legend()
    plt.grid(True)
    plt.show()

def analyze_commits_with_llm(commit_data):
    """Analyze commits and plot time analysis"""
    if not commit_data:
        print("No commit data available.")
        return

    # Calculate time differences between commits
    user_times = calculate_time_differences(commit_data)

    # Assume industrial average time for each commit is 2 hours
    average_times = [2] * len(user_times)

    # Plot the time analysis
    plot_time_analysis(user_times, average_times)

if __name__ == "__main__":
    # Fetch commit data
    commits = get_commit_data()
    
    if commits:
        # Analyze commits and plot time analysis
        analyze_commits_with_llm(commits)
    else:
        print("No commits found matching criteria")