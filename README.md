
# Preconditions
1. Installed Terraform
2. Access and Private keys for DS Outscale cloud account.
3. Inititalize Terraform in the project (once after project clonning from Git)
```
terraform init
```

# Platform installation

## 1. Fill OUTSCALE_ACCESSKEYID and OUTSCALE_SECRETKEYID in env_init_example.sh and rename the file in env_init.sh:
```
export OUTSCALE_ACCESSKEYID=...
export OUTSCALE_SECRETKEYID=...
export OUTSCALE_REGION="eu-west-2"
```

## 2. Create platform
```
./platform_create.sh
```
The script does the following:
1. Create VM with all serivces of the evaluation part of competition environment. The services are running in Docker containers.
2. Create "~/.ssh/hackathon.rsa" private key to access this VM.
3. Create "<vm>_connect.sh" files to connect to the VMs.

## 3. Destroy platform
```
./platform_destroy.sh
```
The script destroy all resources in the cloud.

## 4. Connect to VMs by ssh:
```
./<vm>_connect.sh
```
Where <vm> are app1, ms1, db1...

This files are created by platform_create.sh script.

# Running VSCode on vm
You can run VSCode on any VM. It is not running automatically to avoid unnecessary resources consumption.
You can run it manually in a docker container. 

Example of its configuration is in <application>/vscode folder:
    - Dockerfile - update it according to your needs
    - build.sh - Image compilation
    - run.sh - Run container with VSCode.

To run VSCode in a VM:
1. Connect by SSH: ```./<app>_connect.sh```
2. Unzip files with vscode: ```unzip vscode.zip```
3. Buid the image (it may take up to 20 minutes):
```
cd <app>/vscode # example: cd app1/vscode
bash ./build.sh 
```
4. Run container with VSCode: ```bash ./run.sh```
5. Open VSCode in your browser: http://<vm_ip>:3000, where <vm_ip> can be found in <app>_connect.sh script.

If you run your application on this VM in another container make sure that you code is mapped to the service as a local volume pointed to the same local folder.
By default this is /data/code, but you can change it in run.sh script.

# Components

## App1
One file python application. It watches for new files in **/data/input** folder, process them and output the result in **/data/output**.

The file names must be unique otherwice the result of previous files with this same name will be rewritten by the more recent ones.


Example of input file:
```
{
    "1": {
	    "type": "typeA",
	    "arguments": {
            "arg1": "Hello",
		    "arg2": "world"
        }
	},
    "2": {
	    "type": "typeB",
	    "arguments": {"arg1": "Filled !"}
    },
    "3": {
	    "type": "typeA",
	    "arguments": {
            "arg1": "Beautiful",
		    "arg2": "sunny",
            "arg3": "day"
        }
	},
    "4": {
        "type": "typeB",
        "arguments": {}
    }
}
``` 

The numeric first-level keys are task ids. They must be unique within a file.
- "type" is a command type.
- "arguments" can be unique for every commmand type

Command processing functions return strings. 

Output file has the same name as the input one with .txt extention. Ex: a234.json -> a234.txt.
Every line starts with command id, than one space as separator and command output.
To commands in output file can be in any order.

Example of output file:

```
1 Hello_world
2 value
3 Beautiful_sunnyday
4 Not filled !
```

To send/recieve files from remote machine can be used the following commands:

Send file to app1:
```
scp -i ~/.ssh/hackathon.rsa /tmp/aa.json outscale@<app1_ip>:/data/input/aa.json
```

List files in app1 /data/output:
```
ssh -o StrictHostKeyChecking=no -i ~/.ssh/hackathon.rsa outscale@<app1_ip> "ls /data/output"
```

Copy file from app1:
```
scp -i ~/.ssh/hackathon.rsa outscale@<app1_ip>:/data/input/aa.json /tmp/
```

## Database 1
This is preinstalled PostgreSQL database.

For debug you can connect to it via web interface http://<db1_vm_ip>:8080

host: postgres
username: postgres
password: postgres
database: postgres

It is prefiled by db_init.sql script in db1.

# Connections between containers
VMs can be accessed by their short names: app1, ms1, and db1
These hosts are added to /etc/hosts of all VMs
