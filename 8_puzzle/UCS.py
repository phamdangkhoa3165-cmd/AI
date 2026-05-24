from collections import deque

class Node:
    def __init__(self, state, parent=None, action=None, cost=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost

def path(node):
    path = []

    while node:
        path.append((node.action, node.state, node.cost))
        node = node.parent

    return path[::-1]

def uncorrect(state, goal_state):
    count = 0

    for i in range(9):
        if state[i] != goal_state[i]:
            count += 1

    return count

def get_child(state, goal_state):
    children = []

    idx = state.index(0)

    row, col = divmod(idx, 3)

    moves = {
        "L" : (row, col - 1),
        "R" : (row, col + 1),
        "U" : (row - 1, col),
        "D" : (row + 1, col)
    }

    for action, (r, c) in moves.items():
        if 0 <= r < 3 and 0 <= c < 3:
            new_idx = r*3+c

            new_state = list(state)

            new_state[idx], new_state[new_idx] = new_state[new_idx], new_state[idx]

            children.append((action, tuple(new_state), uncorrect(new_state, goal_state)))

    return children

def UCS(initial_state, goal_state):
    node = Node(initial_state, parent=None, action=None, cost=uncorrect(initial_state, goal_state))

    reached = set()

    frontier = deque([node])

    while frontier:
        de_sort = deque(sorted(frontier, key=lambda x: x.cost))

        for i in range(len(de_sort)):
            if de_sort[i].state not in reached:
                node = de_sort[i]
                break

        if node.state == goal_state:
            return path(node)
        
        for action, child_state, uncorrect_child in get_child(node.state, goal_state):
            child = Node(child_state, node, action, uncorrect_child + node.cost)

            in_frontier = False
            for i in range(len(frontier)):
                if frontier[i].state == child_state:
                    in_frontier = True

                    if frontier[i].state == child_state and child.cost < frontier[i].cost:
                        frontier[i] = child
                        break
       
            if not in_frontier:
                frontier.append(child)

        reached.add(node.state)

    return Node

start_state = (8,6,7,2,5,4,3,0,1)
goal_state = (1,2,3,4,5,6,7,8,0)

path_puzzle = UCS(start_state, goal_state)

for step in path_puzzle:
    print(step)