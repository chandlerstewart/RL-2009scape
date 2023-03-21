import socket
import json
from state_processor import *
import bot_controller
import struct
import constants
from QLearning import *
import torch


STATE_MANAGER = State_Manager()
Q_AGENT = QLearningAgent(constants.STATE_SIZE, constants.ACTION_SIZE)
REPLAY_MEMORY = ReplayMemory()
STEPS_THIS_EPISODE = 0



def get_message():
    global STEPS_THIS_EPISODE, train
    message = None
    #print(STATE_MANAGER.STATE)
    if STATE_MANAGER.STATE == State.WAIT_FOR_CONNECTION:
        message = Message("waiting_for_connection")
    if STATE_MANAGER.STATE == State.WAIT_FOR_DATA:
        message = Message("server_waiting")
    if STATE_MANAGER.STATE in [State.SPAWN_BOTS, State.RESET_EPISDOE]:
        STATE_MANAGER.STATE = State.SPAWN_BOTS
        message = Message(f"spawn_bots {constants.SPAWN_LOCATION[0]} {constants.SPAWN_LOCATION[1]} {constants.NUM_BOTS}")
    if STATE_MANAGER.STATE == State.SEND_ACTION:
        message = bot_controller.next_action(json.loads(STATE_MANAGER.last_response), REPLAY_MEMORY, Q_AGENT)
        message = Message("json", message)
        STEPS_THIS_EPISODE += 1

        if (STEPS_THIS_EPISODE >= constants.NUM_STEPS):
            train = True
 
        
    if message != None:
        print(message.command)
    return message


def handle_client(json_message):
    message = Message(**json_message)

    STATE_MANAGER.manage_state(message)
    print(f"Client message: {message.command}")

    response = get_message()
    print(response.command)
    json_response = json.dumps(response.__dict__)

    return json_response.encode()


class Message:
    def __init__(self, command, info = ""):
        self.command = command
        self.info = info

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((constants.HOST, constants.PORT))
server_socket.listen()




for i in range(constants.NUM_EPISDOES):
    train = False
    while not train:
        client_socket, addr = server_socket.accept()
        length_bytes = client_socket.recv(2)
        data_size = struct.unpack('>H', length_bytes)[0]


        print(f"Connected by {addr}")
        data = client_socket.recv(data_size)

        json_data = json.loads(data.decode('utf-8'))
        
        
        response = handle_client(json_data)

        client_socket.send(response)
        client_socket.close()



    states = torch.stack(REPLAY_MEMORY.states)
    shuffle_indices = torch.randperm(states.shape[0])

    states = states[shuffle_indices]
    actions = torch.Tensor(REPLAY_MEMORY.actions)[shuffle_indices]
    rewards = torch.Tensor(REPLAY_MEMORY.rewards)[shuffle_indices]
    next_states = torch.stack(REPLAY_MEMORY.next_states)[shuffle_indices]

    batch_size = 128
    for j in range(0, len(states), batch_size):

        Q_AGENT.update(
            states[j:j+batch_size], 
            actions[j:j+batch_size],
            rewards[j:j+batch_size],
            next_states[j:j+batch_size]
            )


    print(f"Average reward for episode {i}: {torch.mean(rewards)}")
    STATE_MANAGER.STATE = State.RESET_EPISDOE
    REPLAY_MEMORY.clear()
    STEPS_THIS_EPISODE = 0
    
    train = False

    

    