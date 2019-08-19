#!/bin/bash

# cd to directory that this script is in and then up a level
script_name=$0
script_full_path=$(dirname "$0")
cd "$script_full_path"


# Activate the evirtual environment
source ../venv/bin/activate

# Modify this line with your own command line arguments
python run_client_ui.py -fn win_dc -ma 3600 -mf 4000

deactivate
