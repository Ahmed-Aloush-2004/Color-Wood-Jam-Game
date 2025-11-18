from enum import Enum


class CellType(Enum):
    EMPTY = 0
    MOVING = 1
    CONSTANT = 2
    OUTPUT = 3
