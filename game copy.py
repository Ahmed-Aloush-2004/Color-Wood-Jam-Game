import numpy as np
from cell_type_enum import CellType
from cell_color_enum import CellColor
from direction_enum import Direction
from slice import Slice
from cell import Cell

class Game:
    def __init__(self, vertical_length, horizontal_length, slices,outputCells,obstacleCells=[]):
        self.vertical_length = vertical_length
        self.horizontal_length = horizontal_length
        self.slices = slices
        
        # 1. Correctly create the 2D array (V+2 x H+2)
        rows = vertical_length + 2
        cols = horizontal_length + 2
        self.grid = np.empty((rows, cols), dtype=object)
        for r in range(rows):
            for c in range(cols):
                self.grid[r, c] = Cell(r, c, CellType.EMPTY) 
        self.fill_border_list(self.grid, CellType.CONSTANT, CellColor.BLACK)
        self.initializeTheGrid(outputCells,obstacleCells)


    def initializeTheGrid(self,outputCells,obstacleCells = []):
        for slice in self.slices:
            for cell in slice.cells:
                self.grid[cell.x + 1, cell.y + 1].cellType = cell.cellType
                self.grid[cell.x + 1, cell.y + 1].cellColor = cell.cellColor
                self.grid[cell.x + 1, cell.y + 1].slice = cell.slice
                        
        # --- NEW: Place obstacle cells ---
        for cell in obstacleCells:
            grid_cell = self.grid[cell.x + 1, cell.y + 1]
            grid_cell.cellType = cell.cellType
            grid_cell.cellColor = cell.cellColor
            grid_cell.slice = None # Obstacles don't belong to a slice
        
                
        for cell in outputCells:
            self.grid[cell.x , cell.y ].x = cell.x
            self.grid[cell.x , cell.y ].y = cell.y
            self.grid[cell.x , cell.y ].cellColor = cell.cellColor
            self.grid[cell.x , cell.y ].cellType = cell.cellType
            self.grid[cell.x , cell.y ].slice = cell.slice
        
    def fill_border_list(self,arr_2d, cellType, cellColor):

        height = len(arr_2d)
        width = len(arr_2d[0])

        # print('this is the height : ',height)
        # print('this is the width : ',width)
        # print('this is the range(1,width - 1) : ',range(1,width - 1))
        # print('this is the range(1, height - 1) : ',range(1, height - 1))

        for j in range(0,width):
            # print('this is the j : ',j)
            arr_2d[0][j].cellType = cellType       # Top row
            arr_2d[0][j].cellColor = cellColor       # Top row
            arr_2d[height - 1][j].cellType = cellType # Bottom row
            arr_2d[height - 1][j].cellColor = cellColor # Bottom row

        for i in range(0, height):
            # print('this is the i : ',i)
            arr_2d[i][0].cellType = cellType       # Left column
            arr_2d[i][0].cellColor = cellColor       # Left column
            arr_2d[i][width - 1].cellType = cellType  # Right column
            arr_2d[i][width - 1].cellColor = cellColor  # Right column

        return arr_2d

    def printTheGrid(self):
        print('this is for printing the slices ')
        print('this is the Grid Length : ',len(self.grid))
        for slice in self.slices:
            for cell in slice.cells:
               print('this is the cell:','cell.x',cell.x,' ,cell.y',cell.y,' ,cell.cellColor',cell.cellColor,' ,cell.cellType',cell.cellType)


        print('this is the grid for loop : ')
        for row in self.grid:
                for cell in row:
                    print(cell.x,' ',cell.y,' ',cell.cellColor,' ',cell.cellType)
        


   
    def moveSlice(self, slice, direction: Direction, movments): 
        
        if(slice.numberToBeAbleToMoveIt > 0 ):
            return
       
        # 1. Determine movement delta (dx, dy) and cell iteration order
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

        for i in range(movments):
            # A. COLLISION CHECK (Check all cells before moving any)
            collision = False
            current_positions = set()
            for cell in slice.cells:
                current_grid_x = cell.x + 1 
                current_grid_y = cell.y + 1
                current_positions.add((current_grid_x, current_grid_y))
            
            # Check for collisions
            for cell in slice.cells:
                target_inner_x = cell.x + dx
                target_inner_y = cell.y + dy
                target_grid_x = target_inner_x + 1 
                target_grid_y = target_inner_y + 1
                target_cell = self.grid[target_grid_x, target_grid_y]
                
                # Check if the target position is part of the same slice
                is_same_slice = (target_grid_x, target_grid_y) in current_positions
                
                # Collision Condition: 
                # 1. Target is a CONSTANT cell (e.g., border or fixed obstacle)
                # 2. Target is a MOVING cell of a DIFFERENT slice
                if (
                        target_cell.cellType == CellType.CONSTANT
                        or (
                            target_cell.cellType == CellType.MOVING and 
                            not is_same_slice
                           )
                    ):
                    print('this is condition :  ',(target_cell.slice != cell.slice))
                    print('this is the type of the target_cell : ',target_cell.cellType)
                    print('this is the slice of the target_cell : ',target_cell.x)
                    print('this is the slice of the target_cell : ',target_cell.y)
                    print('this is the slice of the target_cell : ',target_cell.cellColor)
                    print('this is the slice of the target_cell : ',target_cell.slice)
                    collision = True
                    break 
            
            if collision:
                raise Exception(f'something for moving went wrong! Collision detected when moving {direction}.')
            
            # B. EXECUTE MOVEMENT (No collision)
            
            # 1. Clear old cells
            # Iterate using the calculated order for consistency (though not strictly necessary 
            # for clearing if we update the slice coordinates at the end).
            for cell in slice.cells:
                old_grid_x = cell.x + 1
                old_grid_y = cell.y + 1
                
                # Clear the old position by making it an EMPTY cell.
                # Crucially, the EMPTY cell must also have its correct absolute grid coordinates.
                self.grid[old_grid_x, old_grid_y] = Cell(old_grid_x, old_grid_y, CellType.EMPTY)
            
            # 2. Update Grid and Slice coordinates
            for cell in slice.cells: # Iterate over the original slice cells
                
                # Calculate new inner coordinates
                new_inner_x = cell.x + dx
                new_inner_y = cell.y + dy
                
                # Calculate new main grid coordinates (+1 offset)
                new_grid_x = new_inner_x + 1
                new_grid_y = new_inner_y + 1
                
                # Update the cell in the main grid
                self.grid[new_grid_x, new_grid_y] = Cell(new_grid_x, new_grid_y, cell.cellType, cell.cellColor)
                self.grid[new_grid_x, new_grid_y].slice = slice
                
                # Update the cell's coordinates *within the slice* to reflect the new inner position
                # Get the actual index of the cell in the slice's array
                original_index = self.slices[sliceIndex].cells.tolist().index(cell)
                self.slices[sliceIndex].cells[original_index] = Cell(new_inner_x, new_inner_y, cell.cellType, cell.cellColor) 
                self.slices[sliceIndex].cells[original_index].slice = slice
            
            self.removeTheAbilityOfRemovingSlice(self.slices[sliceIndex],direction)
                
                
    def removeTheAbilityOfRemovingSlice(self, slice,direction: Direction):
         
         # 1. Determine movement delta (dx, dy) and cell iteration order
        dx, dy,verticalOrHorizontalLengthForComparesion = 0, 0, 0
        
        
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
                   
        numberOfOutputCells = 0

            # Check for collisions
        for cell in slice.cells:
                target_inner_x = cell.x + dx
                target_inner_y = cell.y + dy
                target_grid_x = target_inner_x + 1 
                target_grid_y = target_inner_y + 1
                target_cell = self.grid[target_grid_x, target_grid_y]
                
                # Check if the target position is part of the same slice
                
                # Collision Condition: 
                # 1. Target is a CONSTANT cell (e.g., border or fixed obstacle)
                # 2. Target is a MOVING cell of a DIFFERENT slice
                if (
                    target_cell.cellType == CellType.OUTPUT and 
                    cell.cellColor == target_cell.cellColor
                    ):
                    numberOfOutputCells+=1
       
        print('this is the numberOfOutputCells : ',numberOfOutputCells)
        print('this is the widthOrHighForComparesion : ',verticalOrHorizontalLengthForComparesion)
        print('this is the condition : ',numberOfOutputCells >= verticalOrHorizontalLengthForComparesion)
        if(numberOfOutputCells >= verticalOrHorizontalLengthForComparesion):
            
            for cell in slice.cells:
                old_grid_x = cell.x + 1
                old_grid_y = cell.y + 1
                # Clear the old position by making it an EMPTY cell.
                # Crucially, the EMPTY cell must also have its correct absolute grid coordinates.
                self.grid[old_grid_x, old_grid_y] = Cell(old_grid_x, old_grid_y, CellType.EMPTY)
                    
            self.slices.remove(slice)
                
      
    def decreaseTheNumberToBeAbleToMoveItForEachSliceHasIt(self):
        for slice in self.slices:
            if(slice.numberToBeAbleToMoveIt > 0):
                sliceIndex = self.slices.index(slice)
                self.slices[sliceIndex].numberToBeAbleToMoveIt -= 1
                    