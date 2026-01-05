
class Node:
    def __init__(self, name, value, children=None,isTheGoal=False):
        self.name = name
        self.value = value
        self.children: list[Node] = children if children is not None else []
        self.isTheGoal:bool = isTheGoal

def hill_climbing(root: Node):
    total_cost = 0
    best_current_value = root.value
    best_current_node = root
    path:list[Node] = [root]
    
    while True:
        print('Current Node:', best_current_node.name, 'Value:', best_current_value)
        if(best_current_node.isTheGoal):
            return {
                "solved": True,
                "moves": len(path)-1,
                "visited": len(path),
                "path": path.copy(),
                "cost": total_cost
            }
        
        if not best_current_node.children:
            return {
                "solved": False,
                "moves": len(path)-1,
                "visited": len(path),
                "path": path.copy(),
                "cost": total_cost
            }



        current_node = best_current_node
        current_value = best_current_value    
        for child in best_current_node.children:
            
            if(child.value <= best_current_value):
                current_value = child.value
                current_node = child
           

        
        if(current_value < best_current_value):
            best_current_node = current_node
            best_current_value = current_value
            total_cost+= best_current_value
            path.append(best_current_node)
        
b= Node("B", 8, isTheGoal=False)
c= Node("C", 11, isTheGoal=False) 
d= Node("D", 6, isTheGoal=False)
e= Node("E", 4, isTheGoal=False)
f= Node("F", 2, isTheGoal=True) 
a = Node("A", 10,[b,c], isTheGoal=False)      
b.children = [d,e]  
e.children = [f]  
       
print('this is the result:',hill_climbing(a)    )            