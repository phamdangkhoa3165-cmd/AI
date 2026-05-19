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
        "RIGHT" : (row, col + 1),
        "UP" : (row - 1, col),
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
        path.append((node.state, node.action))
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

# BFS cách 2
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

# DFS cách 1
def dfs_cach_1(initial_state, goal_state):
    node = Node(initial_state)

    reached = set()

    frontier = [node]
    frontier_state = {initial_state}

    while frontier:
        node = frontier.pop()
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

# DFS cách 2
def dfs_cach_2(initial_state, goal_state):
    node = Node(initial_state)

    if initial_state == goal_state:
        return path(node)
    
    reached = set()
    reached.add(initial_state)

    frontier = [node]

    while frontier:
        node = frontier.pop()

        for child_state, action in get_child(node.state):
            child = Node(child_state, node, action)

            if child_state == goal_state:
                return path(child)
            
            if child_state not in reached and child not in frontier:
                reached.add(child_state)
                frontier.append(child)

    return None

def IDS(initial_state, goal_state):
    for i in range(1000):
        result = IDS_limited(initial_state, goal_state, i)
        if result != i:
            return path(result)

def IDS_limited(initial_state, goal_state, I):
    depth = 0

    node = Node(initial_state)

    reached = set()
    reached.add(initial_state)

    frontier = [node]

    while frontier:
        node = frontier.pop()

        if node.state == goal_state:
            return node
        
        reached.add(node.state)

        if depth >= I:
            result = I
        
        else:
            for child_state, action in get_child(node.state):
                if child_state not in reached:
                    child = Node(child_state, node, action)

                    frontier.append(child)

    return result

import tkinter as tk
import time

class SimpleUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-puzzle - DFS - Phạm Đăng Khoa")

        self.start_state = (1,2,3,4,0,6,7,5,8)
        self.goal_state = (1,2,3,4,5,6,7,8,0)

        self.buttons = []
        for i in range(9):
            btn = tk.Button(root, font = ("Arial", 30, "bold"), width=5, height=2)
            row, col = divmod(i, 3)
            btn.grid(row = row, column = col)
            self.buttons.append(btn)

        tk.Button(root, text = "BFS", font = ("Arial", 20, "bold")).grid(row = 3, column = 0, rowspan = 2, columnspan = 1, sticky = "wesn")
        tk.Button(root, text = "Cách 1", font = ("Arial", 20, "bold"), command=lambda : self.run_algo_BFS(1)).grid(row = 3, column = 1, columnspan=2, sticky = "we")
        tk.Button(root, text = "Cách 2", font = ("Arial", 20, "bold"), command=lambda : self.run_algo_BFS(2)).grid(row = 4, column = 1, columnspan=2, sticky = "we")
        tk.Button(root, text = "DFS", font = ("Arial", 20, "bold")).grid(row = 5, column = 0, rowspan = 2, columnspan = 1, sticky = "wesn")
        tk.Button(root, text = "Cách 1", font = ("Arial", 20, "bold"), command=lambda : self.run_algo_DFS(1)).grid(row = 5, column = 1, columnspan=2, sticky = "we")
        tk.Button(root, text = "Cách 2", font = ("Arial", 20, "bold"), command=lambda : self.run_algo_DFS(2)).grid(row = 6, column = 1, columnspan=2, sticky = "we")
        tk.Button(root, text = "IDS", font = ("Arial", 20, "bold")).grid(row = 7, column = 0, columnspan = 1, sticky = "wesn")
        tk.Button(root, text = "Giải", font = ("Arial", 20, "bold"), command=lambda : self.run_algo_IDS()).grid(row = 7, column = 1, columnspan=2, sticky = "we")
        tk.Button(root, text = "Reset", font = ("Arial", 20, "bold"), command=lambda : self.reset()).grid(row = 8, column = 0, columnspan = 3, sticky = "we")
        tk.Button(root, text = "Dừng", font = ("Arial", 20, "bold"), command=lambda : self.exit()).grid(row = 9, column = 0, columnspan = 3, sticky = "we")
        

        self.show(self.start_state)

    # Hàm in bảng
    def show(self, state):
        for i in range(9):
            # Nếu ô đó bằng 0 thì để trống
            if state[i] == 0:
                self.buttons[i].config(text = "")
            else:
                self.buttons[i].config(text = str(state[i]))

        self.root.update()

    def exit(self):
        return self.exit()

    def reset(self):
        self.show(self.start_state)

    def run_algo_BFS(self, cach):
        if cach == 1:
            print("Cách 1: ")
            path = bfs_cach_1(self.start_state, self.goal_state)
        else:
            print("Cách 2: ")
            path = bfs_cach_2(self.start_state, self.goal_state)

        if path:
            print("Tìm thấy đường đi trong", len(path) - 1, "bước:")

            for step, action in path[1::]:
                self.show(step)

                print(action)

                count = 0
                while count < 9:
                    print(step[count:count + 3])
                    count += 3

                print("\n")
                
                time.sleep(0.5)
        else:
            print("Không có đường đi!")

    def run_algo_DFS(self, cach):
        if cach == 1:
            print("Cách 1: ")
            path = dfs_cach_1(self.start_state, self.goal_state)
        else:
            print("Cách 2: ")
            path = dfs_cach_2(self.start_state, self.goal_state)

        if path:
            print("Tìm thấy đường đi trong", len(path) - 1, "bước:")

            for step, action in path[1::]:
                self.show(step)

                print(action)

                count = 0
                while count < 9:
                    print(step[count:count + 3])
                    count += 3

                print("\n")
                
                time.sleep(0.5)
        else:
            print("Không có đường đi!")

    def run_algo_IDS(self):
        
        path = IDS(self.start_state, self.goal_state)

        if path:
            print("Tìm thấy đường đi trong", len(path) - 1, "bước:")

            for step, action in path[1::]:
                self.show(step)

                print(action)

                count = 0
                while count < 9:
                    print(step[count:count + 3])
                    count += 3

                print("\n")
                
                time.sleep(0.5)
        else:
            print("Không có đường đi!")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleUI(root)
    root.mainloop()