import sys
import requests
import json
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

def analyze_commits_with_llm(commit_data):
    if not commit_data:
        print("No commit data available.")
        return

    # Construct the prompt with all commits
    prompt = """  
Analyze the following commits, their timestamps, and the work done by the developer. Focus on the following:

1. **Time Taken by the Developer**:
   - Calculate the total time taken by the developer to complete all the commits (from the first commit to the last commit).
   - Provide a breakdown of the time taken between each commit (time difference between consecutive commits).

2. **Work Analysis**:
   - Evaluate the nature of the work done in each commit (e.g., new features, bug fixes, refactoring, etc.).
   - Assess the complexity of the changes (e.g., number of lines added/removed, impact of changes).

3. **Comparison to Average Developer**:
   - Based on your general knowledge, estimate how much time an average developer would take to complete the same tasks.
   - Compare the time taken by this developer to the estimated average time.
   - Highlight any significant deviations (e.g., if the developer took significantly longer or shorter than expected).

4. **Performance Summary**:
   - Provide an overall performance summary of the developer based on the time taken and the quality/complexity of the work.
   - Suggest areas for improvement or strengths that stand out.

**Output Format**:
- Total Time Taken by Developer: [Total time in hours/days]
- Time Breakdown Between Commits: [List of time differences between commits]
- Estimated Average Time for Task: [Estimated time in hours/days]
- Comparison to Average: [Faster/Slower/On Par]
- Performance Summary: [Brief summary of performance]
- Suggestions: [Any suggestions for improvement or recognition of strengths] 
"""  

    for commit in commit_data:
        prompt += f"Commit Hash: {commit['commit_hash']}\n"
        prompt += f"Date: {commit['date']}\n"
        prompt += f"Message: {commit['message']}\n"
        prompt += "Added Code:\n"
        prompt += "\n".join(commit['code_changes']['added']) + "\n"
        prompt += "Removed Code:\n"
        prompt += "\n".join(commit['code_changes']['removed']) + "\n\n"

    # Send request to OpenRouter API
    response = client.chat.completions.create(
        model="deepseek/deepseek-r1:free",  # Use DeepSeek model via OpenRouter
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,  # Adjust as needed
        temperature=0.3,  # Lower for more focused responses
        extra_headers={
            "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional. Site URL for rankings on openrouter.ai.
            "X-Title": "<YOUR_SITE_NAME>",  # Optional. Site title for rankings on openrouter.ai.
        },
    )

    # Print the response
    if response.choices:
        print("✅ API is working! Full Response:")
        print(response.choices[0].message.content)
    else:
        print("❌ API request failed!")
        print("Response:", response)

# Main execution
if __name__ == "__main__":
    # Fetch commit data
    commits = get_commit_data()
    
    if commits:
        # Analyze commits with LLM
        analyze_commits_with_llm(commits)
    else:
        print("No commits found matching criteria")