# test deployment
import argparse
import time
import os

from carpark_agent.detection_database import DetectionDatabase
from carpark_agent.threaded_car_detection import ThreadedCarDetection

# parse the command line arguments
parser = argparse.ArgumentParser(description='Launch the Fetch Car Parking Agent for Raspberry Pi')
parser.add_argument('-rd', '--reset_database', action='store_true')
parser.add_argument('-rw', '--reset_wallet', action='store_true')
parser.add_argument('-rm', '--reset_mask', action='store_true')

parser.add_argument(
    '-lat',
    '--default_latitude',
    help='default default_latitude to use of GPS not available',
    type=str,
    default='52.235027')

parser.add_argument(
    '-lon',
    '--default_longitude',
    type=str,
    help='default longitude to use of GPS not available',
    default='0.153508')


parser.add_argument(
    '-ps',
    '--poll_seconds',
    type=float,
    help='number of seconds to wait between each polling of camera',
    default='2')
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


# Create the thread to perform the vehicle detection image processing
car_detection = ThreadedCarDetection(
    db,
    (args.default_latitude, args.default_longitude),
    args.max_file_count)

car_detection.start_processing()


print("Running client headless - press Ctrl+C to quit")
try:
    while True:
        time.sleep(1)
finally:
    # Shut down
    print("killing threads...")
    car_detection.stop_processing()
    print("All threads stopped")
