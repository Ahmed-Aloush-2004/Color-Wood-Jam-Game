# import tkinter as tk
# from tkinter import messagebox
# from game import Game
# from slice import Slice
# from cell import Cell
# from cell_color_enum import CellColor
# from cell_type_enum import CellType
# from direction_enum import Direction
# import numpy as np

# class GameGUI:
#     def __init__(self, master, game):
#         self.master = master
#         self.game = game
#         self.cell_size = 60  # Size of each cell in pixels
#         self.selected_slice = None
#         self.canvas_items = {}  # To store canvas items for each cell
        
#         # Create the main frame
#         self.main_frame = tk.Frame(master)
#         self.main_frame.pack(fill=tk.BOTH, expand=True)
        
#         # Create the canvas for the game grid
#         self.canvas = tk.Canvas(
#             self.main_frame, 
#             width=(game.horizontal_length + 2) * self.cell_size,
#             height=(game.vertical_length + 2) * self.cell_size,
#             bg="white"
#         )
#         self.canvas.pack(side=tk.LEFT, padx=10, pady=10)
        
#         # Create the control panel
#         self.control_panel = tk.Frame(self.main_frame)
#         self.control_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
#         # Add direction buttons
#         tk.Label(self.control_panel, text="Move Selected Slice:", font=("Arial", 12, "bold")).pack(pady=5)
        
#         button_frame = tk.Frame(self.control_panel)
#         button_frame.pack(pady=10)
        
#         # Top button
#         tk.Button(button_frame, text="↑", command=lambda: self.move_slice(Direction.TOP), 
#                  width=5, height=2).grid(row=0, column=1, padx=2, pady=2)
        
#         # Middle buttons
#         tk.Button(button_frame, text="←", command=lambda: self.move_slice(Direction.LEFT), 
#                  width=5, height=2).grid(row=1, column=0, padx=2, pady=2)
#         tk.Button(button_frame, text="→", command=lambda: self.move_slice(Direction.RIGHT), 
#                  width=5, height=2).grid(row=1, column=2, padx=2, pady=2)
        
#         # Bottom button
#         tk.Button(button_frame, text="↓", command=lambda: self.move_slice(Direction.BOTTOM), 
#                  width=5, height=2).grid(row=2, column=1, padx=2, pady=2)
        
#         # Add move count input
#         tk.Label(self.control_panel, text="Move Count:").pack(pady=5)
#         self.move_count = tk.IntVar(value=1)
#         tk.Spinbox(self.control_panel, from_=1, to=10, textvariable=self.move_count, 
#                   width=5).pack(pady=5)
        
#         # Add reset button
#         tk.Button(self.control_panel, text="Reset Game", command=self.reset_game, 
#                  width=15).pack(pady=20)
        
#         # Add slice selection info
#         self.slice_info = tk.Label(self.control_panel, text="Click on a colored slice to select it", 
#                                   wraplength=150, justify=tk.LEFT)
#         self.slice_info.pack(pady=10)
        
#         # Draw the initial grid
#         self.draw_grid()
        
#         # Bind click events
#         self.canvas.bind("<Button-1>", self.on_canvas_click)
        
#         # Check for win condition
#         self.check_win_condition()
    
#     def draw_grid(self):
#         # Clear the canvas
#         self.canvas.delete("all")
#         self.canvas_items = {}
        
#         # Draw grid lines
#         for i in range(self.game.vertical_length + 3):
#             y = i * self.cell_size
#             self.canvas.create_line(0, y, (self.game.horizontal_length + 2) * self.cell_size, y, fill="gray")
        
#         for j in range(self.game.horizontal_length + 3):
#             x = j * self.cell_size
#             self.canvas.create_line(x, 0, x, (self.game.vertical_length + 2) * self.cell_size, fill="gray")
        
#         # Draw cells
#         for i in range(self.game.vertical_length + 2):
#             for j in range(self.game.horizontal_length + 2):
#                 cell = self.game.grid[i, j]
#                 x1 = j * self.cell_size
#                 y1 = i * self.cell_size
#                 x2 = x1 + self.cell_size
#                 y2 = y1 + self.cell_size
                
#                 # Determine cell color
#                 fill_color = "white"
#                 outline_color = "gray"
#                 outline_width = 1

#                 if cell.cellType == CellType.CONSTANT:
#                     fill_color = "black"
#                 elif cell.cellType == CellType.MOVING:
#                     fill_color = cell.cellColor.value
#                     # Highlight if part of the selected slice
#                     if self.selected_slice and cell.slice == self.selected_slice:
#                         outline_color = "yellow"
#                         outline_width = 3
#                 elif cell.cellType == CellType.OUTPUT:
#                     fill_color = cell.cellColor.value
#                     outline_color = "black"
#                     outline_width = 2
                
#                 # Create the cell rectangle
#                 rect = self.canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, 
#                                                    fill=fill_color, outline=outline_color, width=outline_width)
#                 self.canvas_items[(i, j)] = rect
    
#     def on_canvas_click(self, event):
#         # Calculate which cell was clicked
#         j = event.x // self.cell_size
#         i = event.y // self.cell_size
        
#         # Check if the click is within the grid
#         if 0 <= i < self.game.vertical_length + 2 and 0 <= j < self.game.horizontal_length + 2:
#             cell = self.game.grid[i, j]
            
#             # Check if the cell is part of a movable slice
#             if cell.cellType == CellType.MOVING and cell.slice:
#                 self.selected_slice = cell.slice
#                 self.slice_info.config(text=f"Selected slice:\n{len(cell.slice.cells)} cells\nColor: {cell.cellColor.value}")
#                 self.draw_grid()  # Redraw to highlight the selected slice
#             else:
#                 # Deselect if clicking on empty space or a non-movable cell
#                 self.selected_slice = None
#                 self.slice_info.config(text="Click on a colored slice to select it")
#                 self.draw_grid()

#     def move_slice(self, direction):
#         if not self.selected_slice:
#             messagebox.showinfo("No Selection", "Please select a slice first by clicking on it.")
#             return
        
#         try:
#             # Move the slice
#             self.game.moveSlice(self.selected_slice, direction, self.move_count.get())
            
#             # If the slice was removed (win condition), deselect it
#             if self.selected_slice not in self.game.slices:
#                 self.selected_slice = None
#                 self.slice_info.config(text="Slice removed! Keep going!")

#             # Redraw the grid
#             self.draw_grid()
            
#             # Check win condition
#             self.check_win_condition()
            
#         except Exception as e:
#             messagebox.showerror("Invalid Move", str(e))
    
#     def check_win_condition(self):
#         # Check if all slices have been removed (win condition)
#         if len(self.game.slices) == 0:
#             messagebox.showinfo("Congratulations!", "You've won the game!")
#             return True
#         return False
    
#     def reset_game(self):
#         # Recreate the game with the same setup as in the index file
#         c1 = Cell(1, 0, CellType.MOVING, CellColor.RED)
#         c2 = Cell(1, 1, CellType.MOVING, CellColor.RED)
#         c3 = Cell(1, 2, CellType.MOVING, CellColor.RED)
#         cc1 = Cell(2, 0, CellType.MOVING, CellColor.RED)
#         cc2 = Cell(2, 1, CellType.MOVING, CellColor.RED)
#         cc3 = Cell(2, 2, CellType.MOVING, CellColor.RED)
#         c4 = Cell(3, 1, CellType.MOVING, CellColor.RED)
        
#         c7 = Cell(1, 5, CellType.OUTPUT, CellColor.RED)
#         c8 = Cell(2, 5, CellType.OUTPUT, CellColor.RED)
#         c9 = Cell(3, 5, CellType.OUTPUT, CellColor.RED)
#         c10 = Cell(4, 5, CellType.OUTPUT, CellColor.RED)
        
#         s1 = Slice(3, 3, [c1, c2, c3, cc1, cc2, cc3, c4])
        
#         self.game = Game(4, 4, [s1], [c7, c8, c9, c10])
#         self.selected_slice = None
#         self.slice_info.config(text="Click on a colored slice to select it")
#         self.draw_grid()

# def main():
#     # Create the game with the same setup as in the index file
#     c1 = Cell(1, 0, CellType.MOVING, CellColor.RED)
#     c2 = Cell(1, 1, CellType.MOVING, CellColor.RED)
#     c3 = Cell(1, 2, CellType.MOVING, CellColor.RED)
#     cc1 = Cell(2, 0, CellType.MOVING, CellColor.RED)
#     cc2 = Cell(2, 1, CellType.MOVING, CellColor.RED)
#     cc3 = Cell(2, 2, CellType.MOVING, CellColor.RED)
#     c4 = Cell(3, 1, CellType.MOVING, CellColor.RED)
    
#     c7 = Cell(1, 5, CellType.OUTPUT, CellColor.RED)
#     c8 = Cell(2, 5, CellType.OUTPUT, CellColor.RED)
#     c9 = Cell(3, 5, CellType.OUTPUT, CellColor.RED)
#     c10 = Cell(4, 5, CellType.OUTPUT, CellColor.RED)
    
#     s1 = Slice(3, 3, [c1, c2, c3, cc1, cc2, cc3, c4])
    
#     myGame = Game(4, 4, [s1], [c7, c8, c9, c10])
    
#     # Create the GUI
#     root = tk.Tk()
#     root.title("Slice Puzzle Game")
#     app = GameGUI(root, myGame)
#     root.mainloop()

# if __name__ == "__main__":
#     main()


import tkinter as tk
from tkinter import messagebox
import json
import numpy as np

# Import your game logic files
from game import Game
from slice import Slice
from cell import Cell
from cell_color_enum import CellColor
from cell_type_enum import CellType
from direction_enum import Direction

def load_level_from_json( filepath = "level-copy.json" ):
    """
    Loads a game level from a JSON file and returns a Game object.
    """
    try:
        with open(filepath, 'r') as f:
            level_data = json.load(f)
    except FileNotFoundError:
        messagebox.showerror("Error", f"Level file not found at {filepath}")
        return None

    all_slices = []
    all_output_cells = []
    all_obstacle_cells = []

    # 1. Create Slices from JSON data
    for slice_data in level_data.get("slices", []):
        color = CellColor[slice_data["color"].upper()]
        cells = []
        for cell_data in slice_data["cells"]:
            cells.append(Cell(cell_data["x"], cell_data["y"], CellType.MOVING, color))
        
        # Calculate the bounding box for the slice
        min_x = min(c.x for c in cells)
        max_x = max(c.x for c in cells)
        min_y = min(c.y for c in cells)
        max_y = max(c.y for c in cells)
        
        slice_vertical_length = max_x - min_x + 1
        slice_horizontal_length = max_y - min_y + 1
        
        all_slices.append(Slice(slice_vertical_length, slice_horizontal_length, cells))

    # 2. Create Obstacles from JSON data
    for obs_data in level_data.get("obstacles", []):
        all_obstacle_cells.append(
            Cell(obs_data["x"], obs_data["y"], CellType.CONSTANT, CellColor.BLACK)
        )

    # 3. Create Output Cells from JSON data
    for out_data in level_data.get("outputCells", []):
        color = CellColor[out_data["color"].upper()]
        all_output_cells.append(
            Cell(out_data["x"], out_data["y"], CellType.OUTPUT, color)
        )
    
    # 4. Create and return the Game object
    return Game(
        level_data["gridHeight"],
        level_data["gridWidth"],
        all_slices,
        all_output_cells,
        all_obstacle_cells # Pass obstacles to the Game constructor
    )

# --- The GameGUI class remains exactly the same as before ---
class GameGUI:
    def __init__(self, master, game):
        self.master = master
        self.game = game
        self.cell_size = 60
        self.selected_slice = None
        self.canvas_items = {}
        
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(
            self.main_frame, 
            width=(game.horizontal_length + 2) * self.cell_size,
            height=(game.vertical_length + 2) * self.cell_size,
            bg="white"
        )
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.control_panel = tk.Frame(self.main_frame)
        self.control_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        tk.Label(self.control_panel, text="Move Selected Slice:", font=("Arial", 12, "bold")).pack(pady=5)
        
        button_frame = tk.Frame(self.control_panel)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="↑", command=lambda: self.move_slice(Direction.TOP), 
                 width=5, height=2).grid(row=0, column=1, padx=2, pady=2)
        tk.Button(button_frame, text="←", command=lambda: self.move_slice(Direction.LEFT), 
                 width=5, height=2).grid(row=1, column=0, padx=2, pady=2)
        tk.Button(button_frame, text="→", command=lambda: self.move_slice(Direction.RIGHT), 
                 width=5, height=2).grid(row=1, column=2, padx=2, pady=2)
        tk.Button(button_frame, text="↓", command=lambda: self.move_slice(Direction.BOTTOM), 
                 width=5, height=2).grid(row=2, column=1, padx=2, pady=2)
        
        tk.Label(self.control_panel, text="Move Count:").pack(pady=5)
        self.move_count = tk.IntVar(value=1)
        tk.Spinbox(self.control_panel, from_=1, to=10, textvariable=self.move_count, 
                  width=5).pack(pady=5)
        
        tk.Button(self.control_panel, text="Reset Game", command=self.reset_game, 
                 width=15).pack(pady=20)
        
        self.slice_info = tk.Label(self.control_panel, text="Click on a colored slice to select it", 
                                  wraplength=150, justify=tk.LEFT)
        self.slice_info.pack(pady=10)
        
        self.draw_grid()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.check_win_condition()
    
    def draw_grid(self):
        self.canvas.delete("all")
        self.canvas_items = {}
        
        for i in range(self.game.vertical_length + 3):
            y = i * self.cell_size
            self.canvas.create_line(0, y, (self.game.horizontal_length + 2) * self.cell_size, y, fill="gray")
        
        for j in range(self.game.horizontal_length + 3):
            x = j * self.cell_size
            self.canvas.create_line(x, 0, x, (self.game.vertical_length + 2) * self.cell_size, fill="gray")
        
        for i in range(self.game.vertical_length + 2):
            for j in range(self.game.horizontal_length + 2):
                cell = self.game.grid[i, j]
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                fill_color = "white"
                outline_color = "gray"
                outline_width = 1

                if cell.cellType == CellType.CONSTANT:
                    fill_color = "black"
                elif cell.cellType == CellType.MOVING:
                    fill_color = cell.cellColor.value
                    if self.selected_slice and cell.slice == self.selected_slice:
                        outline_color = "yellow"
                        outline_width = 3
                elif cell.cellType == CellType.OUTPUT:
                    fill_color = cell.cellColor.value
                    outline_color = "black"
                    outline_width = 2
                
                rect = self.canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, 
                                                   fill=fill_color, outline=outline_color, width=outline_width)
                self.canvas_items[(i, j)] = rect
    
    def on_canvas_click(self, event):
        j = event.x // self.cell_size
        i = event.y // self.cell_size
        
        if 0 <= i < self.game.vertical_length + 2 and 0 <= j < self.game.horizontal_length + 2:
            cell = self.game.grid[i, j]
            
            if cell.cellType == CellType.MOVING and cell.slice:
                self.selected_slice = cell.slice
                self.slice_info.config(text=f"Selected slice:\n{len(cell.slice.cells)} cells\nColor: {cell.cellColor.value}")
                self.draw_grid()
            else:
                self.selected_slice = None
                self.slice_info.config(text="Click on a colored slice to select it")
                self.draw_grid()

    def move_slice(self, direction):
        if not self.selected_slice:
            messagebox.showinfo("No Selection", "Please select a slice first by clicking on it.")
            return
        
        try:
            self.game.moveSlice(self.selected_slice, direction, self.move_count.get())
            
            if self.selected_slice not in self.game.slices:
                self.selected_slice = None
                self.slice_info.config(text="Slice removed! Keep going!")

            self.draw_grid()
            self.check_win_condition()
            
        except Exception as e:
            messagebox.showerror("Invalid Move", str(e))
    
    def check_win_condition(self):
        if len(self.game.slices) == 0:
            messagebox.showinfo("Congratulations!", "You've won the game!")
            return True
        return False
    
    def reset_game(self):
        """
        Resets the game by reloading it from the JSON file.
        """
        self.game = load_level_from_json()
        if self.game: # Only reset if loading was successful
            self.selected_slice = None
            self.slice_info.config(text="Click on a colored slice to select it")
            self.draw_grid()

def main():
    # Create the game by loading from the JSON file
    myGame = load_level_from_json()
    if not myGame:
        return # Exit if the level file could not be loaded

    root = tk.Tk()
    root.title("Slice Puzzle Game - JSON Level")
    app = GameGUI(root, myGame)
    root.mainloop()

if __name__ == "__main__":
    main()


# import tkinter as tk
# from tkinter import messagebox
# from game import Game
# from slice import Slice
# from cell import Cell
# from cell_color_enum import CellColor
# from cell_type_enum import CellType
# from direction_enum import Direction
# import numpy as np

# def create_hard_level():
#     """
#     Creates and returns a Game object with a larger, more complex puzzle.
#     This function is used by both the main game setup and the reset function.
#     """
#     # --- RED SLICE (2x2 Block) ---
#     red_c1 = Cell(1, 1, CellType.MOVING, CellColor.RED)
#     red_c2 = Cell(1, 2, CellType.MOVING, CellColor.RED)
#     red_c3 = Cell(2, 1, CellType.MOVING, CellColor.RED)
#     red_c4 = Cell(2, 2, CellType.MOVING, CellColor.RED)
#     red_slice = Slice(2, 2, [red_c1, red_c2, red_c3, red_c4])
    
#     # --- BLUE SLICE (1x3 Vertical Bar) ---
#     blue_c1 = Cell(1, 4, CellType.MOVING, CellColor.BLUE)
#     blue_c2 = Cell(2, 4, CellType.MOVING, CellColor.BLUE)
#     blue_c3 = Cell(3, 4, CellType.MOVING, CellColor.BLUE)
#     blue_slice = Slice(3, 1, [blue_c1, blue_c2, blue_c3])

#     # --- YELLOW SLICE (L-Shape) ---
#     yellow_c1 = Cell(4, 1, CellType.MOVING, CellColor.YELLOW)
#     yellow_c2 = Cell(4, 2, CellType.MOVING, CellColor.YELLOW)
#     yellow_c3 = Cell(5, 2, CellType.MOVING, CellColor.YELLOW)
#     yellow_slice = Slice(2, 2, [yellow_c1, yellow_c2, yellow_c3]) # 2x2 bounding box

#     # --- FIXED OBSTACLES ---
#     obstacle_c1 = Cell(3, 2, CellType.CONSTANT, CellColor.BLACK)
#     obstacle_c2 = Cell(3, 3, CellType.CONSTANT, CellColor.BLACK)

#     # --- OUTPUT CELLS ---
#     # Red output on the right
#     red_out1 = Cell(2, 7, CellType.OUTPUT, CellColor.RED)
#     red_out2 = Cell(3, 7, CellType.OUTPUT, CellColor.RED)
#     # Blue output on the left
#     blue_out1 = Cell(2, 0, CellType.OUTPUT, CellColor.BLUE)
#     blue_out2 = Cell(3, 0, CellType.OUTPUT, CellColor.BLUE)
#     blue_out3 = Cell(4, 0, CellType.OUTPUT, CellColor.BLUE)
#     # Yellow output on the bottom
#     yellow_out1 = Cell(7, 4, CellType.OUTPUT, CellColor.YELLOW)
#     yellow_out2 = Cell(7, 5, CellType.OUTPUT, CellColor.YELLOW)

#     # List of all slices and output cells
#     all_slices = [red_slice, blue_slice, yellow_slice]
#     all_output_cells = [red_out1, red_out2, blue_out1, blue_out2, blue_out3, yellow_out1, yellow_out2]

#     # Create the game with a 6x6 grid (plus the border)
#     return Game(6, 6, all_slices, all_output_cells)

# class GameGUI:
#     def __init__(self, master, game):
#         self.master = master
#         self.game = game
#         self.cell_size = 60
#         self.selected_slice = None
#         self.canvas_items = {}
        
#         self.main_frame = tk.Frame(master)
#         self.main_frame.pack(fill=tk.BOTH, expand=True)
        
#         self.canvas = tk.Canvas(
#             self.main_frame, 
#             width=(game.horizontal_length + 2) * self.cell_size,
#             height=(game.vertical_length + 2) * self.cell_size,
#             bg="white"
#         )
#         self.canvas.pack(side=tk.LEFT, padx=10, pady=10)
        
#         self.control_panel = tk.Frame(self.main_frame)
#         self.control_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
#         tk.Label(self.control_panel, text="Move Selected Slice:", font=("Arial", 12, "bold")).pack(pady=5)
        
#         button_frame = tk.Frame(self.control_panel)
#         button_frame.pack(pady=10)
        
#         tk.Button(button_frame, text="↑", command=lambda: self.move_slice(Direction.TOP), 
#                  width=5, height=2).grid(row=0, column=1, padx=2, pady=2)
#         tk.Button(button_frame, text="←", command=lambda: self.move_slice(Direction.LEFT), 
#                  width=5, height=2).grid(row=1, column=0, padx=2, pady=2)
#         tk.Button(button_frame, text="→", command=lambda: self.move_slice(Direction.RIGHT), 
#                  width=5, height=2).grid(row=1, column=2, padx=2, pady=2)
#         tk.Button(button_frame, text="↓", command=lambda: self.move_slice(Direction.BOTTOM), 
#                  width=5, height=2).grid(row=2, column=1, padx=2, pady=2)
        
#         tk.Label(self.control_panel, text="Move Count:").pack(pady=5)
#         self.move_count = tk.IntVar(value=1)
#         tk.Spinbox(self.control_panel, from_=1, to=10, textvariable=self.move_count, 
#                   width=5).pack(pady=5)
        
#         tk.Button(self.control_panel, text="Reset Game", command=self.reset_game, 
#                  width=15).pack(pady=20)
        
#         self.slice_info = tk.Label(self.control_panel, text="Click on a colored slice to select it", 
#                                   wraplength=150, justify=tk.LEFT)
#         self.slice_info.pack(pady=10)
        
#         self.draw_grid()
#         self.canvas.bind("<Button-1>", self.on_canvas_click)
#         self.check_win_condition()
    
#     def draw_grid(self):
#         self.canvas.delete("all")
#         self.canvas_items = {}
        
#         for i in range(self.game.vertical_length + 3):
#             y = i * self.cell_size
#             self.canvas.create_line(0, y, (self.game.horizontal_length + 2) * self.cell_size, y, fill="gray")
        
#         for j in range(self.game.horizontal_length + 3):
#             x = j * self.cell_size
#             self.canvas.create_line(x, 0, x, (self.game.vertical_length + 2) * self.cell_size, fill="gray")
        
#         for i in range(self.game.vertical_length + 2):
#             for j in range(self.game.horizontal_length + 2):
#                 cell = self.game.grid[i, j]
#                 x1 = j * self.cell_size
#                 y1 = i * self.cell_size
#                 x2 = x1 + self.cell_size
#                 y2 = y1 + self.cell_size
                
#                 fill_color = "white"
#                 outline_color = "gray"
#                 outline_width = 1

#                 if cell.cellType == CellType.CONSTANT:
#                     fill_color = "black"
#                 elif cell.cellType == CellType.MOVING:
#                     fill_color = cell.cellColor.value
#                     if self.selected_slice and cell.slice == self.selected_slice:
#                         outline_color = "yellow"
#                         outline_width = 3
#                 elif cell.cellType == CellType.OUTPUT:
#                     fill_color = cell.cellColor.value
#                     outline_color = "black"
#                     outline_width = 2
                
#                 rect = self.canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, 
#                                                    fill=fill_color, outline=outline_color, width=outline_width)
#                 self.canvas_items[(i, j)] = rect
    
#     def on_canvas_click(self, event):
#         j = event.x // self.cell_size
#         i = event.y // self.cell_size
        
#         if 0 <= i < self.game.vertical_length + 2 and 0 <= j < self.game.horizontal_length + 2:
#             cell = self.game.grid[i, j]
            
#             if cell.cellType == CellType.MOVING and cell.slice:
#                 self.selected_slice = cell.slice
#                 self.slice_info.config(text=f"Selected slice:\n{len(cell.slice.cells)} cells\nColor: {cell.cellColor.value}")
#                 self.draw_grid()
#             else:
#                 self.selected_slice = None
#                 self.slice_info.config(text="Click on a colored slice to select it")
#                 self.draw_grid()

#     def move_slice(self, direction):
#         if not self.selected_slice:
#             messagebox.showinfo("No Selection", "Please select a slice first by clicking on it.")
#             return
        
#         try:
#             self.game.moveSlice(self.selected_slice, direction, self.move_count.get())
            
#             if self.selected_slice not in self.game.slices:
#                 self.selected_slice = None
#                 self.slice_info.config(text="Slice removed! Keep going!")

#             self.draw_grid()
#             self.check_win_condition()
            
#         except Exception as e:
#             messagebox.showerror("Invalid Move", str(e))
    
#     def check_win_condition(self):
#         if len(self.game.slices) == 0:
#             messagebox.showinfo("Congratulations!", "You've won the game!")
#             return True
#         return False
    
#     def reset_game(self):
#         """
#         Resets the game by calling the level creation function.
#         This ensures the reset game is identical to the initial game.
#         """
#         self.game = create_hard_level()
#         self.selected_slice = None
#         self.slice_info.config(text="Click on a colored slice to select it")
#         self.draw_grid()

# def main():
#     # Create the game using the new level creation function
#     myGame = create_hard_level()
    
#     root = tk.Tk()
#     root.title("Slice Puzzle Game - Hard Level")
#     app = GameGUI(root, myGame)
#     root.mainloop()

# if __name__ == "__main__":
#     main()