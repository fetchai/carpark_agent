
import threading
import json
import pprint
import time
import os
import base58
import random
from typing import List
from datetime import datetime

# oef stuff

from oef.agents import OEFAgent
from oef.schema import Description
from oef.messages import CFP_TYPES
from oef.query import Query, Constraint, Eq
from carpark_agent.car_detect_dataModel import CarParkDataModel

# Ledger stuff
from fetchai.ledger.api import LedgerApi
from fetchai.ledger.crypto import Entity
from fetchai.ledger.api import TransactionApi


# State machine for testing own service connetion and registration
# service_test_state_starting_up = "starting_up"
# service_test_state_disconnected = "disconnected"
# service_test_state_idle = "idle"
# service_test_state_searching = "searching"
# service_test_state_test_cfp = "test_cfp"
# service_test_state_waiting_for_cfp = "waiting_for_cfp"
# service_test_state_try_restart_agent = "try_restart_agent"

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
        # surely I should be called super first?!?
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
        super(CarParkAgent, self).__init__(oef_key, oef_ip, oef_port)

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
        self.last_detection_time= 0
        self.car_park_service_description = None
        self.test_dlg_id = 0
        # self.service_test_state = service_test_state_starting_up
        # self.last_service_test_state = service_test_state_starting_up
        # self.wait_for_cfp_time = 0
        # self.service_test_cfp_timeout = 60
        # self.db.set_system_status("service_connection_test", self.service_test_state)
        # self.service_test_idle_duration = 10

        # Set up system status
        self.db.set_system_status("ledger-status", "OK")
        self.db.set_system_status("ledger-ip", self.ledger_ip)
        self.db.set_system_status("ledger-port", self.ledger_port)
        self.db.set_system_status("oef-status", "OK")
        self.db.set_system_status("oef-ip", self.oef_ip)
        self.db.set_system_status("oef-port", self.oef_port )

        # Ledger stuff
        self.api = LedgerApi(ledger_ip, ledger_port)
        self.tx = TransactionApi(ledger_ip, ledger_port)
        self.cleared_fet = self.read_balance()
        self.uncleared_fet = self.read_balance()

        # Thread control
        self.agent_thread = threading.Thread(target=self.run_function)
        self.balance_thread = threading.Thread(target=self.balance_poll_function)
        # self.service_poller_thread = threading.Thread(target=self.service_poller_function)
        self.kill_event = threading.Event()

    def start_agent(self):
        self.agent_thread.start()
        self.balance_thread.start()
       # self.service_poller_thread.start()

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

        # Need to do this to shut down the event loop (this will be fixed in OEF SDK at some point)
        if self._task is not None:
            self._loop.call_soon_threadsafe(self._task.cancel)
        if self._task is not None:
            self.stop()
        self.agent_thread.join(120)
        self.balance_thread.join(120)

        try:
            self.unregister_service(0, self.car_park_service_description)
            self.disconnect()
            pass
        except Exception as e:
            print("having some problems closing connection")

    # def restart_agent(self):
    #     try:
    #         self.unregister_service(0, self.car_park_service_description)
    #         self.disconnect()
    #     except Exception as e:
    #         print("Had a problem disconnecting the agent")
    #     if self._task is not None:
    #         self._loop.call_soon_threadsafe(self._task.cancel)
    #         self.stop()
    #
    #     self.agent_thread.join(120)
    #     self.agent_thread = threading.Thread(target=self.run_function)
    #     self.agent_thread.start()

    def balance_poll_function(self):
        while not self.kill_event.wait(0):
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

            time.sleep(1)

    def run_function(self):
        # Need to have some data in the database before we can register our service
        while (self.lat == "" or self.lon == "") and not self.kill_event.wait(0):
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
            print("Waiting for some data before registering OEF agent")
            time.sleep(5)

        while not self.kill_event.wait(0):
            try:
                self.unregister_service(0, self.car_park_service_description)
                self.disconnect()
                pass
            except Exception as e:
                print("having some problems closing connection")

            try:
                self.connect()
                # Sometimes connection is not fully up before going to next line
                time.sleep(1)
                self.register_service(0, self.car_park_service_description)
                self.db.set_system_status("oef-status", "OK")

            except Exception as e:
                print("Failed to connect to OEF: {}".format(e))
                self.db.set_system_status("oef-status", "Error: Failed to connect")

            try:
                self.run()
                # need to do this in case we exited due to an exception
                if self._task is not None:
                    self._loop.call_soon_threadsafe(self._task.cancel)
                if self._task is not None:
                    self.stop()
                print("Runfunction exited")
            except Exception as e:
                self.db.set_system_status("oef-status", "Error: Failed to connect")
                print("Runfunction exited with exception")

            time.sleep(1)



    # regularly search for ourselves to ensure our service is still connected otherwise we
    # may sit there waiting for agents to find us and connect, not get any, and not realise
    # it is because we are no longer descoverable
    # def service_poller_function(self):
    #     service_test_start_time = time.time()
    #     while not self.kill_event.wait(0):
    #         on_enter = self.service_test_state != self.last_service_test_state
    #         self.last_service_test_state = self.service_test_state
    #
    #         #print("{}: self.service_test_state = {}".format(time.time(), self.service_test_state))
    #         if self.service_test_state == service_test_state_disconnected:
    #             try:
    #                 self.unregister_service(0, self.car_park_service_description)
    #                 self.disconnect()
    #             except Exception as e:
    #                 print("Had problems attempting to connect to oef")
    #
    #             try:
    #                 self.attempt_connection()
    #             except Exception as e:
    #                 print("Had problems attempting to connect to oef")
    #
    #         # Test if we can search for ourselves
    #         elif self.service_test_state == service_test_state_idle:
    #             if on_enter:
    #                 service_test_start_time = time.time()
    #
    #             if time.time() - service_test_start_time > self.service_test_idle_duration:
    #                 try:
    #                     self.agents_data = {}
    #                     query = Query(
    #                         [Constraint("unique_id", Eq(self.public_key))],
    #                         CarParkDataModel())
    #                     search_id = random.randint(1, 1000000)
    #                     self.search_services(search_id, query)
    #                     self.service_test_state = service_test_state_searching
    #                 except Exception as e:
    #                     print("Failed to search oef: {}".format(e))
    #                     self.db.set_system_status("oef-status", "Error: Failed to contact OEF")
    #                     self.service_test_state = service_test_state_disconnected
    #         elif self.service_test_state == service_test_state_searching:
    #             if on_enter:
    #                 service_test_start_time = time.time()
    #
    #             # if we dont get a response:
    #             if time.time() - service_test_start_time > self.service_test_idle_duration:
    #                 self.db.set_system_status("oef-status", "Error: Failed to contact OEF")
    #                 self.service_test_state = service_test_state_disconnected
    #
    #         elif self.service_test_state == service_test_state_test_cfp:
    #             self.test_dlg_id = random.randint(1, 1000000)
    #             self.send_cfp(0, self.test_dlg_id, self.public_key, 0, None)
    #             self.service_test_state = service_test_state_waiting_for_cfp
    #             self.wait_for_cfp_time = time.time()
    #
    #         elif self.service_test_state == service_test_state_waiting_for_cfp:
    #             if time.time() - self.wait_for_cfp_time > self.service_test_cfp_timeout:
    #                 self.service_test_state = service_test_state_disconnected
    #
    #         elif self.service_test_state == service_test_state_try_restart_agent:
    #             self.restart_agent()
    #
    #         self.db.set_system_status("service_connection_test", self.service_test_state)
    #         time.sleep(0.1)

    # # in answer to the service polling
    # def on_search_result(self, search_id: int, agents: List[str]):
    #     if len(agents) == 0:
    #         self.service_test_state = service_test_state_disconnected
    #     else:
    #         self.service_test_state = service_test_state_test_cfp


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

    #
    # def wallet_2_oef_key(self, wallet_public_key: str):
    #     time12 = format(int(time.time()), '012d')
    #     time12_as_bytes = str.encode(time12)    # this is still 12 bytes in length
    #     return base58.b58encode(wallet_public_key + time12_as_bytes).decode("utf-8")
    #
    # def oef_2_wallet_key(self, oef_public_key: str):
    #     return base58.b58decode(oef_public_key.encode("utf-8"))[:-12]

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