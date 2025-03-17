import sys
import requests
import json
from openai import OpenAI

# Set the console encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Bitbucket API details
WORKSPACE = "slttest1"  # Replace with your workspace
REPO_SLUG = "test1"  # Replace with your repository slug
BITBUCKET_ACCESS_TOKEN = "ATCTT3xFfGN0CFPRsEATPT8GgX-PamvnKrGFjqXKyCC8ZN0ZI2pnsBUS7-7J0Ig1dposHf6UOsHabOffY360mK3z3kOu7iVd0RZxX94s_UK0KqJGO2oGj-ijJChO_c234MsA_0dBNmCInQuS_NSjFb9x83buMcJMCtqbCylR0iGHU5vuH_Ba_9g=676CC7D2"  # Replaced ACCESS_TOKEN
USER_EMAIL = "sewminiweerakkody1004@gmail.com"  # Replace with the user's email


OPENROUTER_API_KEY = "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"  # Replace with your OpenRouter API key

# Initialize OpenAI client for OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def get_specific_commit_data(commit_hash):
    """Fetch data for a specific commit hash including its diff"""
    API_URL = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/commit/{commit_hash}"
    headers = {"Authorization": f"Bearer {BITBUCKET_ACCESS_TOKEN}"}

    response = requests.get(API_URL, headers=headers)
    if response.status_code == 200:
        commit = response.json()
        commit_data = []
        
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
            "date": commit["date"],
            "message": commit["message"],
            "code_changes": {
                "added": added_code,
                "removed": removed_code
            }
        })

        return commit_data
    else:
        print("Error fetching commit:", response.status_code, response.text)
        return None

def analyze_commits_with_llm(commit_data):
    if not commit_data:
        print("No commit data available.")
        return

    # Construct the prompt
    prompt = """  
Evaluate the developer's performance based on the following commit. Focus on:  

1. **Code Impact**:  
   - Are the changes meaningful (e.g., new features, bug fixes, logic improvements)?  
   - Is the ratio of meaningful changes high compared to trivial changes (e.g., whitespace, formatting)?  
   - Fewer lines of code with high impact is a plus.  

2. **Time Efficiency**:  
   - Consider the time taken for the work relative to the complexity of the changes.  

**Output Format**:  
- Performance: [Average/Below Average/Above Average]  
- Summary: One sentence highlighting a **specific strength/weakness** in their work.  
"""  

    for commit in commit_data:
        prompt += f"\nCommit Hash: {commit['commit_hash']}\n"
        prompt += f"Date: {commit['date']}\n"
        prompt += f"Message: {commit['message']}\n"
        prompt += "Added Code:\n"
        prompt += "\n".join(commit['code_changes']['added'][:500]) + "\n"  # Limit to first 500 lines
        prompt += "Removed Code:\n"
        prompt += "\n".join(commit['code_changes']['removed'][:500]) + "\n"

    # Send request to OpenRouter API
    response = client.chat.completions.create(
        model="deepseek/deepseek-r1:free",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
        temperature=0.3,
        extra_headers={
            "HTTP-Referer": "<YOUR_SITE_URL>",
            "X-Title": "<YOUR_SITE_NAME>",
        },
    )

    # Print the response
    if response.choices:
        print(response.choices[0].message.content)
    else:
        print("API request failed!")

# Main execution
if __name__ == "__main__":
    # Get commit hash from user input
    commit_hash = input("Enter the commit hash to analyze: ")
    
    # Fetch commit data
    commit_data = get_specific_commit_data(commit_hash)
    
    # Analyze commit with LLM
    if commit_data:
        analyze_commits_with_llm(commit_data)
    else:
        print("Failed to fetch commit data")