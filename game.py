import numpy as np
from cell_type_enum import CellType
from cell_color_enum import CellColor
from direction_enum import Direction
from slice import Slice
from cell import Cell
import random
from typing import List, TypedDict, Any, Set, Tuple, Dict
import copy
from collections import deque
import time
import heapq 
import sys

class HistoryState(TypedDict):
    previousGrid: list[Cell]
    previousSlices: list[Slice]

class AvailableMove(TypedDict):
    """Represents a single valid move that can be applied to the current state."""
    slice_id: Any
    slice_color: CellColor
    direction: Direction
    dx: int  
    dy: int  


class Game:
    def __init__(self, vertical_length, horizontal_length, movingSlices, outputSlices, constantSlices=[]):
        self.vertical_length = vertical_length
        self.horizontal_length = horizontal_length
        self.slices = movingSlices
        self.undoStack: List[HistoryState] = []
        self.VisitedStatesMap: Set[str] = set()
        rows = vertical_length
        cols = horizontal_length
        self.grid = np.empty((rows, cols), dtype=object)
        for r in range(rows):
            for c in range(cols):
                self.grid[r, c] = Cell(r, c, CellType.EMPTY)
        self.initializeTheGrid(outputSlices, constantSlices)
        self.calculateTotalAvailableMoves()
        hashString = self.generateHashString()
        self.VisitedStatesMap.add(hashString)

    # ---------- Utility helpers ----------
    def findCellIndexInSlice(self, slice_obj, cell_to_find: Cell) -> int:
        """Find index of a cell in slice_obj.cells by coordinates. Returns -1 if not found."""
        for idx, sc in enumerate(slice_obj.cells):
            if sc.x == cell_to_find.x and sc.y == cell_to_find.y:
                return idx
        return -1


    def generateHashString(self) -> str:
        state = []

        for s in sorted(self.slices, key=lambda x: x.id):
            cells = []

            for c in s.cells:
                cells.append((
                    int(c.x),
                    int(c.y),
                    int(c.cellType.value),
                    str(c.cellColor.value) if c.cellColor else None
                ))

            # IMPORTANT: sort ONLY by coordinates
            cells.sort(key=lambda x: (x[0], x[1]))

            state.append((
                str(s.id),
                int(s.sliceVerticalLength),
                int(s.sliceHorizontalLength),
                tuple(cells)
            ))

        return str(tuple(state))

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

        # Place output slices
        for slice in outputSlices:
            for cell in slice.cells:
                self.grid[cell.x, cell.y].x = cell.x
                self.grid[cell.x, cell.y].y = cell.y
                self.grid[cell.x, cell.y].cellColor = cell.cellColor
                self.grid[cell.x, cell.y].cellType = cell.cellType
                self.grid[cell.x, cell.y].slice = cell.slice

    def moveSlice(self, slice, direction: Direction, movements=1):
        # cannot move if numberToBeAbleToMoveIt restriction
        if getattr(slice, 'numberToBeAbleToMoveIt', None) is not None and slice.numberToBeAbleToMoveIt > 0:
            return False

        if direction not in slice.directions:
            return False

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

        # find current index of slice in self.slices
        try:
            sliceIndex = self.slices.index(slice)
        except ValueError:
            # slice not managed by this game
            return False

        rows, cols = self.grid.shape

        for i in range(movements):
            collision = False
            current_positions = set((cell.x, cell.y) for cell in slice.cells)

            # collision checks first
            for cell in slice.cells:
                target_grid_x = cell.x + dx
                target_grid_y = cell.y + dy

                # boundary check
                if not (0 <= target_grid_x < rows and 0 <= target_grid_y < cols):
                    collision = True
                    break

                target_cell = self.grid[target_grid_x, target_grid_y]
                is_same_slice = (target_grid_x, target_grid_y) in current_positions

                if (
                    target_cell.cellType == CellType.CONSTANT
                    or (target_cell.cellType == CellType.MOVING and not is_same_slice)
                    or (target_cell.cellType == CellType.OUTPUT and target_cell.cellColor != cell.cellColor)
                ):
                    collision = True
                    break

            if collision:
                return False

            # push undo state (deepcopy to be safe)
            state = {
                'previousGrid': copy.deepcopy(self.grid),
                'previousSlices': copy.deepcopy(self.slices)
            }
            self.undoStack.append(state)

            # clear old positions
            for cell in slice.cells:
                old_grid_x = cell.x
                old_grid_y = cell.y
                self.grid[old_grid_x, old_grid_y] = Cell(old_grid_x, old_grid_y, CellType.EMPTY)

            # update cells positions (and grid)
            # We'll construct a new list of new cell objects for this slice
            new_cells = []
            for old_cell in slice.cells:
                new_x = old_cell.x + dx
                new_y = old_cell.y + dy
                # place new cell on grid
                new_cell = Cell(new_x, new_y, old_cell.cellType, old_cell.cellColor)
                new_cell.slice = slice
                self.grid[new_x, new_y] = new_cell
                new_cells.append(new_cell)

            # replace slice.cells with updated cells list (preserving other slice attributes)
            # some implementations keep cells as numpy arrays; we keep it as a list for robustness
            self.slices[sliceIndex].cells = new_cells

            current_slice = self.slices[sliceIndex]

            # run removal checks; these may remove the slice from self.slices
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

            # update sliceIndex if still present
            if slice in self.slices:
                sliceIndex = self.slices.index(slice)

        return True

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

        # Check for collisions and potential output slice detection
        for cell in slice.cells:
            target_grid_x = cell.x + dx
            target_grid_y = cell.y + dy

            # boundary check - if moving outside grid then ignore (can't remove)
            rows, cols = self.grid.shape
            if not (0 <= target_grid_x < rows and 0 <= target_grid_y < cols):
                continue

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
            outputSliceXSet.add(outputCell.x)
            outputSliceYSet.add(outputCell.y)

        if (
            (sliceXSet.issubset(outputSliceXSet) or sliceYSet.issubset(outputSliceYSet))
        ):
            for cell in slice.cells:
                old_grid_x = cell.x
                old_grid_y = cell.y
                self.grid[old_grid_x, old_grid_y] = Cell(old_grid_x, old_grid_y, CellType.EMPTY)

            # Remove slice from slices list
            try:
                self.slices.remove(slice)
            except ValueError:
                pass

            self.decreaseTheNumberToBeAbleToMoveItForEachSliceHasIt()
            self.calculateTotalAvailableMoves()

            return

    def decreaseTheNumberToBeAbleToMoveItForEachSliceHasIt(self):
        for slice in list(self.slices):  # use a copy to be safe while modifying
            if (
                slice.numberToBeAbleToMoveIt is not None and
                slice.numberToBeAbleToMoveIt > 0
            ):
                sliceIndex = self.slices.index(slice)
                # decrement
                self.slices[sliceIndex].numberToBeAbleToMoveIt -= 1
                if self.slices[sliceIndex].numberToBeAbleToMoveIt == 0:
                    # choose new color
                    newColor = None
                    if getattr(slice, 'iceSliceColor', None) is not None:
                        newColor = slice.iceSliceColor
                    else:
                        newColor = self.getRandomSliceColor()

                    for idx, cell in enumerate(self.slices[sliceIndex].cells):
                        self.grid[cell.x, cell.y].cellColor = newColor
                        # update in slice cell list
                        self.slices[sliceIndex].cells[idx].cellColor = newColor

    def undo(self):
        if len(self.undoStack) == 0:
            return

        last_state = self.undoStack.pop()
        self.grid = last_state['previousGrid']
        self.slices = last_state['previousSlices']

    def removeMovementCellsFromGrid(self):
         rows = self.vertical_length
         cols = self.horizontal_length
         for r in range(rows):
            for c in range(cols):
                if(self.grid[r, c].cellType == CellType.MOVING):
                   self.grid[r, c] = Cell(r, c, CellType.EMPTY)

    def canMakeSingleMove(self, slice: 'Slice', dx: int, dy: int) -> bool:
        rows, cols = self.grid.shape
        current_positions: Set[Tuple[int, int]] = set((cell.x, cell.y) for cell in slice.cells)

        for cell in slice.cells:
            target_grid_x = cell.x + dx
            target_grid_y = cell.y + dy

            # boundary check
            if not (0 <= target_grid_x < rows and 0 <= target_grid_y < cols):
                return False

            target_cell = self.grid[target_grid_x, target_grid_y]
            is_same_slice = (target_grid_x, target_grid_y) in current_positions

            if (
                target_cell.cellType == CellType.CONSTANT
                or (slice.cells[0].cellColor == CellColor.FOGGY)
                or (target_cell.cellType == CellType.MOVING and not is_same_slice)
                or (target_cell.cellType == CellType.OUTPUT and target_cell.cellColor != cell.cellColor)
            ):
                return False

        return True

    def getAvailableMovesForState(self) -> List[AvailableMove]:
        all_possible_moves: List[AvailableMove] = []

        DIRECTIONS = {
            Direction.TOP: (-1, 0),
            Direction.BOTTOM: (1, 0),
            Direction.LEFT: (0, -1),
            Direction.RIGHT: (0, 1),
        }

        def getRestriction(slice_obj) -> str:
            has_horizontal = Direction.LEFT in slice_obj.directions and Direction.RIGHT in slice_obj.directions
            has_vertical = Direction.TOP in slice_obj.directions and Direction.BOTTOM in slice_obj.directions

            if has_horizontal and has_vertical:
                return 'none'
            elif has_horizontal:
                return 'horizontal'
            elif has_vertical:
                return 'vertical'
            else:
                return 'none'

        for slice_obj in self.slices:
            restriction = getRestriction(slice_obj)
            slice_id = getattr(slice_obj, 'id', id(slice_obj))
            slice_color = slice_obj.cells[0].cellColor if slice_obj.cells[0].cellColor else None

            for direction, (dx, dy) in DIRECTIONS.items():
                is_vertical_move = direction in (Direction.TOP, Direction.BOTTOM)
                is_horizontal_move = direction in (Direction.LEFT, Direction.RIGHT)

                can_move = False
                if is_vertical_move and (restriction == "vertical" or restriction == "none"):
                    can_move = True
                elif is_horizontal_move and (restriction == "horizontal" or restriction == "none"):
                    can_move = True

                if can_move:
                    if self.canMakeSingleMove(slice_obj, dx, dy):
                        move_details: AvailableMove = {
                            'slice_id': slice_id,
                            'slice_color': slice_color,
                            'direction': direction,
                            'dx': dx,
                            'dy': dy
                        }
                        all_possible_moves.append(move_details)

        return all_possible_moves

    def calculateTotalAvailableMoves(self) -> int:
        all_moves = self.getAvailableMovesForState()
        total_possible = len(all_moves)

        print("\n--- Report of Available Moves ---")
        for move in all_moves:
            direction_name = move['direction'].name
            color_name = move['slice_color'].name if move['slice_color'] is not None else "NONE"
            print(f"Slice [{move['slice_id']},{color_name}] : Can move {direction_name}")

        print(f">>> Total Options: {total_possible}")
        # print("--------------------------------------\n")

        return total_possible

    def resetToInitialState(self):
        while self.undoStack:
              self.undo()


    def DFS_Recursive(self, max_iterations: int = 1000000):
        """
        Depth-first search (recursive, backtracking).
        GUI-compatible version with statistics.
        """

        start_time = time.time()

        visited: Set[str] = set()

        path: List[Tuple[Any, Direction]] = []
        iterations = 0

        # add initial state
        visited.add(self.generateHashString())

        def backtrack():
            nonlocal iterations
            iterations += 1

            # print('this is the iterations : ',iterations)
            # print('this is the max_iterations : ',max_iterations)
            if iterations > max_iterations:
                return None

            # goal
            if len(self.slices) == 0:
                return path.copy()

            for move in self.getAvailableMovesForState():
                slice_id = move["slice_id"]
                direction = move["direction"]

                slice_obj = next(
                    (s for s in self.slices if getattr(s, "id", id(s)) == slice_id),
                    None
                )
                if slice_obj is None:
                    continue

                if not self.moveSlice(slice_obj, direction, 1):
                    continue

                hash_string = self.generateHashString()
                if hash_string in visited:
                    self.undo()
                    continue

                visited.add(hash_string)
                path.append((slice_id, direction))

                result = backtrack()
                if result is not None:
                    return result

                path.pop()
                self.undo()

            return None

        solution = backtrack()
        end_time = time.time()
        return {
            "solved": solution is not None,
            "moves": len(path),
            # "moves": len(solution) if solution else 0,
            "visited": len(visited),
            "time": end_time - start_time,
            "memory": sys.getsizeof(visited), 
            "path": solution
            
        }


    def DFS_Iterative(self, max_iterations: int = 1000000):
        """
        Depth-first search (iterative).
        GUI-compatible version with statistics.
        """

        start_time = time.time()

        visited: Set[str] = set()

        path: List[Tuple[Any, Direction]] = []
        iterations = 0

        stack = []
        stack.append(iter(self.getAvailableMovesForState()))

        visited.add(self.generateHashString())

        while stack:
            iterations += 1
            if iterations > max_iterations:
                break

            try:
                move = next(stack[-1])
            
            except StopIteration:
                stack.pop()
                if path:
                    path.pop()
                    self.undo()
                continue

            slice_id = move["slice_id"]
            direction = move["direction"]

            slice_obj = next(
                (s for s in self.slices if getattr(s, "id", id(s)) == slice_id),
                None
            )
            if slice_obj is None:
                continue

            if not self.moveSlice(slice_obj, direction, 1):
                continue

            hash_string = self.generateHashString()
            if hash_string in visited:
                self.undo()
                continue

            visited.add(hash_string)
            path.append((slice_id, direction))

            if len(self.slices) == 0:
                end_time = time.time()
                self.removeMovementCellsFromGrid()
                return {
                    "solved": True,
                    "moves": len(path),
                    "visited": len(visited),
                    "memory": sys.getsizeof(visited), 
                    "time": end_time - start_time,
                    "path": path.copy()
                }

            stack.append(iter(self.getAvailableMovesForState()))

        end_time = time.time()
        return {
            "solved": False,
            "moves": 0,
            "visited": len(visited),
            "time": end_time - start_time,
            "memory": sys.getsizeof(visited), 
            "path": None
        }

  
    def BFS(self, max_iterations: int = 1000000):

        start_time = time.time()
        visited: Set[str] = set()
        queue = deque()

        # queue item: (game_state, path)
        queue.append((copy.deepcopy(self), []))
        visited.add(self.generateHashString())

        explored_nodes = 0

        while queue:
            if explored_nodes > max_iterations:
                break

            game_state, path = queue.popleft()
            explored_nodes += 1

            # Goal
            if len(game_state.slices) == 0:
               self.removeMovementCellsFromGrid()
               return {
                    "time": time.time() - start_time,
                    "solved": True,
                    "moves": len(path),
                    "visited": len(visited),
                    "memory": sys.getsizeof(visited), 
                    "path": path.copy()
                }
                

            # Expand
            for move in game_state.getAvailableMovesForState():
                new_game = copy.deepcopy(game_state)

                slice_obj = next(
                    (s for s in new_game.slices if s.id == move['slice_id']),
                    None
                )
                
                if slice_obj is None:
                    continue

                if not new_game.moveSlice(slice_obj, move['direction'], 1):
                    continue

                h = new_game.generateHashString()
                if h in visited:
                    continue

                visited.add(h)
                queue.append((
                    new_game,
                    path + [(move['slice_id'], move['direction'])]
                ))

        return {
                    "time": time.time() - start_time,
                    "solved": False,
                    "moves": len(path),
                    "visited": len(visited),
                    "memory": sys.getsizeof(visited), 
                    "path": path.copy(),
                    "game": game_state
               }
      
      
    def calculate_move_cost(self, slice_obj: Slice, direction: Direction) -> int:
        """
        تحسب تكلفة الحركة بناءً على ازدحام المنطقة المستهدفة.
        التكلفة هي عدد الخلايا غير الفارغة المجاورة للموقع الجديد للشريحة.
        """
        # تحديد التغيير في الإحداثيات بناءً على الاتجاه
        dx, dy = 0, 0
        match direction:
            case Direction.TOP: dx, dy = -1, 0
            case Direction.BOTTOM: dx, dy = 1, 0
            case Direction.LEFT: dx, dy = 0, -1
            case Direction.RIGHT: dx, dy = 0, 1

        cost = 0
        # مجموعة لتخزين إحداثيات الخلايا الجديدة لتجنب العد المكرر للجيران
        new_positions = set()
        for cell in slice_obj.cells:
            new_x, new_y = cell.x + dx, cell.y + dy
            new_positions.add((new_x, new_y))

        # فحص كل خلية من الخلايا الجديدة التي ستنتقل إليها الشريحة
        for x, y in new_positions:
            # فحص الجيران الأربعة لكل خلية جديدة
            for dx_neighbor, dy_neighbor in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx_neighbor, y + dy_neighbor
                
                # التأكد من أن الجار داخل حدود الشبكة
                if 0 <= nx < self.grid.shape[0] and 0 <= ny < self.grid.shape[1]:
                    neighbor_cell = self.grid[nx, ny]
                    # إذا لم يكن الجار فارغاً أو جزءاً من نفس الشريحة، زد التكلفة
                    if neighbor_cell.cellType != CellType.EMPTY and (nx, ny) not in new_positions:
                        cost += 1
                        
        return cost  
      
      
    def ucs(self, max_iterations: int = 1000000):
        """
        البحث بالتكلفة الموحدة (UCS) مع تكلفة تعتمد على حجم الشريحة.
        تكلفة كل حركة تساوي عدد الخلايا في الشريحة التي يتم تحريكها.
        """
        start_time = time.time()
        # نستخدم dict لتخزين الحالة مع أقل تكلفة وصلنا إليها
        visited = {self.generateHashString(): 0}
        pq = [] 
        counter = 0
        
        # نضيف الحالة الأولية إلى طابور الأولويات: (التكلفة, رابط فريد, المسار)
        heapq.heappush(pq, (0, counter, []))
        
        iterations = 0
        while pq:
            current_cost, _, path = heapq.heappop(pq)
            iterations += 1
            if iterations > max_iterations: 
                break

            # إعادة بناء الحالة الحالية بناءً على المسار المخزن
            self.resetToInitialState()
            for m_id, m_dir in path:
                s_obj = next(s for s in self.slices if s.id == m_id)
                self.moveSlice(s_obj, m_dir, 1)

            # فحص الهدف: هل انتهت جميع الشرائح؟
            if len(self.slices) == 0:
                return self._format_result(True, path, start_time, visited)

            # توسيع البحث: تجربة جميع الحركات الممكنة من الحالة الحالية
            for move in self.getAvailableMovesForState():
                slice_obj = next(s for s in self.slices if s.id == move['slice_id'])
                
                # تنفيذ الحركة لتقييمها
                if self.moveSlice(slice_obj, move['direction'], 1):
                    # التعديل هنا: التكلفة هي عدد خلايا الشريحة
                    move_cost = len(slice_obj.cells) 
                    new_cost = current_cost + move_cost
                    state_hash = self.generateHashString()
                    
                    # نضيف الحالة الجديدة فقط إذا كانت أقل تكلفة أو لم نزرها من قبل
                    if state_hash not in visited or new_cost < visited[state_hash]:
                        visited[state_hash] = new_cost
                        counter += 1
                        new_path = path + [(move['slice_id'], move['direction'])]
                        heapq.heappush(pq, (new_cost, counter, new_path))
                    
                    # التراجع عن الحركة فوراً لتجربة الحركة التالية
                    self.undo() 

        # إذا انتهت الحلقة ولم نجد حل
        return {
            "solved": False, 
            "time": time.time() - start_time, 
            "memory": sys.getsizeof(visited), 
            "visited": len(visited)
        }
      
      
    def _precompute_output_targets(self) -> Dict[Any, List[Tuple[int, int]]]:
        """تُستدعى مرة واحدة فقط عند بدء اللعبة لتخزين أماكن الأهداف"""
        targets = {}
        rows, cols = self.grid.shape
        for r in range(rows):
            for c in range(cols):
                cell = self.grid[r, c]
                if cell.cellType == CellType.OUTPUT and cell.cellColor:
                    if cell.cellColor not in targets:
                        targets[cell.cellColor] = []
                    targets[cell.cellColor].append((r, c))
        return targets

    def calculate_heuristic(self, game_instance=None) -> int:
        """
        حساب قيمة الـ Heuristic: مجموع مسافات مانهاتن لكل شريحة إلى أقرب هدف لها.
        :param game_instance: نسخة اللعبة المراد حسابها (اختياري). إذا كانت None، يتم الحساب لـ self.
        """

        target_game = game_instance if game_instance is not None else self
        
        total_h = 0
        
        targets = getattr(self, 'output_targets', self._precompute_output_targets())

        for slice_obj in target_game.slices:
            slice_color = slice_obj.cells[0].cellColor
            

            if not slice_color or slice_color not in targets:
                continue 


            
            min_slice_dist = float('inf')
            
            for cell in slice_obj        .cells:
                for target_r, target_c in targets[slice_color]:
                    dist = abs(cell.x - target_r) + abs(cell.y - target_c)
                    if dist < min_slice_dist:
                        min_slice_dist = dist
            

            total_h += min_slice_dist
            
        return total_h



    def a_star(self, max_iterations: int = 1000000):
        """
        A* Search Algorithm: Minimizes f(n) = g(n) + h(n).
        Uses max_iterations to cap search time.
        """
        start_time = time.time()
        visited = {}  
        pq = []       
        counter = 0
        iterations = 0
        
        initial_h = self.calculate_heuristic()

        heapq.heappush(pq, (initial_h, counter, copy.deepcopy(self), [], 0))
        visited[self.generateHashString()] = 0

        while pq:
            iterations += 1
            if iterations > max_iterations:
                break

            f, _, current_game, path, g = heapq.heappop(pq)

            if len(current_game.slices) == 0:
                memory_used = sys.getsizeof(visited) 
                return {
                    "solved": True,
                    "moves": len(path),
                    "visited": len(visited),
                    "iterations": iterations,
                    "time": time.time() - start_time,
                    "memory": memory_used,
                    "path": path
                }


            for move in current_game.getAvailableMovesForState():
                new_game = copy.deepcopy(current_game)
                slice_obj = next(s for s in new_game.slices if s.id == move['slice_id'])
                
                if new_game.moveSlice(slice_obj, move['direction'], 1):
                    new_g = g + 1
                    h = new_game.calculate_heuristic()
                    new_f = new_g + h
                    state_hash = new_game.generateHashString()

                    if state_hash not in visited or new_g < visited[state_hash]:
                        visited[state_hash] = new_g
                        counter += 1
                        heapq.heappush(pq, (new_f, counter, new_game, 
                                          path + [(move['slice_id'], move['direction'])], new_g))

        return {
            "solved": False, 
            "iterations": iterations, 
            "time": time.time() - start_time,
            "visited": len(visited),
            "game":current_game
        }




    def _format_result(self, solved, path, start_time, visited):
        print("Visited states:", len(visited))
        return {
            "solved": solved,
            "moves": len(path),
            "visited": len(visited),
            "time": time.time() - start_time,
            "memory": sys.getsizeof(visited),
            "path": path
        }


    def hill_climbing(self, max_restarts=10, random_moves_per_restart=3, max_iterations_per_climb=5000):
        """
        نسخة محسنة من Hill Climbing باستخدام إعادة البدء العشوائي.
        في حالة الفشل في إيجاد حل، تعيد أفضل نتيجة تم الوصول إليها.
        """
        start_time = time.time()
        
        best_overall_path = []
        best_overall_h = float('inf')  
        best_overall_visited = 0

        initial_state_hash = self.generateHashString()
        
        for restart in range(max_restarts):
            print(f"--- Restart Attempt #{restart + 1} ---")
            
            if restart > 0:

                while self.undoStack:
                    self.undo()
            
            current_restart_path = []
            
            for _ in range(random_moves_per_restart):
                available_moves = self.getAvailableMovesForState()
                if not available_moves:
                    break
                random_move = random.choice(available_moves)
                slice_obj = next(s for s in self.slices if s.id == random_move['slice_id'])
                self.moveSlice(slice_obj, random_move['direction'], 1)
                current_restart_path.append((random_move['slice_id'], random_move['direction']))

            climb_path = []
            visited_for_this_climb = {self.generateHashString()}
            
            for i in range(max_iterations_per_climb):
                if len(self.slices) == 0:

                    final_solution_path = current_restart_path + climb_path
                    total_time = time.time() - start_time
                    print(f"Solution found after {restart + 1} restarts!")
                    return {
                        "solved": True,
                        "moves": len(final_solution_path),
                        "visited": len(visited_for_this_climb),
                        "time": total_time,
                        "memory": sys.getsizeof(visited_for_this_climb),
                        "path": final_solution_path
                    }

                current_h = self.calculate_heuristic()
                neighbors = []
                
                for move in self.getAvailableMovesForState():
                    s_obj = next(s for s in self.slices if s.id == move['slice_id'])
                    if self.moveSlice(s_obj, move['direction'], 1):
                        h = self.calculate_heuristic()
                        h_hash = self.generateHashString()
                        if h_hash not in visited_for_this_climb:
                            neighbors.append((h, move, h_hash))
                        self.undo()

                if not neighbors: 
                    print("Stuck in a local optimum, no better neighbors found.")
                    break 

                neighbors.sort(key=lambda x: x[0])
                best_h, best_move, best_hash = neighbors[0]

                if best_h >= current_h: 
                    print("Stuck in a local optimum, no better moves available.")
                    break 
                    

                s_obj = next(s for s in self.slices if s.id == best_move['slice_id'])
                self.moveSlice(s_obj, best_move['direction'], 1)
                visited_for_this_climb.add(best_hash)
                climb_path.append((best_move['slice_id'], best_move['direction']))

          
            
            full_path_for_this_attempt = current_restart_path + climb_path
            

            final_h_for_this_attempt = self.calculate_heuristic()
            

            if final_h_for_this_attempt < best_overall_h:
                print(f"New best attempt found with heuristic: {final_h_for_this_attempt}")
                best_overall_h = final_h_for_this_attempt
                best_overall_path = full_path_for_this_attempt
                best_overall_visited = len(visited_for_this_climb)



        total_time = time.time() - start_time
        print("Failed to find a solution after all restart attempts.")
        print(f"Returning the best attempt found with a heuristic of: {best_overall_h}")
        

        return {
            "solved": False,
            "moves": len(best_overall_path),
            "visited": best_overall_visited,
            "time": total_time,
            "memory": sys.getsizeof(best_overall_path),
            "path": best_overall_path,
            "final_heuristic": best_overall_h 
        }  
      
    
    def minimax_alpha_beta(self, depth, alpha, beta, is_maximizing):
        """
        Recursive helper for Minimax with Alpha-Beta pruning.
        Returns the score of the current state.
        """
        # Terminal Check: Did we win? (All slices removed)
        if len(self.slices) == 0:
            return float('inf')

        # Depth Check: Reached lookahead limit
        if depth == 0:
            # We want to minimize the distance to goal (heuristic).
            # Standard Minimax Maximizes Score. So we invert the heuristic.
            # Lower Heuristic -> Higher Score.
            return -self.calculate_heuristic()

        if is_maximizing:
            max_eval = -float('inf')
            for move in self.getAvailableMovesForState():
                slice_obj = next((s for s in self.slices if s.id == move['slice_id']), None)
                if slice_obj:
                    # Make move
                    if self.moveSlice(slice_obj, move['direction'], 1):
                        # Recurse (Next turn is Minimizing/Opponent)
                        eval_val = self.minimax_alpha_beta(depth - 1, alpha, beta, False)
                        self.undo() # Backtrack
                        
                        max_eval = max(max_eval, eval_val)
                        alpha = max(alpha, eval_val)
                        if beta <= alpha:
                            break # Beta Cutoff
            return max_eval
        else:
            # Minimizing Player (The "Opponent" or Pessimistic View)
            min_eval = float('inf')
            for move in self.getAvailableMovesForState():
                slice_obj = next((s for s in self.slices if s.id == move['slice_id']), None)
                if slice_obj:
                    if self.moveSlice(slice_obj, move['direction'], 1):
                        # Recurse (Next turn is Maximizing/Player)
                        eval_val = self.minimax_alpha_beta(depth - 1, alpha, beta, True)
                        self.undo() # Backtrack
                        
                        min_eval = min(min_eval, eval_val)
                        beta = min(beta, eval_val)
                        if beta <= alpha:
                            break # Alpha Cutoff
            return min_eval


    def minimax(self, max_depth=3, max_iterations=100000):
        """
        Minimax Algorithm: Executes moves based on a lookahead search.
        """
        start_time = time.time()
        path = []
        iterations = 0
        
        # Initial check
        if len(self.slices) == 0:
            return self._format_result(True, path, start_time, set())

        while len(self.slices) > 0 and iterations < max_iterations:
            iterations += 1
            
            best_move = None
            best_value = -float('inf')
            
            possible_moves = self.getAvailableMovesForState()
            
            if not possible_moves:
                break # Dead end (no moves available)

            # For each available move at the current state:
            for move in possible_moves:
                slice_obj = next((s for s in self.slices if s.id == move['slice_id']), None)
                if slice_obj:
                    # 1. Simulate Move
                    if self.moveSlice(slice_obj, move['direction'], 1):
                        # 2. Evaluate State using Recursive Minimax
                        # Note: We pass False because we assume the "opponent" plays next
                        value = self.minimax_alpha_beta(max_depth - 1, -float('inf'), float('inf'), False)
                        
                        # 3. Undo Move
                        self.undo()
                        
                        # 4. Keep track of best move
                        if value > best_value:
                            best_value = value
                            best_move = move

            # If we found a best move, execute it permanently
            if best_move:
                slice_obj = next((s for s in self.slices if s.id == best_move['slice_id']), None)
                if self.moveSlice(slice_obj, best_move['direction'], 1):
                    path.append((best_move['slice_id'], best_move['direction']))
            else:
                # No move improved our score (or all were -inf), stop to avoid infinite loop
                break

        # Check if solved
        solved = (len(self.slices) == 0)
        
        return {
            "solved": solved,
            "moves": len(path),
            "visited": iterations, # In Minimax, iterations represent "steps taken", not strictly "states visited" like in BFS
            "time": time.time() - start_time,
            "path": path
        }  
      
    def compare_algorithms(self, max_iterations=1000000):
        """
        يقوم هذه الدالة بمقارنة جميع الخوارزميات المطبقة وإرجاع جدول بالمقارنة
        """
        algorithms = [
            ("DFS (Recursive)", lambda g: g.DFS_Recursive(max_iterations)),
            ("DFS (Iterative)", lambda g: g.DFS_Iterative(max_iterations)),
            ("BFS (Iterative)", lambda g: g.BFS(max_iterations)),
            ("UCS", lambda g: g.ucs(max_iterations)),
            ("A*", lambda g: g.a_star(max_iterations)),
            ("Hill Climbing", lambda g: g.hill_climbing(max_iterations))
        ]
        
        results = {}
        
        for name, algorithm in algorithms:

            game_copy = copy.deepcopy(self)
            

            start_time = time.time()
            result = algorithm(game_copy)
            end_time = time.time()
            

            results[name] = {
                "solved": result["solved"],
                "time": result.get("time", end_time - start_time),
                "memory": result.get("memory", 0),
                "moves": result.get("moves", 0),
                "visited": result.get("visited", 0),
                "path": result.get("path", None)
            }
        
        return results  
            
    
    @staticmethod
    def display_comparison_table(results):
        """
        Displays comparison results in a table and renders the path for each algorithm.
        """

        print("\n" + "="*80)
        print("{:<20} {:<10} {:<15} {:<15} {:<10} {:<10}".format(
            "Algorithm", "Solved", "Time (sec)", "Memory (KB)", "Moves", "Visited"
        ))
        print("-" * 80)
        
        for name, data in results.items():
            memory_kb = f"{data['memory'] / 1024:.2f}" if data["memory"] > 0 else "N/A"
            print("{:<20} {:<10} {:<15.4f} {:<15} {:<10} {:<15}".format(
                name,
                "Yes" if data["solved"] else "No",
                data["time"],
                memory_kb,
                data["moves"],
                data["visited"]
            ))
        
        print("="*80 + "\n")


        print("DETAILED PATHS PER ALGORITHM:")

        
        print("\n")

        for name, data in results.items():
            print("="*80 + "\n")
            print(f"PATH FOR: {name}")
            

            if data["solved"] and "path" in data and data["path"]:

                path_string = " -> ".join(map(str, data["path"]))
                print(path_string)
            elif data["solved"]:
                print("No specific path data recorded (Solved).")
            else:
                print("No path available (Algorithm did not solve).")
            

            
            print("\n")      

               
               
               