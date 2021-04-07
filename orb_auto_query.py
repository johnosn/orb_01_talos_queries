# -*- coding: utf-8 -*-
"""Create Orbital queries from Cisco-Talos osquery repository."""

import ast
import configparser
import re

from util.pull_git import check_git
from util.folder import process_folder
from util.orbital import gen_orb_auth, check_orb_expiry, submit_orb_query

# START MAIN SCRIPT BODY
# SET CONFIGURATION FILE VALUES
CFG_FILE = r'.\api.cfg'
config = configparser.ConfigParser()
config.read(CFG_FILE)

# PARSE SETTINGS FROM CONFIG FILE
orb_url = config.get('ORB', 'url')
orb_client = config.get('ORB', 'client')
orb_secret = config.get("ORB", 'secret')
orb_webhookid = config.get("ORB", 'webhookid')
try:
    orb_nodes = ast.literal_eval(config.get('ORB', 'nodes'))
except configparser.NoOptionError:
    orb_nodes = None

git_folders = config.items("GIT_FOLDERS")
git_url = config.get("GIT", 'url')
repo_path = ".\\" + re.findall(r".*\/(.+?)\.git", git_url)[0] + "\\"


def main():
    """Execute main function for the script."""
    # UPDATE GIT REPOSITORY
    check_git(git_url)

    # ITERATE THROUGH FOLDER LIST
    for git_folder in git_folders:
        folder = git_folder[1]

        # CREATE DICTIONARY OF QUERIES
        vars()[folder] = process_folder(repo_path, folder)

        # GET ORBITAL AUTHENTICATION TOKEN
        orb_token, orb_expiry = gen_orb_auth(orb_url, orb_client,
                                             orb_secret)

        # PROCESS QUERIES
        for job, value in vars()[folder].items():

            # CHECK IF THE AUTH TOKEN IS STILL VALID
            if check_orb_expiry(orb_expiry):
                orb_token, orb_expiry = gen_orb_auth(orb_url, orb_client,
                                                     orb_secret)

            # QUERY THE ORBITAL API
            query_data = (folder, job, value)
            orb_data = (orb_url, orb_token, orb_nodes, orb_webhookid)
            submit_orb_query(query_data, orb_data)


# STARTUP THE SCRIPT AND INITIALIZE MAIN
if __name__ == "__main__":
    main()
