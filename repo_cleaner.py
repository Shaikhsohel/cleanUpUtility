import os
import requests
from github import Github
from datetime import datetime, timezone
age_days = (datetime.now(timezone.utc) - last_commit).days
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_LIST_FILE = "masterRepoList.txt"
STALE_BRANCHES_FILE = "stale_branches_summary.txt"
TIME_WINDOW_YEARS = 1  # Stale threshold (1 year)

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
    repo = github.get_repo(repo_name)
    branches = repo.get_branches()

    for branch in branches:
        last_commit = repo.get_branch(branch.name).commit.commit.author.date
        age_days = (datetime.now() - last_commit).days

        if age_days > (TIME_WINDOW_YEARS * 365):
            stale_branches.append(f"{repo_name} - {branch.name} (Last Commit: {last_commit})")

# Store stale branches in a file
with open(STALE_BRANCHES_FILE, "w") as f:
    for branch in stale_branches:
        f.write(branch + "\n")

print("Stale branches identified. Please review 'stale_branches_summary.txt'.")
