import torch
import torch.nn as nn
import torch.optim as optim
import random
import constants
import utils

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class QNetwork(nn.Module):
    def __init__(self, state_size, action_size):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, action_size)
        self.softmax = nn.Softmax()

    def forward(self, state):
        x = torch.relu(self.fc1(state))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)


class QLearningAgent:
    def __init__(self, state_size, action_size):
        self.q_network = QNetwork(state_size, action_size).to(device)
        self.optimizer = optim.Adam(self.q_network.parameters())
        self.epsilon = 0.8

    def update(self, state, action, reward, next_state):

        q_values = self.q_network(state)
        next_q_values = self.q_network(next_state)

        q_value = q_values.gather(1, action.long().unsqueeze(1)).squeeze(1)
        next_q_value = next_q_values.max(1)[0]
    
        target = reward + 0.99 * next_q_value

        loss = (q_value - target.detach()).pow(2).mean()

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def get_action(self, state):

        if random.random() > self.epsilon:
            return random.randint(0,3)
        else:
            if len(state) == 2:
                state = utils.one_hot_state(state)
            action_prob = self.q_network(state)
            return torch.argmax(self.q_network.softmax(action_prob))

        


class MemoryStep:
    def __init__(self, state, action, reward, next_state):
        self.state = state
        self.action = action
        self.reward = reward
        self.next_state = next_state


class ReplayMemory:

    def __init__(self):
        self.states = []
        self.actions = []
        self.rewards = []
        self.next_states = []

    def append(self, memory_step):
        self.states.append(utils.one_hot_state(memory_step.state))
        self.actions.append(memory_step.action)
        self.rewards.append(memory_step.reward)
        self.next_states.append(utils.one_hot_state(memory_step.next_state))


    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)
    
    def clear(self):
        self.states.clear()
        self.actions.clear()
        self.rewards.clear()
        self.next_states.clear()
    

import math
def get_reward(state, next_state):

    prev_dist_to_goal = math.dist(state,constants.RELATIVE_GOAL_LOC)
    cur_dist_to_goal = math.dist(next_state, constants.RELATIVE_GOAL_LOC)
    start_dist_to_goal = math.dist(constants.RELATIVE_SPAWN_LOCATION, constants.RELATIVE_GOAL_LOC)
    
    if (next_state == constants.GOAL_LOC):
        return start_dist_to_goal
    elif (cur_dist_to_goal < prev_dist_to_goal and cur_dist_to_goal < start_dist_to_goal):
        return 1 - cur_dist_to_goal / start_dist_to_goal
    else:
        return 0
