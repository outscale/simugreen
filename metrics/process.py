#! /usr/bin/python3

# Process output files

import sys, os, re, datetime

def main() -> int:
    watts = process_powertop()
    process_output()
    time_sec = process_date()
    watts += process_iddle_consumption(time_sec)
    watts += process_traffic()
    watts = round(watts, 2)
    print(f"Total consumption: {watts}(Wh)")

    with open(os.path.join('totals', 'total.txt'), "w") as f:
        f.write(str(watts))

    return 0


"""
Process files with energy consumption
"""
def process_powertop():

    def process_file(path):

        def process_line(line):
            time_sec = 15 # time value of powertop. i.e. the number of seconds in one interval
            block = re.search("([0-9]+ .?W)", line).group(1)
            value, unit = re.search('([0-9]*)[ \t]*(.*)', block).groups()
            
            # convert value to Watts
            value = int(value)
            if unit == 'mW':
                value = value / 1000
            elif  unit == 'uW':
                value = value / 1000000
            elif  unit == 'kW':
                value = value * 1000

            # convert Watts in Wh
            value = (value * time_sec) / 3600
            return value

        with open(os.path.join('metrics', path)) as f:
            total = sum([process_line(i) for i in f.readlines() if re.search("([0-9]+ .?W)", i)])
            print(f"Energy consumption for {path}: {total}")
            return total


    total = round(sum([process_file(file) for file in os.listdir('metrics') if file.startswith('power-')]),2)
    print(f"Total energy consumption: {total}")
    
    with open(os.path.join('totals', 'energy.txt'), "w") as f:
        f.write(str(total))
    return total


"""
Check if output files equal to the expected ones
Commands in output files can be in any order
"""
def process_output():
    output_files = os.listdir('output')
    expected_files = os.listdir('expected')
    assert(output_files == expected_files)

    with open(os.path.join('totals', 'correctness.txt'), "w") as out:
        for file in output_files:
            with open(os.path.join('expected', file)) as f:
                expected = sorted([i.strip() for i in f.readlines() if len(i.strip()) > 0])
            with open(os.path.join('output', file)) as f:
                output = sorted([i.strip() for i in f.readlines() if len(i.strip()) > 0])
            if expected != output:
                print(f"Error in {file}")
                print("Expected:", expected)
                print("Received output:", output)
                out.write(f"{file} - ERROR\n")
            else:
                out.write(f"{file} - OK\n")


def process_date():
    with open(os.path.join('metrics', 'start_date.txt')) as f:
        start = re.search('([0-9]{2}:[0-9]{2}:[0-9]{2})', f.readlines()[0]).group(1)
        start = datetime.datetime.strptime(start, "%H:%M:%S")

    with open(os.path.join('metrics', 'stop_date.txt')) as f:
        stop = re.search('([0-9]{2}:[0-9]{2}:[0-9]{2})', f.readlines()[0]).group(1)
        stop = datetime.datetime.strptime(stop, "%H:%M:%S")

    print(f"Execution time: {(stop - start)}")

    with open(os.path.join('totals', 'time.txt'), "w") as out:
        out.write(f"{(stop - start)}")

    return (stop - start).total_seconds()


def process_iddle_consumption(time_sec):
    SERVER_CORES = 48
    SERVER_RAM = 1024
    SERVER_BASE_CONSUMPTION = 400 

    compute_idle_consumption = 0

    with open("../main.tf") as f:
        
        def process_line(line):
            gr = re.search('tinav([0-9]?)\.c([0-9]*)r([0-9]*)p([0-9]*)', line)
            if gr:
                gen, cores, ram, perf = [int(i) for i in gr.groups()]
                if perf == 2:
                    cores /= 2
                elif perf == 3:
                    cores /= 4
                
                nb_vm_per_server = min(SERVER_CORES / cores, SERVER_RAM / ram)
                compute_idle_consumption = SERVER_BASE_CONSUMPTION / nb_vm_per_server * time_sec / 3600

                print(f"gen: {gen}, cores: {cores}, ram: {ram}, perf: {perf}, part: {nb_vm_per_server}, vm idle consumption: {compute_idle_consumption}")
                return compute_idle_consumption
            return 0
        
        compute_idle_cons = round(sum([process_line(line) for line in f.readlines()]), 2)
    
    print("total compute idle consumption: ", compute_idle_cons)

    with open(os.path.join('totals', 'compute_idle_cons.txt'), "w") as out:
        out.write(f"{compute_idle_cons}")

    return compute_idle_cons


def process_traffic():
    CONSUMPTION_PER_GB = 100 # Wh/GB
    def process_file(path):

        def process_line(line):
            # 12:36:39      6.51      5.01
            gr = re.search("[0-9:]*[ ]*([0-9.]+)[ ]*([0-9.]+)", line)
            if gr:
                kbs_in, kbs_out = [float(i) for i in gr.groups()]
                return kbs_in + kbs_out
            return 0

        with open(os.path.join('metrics', path)) as f:
            total = sum([process_line(i) for i in f.readlines()])
            print(f"Total traffic for {path}: {total}")
            return total


    traffic = sum([process_file(file) for file in os.listdir('metrics') if file.startswith('ifstat_')])
    traffic = round(traffic/(1024*1024),4)
    consumption = round(traffic * CONSUMPTION_PER_GB,2)
    print(f"Total traffic: {traffic}(GB), Traffic power consumption: {consumption}(Wh)")
    
    with open(os.path.join('totals', 'traffic.txt'), "w") as f:
        f.write(f"Total traffic: {traffic}(GB), Traffic power consumption: {consumption}(Wh)")
    
    return consumption


if __name__ == '__main__':
    sys.exit(main())