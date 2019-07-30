# Car detection

## Preparation (Ubuntu; tested on a Google Cloud VM)

    sudo apt-get update`
    sudo apt-get install htop vim mc python3-dev ffmpeg virtualenv libatlas-base-dev libsm6 libxext6 libjasper-dev libqtgui4 libqt4-test
    sudo apt-get install cython
    virtualenv -p python3.6 env
    source env/bin/activate
    pip install numpy tensorflow colour scikit-image keras IPython h5py Cython tablib crontab clint docopt
    pip install coco
    pip install pycocotools imgaug
    

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
