
# Preconditions
1. GitHub account
It's free. You start by forking https://github.com/outscale-dev/hackathon202210.
Your delivery is an updated project in your account.

2. Linux or Mac computer
The scripts in this project are for the bash. If you have a Windows computer you can use a VM running in VirtualBox on your computer or in DS Outscale cloud.

3. Installed Terraform
We use Terraform to deploy the environment into the cloud. Please [install it](https://learn.hashicorp.com/tutorials/terraform/install-cli).


4. Access and Secret keys for DS Outscale cloud account.
Every team has a separate account. There are several ways of working with it.
- [Terraform](https://www.terraform.io/) - automation tool. 
    - See [OUTSCALE Provider](https://registry.terraform.io/providers/outscale-dev/outscale/latest/docs)
- [Cockpit](https://cockpit.outscale.com/login/) - Web UI. Normally, you don't need to use it, but if you want please use AccessKey as login and SecretKey as password.
- [VS Code plugin osc-viewer](https://marketplace.visualstudio.com/items?itemName=outscale.osc-viewer)



# Platform installation

## Initialize Terraform in the project (once after project cloning from GitHub)
Run it in the project folder:
```
terraform init
```

## Set Access and Secret keys
Rename env_init_example.sh file into env_init.sh and set values for OUTSCALE_ACCESSKEYID and OUTSCALE_SECRETKEYID.
```
export OUTSCALE_ACCESSKEYID=...
export OUTSCALE_SECRETKEYID=...
export OUTSCALE_REGION="eu-west-2"
```

## Create a platform
```
./platform_create.sh
```
The script does the following:
1. Create virtual machines, security groups, and other environmental elements. 
2. Create "~/.ssh/hackathon.rsa" private key to access this VM by ssh. The same key for all VMs.
3. Create "<vm>_connect.sh" files to connect to the VMs.

Be patient. It takes about 20 minutes.


## Destroy platform
If you want to restart your work or test your updated scripts you have first destroy the platform. 
```
./platform_destroy.sh
```
The script destroys ALL resources in the cloud.
Then you can re-create it again.

## Connect to VMs by ssh:
When the platform is up, you can connect to machines by SSH. To simplify this the scripts are created in the project root for all VMs.

```
./<vm>_connect.sh
```
Where <vm> is app1, ms1, or db1.

These files are re-created by platform_create.sh script on every platform re-creation.

# Running VSCode on a virtual machine
You can use whatever IDE you want to work with code. VS Code is one of the most popular. To simplify your work with code in the VMs we prepare it for you.

You can run VSCode on any VM. It is not running automatically to avoid unnecessary resource consumption.
You can run it manually in a docker container. 

Example of its configuration is in <application>/vscode folder:
    - Dockerfile - install all needed tools here
    - build.sh - Image compilation script
    - run.sh - Run container with VSCode.

To run VSCode in a VM:
1. Connect by SSH: ```./<app>_connect.sh```
2. Unzip files with vscode: ```unzip vscode.zip```
3. Build the image (it may take up to 20 minutes):
```
cd <app>/vscode # example: cd app1/vscode
bash ./build.sh 
```
4. Run container with VSCode: ```bash ./run.sh```
5. Open VSCode in your browser: http://<vm_ip>:3000, where <vm_ip> can be found in <app>_connect.sh script.

If you run your application on this VM in another container make sure that your code is mapped to the service as a local volume pointed to the same local folder.
By default, this is /data/code, but you can change it in run.sh script.

# Components

## App1
One-file python application. It watches for new files in VM's local **/data/input** folder, processes them, and outputs the result in **/data/output**.

The file names must be unique otherwise the result of previous files with the same name will be rewritten by the more recent one.


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
- "arguments" can be unique for every command type

Every command is processed by its function in the app1 (see /app1/src/app1.py).

The output for all commands is a string.
The outputs are saved in the output file.
The output file has the same name as the input one, but with .txt extension. Ex: a234.json -> a234.txt.
Every line starts with command id, then one space as separator followed by command output.
Commands in the output file can be in any order.

Example of an output file:

```
1 Hello_world
2 value
3 Beautiful_sunnyday
4 Not filled !
```

To send/receive files from a remote machine can be used the following commands:

Send a file from the local machine to app1:
```
scp -i ~/.ssh/hackathon.rsa /tmp/aa.json outscale@<app1_ip>:/data/input/aa.json
```

List files in app1 /data/output:
```
ssh -o StrictHostKeyChecking=no -i ~/.ssh/hackathon.rsa outscale@<app1_ip> "ls /data/output"
```

Copy file from app1 to the local machine:
```
scp -i ~/.ssh/hackathon.rsa outscale@<app1_ip>:/data/input/aa.json /tmp/
```

## Database 1
PostgreSQL database.

It is prefilled by db1/db_init.sql script in.

For debugging you can connect to it via web interface http://<db1_vm_ip>:8080 using these connection parameters:

host: postgres
username: postgres
password: postgres
database: postgres

# Connections between containers
VMs can be accessed by their short names: app1, ms1, and db1
These hosts are added to /etc/hosts of all VMs
