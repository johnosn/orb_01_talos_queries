"""Proccesing for folders."""
from util.json_files import enum_json
from util.yaml_files import enum_yaml


def process_folder(repo_path, folder):
    """Find files and send for processing."""
    folder_path = repo_path + folder + "\\"
    vars()[folder] = dict()
    json_queries = enum_json(folder_path)
    vars()[folder].update(json_queries)

    yaml_queries = enum_yaml(folder_path)
    vars()[folder].update(yaml_queries)

    return vars()[folder]
