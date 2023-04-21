HOST = 'localhost'
PORT = 5000

NUM_BOTS = 200
NUM_EPISDOES = 1000


EPISODE_NUM_STEPS_MIN = 100
EPISODE_NUM_STEPS_MAX = 400

BOUNDSX = (3134, 3267)
BOUNDSY = (3142, 3294)

X_SIZE = BOUNDSX[1] - BOUNDSX[0]
Y_SIZE = (BOUNDSY[1] - BOUNDSY[0])
#STATE_SIZE =  X_SIZE * Y_SIZE
STATE_SIZE = 9 #int state + bool representing if can in each direction + bool representing if node in each direction
ACTION_SIZE = 8 #move in each direction, interact in each direction

SPAWN_LOCATION = (2728, 3479)
RELATIVE_SPAWN_LOCATION = (SPAWN_LOCATION[0] - BOUNDSX[0], SPAWN_LOCATION[1] - BOUNDSY[0])

GOAL_LOC = (2743, 3444)
RELATIVE_GOAL_LOC = (GOAL_LOC[0] - BOUNDSX[0], GOAL_LOC[1] - BOUNDSY[0])

