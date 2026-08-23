import os
import re
import csv
import time
import requests

GITHUB_TOKEN = ''
INPUT_DIR = '../../data/input'
RESULT_DIR = '../../data/result'
URL = 'https://api.github.com/graphql'
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

def generate_year_aliases(start_year, end_year):
    aliases = ""
    for year in range(start_year, end_year + 1):
        aliases += f"""
        y{year}: contributionsCollection(from: "{year}-01-01T00:00:00Z", to: "{year}-12-31T23:59:59Z") {{
          totalCommitContributions
          restrictedContributionsCount
          totalPullRequestReviewContributions
          totalPullRequestContributions
        }}"""
    return aliases

def get_expert_query(login):
    return f"""
    query {{
      user(login: "{login}") {{
        login
        isGitHubStar
        followers {{ totalCount }}
        repositoriesContributedTo {{ totalCount }}
        {generate_year_aliases(2021, 2025)}
      }}
    }}
    """

def get_last_processed_index():
    files = [f for f in os.listdir(RESULT_DIR) if f.startswith('result_') and f.endswith('.csv')]
    if not files:
        return 0
    numbers = [int(re.search(r'result_(\d+)', f).group(1)) for f in files]
    return max(numbers)

def fetch_github_data(name):
    try:
        query = get_expert_query(name)
        response = requests.post(URL, json={'query': query}, headers=HEADERS, timeout=20)
        
        if response.status_code != 200:
            return None

        data = response.json()
        if 'errors' in data or not data.get('data', {}).get('user'):
            return None

        user = data['data']['user']
        years = [f"y{y}" for y in range(2021, 2026)]

        pub_commits = sum(user[y]['totalCommitContributions'] for y in years)
        priv_work   = sum(user[y]['restrictedContributionsCount'] for y in years)
        reviews     = sum(user[y]['totalPullRequestReviewContributions'] for y in years)
        prs         = sum(user[y]['totalPullRequestContributions'] for y in years)

        return {
            "login": user['login'],
            "is_star": int(user['isGitHubStar']),
            "followers": user['followers']['totalCount'],
            "collab_breadth": user['repositoriesContributedTo']['totalCount'],
            "5yr_public_commits": pub_commits,
            "5yr_private_work": priv_work,
            "5yr_reviews_given": reviews,
            "5yr_prs_opened": prs,
            "5yr_total_activity": pub_commits + priv_work
        }
    except Exception as e:
        print(f"Error fetching {name}: {e}")
        return None

def process_file(file_number):
    input_path = os.path.join(INPUT_DIR, f"{file_number}.csv")
    output_path = os.path.join(RESULT_DIR, f"result_{file_number}.csv")
    
    if not os.path.exists(input_path):
        return False

    user_names = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row: user_names.append(row[0].strip())

    print(f"Processing {file_number}.csv ")

    results = []
    for name in user_names:
        data = fetch_github_data(name)
        if data:
            results.append(data)
            print(f"  Succes: {name}")
        else:
            print(f"  Error: {name} (Skipped/Not Found)")
        
        time.sleep(0.2)

    if results:
        keys = results[0].keys()
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
    
    return True

def main():
    last_index = get_last_processed_index()

    for i in range(last_index + 1, 500): 
        success = process_file(i)
        if not success:
            print("Task complete.")
            break

if __name__ == "__main__":
    main()
