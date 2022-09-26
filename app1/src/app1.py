import configparser
import json
import os
import time

# Load the config file

CONFIG_FILE = "/tmp/app1.cfg"
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

def main():
    while True:

        # List files under the input folder
        files = os.listdir(config['FILE']['INPUT'])

        # If no file is present we wait for 5 seconds and look again
        if not files: 
            time.sleep(5)
            continue

        # We process the first file
        file = files[0]
        with open(os.path.join(config['FILE']['INPUT'], file), 'r') as f:
            commands = json.load(f)
        
        tmp_path = f"/tmp/app1/{os.path.splitext(file)[0]}.txt"
        # For each command within the file perform an action
        with open(tmp_path, 'w') as f:
            for id, command in commands.items():
                # !!!!!!!!!!!!!!!!!!!!!!!! WIP !!!!!!!!!!!!!!!!!!!
                output = "placeholder" # replace this lines by operation depanding of the command type
                # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                f.write(f"{id} {output}\n")

        # Once the file is processed delete it
        os.remove(os.path.join(config['FILE']['INPUT'], file))

        # Move the temporary output in the output folder
        os.replace(tmp_path, os.path.join(config['FILE']['OUTPUT'], f"{os.path.splitext(file)[0]}.txt"))
        

if __name__ == "__main__":
    main()