
import threading
import time
from typing import List
import os
import base58
import json
import asyncio
import random
import pprint

from datetime import datetime

# oef agent stuff
from oef.query import Query, Constraint, Range, NotEq
from oef.messages import PROPOSE_TYPES
from oef.agents import OEFAgent
from oef.core import AsyncioCore
from carpark_agent.car_detect_dataModel import CarParkDataModel

# Ledger
from fetchai.ledger.api import LedgerApi
from fetchai.ledger.api import TransactionApi
from fetchai.ledger.crypto import Entity, Address, Identity

def logger(*args):
    print(">>", *args)

class CarParkClientAgent(OEFAgent):

    def __init__(
            self,
            oef_ip,
            oef_port,
            reset_wallet,
            max_price_fet,
            max_detection_age_seconds,
            ledger_ip,
            ledger_port,
            friendly_name,
            run_dir):
        # surely I should be called super first?!?
        self.run_dir = run_dir
        self.entity = self.create_or_load_wallet(reset_wallet,  "car_park_client_agent_private.key")
        print("Client wallet key: " + str(self.entity.public_key_bytes))
        oef_key = self.wallet_2_oef_key(self.entity.public_key_bytes)
        print("Client oef key: " + oef_key)
        print("Address(self.entity): " + str(Address(self.entity)))
        print("oef_ip: " + oef_ip)
        print("oef_port: " + str(oef_port))
        print("ledger_ip: " + ledger_ip)
        print("ledger_port: " + str(ledger_port))
        self.core = AsyncioCore(logger=logger)
        self.core.run_threaded()
        super(CarParkClientAgent, self).__init__(public_key=oef_key, oef_addr=oef_ip, oef_port=oef_port, core=self.core)

        # configuration
        self.cost = 0
        self.max_price_fet = max_price_fet
        self.max_detection_age_seconds = max_detection_age_seconds
        self.ledger_ip = ledger_ip
        self.ledger_port = ledger_port
        self.oef_ip = oef_ip
        self.oef_port = oef_port

        if friendly_name != "":
            self.friendly_name = friendly_name
        else:
            self.friendly_name = "car_park_agent_client_{}".format(random.randint(1, 1000000))

        # Market data
        self.agents_data = {}
        self.last_search_id = -1

        # Ledger
        self.api = LedgerApi(ledger_ip, ledger_port)
        self.tx = TransactionApi(ledger_ip, ledger_port)
        self.transfer_fee = 1
        self.oef_status = "Trying to connect..."
        self.ledger_status = "OK"
        self.cleared_fet = 0
        try:
            self.cleared_fet = self.api.tokens.balance(self.entity)
        except Exception as e:
            self.ledger_status = "Failed: Error on connection"

        self.in_progress_transactions = {}
        self.transaction_lock = threading.Lock()

        # Thread control
        self.polling_thread = None
        self.kill_event = threading.Event()

        # Logging
        self.msg_log = []

    def start_agent(self):
        # Let the polling function actualy handle the connection
        self.polling_thread = threading.Thread(target=self.poll_function)
        self.polling_thread.start()

    def stop_agent(self):
        self.kill_event.set()

        if self.get_state() == "connected":
            self.disconnect()

        self.core.stop()

        self.polling_thread.join(10)


    def poll_function(self):
        while not self.kill_event.wait(0):
            self.handle_transaction_clearing()

            # If we got disconnected from the OEF, then reconnect
            if self.get_state() != "connected" and not self.kill_event.wait(0):
                self.oef_status = "Trying to connect..."
                self.connect()
                if self.get_state() == "connected":
                    self.oef_status = "OK: {}".format(self.get_state())
                else:
                    self.oef_status = "Error: {}".format(self.get_state())

            time.sleep(2)


    def push_msg(self, text):
        t = int(time.time())
        txt = time.strftime('%Y-%m-%d %H:%M:%S:', time.localtime(t)) + "\t" + text
        self.msg_log.append(txt)

    def pop_msg(self):
        return self.msg_log.pop(0)

    def has_log_msgs(self):
        return len(self.msg_log)



# Constraint("latitude", Range((0., 90.))), Constraint("longitude", Range((0., 180.)))
    def perform_search(self):
        # try:
            self.push_msg("Search for car parking services...")
            self.agents_data = {}
            query = Query(
                [Constraint("latitude", NotEq(0.0))],
                CarParkDataModel())
            self.last_search_id = random.randint(1, 1000000)
            self.search_services(self.last_search_id, query)
        # except Exception as e:
        #     print("Failed to search oef: {}".format(e))
        #     self.oef_status = "Error: Failed to contact OEF"


    def on_search_result(self, search_id: int, agents: List[str]):
        if search_id != self.last_search_id:
            print("Old search results - wait for latest ones")
            return

        self.push_msg("Search Results returned")

        """For every agent returned in the service search, send a CFP to obtain resources from them."""
        if len(agents) == 0:
            print("No agent found.")
            return
        else:
            print("{} agents found.".format(len(agents)))

        for agent in agents:
            self.agents_data[agent] = {'public_key': agent}


    def can_do_cfp(self):
        return len(self.agents_data) > 0


    def do_cfp_to_all(self):
        # Clear the agent data apart from the public keys
        new_data = {}

        for data in self.agents_data.values():
            key = data['public_key']
            new_data[key] = {'public_key': key}

        self.agents_data = new_data

        # Send a CFP to all agents in the list
        for agent in self.agents_data:
            print("[{0}]: Sending to agent {1}".format(self.public_key, agent))
            self.push_msg("Sending cfp to : " + agent[:8] + "....")

            # we send a 'None' query, meaning "give me all the resources you can propose."
            self.send_cfp(1, random.randint(1, 1000000), agent, 0, b'')

            # Send them our friendly name too so they can display it
            data = {}
            data['message_type'] = 'friendly_name_intro'
            data['friendly_name'] = self.friendly_name
            encoded_data = json.dumps(data).encode("utf-8")
            self.send_message(0, random.randint(1, 1000000), agent, encoded_data)


    def on_propose(self, msg_id: int, dialogue_id: int, origin: str, target: int, proposals: PROPOSE_TYPES):
        """When we receive a Propose message, answer with an Accept."""
        print("[{0}]: Received propose from agent {1}".format(self.public_key, origin))

        if len(proposals) == 0:
            print("{} Warning: agent has sent zero proposals")

        if len(proposals) != 1:
            print("{} Warning: agent has sent several proposals - UI not really set up for this "
                  "- just use first one".format(origin))

        # If for some reason our agent is not in the list - then add it
        if origin not in self.agents_data:
            self.agents_data[origin] = {'public_key': origin}

        # Add additional data we now know about the proposal
        proposal = proposals[0]
        self.agents_data[origin]['lat'] = proposal['lat']
        self.agents_data[origin]['lon'] = proposal['lon']
        self.agents_data[origin]['price'] = proposal['price']
        self.agents_data[origin]['friendly_name'] = proposal['friendly_name']
        self.agents_data[origin]['last_detection_time'] = proposal['last_detection_time']
        self.agents_data[origin]['max_spaces'] = proposal['max_spaces']
        self.agents_data[origin]['proposal_dialogue_id'] = dialogue_id
        self.agents_data[origin]['proposal_msg_id'] = msg_id


        self.push_msg("Proposal returned from : " + proposal['friendly_name'])


    def generate_wealth(self, fet):
        self.push_msg("Generate_wealth")
        try:
            self.api.sync(self.api.tokens.wealth(self.entity, fet))
        except Exception as e:
            self.ledger_status = "Failed: Error on connection"
        self.handle_transaction_clearing()

    def can_do_accept_decline(self):
        # check if we have enough fund
        required_fet = self.calc_funds_needed()

        # Note we need both cleared and uncleared fet to be more than what we need
        # because we can't rely on uncleared fet being available by the time the transaction
        # in processed and we can't be sure that the cleared get takes into account
        # in-progress transactions
        if required_fet > min(self.cleared_fet, self.calc_uncleared_fet()):
            return False

        for agent in self.agents_data.values():
            if 'proposal_dialogue_id' in agent:
                return True

        return False

    # This actually returns an upper bound on what we might need.
    def calc_funds_needed(self):
        fet_required = 0
        for proposal in self.agents_data.values():
            if 'proposal_dialogue_id' in proposal:
                if self.is_acceptable_proposal(proposal['price'], proposal['last_detection_time']):
                    fet_required += self.max_price_fet + self.transfer_fee

        return fet_required

    def do_accept_decline_to_all(self):
        print("do_accept_decline_to_all")
        for proposal in self.agents_data.values():
            if 'num_free_spaces' in proposal:
                del proposal['num_free_spaces']

            # check that we have enough funds
            fet_required = self.calc_funds_needed()

            if fet_required > self.cleared_fet:
                print("****** ERROR - trying to accept transactions we don't have enough FET for")

            # only do it for entries which have a proposal
            if 'proposal_dialogue_id' in proposal:
                origin = proposal['public_key']
                dialogue_id = proposal['proposal_dialogue_id']
                msg_id = proposal['proposal_msg_id']
                if self.is_acceptable_proposal(proposal['price'], proposal['last_detection_time']):
                    print("Accept transaction")
                    self.send_accept(msg_id+1, dialogue_id, origin, msg_id)
                    self.push_msg("Request data from: " + proposal['friendly_name'])
                else:
                    print("Declining proposal as price was too high or data was too old")
                    self.push_msg("Decline to request data from : " + proposal['friendly_name'])
                    self.send_decline(msg_id+1, dialogue_id, origin, msg_id)

    def is_acceptable_proposal(self, price, last_detection_time):
        return price <= self.max_price_fet and int(time.time()) - last_detection_time <= self.max_detection_age_seconds

    def on_message(self, msg_id: int, dialogue_id: int, origin: str, content: bytes):
        # print("Received message: origin={}, dialogue_id={}, content={}".format(origin, dialogue_id, content))
        data = json.loads(content.decode())
        if 'message_type' not in data:
            return

        message_type = data['message_type']
        if message_type == "car_park_data":
            # check that the price is still within what we are able to accept. We will have only accepted it if it
            # was below our maximum - if they are asking for more - then just pay the max what we were will to pay
            price_to_pay = min(int(data['price_fet']), self.max_price_fet)
            time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data["epoch"]))
            print("{}: message: {} ...".format(message_type, time_str))

            print("Data: {}".format(data))

            print("Paying for data...")
            payee_public_key_bytes = self.oef_2_wallet_key(origin)
            payee_id = Identity(payee_public_key_bytes)

            print("{}: Transfer: {} fet from {} to {} with transaction fee {} fet".format(
                datetime.now().strftime("%H:%M:%S"),
                price_to_pay,
                Address(self.entity),
                Address(payee_id),
                self.transfer_fee))
            tx = self.api.tokens.transfer(self.entity, payee_id, price_to_pay, self.transfer_fee)
            print("{}: tx: {}".format(datetime.now().strftime("%H:%M:%S"), tx))

            # Record our data so we can display it in the UI
            if origin not in self.agents_data:
                self.agents_data[origin] = {'public_key': origin}

            self.push_msg("Car Park Data received from : " + self.agents_data[origin]["friendly_name"])

            self.agents_data[origin]['num_free_spaces'] = data['free_spaces']
            self.agents_data[origin]['last_detection_time'] = data['epoch']

            # Send the transaction hash to the agent supplying the data
            receipt = {}
            receipt["message_type"] = "car_park_data_receipt"
            receipt["transaction_hash"] = tx
            receipt["amount"] = price_to_pay
            encoded_data = json.dumps(receipt).encode("utf-8")
            print("[{0}]: Sending data to {1}: {2}".format(
                self.public_key,
                origin,
                pprint.pformat(receipt)))
            self.send_message(msg_id + 1, dialogue_id, origin, encoded_data)
            with self.transaction_lock:
                self.in_progress_transactions[tx] = -price_to_pay - self.transfer_fee

    def calc_uncleared_fet(self):
        total = self.cleared_fet
        for amount in self.in_progress_transactions.values():
            total += amount
        return total

    def handle_transaction_clearing(self):
        try:
            with self.transaction_lock:
                tx_to_remove = []
                for key, value in self.in_progress_transactions.items():
                    if self.tx.status(key) == 'Executed':
                        self.push_msg("Transaction {} complete".format(key[:4] + "...."))
                        print("Transaction complete: {}".format(key))
                        tx_to_remove.append(key)

                for key in tx_to_remove:
                    del self.in_progress_transactions[key]

            self.cleared_fet = self.api.tokens.balance(self.entity)

        except Exception as e:
            self.ledger_status = "Failed: Error on connection"

    def on_decline(self, msg_id: int, dialogue_id: int, origin: str, target: int):
        print("Received a decline!")
        self.received_declines += 1

    def wallet_2_oef_key(self, wallet_public_key: str):
        return base58.b58encode(wallet_public_key).decode("utf-8")

    def oef_2_wallet_key(self, oef_public_key: str):
        return base58.b58decode(oef_public_key.encode("utf-8"))

    def create_or_load_wallet(self, reset_wallet, filename):

        private_key_dir = str(os.path.join(self.run_dir, '..', "temp_files"))

        # ensure the directory exists
        if not os.path.isdir(private_key_dir):
            os.mkdir(private_key_dir)

        file_path = private_key_dir + "/" + filename
        if not reset_wallet and os.path.isfile(file_path):
            with open(file_path, 'r') as private_key_file:
                return Entity.load(private_key_file)
        else:
            if not os.path.isdir(private_key_dir ):
                os.mkdir(private_key_dir+"/")

            entity = Entity()
            with open(file_path, 'w') as private_key_file:
                entity.dump(private_key_file)

            return entity

