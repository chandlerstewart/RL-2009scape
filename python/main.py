import server
import constants
from QLearning import *
from PPO import *
import traceback
from bot_controller import *
from utils import State
#from HAC import HAC



render = False

# primitive action bounds and offset
action_bounds = constants.ACTION_SIZE
action_offset = np.array([0.0])
action_offset = torch.FloatTensor(action_offset.reshape(1, -1)).to(device)
action_clip_low = np.array([-1.0 * action_bounds])
action_clip_high = np.array([action_bounds])

# state bounds and offset
state_bounds_np = np.array([0.9, 0.07])
state_bounds = torch.FloatTensor(state_bounds_np.reshape(1, -1)).to(device)
state_offset =  np.array([-0.3, 0.0])
state_offset = torch.FloatTensor(state_offset.reshape(1, -1)).to(device)
state_clip_low = np.array([-1.2, -0.07])
state_clip_high = np.array([0.6, 0.07])

# exploration noise std for primitive action and subgoals
exploration_action_noise = np.array([0.1])        
exploration_state_noise = np.array([0.02, 0.01]) 

goal_state = np.array([0.48, 0.04])        # final goal state to be achived
threshold = np.array([0.01, 0.02])         # threshold value to check if goal state is achieved


# HAC parameters:
k_level = 2                 # num of levels in hierarchy
H = 20                      # time horizon to achieve subgoal
lamda = 0.3                 # subgoal testing parameter

# DDPG parameters:
gamma = 0.95                # discount factor for future rewards
n_iter = 100                # update policy n_iter times in one DDPG update
batch_size = 100            # num of transitions sampled from replay buffer
lr = 0.0001




if __name__ == "__main__":
    Server = server.Server()
    Server.start()

    
    #QLearning parameters:
    #batch_size = 128
    #epochs = 5
    #lr = 0.0001



    AGENT = QLearningAgent(constants.STATE_SIZE, constants.ACTION_SIZE,lr=lr)
    #AGENT = PPO()
    #AGENT = HAC(k_level, H, constants.STATE_SIZE, constants.ACTION_SIZE, render, threshold, 
    #            action_bounds, action_offset, state_bounds, state_offset, lr)

    #AGENT.set_parameters(lamda, gamma, action_clip_low, action_clip_high, 
    #                   state_clip_low, state_clip_high, exploration_action_noise, #exploration_state_noise)

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

            #if STEPS_THIS_EPISODE % 10 == 9:
                #AGENT.train(REPLAY_MEMORY, STEPS_THIS_EPISODE, batch_size=batch_size, epochs=epochs)

            
            if STEPS_THIS_EPISODE >= EPISODE_NUM_STEPS: #if End of Episode
                
                print(f"======= END OF EPISODE {EPISODE} =======")
                AGENT.train(REPLAY_MEMORY, STEPS_THIS_EPISODE, batch_size=batch_size)
                #AGENT.update(REPLAY_MEMORY.rewards, REPLAY_MEMORY.actions, REPLAY_MEMORY.states)  #PPO
                REPLAY_MEMORY.clear()

                Server.STATE = State.RESET_EPISDOE
                EPISODE_NUM_STEPS  = min(constants.EPISODE_NUM_STEPS_MAX, EPISODE_NUM_STEPS + 5)
                STEPS_THIS_EPISODE = 0
                EPISODE += 1
                print(f"======= END OF EPISODE {EPISODE} =======")
            

        except Exception as e:
            traceback.print_exc()
            Server.close()
            exit(1)
            
        
    SOCKET_OPEN = False
    