
import argparse
import time

from carpark_agent.car_park_client_agent import CarParkClientAgent

# parse the command line arguments
parser = argparse.ArgumentParser(description='Launch the Fetch Car Parking Agent for Raspberry Pi')

parser.add_argument(
    '-mf',
    '--max_price_fet',
    default=4000,
    help='maximum price we would be prepared to pay for data in Fetch Tokens (default: 4000)'
)
parser.add_argument(
    '-ma',
    '--max_detection_age_seconds',
    type=int,
    default=3600,
    help='maximum age that detections can be for us to care about them. Default: 3600 [1-hour]'
)
parser.add_argument(
    '-li',
    '--ledger_ip',
    help='IP or name of ledger node to connect to. use 127.0.0.1 for local (default dev.fetch-ai.com)',
    type=str,
    default='dev.fetch-ai.com')
parser.add_argument(
    '-lp',
    '--ledger_port',
    help='Port of ledger node to connect to. use 8000 for local (default 80)',
    type=str,
    default='80')

parser.add_argument(
    '-fn',
    '--friendly_name',
    help='A human readable name we can refer to our agent by',
    type=str,
    default='')
parser.add_argument('-rw', '--reset_wallet', action='store_true')
args = parser.parse_args()


print("Starting Fetch Car Parking Client Agent...")

client_agent = CarParkClientAgent(
    oef_ip="k-1-delta.fetch-ai.com",
    oef_port=50001,
    reset_wallet=args.reset_wallet,
    max_price_fet=int(args.max_price_fet),
    max_detection_age_seconds=int(args.max_detection_age_seconds),
    ledger_ip=args.ledger_ip,
    ledger_port=args.ledger_port,
    friendly_name=args.friendly_name)

client_agent.start_agent()

print("Running client headless - press Ctrl+C to quit")
while True:
    time.sleep(1)

client_agent.stop_agent()
