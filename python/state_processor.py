from enum import Enum

class State(Enum):
    WAIT_FOR_CONNECTION = 0
    SPAWN_BOTS = 1
    WAIT_FOR_DATA = 2
    SEND_ACTION = 3
    RESET_EPISDOE = 4


class State_Manager:
    def __init__(self):
        self.STATE = State.WAIT_FOR_CONNECTION

    
    def manage_state(self,message):
        self.last_response = message
        if self.STATE == State.RESET_EPISDOE:
            return
        elif message.command == "Connected":
            self.STATE = State.SPAWN_BOTS
            print("State: Spawn Bots")
        elif message.command in ["Wait", "Success: spawn_bots"]:
            self.STATE = State.WAIT_FOR_DATA
            print("State: Waiting for DATA")
        elif message.command == "json":
            self.last_response = message.info
            self.STATE = State.SEND_ACTION

