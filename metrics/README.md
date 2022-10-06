This folder contains scripts to test the system

You can change files in [input](input) and [expected](expected).

For example, if you optimize command "A", you can leave/create only one file with this command in ```input``` and ```expected```, and run tests only for it.

PLEASE DO NOT CHANGE THE SCRIPTS IN THIS FOLDER!

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
├── process.py - script used by start.sh
├── start.sh - main script to run the evaluation
└── wait_termination.py - script used by start.sh
```

# Run tests
1. Create/update files with commands in ```metrics/input```
2. Create/update files with expected output of these files in ```metrics/expected```
3. Run test:
```
cd metrics
./start.sh
```

**ATTENTION**: You may need to wait 5-10 minutes after platform creation before running tests. This time is needed to load the database.
