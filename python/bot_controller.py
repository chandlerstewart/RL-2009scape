import json
import time
import random
import constants
from QLearning import MemoryStep



def json_to_bot(json_data):
    bots = []

    for val in json_data:
        bots.append(Bot(**val))


    return bots





def get_action_data(data, replay_memory, agent):
    bots = json_to_bot(data)
    
    for bot in bots:
        state = bot.get_relative_state()
        action = agent.get_action(state)
        bot.take_action(action)
        next_state = bot.get_relative_state()
        reward = agent.get_reward(state, next_state)
        #print(reward)

        memory_step = MemoryStep(state,action,reward,next_state)
        replay_memory.append(memory_step)
        


    json_data = json.dumps([b.__dict__ for b in bots])
    #time.sleep(0.5) #Do not remove this statement

    
    return json_data



    


class Bot:

    def __init__(self, name, xLoc, yLoc):
        self.name = name
        self.xLoc = xLoc
        self.yLoc = yLoc

    def move_north(self):
        self.yLoc += 1

    def move_south(self):
        self.yLoc -= 1

    def move_west(self):
        self.xLoc -= 1

    def move_east(self):
        self.xLoc += 1

    def get_absolute_state(self):
        return (self.xLoc,self.yLoc)
    
    def get_relative_state(self):
        return (self.get_relative_x(),self.get_relative_y())
    
    def take_action(self, action):
        if action == 0:
            self.move_north()
        if action == 1:
            self.move_south()
        if action == 2:
            self.move_east()
        if action == 3:
            self.move_west()


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
        return self.xLoc - constants.BOUNDSX[0]
    
    def get_relative_y(self):
        return self.yLoc - constants.BOUNDSY[0]


