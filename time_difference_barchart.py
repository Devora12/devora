import sys
import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime

# Set the console encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Bitbucket API configuration
WORKSPACE = "slttest1"  # Replace with your workspace
REPO_SLUG = "test1"     # Replace with your repository slug
ACCESS_TOKEN = "ATCTT3xFfGN0CFPRsEATPT8GgX-PamvnKrGFjqXKyCC8ZN0ZI2pnsBUS7-7J0Ig1dposHf6UOsHabOffY360mK3z3kOu7iVd0RZxX94s_UK0KqJGO2oGj-ijJChO_c234MsA_0dBNmCInQuS_NSjFb9x83buMcJMCtqbCylR0iGHU5vuH_Ba_9g=676CC7D2"  # Replace with your token
USER_EMAIL = "sewminiweerakkody1004@gmail.com"  # Replace with user email
BRANCH_NAME = "testcase2"    # Replace with target branch name

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
        date = commit["date"]
        commit_data.append({
            "commit_hash": commit_hash,
            "date": date,
        })

    return commit_data

def calculate_total_time(commit_data):
    """Calculate total time taken by the user"""
    commit_data.sort(key=lambda x: datetime.fromisoformat(x["date"].replace("Z", "+00:00")))
    if len(commit_data) < 2:
        return 0  # Not enough commits to calculate total time
    start_time = datetime.fromisoformat(commit_data[0]["date"].replace("Z", "+00:00"))
    end_time = datetime.fromisoformat(commit_data[-1]["date"].replace("Z", "+00:00"))
    total_time = (end_time - start_time).total_seconds() / 3600  # Convert to hours
    return total_time

def plot_total_time_barchart(user_time, industrial_time):
    """Plot total time taken by the user vs industrial expected time in a bar chart"""
    labels = ["User Time Taken", "Industrial Expected Time"]
    values = [user_time, industrial_time]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values, color=['skyblue', 'orange'], edgecolor='black')

    # Annotate the bars with their values
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,  # X-coordinate (center of the bar)
            height + 0.2,  # Y-coordinate (slightly above the bar)
            f"{height:.2f} hours",  # Text to display
            ha='center',  # Horizontal alignment
            va='bottom',  # Vertical alignment
            fontsize=10,  # Font size
            color='black'  # Text color
        )

    # Adjust the Y-axis limits to add extra space above the tallest bar
    plt.ylim(0, max(values) + 1)  # Add 5 units of padding above the tallest bar

    # Add labels and title
    plt.ylabel("Time (hours)")
    plt.title("Total Time: User vs Industrial Expected")
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Show the chart
    plt.show()

if __name__ == "__main__":
    # Fetch commit data
    commits = get_commit_data()
    
    if commits:
        # Calculate total time taken by the user
        user_time = calculate_total_time(commits)

        # Assume industrial expected time (e.g., 2 hours per commit)
        industrial_time = len(commits) * 2  # 2 hours per commit

        # Plot the total time comparison in a bar chart
        plot_total_time_barchart(user_time, industrial_time)
    else:
        print("No commits found matching criteria")