from collections import deque

class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action

def get_child(state):
    children = []

    idx = state.index(0)

    row, col = divmod(idx, 3)

    moves = { 
        "LEFT" : (row, col - 1),
        "UP" : (row - 1, col),
        "RIGHT" : (row, col + 1),
        "DOWN" : (row + 1, col)
    }

    for action, (r, c) in moves.items():
        if 0 <= r < 3 and 0 <= c < 3:
            new_state = list(state)

            new_idx = r * 3 + c

            new_state[idx], new_state[new_idx] = new_state[new_idx], new_state[idx]

            children.append((tuple(new_state), action))

    return children

def path(node):
    path = []

    while node:
        path.append(node.state)
        node = node.parent

    return path[::-1]

def bfs_cach_1(initial_state, goal_state):
    node = Node(initial_state)

    reached = set()

    frontier = deque([node])
    frontier_state = {initial_state}

    while frontier:
        node = frontier.popleft()
        frontier_state.remove(node.state)

        if node.state == goal_state:
            return path(node)
        
        reached.add(node.state)
        
        for child_state, action in get_child(node.state):
            if child_state not in reached and child_state not in frontier_state:
                child = Node(child_state, node, action)

                frontier.append(child)

                frontier_state.add(child_state)

    return None

def bfs_cach_2(initial_state, goal_state):
    node = Node(initial_state)

    if initial_state == goal_state:
        return path(node)
    
    reached = set()
    reached.add(initial_state)

    frontier = deque([node])

    while frontier:
        node = frontier.popleft()

        for child_state, action in get_child(node.state):
            child = Node(child_state, node, action)

            if child_state == goal_state:
                return path(child)
            
            if child_state not in reached:
                reached.add(child_state)
                frontier.append(child)

    return None

import tkinter as tk
import time

class SimpleUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-puzzle - Pham Dang Khoa")

        self.start_state = [2,8,3,1,6,4,7,0,5]
        self.goal_state = [1,2,3,8,0,3,7,6,5]

        self.buttons = []
        for i in range(9):
            btn = tk.Button(root, font = ("Arial", 24, "bold"), width=4, height=2)
            row, col = divmod(i, 3)
            btn.grid(row = row, column = col)
            self.buttons.append(btn)

        tk.Button(root, text = "Cách 1", command=lambda : self.run_algo(1)).grid(row = 3, column = 0, columnspan=3, sticky = "we")
        tk.Button(root, text = "Cách 2", command=lambda : self.run_algo(2)).grid(row = 4, column = 0, columnspan=3, sticky = "we")

        self.show(self.start_state)

    def show(self, state):
        for i in range(9):
            if state == 0:
                self.buttons[i].config(text = "")
            else:
                self.buttons[i].config(text = str(state[i]))

        self.root.update

    def run_algo(self, cach):
        if cach == 1:
            path = bfs_cach_1(self.start_state, self.goal_state)
        else:
            path = bfs_cach_2(self.start_state, self.goal_state)

        if path:
            for step in path:
                self.show(step)
                time.sleep(0.4)
        else:
            print("Không có đường đi!")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleUI(root)
    root.mainloop()