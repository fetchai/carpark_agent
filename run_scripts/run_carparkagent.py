# test deployment
import argparse
import time
import os

from carpark_agent.detection_database import DetectionDatabase
from carpark_agent.tk_gui_app import TkGuiApp
from carpark_agent.threaded_image_capture import ThreadedImageCapture
from carpark_agent.threaded_image_recorder import ThreadedImageRecorder



# parse the command line arguments
parser = argparse.ArgumentParser(description='Launch the Fetch Car Parking Agent for Raspberry Pi')
parser.add_argument('-rd', '--reset_database', action='store_true')
parser.add_argument('-rw', '--reset_wallet', action='store_true')
parser.add_argument('-rh', '--run_headless', help='use this option to run without the GUI', action='store_true')
parser.add_argument('-rm', '--reset_mask', action='store_true')
parser.add_argument('-dd', '--disable_detection', action='store_true')


parser.add_argument(
    '-sf',
    '--screen_width_fraction',
    type=float,
    default=0.9,
    help='What portion of the screen width the GUI should take up. 1 => whole screen (default: 0.9)'
)
parser.add_argument(
    '-lat',
    '--default_latitude',
    help='default default_latitude to use if GPS is not available or has never been read',
    type=str,
    default='20.079735')
parser.add_argument(
    '-lon',
    '--default_longitude',
    type=str,
    help='default longitude to use if GPS is not available or has never been read',
    default='-157.422098')
parser.add_argument(
    '-ps',
    '--poll_seconds',
    type=float,
    help='number of seconds to wait between each polling of camera',
    default='300')  # 5 mins
parser.add_argument(
    '-mf',
    '--max_file_count',
    type=int,
    help='maximum number of images files to store on disk (old ones are deleted)',
    default='5000')

# Get command line arguments and construct database interface
args = parser.parse_args()
db = DetectionDatabase(os.path.dirname(__file__))

if args.reset_database:
    db.reset_database()

if args.reset_mask:
    db.reset_mask()

# Create the thread capturing images from the camera
image_capture = ThreadedImageCapture()
image_capture.start_capture()

# Create the thread to get images from the camera and save them to disk
# at regular intervals
image_recorder = ThreadedImageRecorder(
    image_capture,
    args.poll_seconds,
    args.max_file_count,
    db)

image_recorder.start_processing()
print("Recorder started")

# Ensure detection is activated by default when we start up
# we have the time it takes for the libaries to initialise in order to disable it
db.set_system_status("detection", "unpaused")

# Create the thread to perform the vehicle detection image processing
if not args.disable_detection:
    from carpark_agent.threaded_car_detection import ThreadedCarDetection
    car_detection = ThreadedCarDetection(
        db,
        (args.default_latitude, args.default_longitude),
        args.max_file_count)

    car_detection.start_processing()
else:
    car_detection = None

print("Detection started")

print("About to start gui")
# (optionally) create a GUI application (or just a loop which waits to be cancelled)
if not args.run_headless:
    TkGuiApp("Fetch.AI car-park agent", image_capture, db, args.screen_width_fraction)
else:
    print("Running client headless - press Ctrl+C to quit")
    while True:
        time.sleep(1)

# Shut down
print("killing threads...")
image_recorder.stop_processing()

if image_capture is not None:
    image_capture.stop_capture()


if not args.disable_detection:
    car_detection.stop_processing()

print("All threads stopped")
