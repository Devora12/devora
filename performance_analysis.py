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
    headers = {"Authorization": f"Bearer {BITBUCKET_ACCESS_TOKEN}"}  # Updated variable name

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


# Function to send commit data to OpenRouter API
def analyze_commits_with_llm(commit_data):
    if not commit_data:
        print("No commit data available.")
        return

    # Construct the prompt with both commits
    prompt = """  
Evaluate the developer's performance based **only on their last commit**. Focus on:  

1. **Code Impact**:  
   - Are the changes meaningful (e.g., new features, bug fixes, logic improvements)?  
   - Is the ratio of meaningful changes high compared to trivial changes (e.g., whitespace, formatting)?  
   - Fewer lines of code with high impact is a plus.  

2. **Time Efficiency**:  
   - Compare the time taken for the work to the expected time for similar tasks.  
   - If the developer took significantly longer than expected (e.g., 2 weeks for 2 days of work), note it as a concern.  

**Output Format**:  
- Performance: [Average/Below Average/Above Average]  
- Summary: One sentence highlighting a **specific strength/weakness** in their work.  
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
    commit_data = get_commit_data()

    # Analyze commits with LLM
    analyze_commits_with_llm(commit_data)
