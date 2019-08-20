#!/bin/bash

# cd to directory that this script is in and then up a level
script_name=$0
script_full_path=$(dirname "$0")
cd "$script_full_path"


# Activate the evirtual environment
source ../venv/bin/activate

# Modify this line with your own command line arguments
nice python run_detection_only.py &
python run_carparkagent.py -ps 300 -fn set_friendly_name -dd -fet 2000 -lat 40.780343 -lon -73.967491

pkill -KILL 'python3'

deactivate