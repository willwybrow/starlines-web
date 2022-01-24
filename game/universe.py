from enum import Enum

CLUSTER_SIZE = 5
MASS_PER_NEW_CLUSTER = 20

class Dimension(Enum):
    UP = 1,
    DOWN = 2,
    LEFT = 3,
    RIGHT = 4