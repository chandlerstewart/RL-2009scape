import torch
import constants

'''
def one_hot_state(xystate):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        state = torch.zeros(constants.X_SIZE, constants.Y_SIZE)
        state[xystate[0], xystate[1]] = 1
        state = state.flatten().to(device)
        return state
'''

def encode_state(state):
    ret = torch.tensor(state[0] * constants.X_SIZE + state[1])
    return ret