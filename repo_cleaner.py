import os
import requests
from github import Github
from datetime import datetime, timezone

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_LIST_FILE = "masterRepoList.txt"
STALE_BRANCHES_FILE = "stale_branches_summary.txt"
TIME_WINDOW_YEARS = 1  # Stale threshold (1 year)

# List of repositories to scan
repos = [
    "github/docs",
    "github/gh-ost",
    "github/dmca",
    "github/DPG-guidance"
]

# Fetch and store repo names
with open(REPO_LIST_FILE, "w") as f:
    for repo in repos:
        f.write(f"https://github.com/{repo}\n")

# Connect to GitHub
github = Github(GITHUB_TOKEN)
stale_branches = []

for repo_name in repos:
    try:
        repo = github.get_repo(repo_name)
        branches = repo.get_branches()

        for branch in branches:
            last_commit = repo.get_branch(branch.name).commit.commit.author.date

            if last_commit is None:
                print(f" WARNING: No last commit found for {repo_name}/{branch.name}")
                continue  # Skip this branch if no commit is found

            # Convert last_commit to timezone-aware datetime
            last_commit = last_commit.replace(tzinfo=timezone.utc)
            age_days = (datetime.now(timezone.utc) - last_commit).days

            if age_days > (TIME_WINDOW_YEARS * 365):
                stale_branches.append(f"{repo_name} - {branch.name} (Last Commit: {last_commit})")

    except Exception as e:
        print(f" ERROR: Failed to process {repo_name} - {e}")

# Store stale branches in a file
with open(STALE_BRANCHES_FILE, "w") as f:
    for branch in stale_branches:
        f.write(branch + "\n")

print(" Stale branches identified. Please review 'stale_branches_summary.txt'.")
