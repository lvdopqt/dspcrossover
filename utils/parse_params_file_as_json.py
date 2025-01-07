import re
import os
import json
from collections import defaultdict

def parse_params_file(file_content):
    # Define a regex pattern for matching the data structure
    pattern = r"""
        Cell\sName\s+=\s(?P<cell_name>.+?)\n
        Parameter\sName\s+=\s(?P<parameter_name>.+?)\n
        Parameter\sAddress\s+=\s(?P<parameter_address>\d+)\n
        Parameter\sValue\s+=\s(?P<parameter_value>[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)\n
        Parameter\sData\s+:\s*\n
        (?P<parameter_data>(?:0x[0-9A-Fa-f]{2}\s*,?\s*)+)
    """
    matches = re.finditer(pattern, file_content, re.VERBOSE)

    parsed_data = defaultdict(list)

    # Iterate through matches and build a dictionary
    for match in matches:
        cell_name = match.group('cell_name').strip()
        parameter_info = {
            "Parameter Name": match.group('parameter_name').strip(),
            "Parameter Address": int(match.group('parameter_address'))
        }
        parsed_data[cell_name].append(parameter_info)

    return parsed_data


def main():
    file_path = "params/dsp_params.params"  # Replace with the actual file path
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            file_content = file.read()
            parameters = parse_params_file(file_content)
    with open('params/params.json', 'w') as f:
        json.dump(parameters, f)

main()
