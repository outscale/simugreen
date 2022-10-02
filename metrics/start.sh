SSH="ssh -o StrictHostKeyChecking=no -i ~/.ssh/hackathon.rsa"
SCP="scp -i ~/.ssh/hackathon.rsa"

# Clean 
rm -rf output/*
rm -rf metrics/*
rm -rf totals/*

# Get IPs of all VMs 
# If new vm is added add it here
app1ip=$(cat ../app1_connect.sh | sed 's/.*@\([.0-9]*\)/\1/')
db1ip=$(cat ../db1_connect.sh | sed 's/.*@\([.0-9]*\)/\1/')
ms1ip=$(cat ../ms1_connect.sh | sed 's/.*@\([.0-9]*\)/\1/')

# Start collecting energy consumption metrics on all VMs
$SSH outscale@$ms1ip "sudo killall powertop; sudo rm -rf /data/metrics/*" 
$SSH outscale@$ms1ip "nohup sudo powertop --csv=/data/metrics/power.csv --time=15 --iteration=1000 > /data/logs/powertop.log 2> /data/logs/powertop.err < /dev/null &" 

$SSH outscale@$db1ip "sudo killall powertop; sudo rm -rf /data/metrics/*" 
$SSH outscale@$db1ip "nohup sudo powertop --csv=/data/metrics/power.csv --time=15 --iteration=1000 > /data/logs/powertop.log 2> /data/logs/powertop.err < /dev/null &" 

$SSH outscale@$app1ip "sudo killall powertop; sudo rm -rf /data/metrics/*" 
$SSH outscale@$app1ip "nohup sudo powertop --csv=/data/metrics/power.csv --time=15 --iteration=1000 > /data/logs/powertop.log 2> /data/logs/powertop.err < /dev/null &" 


# Start collecting traffic metrics on all VMs
# - TODO -

# Log test start timestamp
date > metrics/start_date.txt

# Copy command files to app1
$SSH outscale@$app1ip "sudo rm -rf /data/output/*; sudo rm -rf /data/input/*" 
$SCP input/* outscale@$app1ip:/data/input/

# Watch output folder on app1 unitil all expected files are created
is_terminated() {
    # Compare the list of files in input and app1.output. Terminated when equal
    $SSH outscale@$app1ip "ls /data/output/" \
        | ./wait_termination.py
}
while true; do
    is_terminated
    if [ $? -eq 0 ]; then
        echo "All files are processed"
        break
    fi
    sleep 5    
done

# Log test stop timestamp
date > metrics/stop_date.txt

# Collect energy consumption files from all vms
$SCP outscale@$app1ip:/data/metrics/* metrics/
$SCP outscale@$db1ip:/data/metrics/* metrics/
$SCP outscale@$ms1ip:/data/metrics/* metrics/

# Collect traffic files from all vms
# - TODO -

# Collect output files
$SCP outscale@$app1ip:/data/output/* output/

# Process collected files
./process.py


# === Outputs ===
# 1. Total consumption of all VMs in Watts
# 2. Total traffic from all VMs
# 3. Execution time
# 4. Correctness of the test

value=`cat totals/time.txt`
correctness=`cat totals/correctness.txt`
energy=`cat totals/energy.txt`

echo 
echo "==========================================================="
echo "Execution time: $value"
echo "Correctness: $correctness"
echo "Energy: $energy (Wh)"
echo "==========================================================="
echo 