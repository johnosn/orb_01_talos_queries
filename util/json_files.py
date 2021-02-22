"""Processing for json files."""
import glob
import json


def read_json(file_path):
    """Read a JSON file."""
    with open(file_path) as json_file:
        query_data = json.load(json_file)
        json_file.close()
    return query_data


def enum_json(folder):
    """Get list of JSON files from directory."""
    json_files = glob.glob(folder + "\\*.json")
    vars()[folder] = dict()

    for file in json_files:
        json_query = read_json(file)
        vars()[folder].update(json_query)

    return vars()[folder]
