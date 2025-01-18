import json


def get_params():
    params_path = 'params/params.json'
    try:
        with open(params_path, "r") as file:
            params = json.load(file)
    except FileNotFoundError:
        print(f"Error: The file {params_path} does not exist.")
    except json.JSONDecodeError:
        print(f"Error: The file {params_path} contains invalid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return params