import sys
import requests
import json

# Set the console encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Bitbucket API details
WORKSPACE = "slttest1"  # Replace with your workspace
REPO_SLUG = "test1"     # Replace with your repository slug
ACCESS_TOKEN = "ATCTT3xFfGN0CFPRsEATPT8GgX-PamvnKrGFjqXKyCC8ZN0ZI2pnsBUS7-7J0Ig1dposHf6UOsHabOffY360mK3z3kOu7iVd0RZxX94s_UK0KqJGO2oGj-ijJChO_c234MsA_0dBNmCInQuS_NSjFb9x83buMcJMCtqbCylR0iGHU5vuH_Ba_9g=676CC7D2"  # Replace with your token
USER_EMAIL = "2021t01245@stu.cmb.ac.lk"  # Replace with the user's email

# Together AI API details
API_KEY = "bdc41d8567888349149e521dfb8351ce46323cbe5b28282ce32b9e13c574f8d3"  # Replace with your actual Together AI API key
MODEL = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free"  # Use an available model

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

# Function to send commit data to Together AI API
def analyze_commits_with_llm(commit_data):
    if not commit_data:
        print("No commit data available.")
        return

    # Construct the prompt with both commits
    prompt = """  
Evaluate the developer's performance based **only on their last commit** (ignore security practices like hardcoded keys). Focus on:  

1. **Code Impact**:  
   - Ratio of meaningful code (e.g., logic, features) vs. trivial changes (comments, whitespace).  
   - Efficiency: Fewer lines with high impact is a plus.  

2. **Commit Message Alignment**:  
   - Does the message clearly describe the actual work done?  
   - Is it vague or misleading (e.g., "bug fix" without details)?  

3. **Time Efficiency**:  
   - If the time taken is unusually long for the scope of work, note it.  

4. **Potential Misleading Behavior**:  
   - Flag if the commit inflates activity (e.g., minor formatting to show progress).  

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

    # Create the payload for the Together AI API
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 7500,  # Increase token limit
        "temperature": 0.7  # Optional: Adjust creativity (0.7 is balanced)
    }

    # Send request to Together AI API
    response = requests.post(
        "https://api.together.xyz/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json=payload
    )

    # Print the response
    if response.status_code == 200:
        print("✅ API is working! Full Response:")
        print(response.json()["choices"][0]["message"]["content"])
    else:
        print("❌ API request failed!")
        print("Status Code:", response.status_code)
        print("Response:", response.text)

# Main execution
if __name__ == "__main__":
    # Fetch commit data
    commit_data = get_commit_data()

    # Analyze commits with LLM
    analyze_commits_with_llm(commit_data)