
## Preconditions
1. Installed Terraform
2. Access and Private keys for DS Outscale cloud account.
3. Inititalize Terraform in the project (once after project clonning from Git)
```
terraform init
```

## Platform installation

1. Update OUTSCALE_ACCESSKEYID and OUTSCALE_SECRETKEYID in env_init.sh:
```
export OUTSCALE_ACCESSKEYID=...
export OUTSCALE_SECRETKEYID=...
export OUTSCALE_REGION="eu-west-2"
```

2. Create platform
```
./platform_create.sh
```
The script does the following:
1. Create VM with all serivces of the evaluation part of competition environment. The services are running in Docker containers.
2. Create "~/.ssh/hackathon.rsa" private key to access this VM.
3. Create "<vm>_connect.sh" files to connect to the VMs.

3. Destroy platform
```
./platform_destroy.sh
```
The script destroy all resources in the cloud.

4. Connect to VMs by ssh:
```
./<vm>_connect.sh
```
Where <vm> are app1, ms1, db1...

This files are created by platform_create.sh script.

## Connections between containers
### PostgreSQL

host: postgres
username: postgres
password: postgres
database: postgres
