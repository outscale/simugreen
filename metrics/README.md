This folder contains scripts to test the system

# File structure
```
.
├── README.md - this file
├── expected - folder with expected outputs
│   ├── prime.txt
│   └── store_prices.txt
├── input - folder with commands to run
│   ├── prime.json
│   └── store_prices.json
├── metrics - empty folder used start.sh
├── output -  empty folder used start.sh
├── process.py - script used by start.sh
├── start.sh - main script to run the evaluation
├── totals -  empty folder used by start.sh
└── wait_termination.py - script used by start.sh
```

PLEASE DO NOT CHANGE_SCRIPTS IN THIS FOLDER!

You can change files in ```input``` and ```expected``` folders.

Folders with content:
- input - place for input command files
- expected - files with expected ouputs. Lines are sorted by command id

# Run tests
1. Create/update files with commands in ```metrics/input```
2. Create/update files with expected output of these files in ```metrics/expected```
3. Run test:
```
cd metrics
./start.sh
```
