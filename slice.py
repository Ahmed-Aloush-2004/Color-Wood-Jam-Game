
from cell import Cell
import numpy as np
from direction_enum import Direction 
class Slice:
    def __init__(self,sliceVerticalLength,sliceHorizontalLength,cells,numberToBeAbleToMoveIt = 0,
                 directions:Direction = [Direction.TOP,Direction.BOTTOM,Direction.LEFT,Direction.RIGHT],iceSliceColor = None):
        self.cells = np.array(cells,dtype=Cell)
        self.sliceVerticalLength = sliceVerticalLength
        self.sliceHorizontalLength = sliceHorizontalLength
        self.numberToBeAbleToMoveIt = numberToBeAbleToMoveIt
        self.directions = directions
        self.iceSliceColor = iceSliceColor
        for cell in self.cells.flatten():
              cell.slice = self

      