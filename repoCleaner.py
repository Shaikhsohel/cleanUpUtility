import os
import requests
import sys

# GitHub Authentication
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print(" Error: GITHUB_TOKEN is not set. Exiting.")
    sys.exit(1)

# Repositories to clean (Replace with your actual repositories)
REPO_LIST = [
    "docs",
    "gh-ost",
    "dmca",
    "DPG-guidance"
]
GITHUB_OWNER = "github"  # Replace with your GitHub organization or username

# GitHub API Headers
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

def get_branches(repo):
    """Fetch all branches of a repository."""
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{repo}/branches"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        return [branch["name"] for branch in response.json()]
    else:
        print(f" Failed to fetch branches for {repo}: {response.json().get('message', 'Unknown error')}")
        return []

def delete_branch(repo, branch):
    """Delete a stale branch."""
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{repo}/git/refs/heads/{branch}"
    response = requests.delete(url, headers=HEADERS)

    if response.status_code == 204:
        print(f" Deleted stale branch: {branch} in {repo}")
    else:
        print(f" Failed to delete {branch} in {repo}: {response.json().get('message', 'Unknown error')}")

def is_stale(branch_name):
    """Custom condition to check if a branch is stale."""
    return branch_name.startswith("stale-")  # Modify this rule as needed

def main():
    for repo in REPO_LIST:
        print(f"\n🔍 Checking repository: {repo}")
        branches = get_branches(repo)

        for branch in branches:
            if is_stale(branch):  # Use a function to define stale branches
                delete_branch(repo, branch)

if __name__ == "__main__":
    main()
