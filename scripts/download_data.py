import subprocess
import os

files = [
    "all_pull_request",
    "all_repository",
    "all_user",
    "human_pr_task_type",
    "human_pull_request",
    "issue",
    "pr_comments",
    "pr_commit_details",
    "pr_commits",
    "pr_review_comments",
    "pr_review_comments_v2",
    "pr_reviews",
    "pr_task_type",
    "pr_timeline",
    "related_issue",
]

target_dir = "/home/sobczakus/projekt_badawczy/AIDev"

if not os.path.exists(target_dir):
    os.makedirs(target_dir)

print(f"Rozpoczynam pobieranie {len(files)} plikow do: {target_dir}\n")

for file_name in files:
    parquet_file = f"{file_name}.parquet"
    url = f"https://huggingface.co/datasets/hao-li/AIDev/resolve/main/{parquet_file}?download=true"
    output_path = os.path.join(target_dir, parquet_file)
    
    print(f"Pobieranie: {parquet_file}...")
    
    command = [
        "curl", "-L", url, "-o", output_path
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Sukces: {parquet_file} zostal zapisany.\n")
    except subprocess.CalledProcessError as e:
        print(f"BLAD przy pobieraniu {parquet_file}: {e}\n")

print("Wszystkie operacje zakonczone.")