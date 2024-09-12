import json
import subprocess
import os
import argparse
from numpy import empty
import pandas as pd
import requests
import re
import csv

def main():
    # Initialize the argument parser
    parser = argparse.ArgumentParser(description='Process configuration and variable inputs for the script.')

    # Add arguments for configuration file (-cfg) and variable file (-var)
    parser.add_argument('-cfg', '--config', required=True, help='Path to the configuration file', dest='config_file')
    parser.add_argument('-var', '--variables', required=True, help='Path to the variables CSV file', dest='variables_file')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Access the parsed arguments
    config_file = args.config_file
    variables_file = args.variables_file

    number_of_configs = setup_configs(config_file, variables_file)
    setup_simulations(config_file, variables_file, number_of_configs)
    create_results_sheet(config_file, variables_file, number_of_configs)

def setup_configs(gcsim_config, variable_config):
    # Hard-coded 5-star main stat values
    stat_values = {
        'hp%': 0.466,
        'atk%': 0.466,
        'def%': 0.583,
        'em': 187,
        'er': 0.518,
        'cd': 0.622,
        'cr': 0.311,
        'heal': 0.359,
        'phys%': 0.583,
        'pyro%': 0.466,
        'cryo%': 0.466,
        'dendro%': 0.466,
        'hydro%': 0.466,
        'electro%': 0.466,
        'geo%': 0.466,
        'anemo%': 0.466
    }

    configcount = 0

    df = pd.read_csv(variable_config)

    with open(gcsim_config, 'r') as file:
        template = file.read()
        base_filename = get_base_filename(file.name)

    # Define which columns to replace for each character (char1, char2, char3, char4)
    char_columns = [
        ('$char1', ['$char1_name', '$char1_weapon', '$char1_refinement', '$char1_artifact1', '$char1_artifact2', '$char1_sands', '$char1_goblet', '$char1_circlet']),
        ('$char2', ['$char2_name', '$char2_weapon', '$char2_refinement', '$char2_artifact1', '$char2_artifact2', '$char2_sands', '$char2_goblet', '$char2_circlet']),
        ('$char3', ['$char3_name', '$char3_weapon', '$char3_refinement', '$char3_artifact1', '$char3_artifact2', '$char3_sands', '$char3_goblet', '$char3_circlet']),
        ('$char4', ['$char4_name', '$char4_weapon', '$char4_refinement', '$char4_artifact1', '$char4_artifact2', '$char4_sands', '$char4_goblet', '$char4_circlet']),
    ]

    for index, row in df.iterrows():
        # Make a copy of the template for this specific row
        modified_config = template
        
        # Loop through each character set and replace them dynamically
        for placeholder, columns in char_columns:
            char_name = row[columns[0]]
            char_weapon = row[columns[1]]
            char_refinement = row[columns[2]]
            char_artifact1 = row[columns[3]]
            char_artifact2 = row[columns[4]]
            char_sands = row[columns[5]]
            char_goblet = row[columns[6]]
            char_circlet = row[columns[7]]

            if pd.isna(char_name) or not char_name.strip():
                continue  # Skip to the next character if any required field is empty
            
            # Resolve the values for sands, goblet, and circlet
            sands_value = stat_values.get(char_sands, 0)  # Default to 0 if not found
            goblet_value = stat_values.get(char_goblet, 0)
            circlet_value = stat_values.get(char_circlet, 0)
            
            # Construct custom string based on the new format
            custom_string = f"""{char_name} add weapon="{char_weapon}" refine={char_refinement} lvl=90/90;"""
            
            # Check if char_artifact2 is not empty and append the appropriate line
            if pd.notna(char_artifact2) and char_artifact2.strip():
                custom_string += f"\n{char_name} add set=\"{char_artifact1}\" count=2;\n{char_name} add set=\"{char_artifact2}\" count=2;"
            else:
                custom_string += f"\n{char_name} add set=\"{char_artifact1}\" count=4;"
            
            # Add the stats line at the end with the resolved values
            custom_string += f"""\n{char_name} add stats hp=4780 atk=311 {char_sands}={sands_value} {char_goblet}={goblet_value} {char_circlet}={circlet_value} ; #main"""
            
            # Replace the placeholder (e.g., $char1, $char2, etc.) in the template
            modified_config = modified_config.replace(placeholder, custom_string)
        
        # Save the modified config as a new file
        output_filename = f'{base_filename}_{index + 1}.txt'
        with open(output_filename, 'w', newline='\n') as output_file:
            output_file.write(modified_config)
        
        print(f"Modified {file.name} saved as {output_filename}")
        configcount += 1

    print(f"Config preparation completed! Total configs created: {configcount}")

    return configcount

def get_base_filename(file_name):
    base_filename = os.path.splitext(file_name)[0]
    return base_filename

def setup_simulations(config_file, variables_file, number_of_configs):
   # Define the path to the executable (assuming it's in the same directory as this script)
    executable_path = os.path.join(os.getcwd(), 'gcsim.exe')

    base_filename = get_base_filename(config_file)

    for i in range(1, number_of_configs + 1):
        # Build input/output filenames for each run
        input_file = f"{base_filename}_{i}.txt"
        output_file = f"result_{base_filename}_{i}.json"
        # Build the command (command-line)
        command = [executable_path, '-c', input_file, '-out', output_file, '-substatOptimFull']
        
        # Run the simulation for this configuration
        run_simulation(command, i, number_of_configs)

def run_simulation(command, simulation_number, number_of_configs):
    print(f"Starting simulation {simulation_number}/{number_of_configs}...")

    try:
        # Run the command and capture the output in real-time
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Monitor the output
        for line in process.stdout:
            print(line, end='')  # Print the output line by line as it is produced
            if "Simulation completed" in line:
                print(f"Simulation {simulation_number}/{number_of_configs} completed!")
                break
            
        # Wait for the process to finish
        process.wait()

        # Check if there were any errors
        if process.returncode != 0:
            print(f"Process finished with errors. Return code: {process.returncode}")
            print("Error Output:", process.stderr.read())

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        print("Error Output:", e.stderr)

# URL to fetch character and weapon mappings from GitHub
CHARACTER_URL = 'https://raw.githubusercontent.com/genshinsim/gcsim/main/pkg/shortcut/characters.go'
WEAPON_URL = 'https://raw.githubusercontent.com/genshinsim/gcsim/main/pkg/shortcut/weapons.go'

# Function to fetch and create the mapping from the Go files
def fetch_mapping(url):
    response = requests.get(url)
    go_code = response.text

    # Regex pattern to extract short names and key names
    pattern_short = r'"([^"]+)":'   # Short names inside double quotes
    pattern_key = r'keys.([^,]+),'  # Keys used in Go file (e.g., keys.Xiao)

    # Find all matches
    shortcut_names = re.findall(pattern_short, go_code)
    key_names = re.findall(pattern_key, go_code)

    # Create a dictionary mapping shortcut names to key names
    mapping = dict(zip(shortcut_names, key_names))
    
    return mapping

# Fetch the character and weapon mappings
character_mapping = fetch_mapping(CHARACTER_URL)
weapon_mapping = fetch_mapping(WEAPON_URL)

# Function to add spaces before each capital letter except the first one
def add_spaces_to_name(name):
    # Use a regular expression to add a space before each capital letter except the first
    return re.sub(r'(?<!^)([A-Z])', r' \1', name)


# Function to rename character and weapon based on the mappings and format the names
def rename_character_and_weapon(char_name, weapon_name):
    # Rename character based on mapping
    renamed_char = character_mapping.get(char_name, char_name)  # Use original name if not found
    renamed_char = add_spaces_to_name(renamed_char)  # Add spaces to the character name

    # Rename weapon based on mapping
    renamed_weapon = weapon_mapping.get(weapon_name, weapon_name)  # Use original name if not found
    renamed_weapon = add_spaces_to_name(renamed_weapon)  # Add spaces to the weapon name

    return renamed_char, renamed_weapon

def create_results_sheet(file_name, variables_file, number_of_configs):
    # Initialize an empty list to store the data for each configuration
    results = []
    base_filename = get_base_filename(file_name)

    # Loop through each config file
    for i in range(1, number_of_configs + 1):
        json_file = f'result_{base_filename}_{i}.json'
        
        try:
            with open(json_file, 'r') as file:
                data = json.load(file)

            # Create a dictionary for the current config's details
            config_details = {'Config': f'{base_filename}_{i}'}
            
            # Extract the mean DPS
            config_details['mean_dps'] = data['statistics']['dps']['mean']

            # Extract details for each character and merge into the config details
            for char_index in range(0, 4):
                char_details = extract_character_details(data, variables_file, i, char_index)
                if char_details:
                    config_details.update(char_details)
            
            # Add the combined row (config + character details) to results
            results.append(config_details)
        
        except FileNotFoundError:
            print(f"File {json_file} not found.")
        except KeyError as e:
            print(f"Key error: {e} in {json_file}")
        except json.JSONDecodeError:
            print(f"Error decoding JSON in {json_file}")

    df = pd.DataFrame(results)

    output_csv = f'sheet_{base_filename}.csv'
    df.to_csv(output_csv, index=False)

    print(f"Results saved to {output_csv}")

# Function to extract character details from JSON data
def extract_character_details(data, variables_file, row_number, char_index):
    try:
        char_name = data['character_details'][char_index]['name']
        char_weapon = data['character_details'][char_index]['weapon']['name']
        char_refinement = data['character_details'][char_index]['weapon']['refine']
        char_dps = data['statistics']['character_dps'][char_index]['mean']

        # Rename character and weapon using the rename function
        renamed_char, renamed_weapon = rename_character_and_weapon(char_name, char_weapon)

        char_sets = data['character_details'][char_index]['sets']
        sets_list = [f"{value}p {key}" for key, value in char_sets.items()]
        char_sets_merged = "/".join(sets_list)  # Merge them into a single string

        char_sands = ''
        char_goblet = ''
        char_circlet = ''

        # Open the CSV file and extract the relevant row
        with open(variables_file, mode='r') as file:
            csv_reader = list(csv.DictReader(file))  # Read the CSV into a list of dictionaries
            if row_number <= len(csv_reader):  # Ensure the row_number is valid
                row = csv_reader[row_number - 1]  # Get the specified row
                
                # Build column names based on the character index
                sands_col = f'$char{char_index+1}_sands'
                goblet_col = f'$char{char_index+1}_goblet'
                circlet_col = f'$char{char_index+1}_circlet'
                
                # Extract the corresponding sands, goblet, and circlet values from the CSV row
                char_sands = row.get(sands_col, 'N/A')
                char_goblet = row.get(goblet_col, 'N/A')
                char_circlet = row.get(circlet_col, 'N/A')
            else:
                print(f"Row number {row_number} out of range")

        return {
            f'char{char_index+1}_name': renamed_char,
            f'char{char_index+1}_weapon': renamed_weapon,
            f'char{char_index+1}_refinement': char_refinement,
            f'char{char_index+1}_sets': char_sets_merged,
            f'char{char_index+1}_sands': char_sands,
            f'char{char_index+1}_goblet': char_goblet,
            f'char{char_index+1}_circlet': char_circlet,
            f'char{char_index+1}_dps': char_dps
        }
    
    except KeyError as e:
        print(f"Key error: {e}")
        return None
        
if __name__ == "__main__":
    main()