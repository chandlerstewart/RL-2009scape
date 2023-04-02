import socket
import json
from state_processor import *
import bot_controller
import struct
import constants
from QLearning import *
import torch
import threading
import signal
import traceback



class Message:
    def __init__(self, command, info = ""):
        self.command = command
        self.info = info

    def to_json_out(self):
        json_out = json.dumps(MESSAGE_OUT.__dict__)
        return json_out.encode()

MESSAGE_IN_UPDATED = False
MESSAGE_IN = Message("temp")
MESSAGE_OUT = Message("waiting_for_connection")
SOCKET_OPEN = True

def get_message():
    global STEPS_THIS_EPISODE, MESSAGE_OUT

    if STATE_MANAGER.STATE == State.WAIT_FOR_CONNECTION:
        MESSAGE_OUT = Message("waiting_for_connection")
    if STATE_MANAGER.STATE == State.WAIT_FOR_DATA:
        MESSAGE_OUT = Message("server_waiting")
    if STATE_MANAGER.STATE in [State.SPAWN_BOTS, State.RESET_EPISDOE]:
        STATE_MANAGER.STATE = State.SPAWN_BOTS
        MESSAGE_OUT = Message(f"spawn_bots {constants.SPAWN_LOCATION[0]} {constants.SPAWN_LOCATION[1]} {constants.NUM_BOTS}")
    if STATE_MANAGER.STATE == State.SEND_ACTION:
        MESSAGE_OUT = bot_controller.next_action(json.loads(STATE_MANAGER.last_response), REPLAY_MEMORY, Q_AGENT)
        MESSAGE_OUT = Message("json", MESSAGE_OUT)
        STEPS_THIS_EPISODE += 1
 
        
    if MESSAGE_OUT != None:
        print(MESSAGE_OUT.command)
    return MESSAGE_OUT


def train(batch_size=128, epochs=5):
    states = torch.stack(REPLAY_MEMORY.states)
    shuffle_indices = torch.randperm(states.shape[0])

    
    states = states[shuffle_indices]
    actions = torch.stack(REPLAY_MEMORY.actions)[shuffle_indices]
    rewards = torch.Tensor(REPLAY_MEMORY.rewards)[shuffle_indices]
    next_states = torch.stack(REPLAY_MEMORY.next_states)[shuffle_indices]
    print(f"Average reward {torch.mean(rewards)}")


    for i in range(epochs):
        print(f"Training. Epoch {i}")
        for j in range(0, len(states), batch_size):

            Q_AGENT.update(
                states[j:j+batch_size], 
                actions[j:j+batch_size],
                rewards[j:j+batch_size],
                next_states[j:j+batch_size]
                )
            
    Q_AGENT.update_epsilon(EPISODE_NUM_STEPS)


    

def start_server():
    global MESSAGE_IN, MESSAGE_IN_UPDATED, MESSAGE_OUT, SOCKET_OPEN

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((constants.HOST, constants.PORT))
    server_socket.listen()


    while SOCKET_OPEN:
        client_socket, addr = server_socket.accept()
        length_bytes = client_socket.recv(2)
        data_size = struct.unpack('>H', length_bytes)[0]


        print(f"Connected by {addr}")
        data = client_socket.recv(data_size)

        MESSAGE_IN = Message(**json.loads(data.decode('utf-8')))
        MESSAGE_IN_UPDATED = True

        response = MESSAGE_OUT.to_json_out()
        
        

        client_socket.send(response)
        client_socket.close()




def handler(signum, frame):
    global SOCKET_OPEN
    SOCKET_OPEN = False
    exit(1)
 




batch_size = 128
epochs = 5
lr = 0.0001

STATE_MANAGER = State_Manager()
Q_AGENT = QLearningAgent(constants.STATE_SIZE, constants.ACTION_SIZE, lr=lr)
REPLAY_MEMORY = ReplayMemory()
EPISODE_NUM_STEPS = constants.EPISODE_NUM_STEPS_MIN
STEPS_THIS_EPISODE = 0


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    server_thread = threading.Thread(target = start_server)
    server_thread.start()

    EPISODE = 0
    while EPISODE < constants.NUM_EPISDOES:
        try:
            if MESSAGE_IN_UPDATED:
                STATE_MANAGER.manage_state(MESSAGE_IN)
                MESSAGE_OUT = get_message()

            #if STEPS_THIS_EPISODE % 10 == 9: # train after n steps
            #    train(batch_size=batch_size, epochs=epochs)
            #    #REPLAY_MEMORY.clear()

            if STEPS_THIS_EPISODE >= EPISODE_NUM_STEPS: #if End of Episode
                STEPS_THIS_EPISODE = 0
                EPISODE += 1
                EPISODE_NUM_STEPS  = min(constants.EPISODE_NUM_STEPS_MAX, EPISODE_NUM_STEPS + 10)
                print("======= END OF EPISODE =======")
                train(batch_size=batch_size, epochs=epochs)
                REPLAY_MEMORY.clear()
                STATE_MANAGER.STATE = State.RESET_EPISDOE
                print("======= END OF EPISODE =======")
        except Exception as e:
            traceback.print_exc()
            SOCKET_OPEN = False
            exit(1)
            
        
    SOCKET_OPEN = False

    