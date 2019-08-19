#!/bin/bash

# cd to directory that this script is in and then up a level
script_name=$0
script_full_path=$(dirname "$0")
cd "$script_full_path"


# Activate the evirtual environment
source ../venv/bin/activate

# Modify this line with your own command line arguments
python run_carparkagent.py -ps 120 -fn set_friendly_name -fet 2000 -lat 40.780343 -lon -73.967491

deactivate