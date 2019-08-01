import argparse
import os
from carpark_agent.tk_client_gui_app import TkClientGuiApp
from carpark_agent.car_park_client_agent import CarParkClientAgent

parser = argparse.ArgumentParser(description='Launch the Fetch Car Parking Agent for Raspberry Pi')
parser.add_argument(
    '-sf',
    '--screen_width_fraction',
    type=float,
    default=0.9,
    help='What portion of the screen width the GUI should take up. 1 => whole screen (default: 0.9)'
)
parser.add_argument(
    '-mf',
    '--max_price_fet',
    default=4000,
    help='maximum price we would be prepared to pay for data in Fetch Tokens (default: 20)'
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
    '-oi',
    '--oef_ip',
    help='IP or name of oef node to connect to. use 127.0.0.1 for local (default k-1-delta.fetch-ai.com)',
    type=str,
    default='k-1-delta.fetch-ai.com')
parser.add_argument(
    '-op',
    '--oef_port',
    help='Port of oef node to connect to. use 10000 for local (default 50001)',
    type=str,
    default='50001')
parser.add_argument(
    '-fn',
    '--friendly_name',
    help='A human readable name we can refer to our agent by',
    type=str,
    default='')
parser.add_argument('-rw', '--reset_wallet', action='store_true')
args = parser.parse_args()


client_agent = CarParkClientAgent(
    oef_ip=args.oef_ip,
    oef_port=args.oef_port,
    reset_wallet=args.reset_wallet,
    max_price_fet=int(args.max_price_fet),
    max_detection_age_seconds=float(args.max_detection_age_seconds),
    ledger_ip=args.ledger_ip,
    ledger_port=args.ledger_port,
    friendly_name=args.friendly_name,
    run_dir=os.path.dirname(__file__))

client_agent.start_agent()


TkClientGuiApp("Fetch.AI car-park client agent", client_agent)

client_agent.stop_agent()
