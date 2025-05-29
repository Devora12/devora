from pymongo import MongoClient
import requests
import re
import json  # Add this import
from datetime import datetime, timedelta

# Replace the following URI with your actual MongoDB Atlas connection string

uri = "mongodb+srv://udanaravindurv:9wu9GDMrXNgPQqFv@cluster0.iofqwq5.mongodb.net/QA_MANAGEMENT?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB
client = MongoClient(uri)

# Access a specific database
db = client["QA"]

# Access a specific collection
projects_collection = db["projects"]
testmodules_collection = db["testmodules"]
testcases_collection = db["testcases"]

commits_collection = db["devora_commits"]
function_collection = db["devora_functions"]


def step1(testCaseId):
    """
    Retrieves all test cases related to the project of the given testCaseId and returns the projectId,
    along with repo_slug, repo_token, and workspace from the projects_collection.
    
    Args:
        testCaseId (str): The ID of the test case to start the lookup.
    
    Returns:
        tuple: A dictionary with testCaseId as keys and their statuses as values,
               the projectId, repo_slug, repo_token, and workspace.
    """
    # Step 1: Retrieve testModuleId from testcases collection
    testcase_document = testcases_collection.find_one(
        {"testCaseId": testCaseId},  # Query filter
        {"testModuleId": 1, "_id": 0}  # Projection to include testModuleId and exclude _id
    )

    if testcase_document and "testModuleId" in testcase_document:
        testModuleId = testcase_document["testModuleId"]
        print("\nStep 1: Extracted testModuleId:", testModuleId)

        # Step 2: Retrieve projectId from testmodules collection using testModuleId
        testmodule_document = testmodules_collection.find_one(
            {"id": testModuleId},  # Query filter (match by id in testmodules)
            {"projectId": 1, "_id": 0}  # Projection to include projectId and exclude _id
        )

        if testmodule_document and "projectId" in testmodule_document:
            try:
                projectId = int(testmodule_document["projectId"])
                print("\nStep 2: Extracted projectId:", projectId)

                # Step 3: Retrieve repo_slug, repo_token, and workspace from projects_collection
                project_document = projects_collection.find_one(
                    {"id": projectId},  # Query filter to match projectId
                    {"repo_slug": 1, "repo_token": 1, "workspace": 1, "_id": 0}  # Projection to include required fields
                )
            except (ValueError, TypeError) as e:
                print(f"\nError: Could not convert projectId to integer: {str(e)}")
                projectId = None

            if project_document:
                repo_slug = project_document.get("repo_slug")
                repo_token = project_document.get("repo_token")
                workspace = project_document.get("workspace")
                print("\nStep 3: Extracted repo_slug:", repo_slug)
                print("\nStep 3: Extracted repo_token:", repo_token)
                print("\nStep 3: Extracted workspace:", workspace)

                # Step 4: Retrieve all testmodules for the project using projectId
                testmodules_cursor = testmodules_collection.find(
                    {"projectId": projectId},  # Query filter to match projectId
                    {"id": 1, "_id": 0}  # Projection to include id (testModuleId) and exclude _id
                )

                # Convert cursor to a list of testModuleIds
                testModuleIds = [doc["id"] for doc in testmodules_cursor]
                print("\nStep 4: Retrieved testModuleIds:", testModuleIds)

                if testModuleIds:
                    # Step 5: Retrieve all test cases for the testModuleIds
                    testcases_cursor = testcases_collection.find(
                        {"testModuleId": {"$in": testModuleIds}},  # Query filter to match testModuleIds
                        {"testCaseId": 1, "status": 1, "_id": 0}  # Projection to include testCaseId and status, exclude _id
                    )

                    # Convert cursor to a list for debugging
                    testcases_list = list(testcases_cursor)

                    # Store test cases in a dictionary
                    testcases_dict = {doc["testCaseId"]: doc["status"] for doc in testcases_list}
                    print("\nStep 5: Created testcases_dict:", testcases_dict)
                    return testcases_dict, projectId, repo_slug, repo_token, workspace
                else:
                    print("Step 4: No testmodules found for the given projectId.")
                    return {}, projectId, repo_slug, repo_token, workspace
            else:
                print("Step 3: No matching document found in projects collection.")
                return {}, projectId, None, None, None
        else:
            print("Step 2: No matching document found in testmodules collection.")
            return {}, None, None, None, None
    else:
        print("Step 1: No matching document found in testcases collection.")
        return {}, None, None, None, None
    
    
def get_commits(projectId):
    """
    Retrieves the latest commit hash for the given projectId based on date&time.

    Args:
        projectId (int): The ID of the project to retrieve the latest commit.

    Returns:
        str: The hash of the latest commit or None if no commits are found.
    """
    # Step 1: Query the commits collection for the given projectId
    latest_commit = commits_collection.find_one(
        {"project_id": int(projectId)},  # Ensure projectid is matched as an integer
        {"hash": 1, "_id": 0},  # Projection to include only the hash field
        sort=[("date", -1)]  # Sort by date&time in descending order to get the latest
    )

    # Step 2: Print and return the latest commit hash
    if latest_commit and "hash" in latest_commit:
        return latest_commit["hash"]
    else:
        print("No commits found in database. Looking for first valid commit in repository...")
        
        # Get the first page of commits from repository
        API_URL = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/commits"
        headers = {"Authorization": f"Bearer {repo_token}"}
        testcase_pattern = re.compile(r"testcase\s*:\s*\[([^\]]+)\]", re.IGNORECASE)
        
        try:
            # Add paginate parameter to get all commits
            API_URL_WITH_PARAMS = f"{API_URL}?pagelen=100"
            all_commits = []
            
            # Fetch all commits through pagination
            while API_URL_WITH_PARAMS:
                response = requests.get(API_URL_WITH_PARAMS, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    all_commits.extend(data.get("values", []))
                    API_URL_WITH_PARAMS = data.get("next")  # Move to next page if exists
                else:
                    print(f"Error fetching commits: {response.status_code}")
                    return None
            
            # Reverse the commits list to start from oldest to newest
            all_commits.reverse()
            
            # Look for the first valid commit
            for commit in all_commits:
                message = commit["message"].strip()
                match = testcase_pattern.search(message)
                if match:
                    testcases = [tc.strip() for tc in match.group(1).split(",")]
                    if all(tc in testcases_dict for tc in testcases):
                        # Prepare the commit document
                        commit_document = {
                            "hash": commit["hash"],
                            "date": commit["date"],
                            "message": message,
                            "author_username": commit["author"]["raw"].split("<")[0].strip(),
                            "author_email": commit["author"]["raw"].split("<")[1].strip(">").strip(),
                            "testcases": testcases,
                            "project_id": projectId,
                            "function": "no"
                        }

                        # Store the commit in the database
                        try:
                            commits_collection.insert_one(commit_document)
                            print(f"Stored first valid commit: {commit_document['hash']}")
                        except Exception as e:
                            print(f"Error storing first commit {commit_document['hash']}: {e}")
                            
                        print("Found first valid commit:", commit["hash"])
                        return commit["hash"]
            
            print("No valid commits found in repository.")
            return None
        except Exception as e:
            print(f"Error while fetching first valid commit: {str(e)}")
            return None


def get_commits_after_hash(latest_commit_hash, repo_slug, repo_token, workspace, testcases_dict):
    """
    Fetch, filter, and store commits made after the given commit hash from the Bitbucket repository.
    If the latest commit hash is not found in Bitbucket, iteratively check the next latest commit hash.

    Args:
        latest_commit_hash (str): The hash of the latest commit to start from.
        repo_slug (str): The repository slug.
        repo_token (str): The repository access token.
        workspace (str): The workspace name.
        testcases_dict (dict): A dictionary with testCaseId as keys and their statuses as values.

    Returns:
        list: A list of filtered commits that match the criteria.
    """
    API_URL = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/commits"
    headers = {"Authorization": f"Bearer {repo_token}"}
    filtered_commits = []

    # Regular expression to match the valid format for test cases
    testcase_pattern = re.compile(r"testcase\s*:\s*\[([^\]]+)\]", re.IGNORECASE)

    while latest_commit_hash:
        print(f"Checking for commits after hash: {latest_commit_hash}")
        found_in_bitbucket = False
        commits_to_store = []

        # Handle pagination
        next_url = API_URL
        while next_url:
            response = requests.get(next_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                commits = data.get("values", [])
                for commit in commits:
                    # Stop processing if we reach the latest commit hash
                    if commit["hash"] == latest_commit_hash:
                        print(f"Found the latest commit hash in Bitbucket: {latest_commit_hash}")
                        found_in_bitbucket = True
                        break

                    # Step 1: Check if the commit message has a valid format
                    message = commit["message"].strip()
                    match = testcase_pattern.search(message)
                    if match:
                        # Step 2: Extract test cases and validate against testcases_dict
                        testcases = [tc.strip() for tc in match.group(1).split(",")]
                        if all(tc in testcases_dict for tc in testcases):
                            # Convert UTC date to Sri Lanka time (UTC+5:30)
                            utc_time = datetime.fromisoformat(commit["date"].replace("Z", "+00:00"))
                            sri_lanka_time = utc_time + timedelta(hours=5, minutes=30)

                            # Prepare the commit document
                            commit_document = {
                                "hash": commit["hash"],
                                "date": sri_lanka_time.isoformat(),  # Save in Sri Lanka time
                                "message": message,
                                "author_username": commit["author"]["raw"].split("<")[0].strip(),
                                "author_email": commit["author"]["raw"].split("<")[1].strip(">").strip(),
                                "testcases": testcases,
                                "project_id": projectId,
                                "function": "no"
                            }
                            # Add the commit to the list of commits to store
                            commits_to_store.append(commit_document)

                if found_in_bitbucket:
                    break

                # Move to the next page of results
                next_url = data.get("next")
            else:
                print(f"Error fetching commits: {response.status_code}")
                break

        if found_in_bitbucket:
            # Store all commits made after the latest commit hash
            for commit_document in commits_to_store:
                try:
                    commits_collection.insert_one(commit_document)
                    print(f"Stored commit: {commit_document['hash']}")
                    filtered_commits.append(commit_document)
                except Exception as e:
                    print(f"Error storing commit {commit_document['hash']}: {e}")
            break

        # If the latest commit hash is not found, get the next latest commit from the database
        latest_commit = commits_collection.find_one(
            {"project_id": projectId, "date": {"$lt": commits_collection.find_one({"hash": latest_commit_hash})["date"]}},
            {"hash": 1, "_id": 0},
            sort=[("date", -1)]
        )
        if latest_commit:
            latest_commit_hash = latest_commit["hash"]
            print(f"Latest commit hash not found in Bitbucket. Trying next latest commit hash: {latest_commit_hash}")
        else:
            print("No more commits found in the database to check.")
            break

    return filtered_commits


def get_incomplete_commits(projectId):
    """
    Retrieves all commits from the project where function = 'no' (not completed).
    
    Args:
        projectId (int): The ID of the project.
        
    Returns:
        list: A list of incomplete commits.
    """
    # Query the commits collection for commits with function = 'no'
    incomplete_commits = list(commits_collection.find(
        {
            "project_id": int(projectId),
            "function": "no"
        }
    ))
    
    print(f"\nFound {len(incomplete_commits)} incomplete commits (function = 'no'):")
    for commit in incomplete_commits:
        print(f"Hash: {commit.get('hash')}, Author: {commit.get('author_username')}, TestCases: {commit.get('testcases')}")
    
    return incomplete_commits


def identify_completed_functions(incomplete_commits, testcases_dict):
    """
    Finds completed functions through the validation process using only incomplete commits:
    - All the testcases should be in 'PASS' status
    - Should be a minimum of 2 commits with exact testcases
    - Should be made by the same developer
    
    Args:
        incomplete_commits (list): List of commits with function='no'
        testcases_dict (dict): Dictionary of test cases and their statuses.
        
    Returns:
        list: A list of identified completed functions.
    """
    # Group incomplete commits by test cases and author
    commit_groups = {}
    
    for commit in incomplete_commits:
        testcases = commit.get('testcases', [])
        testcases.sort()
        testcases_tuple = tuple(testcases)
        author = commit.get('author_username')
        
        key = (author, testcases_tuple)
        
        if key not in commit_groups:
            commit_groups[key] = []
        
        commit_groups[key].append(commit)
    
    completed_functions = []
    
    for (author, testcases_tuple), commits in commit_groups.items():
        if len(commits) >= 2 and all(testcases_dict.get(tc) == "PASS" for tc in testcases_tuple):
            sorted_commits = sorted(commits, key=lambda x: x.get('date', ''))
            
            if len(sorted_commits) >= 2:
                first_commit = sorted_commits[0]
                last_commit = sorted_commits[-1]
                commit_hashes = [commit.get('hash') for commit in sorted_commits]
                
                # Calculate working hours between the first and last commit
                start_date = first_commit.get('date')
                end_date = last_commit.get('date')
                total_working_hours, total_working_time_days = calculate_working_hours(start_date, end_date)
                
                # Get test case and commit details
                testcase_details, commit_changes = get_testcase_and_commit_details(
                    list(testcases_tuple),
                    commit_hashes,
                    repo_slug,
                    repo_token,
                    workspace
                )
                
                # Get LLM analysis
                llm_analysis = get_llm_analysis(commit_changes, testcase_details)
                
                try:
                    # Handle different types of LLM output
                    if isinstance(llm_analysis, str):
                        # Clean the string and handle potential whitespace/newlines
                        llm_analysis = llm_analysis.strip()
                        if llm_analysis:
                            try:
                                llm_analysis = json.loads(llm_analysis)
                            except json.JSONDecodeError:
                                # If direct parsing fails, try to extract JSON from the string
                                json_match = re.search(r'\{.*\}', llm_analysis, re.DOTALL)
                                if json_match:
                                    llm_analysis = json.loads(json_match.group(0))
                                else:
                                    raise ValueError("Could not extract valid JSON from LLM output")
                    
                    # Create completed function document with metrics
                    completed_function = {
                        'author': author,
                        'testcases': list(testcases_tuple),
                        'first_commit': first_commit.get('hash'),
                        'first_commit_date': first_commit.get('date'),
                        'last_commit': last_commit.get('hash'),
                        'last_commit_date': last_commit.get('date'),
                        'commit_count': len(commits),
                        'project_id': first_commit.get('project_id'),
                        'commit_hashes': commit_hashes,
                        'metrics': {
                            'code_complexity': llm_analysis.get('code_complexity'),
                            'code_quality': llm_analysis.get('code_quality'),
                            'code_readability': llm_analysis.get('code_readability'),
                            'developer_performance': llm_analysis.get('developer_performance'),
                            'function_complexity': llm_analysis.get('function_complexity'),
                            'estimated_time': llm_analysis.get('estimated_time'),
                            'total_working_hours': total_working_hours,
                            'total_working_time_days': total_working_time_days
                        }
                    }
                    
                    # Store in function collection
                    function_collection.insert_one(completed_function)
                    completed_functions.append(completed_function)
                    
                    print(f"\nStored completed function for author {author}")
                    print(f"Test cases: {list(testcases_tuple)}")
                    print(f"Commit hashes in order: {commit_hashes}")
                    print("LLM Metrics:", completed_function['metrics'])
                    
                    # Update commit statuses
                    for commit in commits:
                        commits_collection.update_one(
                            {"_id": commit.get('_id')},
                            {"$set": {"function": "yes"}}
                        )
                        
                except Exception as e:
                    print(f"Error storing completed function: {str(e)}")
    
    print(f"\nIdentified {len(completed_functions)} completed functions:")
    for func in completed_functions:
        print(f"Author: {func.get('author')}")
        print(f"TestCases: {func.get('testcases')}")
        print(f"Commits ({func.get('commit_count')}): {func.get('commit_hashes')}")
        print("---")
    
    return completed_functions


def get_testcase_and_commit_details(testcases, commit_hashes, repo_slug, repo_token, workspace):
    """
    Retrieves test case details from MongoDB and commit changes from Bitbucket.
    
    Args:
        testcases (list): List of test case IDs
        commit_hashes (list): List of commit hashes in chronological order
        repo_slug (str): Repository slug
        repo_token (str): Repository access token
        workspace (str): Workspace name
        
    Returns:
        tuple: (testcase_details, commit_changes)
    """
    # Get testcase details from MongoDB
    testcase_details = {}
    for tc_id in testcases:
        tc_doc = testcases_collection.find_one(
            {"testCaseId": tc_id},
            {
                "testCaseId": 1,
                "testCase": 1,
                "objective": 1,
                "testData": 1,
                "testSteps": 1,
                "_id": 0
            }
        )
        if tc_doc:
            testcase_details[tc_id] = tc_doc

    # Get commit changes from Bitbucket
    commit_changes = {}
    headers = {"Authorization": f"Bearer {repo_token}"}
    
    for commit_hash in commit_hashes:
        url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/diffstat/{commit_hash}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            diff_data = response.json()
            
            # Get the detailed diff for this commit
            diff_url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/diff/{commit_hash}"
            diff_response = requests.get(diff_url, headers=headers)
            
            if diff_response.status_code == 200:
                commit_changes[commit_hash] = {
                    'stats': diff_data.get('values', []),
                    'diff': diff_response.text
                }
            else:
                print(f"Error getting diff for commit {commit_hash}: {diff_response.status_code}")
        else:
            print(f"Error getting diffstat for commit {commit_hash}: {response.status_code}")
    
    return testcase_details, commit_changes


def get_llm_analysis(commit_changes, testcase_details):
    """
    Analyzes commit changes and test case details using LLM and returns structured output.
    
    Args:
        commit_changes (dict): Dictionary containing commit changes
        testcase_details (dict): Dictionary containing test case details
        
    Returns:
        dict: Structured analysis from LLM including various metrics and insights
    """
    from openai import OpenAI
    import json
    import re

    # Initialize OpenAI client with OpenRouter configuration
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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"
    )

    # Prepare the prompt with commit and test case information
    prompt = f"""
    Analyze the following code changes and test cases:
    
    Commit Changes:
    {json.dumps(commit_changes, indent=2)}
    
    Test Case Details:
    {json.dumps(testcase_details, indent=2)}
    
    Strictly follow this output format in JSON:
    
    - code_complexity : <1 to 5>
    - code_quality : <1 to 5>
    - code_readability : <1 to 5>
    - developer_performance : <1 to 5>
    - function_complexity : <1 to 5>
    - estimated_time : <in hours> (this is very important. time estimate for the developer to complete the tasks)
    """

    try:
        # Make API call to LLM
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://your-site.com",
                "X-Title": "Code Analysis Tool",
            },
            model="deepseek/deepseek-r1:free",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            # max_tokens=12000,
            temperature=0.2,
        )

        if not completion or not completion.choices:
            raise Exception("No valid response from LLM API")
        
        print("\n🤖 LLM Output:")
        print(completion.choices[0].message.content)
        # analysis = json.loads(completion.choices[0].message.content)
        # print(json.dumps(analysis, indent=2))
        analysis = completion.choices[0].message.content
        return analysis

    except Exception as e:
        print(f"Error in LLM analysis: {str(e)}")
        return None

def calculate_working_hours(start_date, end_date, api_key="AIzaSyAuVdOZltds4UuA_hYW25BgR_NTpxlrQZw"):
    """
    Calculate working hours between two dates, excluding holidays and weekends.
    Fetches holidays from Google Calendar API.
    
    Args:
        start_date (str): Start date/time in ISO format
        end_date (str): End date/time in ISO format
        api_key (str): Google Calendar API key
        
    Returns:
        tuple: (total_working_hours, total_working_time_days)
    """
    # Convert string dates to datetime objects
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    
    # Ensure start_date is before end_date
    if start > end:
        start, end = end, start

    print(f"🔍 Calculating working hours between {start} and {end}...\n")

    # Fetch holidays from Google Calendar
    CALENDAR_ID = 'en.lk#holiday@group.v.calendar.google.com'
    encoded_calendar_id = CALENDAR_ID.replace('#', '%23').replace('@', '%40')
    calendar_url = f'https://www.googleapis.com/calendar/v3/calendars/{encoded_calendar_id}/events'
    
    params = {
        'key': api_key,
        'timeMin': start.isoformat(),
        'timeMax': end.isoformat(),
        'singleEvents': True,
        'orderBy': 'startTime'
    }
    
    # Get holidays
    try:
        response = requests.get(calendar_url, params=params)
        response.raise_for_status()
        holidays = {}
        for event in response.json().get('items', []):
            if 'date' in event['start']:
                holiday_date = datetime.strptime(event['start']['date'], '%Y-%m-%d').date()
                holidays[holiday_date.strftime('%Y-%m-%d')] = event['summary']
    except Exception as e:
        print(f"Error fetching holidays: {str(e)}")
        holidays = {}

    print("📅 Holidays:")
    for date, holiday_name in holidays.items():
        print(f"  {date}: {holiday_name}")

    # Calculate total duration
    total_duration_hours = (end - start).total_seconds() // 3600
    total_duration_days = total_duration_hours / 24
    print(f"⏳ Total Duration: {total_duration_days:.2f} days ({total_duration_hours:.2f} hours)\n")

    # Calculate weekend hours
    weekend_hours = 0
    weekend_count = 0
    weekend_dates = set()
    current_day = start.date()
    while current_day <= end.date():
        if current_day.weekday() in [5, 6]:
            if current_day != start.date() and current_day != end.date():
                weekend_hours += 24
                weekend_count += 1
                weekend_dates.add(current_day)
        current_day += timedelta(days=1)

    # Calculate holiday hours (excluding weekends)
    adjusted_holiday_hours = 0
    adjusted_holiday_count = 0
    for holiday in holidays:
        holiday_date = datetime.strptime(holiday, "%Y-%m-%d").date()
        if (holiday_date != start.date() and 
            holiday_date != end.date() and 
            holiday_date not in weekend_dates):
            adjusted_holiday_hours += 24
            adjusted_holiday_count += 1

    print(f"📅 Holiday Hours (excluding weekends): {adjusted_holiday_hours} hours")
    print(f"📅 Holiday Count (excluding weekends and first/last days): {adjusted_holiday_count} days\n")
    print(f"🛌 Weekend Hours: {weekend_hours} hours")
    print(f"🛌 Weekend Count (excluding first and last days): {weekend_count} days\n")

    # Calculate final working hours
    working_hours = total_duration_hours - adjusted_holiday_hours - weekend_hours
    working_days = working_hours / 24
    print(f"✅ Duration Hours (excluding weekends and holidays): {working_hours:.2f} hours ({working_days:.2f} days)\n")

    # Calculate adjusted working time
    total_working_hours = working_hours / 3
    total_working_time_days = total_working_hours / 24
    print(f"✅ Adjusted Working Hours: {total_working_hours:.2f} hours ({total_working_time_days:.2f} days)\n")

    return total_working_hours, total_working_time_days

# ==========================================================================
# EXECUTION OF THE ORIGINAL CODE
# ==========================================================================
print("\n" + "="*80)
print("EXECUTION OF THE ORIGINAL CODE")
print("="*80)

# Execute the original code
testcases_dict, projectId, repo_slug, repo_token, workspace = step1("TC02")

print("\nFinal Output (Test Cases):", testcases_dict)
print("Final Output (Project ID):", projectId)
print("Final Output (Repo Slug):", repo_slug)
print("Final Output (Repo Token):", repo_token)
print("Final Output (Workspace):", workspace)

latest_commit = get_commits(projectId)
print("Latest commit hash:", latest_commit)

if latest_commit:  # Ensure latest_commit is not None
    filtered_commits = get_commits_after_hash(latest_commit, repo_slug, repo_token, workspace, testcases_dict)
    print("Filtered commits made after the latest commit:")
    for commit in filtered_commits:
        print(commit)
else:
    print("No latest commit found. Cannot fetch commits after the latest commit.")

# ==========================================================================
# NEW FUNCTIONS ADDED FOR RETRIEVING INCOMPLETE COMMITS AND FINDING COMPLETED FUNCTIONS
# ==========================================================================
print("\n" + "="*80)
print("NEW FUNCTIONS FOR RETRIEVING INCOMPLETE COMMITS AND FINDING COMPLETED FUNCTIONS")
print("="*80)

print("\nExecuting modified functions with the project ID:", projectId)

print("\n1. Retrieving incomplete commits...")
incomplete_commits = get_incomplete_commits(projectId)

print("\n2. Identifying completed functions from incomplete commits...")
completed_functions = identify_completed_functions(incomplete_commits, testcases_dict)

print("\n3. Retrieving test case and commit details...")
if completed_functions:
    for func in completed_functions:
        testcase_details, commit_changes = get_testcase_and_commit_details(
            func['testcases'],
            func['commit_hashes'],
            repo_slug,
            repo_token,
            workspace
        )
        # print("\nTestcase Details:", testcase_details)
        # print("\nCommit Changes:", commit_changes)

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"- Analyzed {len(incomplete_commits)} incomplete commits")
print(f"- Identified {len(completed_functions)} completed functions")
print("="*80)