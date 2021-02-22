"""Processing for yaml files."""
import glob
import yaml


def read_yaml(file_path):
    """Read a YAML file."""
    try:
        with open(file_path) as yaml_file:
            query_data = yaml.load(yaml_file, Loader=yaml.FullLoader)
            yaml_file.close()
    except yaml.parser.ParserError as err:
        print("\nFAILED TO IMPORT: " + file_path)
        print("ERROR:")
        print(err)
        print()
        query_data = {}
    return query_data


def enum_yaml(folder):
    """Get list of YAML files from directory."""
    yaml_files = glob.glob(folder + "\\*.yaml")
    vars()[folder] = dict()

    for file in yaml_files:
        yaml_query = read_yaml(file)
        vars()[folder].update(yaml_query)

    return vars()[folder]
