#!/bin/bash

script_name=$0
script_full_path=$(dirname "$0")

cd "$script_full_path"
source venv/bin/activate
python3 run_carparkagent.py -ps 120 -fn set_friendly_name
