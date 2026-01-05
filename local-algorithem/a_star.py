import heapq

class Node:
    def __init__(self, name, h_value, streets=None, isTheGoal=False):
        self.name = name
        self.h_value = h_value
        self.streets = streets if streets is not None else []
        self.isTheGoal = isTheGoal

    # Added this so heapq can handle nodes with the same f_score
    def __lt__(self, other):
        return self.h_value < other.h_value

class Street:
    def __init__(self, start, end, g_value):
        self.start = start
        self.end = end
        self.g_value = g_value
        
def a_star(start: Node):
    open_set = []
    # heapq stores (priority, node)
    heapq.heappush(open_set, (start.h_value, start))
    
    came_from = {}
    g_score = {start: 0}
    
    # Track visited nodes to avoid infinite loops/redundancy
    visited = set()

    while open_set:
        # Get the node with the lowest f_score
        current_f, current = heapq.heappop(open_set)

        if current.isTheGoal:
            return reconstruct_path(came_from, current)

        if current in visited:
            continue
        visited.add(current)

        for street in current.streets:
            neighbor = street.end
            tentative_g_score = g_score[current] + street.g_value

            # If this path to neighbor is better than any previous one
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + neighbor.h_value
                heapq.heappush(open_set, (f_score, neighbor))
    
    return None # No path found

def reconstruct_path(came_from, current):
    # print('this is the came from:', came_from)
    # print('this is the current:', current)
    total_path = [current]
    while current in came_from:
        current = came_from[current]        
        total_path.append(current)
    return total_path[::-1]

if __name__ == "__main__":
    A = Node("A", 7)
    B = Node("B", 6)
    C = Node("C", 2)
    D = Node("D", 1)
    E = Node("E", 0, isTheGoal=True)

    A.streets = [Street(A, B, 1), Street(A, C, 4)]
    B.streets = [Street(B, C, 2), Street(B, D, 5)]
    C.streets = [Street(C, D, 1), Street(C, E, 3)]
    D.streets = [Street(D, E, 1)]

    path = a_star(A)
    if path:
        print("Path found:", " -> ".join(node.name for node in path))
    else:
        print("No path found.")