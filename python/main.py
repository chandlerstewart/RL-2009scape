import gymnasium as gym
import math
import random
import matplotlib
import matplotlib.pyplot as plt
from collections import namedtuple, deque
from itertools import count

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

import constants
from QLearning import DQN, ReplayMemory, Transition
import server
from utils import State
import utils
import traceback

from Trainer import DoubleQTrainer

matplotlib.use("TkAgg")
plt.ion()
#plt.show(block=False)




# if GPU is to be used
#device = torch.device("cuda" if torch.cuda.is_available() else "cpu")



# BATCH_SIZE is the number of transitions sampled from the replay buffer
# GAMMA is the discount factor as mentioned in the previous section
# EPS_START is the starting value of epsilon
# EPS_END is the final value of epsilon
# EPS_DECAY controls the rate of exponential decay of epsilon, higher means a slower decay
# TAU is the update rate of the target network
# LR is the learning rate of the ``AdamW`` optimizer
BATCH_SIZE = 128
GAMMA = 0.99
EPS_START = 0.9
EPS_END = 0.05
EPS_DECAY = 1000
TAU = 0.005
LR = 1e-4

# Get number of actions from gym action space
n_actions = constants.ACTION_SIZE
n_observations = constants.STATE_SIZE





steps_done = 0



Server = server.Server()
Server.start()

episode = 0
steps_this_episode = 0
steps_per_episode = constants.EPISODE_NUM_STEPS_MIN


trainer = DoubleQTrainer()

best_reward_mean = 0
mean_rewards = []

while episode < constants.NUM_EPISDOES:
    try:
        if Server.MESSAGE_IN_UPDATED:
                Server.update_message()

                if Server.STATE == State.SEND_ACTION:
                    trainer.step(Server.last_response)
                    Server.step(utils.bot_to_json(trainer.bots))
                    steps_this_episode += 1
                    
                    

                if steps_this_episode >= steps_per_episode:
                    episode += 1
                    steps_this_episode = 0
                    steps_per_episode = min(constants.EPISODE_NUM_STEPS_MAX, steps_per_episode + 5)
                    mean_rewards.append(trainer.reward_mean())
                    utils.plot_rewards(mean_rewards)
                    if trainer.reward_mean() > best_reward_mean:
                        best_reward_mean = trainer.reward_mean()
                        trainer.save_model()

                    

                    Server.STATE = State.RESET_EPISDOE
                    
                    
                    print("Step: " + str(steps_this_episode) + " Episode: " + str(episode) + " Steps: " + str(steps_per_episode))
                    print("Reward Mean: " + str(trainer.reward_mean()))
                    print("Epsilon: " + str(trainer.epsilon()))
                    print("Top Reward: " + str(trainer.reward_max()))
                    trainer.clear_memory()


    except Exception as e:
            traceback.print_exc()
            Server.close()
            exit(1)






