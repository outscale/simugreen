#! /usr/bin/python3

# Process output files

import sys, os, re, datetime

def main() -> int:
    process_powertop()
    process_output()
    process_date()
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


    total = sum([process_file(file) for file in os.listdir('metrics') if file.startswith('power-')])
    print(f"Total energy consumption: {total}")
    
    with open(os.path.join('totals', 'energy.txt'), "a") as f:
        f.write(str(total))


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

if __name__ == '__main__':
    sys.exit(main())