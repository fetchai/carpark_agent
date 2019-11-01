#!/bin/bash

# cd to directory that this script is in
script_name=$0
script_full_path=$(dirname "$0")
cd "$script_full_path"

# Activate the evirtual environment in parent
source ../venv/bin/activate

# Run the aea agent as a background thread
cd ../carpark_aea
nice aea run &
AEA_PID=$!

# Run the rest of the agent - Modify this line with your own command line arguments
python run_carparkagent.py -ps 300 -lat 40.780343 -lon -73.967491

kill $AEA_PID

deactivate