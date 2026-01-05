import tkinter as tk
from tkinter import messagebox
import json
import numpy as np
from game import Game
from slice import Slice
from cell import Cell
from cell_color_enum import CellColor
from cell_type_enum import CellType
from direction_enum import Direction
import math


def returnColorValue(colorSymbol):
    print('this is before everything,while reading the file : ',CellColor.RED)
    match colorSymbol:
         case 0:
             return CellColor.BLACK
         case 1:
             return CellColor.RED
         case 2:
             return CellColor.BLUE
         case 3:
             return CellColor.GREEN
         case 4:
             return CellColor.YELLOW
         case 5:
             return CellColor.BLUE
         case 6:
             return CellColor.PURPLE
         case 7:
             return CellColor.ORANGE
         case 8:
             return CellColor.FOGGY
         
def load_level_from_json(filepath="field-1.2.json"):
    """
    Loads a game level from a JSON file and returns a Game object.
    
    Updated to handle the JSON structure with 'shapes', 'blocks', and 'exists'.
    """
    try:
        with open(filepath, 'r') as f:
            level_data = json.load(f)
    except FileNotFoundError:
        messagebox.showerror("Error", f"Level file not found at {filepath}")
        return None

    all_moving_slices = []
    all_output_slices = []
    all_constant_slices = []

    # 1. Create MOVING Slices from JSON data
    for slice_data in level_data.get("shapes", []):
        color = None
        if(slice_data.get("move_lock", 0) is not 0):
            color = CellColor.FOGGY
        else:
            color = returnColorValue(slice_data["colors"])
            
        cells = []
        move_lock = 0 
        directions: Direction = []
        
        for cell_data in slice_data["coordinates"]:
            cells.append(Cell(cell_data[0], cell_data[1], CellType.MOVING, color))
        
        if slice_data.get("direction") == 'horizontal':   
            directions.append(Direction.LEFT) 
            directions.append(Direction.RIGHT) 
        
        if slice_data.get("direction") == 'vertical':
            directions.append(Direction.TOP) 
            directions.append(Direction.BOTTOM) 
        
        # If no direction is specified, allow all directions
        if not directions:
            directions = [Direction.TOP, Direction.BOTTOM, Direction.LEFT, Direction.RIGHT]
            
        move_lock = slice_data.get("move_lock", 0)
        iceSliceColor = returnColorValue(slice_data["colors"])
                     
        # Calculate the bounding box for the slice
        min_x = min(c.x for c in cells)
        max_x = max(c.x for c in cells)
        min_y = min(c.y for c in cells)
        max_y = max(c.y for c in cells)
        
        slice_vertical_length = max_x - min_x + 1
        slice_horizontal_length = max_y - min_y + 1
        
        all_moving_slices.append(Slice(slice_vertical_length, slice_horizontal_length, cells, move_lock, directions,iceSliceColor))

    # 2. Create Obstacles from JSON data (blocks)
    blocks = level_data.get("blocks", [])
    if blocks:
        # Group blocks by color (they're all black)
        cells = []
        for block_data in blocks:
            cells.append(Cell(block_data[0], block_data[1], CellType.CONSTANT, CellColor.BLACK))
        
        # Calculate the bounding box for the slice
        min_x = min(c.x for c in cells)
        max_x = max(c.x for c in cells)
        min_y = min(c.y for c in cells)
        max_y = max(c.y for c in cells)
        
        slice_vertical_length = max_x - min_x + 1
        slice_horizontal_length = max_y - min_y + 1
        
        all_constant_slices.append(Slice(slice_vertical_length, slice_horizontal_length, cells))

    # 3. Create Output Cells from JSON data (exists)
    for output_data in level_data.get("exists", []):
        color = returnColorValue(output_data["color"])
        cells = []
        for cell_data in output_data["coordinates"]:
            cells.append(Cell(cell_data[0], cell_data[1], CellType.OUTPUT, color))
        
        # Calculate the bounding box for the slice
        min_x = min(c.x for c in cells)
        max_x = max(c.x for c in cells)
        min_y = min(c.y for c in cells)
        max_y = max(c.y for c in cells)
        
        slice_vertical_length = max_x - min_x + 1
        slice_horizontal_length = max_y - min_y + 1
        
        all_output_slices.append(Slice(slice_vertical_length, slice_horizontal_length, cells))

    # 4. Create and return the Game object
    return Game(
        level_data["rows"],
        level_data["cols"],
        all_moving_slices,
        all_output_slices,
        all_constant_slices
    )





class GameGUI:
    def __init__(self, master, game):
        self.master = master
        self.game = game
        self.cell_size = 60
        self.selected_slice = None
        self.canvas_items = {}
        self.last_game_copy = game
        
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Use game dimensions + 2 for borders
        self.canvas = tk.Canvas(
            self.main_frame, 
            width=(game.horizontal_length) * self.cell_size,
            height=(game.vertical_length ) * self.cell_size,
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
        
        tk.Button(self.control_panel, text="Visualize State Tree", 
                  command=self.draw_state_tree, 
                  width=15, bg="#a0a0ff").pack(pady=10)
        
        tk.Label(self.control_panel, text="Move Count:").pack(pady=5)
        self.move_count = tk.IntVar(value=1)
        tk.Spinbox(self.control_panel, from_=1, to=10, textvariable=self.move_count, 
                   width=5).pack(pady=5)
        
        tk.Button(self.control_panel, text="Undo Last Move", command=self.trigger_undo, 
                  width=15, bg="#e1e1e1").pack(pady=10)

        tk.Button(self.control_panel, text="Reset Game", command=self.reset_game, 
                  width=15).pack(pady=20)
        
        
        tk.Label(self.control_panel, text="Search Algorithms", 
         font=("Arial", 12, "bold")).pack(pady=10)

        tk.Button(self.control_panel, text="DFS Recursive",
                command=self.run_dfs_recursive,
                width=18).pack(pady=3)

        tk.Button(self.control_panel, text="DFS Iterative",
                command=self.run_dfs_iterative,
                width=18).pack(pady=3)

        tk.Button(self.control_panel, text="A* ",
                command=self.run_a_star,
                width=18).pack(pady=3)

        tk.Button(self.control_panel, text="Hill Climbing",
                command=self.run_hill_climbing,
                width=18).pack(pady=3)
        
        tk.Button(self.control_panel, text="Minimax",
                command=self.run_minimax,
                width=18).pack(pady=3)

        tk.Button(self.control_panel, text="Minimax Alpha Beta",
                command=self.run_minimax_alpha_beta,
                width=18).pack(pady=3)
        
        tk.Button(self.control_panel, text="UCS",
                command=self.run_ucs,
                width=18).pack(pady=3)
        
        tk.Button(self.control_panel, text="BFS Iterative",
                command=self.run_BFS,
                width=18).pack(pady=3)
        
        tk.Button(self.control_panel, text="Heuristic",
                command=self.run_heuristic,
                width=18).pack(pady=3)

        tk.Button(self.control_panel, text="Comparison",
                command=self.run_comparesion,
                width=18).pack(pady=3)
        

        
        self.slice_info = tk.Label(self.control_panel, text="Click on a colored slice to select it", 
                                   wraplength=150, justify=tk.LEFT)
        self.slice_info.pack(pady=10)
        
        self.draw_grid()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.check_win_condition()

    def show_search_result(self, title, result):
        win = tk.Toplevel(self.master)
        win.title(title)
        win.geometry("300x250") 
        win.resizable(False, False)

        if result is None:
            tk.Label(win, text="Algorithm failed or returned nothing", fg="red").pack(pady=20)
            tk.Button(win, text="OK", command=win.destroy, width=10).pack(pady=10)
            return

        print('this is the result : ',result)
        status = "SOLVED ✅" if result["solved"] else "NOT SOLVED ❌"
        tk.Label(win, text=status, font=("Arial", 14, "bold")).pack(pady=10)
        
        if result["solved"]:
            tk.Label(win, text=f"Moves: {result.get('moves', 'N/A')}").pack()
                  
        if result.get('message'):
            tk.Label(win, text=f"Message: {result['message']}", wraplength=250).pack(pady=10)
        
        tk.Label(win, text=f"Time: {result.get('time', 0):.4f} sec").pack()
        tk.Label(win, text=f"Visited States: {result.get('visited', 'N/A')}").pack()
        tk.Label(win, text=f"Memory: {result.get('memory', 'N/A')} Bytes").pack()
        tk.Button(win, text="OK", command=win.destroy, width=10, bg="#d9d9d9").pack(pady=20)
   
    def trigger_undo(self):
        if len(self.game.undoStack) == 0:
            messagebox.showinfo("No Moves to Undo", "There are no moves to undo.")
            return
        
        self.game.undo()
        self.selected_slice = None
        self.slice_info.config(text="Undo successful. Please select a slice.")
        self.draw_grid()

    def draw_grid(self):
            self.canvas.delete("all")
            self.canvas_items = {}
            
            for i in range(self.game.vertical_length + 3):
                y = i * self.cell_size
                self.canvas.create_line(0, y, (self.game.horizontal_length + 2) * self.cell_size, y, fill="gray")
            
            for j in range(self.game.horizontal_length + 3):
                x = j * self.cell_size
                self.canvas.create_line(x, 0, x, (self.game.vertical_length + 2) * self.cell_size, fill="gray")

            # Draw cells
            for i in range(self.game.vertical_length ):
                for j in range(self.game.horizontal_length ):
                    cell = self.game.grid[i, j]
                    x1 = j * self.cell_size
                    y1 = i * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    
                    # Center coordinates for the text
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2
                
                    fill_color = "white"
                    outline_color = "gray"
                    outline_width = 1

                    if cell.cellType == CellType.CONSTANT:
                        fill_color = "black"
                    elif cell.cellType == CellType.MOVING:
                        # Check if cellColor is not None before accessing its value
                        if cell.cellColor is not None:
                            fill_color = cell.cellColor.value
                            print('this is the moving cell color : ', cell.cellColor.value)
                        if self.selected_slice and cell.slice == self.selected_slice:
                            outline_color = "yellow"
                            outline_width = 3
                    elif cell.cellType == CellType.OUTPUT:
                        # Check if cellColor is not None before accessing its value
                        if cell.cellColor is not None:
                            fill_color = cell.cellColor.value
                        outline_color = "black"
                        outline_width = 2
                    
                    # rect = self.canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, 
                    #                                     fill=fill_color, outline=outline_color, width=outline_width)
                    # self.canvas_items[(i, j)] = rect
                    
                    
                        # 1. Draw the Rectangle
                    rect = self.canvas.create_rectangle(
                        x1+2, y1+2, x2-2, y2-2, 
                        fill=fill_color, 
                        outline=outline_color, 
                        width=outline_width,
                        tags="cell"
                    )
                    
                    # 2. Draw the Slice ID Text
                    # We check if the cell belongs to a slice (Moving or Constant blocks)
                    if hasattr(cell, 'slice') and cell.slice is not None:
                        # You can use a custom 'id' attribute if you added one to Slice, 
                        # otherwise use the index from the list or Python's internal id()
                        try:
                            # If you want a simple number (0, 1, 2...) based on its position in the game list:
                            slice_id = cell.slice.id
                            # self.game.all_moving_slices.index(cell.slice)
                        except ValueError:
                            # Fallback to internal memory ID if not in moving slices
                            slice_id = id(cell.slice) % 1000 
                        
                        if(cell.cellType == CellType.MOVING ):
                            self.canvas.create_text(
                                center_x, center_y, 
                                text=str(slice_id), 
                                fill='black',
                                font=("Arial", 10, "bold")
                            )
                    
                    self.canvas_items[(i, j)] = rect
            
            
    def on_canvas_click(self, event):
        j = event.x // self.cell_size
        i = event.y // self.cell_size
        
        if 0 <= i < self.game.vertical_length + 2 and 0 <= j < self.game.horizontal_length + 2:
            cell = self.game.grid[i, j]
            
            if cell.cellType == CellType.MOVING and cell.slice:
                self.selected_slice = cell.slice
                self.slice_info.config(text=f"Selected slice:\n{len(cell.slice.cells)} cells\nColor: {cell.cellColor.value} \n id:{cell.slice.id}")
                self.draw_grid()
            else:
                self.selected_slice = None
                self.slice_info.config(text="Click on a colored slice to select it")
                self.draw_grid()

    def move_slice(self, direction):
        if not self.selected_slice:
            messagebox.showinfo("No Selection", "Please select a slice first by clicking on it.")
            return
        
        if self.selected_slice not in self.game.slices:
            self.selected_slice = None
            self.slice_info.config(text="Slice was removed. Select a new one.")
            self.draw_grid()
            return
            
        try:
            self.game.moveSlice(self.selected_slice, direction, self.move_count.get())
            
            if self.selected_slice not in self.game.slices:
                self.selected_slice = None
                self.slice_info.config(text="Slice removed! Keep going!")

            self.draw_grid()
            self.check_win_condition()
            self.last_game_copy = self.game
            
        except Exception as e:
            messagebox.showerror("Invalid Move", str(e))
    
    def check_win_condition(self):
        if len(self.game.slices) == 0:
            self.draw_grid()
            messagebox.showinfo("Congratulations!", "You've won the game!")
            return True
        return False
    
    def reset_game(self):
        Slice.my_iterator = iter(range(10000))  # Reset the iterator for Slice IDs
        self.game = load_level_from_json()
        if self.game: 
            self.selected_slice = None
            self.slice_info.config(text="Click on a colored slice to select it")
            self.draw_grid()
    
    def run_dfs_recursive(self):
        result = self.game.DFS_Recursive()
        self.show_search_result("DFS Recursive", result)
        
    def run_dfs_iterative(self):
        result = self.game.DFS_Iterative()
        self.show_search_result("DFS Iterative", result)

    def run_BFS(self):
        result = self.game.BFS()
        self.show_search_result("BFS Iterative", result)
            
    def run_ucs(self):
        result = self.game.ucs()
        self.show_search_result("UCS", result)            
    
    
    def run_hill_climbing(self):
        result = self.game.hill_climbing()
        self.show_search_result("Hill Climbing", result) 
    
    def run_a_star(self):
        result = self.game.a_star()
        if(self.last_game_copy is not None):
            self.last_game_copy = result["game"]
        self.show_search_result("A*", result)   
        
    def run_minimax_alpha_beta(self):
        result = self.game.minimax_alpha_beta(3,-float('inf'),float('inf'),False)
        if(self.last_game_copy is not None):
            print('this is the result : ',result)
       
    def run_minimax(self):
        result = self.game.minimax()
        if(self.last_game_copy is not None):
            self.last_game_copy = result["game"]
        self.show_search_result("Minimax", result)   
      
      
        
    def run_heuristic(self):
        result = self.game.calculate_heuristic(self.last_game_copy)
        print('this is the heuristic value from gui main : ',result)
    
    def run_comparesion(self):
        results = self.game.compare_algorithms()
        self.game.display_comparison_table(results)
                 
        
    def draw_state_tree(self):       
        self.check_win_condition()
        
        
       
            
def main(): 
    
        myGame = load_level_from_json()
        if not myGame:
            return 
        
        root = tk.Tk()
        root.title("Slice Puzzle Game - JSON Level")
        app = GameGUI(root, myGame)
        root.mainloop()

if __name__ == "__main__":
    main()
    
    
    
    
    
    
    