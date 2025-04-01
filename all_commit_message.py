import sys
import requests
import json
import re
import matplotlib.pyplot as plt
from datetime import datetime
from openai import OpenAI

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
    while API_URL:
        response = requests.get(API_URL, headers=headers)
        if response.status_code == 200:
            data = response.json()
            commits = data.get("values", [])
            for commit in commits:
                if str(testcase_id) in commit["message"]:
                    matching_commits.append({
                        "hash": commit["hash"],
                        "date": commit["date"],
                        "message": commit["message"].strip(),
                        "author": commit["author"]["raw"]
                    })
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

def get_commit_changes(commit_hash):
    """Get code changes for a specific commit"""
    diff_url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/diff/{commit_hash}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(diff_url, headers=headers)
    added_code = []
    removed_code = []
    if response.status_code == 200:
        diff_content = response.text
        for line in diff_content.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                added_code.append(line[1:])
            elif line.startswith('-') and not line.startswith('---'):
                removed_code.append(line[1:])
    return {"added": added_code, "removed": removed_code}

def calculate_user_time(commits):
    """Calculate time taken by the developer as the difference (in hours) 
       between the earliest and latest commit from the matching commits."""
    if len(commits) < 2:
        return 0.0
    sorted_commits = sorted(commits, key=lambda c: datetime.fromisoformat(c["date"].replace("Z", "+00:00")))
    start = datetime.fromisoformat(sorted_commits[0]["date"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(sorted_commits[-1]["date"].replace("Z", "+00:00"))
    return (end - start).total_seconds() / 3600.0

def analyze_commits_with_llm(commits):
    """Send commit code changes to LLM to predict expected industrial time.
       LLM should return:
       industrial time: Y.YY hours
       analysis: [detailed analysis]
    """
    if not commits:
        return None
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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"
    )
    try:
        prompt = (
            "Analyze the following commits and their code changes. "
            "Only consider commits with code changes. "
            "Based on similar GitHub projects and industry standards, predict how many hours "
            "an average developer would take to implement these changes.\n"
            "Format your answer exactly as follows:\n"
            "industrial time: Y.YY hours\n"
            "analysis: [detailed analysis]\n"
        )
        for commit in commits:
            prompt += f"\nCommit: {commit['hash']}\n"
            prompt += f"Message: {commit['message']}\n"
            changes = get_commit_changes(commit['hash'])
            print(f"DEBUG: Commit {commit['hash']} changes:", changes)
            if changes['added'] or changes['removed']:
                if changes['added']:
                    prompt += "Added code:\n" + "\n".join(changes['added']) + "\n"
                if changes['removed']:
                    prompt += "Removed code:\n" + "\n".join(changes['removed']) + "\n"
            else:
                prompt += "No code changes found for this commit.\n"
        
        # Print a preview of the prompt for debugging.
        print("DEBUG: Full prompt preview (first 1000 characters):")
        print(prompt[:1000])
        
        response = client.chat.completions.create(
            model="anthropic/claude-2",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500
        )
        if response and response.choices:
            return response.choices[0].message.content
        else:
            return "industrial time: 0.00 hours\nanalysis: Error analyzing commits"
    except Exception as e:
        print(f"Error in LLM analysis: {str(e)}")
        return "industrial time: 0.00 hours\nanalysis: Error during analysis"

def plot_time_comparison(user_time, industrial_time):
    """Plot bar chart comparing computed user time and LLM predicted industrial time"""
    labels = ["User Time Taken", "Industrial Expected Time"]
    values = [user_time, industrial_time]
    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values, color=['skyblue', 'orange'], edgecolor='black')
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height + 0.5,
                 f"{height:.2f} hours", ha='center', va='bottom')
    plt.ylabel("Time (hours)")
    plt.title("Time Comparison: User vs Industrial Average")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.ylim(0, max(values) + 5)
    plt.show()

def print_commit_changes(commits):
    """Print the added and removed code for each commit."""
    for commit in commits:
        changes = get_commit_changes(commit["hash"])
        print(f"\nCommit: {commit['hash']}")
        print(f"Message: {commit['message']}")
        if changes['added']:
            print("Added code:")
            for line in changes['added']:
                print(f"  + {line}")
        else:
            print("No added code.")
        if changes['removed']:
            print("Removed code:")
            for line in changes['removed']:
                print(f"  - {line}")
        else:
            print("No removed code.")
        print("-" * 60)

if __name__ == "__main__":
    testcase_id = "202503002"
    print(f"🔎 Searching for commits containing testcase ID: {testcase_id}")
    matching_commits = find_commits_by_testcase(testcase_id)
    print_matching_commits(matching_commits, testcase_id)
    
    # Print the code changes for each commit
    print("\n📄 Commit Code Changes:")
    print_commit_changes(matching_commits)