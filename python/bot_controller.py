import json
import time
import random
import constants
from QLearning import MemoryStep
import utils
import numpy as np



def json_to_bot(json_data):
    bots = []

    for val in json_data:
        print(val)
        bots.append(Bot(val))


    return bots





def get_action_data(data, replay_memory, agent):
    bots = json_to_bot(data)

    num_of_bots = len(bots)
    
    for i in range(num_of_bots):
        bot = bots[i]
        state = bot.get_absolute_state()
        action = agent.get_action(state)
        bot.take_action(action)
        next_state = bot.get_absolute_state()
        #reward = agent.get_reward(state, next_state)
        

        if len(replay_memory.rewards) >= num_of_bots:
            reward = bot.info["reward"]
            if reward > 0:
                print(f"BOT: {i}")
            replay_memory.rewards[len(replay_memory.rewards)-num_of_bots-1 +i] = reward

        #print(replay_memory.rewards[len(replay_memory.rewards)-num_of_bots:])
        memory_step = MemoryStep(state,action,0,next_state)
        replay_memory.append(memory_step)
        

    
    json_data = json.dumps([b.info for b in bots])

    
    return json_data



    


class Bot:

    def __init__(self, info):
        self.info = info

    def move_north(self):
        self.info["yLoc"] +=  1

    def move_south(self):
        self.info["yLoc"] -= 1

    def move_west(self):
        self.info["xLoc"] -= 1

    def move_east(self):
        self.info["xLoc"] += 1

    def get_absolute_state(self):
        state = [(self.info["xLoc"],self.info["yLoc"])]
        state += self.get_state_bools()
        return state
    
    def get_relative_state(self):
        state = [(self.get_relative_x(),self.get_relative_y())]
        state += self.get_state_bools()
        return state
    
    def take_action(self, action):
        if action in [0,1,2,3]:
            self.info["interact"] = "none"
        if action == 0:
            self.move_north()
        if action == 1:
            self.move_south()
        if action == 2:
            self.move_east()
        if action == 3:
            self.move_west()
        if action == 4:
            self.info["interact"] = "north"
        if action == 5:
            self.info["interact"] = "south"
        if action == 6:
            self.info["interact"] = "east" 
        if action == 7:
            self.info["interact"] = "west"

    def get_state_bools(self):
        bools = [
                 self.info["canMoveNorth"],self.info["canMoveSouth"], self.info["canMoveEast"], self.info["canMoveWest"],
                 self.info["northNode"], self.info["southNode"], self.info["eastNode"], self.info["westNode"]
                 ]
        

        bools = np.asarray(bools).astype(int)

        return bools.tolist()


    def random_move(self):
        choice = random.randint(0,3)

        if choice == 0:
            self.move_north()
        if choice == 1:
            self.move_south()
        if choice == 2:
            self.move_east()
        if choice == 3:
            self.move_west()

    def get_relative_x(self):
        return self.info["xLoc"] - constants.BOUNDSX[0]
    
    def get_relative_y(self):
        return self.info["yLoc"] - constants.BOUNDSY[0]


