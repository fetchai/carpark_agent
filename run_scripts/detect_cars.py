"""Process frames or videos. Detect cars. Save frames or videos with colorful boxes."""

import os
import datetime
import skimage.io
import argparse
import cv2

from car_detection.helpers import ParkedCarDetector


# parse the commnad line arguments
parser = argparse.ArgumentParser(description='Perform car detection on videos')
parser.add_argument('--input', type=str, help='Input directory for video frames or input file of video (if arg ends in .mp4)')
parser.add_argument('--output', type=str, help='Output directory for video frames or output file of video (if arg ends in .mp4)')
parser.add_argument('--ofps', type=int, help='frames per second of output video (only used if input is frames directory) - default 25', default=25)
parser.add_argument('--ext', type=str, help='extension of images to load and save - default png', default='png')
args = parser.parse_args()

input_is_video = (args.input[-4:] == ".mp4")
output_is_video = (args.output[-4:] == ".mp4")


# do some command line argument error checking
if input_is_video:
    if not os.path.isfile(args.input):
        print("Input looks like a video file, but it doesn't exits")
        exit()
else:
    if not os.path.isdir(args.input):
        print("Input looks like a directory, but it doesn't exist")
        exit()

if output_is_video:
    output_dir = os.path.dirname(args.output)
    if not os.path.isdir(output_dir):
        print("Output looks like a video but location doesn't exist")
        exit()
else:
    if not os.path.isdir(args.output):
        print("Output looks like a directory, but it doesn't exist")
        exit()


# Create a list of images from a directory or video
if (input_is_video):
    vidcap = cv2.VideoCapture(args.input)
    if not vidcap:
        print("Failed to read video file: " + args.input)
        exit()
    width = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    images = []

    success, image = vidcap.read()

    while success:
        images.append(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        success, image = vidcap.read()
else:
    images = skimage.io.imread_collection(args.input + "/*." + args.ext)
    if len(images) == 0:
        print("No images in directory")
        exit()
    image0 = images[0]
    height, width, depth = images[0].shape

    fps = args.ofps

# Create the car detector
detector = ParkedCarDetector()
detector.enable_flicker_removal = False
detector.enable_remove_large_unconfident = False

# if outputting a video - set up the video
if output_is_video:
    print("output video parameters: " + str(width) + ", " + str(height) + ", " + str(fps))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Be sure to use lower case
    out_vid = cv2.VideoWriter(args.output, fourcc, fps, (width, height))

# Cycle through the image
checkpoint = datetime.datetime.now()
for i, image in enumerate(images):
    result = detector.detect_cars(image)

    # check time
    now = datetime.datetime.now()
    print('Step: {} - Time: {}'.format(i, now - checkpoint))
    checkpoint = now


    # visualisation
    if (output_is_video):
        out_image = detector.image_visualise(image, result)
        height, width, depth = out_image.shape

        out_image = cv2.cvtColor(out_image, cv2.COLOR_RGB2BGR)
        out_vid.write(out_image);
        #skimage.io.imsave(args.output + "_{:05d}.png".format(i), out_image)
    else:
        # Get ready to visualize
        out_filename = args.output + '/frame_{:05d}.{}'.format(i, args.ext)
        detector.save_visualise(image, result, out_filename)

    # print overall summary stats of detections
    if (detector.moving is not None):
        print('   Detected cars: {}'.format(len(result['class_ids'])))
        print('   Moving: {}'.format(sum(detector.moving)))
        print('   Standing or parked: {}'.format(len(detector.moving) - sum(detector.moving)))

    # print detailed stats for each detection
    if result is not None:
        for sc, mr in zip(result['scores'], result['max_rois']):
            print("sc: " + str(sc) + ", mr: " + str(mr))

if output_is_video:
    print("Saving video file: " + args.output)
    out_vid.release()


