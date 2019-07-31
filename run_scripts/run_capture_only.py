# test deployment
import argparse
import time

from carpark_agent.threaded_image_recorder import ThreadedImageRecorder
from carpark_agent.threaded_image_capture import ThreadedImageCapture

# parse the command line arguments
parser = argparse.ArgumentParser(description='Launch the Fetch Car Parking Agent for Raspberry Pi')
parser.add_argument('-rh', '--run_headless', help='use this option to run without the GUI', action='store_true')

parser.add_argument(
    '-ps',
    '--poll_seconds',
    type=float,
    help='number of seconds to wait between each polling of camera',
    default='10')

# Get command line arguments and construct database interface
args = parser.parse_args()

db = DetectionDatabase(os.path.dirname(__file__))

# Create the thread capturing images from the camera
image_capture = ThreadedImageCapture()
image_capture.start_capture()

# Create the thread to perform the vehicle detection image processing
image_recorder = ThreadedImageRecorder(
    image_capture,
    args.poll_seconds,
    db)

image_recorder.start_processing()

print("Running client headless - press Ctrl+C to quit")
try:
    while True:
        time.sleep(1)
finally:
    # Shut down
    print("killing threads...")
    image_capture.stop_capture()
    image_recorder.stop_processing()
    print("All threads stopped")
