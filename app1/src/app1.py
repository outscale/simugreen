import json
import os
import time
import shutil

# Load the config file

INPUT_FOLDER = "/data/input"
OUTPUT_FOLDER = "/data/output"

# Below you will find demo func don't hesitate to try this code using example_input.json as input file
def funcA(arg1, arg2, arg3=""):
    """
    This is an example function
    Concatenate multiple string, note that arg3 is optional
    """
    return f"{arg1}_{arg2}{arg3}"

def funcB(arg1=None):
    """
    This is an example function
    Check if an argument was passed. if so return it else return default message
    """
    if arg1:
        return arg1
    else:
        return "Not filled !"

def main():
    while True:

        # List files under the input folder
        files = os.listdir(INPUT_FOLDER)

        # If no file is present we wait for 5 seconds and look again
        if not files: 
            time.sleep(5)
            continue

        # We process the first file
        file = files[0]
        time.sleep(5) # make sure that file is completely uploaded
        with open(os.path.join(INPUT_FOLDER, file), 'r') as f:
            try:
                commands = json.load(f)
            except Exception as e:
                print(e)
                continue
        
        tmp_path = f"/tmp/{os.path.splitext(file)[0]}.txt"
        print("tmp_path:", tmp_path)

        # For each command within the file perform an action
        with open(tmp_path, 'w') as f:
            for id, command in commands.items():
                print(f"id: {id}, command: {command}")

                
                try:
                    # !!!!!!!!!!!!!!!!!!!!!!!! WIP !!!!!!!!!!!!!!!!!!!
                    # This is where you can add specific processing for each command type

                    if command.get("type") == "typeA":
                        output = funcA(**command.get("arguments"))

                    elif command.get("type") == "typeB":
                        output = funcB(**command.get("arguments"))

                    else:
                        output = f"{command.get('type')} not handled"
                    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

                    f.write(f"{id} {output}\n")

                except Exception as e:
                    print(e)
                    continue

        # Once the file is processed delete it
        os.remove(os.path.join(INPUT_FOLDER, file))

        # Move the temporary output in the output folder
        shutil.move(tmp_path, os.path.join(OUTPUT_FOLDER, f"{os.path.splitext(file)[0]}.txt"))
        

if __name__ == "__main__":
    main()