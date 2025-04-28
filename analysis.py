from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
import requests
import re
import json
from datetime import datetime, timedelta
from urllib.parse import unquote
from openai import OpenAI

load_dotenv()



app = Flask(__name__)
CORS(app)

# MongoDB setup
client = MongoClient(os.getenv("MONGODB_URI"))
db = client.QA_MANAGEMENT

# Google Calendar API configuration for holidays from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
encoded_calendar_id = CALENDAR_ID.replace('@', '%40').replace('#', '%23')
calendar_url = f'https://www.googleapis.com/calendar/v3/calendars/{encoded_calendar_id}/events'

# LLM API Configuration from environment variables
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_MODEL = os.getenv("LLM_MODEL")

def get_bitbucket_config(testcase_id=None, project=None):
    """Get Bitbucket config from project hierarchy or provided project"""
    if project:
        return {
            "workspace": project['workspace'],
            "repo_slug": project['repo_slug'],
            "access_token": unquote(project['repo_token'])  # Decode URL-encoded token
        }
    
    # If no project provided, find it based on testcase_id
    testcase = db.testcases.find_one({"testCaseId": testcase_id})
    if not testcase:
        raise ValueError("Test case not found")
    
    test_module = db.testmodules.find_one({"id": testcase['testModuleId']})
    if not test_module:
        raise ValueError("Test module not found")
    
    project = db.projects.find_one({"id": test_module['projectId']})
    if not project:
        raise ValueError("Project not found")
    
    return {
        "workspace": project['workspace'],
        "repo_slug": project['repo_slug'],
        "access_token": unquote(project['repo_token'])
    }

def get_commit_changes(commit_hash, bb_config):
    """
    Fetch diff from Bitbucket for a given commit and parse changes file by file.
    Returns a structure that maps file names to a dict with "added" and "removed" lists.
    """
    diff_url = f"https://api.bitbucket.org/2.0/repositories/{bb_config['workspace']}/{bb_config['repo_slug']}/diff/{commit_hash}"
    headers = {"Authorization": f"Bearer {bb_config['access_token']}"}
    response = requests.get(diff_url, headers=headers)
    file_changes = {}
    current_file = None

    if response.status_code == 200:
        for line in response.text.splitlines():
            # Detect start of a file diff block. Pattern "diff --git a/FILE b/FILE"
            if line.startswith("diff --git"):
                parts = line.split()
                if len(parts) >= 4:
                    # Use the filename from b/ portion
                    file_name = parts[3][2:] if parts[3].startswith("b/") else parts[3]
                    current_file = file_name
                    file_changes[current_file] = {"added": [], "removed": []}
                continue
            # Skip header lines for the file
            if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
                continue
            # Otherwise, classify added/removed lines if a file block is active
            if current_file:
                if line.startswith('+'):
                    file_changes[current_file]["added"].append(line[1:])
                elif line.startswith('-'):
                    file_changes[current_file]["removed"].append(line[1:])
    return file_changes

def find_commits_by_testcase(testcase_id, bb_config, pattern_type="exact"):
    """
    Find commits related to a test case ID using the specified pattern type:
    - "exact": Match the exact test case ID
    - "format": Match TestCaseID: 'ID' format
    """
    api_url = f"https://api.bitbucket.org/2.0/repositories/{bb_config['workspace']}/{bb_config['repo_slug']}/commits"
    headers = {"Authorization": f"Bearer {bb_config['access_token']}"}
    
    if pattern_type == "exact":
        pattern = re.compile(rf"\b{testcase_id}\b")
    else:  # format
        pattern = re.compile(rf"TestCaseID: '{testcase_id}'")
    
    commits = []
    while api_url:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            for commit in data.get("values", []):
                if pattern.search(commit["message"]):
                    changes = get_commit_changes(commit["hash"], bb_config)
                    commits.append({
                        "hash": commit["hash"],
                        "date": commit["date"],
                        "message": commit["message"].strip(),
                        "author": commit["author"]["raw"],
                        "code_changes": changes
                    })
            api_url = data.get('next')
        else:
            return {"error": f"Error fetching commits: {response.status_code}"}, 500
    
    return commits

def get_holidays(start, end):
    """Fetch holiday events between start and end dates."""
    time_min = start.strftime('%Y-%m-%dT%H:%M:%SZ')
    time_max = end.strftime('%Y-%m-%dT%H:%M:%SZ')

    params = {
        'key': GOOGLE_API_KEY,
        'timeMin': time_min,
        'timeMax': time_max,
        'singleEvents': True,
        'orderBy': 'startTime',
        'maxResults': 100,
    }

    response = requests.get(calendar_url, params=params)
    data = response.json()

    holidays = {}
    for event in data.get('items', []):
        date = event['start'].get('date')  # all-day events
        holiday_name = event.get('summary', 'Unknown Holiday')
        holidays[date] = holiday_name
    return holidays

def calculate_working_hours(start, end, holidays):
    """Calculate total working hours by deducting holidays and weekends from total duration."""
    # Calculate total duration in hours
    total_duration_hours = (end - start).total_seconds() // 3600
    total_duration_days = total_duration_hours / 24

    # Calculate holiday hours (24 hours per holiday), excluding the first day if it's a holiday
    holiday_hours = 0
    adjusted_holidays = set()
    for holiday in holidays:
        holiday_date = datetime.strptime(holiday, "%Y-%m-%d").date()
        if holiday_date != start.date() and holiday_date != end.date():
            holiday_hours += 24
            adjusted_holidays.add(holiday_date)

    # Calculate weekend hours
    weekend_hours = 0
    weekend_count = 0
    current_day = start.date()
    while current_day <= end.date():
        if current_day.weekday() in [5, 6]:  # Saturday (5) or Sunday (6)
            if current_day != start.date() and current_day != end.date():
                weekend_hours += 24
                weekend_count += 1
        current_day += timedelta(days=1)

    # Deduct holiday and weekend hours from total duration hours
    working_hours = total_duration_hours - holiday_hours - weekend_hours
    working_days = working_hours / 8  # Convert working hours to days (assuming 8-hour workday)

    # Adjust Total Working Hours (divide by 3 as per requirements)
    total_working_hours = working_hours / 3
    total_working_time_days = total_working_hours / 24

    return {
        "total_duration_hours": total_duration_hours,
        "total_duration_days": total_duration_days,
        "holiday_hours": holiday_hours,
        "holiday_count": len(adjusted_holidays),
        "weekend_hours": weekend_hours,
        "weekend_count": weekend_count,
        "working_hours": working_hours,
        "working_days": working_days,
        "total_working_hours": total_working_hours,
        "total_working_time_days": total_working_time_days
    }

def build_prompt(commits):
    """
    Build the prompt text for LLM analysis including commit details and file-specific code changes.
    """
    commit_list = []
    for commit in commits:
        file_list = []
        for file, changes in commit["code_changes"].items():
            file_text = (
                f"File: {file}\n"
                f"Added Code:\n" + "\n".join(changes["added"]) + "\n" +
                f"Removed Code:\n" + "\n".join(changes["removed"]) + "\n"
            )
            file_list.append(file_text)
        files_text = "\n".join(file_list)
        commit_text = (
            f"Commit: {commit['hash']}\n"
            f"Message: {commit['message']}\n"
            f"{files_text}\n"
        )
        commit_list.append(commit_text)
    commits_text = "\n".join(commit_list)
    
    prompt = (
"""
You are a highly experienced software engineering analyst trained on vast amounts of open-source code, GitHub commits, and real-world developer practices.
You are acting as a Senior Software Engineering Analyst and Tech Lead. Your task is to simulate a project post-mortem analysis of a full Git commit history as if preparing insights for a CTO.

I will provide you with a complete list of git commits and code diffs from a project.

Your task is to analyze the entire commit history as a whole, and:

1. Understand the overall nature of the work (e.g., new feature development, refactoring, bug fixing, testing, etc.).
2. Assess the total complexity based on all the changes — consider number of files, architectural depth, domain logic, cross-module impact, and technical difficulty.
3. Estimate how much time a typical industrial-level developer (3–5 years experience) would have taken (uninterupted working hours) to complete this entire set of commits.

🎯 Strictly follow this output format in JSON(very important need to be a valid JSON):

{
    "summary_of_change": "<as points>",
    "code_complexity": {"rating": <1 to 5>, "level": "<Low/Medium/High>"},
    "languages_used": "<language name>",
    "code_quality": {"rating": <1 to 5>, "level": "<Low/Medium/High>"},
    "code_readability": {"rating": <1 to 5>, "level": "<Low/Medium/High>"},
    "skills_gained": ["<skills gained as points>"],
    "recommendations": ["<recommendations as points>"],
    "code_review": "<provide a code review>",
    "estimated_time": {"hours": <A>}
    "developer_performance": {"rating": <1 to 5>, "level": "<Low/Medium/High>"},
}

Each point should feel like pro-level advice from an experienced tech lead doing a detailed review.

Use your knowledge from GitHub, open-source projects, and engineering standards to ground your estimates.
Be accurate, consistent, and insight-driven — do not rely on token count, file count, or hardcoded LOC rules.
The same input must always yield the same output.

"""
        f"{commits_text}"
    )
    return prompt

def analyze_with_llm(prompt):
    """Send the prompt to the LLM and return the analysis"""
    client = OpenAI(
        base_url=LLM_BASE_URL,
        api_key=LLM_API_KEY,
    )

    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "<YOUR_SITE_URL>",
                "X-Title": "<YOUR_SITE_NAME>",
            },
            extra_body={},
            model=LLM_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=12000,
            temperature=0.2,
        )
    except Exception as e:
        return {"error": f"Error during LLM API call: {str(e)}"}, 500

    if not completion or not completion.choices:
        return {"error": "No valid response from LLM API."}, 500

    return completion.choices[0].message.content

def parse_llm_output(llm_output):
    """Parse the LLM output and extract the JSON content"""
    if not llm_output:
        return None
    
    # Extract JSON content from the LLM output
    json_match = re.search(r"\{.*\}", llm_output, re.DOTALL)
    if json_match:
        llm_output = json_match.group(0)
    else:
        return None

    try:
        # Parse the JSON output
        return json.loads(llm_output)
    except json.JSONDecodeError as e:
        return None

# API Endpoints
@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Endpoint to get all projects"""
    try:
        projects = list(db.projects.find({}, {'_id': 0}))
        return jsonify({"status": "success", "data": projects})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/projects/<int:project_id>/modules', methods=['GET'])
def get_modules(project_id):
    """Endpoint to get test modules for a specific project"""
    try:
        modules = list(db.testmodules.find({"projectId": project_id}, {'_id': 0}))
        return jsonify({"status": "success", "data": modules})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/modules/<int:module_id>/testcases', methods=['GET'])
def get_testcases(module_id):
    """Endpoint to get test cases for a specific module"""
    try:
        testcases = list(db.testcases.find({"testModuleId": module_id}, {'_id': 0}))
        return jsonify({"status": "success", "data": testcases})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/testcases/<string:testcase_id>/analyze', methods=['GET'])
def analyze_testcase(testcase_id):
    """Endpoint to analyze a specific test case"""
    try:
        # Get Bitbucket configuration
        bb_config = get_bitbucket_config(testcase_id)
        
        # Find commits related to the test case
        exact_commits = find_commits_by_testcase(testcase_id, bb_config, "exact")
        format_commits = find_commits_by_testcase(testcase_id, bb_config, "format")
        all_commits = exact_commits + format_commits
        
        # Remove duplicates based on commit hash
        unique_commits = []
        commit_hashes = set()
        for commit in all_commits:
            if commit["hash"] not in commit_hashes:
                unique_commits.append(commit)
                commit_hashes.add(commit["hash"])
        
        # Sort commits by date
        unique_commits.sort(key=lambda x: x["date"])
        
        result = {
            "testcase_id": testcase_id,
            "commits": unique_commits,
        }
        
        # Calculate statistics
        commit_stats = {}
        for commit in unique_commits:
            developer = commit["author"]
            if developer in commit_stats:
                commit_stats[developer] += 1
            else:
                commit_stats[developer] = 1
        
        result["commit_statistics"] = commit_stats
        
        # Calculate time metrics if commits are available
        if unique_commits:
            # Extract commit dates
            commit_dates = [datetime.fromisoformat(commit["date"].replace("Z", "+00:00")) for commit in unique_commits]
            start_time = min(commit_dates)
            end_time = max(commit_dates)
            
            result["time_metrics"] = {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration": str(end_time - start_time)
            }
            
            # Fetch holidays
            holidays = get_holidays(start_time, end_time)
            result["holidays"] = holidays
            
            # Calculate working hours
            working_hours = calculate_working_hours(start_time, end_time, holidays)
            result["working_hours"] = working_hours
        
        return jsonify({"status": "success", "data": result})
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/testcases/<string:testcase_id>/llm-analysis', methods=['GET'])
def llm_analyze_testcase(testcase_id):
    """Endpoint to perform LLM analysis on a test case and save results"""
    try:
        # Get Bitbucket configuration
        bb_config = get_bitbucket_config(testcase_id)
        
        # Find commits related to the test case
        exact_commits = find_commits_by_testcase(testcase_id, bb_config, "exact")
        format_commits = find_commits_by_testcase(testcase_id, bb_config, "format")
        all_commits = exact_commits + format_commits
        
        # Remove duplicates based on commit hash
        unique_commits = []
        commit_hashes = set()
        for commit in all_commits:
            if commit["hash"] not in commit_hashes:
                unique_commits.append(commit)
                commit_hashes.add(commit["hash"])
        
        # Sort commits by date
        unique_commits.sort(key=lambda x: x["date"])
        
        if not unique_commits:
            return jsonify({"status": "error", "message": "No commits found for this test case"}), 404
        
        # Extract commit dates for time metrics
        commit_dates = [datetime.fromisoformat(commit["date"].replace("Z", "+00:00")) for commit in unique_commits]
        start_time = min(commit_dates)
        end_time = max(commit_dates)
        duration = str(end_time - start_time)
        
        # Format commits to match schema
        formatted_commits = []
        for commit in unique_commits:
            formatted_commit = {
                "hash": commit["hash"],
                "message": commit["message"],
                "date": datetime.fromisoformat(commit["date"].replace("Z", "+00:00")),
                "author": commit["author"],
                "codeChanges": commit["code_changes"]  # Map of file changes
            }
            formatted_commits.append(formatted_commit)
        
        # Prepare commit details
        commit_details = {
            "startTime": start_time,
            "endTime": end_time,
            "duration": duration,
            "commits": formatted_commits
        }
        
        # Build prompt for LLM
        prompt = build_prompt(unique_commits)
        
        # Send to LLM and get analysis
        llm_output = analyze_with_llm(prompt)
        
        if isinstance(llm_output, tuple) and len(llm_output) == 2 and isinstance(llm_output[0], dict) and 'error' in llm_output[0]:
            return jsonify({"status": "error", "message": llm_output[0]['error']}), llm_output[1]
        
        # Parse the output
        analysis = parse_llm_output(llm_output)
        
        if not analysis:
            return jsonify({"status": "error", "message": "Failed to parse LLM output"}), 500
        
        # Format the analysis to match the schema
        formatted_analysis = {
            "summary_of_change": analysis.get("summary_of_change", []),
            "code_complexity": analysis.get("code_complexity", {}),
            "code_quality": analysis.get("code_quality", {}),
            "code_readability": analysis.get("code_readability", {}),
            "skills_gained": analysis.get("skills_gained", []),
            "recommendations": analysis.get("recommendations", []),
            "code_review": analysis.get("code_review", ""),
            "estimated_time": analysis.get("estimated_time", {}),
            "developer_performance": analysis.get("developer_performance", {}),
            "languages_used": analysis.get("languages_used", "")
        }
        
        # Convert summary_of_change to array if it's a string
        if isinstance(formatted_analysis["summary_of_change"], str):
            formatted_analysis["summary_of_change"] = [item.strip() for item in formatted_analysis["summary_of_change"].split('\n') if item.strip()]
        
        # Get test case details (objective)
        testcase = db.testcases.find_one({"testCaseId": testcase_id}, {'_id': 0})
        objective = testcase.get('objective', '') if testcase else ''
        
        # Prepare the analysis result document
        analysis_result = {
            "testCaseId": testcase_id,
            "objective": objective,
            "status": "completed",
            "commitDetails": commit_details,
            "llmAnalysis": formatted_analysis,
            "lastUpdated": datetime.utcnow(),
            "created": datetime.utcnow()
        }
        
        # Insert or update in MongoDB (upsert)
        db.analysis_results.update_one(
            {"testCaseId": testcase_id},
            {"$set": analysis_result},
            upsert=True
        )
        
        return jsonify({
            "status": "success", 
            "data": analysis,
            "saved": True
        })
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint to check API health"""
    return jsonify({"status": "ok"})

@app.route('/api/testcases/<string:testcase_id>', methods=['GET'])
def get_testcase(testcase_id):
    """Endpoint to get a single test case by ID"""
    try:
        testcase = db.testcases.find_one({"testCaseId": testcase_id}, {'_id': 0})
        if not testcase:
            return jsonify({"status": "error", "message": "Test case not found"}), 404
        return jsonify({"status": "success", "data": testcase})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

