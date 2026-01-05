
from cell import Cell
import numpy as np
from direction_enum import Direction 
import uuid

class Slice:
    
    my_iterator = iter(range(10000))
    
    def __init__(self,sliceVerticalLength,sliceHorizontalLength,cells,numberToBeAbleToMoveIt = 0,
                 directions:Direction = [Direction.TOP,Direction.BOTTOM,Direction.LEFT,Direction.RIGHT],iceSliceColor = None):
        self.cells = list(cells)
        self.sliceVerticalLength = sliceVerticalLength
        self.sliceHorizontalLength = sliceHorizontalLength
        self.numberToBeAbleToMoveIt = numberToBeAbleToMoveIt
        self.directions = directions
        self.id = str(next(self.my_iterator))
        self.iceSliceColor = iceSliceColor
        for cell in self.cells:
              cell.slice = self

      