import torch
import constants
import json
from enum import Enum

'''
def one_hot_state(xystate):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        state = torch.zeros(constants.X_SIZE, constants.Y_SIZE)
        state[xystate[0], xystate[1]] = 1
        state = state.flatten().to(device)
        return state
'''

class Message:
    def __init__(self, command, info = ""):
        self.command = command
        self.info = info

    def to_json_out(self):
        json_out = json.dumps(self.__dict__)
        return json_out.encode()
    

class State(Enum):
    WAIT_FOR_CONNECTION = 0
    SPAWN_BOTS = 1
    WAIT_FOR_DATA = 2
    SEND_ACTION = 3
    RESET_EPISDOE = 4

def encode_state(state):
    ret = torch.tensor(state[0] * constants.X_SIZE + state[1])
    return ret


