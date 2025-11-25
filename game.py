import numpy as np
from cell_type_enum import CellType
from cell_color_enum import CellColor
from direction_enum import Direction
from slice import Slice
from cell import Cell
import random
from typing import List, TypedDict, Any
import copy
# Define the shape of your history object
class HistoryState(TypedDict):
    previousGrid: list[Cell]
    previousSlices: list[Slice]
    
    
class Game:
    def __init__(self, vertical_length, horizontal_length, movingSlices,outputSlices,constantSlices=[]):
        self.vertical_length = vertical_length
        self.horizontal_length = horizontal_length
        self.slices = movingSlices
        self.undoStack: List[HistoryState] = []
        
        # 1. Correctly create the 2D array (V+2 x H+2)
        rows = vertical_length 
        cols = horizontal_length 
        self.grid = np.empty((rows, cols), dtype=object)
        for r in range(rows):
            for c in range(cols):
                self.grid[r, c] = Cell(r, c, CellType.EMPTY) 
        self.initializeTheGrid(outputSlices,constantSlices)



    def getRandomSliceColor(self):
            SELECTABLE_COLORS = [
                        CellColor.RED,
                        CellColor.BLUE,
                        CellColor.GREEN,
                        CellColor.PURPLE,
                        CellColor.ORANGE,
                        CellColor.YELLOW
                                ]
            return random.choice(SELECTABLE_COLORS)
     
    def initializeTheGrid(self, outputSlices, constantSlices):
        for slice in self.slices:
            for cell in slice.cells:
                self.grid[cell.x, cell.y].x = cell.x
                self.grid[cell.x, cell.y].y = cell.y
                self.grid[cell.x, cell.y].cellType = cell.cellType
                self.grid[cell.x, cell.y].cellColor = cell.cellColor
                self.grid[cell.x, cell.y].slice = cell.slice
                        
        # Place constant slices
        for slice in constantSlices:
            for cell in slice.cells:
                self.grid[cell.x, cell.y].x = cell.x
                self.grid[cell.x, cell.y].y = cell.y
                self.grid[cell.x, cell.y].cellType = cell.cellType
                self.grid[cell.x, cell.y].cellColor = cell.cellColor
                self.grid[cell.x, cell.y].slice = cell.slice
            
        # Place output slices - also add 1 to coordinates for consistency
        for slice in outputSlices:
            for cell in slice.cells:
                self.grid[cell.x, cell.y].x = cell.x
                self.grid[cell.x, cell.y].y = cell.y
                self.grid[cell.x, cell.y].cellColor = cell.cellColor
                self.grid[cell.x, cell.y].cellType = cell.cellType
                self.grid[cell.x, cell.y].slice = cell.slice
    
        
    def moveSlice(self, slice, direction: Direction, movements): 
        if slice.numberToBeAbleToMoveIt is not None and slice.numberToBeAbleToMoveIt > 0:
            return
        
        if direction not in slice.directions:
            return
        
        # 1. Determine movement delta (dx, dy)
        dx, dy = 0, 0
        
        match direction:
            case Direction.TOP:
                dx = -1
                dy = 0
            case Direction.BOTTOM:
                dx = 1
                dy = 0
            case Direction.LEFT:
                dx = 0
                dy = -1
            case Direction.RIGHT:
                dx = 0
                dy = 1
        
        sliceIndex = self.slices.index(slice)
        
        for i in range(movements):
            collision = False
            current_positions = set()
            for cell in slice.cells:
                current_grid_x = cell.x  
                current_grid_y = cell.y 
                current_positions.add((current_grid_x, current_grid_y))
            
            for cell in slice.cells:
                target_inner_x = cell.x + dx
                target_inner_y = cell.y + dy
                target_grid_x = target_inner_x 
                target_grid_y = target_inner_y 
                target_cell = self.grid[target_grid_x, target_grid_y]
                
                is_same_slice = (target_grid_x, target_grid_y) in current_positions
                
                if (
                    target_cell.cellType == CellType.CONSTANT
                    or (
                        target_cell.cellType == CellType.MOVING and 
                        not is_same_slice
                    )
                    or (
                        target_cell.cellType == CellType.OUTPUT and 
                        target_cell.cellColor != cell.cellColor  
                    )
                ):
                    collision = True
                    break 
            
            if collision:
                return
            
            state = { 
                'previousGrid': copy.deepcopy(self.grid),
                'previousSlices': copy.deepcopy(self.slices)
            }
            self.undoStack.append(state)
            
            for cell in slice.cells:
                old_grid_x = cell.x 
                old_grid_y = cell.y 
                self.grid[old_grid_x, old_grid_y] = Cell(old_grid_x, old_grid_y, CellType.EMPTY)
            
            for cell in slice.cells:
                new_inner_x = cell.x + dx
                new_inner_y = cell.y + dy
                new_grid_x = new_inner_x 
                new_grid_y = new_inner_y 
                
                self.grid[new_grid_x, new_grid_y] = Cell(new_grid_x, new_grid_y, cell.cellType, cell.cellColor)
                self.grid[new_grid_x, new_grid_y].slice = slice
                
                original_index = self.slices[sliceIndex].cells.tolist().index(cell)
                self.slices[sliceIndex].cells[original_index] = Cell(new_inner_x, new_inner_y, cell.cellType, cell.cellColor) 
                self.slices[sliceIndex].cells[original_index].slice = slice
            
            current_slice = self.slices[sliceIndex]
            
            self.removeTheAbilityOfRemovingSlice(current_slice, Direction.TOP)
            if current_slice not in self.slices:
                break  
                
            self.removeTheAbilityOfRemovingSlice(current_slice, Direction.BOTTOM)
            if current_slice not in self.slices:
                break  
                
            self.removeTheAbilityOfRemovingSlice(current_slice, Direction.RIGHT)
            if current_slice not in self.slices:
                break  
                
            self.removeTheAbilityOfRemovingSlice(current_slice, Direction.LEFT)
            
            if slice in self.slices:
                sliceIndex = self.slices.index(slice)
         
             
    def removeTheAbilityOfRemovingSlice(self, slice, direction: Direction):
        dx, dy, verticalOrHorizontalLengthForComparesion = 0, 0, 0
        numberOfOutputCells = 0
        outputSlice = None
        sliceXSet = set()
        sliceYSet = set()
        outputSliceXSet = set()
        outputSliceYSet = set()
        
        match direction:
            case Direction.TOP:
                dx = -1
                dy = 0
                verticalOrHorizontalLengthForComparesion = slice.sliceHorizontalLength
            case Direction.BOTTOM:
                dx = 1
                dy = 0
                verticalOrHorizontalLengthForComparesion = slice.sliceHorizontalLength
            case Direction.LEFT:
                dx = 0
                dy = -1
                verticalOrHorizontalLengthForComparesion = slice.sliceVerticalLength
            case Direction.RIGHT:
                dx = 0
                dy = 1
                verticalOrHorizontalLengthForComparesion = slice.sliceVerticalLength
        
        # Check for collisions
        for cell in slice.cells:
            target_inner_x = cell.x + dx
            target_inner_y = cell.y + dy
            target_grid_x = target_inner_x 
            target_grid_y = target_inner_y 
            target_cell = self.grid[target_grid_x, target_grid_y]
            
            sliceXSet.add(cell.x)
            sliceYSet.add(cell.y)
            
            if (
                target_cell.cellType == CellType.OUTPUT and 
                cell.cellColor == target_cell.cellColor
            ):
                outputSlice = target_cell.slice
                numberOfOutputCells += 1
            
        if outputSlice is None:
            return    
        
        for outputCell in outputSlice.cells:
            outputSliceXSet.add(outputCell.x )  
            outputSliceYSet.add(outputCell.y )  
            
        if (
            (sliceXSet.issubset(outputSliceXSet) or sliceYSet.issubset(outputSliceYSet)) 
        ):    
            for cell in slice.cells:
                old_grid_x = cell.x 
                old_grid_y = cell.y 
                self.grid[old_grid_x, old_grid_y] = Cell(old_grid_x, old_grid_y, CellType.EMPTY)
        
            self.slices.remove(slice)
            self.decreaseTheNumberToBeAbleToMoveItForEachSliceHasIt()            
            return        
          
      
    def decreaseTheNumberToBeAbleToMoveItForEachSliceHasIt(self):
        for slice in self.slices:
            if(
               slice.numberToBeAbleToMoveIt is not None and 
               slice.numberToBeAbleToMoveIt > 0
              ):
                sliceIndex = self.slices.index(slice)
                self.slices[sliceIndex].numberToBeAbleToMoveIt -= 1
                if(slice.numberToBeAbleToMoveIt is 0):
                    newColor:CellColor = None
                    if(slice.iceSliceColor is not None):
                        newColor = slice.iceSliceColor
                    else:
                        newColor = self.getRandomSliceColor()
                        
                    for cell in slice.cells:
                        self.grid[cell.x, cell.y ].cellColor = newColor
                        original_index = self.slices[sliceIndex].cells.tolist().index(cell)
                        self.slices[sliceIndex].cells[original_index].cellColor = newColor
                                      
                        
    def undo(self):
        if len(self.undoStack) == 0:
            return
        
        last_state = self.undoStack.pop()
        self.grid = last_state['previousGrid']
        self.slices = last_state['previousSlices']
        
                    
                        