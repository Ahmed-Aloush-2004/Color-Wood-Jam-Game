
from cell import Cell
import numpy as np

class Slice:
    def __init__(self,sliceVerticalLength,sliceHorizontalLength,cells,numberToBeAbleToMoveIt = 0 ):
        self.cells = np.array(cells,dtype=Cell)
        self.sliceVerticalLength = sliceVerticalLength
        self.sliceHorizontalLength = sliceHorizontalLength
        self.numberToBeAbleToMoveIt = numberToBeAbleToMoveIt
        for cell in self.cells.flatten():
              cell.slice = self

        # self.checkSliceCellsIfTheyAreConsistent()
    
    # def checkSliceCellsIfTheyAreConsistent(self):

    #     dims = self.cells.ndim
    #     # print(f"Slice detected {dims}D array with shape {self.cells.shape}")

    #     if dims == 1:
    #         vertical_length = 1
    #         horizontal_length = len(self.cells)
    #     elif dims >= 2:
    #         vertical_length, horizontal_length = self.cells.shape[:2]
    #     else:
    #         raise Exception("Invalid cell array dimension!")
        
    #     # print('this is something : ',self.cells.shape[:2])
    #     # print(f"→ Slice has {vertical_length} vertical and {horizontal_length} horizontal cells")
        
    #     # Compare with provided lengths
    #     if vertical_length != self.sliceVerticalLength:
    #         raise Exception("The vertical length of the slice does not match the one provided!")
    #     if horizontal_length != self.sliceHorizontalLength:
    #         raise Exception("The horizontal length of the slice does not match the one provided!")

    #     # Optional: Check cell consistency (color/type)
    #     flat_cells = self.cells.flatten()
    #     first_cell = flat_cells[0]
    #     for cell in flat_cells[1:]:
    #         if cell.cellColor != first_cell.cellColor or cell.cellType != first_cell.cellType:
    #             raise Exception("All cells in a slice must have the same color and type!")

    #     # print("✅ Slice consistency check passed.")



