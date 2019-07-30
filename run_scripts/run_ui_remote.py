# test deployment
import argparse
# HMM THIS FILE DOESN'T WORK!!

from carpark_agent.detection_database import DetectionDatabase
from carpark_agent.tk_gui_app import TkGuiApp
from carpark_agent.threaded_image_capture import ThreadedImageCapture
from carpark_agent.file_paths import FilePaths

parser = argparse.ArgumentParser(description='Launch the Fetch Car Parking Agent for Raspberry Pi')
parser.add_argument(
    '-sf',
    '--screen_width_fraction',
    type=float,
    default=0.9,
    help='What portion of the screen width the GUI should take up. 1 => whole screen (default: 0.9)'
)
parser.add_argument(
    '-rl',
    '--remote_directory_location',
    type=str,
    default='/Volumes/Home Directory/Desktop/RPiProjects/cctv_parking02/car_detection_RPi/carpark_agent',
    help='Path to symlink to remote directory'
)
args = parser.parse_args()


# Get command line arguments and construct database interface
db = DetectionDatabase(args.remote_directory_location)


# Create the thread capturing images from the camera and make them available in a threadsafe way
image_capture = ThreadedImageCapture()
image_capture.start_capture()


TkGuiApp(
    "Fetch.AI car-park agent",
    image_capture,
    db,
    args.screen_width_fraction)

# Shut down
print("killing threads...")
image_capture.stop_capture()
print("All threads stopped")
