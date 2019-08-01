# Fetch Car Park Agent
This is a project to get a Fetch.AI agent running on a Rasperry Pi which utilises the camera to report on free parking spaces. This data is made available on the Fetch network and can be purchased by other agents. 

This project primarily targets the Raspbery Pi 4. It can be made to run on the Raspberry Pi 3, but it striggles a little. I include instructions for both versions.

This document will take you through:
1. Physically building the Camera/Raspberry PI module
2. Preparing the Raspberry Pi so we do not need a monitor/keybaord etc. attached
3. Installing the Fetch carpark_agent software on the Rasperry Pi
4. Using the software to report on car parking spaces
5. Installing the client software on a desktop machine (mac only at the moment)


## Physically building the Camera/Raspberry PI module
You will need - I've added links to the things I bought:
* Raspberry Pi 4 [link](https://thepihut.com/products/raspberry-pi-4-model-b?gclid=EAIaIQobChMImcuwvcfh4wIVirHtCh3szg2EEAAYASAAEgJQ_fD_BwE)
* Case to put Raspbery Pi and Camera in [link](https://uk.rs-online.com/web/p/products/1270210/?grossPrice=Y&cm_mmc=UK-PLA-DS3A-_-google-_-CSS_UK_EN_CatchAll-_-Catch+All-_-PRODUCT_GROUP&matchtype=&pla-381930223918&gclsrc=aw.ds&&gclid=EAIaIQobChMIqoC2hsjh4wIVxbHtCh0w5whsEAQYASABEgKsJfD_BwE)
* Clamp and Arm [link](https://www.amazon.co.uk/dp/B011769YUM/ref=pe_3187911_189395841_TE_dp_1)
* (optional) Adafruit GPS unit [link] (https://www.amazon.co.uk/dp/B01H1R8BK0?ref_=pe_3187911_264767211_E_301_dt_1)

The GPS unit is optional 
    
## Download weights

    cd resources/weights/
    wget "https://github.com/matterport/Mask_RCNN/releases/download/v2.0/mask_rcnn_coco.h5"


## Prepare folders

    mkdir -p /tmp/video-frames
    mkdir -p /tmp/boxed-frames

## Prepare frames

    ffmpeg -i resources/video/car_short_25fps.mp4 -vf fps=50 /tmp/video-frames/frame_%05d.png
    
or to save some space
    
    ffmpeg -i path_to_your_video.mp4 -vf fps=50 /tmp/video-frames/frame_%05d.jpg
    

## PYTHONPATH

Add `car_detection` folder to your `PYTHONPATH`.

    export PYTHONPATH=$PYTHONPATH:/your/path/to/car_detection


## Run the script

    python scripts/process.py

## Assemble the frames

    ffmpeg -r 25 -i /tmp/boxed-frames/frame_%05d.png -c:v libx264 -vf fps=25 -pix_fmt yuv420p your_final_video.mp4

or if the format was jpg
    
    ffmpeg -r 25 -i /tmp/boxed-frames/frame_%05d.jpg -c:v libx264 -vf fps=25 -pix_fmt yuv420p your_final_video.mp4
