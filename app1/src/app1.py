import json
import os
import time
import shutil
from fact import cmd_fact
from decrypt_frame import decode_frame
from generateDLMSCMD import templating_dlms 
from x_max import get_x_max

from store_price import clone_product, sum_of_prices, delete_product
from prime_numbers import prime_numbers, sum_prime_numbers
from transport_stream import parse_transport_stream
from sink_aggregation import sink_aggregation

# See README.md for details

# Don't forget to relaod the service after any code change: 
#   ./app1_connect.sh
#   sudo systemctl restart app1.service
# 
# To see the errors:
#   ./app1_connect.sh
#   journalctl -u app1.service

# DO NOT CHANGE THESE CONSTANTS
INPUT_FOLDER = "/data/input" 
OUTPUT_FOLDER = "/data/output"


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
                    command_type = command.get("type")
                    if command_type == "prime_numbers":
                        output = prime_numbers(**command.get("arguments"))
                    elif command_type == "sum_prime_numbers":
                        output = sum_prime_numbers(**command.get("arguments"))    
                    elif command_type == "clone_product":
                        output = clone_product(**command.get("arguments"))        
                    elif command_type == "delete_product":
                        output = delete_product(**command.get("arguments"))
                    elif command_type == "sum_of_prices":
                        output = sum_of_prices(**command.get("arguments"))      
                    elif command_type == "parse_transport_stream":
                        output = parse_transport_stream(**command.get("arguments"))
                    elif command_type == "cmd_fact":
                        output = cmd_fact(**command.get("arguments"))
                    elif command_type == "get_x_max":
                        output = get_x_max(**command.get("arguments"))
                    elif command_type == "templating_dlms":
                        output = templating_dlms(**command.get("arguments"))
                    elif command_type == "decode_frame":
                        output = decode_frame(**command.get("arguments"))          
                    elif command_type == "sink_aggregation":
                        output = sink_aggregation(**command.get("arguments"))

                    else:
                        output = f"{command.get('type')} not handled"

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
