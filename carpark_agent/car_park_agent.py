
import threading
import json
import pprint
import time
import os
import base58
import random
from datetime import datetime

# oef stuff
from oef.agents import OEFAgent
from oef.core import AsyncioCore
#
# from typing import List
# from oef.agents import PROPOSE_TYPES
# from oef.query import Eq, Constraint
# from oef.query import Query

#from oef.query import Query, Constraint, NotEq


from oef.schema import Description
from oef.messages import CFP_TYPES
from carpark_agent.car_detect_dataModel import CarParkDataModel

# Ledger stuff
from fetchai.ledger.api import LedgerApi
from fetchai.ledger.crypto import Entity
from fetchai.ledger.api import TransactionApi

def logger(*args):
    print(">>", *args)

class CarParkAgent(OEFAgent):

    def __init__(
            self,
            oef_ip,
            oef_port,
            database,
            reset_wallet,
            data_price_fet,
            ledger_ip,
            ledger_port,
            friendly_name):

        # We need to call super - but don't do it yet!
        self.db = database

        self.entity = self.create_or_load_wallet(reset_wallet,  "car_park_agent_private.key")
        print("Agent wallet key: " + str(self.entity.public_key_bytes))
        oef_key = self.wallet_2_oef_key(self.entity.public_key_bytes)
        print("Agent oef key: " + oef_key)
        print("oef_ip: " + oef_ip)
        print("oef_port: " + str(oef_port))
        print("ledger_ip: " + ledger_ip)
        print("ledger_port: " + str(ledger_port))
        self.oef_ip = oef_ip
        self.oef_port = oef_port
        self.core = AsyncioCore(logger=logger)
        self.core.run_threaded()
        super(CarParkAgent, self).__init__(public_key=oef_key, oef_addr=oef_ip, oef_port=oef_port, core=self.core)

        # Configuration
        self.data_price_fet = data_price_fet
        self.ledger_ip = ledger_ip
        self.ledger_port = ledger_port
        if friendly_name != "":
            self.friendly_name = friendly_name
        else:
            self.friendly_name = "car_park_agent_client_{}".format(random.randint(1, 1000000))
        self.db.add_friendly_name(self.public_key, self.friendly_name, True)

        # Set up data model object
        self.lat = ""
        self.lon = ""
        self.last_detection_time = 0
        self.car_park_service_description = None
        self.test_dlg_id = 0

        # Set up system status
        self.db.set_system_status("ledger-status", "OK")
        self.db.set_system_status("ledger-ip", self.ledger_ip)
        self.db.set_system_status("ledger-port", self.ledger_port)
        self.db.set_system_status("oef-status", "OK")
        self.db.set_system_status("oef-ip", self.oef_ip)
        self.db.set_system_status("oef-port", self.oef_port)
        self.is_service_registered = False

        # Ledger stuff
        self.api = LedgerApi(ledger_ip, ledger_port)
        self.tx = TransactionApi(ledger_ip, ledger_port)
        self.cleared_fet = self.read_balance()
        self.uncleared_fet = self.read_balance()

        # Thread control
        self.polling_thread = threading.Thread(target=self.poll_function)

        self.kill_event = threading.Event()

    def start_agent(self):
        self.db.set_system_status("oef-status", "Trying to connect...")

        # Let the polling loop handle connections
        self.polling_thread.start()

    def read_balance(self):
        try:
            balance = self.api.tokens.balance(self.entity)
            self.db.set_system_status("ledger-status", "OK")
            return balance
        except Exception as e:
            print("Failed to read balance from ledger: {}".format(e.args))
            self.db.set_system_status("ledger-status", "Error: Failed to connect")
            return -1

    def stop_agent(self):
        self.kill_event.set()

        if self.get_state() == "connected":
            self.disconnect()

        self.core.stop()

        self.polling_thread.join(120)


    def poll_function(self):

        while not self.kill_event.wait(0):
            # Check if we have data before registering our service with the oef
            if self.get_state() == "connected" and (self.lat == "" or self.lon == "" or not self.is_service_registered):
                data = self.db.get_latest_detection_data(1)
                if data is not None and len(data) != 0:
                    self.lat = data[0]["lat"]
                    self.lon = data[0]["lon"]
                    self.car_park_service_description = Description(
                        {
                            "latitude": float(self.lat),
                            "longitude": float(self.lon),
                            "unique_id": str(self.public_key)
                        }, CarParkDataModel()
                    )
                    self.register_service(0, self.car_park_service_description)
                    self.is_service_registered = True

                else:
                    print("Waiting for some data before registering OEF agent")

            # poll for balance
            new_fet = self.read_balance()
            if new_fet != self.cleared_fet:
                print("{0} fet has changed: {1:.10f}".format(datetime.now().strftime("%H:%M:%S"), new_fet))

            self.cleared_fet = new_fet
            self.db.set_fet(self.cleared_fet, str(int(time.time())))

            # poll if transactions have been completed
            in_progress_transactions = self.db.get_in_progress_transactions()
            try:
                for transaction in in_progress_transactions:
                    tx_hash = transaction['tx_hash']
                    if self.tx.status(tx_hash) == 'Executed':
                        self.db.set_transaction_complete(tx_hash)
            except Exception as e:
                print("Error querying status of transaction: {}".format(e))
                self.db.set_system_status("ledger-status", "Error: Failed to connect")

            # If we got disconnected from the OEF, then reconnect
            if self.get_state() != "connected" and not self.kill_event.wait(0):
                self.db.set_system_status("oef-status", "Trying to connect...")
                self.connect()
                self.is_service_registered = False
                if self.get_state() == "connected":
                    self.db.set_system_status("oef-status", "OK: {}".format(self.get_state()))
                else:
                    self.db.set_system_status("oef-status", "Error: {}".format(self.get_state()))

            time.sleep(5)
        print("Leaving poll loop!")


    def on_message(self, msg_id: int, dialogue_id: int, origin: str, content: bytes):
        # print("Received message: origin={}, dialogue_id={}, content={}".format(origin, dialogue_id, content))
        data = json.loads(content.decode())
        if 'message_type' not in data:
            return

        message_type = data['message_type']
        if message_type == "car_park_data_receipt":
            if 'transaction_hash' not in data:
                return
            if 'amount' not in data:
                return

            self.db.add_in_progress_transaction(
                data['transaction_hash'],
                origin,
                self.public_key,
                int(data['amount']))

            # Message logging
            self.db.set_dialogue_status(dialogue_id, origin, "on_car_park_data_receipt", "[NONE]")

        if message_type == "friendly_name_intro":
            if 'friendly_name' not in data:
                return

            self.db.add_friendly_name(origin, data['friendly_name'])


    def on_cfp(self, msg_id: int, dialogue_id: int, origin: str, target: int, query: CFP_TYPES):
        # Send a simple Propose to the sender of the CFP
        print("[{0}]: Received CFP from {1}".format(self.public_key, origin))

            # TO DO check that we can trust the other agent - these systems are not yet
        # implemented in the Ledger/OEF
        # If we don't trust them, we may want to include a condition that they must
        # pay before we will send the data - for the moment, just assume the agent is trustworthy

        # prepare the proposal with a given price.
        data = self.db.get_latest_detection_data(1)
        del data[0]['raw_image_path']
        del data[0]['processed_image_path']

        last_detection_time = data[0]["epoch"]
        max_spaces = data[0]["free_spaces"] + data[0]["total_count"]
        proposal = Description({
            "lat": data[0]["lat"],
            "lon": data[0]["lon"],
            "price": self.data_price_fet,
            "friendly_name": self.friendly_name,
            "last_detection_time": last_detection_time,
            "max_spaces": max_spaces,
        })
        print("[{}]: Sending propose at price: {}".format(self.public_key, self.data_price_fet))
        self.send_propose(msg_id + 1, dialogue_id, origin, target + 1, [proposal])

        # Message logging
        self.db.set_dialogue_status(dialogue_id, origin, "on_cfp", "send send proposal")

    def on_accept(self, msg_id: int, dialogue_id: int, origin: str, target: int):
        # Once we received an Accept, send the requested data
        print("[{0}]: Received accept from {1}."
              .format(self.public_key, origin))

        data = self.db.get_latest_detection_data(1)
        if data is None:
            return

        data[0]["price_fet"] = self.data_price_fet
        data[0]["message_type"] = "car_park_data"
        encoded_data = json.dumps(data[0]).encode("utf-8")
        print("[{0}]: Sending data to {1}: {2}".format(
            self.public_key,
            origin,
            pprint.pformat(data)))
        self.send_message(0, dialogue_id, origin, encoded_data)

        # Message logging
        self.db.set_dialogue_status(dialogue_id, origin, "on_accept", "send car_park_data")

    def wallet_2_oef_key(self, wallet_public_key: str):
        return base58.b58encode(wallet_public_key).decode("utf-8")

    def oef_2_wallet_key(self, oef_public_key: str):
        return base58.b58decode(oef_public_key.encode("utf-8"))


    def create_or_load_wallet(self, reset_wallet, filename):
        private_key_dir = self.db.temp_dir

        file_path = private_key_dir + "/" + filename
        if not reset_wallet and os.path.isfile(file_path):
            with open(file_path, 'r') as private_key_file:
                return Entity.load(private_key_file)
        else:
            if not os.path.isdir(private_key_dir):
                os.mkdir(private_key_dir + "/")

            entity = Entity()
            with open(file_path, 'w') as private_key_file:
                entity.dump(private_key_file)

            return entity

    # # Constraint("latitude", Range((0., 90.))), Constraint("longitude", Range((0., 180.)))
    # def perform_search(self):
    #     # try:
    #     query = Query(
    #         [Constraint("latitude", NotEq(0.0))],
    #         CarParkDataModel())
    #     self.search_services(random.randint(1, 1000000), query)
