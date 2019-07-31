# test deployment
import argparse
import os

from carpark_agent.detection_database import DetectionDatabase
from carpark_agent.tk_gui_app import TkGuiApp
from carpark_agent.threaded_image_capture import ThreadedImageCapture
from carpark_agent.threaded_image_recorder import ThreadedImageRecorder

parser = argparse.ArgumentParser(description='Launch the Fetch Car Parking Agent for Raspberry Pi')
parser.add_argument(
    '-sf',
    '--screen_width_fraction',
    type=float,
    default=0.9,
    help='What portion of the screen width the GUI should take up. 1 => whole screen (default: 0.9)'
)
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

args = parser.parse_args()



# Get command line arguments and construct database interface
db = DetectionDatabase(os.path.dirname(__file__))

# Create the thread capturing images from the camera and make them available in a threadsafe way
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


TkGuiApp(
    "Fetch.AI car-park agent",
    image_capture,
    db,
    args.screen_width_fraction)

# Shut down
print("killing threads...")
image_recorder.stop_processing()
image_capture.stop_capture()
print("All threads stopped")
