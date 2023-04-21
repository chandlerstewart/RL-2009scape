import torch
import torch.nn as nn
import torch.optim as optim
import random
import constants
import utils
import math

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class QNetwork(nn.Module):
    def __init__(self, state_size, action_size):
        super(QNetwork, self).__init__()
        layer_size = 128
        self.fc1 = nn.Linear(state_size, layer_size)
        self.fc2 = nn.Linear(layer_size, layer_size)
        self.fc3 = nn.Linear(layer_size, layer_size)
        self.fc4 = nn.Linear(layer_size, action_size)

    def forward(self, state):
        x = torch.relu(self.fc1(state.float()))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        return self.fc4(x)




class QLearningAgent:
    def __init__(self, state_size, action_size, lr=0.0001, start_epsilon=1, min_epsilon=0.3, decay_rate=0.0025, decay_type = "linear"):
        self.q_network = QNetwork(state_size, action_size).to(device)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=lr)
        self.start_epsilon = start_epsilon
        self.epsilon = start_epsilon
        self.min_epsilon = min_epsilon
        self.decay_rate = decay_rate
        self.decay_type = decay_type
        self.criterion = torch.nn.SmoothL1Loss()

    def update_epsilon(self, steps):
        if self.decay_type == 'linear':
            self.epsilon = max(self.min_epsilon, self.start_epsilon - steps * self.decay_rate)
        elif self.decay_type == 'exponential':
            self.epsilon = max(self.min_epsilon, self.start_epsilon * (self.decay_rate ** steps))


        print(f"EPSILON: {self.epsilon}")

    def update(self, state, action, reward, next_state):

        q_values = self.q_network(state)
        next_q_values = self.q_network(next_state)

        q_value = q_values[0][action]
        next_q_value = next_q_values.max(1)[0]
        
        target = reward + 0.99 * next_q_value

        loss = self.criterion(q_value.squeeze(),target.detach().squeeze())


        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()


    def train(self, replay_memory, num_steps, batch_size=128, epochs=5):
        states = torch.stack(replay_memory.states)
        shuffle_indices = torch.randperm(states.shape[0])

        
        states = states[shuffle_indices]
        actions = torch.stack(replay_memory.actions)[shuffle_indices]
        rewards = torch.Tensor(replay_memory.rewards)[shuffle_indices]

        next_states = torch.stack(replay_memory.next_states)[shuffle_indices]
        print(f"Average reward {torch.mean(rewards)}")


        for i in range(epochs):
            print(f"Training. Epoch {i}")
            for j in range(0, len(states), batch_size):

                self.update(
                    states[j:j+batch_size], 
                    actions[j:j+batch_size],
                    rewards[j:j+batch_size],
                    next_states[j:j+batch_size]
                    )
                
        self.update_epsilon(num_steps)

    def get_action(self, state):
        pos = utils.encode_state(state[0])
        state = [pos] + state[1:]
        state = torch.tensor(state)
        if random.random() < self.epsilon:
            return torch.tensor([random.randint(0,constants.ACTION_SIZE-1)])
        else:
            action_prob = self.q_network(state)
            return torch.argmax(torch.nn.functional.softmax(action_prob)).unsqueeze(0)
        
    def get_reward(self, state, next_state):
        state = state[0]
        next_state = next_state[0]

        prev_dist_to_goal = math.dist(state,constants.GOAL_LOC)
        cur_dist_to_goal = math.dist(next_state, constants.GOAL_LOC)
        start_dist_to_goal = math.dist(constants.SPAWN_LOCATION, constants.GOAL_LOC)
        
        if (next_state == constants.GOAL_LOC):
            return start_dist_to_goal
        elif (cur_dist_to_goal < prev_dist_to_goal and cur_dist_to_goal < start_dist_to_goal):
            #return 1 - cur_dist_to_goal / start_dist_to_goal
            #return 1
            return start_dist_to_goal - cur_dist_to_goal
        else:
            return -1

        


class MemoryStep:
    def __init__(self, state, action, reward, next_state):
        pos = utils.encode_state(state[0])
        next_pos = utils.encode_state(next_state[0])

        self.state = torch.tensor([pos] + state[1:])
        self.action = action
        self.reward = reward
        self.next_state = torch.tensor([next_pos] + next_state[1:])


class ReplayMemory:

    def __init__(self):
        self.states = []
        self.actions = []
        self.rewards = []
        self.next_states = []

    def append(self, memory_step):
        self.states.append(memory_step.state)
        self.actions.append(memory_step.action)
        self.rewards.append(memory_step.reward)
        self.next_states.append(memory_step.next_state)

    
    def clear(self):
        self.states.clear()
        self.actions.clear()
        self.rewards.clear()
        self.next_states.clear()
    



