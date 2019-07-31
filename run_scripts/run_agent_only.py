# test deployment
import argparse
import time
import os


from carpark_agent.detection_database import DetectionDatabase
from carpark_agent.car_park_agent import CarParkAgent

# parse the command line arguments
parser = argparse.ArgumentParser(description='Launch the Fetch Car Parking Agent for Raspberry Pi')
parser.add_argument('-rw', '--reset_wallet', action='store_true')


parser.add_argument(
    '-fet',
    '--data_price_fet',
    default=2000,
    help='price of the data in Fetch Tokens (default: 5)'
)

parser.add_argument(
    '-li',
    '--ledger_ip',
    help='IP or name of ledger node to connect to. use 127.0.0.1 for local (default delta.fetch-ai.com)',
    type=str,
    default='delta.fetch-ai.com')
parser.add_argument(
    '-lp',
    '--ledger_port',
    help='Port of ledger node to connect to. use 8000 for local (default 80)',
    type=str,
    default='80')
parser.add_argument(
    '-op',
    '--oef_port',
    help='Port of oef node to connect to. use 10000 for local (default 50001)',
    type=str,
    default='50001')
parser.add_argument(
    '-oi',
    '--oef_ip',
    help='IP or name of oef node to connect to. use 127.0.0.1 for local (default k-1-delta.fetch-ai.com)',
    type=str,
    default='k-1-delta.fetch-ai.com')
parser.add_argument(
    '-fn',
    '--friendly_name',
    help='A human readable name we can refer to our agent by',
    type=str,
    default='')

# Get command line arguments and construct database interface
args = parser.parse_args()

# Get command line arguments and construct database interface
db = DetectionDatabase(os.path.dirname(__file__))

# Create the OEF Agent
agent = CarParkAgent(
    oef_ip=args.oef_ip,
    oef_port=args.oef_port,
    database=db,
    reset_wallet=args.reset_wallet,
    data_price_fet=args.data_price_fet,
    ledger_ip=args.ledger_ip,
    ledger_port=args.ledger_port,
    friendly_name=args.friendly_name)
agent.start_agent()

print("Running client headless - press Ctrl+C to quit")
while True:
    time.sleep(1)

# Shut down
print("killing threads...")
agent.stop_agent()
print("All threads stopped")
