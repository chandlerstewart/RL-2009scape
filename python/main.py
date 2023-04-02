import server
import constants
from QLearning import *
from PPO import *
import traceback
from bot_controller import *
from utils import State



if __name__ == "__main__":
    Server = server.Server()
    Server.start()

    
    batch_size = 128
    epochs = 5
    lr = 0.001

    AGENT = QLearningAgent(constants.STATE_SIZE, constants.ACTION_SIZE,lr=lr)
    #AGENT = PPO()

    REPLAY_MEMORY = ReplayMemory()



    EPISODE = 0
    STEPS_THIS_EPISODE = 0
    EPISODE_NUM_STEPS = constants.EPISODE_NUM_STEPS_MIN

    while EPISODE < constants.NUM_EPISDOES:
        try:
            if Server.MESSAGE_IN_UPDATED:
                Server.update_message()

                if Server.STATE == State.SEND_ACTION:
                    action_data = get_action_data(Server.last_response, REPLAY_MEMORY, AGENT)
                    Server.step(action_data)
                    STEPS_THIS_EPISODE += 1

            
            if STEPS_THIS_EPISODE >= EPISODE_NUM_STEPS: #if End of Episode
                
                print("======= END OF EPISODE =======")
                AGENT.train(REPLAY_MEMORY, STEPS_THIS_EPISODE, batch_size=batch_size, epochs=epochs)
                AGENT.update_epsilon(STEPS_THIS_EPISODE)
                #AGENT.update(REPLAY_MEMORY.rewards, REPLAY_MEMORY.actions, REPLAY_MEMORY.states)  #PPO
                REPLAY_MEMORY.clear()

                Server.STATE = State.RESET_EPISDOE
                EPISODE_NUM_STEPS  = min(constants.EPISODE_NUM_STEPS_MAX, EPISODE_NUM_STEPS + 10)
                STEPS_THIS_EPISODE = 0
                EPISODE += 1
                print("======= END OF EPISODE =======")
            

        except Exception as e:
            traceback.print_exc()
            Server.close()
            exit(1)
            
        
    SOCKET_OPEN = False
    