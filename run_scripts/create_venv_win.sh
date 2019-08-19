#!/bin/bash

# cd to directory that this script is in and then up a level
script_name=$0
script_full_path=$(dirname "$0")
cd "$script_full_path"


virtualenv --system-site-packages ../venv

# In windows the acivate program is in Scripts, but on linux it is in bin - this makes it rather
# awkward to automate it - so make a symbolic link called bin to the scripts dir so our other sctipts work
ln -s ../venv/Scripts ../venv/bin
