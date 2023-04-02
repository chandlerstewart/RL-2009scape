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
        self.fc1 = nn.Linear(state_size, 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(256, 256)
        self.fc4 = nn.Linear(256, action_size)

    def forward(self, state):
        x = torch.relu(self.fc1(state.float()))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        return self.fc4(x)




class QLearningAgent:
    def __init__(self, state_size, action_size, lr=0.001, start_epsilon=1, min_epsilon=0.2, decay_rate=0.01, decay_type = "linear"):
        self.q_network = QNetwork(state_size, action_size).to(device)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=lr)
        self.start_epsilon = start_epsilon
        self.epsilon = start_epsilon
        self.min_epsilon = min_epsilon
        self.decay_rate = decay_rate
        self.decay_type = decay_type

    def update_epsilon(self, steps):
        if self.decay_type == 'linear':
            self.epsilon = max(self.min_epsilon, self.start_epsilon - steps * self.decay_rate)
        elif self.decay_type == 'exponential':
            self.epsilon = max(self.min_epsilon, self.start_epsilon * (self.decay_rate ** steps))


        print(f"EPSILON: {self.epsilon}")

    def update(self, state, action, reward, next_state):
        state = state.unsqueeze(dim=0).T
        next_state = next_state.unsqueeze(dim=0).T

        q_values = self.q_network(state)
        next_q_values = self.q_network(next_state)

        q_value = q_values[0][action]
        next_q_value = next_q_values.max(1)[0]
        
        target = reward + 0.99 * next_q_value

        loss = (q_value - target.detach()).pow(2).mean()

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def get_action(self, state):
        state = utils.encode_state(state)
        if random.random() < self.epsilon:
            return torch.tensor([random.randint(0,3)])
        else:
            state = torch.tensor([[state]], device=device, dtype=torch.float32)
            action_prob = self.q_network(state)
            return torch.argmax(torch.nn.functional.softmax(action_prob)).unsqueeze(0)

        


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
        self.states.append(utils.encode_state(memory_step.state))
        self.actions.append(memory_step.action)
        self.rewards.append(memory_step.reward)
        self.next_states.append(utils.encode_state(memory_step.next_state))

    
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
        #return 1 - cur_dist_to_goal / start_dist_to_goal
        #return 1
        return start_dist_to_goal - cur_dist_to_goal
    else:
        return -1
