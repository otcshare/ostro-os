import json
import os
import sys

SCRIPT_PATH = os.path.realpath(__file__)
CONST_PATH = os.path.dirname(SCRIPT_PATH)
JSON_PATH = os.path.join(CONST_PATH, "package.json")

def get_version(json_path):
    with open(json_path) as data_file:
        data = json.load(data_file)
    version_num = data["version"]
    sys.stdout.write(version_num)

if __name__ == '__main__':
    get_version(JSON_PATH)
