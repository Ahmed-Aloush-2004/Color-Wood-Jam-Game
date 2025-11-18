from cell_type_enum import CellType
from cell_color_enum import CellColor
from typing import Optional  # for clear type hinting


class Cell:
    def __init__(self, x: int, y: int, cellType: CellType, cellColor: Optional[CellColor] = None):
        self.x = x
        self.y = y
        self.cellType = cellType
        self.cellColor = cellColor
        self.slice = None  

