import json
import sys
import os

def parse_parameters(data, output_path):
    # Split data by cell blocks
    blocks = data.strip().split("\n\n\n")
    cells = {}

    for block in blocks:
        # Split each block by lines and create a dictionary for each parameter set
        lines = block.strip().split("\n")
        entry = {}
        
        for line in lines:
            if "=" in line:
                # Split each line by '=' and strip whitespace
                key, value = map(str.strip, line.split("=", 1))
                
                # Remove trailing colons from keys
                key = key.replace(":", "")
                
                if key == "Parameter Data":
                    # Split the parameter data by commas and strip whitespace
                    entry[key] = [byte.strip() for byte in value.split(",") if byte.strip()]
                elif key == "Parameter Value":
                    # Convert the parameter value to a float if possible
                    entry[key] = float(value) if "." in value else int(value)
                else:
                    entry[key] = value

        # Get the cell name and ensure it has a default if missing
        cell_name = entry.get("Cell Name", "unnamed_cell").replace(" ", "_")
        
        # Append the entry to the cell name group
        if cell_name not in cells:
            cells[cell_name] = []
        cells[cell_name].append(entry)

    # Ensure output path exists
    os.makedirs(output_path, exist_ok=True)

    # Write each cell's parameters to its respective JSON file in the output path
    for cell_name, entries in cells.items():
        filename = os.path.join(output_path, f"{cell_name}.json")
        with open(filename, "w") as f:
            json.dump(entries, f, indent=4)
        print(f"Saved {filename}")

def process_file(filename, output_path):
    try:
        with open(filename, 'r') as file:
            data = file.read()
            parse_parameters(data, output_path)
    except FileNotFoundError:
        print(f"File {filename} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        input_file = sys.argv[1]
        output_path = sys.argv[2]
        process_file(input_file, output_path)
    else:
        print("Please provide an input filename and an output path.")
