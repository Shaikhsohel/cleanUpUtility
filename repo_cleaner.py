import os
import time
from github import Github, RateLimitExceededException
from datetime import datetime, timezone

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_LIST_FILE = "masterRepoList.txt"
STALE_BRANCHES_FILE = "stale_branches_summary.txt"
TIME_WINDOW_YEARS = 1  # Stale threshold (1 year)
RETRY_WAIT = 60  # Initial retry wait time in seconds

repos = [
    "github/docs",
    "github/gh-ost",
    "github/dmca",
    "github/DPG-guidance"
]

# Connect to GitHub
github = Github(GITHUB_TOKEN)
stale_branches = []

def check_rate_limit():
    """Check and handle API rate limits with exponential backoff."""
    rate_limit = github.get_rate_limit().core
    if rate_limit.remaining == 0:
        reset_time = rate_limit.reset.timestamp()
        sleep_time = max(0, reset_time - time.time()) + 5  # Add buffer
        print(f"⚠️ Rate limit exceeded! Sleeping for {int(sleep_time / 60)} minutes...")
        time.sleep(sleep_time)  # Sleep until rate limit resets

for repo_name in repos:
    try:
        check_rate_limit()  # Ensure we have API quota before proceeding
        repo = github.get_repo(repo_name)
        branches = repo.get_branches()

        for branch in branches:
            try:
                check_rate_limit()  # Check before fetching each branch
                last_commit = repo.get_branch(branch.name).commit.commit.author.date

                if last_commit is None:
                    print(f"⚠️ WARNING: No last commit found for {repo_name}/{branch.name}")
                    continue  # Skip this branch if no commit is found

                last_commit = last_commit.replace(tzinfo=timezone.utc)
                age_days = (datetime.now(timezone.utc) - last_commit).days

                if age_days > (TIME_WINDOW_YEARS * 365):
                    stale_branches.append(f"{repo_name} - {branch.name} (Last Commit: {last_commit})")

            except RateLimitExceededException:
                print("⚠️ GitHub API rate limit hit. Sleeping before retrying...")
                time.sleep(RETRY_WAIT)
                RETRY_WAIT *= 2  # Exponential backoff

    except Exception as e:
        print(f"❌ ERROR: Failed to process {repo_name} - {e}")

# Store stale branches in a file
with open(STALE_BRANCHES_FILE, "w") as f:
    for branch in stale_branches:
        f.write(branch + "\n")

print("✅ Stale branches identified. Please review 'stale_branches_summary.txt'.")
