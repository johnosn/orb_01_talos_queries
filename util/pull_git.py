"""Pull or clone data from git repository."""
import os.path
import re
import git


def check_git(repo_url):
    """Determine pull or clone action and download repo."""
    repo_name = re.findall(r".*\/(.+?)\.git", repo_url)[0]
    repo_path = ".\\" + repo_name
    isdir = os.path.isdir(repo_path)
    if isdir:
        repo = git.Repo(repo_path)
        repo.remotes.origin.pull()

    else:
        git.Git(".\\").clone(repo_url)
