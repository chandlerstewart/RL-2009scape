import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.distributions import Categorical
import utils
import constants
import math

class ActorCritic(nn.Module):
    def __init__(self):
        super(ActorCritic, self).__init__()
        self.fc1 = nn.Linear(constants.STATE_SIZE, 128)
        self.fc2 = nn.Linear(128, 2)
        self.fc3 = nn.Linear(128, 1)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        policy = F.softmax(self.fc2(x), dim=0)
        value = self.fc3(x)
        return policy, value

class PPO:
    def __init__(self):
        self.policy = ActorCritic()
        self.optimizer = optim.Adam(self.policy.parameters(), lr=0.01)
        self.gamma = 0.99
        self.eps_clip = 0.2

    def get_action(self, state):
        state = utils.encode_state(state)
        state = state.float().unsqueeze(0)
        probs, _ = self.policy(state)
        m = Categorical(probs)
        action = m.sample()
        return action.item(), m.log_prob(action)
    



    def update(self, rewards, log_probs, states):
        returns = []
        discounted_reward = 0
        for reward in reversed(rewards):
            discounted_reward = reward + (self.gamma * discounted_reward)
            returns.insert(0, discounted_reward)

        returns = torch.tensor(returns)
        returns = (returns - returns.mean()) / (returns.std() + 1e-5)

        for _ in range(10):
            for i in range(len(rewards)):
                state = states[i].float().unsqueeze(0)
                old_probs, old_value = self.policy(state)
                m_old = Categorical(old_probs)

                action = torch.tensor([log_probs[i][0]]).long()
                prob_new, value_new = self.policy(state)
                m_new = Categorical(prob_new)

                ratio = (m_new.probs / m_old.probs)[action]
                surr1 = ratio * log_probs[i][1]
                surr2 = torch.clamp(ratio, 1 - self.eps_clip,
                                    1 + self.eps_clip) * log_probs[i][1]
                entropy_bonus = 0.01 * m_new.entropy()

                loss_actor_critic = -torch.min(surr1, surr2) + \
                    F.smooth_l1_loss(old_value,
                                     returns[i].unsqueeze(0))
                loss_entropy_bonus = -entropy_bonus

                total_loss = loss_actor_critic + loss_entropy_bonus

                self.optimizer.zero_grad()
                total_loss.backward()
                self.optimizer.step()


    def get_reward(self, state, next_state):

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


class MemoryStep:
    def __init__(self, state, action, reward, next_state):
        self.state = state
        self.action = action
        self.reward = reward
        self.next_state = next_state


class Data:

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
    
