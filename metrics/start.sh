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

# Start collecting traffic on all VMs
$SSH outscale@$ms1ip "sudo killall ifstat; sudo rm -rf /data/metrics/ifstat.txt"
$SSH outscale@$ms1ip "nohup ifstat -n -t -w -i eth0 > /data/metrics/ifstat_ms1.txt 2> /data/logs/ifstat.err < /dev/null &" 

$SSH outscale@$db1ip "sudo killall ifstat; sudo rm -rf /data/metrics/ifstat.txt"
$SSH outscale@$db1ip "nohup ifstat -n -t -w -i eth0 > /data/metrics/ifstat_db1.txt 2> /data/logs/ifstat.err < /dev/null &"

$SSH outscale@$app1ip "sudo killall ifstat; sudo rm -rf /data/metrics/ifstat.txt"
$SSH outscale@$app1ip "nohup ifstat -n -t -w -i eth0 > /data/metrics/ifstat_app1.txt 2> /data/logs/ifstat.err < /dev/null &"

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

# Collect mitric files from all vms
$SCP outscale@$app1ip:/data/metrics/* metrics/
$SCP outscale@$db1ip:/data/metrics/* metrics/
$SCP outscale@$ms1ip:/data/metrics/* metrics/

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
idle_compute_energy=`cat totals/compute_idle_cons.txt`
traffic=`cat totals/traffic.txt`
total=`cat totals/total.txt`

echo 
echo "==========================================================="
echo "Execution time: $value"
echo "Correctness: $correctness"
echo "VM consumption: $energy (Wh)"
echo "Idle compute consumption: $idle_compute_energy (Wh)"
echo "$traffic"
echo "TOTAL: $total(Wh)"
echo "==========================================================="
echo 