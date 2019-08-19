#!/bin/bash

# cd to directory that this script is in
script_name=$0
script_full_path=$(dirname "$0")
cd "$script_full_path"

./wget.exe "https://github.com/matterport/Mask_RCNN/releases/download/v2.0/mask_rcnn_coco.h5"