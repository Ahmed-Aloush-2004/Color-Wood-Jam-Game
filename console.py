# from game import Game
# from slice import Slice
# from cell import Cell
# from cell_color_enum import CellColor
# from cell_type_enum import CellType
# from direction_enum import Direction





# c1 = Cell(0,2,CellType.MOVING,CellColor.RED)
# c2 = Cell(1,2,CellType.MOVING,CellColor.RED)
# c3 = Cell(2,2,CellType.MOVING,CellColor.RED)

# c4 = Cell(1,1,CellType.MOVING,CellColor.YELLOW)


# # c5 = Cell(1,1,CellType.CONSTANT,CellColor.BLACK)


# s1 = Slice(1,3,[c1,c2,c3])
# s2 = Slice(1,1,[c4])
# # s3 = Slice(1,1,[c5])

# myGame = Game(3,3,[s1,s2])
# # myGame = Game(3,3,[s1,s2,s3])

# myGame.printTheGrid()

# myGame.moveSlice(s2,Direction.TOP,1)


# print(" Hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii ")


# myGame.printTheGrid()





from game import Game
from slice import Slice
from cell import Cell
from cell_color_enum import CellColor
from cell_type_enum import CellType
from direction_enum import Direction

c1 = Cell(1, 0, CellType.MOVING, CellColor.RED)
c2 = Cell(1, 1, CellType.MOVING, CellColor.RED)
c3 = Cell(1, 2, CellType.MOVING, CellColor.RED)
cc1 = Cell(2, 0, CellType.MOVING, CellColor.RED)
cc2 = Cell(2, 1, CellType.MOVING, CellColor.RED)
cc3 = Cell(2, 2, CellType.MOVING, CellColor.RED)
c4 = Cell(3, 1, CellType.MOVING, CellColor.RED)
# c4 = Cell(0, 1, CellType.MOVING, CellColor.RED)
# c4 = Cell(1, 1, CellType.MOVING, CellColor.YELLOW)  # fixed overlapping (2,2)
# c5 = Cell(1, 1, CellType.CONSTANT, CellColor.BLACK)

# c7 = Cell(0,1,CellType.OUTPUT,CellColor.RED)
# c8 = Cell(0,2,CellType.OUTPUT,CellColor.RED)
# c9 = Cell(0,3,CellType.OUTPUT,CellColor.RED)


c7 = Cell(1,5,CellType.OUTPUT,CellColor.RED)
c8 = Cell(2,5,CellType.OUTPUT,CellColor.RED)
c9 = Cell(3,5,CellType.OUTPUT,CellColor.RED)
c10 = Cell(4,5,CellType.OUTPUT,CellColor.RED)


c6 = Cell(0, 1, CellType.MOVING, CellColor.RED)

s1 = Slice(3, 3, [
                   c1,
                   c2
                  ,c3
                  ,cc1,cc2
                  ,cc3
                  ,c4])

s3 = Slice(1,1,[c4],4)
# s2 = Slice(1, 1, [c6])
# s3 = Slice(1, 1, [c5])
# s4 = Slice(1, 1, [c6])

# myGame = Game(3, 3, [s1])
myGame = Game(4, 4, [s1],[c7,c8,c9,c10])
print(" before top  ")
myGame.printTheGrid()
myGame.moveSlice(s1, Direction.RIGHT, 1)
print(" after top  ")
myGame.printTheGrid()


# print(" before right  ")
# myGame.printTheGrid()
# myGame.moveSlice(s2, Direction.RIGHT, 1)
# print(" after right  ")
# myGame.printTheGrid()


# print(" before bottom  ")
# myGame.printTheGrid()
# myGame.moveSlice(s2, Direction.BOTTOM, 2)
# print(" after bottom  ")
# myGame.printTheGrid()



# print(" before left  ")
# myGame.printTheGrid()
# myGame.moveSlice(s2, Direction.LEFT, 2)
# print(" after left  ")
# myGame.printTheGrid()





# import tkinter as tk
# from tkinter import ttk  # Themed Tkinter for a better look

# # 1. Create the main window
# root = tk.Tk()
# root.title("My Python GUI App")
# root.geometry("300x150") # Set initial size

# # 2. Add a widget (a label)
# label = ttk.Label(root, text="Hello, GUI World!")
# label.pack(pady=20) # 'pack' is a layout manager to place the widget

# # 3. Add a button
# def on_button_click():
#     label.config(text="Button Clicked!")

# button = ttk.Button(root, text="Click Me", command=on_button_click)
# button.pack()

# # 4. Start the main event loop
# # This keeps the window open and responsive to user input
# root.mainloop()