# test deployment
import argparse
import time
import os

from carpark_agent.detection_database import DetectionDatabase
from carpark_agent.tk_gui_app import TkGuiApp
from carpark_agent.threaded_image_capture import ThreadedImageCapture
from carpark_agent.threaded_image_recorder import ThreadedImageRecorder
from carpark_agent.car_park_agent import CarParkAgent


# parse the command line arguments
parser = argparse.ArgumentParser(description='Launch the Fetch Car Parking Agent for Raspberry Pi')
parser.add_argument('-rd', '--reset_database', action='store_true')
parser.add_argument('-rw', '--reset_wallet', action='store_true')
parser.add_argument('-rh', '--run_headless', help='use this option to run without the GUI', action='store_true')
parser.add_argument('-rm', '--reset_mask', action='store_true')
parser.add_argument('-dd', '--disable_detection', action='store_true')
parser.add_argument('-da', '--disable_agent', action='store_true')

parser.add_argument(
    '-fet',
    '--data_price_fet',
    default=2000,
    help='price of the data in Fetch Tokens (default: 5)'
)
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
    '-li',
    '--ledger_ip',
    help='IP or name of ledger node to connect to. use 127.0.0.1 for local (default delta.fetch-ai.com)',
    type=str,
    default='alpha.fetch-ai.com')
parser.add_argument(
    '-lp',
    '--ledger_port',
    help='Port of ledger node to connect to. use 8000 for local (default 80)',
    type=str,
    default='80')
parser.add_argument(
    '-oi',
    '--oef_ip',
    help='IP or name of oef node to connect to. use 127.0.0.1 for local and k-1-alpha.fetch-ai.com for Fetch.AI servers (default 127.0.0.1)',
    type=str,
    default='127.0.0.1')
parser.add_argument(
    '-op',
    '--oef_port',
    help='Port of oef node to connect to. use 10000 for local and 50001 for Fetch.AI servers (default 10000)',
    type=str,
    default='50001')
parser.add_argument(
    '-mf',
    '--max_file_count',
    type=int,
    help='maximum number of images files to store on disk (old ones are deleted)',
    default='5000')
parser.add_argument(
    '-fn',
    '--friendly_name',
    help='A human readable name we can refer to our agent by',
    type=str,
    default='')

# Get command line arguments and construct database interface
args = parser.parse_args()
db = DetectionDatabase(os.path.dirname(__file__))

if args.reset_database:
    db.reset_database()

if args.reset_mask:
    db.reset_mask()

if not args.disable_agent:
    # Create the OEF Agent
    agent = CarParkAgent(
        oef_ip=args.oef_ip,
        oef_port=args.oef_port,
        database=db,
        reset_wallet=args.reset_wallet,
        data_price_fet=int(args.data_price_fet),
        ledger_ip=args.ledger_ip,
        ledger_port=args.ledger_port,
        friendly_name=args.friendly_name)
    agent.start_agent()

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

if not args.disable_agent:
    agent.stop_agent()

if not args.disable_detection:
    car_detection.stop_processing()

print("All threads stopped")
