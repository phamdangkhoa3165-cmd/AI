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
        "LEFT" : (row - 1, col),
        "UP" : (row, col - 1),
        "RIGHT" : (row + 1, col),
        "DOWN" : (row, col + 1)
    }

    for action, (r, c) in moves.items():
        if 0 <= r < 3 and 0 <= c < 3:
            new_idx = r * 3 + c

            new_state = list(state)

            new_state[idx], new_state[new_idx] = new_state[new_idx], new_state[idx]

            children.append((tuple(new_state), action))

    return children

def path(node):
    path = []

    while node:
        path.append((node.state, node.action))
        node = node.parent

    return path[::-1]

def bfs_cach_1(initial_state, goal_state):
    node = Node(initial_state)

    reached = set()
    reached.add(initial_state)

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

class UI:
    def __init__(self, root):
        self.root = root
        self.root.title("8 puzzle")

        self.start_state = (2,8,3,1,6,4,7,0,5)
        self.goal_state = (1,2,3,8,0,4,7,6,5)

        self.buttons = []
        for i in range(9):
            btn = tk.Button(root, font = ("Arial", 30, "bold"), width=8, height=3)
            row, col = divmod(i, 3)
            btn.grid(row = row, column = col)
            self.buttons.append(btn)

        tk.Button(root, text = "Cach 1", font = ("Arial", 20, "bold"), command=lambda : self.run_algo(1)).grid(row = 3, column = 0, columnspan=3, sticky = "we")
        tk.Button(root, text = "Cach 2", font = ("Arial", 20, "bold"), command=lambda : self.run_algo(2)).grid(row = 4, column = 0, columnspan=3, sticky = "we")

        self.show(self.start_state)

    def show(self, state):
        for i in range(9):
            if state[i] == 0:
                self.buttons[i].config(text = "")
            else:
                self.buttons[i].config(text = str(state[i]))

        self.root.update()

    def run_algo(self, cach):
        if cach == 1:
            print("Cach 1:")
            path = bfs_cach_1(self.start_state, self.goal_state)
        else:
            print("Cach 2:")
            path = bfs_cach_2(self.start_state, self.goal_state)

        for step, action in path[1:]:
            print(action)

            count = 0
            while count < 9:
                print(step[count : count + 3])
                count += 3

            print("\n")

            self.show(step)
            time.sleep(0.5)

if __name__ == "__main__":
    root = tk.Tk()
    app = UI(root)
    root.mainloop()