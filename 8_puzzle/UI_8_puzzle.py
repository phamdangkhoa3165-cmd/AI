import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import time
from collections import deque
import textwrap
import random
import math
import itertools

class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = parent.depth + 1 if parent else 0
        self.cost = self.depth

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
    path_list = []
    while node:
        path_list.append((node.state, node.action))
        node = node.parent
    return path_list[::-1]

# --- HÀM HEURISTIC 1: Số ô sai vị trí (Dùng cho UCS) ---
def uncorrect(state, goal_state):
    count = 0
    for i in range(9):
        # Đếm TẤT CẢ các ô khác nhau (tính cả ô trống 0)
        if state[i] != goal_state[i]:
            count += 1
    return count

# --- HÀM HEURISTIC 2: Khoảng cách Manhattan (Dùng cho Greedy, A*, IDA*) ---
def manhattan_distance(state, goal_state):
    distance = 0
    for i in range(9):
        if state[i] != 0:
            goal_idx = goal_state.index(state[i])
            r1, c1 = divmod(i, 3)
            r2, c2 = divmod(goal_idx, 3)
            distance += abs(r1 - r2) + abs(c1 - c2)
    return distance

# --- TRÌNH QUẢN LÝ GÁN NHÃN (A, B, C...) CHO CÁC TRẠNG THÁI ---
class LabelManager:
    def __init__(self):
        self.counter = 0
        self.mapping = {}
        self.current_depth_generated = []

    def reset_all(self):
        self.counter = 0
        self.mapping = {}
        self.current_depth_generated = []

    def reset_for_depth(self):
        self.current_depth_generated = []

    def generate_label(self, index):
        label = ""
        while index >= 0:
            label = chr(index % 26 + 65) + label
            index = index // 26 - 1
        return label

    def get_label(self, state):
        if state not in self.mapping:
            lbl = self.generate_label(self.counter)
            self.mapping[state] = lbl
            self.counter += 1
        
        lbl = self.mapping[state]
        if lbl not in self.current_depth_generated:
            self.current_depth_generated.append(lbl)
        return lbl
    
# ================= CÁC THUẬT TOÁN TÌM KIẾM =================

def bfs_cach_1(initial_state, goal_state, callback, label_mgr):
    label_mgr.reset_all()
    node = Node(initial_state)
    label_mgr.get_label(node.state)
    
    reached = {}
    frontier = deque([node])
    frontier_state = {initial_state}

    callback("START", None, [node], list(frontier), label_mgr, list(reached.keys()))

    while frontier:
        node = frontier.popleft()
        frontier_state.remove(node.state)

        if node.state == goal_state:
            callback(None, node, [], list(frontier), label_mgr, list(reached.keys()))
            return path(node)
        
        reached[node.state] = True
        
        new_nodes = []
        for child_state, action in get_child(node.state):
            if child_state not in reached and child_state not in frontier_state:
                child = Node(child_state, node, action)
                label_mgr.get_label(child.state)
                frontier.append(child)
                frontier_state.add(child_state)
                new_nodes.append(child)
                
        callback(None, node, new_nodes, list(frontier), label_mgr, list(reached.keys()))
    return None

def bfs_cach_2(initial_state, goal_state, callback, label_mgr):
    label_mgr.reset_all()
    node = Node(initial_state)
    label_mgr.get_label(node.state)
    
    if initial_state == goal_state:
        return path(node)
    
    reached = set()
    reached.add(initial_state)
    frontier = deque([node])
    
    callback("START", None, [node], list(frontier), label_mgr)

    while frontier:
        node = frontier.popleft()
        
        new_nodes = []
        for child_state, action in get_child(node.state):
            child = Node(child_state, node, action)
            label_mgr.get_label(child.state)
            
            if child_state == goal_state:
                callback(None, node, new_nodes + [child], list(frontier) + [child], label_mgr)
                return path(child)
            
            if child_state not in reached:
                reached.add(child_state)
                frontier.append(child)
                new_nodes.append(child)
                
        callback(None, node, new_nodes, list(frontier), label_mgr)
    return None

def dfs_cach_1(initial_state, goal_state, callback, label_mgr):
    label_mgr.reset_all()
    node = Node(initial_state)
    label_mgr.get_label(node.state)
    
    reached = {}
    frontier = [node]
    frontier_state = {initial_state}

    callback("START", None, [node], list(frontier), label_mgr, list(reached.keys()))

    while frontier:
        node = frontier.pop()
        frontier_state.remove(node.state)

        if node.state == goal_state:
            callback(None, node, [], list(frontier), label_mgr, list(reached.keys()))
            return path(node)
        
        reached[node.state] = True
        
        new_nodes = []
        for child_state, action in get_child(node.state):
            if child_state not in reached and child_state not in frontier_state:
                child = Node(child_state, node, action)
                label_mgr.get_label(child.state)
                frontier.append(child)
                frontier_state.add(child_state)
                new_nodes.append(child)
                
        callback(None, node, new_nodes, list(frontier), label_mgr, list(reached.keys()))
    return None

def dfs_cach_2(initial_state, goal_state, callback, label_mgr):
    label_mgr.reset_all()
    node = Node(initial_state)
    label_mgr.get_label(node.state)
    
    if initial_state == goal_state:
        return path(node)
    
    reached = set()
    reached.add(initial_state)
    frontier = [node]
    
    callback("START", None, [node], list(frontier), label_mgr)

    while frontier:
        node = frontier.pop()
        
        new_nodes = []
        for child_state, action in get_child(node.state):
            child = Node(child_state, node, action)
            label_mgr.get_label(child.state)
            
            if child_state == goal_state:
                callback(None, node, new_nodes + [child], list(frontier) + [child], label_mgr)
                return path(child)
            
            if child_state not in reached and not any(n.state == child_state for n in frontier):
                reached.add(child_state)
                frontier.append(child)
                new_nodes.append(child)
                
        callback(None, node, new_nodes, list(frontier), label_mgr)
    return None

def IDS(initial_state, goal_state, callback, label_mgr):
    label_mgr.reset_all()
    for i in range(1000):
        result = IDS_limited(initial_state, goal_state, i, callback, label_mgr)
        if isinstance(result, Node):
            return path(result)
    return None

def IDS_limited(initial_state, goal_state, limit, callback, label_mgr):
    label_mgr.reset_for_depth()
    node = Node(initial_state)
    label_mgr.get_label(node.state)
    reached = set()
    frontier = [node]

    callback(f"Depth = {limit}", None, [node], list(frontier), label_mgr)

    while frontier:
        node = frontier.pop()

        if node.state == goal_state:
            callback(None, node, [], list(frontier), label_mgr)
            return node
        
        reached.add(node.state)

        new_nodes = []
        if node.depth < limit:
            for child_state, action in get_child(node.state):
                if child_state not in reached and not any(n.state == child_state for n in frontier):
                    child = Node(child_state, node, action)
                    label_mgr.get_label(child.state)
                    frontier.append(child)
                    new_nodes.append(child)
                    
        callback(None, node, new_nodes, list(frontier), label_mgr)
    return limit

def UCS_search(initial_state, goal_state, callback, label_mgr):
    label_mgr.reset_all()
    node = Node(initial_state)
    # Lưu g_cost (được tính bằng hàm uncorrect) để in ra
    node.g_cost = uncorrect(initial_state, goal_state)
    node.f_cost = node.g_cost 
    label_mgr.get_label(node.state)
    
    reached = set()
    frontier = [node]
    
    callback("START", None, [node], list(frontier), label_mgr, list(reached))
    
    while frontier:
        frontier.sort(key=lambda x: getattr(x, 'f_cost', float('inf')))
        node = frontier.pop(0)
        
        if node.state == goal_state:
            callback(None, node, [], list(frontier), label_mgr, list(reached))
            return path(node)
            
        if node.state in reached:
            continue
            
        reached.add(node.state)
        
        new_nodes = []
        for child_state, action in get_child(node.state):
            if child_state in reached:
                continue
                
            child = Node(child_state, node, action)
            # Bản chất UCS trong yêu cầu của bạn là tìm đường ngắn nhất theo hàm uncorrect
            child.g_cost = node.g_cost + uncorrect(child_state, goal_state)
            child.f_cost = child.g_cost
            label_mgr.get_label(child.state)
            
            in_frontier = False
            for i in range(len(frontier)):
                if frontier[i].state == child_state:
                    in_frontier = True
                    if child.f_cost < getattr(frontier[i], 'f_cost', float('inf')):
                        frontier[i] = child
                        new_nodes.append(child)
                    break
            
            if not in_frontier:
                frontier.append(child)
                new_nodes.append(child)
                
        callback(None, node, new_nodes, list(frontier), label_mgr, list(reached))
    return None

def Greedy_Search(initial_state, goal_state, callback, label_mgr):
    label_mgr.reset_all()
    node = Node(initial_state)
    node.h_cost = manhattan_distance(initial_state, goal_state)
    label_mgr.get_label(node.state)
    
    reached = set()
    frontier = [node]
    
    callback("START", None, [node], list(frontier), label_mgr, list(reached))
    
    while frontier:
        frontier.sort(key=lambda x: getattr(x, 'h_cost', float('inf')))
        node = frontier.pop(0)
        
        if node.state == goal_state:
            callback(None, node, [], list(frontier), label_mgr, list(reached))
            return path(node)
            
        reached.add(node.state)
        
        new_nodes = []
        for child_state, action in get_child(node.state):
            in_frontier = any(f.state == child_state for f in frontier)
            
            if not in_frontier and child_state not in reached:
                child = Node(child_state, node, action)
                child.h_cost = manhattan_distance(child_state, goal_state)
                label_mgr.get_label(child.state)
                
                frontier.append(child)
                new_nodes.append(child)
                
        callback(None, node, new_nodes, list(frontier), label_mgr, list(reached))
    return None


def AStar_Search(initial_state, goal_state, callback, label_mgr):
    label_mgr.reset_all()
    node = Node(initial_state)
    
    node.g_cost = manhattan_distance(initial_state, goal_state)
    node.h_cost = manhattan_distance(initial_state, goal_state)
    node.f_cost = node.g_cost + node.h_cost
    
    label_mgr.get_label(node.state)
    
    reached = {initial_state: node.g_cost}
    frontier = [node]
    
    callback("START", None, [node], list(frontier), label_mgr, list(reached.keys()))
    
    while frontier:
        frontier.sort(key=lambda x: getattr(x, 'f_cost', float('inf')))
        node = frontier.pop(0)
        
        if node.state == goal_state:
            callback(None, node, [], list(frontier), label_mgr, list(reached.keys()))
            return path(node)
            
        new_nodes = []
        for child_state, action in get_child(node.state):
            child = Node(child_state, node, action)
            
            child.h_cost = manhattan_distance(child_state, goal_state)
            child.g_cost = node.g_cost + child.h_cost
            child.f_cost = child.g_cost + child.h_cost
            
            if child_state in reached and reached[child_state] <= child.g_cost:
                continue
                
            label_mgr.get_label(child.state)
            reached[child_state] = child.g_cost
            
            in_frontier = False
            for i in range(len(frontier)):
                if frontier[i].state == child_state:
                    in_frontier = True
                    if child.g_cost < getattr(frontier[i], 'g_cost', float('inf')):
                        frontier[i] = child
                        new_nodes.append(child)
                    break
            
            if not in_frontier:
                frontier.append(child)
                new_nodes.append(child)
                
        callback(None, node, new_nodes, list(frontier), label_mgr, list(reached.keys()))
        
    return None

def IDAStar_Search(initial_state, goal_state, callback, label_mgr):
    label_mgr.reset_all()
    threshold = manhattan_distance(initial_state, goal_state)

    while True:
        label_mgr.reset_for_depth()
        node = Node(initial_state)
        
        node.g_cost = manhattan_distance(initial_state, goal_state)
        node.h_cost = manhattan_distance(initial_state, goal_state)
        node.f_cost = node.g_cost + node.h_cost
        
        label_mgr.get_label(node.state)

        frontier = [node]
        reached = {initial_state: node.g_cost} 
        
        callback(f"Thres = {threshold}", None, [node], list(frontier), label_mgr, list(reached.keys()))

        min_exceeded = float('inf')
        
        while frontier:
            node = frontier.pop() 

            if node.f_cost > threshold:
                min_exceeded = min(min_exceeded, node.f_cost)
                continue

            if node.state == goal_state:
                callback(None, node, [], list(frontier), label_mgr, list(reached.keys()))
                return path(node)

            new_nodes = []
            children = get_child(node.state)
            
            for child_state, action in reversed(children):
                child = Node(child_state, node, action)
                
                child.h_cost = manhattan_distance(child_state, goal_state)
                child.g_cost = node.g_cost + child.h_cost
                child.f_cost = child.g_cost + child.h_cost

                if child_state in reached and reached[child_state] <= child.g_cost:
                    continue

                reached[child_state] = child.g_cost
                label_mgr.get_label(child.state)
                frontier.append(child)
                new_nodes.append(child)

            new_nodes.reverse() 
            if new_nodes:
                callback(None, node, new_nodes, list(frontier), label_mgr, list(reached.keys()))

        if min_exceeded == float('inf'):
            return None
            
        threshold = min_exceeded

def hill_climbing_simple(initial_state, goal_state, callback, label_mgr):
    label_mgr.reset_all()
    node = Node(initial_state)
    node.h_cost = manhattan_distance(initial_state, goal_state)
    label_mgr.get_label(node.state)

    reached = {initial_state}
    frontier = [node] # Dùng frontier giả lập để ghi trace table

    callback("START", None, [node], list(frontier), label_mgr, list(reached))

    while frontier:
        node = frontier.pop(0)

        if node.state == goal_state:
            callback(None, node, [], list(frontier), label_mgr, list(reached))
            return path(node)

        new_nodes = []
        found_better = False

        # a. Sinh lần lượt các trạng thái lân cận
        for child_state, action in get_child(node.state):
            child = Node(child_state, node, action)
            child.h_cost = manhattan_distance(child_state, goal_state)
            label_mgr.get_label(child.state)
            new_nodes.append(child)

            # ii. NẾU Value(Next) < Value(Current) -> Tìm min thay vì max
            if child.h_cost < node.h_cost: 
                frontier.append(child)
                reached.add(child.state)
                found_better = True
                break # c. Chuyển sang lần lặp tiếp theo ngay lập tức

        callback(None, node, new_nodes, list(frontier), label_mgr, list(reached))

        # Nếu sinh hết lân cận mà không có cái nào tốt hơn
        if not found_better:
            # Dừng vì đã đạt cực tiểu cục bộ (Local Minimum)
            break

    return path(node)


def hill_climbing_steepest(initial_state, goal_state, callback, label_mgr):
    label_mgr.reset_all()
    node = Node(initial_state)
    node.h_cost = manhattan_distance(initial_state, goal_state)
    label_mgr.get_label(node.state)

    reached = {initial_state}
    frontier = [node]

    callback("START", None, [node], list(frontier), label_mgr, list(reached))

    while frontier:
        node = frontier.pop(0)

        if node.state == goal_state:
            callback(None, node, [], list(frontier), label_mgr, list(reached))
            return path(node)

        new_nodes = []
        best_child = None
        best_h = float('inf')

        # Sinh TOÀN BỘ các trạng thái lân cận
        for child_state, action in get_child(node.state):
            child = Node(child_state, node, action)
            child.h_cost = manhattan_distance(child_state, goal_state)
            label_mgr.get_label(child.state)
            new_nodes.append(child)

            # Tìm lân cận có chi phí nhỏ nhất (dốc nhất)
            if child.h_cost < best_h:
                best_h = child.h_cost
                best_child = child

        # Nếu trạng thái dốc nhất đó tốt hơn trạng thái hiện tại
        if best_child and best_child.h_cost < node.h_cost:
            frontier.append(best_child)
            reached.add(best_child.state)
            callback(None, node, new_nodes, list(frontier), label_mgr, list(reached))
        else:
            # Không tồn tại lân cận tốt hơn -> Đạt cực tiểu cục bộ
            callback(None, node, new_nodes, list(frontier), label_mgr, list(reached))
            break

    return path(node)

def hill_climbing_stochastic(initial_state, goal_state, callback, label_mgr):
    label_mgr.reset_all()
    node = Node(initial_state)
    node.h_cost = manhattan_distance(initial_state, goal_state)
    label_mgr.get_label(node.state)

    reached = {initial_state}
    frontier = [node]

    callback("START", None, [node], list(frontier), label_mgr, list(reached))

    while frontier:
        node = frontier.pop(0)

        if node.state == goal_state:
            callback(None, node, [], list(frontier), label_mgr, list(reached))
            return path(node)

        new_nodes = []
        better_neighbors = []

        for child_state, action in get_child(node.state):
            child = Node(child_state, node, action)
            child.h_cost = manhattan_distance(child_state, goal_state)
            label_mgr.get_label(child.state)
            new_nodes.append(child)

            # Lọc tập Better_Neighbors: Chọn lân cận tốt hơn trạng thái hiện tại (min)
            if child.h_cost < node.h_cost:
                better_neighbors.append(child)

        if not better_neighbors: # NẾU Better_Neighbors RỖNG
            callback(None, node, new_nodes, list(frontier), label_mgr, list(reached))
            break # Dừng vì đạt cực tiểu cục bộ

        # NGƯỢC LẠI: Chọn ngẫu nhiên 1 trạng thái từ tập Better_Neighbors
        next_node = random.choice(better_neighbors)
        frontier.append(next_node)
        reached.add(next_node.state)

        callback(None, node, new_nodes, list(frontier), label_mgr, list(reached))

    return path(node)


def hill_climbing_random_restart(initial_state, goal_state, callback, label_mgr):
    MAX_RESTART = 5 # Cài đặt giới hạn 5 lần khởi động lại
    
    for i in range(1, MAX_RESTART + 1):
        label_mgr.reset_all()
        node = Node(initial_state)
        node.h_cost = manhattan_distance(initial_state, goal_state)
        label_mgr.get_label(node.state)

        reached = {initial_state}
        frontier = [node]

        callback(f"LƯỢT {i}", None, [node], list(frontier), label_mgr, list(reached))

        while frontier:
            node = frontier.pop(0)

            if node.state == goal_state:
                callback(None, node, [], list(frontier), label_mgr, list(reached))
                return path(node)

            new_nodes = []
            better_neighbors = []

            for child_state, action in get_child(node.state):
                child = Node(child_state, node, action)
                child.h_cost = manhattan_distance(child_state, goal_state)
                label_mgr.get_label(child.state)
                new_nodes.append(child)

                if child.h_cost < node.h_cost:
                    better_neighbors.append(child)

            if not better_neighbors:
                callback(None, node, new_nodes, list(frontier), label_mgr, list(reached))
                break # Kẹt cục bộ, thoát vòng lặp WHILE để nhảy sang lượt i tiếp theo
            
            next_node = random.choice(better_neighbors)
            frontier.append(next_node)
            reached.add(next_node.state)

            callback(None, node, new_nodes, list(frontier), label_mgr, list(reached))

    return None # Thất bại sau MAX_RESTART


def local_beam_search(initial_state, goal_state, callback, label_mgr):
    k = 3 # Khởi tạo k=3
    label_mgr.reset_all()
    start_node = Node(initial_state)
    label_mgr.get_label(start_node.state)

    # 1. Sinh ngẫu nhiên k trạng thái từ Start (Bằng cách đi ngẫu nhiên 3 bước)
    current_state_set = []
    reached = {initial_state}
    new_nodes = []
    
    for _ in range(k):
        rand_node = start_node
        for _ in range(3):
            children = get_child(rand_node.state)
            child_state, action = random.choice(children)
            rand_node = Node(child_state, rand_node, action)
        
        rand_node.h_cost = manhattan_distance(rand_node.state, goal_state)
        label_mgr.get_label(rand_node.state)
        current_state_set.append(rand_node)
        reached.add(rand_node.state)
        new_nodes.append(rand_node)

    current_state_set.sort(key=lambda x: x.h_cost)
    frontier = list(current_state_set)

    callback(f"START k={k}", None, new_nodes, list(frontier), label_mgr, list(reached))

    while True:
        neighbor_states = []
        all_new_nodes = []

        # 2.1 Sinh trạng thái lân cận cho toàn bộ chùm k
        for state_node in current_state_set:
            for child_state, action in get_child(state_node.state):
                child = Node(child_state, state_node, action)
                child.h_cost = manhattan_distance(child_state, goal_state)
                
                if child_state not in reached:
                    label_mgr.get_label(child.state)
                    neighbor_states.append(child)
                    all_new_nodes.append(child)

        # 2.2 Kiểm tra bế tắc / Không cải thiện
        if not neighbor_states:
            current_state_set.sort(key=lambda x: x.h_cost)
            callback(None, current_state_set[0], [], list(current_state_set), label_mgr, list(reached))
            return path(current_state_set[0])

        # 2.3 Kiểm tra đích
        for neighbor in neighbor_states:
            if neighbor.state == goal_state:
                reached.add(neighbor.state)
                callback(None, neighbor.parent, all_new_nodes, [neighbor], label_mgr, list(reached))
                return path(neighbor)

        # 2.4 Lựa chọn chùm: Lấy đúng k trạng thái tốt nhất (h min)
        neighbor_states.sort(key=lambda x: x.h_cost)
        current_state_set = neighbor_states[:k]
        
        for node in current_state_set:
            reached.add(node.state)

        frontier = list(current_state_set)
        
        # Mượn đỉnh đại diện để in bảng Trace
        repr_node = current_state_set[0].parent if current_state_set[0].parent else current_state_set[0]
        callback(None, repr_node, all_new_nodes, list(frontier), label_mgr, list(reached))

def simulated_annealing(initial_state, goal_state, callback, label_mgr):
    label_mgr.reset_all()
    node = Node(initial_state)
    node.h_cost = manhattan_distance(initial_state, goal_state)
    label_mgr.get_label(node.state)

    reached = {initial_state}
    frontier = [node]

    T = 1000.0       # T0: Nhiệt độ ban đầu
    T_min = 0.01     # Nhiệt độ tối thiểu để dừng
    alpha = 0.95     # Hệ số giảm nhiệt (cooling rate)

    callback("START", None, [node], list(frontier), label_mgr, list(reached))

    while T > T_min:
        node = frontier.pop(0)

        if node.state == goal_state:
            callback(None, node, [], list(frontier), label_mgr, list(reached))
            return path(node)

        # RandomNeighbor: Lấy ngẫu nhiên 1 lân cận thay vì duyệt hết
        children = get_child(node.state)
        child_state, action = random.choice(children)
        
        next_node = Node(child_state, node, action)
        next_node.h_cost = manhattan_distance(child_state, goal_state)
        label_mgr.get_label(next_node.state)

        # Δ = h(next state) - h(current state)
        delta_E = next_node.h_cost - node.h_cost

        # Nếu Δ < 0 (tốt hơn), luôn chấp nhận
        if delta_E < 0:
            frontier.append(next_node)
            reached.add(next_node.state)
        # Nếu tệ hơn, chấp nhận với xác suất p = exp(-Δ / T)
        else:
            p = math.exp(-delta_E / T)
            if random.random() < p:
                frontier.append(next_node)
                reached.add(next_node.state)
            else:
                # Từ chối, giữ nguyên trạng thái hiện tại cho vòng lặp sau
                frontier.append(node)

        callback(f"T={T:.2f}", node, [next_node], list(frontier), label_mgr, list(reached))
        
        # Giảm nhiệt độ
        T = T * alpha

    return path(node) # Trả về trạng thái tốt nhất tìm được khi hết nhiệt

# --- THUẬT TOÁN TÌM KIẾM AND-OR (MÔI TRƯỜNG KHÔNG TẤT ĐỊNH) ---
def and_or_graph_search(initial_state, goal_state, max_depth=10):
    # Hàm kết quả (Results): Giả lập môi trường bị "trơn trượt"
    # Khi thực hiện 1 hành động, có thể thành công (ra state mới) hoặc thất bại (giữ nguyên state cũ)
    def results(state, action):
        intended_state = None
        for child_state, act in get_child(state):
            if act == action:
                intended_state = child_state
                break
        if intended_state:
            return [intended_state, state] # Trả về 2 khả năng (Thành công và Thất bại)
        return [state]

    def or_search(state, path, depth):
        if state == goal_state:
            return [] # Kế hoạch rỗng (Đã đạt đích)
        if state in path or depth > max_depth:
            return 'failure' # Tránh lặp hoặc quá sâu
        
        for child_state, action in get_child(state):
            result_states = results(state, action)
            plan = and_search(result_states, path + [state], depth + 1)
            if plan != 'failure':
                return {'action': action, 'if_states': plan}
        return 'failure'

    def and_search(states, path, depth):
        plans = {}
        for s in states:
            plan_s = or_search(s, path, depth)
            if plan_s == 'failure':
                return 'failure'
            plans[s] = plan_s
        return plans

    return or_search(initial_state, [], 0)

# ================= GIAO DIỆN ĐỒ HỌA =================
class SimpleUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Trí tuệ Nhân tạo - 8-Puzzle Simulator (UI Tối ưu)")
        
        # Khuyên dùng: Mở rộng kích thước cửa sổ mặc định để tránh bị hẹp
        self.root.geometry("1350x750")

        self.start_state = (1,2,3,4,0,6,7,5,8)
        self.goal_state = (1,2,3,4,5,6,7,8,0)
        self.label_mgr = LabelManager()

        self.solution_path = []
        self.current_step = 0
        self.is_playing = False
        self.cancel_algo = False

        # Dùng pack cho các khối chính thay vì grid toàn cục để dễ chia bố cục
        left_frame = tk.Frame(root, width=420)
        left_frame.pack(side="left", fill="y", padx=15, pady=10)
        
        right_frame = tk.LabelFrame(root, text="BẢNG TRẠNG THÁI TIẾN TRÌNH", font=("Arial", 12, "bold"), padx=10, pady=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # ==========================================
        # KHU VỰC 1: MA TRẬN 8-PUZZLE
        # ==========================================
        grid_frame = tk.Frame(left_frame)
        grid_frame.pack(pady=5)
        self.buttons = []
        for i in range(9):
            # Thu nhỏ font một chút để ma trận gọn hơn
            btn = tk.Button(grid_frame, font=("Arial", 22, "bold"), width=4, height=1)
            row, col = divmod(i, 3)
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.buttons.append(btn)

        # ==========================================
        # KHU VỰC 2: NHẬP LIỆU (START & GOAL)
        # ==========================================
        input_frame = tk.LabelFrame(left_frame, text="Thiết lập trạng thái (0 là ô trống)", font=("Arial", 9, "bold"))
        input_frame.pack(fill="x", pady=5)
        
        start_frame = tk.Frame(input_frame)
        start_frame.grid(row=0, column=0, padx=5, pady=5)
        tk.Label(start_frame, text="Bắt đầu:", font=("Arial", 9, "bold"), fg="blue").grid(row=0, column=0, columnspan=3)
        self.entries_start = []
        default_start = [1, 2, 3, 4, 0, 6, 7, 5, 8]
        for i in range(9):
            e = tk.Entry(start_frame, width=3, font=("Arial", 12, "bold"), justify="center")
            e.insert(0, str(default_start[i]))
            e.grid(row=(i//3)+1, column=(i%3), padx=2, pady=2)
            self.entries_start.append(e)

        goal_frame = tk.Frame(input_frame)
        goal_frame.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(goal_frame, text="Đích:", font=("Arial", 9, "bold"), fg="red").grid(row=0, column=0, columnspan=3)
        self.entries_goal = []
        default_goal = [1, 2, 3, 4, 5, 6, 7, 8, 0]
        for i in range(9):
            e = tk.Entry(goal_frame, width=3, font=("Arial", 12, "bold"), justify="center")
            e.insert(0, str(default_goal[i]))
            e.grid(row=(i//3)+1, column=(i%3), padx=2, pady=2)
            self.entries_goal.append(e)
        
        tk.Button(input_frame, text="Cập\nnhật", font=("Arial", 10, "bold"), bg="#5cb85c", fg="white", 
                  command=self.apply_input).grid(row=0, column=2, padx=5, pady=5, sticky="ns")

        # ==========================================
        # KHU VỰC 3: MENU THUẬT TOÁN DẠNG TABS
        # ==========================================
        notebook = ttk.Notebook(left_frame)
        notebook.pack(fill="x", pady=10)

        # Tab 1: Tìm kiếm mù & Có thông tin
        tab_basic = ttk.Frame(notebook)
        notebook.add(tab_basic, text="Tìm kiếm Cơ bản")
        
        tk.Button(tab_basic, text="BFS 1", font=("Arial", 10), width=10, command=lambda: self.run_algo(bfs_cach_1)).grid(row=0, column=0, padx=2, pady=4)
        tk.Button(tab_basic, text="BFS 2", font=("Arial", 10), width=10, command=lambda: self.run_algo(bfs_cach_2)).grid(row=0, column=1, padx=2, pady=4)
        tk.Button(tab_basic, text="DFS 1", font=("Arial", 10), width=10, command=lambda: self.run_algo(dfs_cach_1)).grid(row=0, column=2, padx=2, pady=4)
        
        tk.Button(tab_basic, text="DFS 2", font=("Arial", 10), width=10, command=lambda: self.run_algo(dfs_cach_2)).grid(row=1, column=0, padx=2, pady=4)
        tk.Button(tab_basic, text="UCS", font=("Arial", 10, "bold"), bg="#d1ecf1", width=10, command=lambda: self.run_algo(UCS_search)).grid(row=1, column=1, padx=2, pady=4)
        tk.Button(tab_basic, text="Greedy", font=("Arial", 10, "bold"), bg="#d1ecf1", width=10, command=lambda: self.run_algo(Greedy_Search)).grid(row=1, column=2, padx=2, pady=4)
        
        tk.Button(tab_basic, text="IDS", font=("Arial", 10, "bold"), bg="#fff3cd", width=10, command=lambda: self.run_algo(IDS)).grid(row=2, column=0, padx=2, pady=4)
        tk.Button(tab_basic, text="A*", font=("Arial", 10, "bold"), bg="#fff3cd", width=10, command=lambda: self.run_algo(AStar_Search)).grid(row=2, column=1, padx=2, pady=4)
        tk.Button(tab_basic, text="IDA*", font=("Arial", 10, "bold"), bg="#fff3cd", width=10, command=lambda: self.run_algo(IDAStar_Search)).grid(row=2, column=2, padx=2, pady=4)

        # Tab 2: Tìm kiếm Cục bộ (Local Search)
        tab_local = ttk.Frame(notebook)
        notebook.add(tab_local, text="Tìm kiếm Cục bộ")
        
        tk.Button(tab_local, text="HC Simple", font=("Arial", 10, "bold"), bg="#e2e3e5", width=15, command=lambda: self.run_algo(hill_climbing_simple)).grid(row=0, column=0, padx=4, pady=5)
        tk.Button(tab_local, text="HC Steepest", font=("Arial", 10, "bold"), bg="#e2e3e5", width=15, command=lambda: self.run_algo(hill_climbing_steepest)).grid(row=0, column=1, padx=4, pady=5)
        
        tk.Button(tab_local, text="HC Stochastic", font=("Arial", 10, "bold"), bg="#d4edda", width=15, command=lambda: self.run_algo(hill_climbing_stochastic)).grid(row=1, column=0, padx=4, pady=5)
        tk.Button(tab_local, text="HC Restart", font=("Arial", 10, "bold"), bg="#d4edda", width=15, command=lambda: self.run_algo(hill_climbing_random_restart)).grid(row=1, column=1, padx=4, pady=5)
        
        tk.Button(tab_local, text="Beam Search", font=("Arial", 10, "bold"), bg="#cce5ff", width=15, command=lambda: self.run_algo(local_beam_search)).grid(row=2, column=0, padx=4, pady=5)
        tk.Button(tab_local, text="Simulated Annealing", font=("Arial", 10, "bold"), bg="#f8d7da", width=17, command=lambda: self.run_algo(simulated_annealing)).grid(row=2, column=1, padx=4, pady=5)

        # Tab 3: Môi trường nâng cao & Đối kháng
        tab_adv = ttk.Frame(notebook)
        notebook.add(tab_adv, text="AI Mở rộng")
        
        tk.Button(tab_adv, text="Nhóm 4: Môi trường Phức tạp", font=("Arial", 10, "bold"), bg="#fd7e14", fg="white", width=32, command=lambda: ComplexUI(self.root)).pack(pady=6)
        tk.Button(tab_adv, text="Nhóm 5: Ràng buộc (CSP) 8-Puzzle", font=("Arial", 10, "bold"), bg="#6f42c1", fg="white", width=32, command=lambda: CSP_8Puzzle_UI(self.root)).pack(pady=6)
        tk.Button(tab_adv, text="Nhóm 6: Tìm kiếm Đối kháng (Caro)", font=("Arial", 10, "bold"), bg="#20c997", fg="white", width=32, command=lambda: Caro_UI(self.root)).pack(pady=6)

        # ==========================================
        # KHU VỰC 4: ĐIỀU KHIỂN & BÁO CÁO (LOG)
        # ==========================================
        play_frame = tk.LabelFrame(left_frame, text="Điều khiển xem bước", font=("Arial", 9, "bold"), fg="purple")
        play_frame.pack(fill="x", pady=5)
        
        # Căn giữa các nút điều khiển
        play_inner = tk.Frame(play_frame)
        play_inner.pack(pady=5)
        self.btn_prev = tk.Button(play_inner, text="<", state=tk.DISABLED, width=5, command=self.prev_step)
        self.btn_prev.pack(side="left", padx=5)
        self.btn_play = tk.Button(play_inner, text="Tự động Phát", state=tk.DISABLED, width=15, command=self.toggle_play)
        self.btn_play.pack(side="left", padx=5)
        self.btn_next = tk.Button(play_inner, text=">", state=tk.DISABLED, width=5, command=self.next_step)
        self.btn_next.pack(side="left", padx=5)

        self.txt_log = scrolledtext.ScrolledText(left_frame, height=6, font=("Consolas", 10), bg="#f8f9fa")
        self.txt_log.pack(fill="x", pady=5)

        action_frame = tk.Frame(left_frame)
        action_frame.pack(fill="x", pady=5)
        tk.Button(action_frame, text="Reset Toàn bộ", font=("Arial", 11, "bold"), bg="#d9534f", fg="white", width=15, command=self.reset).pack(side="left", expand=True, padx=2)
        tk.Button(action_frame, text="Thoát Chương trình", font=("Arial", 11, "bold"), bg="#343a40", fg="white", width=15, command=self.exit).pack(side="right", expand=True, padx=2)

        # ==========================================
        # KHU VỰC 5: BẢNG TRẠNG THÁI (RIGHT FRAME)
        # ==========================================
        self.txt_trace = tk.Text(right_frame, width=110, font=("Consolas", 10), wrap="none", bg="#1e1e1e", fg="#d4d4d4", borderwidth=0)
        
        y_scroll = tk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.txt_trace.yview)
        x_scroll = tk.Scrollbar(right_frame, orient=tk.HORIZONTAL, command=self.txt_trace.xview)
        self.txt_trace.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.txt_trace.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.show(self.start_state)

    def show(self, state):
        for i in range(9):
            self.buttons[i].config(text="" if state[i] == 0 else str(state[i]), bg="#e9ecef" if state[i] == 0 else "#ffffff")
        self.root.update()

    def apply_input(self):
        try:
            nums_start = [int(e.get().strip()) for e in self.entries_start]
            nums_goal = [int(e.get().strip()) for e in self.entries_goal]
            
            if set(nums_start) != set(range(9)) or set(nums_goal) != set(range(9)):
                messagebox.showerror("Lỗi Input", "Các số phải nằm trong khoảng từ 0 đến 8 và KHÔNG được trùng lặp ở mỗi bảng!")
                return
                
            def count_inversions(state_nums):
                inv = 0
                lst = [x for x in state_nums if x != 0]
                for i in range(8):
                    for j in range(i+1, 8):
                        if lst[i] > lst[j]:
                            inv += 1
                return inv
                
            inv_start = count_inversions(nums_start)
            inv_goal = count_inversions(nums_goal)
            
            if (inv_start % 2) != (inv_goal % 2):
                answer = messagebox.askyesno("Cảnh báo Vô nghiệm", 
                    "Trạng thái Bắt đầu và Đích KHÔNG CÙNG TÍNH CHẴN LẺ (không thể giải được).\n"
                    "Thuật toán sẽ chạy vô tận khám phá đủ ~181,440 đỉnh cho đến khi tràn RAM.\n\n"
                    "Bạn có chắc chắn vẫn muốn nạp vào bảng không?")
                if not answer:
                    return
            
            self.start_state = tuple(nums_start)
            self.goal_state = tuple(nums_goal)
            self.reset() 
            self.txt_log.insert(tk.END, f"Đã nạp Start và Goal mới thành công!\nSẵn sàng chạy thuật toán.\n\n")
            
        except ValueError:
            messagebox.showerror("Lỗi Input", "Vui lòng điền ĐẦY ĐỦ các ô.\nChỉ nhập số nguyên, ô trống hãy điền số 0.")

    def exit(self):
        self.root.destroy()

    def reset(self):
        self.cancel_algo = True 
        
        self.is_playing = False
        self.solution_path = []
        self.show(self.start_state)
        
        self.btn_prev.config(state=tk.DISABLED)
        self.btn_play.config(text="Tự động", state=tk.DISABLED)
        self.btn_next.config(state=tk.DISABLED)

        self.txt_log.delete('1.0', tk.END)
        self.txt_trace.delete('1.0', tk.END)

    def init_trace_table(self):
        self.txt_trace.delete('1.0', tk.END)
        
        self.txt_trace.tag_configure("header", foreground="#5CE1E6", font=("Consolas", 10, "bold"))
        self.txt_trace.tag_configure("depth", foreground="#A8E6CF", font=("Consolas", 10, "bold"))
        self.txt_trace.tag_configure("purple", foreground="#CBA6F7", font=("Consolas", 10))
        self.txt_trace.tag_configure("dash", foreground="#5C6370")

        # Điều chỉnh lại độ rộng cột để chứa chuỗi text dài hơn
        self.w1 = 16 
        self.w2 = 72
        self.w3 = 35 

        col1 = "NODE".center(self.w1)
        col2 = "FRONTIER".center(self.w2)
        col3 = "REACHED".center(self.w3)
        
        self.txt_trace.insert(tk.END, col1, "header")
        self.txt_trace.insert(tk.END, "|", "dash")
        self.txt_trace.insert(tk.END, col2, "header")
        self.txt_trace.insert(tk.END, "|", "dash")
        self.txt_trace.insert(tk.END, col3 + "\n", "header")

        self.sep_line = "-" * self.w1 + "+" + "-" * self.w2 + "+" + "-" * self.w3
        self.txt_trace.insert(tk.END, self.sep_line + "\n", "dash")

    def trace_callback(self, depth_event, current_node, new_nodes, frontier_nodes, label_mgr, reached_states=None):
        if hasattr(self, 'cancel_algo') and self.cancel_algo:
            raise InterruptedError("Ép dừng thuật toán từ nút Reset")

        def pad(text, width): 
            return text[:width].ljust(width)

        if depth_event:
            depth_text = f" {depth_event.upper()} "
            total_width = self.w1 + self.w2 + self.w3 + 2
            formatted_depth = depth_text.center(total_width, "-")
            self.txt_trace.insert(tk.END, formatted_depth + "\n", "depth")

        col1 = f" [{label_mgr.get_label(current_node.state)}]" if current_node else ""
        
        if reached_states is not None:
            reached_labels = [label_mgr.get_label(s) for s in reached_states]
            col3_str = "[" + ", ".join(reached_labels) + "]"
        else:
            col3_str = "[" + ", ".join(label_mgr.current_depth_generated) + "]"
            
        col3_wrapped = textwrap.wrap(col3_str, self.w3 - 2)

        frontier_lines = []
        old_nodes = [n for n in frontier_nodes if n not in new_nodes]
        old_labels = [label_mgr.get_label(n.state) for n in old_nodes]

        frontier_header = ""
        if old_labels: frontier_header += "[" + ", ".join(old_labels) + "]"
        if new_nodes and frontier_header: frontier_header += ", "
        if frontier_header:
            frontier_lines.extend(textwrap.wrap(frontier_header, self.w2 - 2))

        pairs = [new_nodes[i:i+2] for i in range(0, len(new_nodes), 2)]
        for pair in pairs:
            p_lines = ["", "", ""]
            for n in pair:
                s = ['_' if x == 0 else str(x) for x in n.state]
                p_lbl = label_mgr.get_label(n.parent.state) if n.parent else "-"
                
                act = n.action if n.action else "-" 
                
                # --- LOGIC IN CHI PHÍ THÔNG MINH ---
                # A* và IDA* có f_cost, g_cost, và h_cost
                if hasattr(n, 'f_cost') and hasattr(n, 'g_cost') and hasattr(n, 'h_cost'):
                    cost = f"f={n.f_cost}(g={n.g_cost}+h={n.h_cost})"
                # UCS có f_cost và g_cost (nhưng h_cost không có hoặc ko cần hiển thị)
                elif hasattr(n, 'g_cost'):
                    cost = f"g={n.g_cost}"
                # Greedy chỉ có h_cost
                elif hasattr(n, 'h_cost'):
                    cost = f"h={n.h_cost}"
                # BFS/DFS
                else:
                    cost = f"depth={n.depth}"
                # -----------------------------------

                lbl = label_mgr.get_label(n.state)

                # Format lại chuỗi in ra dài hơn để không bị lỗi dòng
                l1 = f"{{[{s[0]} {s[1]} {s[2]}]"
                l2 = f" [{s[3]} {s[4]} {s[5]}],{p_lbl},{act},{cost}}}={lbl}"
                l3 = f" [{s[6]} {s[7]} {s[8]}]"

                # Chỉnh padding lên 36 để đủ chỗ chứa text f=..(g+h)
                p_lines[0] += pad(l1, 36)
                p_lines[1] += pad(l2, 36)
                p_lines[2] += pad(l3, 36)
            frontier_lines.extend(p_lines)

        max_lines = max(2, len(frontier_lines), len(col3_wrapped))
        for i in range(max_lines):
            c1 = col1 if i == 0 else ""
            c2 = frontier_lines[i] if i < len(frontier_lines) else ""
            c3 = col3_wrapped[i] if i < len(col3_wrapped) else ""
            
            str_c1 = pad(c1, self.w1)
            str_c2 = pad(" " + c2 if c2 else "", self.w2)
            str_c3 = pad(" " + c3 if c3 else "", self.w3)
            
            self.txt_trace.insert(tk.END, str_c1)
            self.txt_trace.insert(tk.END, "|", "dash")
            self.txt_trace.insert(tk.END, str_c2)
            self.txt_trace.insert(tk.END, "|", "dash")
            
            if "Reached:" in str_c3:
                idx = str_c3.index("Reached:")
                self.txt_trace.insert(tk.END, str_c3[:idx])
                self.txt_trace.insert(tk.END, "Reached:", "purple")
                self.txt_trace.insert(tk.END, str_c3[idx+8:])
            else:
                self.txt_trace.insert(tk.END, str_c3)
                
            self.txt_trace.insert(tk.END, "\n")

        self.txt_trace.insert(tk.END, self.sep_line + "\n", "dash")
        self.txt_trace.see(tk.END)
        self.root.update()
        time.sleep(0.02)

    def load_solution(self, path_result):
        self.is_playing = False
        if not path_result:
            self.txt_log.insert(tk.END, "Không tìm thấy đường đi!\n")
            return
        self.solution_path = path_result
        self.current_step = 0
        self.btn_play.config(state=tk.NORMAL, text="Tự động")
        self.update_buttons_state()
        self.update_log_for_current_step()
        self.show(self.solution_path[self.current_step][0])

    def update_buttons_state(self):
        self.btn_prev.config(state=tk.DISABLED if self.current_step <= 0 else tk.NORMAL)
        if self.current_step >= len(self.solution_path) - 1:
            self.btn_next.config(state=tk.DISABLED)
            self.is_playing = False
            self.btn_play.config(text="Tự động")
        else:
            self.btn_next.config(state=tk.NORMAL)

    def update_log_for_current_step(self):
        self.txt_log.delete('1.0', tk.END)
        self.txt_log.insert(tk.END, f"Tìm thấy đích trong: {len(self.solution_path) - 1} bước\n")
        self.txt_log.insert(tk.END, f"Đang xem bước: {self.current_step} / {len(self.solution_path) - 1}\n")
        self.txt_log.insert(tk.END, "-" * 32 + "\n")
        
        for i in range(self.current_step + 1):
            state = self.solution_path[i][0]
            act = self.solution_path[i][1]
            
            s = ['_' if x == 0 else str(x) for x in state]
            matrix_str = (
                f"   [{s[0]} {s[1]} {s[2]}]\n"
                f"   [{s[3]} {s[4]} {s[5]}]\n"
                f"   [{s[6]} {s[7]} {s[8]}]"
            )
            
            if i == 0:
                self.txt_log.insert(tk.END, f"Bắt đầu:\n{matrix_str}\n\n")
            else:
                self.txt_log.insert(tk.END, f"Bước {i} (Đi {act}):\n{matrix_str}\n\n")
                
        self.txt_log.see(tk.END)

    def next_step(self):
        if self.solution_path and self.current_step < len(self.solution_path) - 1:
            self.current_step += 1
            self.show(self.solution_path[self.current_step][0])
            self.update_log_for_current_step()
            self.update_buttons_state()

    def prev_step(self):
        if self.solution_path and self.current_step > 0:
            self.current_step -= 1
            self.show(self.solution_path[self.current_step][0])
            self.update_log_for_current_step()
            self.update_buttons_state()

    def toggle_play(self):
        if not self.is_playing:
            if self.current_step >= len(self.solution_path) - 1: self.current_step = 0
            self.is_playing = True
            self.btn_play.config(text="Dừng")
            self.play_next_frame()
        else:
            self.is_playing = False
            self.btn_play.config(text="Tự động")

    def play_next_frame(self):
        if self.is_playing and self.current_step < len(self.solution_path) - 1:
            self.next_step()
            self.root.after(400, self.play_next_frame) 
        else:
            self.is_playing = False
            self.btn_play.config(text="Tự động")

    def run_algo(self, algo_func):
        self.cancel_algo = False 
        
        self.is_playing = False
        self.solution_path = []
        self.show(self.start_state)
        self.btn_prev.config(state=tk.DISABLED)
        self.btn_play.config(text="Tự động", state=tk.DISABLED)
        self.btn_next.config(state=tk.DISABLED)
        self.txt_log.delete('1.0', tk.END)
        
        self.init_trace_table()
        self.txt_log.insert(tk.END, f"Đang chạy thuật toán...\n")
        self.root.update()
        
        try:
            path_res = algo_func(self.start_state, self.goal_state, self.trace_callback, self.label_mgr)
            self.load_solution(path_res)
        except InterruptedError:
            pass

class ComplexUI:
    def __init__(self, root):
        self.top = tk.Toplevel(root)
        self.top.title("Nhóm 4: Môi trường Phức tạp (Khuyết thông tin)")
        self.label_mgr = LabelManager()

        left_frame = tk.Frame(self.top)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        # --- CHỌN CHẾ ĐỘ ---
        self.mode_var = tk.IntVar(value=3)
        mode_frame = tk.LabelFrame(left_frame, text="Chọn loại Môi trường", font=("Arial", 10, "bold"))
        mode_frame.grid(row=0, column=0, columnspan=2, sticky="we", pady=5)
        
        tk.Radiobutton(mode_frame, text="1. Thiếu Start (Belief State gồm 2 trạng thái xuất phát)", variable=self.mode_var, value=1, command=self.update_ui).pack(anchor="w")
        tk.Radiobutton(mode_frame, text="2. Thiếu Goal (Tạo tập gồm 2 Đích khả dĩ)", variable=self.mode_var, value=2, command=self.update_ui).pack(anchor="w")
        tk.Radiobutton(mode_frame, text="3. Mất một phần S và G (Auto-complete điền ô khuyết)", variable=self.mode_var, value=3, command=self.update_ui).pack(anchor="w")
        tk.Radiobutton(mode_frame, text="4. Hành động không rõ ràng (AND-OR Graph Search)", variable=self.mode_var, value=4, command=self.update_ui).pack(anchor="w")
        # --- LƯỚI INPUT ---
        input_frame = tk.Frame(left_frame)
        input_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        self.start_frame = tk.LabelFrame(input_frame, text="Start (* là khuyết)", fg="blue")
        self.start_frame.grid(row=0, column=0, padx=5)
        self.entries_start = []
        for i in range(9):
            e = tk.Entry(self.start_frame, width=3, font=("Arial", 14, "bold"), justify="center")
            e.grid(row=i//3, column=i%3, padx=2, pady=2)
            self.entries_start.append(e)

        self.goal_frame = tk.LabelFrame(input_frame, text="Goal (* là khuyết)", fg="red")
        self.goal_frame.grid(row=0, column=1, padx=5)
        self.entries_goal = []
        for i in range(9):
            e = tk.Entry(self.goal_frame, width=3, font=("Arial", 14, "bold"), justify="center")
            e.grid(row=i//3, column=i%3, padx=2, pady=2)
            self.entries_goal.append(e)

        # --- CHỌN THUẬT TOÁN ĐỂ GIẢI ---
        algo_frame = tk.Frame(left_frame)
        algo_frame.grid(row=2, column=0, columnspan=2, sticky="we", pady=5)
        
        tk.Label(algo_frame, text="Thuật toán:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=2)
        
        # BỔ SUNG ĐẦY ĐỦ CÁC THUẬT TOÁN LOCAL SEARCH VÀO DANH SÁCH
        danh_sach_thuat_toan = [
            "BFS", "DFS", "UCS", "Greedy", "A*", 
            "HC Simple", "HC Steepest", "HC Stochastic", 
            "HC Restart", "Beam Search", "Simulated Annealing"
        ]
        self.algo_combobox = ttk.Combobox(algo_frame, values=danh_sach_thuat_toan, state="readonly", width=18, font=("Arial", 11, "bold"))
        self.algo_combobox.current(4) # Mặc định chọn A*
        self.algo_combobox.grid(row=0, column=1, padx=5)

        tk.Button(algo_frame, text="Xử lý & Chạy", font=("Arial", 11, "bold"), bg="#ffc107", command=self.run_complex_mode).grid(row=0, column=2, padx=5, sticky="we")

        self.txt_log = scrolledtext.ScrolledText(left_frame, width=50, height=12, font=("Consolas", 10), bg="#f8f9fa")
        self.txt_log.grid(row=3, column=0, columnspan=2, pady=5)

        # --- BẢNG TRẠNG THÁI (TRACE TABLE) ---
        right_frame = tk.LabelFrame(self.top, text="BẢNG TRẠNG THÁI (TRACE TABLE)", font=("Arial", 10, "bold"))
        right_frame.grid(row=0, column=1, rowspan=4, padx=10, pady=10, sticky="nsew")
        self.txt_trace = tk.Text(right_frame, width=125, height=35, font=("Consolas", 10), bg="#1e1e1e", fg="#d4d4d4", borderwidth=0)
        
        y_scroll = tk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.txt_trace.yview)
        self.txt_trace.configure(yscrollcommand=y_scroll.set)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_trace.pack(fill=tk.BOTH, expand=True)

        self.update_ui()

    def update_ui(self):
        mode = self.mode_var.get()
        for e in self.entries_start + self.entries_goal:
            e.config(state=tk.NORMAL, fg="black")
            e.delete(0, tk.END)
            
        if mode == 1:
            for e in self.entries_start:
                e.insert(0, "*")
                e.config(state=tk.DISABLED, fg="gray")
            for i, val in enumerate([1,2,3,4,5,6,7,8,0]): self.entries_goal[i].insert(0, str(val))
        elif mode == 2:
            for i, val in enumerate([1,2,3,4,0,6,7,5,8]): self.entries_start[i].insert(0, str(val))
            for e in self.entries_goal:
                e.insert(0, "*")
                e.config(state=tk.DISABLED, fg="gray")
        else:
            for i, val in enumerate(["1","2","3","4","*","6","*","5","8"]): self.entries_start[i].insert(0, val)
            for i, val in enumerate(["1","2","3","*","5","6","7","*","0"]): self.entries_goal[i].insert(0, val)

    def get_input(self, entries):
        res = []
        for e in entries:
            val = e.get().strip()
            if val == "" or val == "*": res.append(-1)
            else: res.append(int(val))
        return res

    def generate_close_state(self, state, steps):
        curr = state
        for _ in range(steps):
            children = get_child(curr)
            curr, _ = random.choice(children)
        return curr

    def run_complex_mode(self):
        mode = self.mode_var.get()
        algo_choice = self.algo_combobox.get()
        self.current_algo_choice = algo_choice
        self.txt_log.delete('1.0', tk.END)
        self.label_mgr.reset_all()

        local_searches = ["HC Simple", "HC Steepest", "HC Stochastic", "HC Restart", "Beam Search", "Simulated Annealing"]

        # CẢNH BÁO THÔNG MINH NẾU CHỌN LOCAL SEARCH CHO MÔI TRƯỜNG TẬP NIỀM TIN
        if mode in [1, 2] and algo_choice in local_searches:
            messagebox.showinfo("Chuyển đổi Thuật toán", f"Bạn đang chọn {algo_choice} (Tìm kiếm cục bộ).\n\nThuật toán này chỉ hoạt động trên 1 trạng thái duy nhất. Môi trường 1 và 2 chứa Tập Niềm Tin (Nhiều trạng thái). Hệ thống sẽ tự động chuyển sang giải bằng A* để đảm bảo tính khả thi.")
            algo_choice = "A*"
            self.algo_combobox.set("A*")

        class BeliefNode:
            def __init__(self, bs, parent=None, action=None):
                self.bs = bs; self.parent = parent; self.action = action

        if mode == 1: # KHUYẾT START (BELIEF STATE)
            goal_in = tuple(self.get_input(self.entries_goal))
            S1 = self.generate_close_state(goal_in, 3)
            S2 = self.generate_close_state(goal_in, 4)
            while S2 == S1: S2 = self.generate_close_state(goal_in, 4)
            
            bs_initial = tuple(sorted([S1, S2]))
            self.txt_log.insert(tk.END, f"[TH1] KHUYẾT START\n- Sinh Belief State chứa 2 trạng thái:\n  S1: {S1}\n  S2: {S2}\n- Giải bằng thuật toán {algo_choice}...\n")
            
            def get_sensorless_transition(state, action):
                idx = state.index(0); r, c = divmod(idx, 3)
                moves = {"UP": (r-1, c), "DOWN": (r+1, c), "LEFT": (r, c-1), "RIGHT": (r, c+1)}
                if action in moves:
                    tr, tc = moves[action]
                    if 0 <= tr < 3 and 0 <= tc < 3:
                        new_s = list(state)
                        t_idx = tr * 3 + tc; new_s[idx], new_s[t_idx] = new_s[t_idx], new_s[idx]
                        return tuple(new_s)
                return state

            node = BeliefNode(bs_initial)
            node.g_cost = 0
            node.h_cost = min(manhattan_distance(s, goal_in) for s in node.bs)
            node.f_cost = node.g_cost + node.h_cost
            self.label_mgr.get_label(node.bs)
            frontier = [node]; reached = {node.bs}
            
            self.init_trace_table(algo_choice)
            self.trace_callback("START", node, [], list(frontier), self.label_mgr, list(reached), algo_choice)

            solution_node = None
            while frontier:
                if algo_choice == "BFS": node = frontier.pop(0)
                elif algo_choice == "DFS": node = frontier.pop(-1)
                elif algo_choice == "UCS": frontier.sort(key=lambda x: x.g_cost); node = frontier.pop(0)
                elif algo_choice == "Greedy": frontier.sort(key=lambda x: x.h_cost); node = frontier.pop(0)
                elif algo_choice == "A*": frontier.sort(key=lambda x: x.f_cost); node = frontier.pop(0)

                if len(node.bs) == 1 and node.bs[0] == goal_in:
                    solution_node = node
                    self.trace_callback(None, node, [], list(frontier), self.label_mgr, list(reached), algo_choice)
                    break
                
                new_nodes = []
                for act in ["UP", "DOWN", "LEFT", "RIGHT"]:
                    new_bs = set()
                    for state in node.bs: new_bs.add(get_sensorless_transition(state, act))
                    child_bs = tuple(sorted(list(new_bs)))
                    if child_bs not in reached:
                        child_node = BeliefNode(child_bs, node, act)
                        child_node.g_cost = node.g_cost + 1
                        child_node.h_cost = min(manhattan_distance(s, goal_in) for s in child_bs)
                        child_node.f_cost = child_node.g_cost + child_node.h_cost
                        
                        self.label_mgr.get_label(child_bs); frontier.append(child_node)
                        reached.add(child_bs); new_nodes.append(child_node)
                self.trace_callback(None, node, new_nodes, list(frontier), self.label_mgr, list(reached), algo_choice)

            if solution_node:
                path_acts = []
                curr = solution_node
                while curr.parent: path_acts.append(curr.action); curr = curr.parent
                path_acts.reverse()
                self.txt_log.insert(tk.END, f"\n=> TÌM THẤY CHUỖI ÉP BUỘC ĐẾN ĐÍCH:\n{path_acts}")

        elif mode == 2: # KHUYẾT GOAL (MULTI-GOAL)
            start_in = tuple(self.get_input(self.entries_start))
            G1 = self.generate_close_state(start_in, 4)
            G2 = self.generate_close_state(start_in, 4)
            while G2 == G1: G2 = self.generate_close_state(start_in, 4)
            targets = [G1, G2]
            
            self.txt_log.insert(tk.END, f"[TH2] KHUYẾT GOAL\n- Sinh Tập Đích khả dĩ:\n  G1: {G1}\n  G2: {G2}\n- Giải bằng thuật toán {algo_choice}...\n")
            
            node = Node(start_in)
            node.g_cost = 0
            node.h_cost = min(manhattan_distance(start_in, g) for g in targets)
            node.f_cost = node.g_cost + node.h_cost
            self.label_mgr.get_label(node.state)
            frontier = [node]; reached = {node.state}
            
            self.init_trace_table(algo_choice)
            self.trace_callback("START", node, [], list(frontier), self.label_mgr, list(reached), algo_choice)

            solution_node = None
            while frontier:
                if algo_choice == "BFS": node = frontier.pop(0)
                elif algo_choice == "DFS": node = frontier.pop(-1)
                elif algo_choice == "UCS": frontier.sort(key=lambda x: x.g_cost); node = frontier.pop(0)
                elif algo_choice == "Greedy": frontier.sort(key=lambda x: x.h_cost); node = frontier.pop(0)
                elif algo_choice == "A*": frontier.sort(key=lambda x: x.f_cost); node = frontier.pop(0)

                if node.state in targets:
                    solution_node = node
                    self.trace_callback(None, node, [], list(frontier), self.label_mgr, list(reached), algo_choice)
                    break
                    
                new_nodes = []
                for child_state, action in get_child(node.state):
                    if child_state not in reached:
                        child = Node(child_state, node, action)
                        child.g_cost = node.g_cost + 1
                        child.h_cost = min(manhattan_distance(child.state, g) for g in targets)
                        child.f_cost = child.g_cost + child.h_cost
                        
                        self.label_mgr.get_label(child.state); frontier.append(child)
                        reached.add(child_state); new_nodes.append(child)
                self.trace_callback(None, node, new_nodes, list(frontier), self.label_mgr, list(reached), algo_choice)

            if solution_node:
                self.txt_log.insert(tk.END, f"\n=> ĐÃ CHẠM ĐƯỢC 1 ĐÍCH TRONG TẬP KHẢ DĨ!\nĐích tìm thấy: {solution_node.state}")

        elif mode == 3: # MẤT MỘT PHẦN S VÀ G (GỌI TRỰC TIẾP HÀM GỐC)
            start_in = self.get_input(self.entries_start)
            goal_in = self.get_input(self.entries_goal)
            
            def fill_missing(state_in):
                actual_missing = [x for x in range(9) if x not in state_in]
                random.shuffle(actual_missing)
                res = []; idx = 0
                for v in state_in:
                    if v == -1: res.append(actual_missing[idx]); idx += 1
                    else: res.append(v)
                return res

            def count_inv(state_nums):
                inv = 0; lst = [x for x in state_nums if x != 0]
                for i in range(8):
                    for j in range(i+1, 8):
                        if lst[i] > lst[j]: inv += 1
                return inv

            success = False
            for _ in range(200):
                st = fill_missing(start_in); gl = fill_missing(goal_in)
                if (count_inv(st) % 2) == (count_inv(gl) % 2):
                    success = True; break
            
            if not success:
                messagebox.showerror("Vô nghiệm", "Không thể khôi phục chẵn lẻ hợp lệ. Đổi vị trí ô '*'!")
                return
                
            for i, e in enumerate(self.entries_start):
                e.delete(0, tk.END); e.insert(0, str(st[i]))
                if start_in[i] == -1: e.config(fg="purple")
            for i, e in enumerate(self.entries_goal):
                e.delete(0, tk.END); e.insert(0, str(gl[i]))
                if goal_in[i] == -1: e.config(fg="purple")

            self.txt_log.insert(tk.END, f"[TH3] MẤT MỘT PHẦN\n- Start: {st}\n- Goal: {gl}\n- Giải bằng {algo_choice}...\n")
            
            # ÁNH XẠ ĐẦY ĐỦ CÁC THUẬT TOÁN BAO GỒM CẢ LOCAL SEARCH
            algo_map = {
                "BFS": bfs_cach_1,
                "DFS": dfs_cach_1,
                "UCS": UCS_search,
                "Greedy": Greedy_Search,
                "A*": AStar_Search,
                "HC Simple": hill_climbing_simple,
                "HC Steepest": hill_climbing_steepest,
                "HC Stochastic": hill_climbing_stochastic,
                "HC Restart": hill_climbing_random_restart,
                "Beam Search": local_beam_search,
                "Simulated Annealing": simulated_annealing
            }
            
            self.init_trace_table(algo_choice)
            selected_function = algo_map.get(algo_choice, AStar_Search)
            
            try:
                # Trỏ callback về trace_callback_original để đảm bảo in đúng chuẩn cho tất cả
                selected_function(tuple(st), tuple(gl), self.trace_callback_original, self.label_mgr)
                self.txt_log.insert(tk.END, f"\n=> GIẢI QUYẾT THÀNH CÔNG BẰNG {algo_choice}!")
            except InterruptedError:
                pass

        elif mode == 4: # AND-OR GRAPH SEARCH
            start_in = tuple(self.get_input(self.entries_start))
            goal_in = tuple(self.get_input(self.entries_goal))
            
            if -1 in start_in or -1 in goal_in:
                messagebox.showerror("Lỗi", "Chế độ này yêu cầu nhập đầy đủ Start và Goal (không chứa '*').")
                return

            self.txt_log.insert(tk.END, "[TH4] MÔI TRƯỜNG HÀNH ĐỘNG KHÔNG RÕ RÀNG\n")
            self.txt_log.insert(tk.END, "- Giả lập: Khi trượt một ô, có khả năng ô đó bị kẹt và không di chuyển.\n")
            self.txt_log.insert(tk.END, "- Đang duyệt cây AND-OR để lập Kế hoạch dự phòng...\n\n")
            self.top.update()

            plan = and_or_graph_search(start_in, goal_state=goal_in, max_depth=5)
            
            self.txt_trace.delete('1.0', tk.END)
            self.txt_trace.insert(tk.END, "=== KẾ HOẠCH DỰ PHÒNG (CONTINGENCY PLAN) ===\n\n", "header")
            
            import pprint
            if plan == 'failure':
                self.txt_trace.insert(tk.END, "Thất bại: Không thể lập kế hoạch chắc chắn đạt đích trong giới hạn độ sâu (Tránh tràn RAM do nhánh AND quá lớn).", "dash")
            else:
                formatted_plan = pprint.pformat(plan, indent=4, width=80)
                self.txt_trace.insert(tk.END, formatted_plan, "purple")
                self.txt_log.insert(tk.END, "=> LẬP KẾ HOẠCH THÀNH CÔNG! (Xem chi tiết trên bảng)")

    # --- KHU VỰC VẼ TRACE TABLE ĐA DỤNG ---
    def init_trace_table(self, algo_choice):
        self.txt_trace.delete('1.0', tk.END)
        self.txt_trace.tag_configure("header", foreground="#5CE1E6", font=("Consolas", 10, "bold"))
        self.txt_trace.tag_configure("dash", foreground="#5C6370")
        
        self.w1 = 12; self.w2 = 80; self.w3 = 25 
        self.txt_trace.insert(tk.END, f"{'NODE'.center(self.w1)}|{'FRONTIER (FORMAT PHẲNG)'.center(self.w2)}|{'REACHED'.center(self.w3)}\n", "header")
        self.sep_line = "-" * self.w1 + "+" + "-" * self.w2 + "+" + "-" * self.w3
        self.txt_trace.insert(tk.END, self.sep_line + "\n", "dash")

    def trace_callback(self, label_evt, current_node, new_nodes, frontier_nodes, label_mgr, reached, algo_choice):
        try:
            # Kiểm tra xem cửa sổ còn tồn tại không, nếu đã bị đóng thì báo lỗi để ép ngắt thuật toán
            if not self.top.winfo_exists():
                raise InterruptedError()
                
            def pad(text, width): return text[:width].ljust(width)
            if label_evt:
                self.txt_trace.insert(tk.END, f" {label_evt.upper()} ".center(self.w1+self.w2+self.w3+2, "-") + "\n", "dash")

            col1_state = current_node.bs if hasattr(current_node, 'bs') else current_node.state if current_node else None
            col1 = f" [{label_mgr.get_label(col1_state)}]" if col1_state else ""
            col3_wrapped = textwrap.wrap("[" + ", ".join([label_mgr.get_label(s) for s in reached]) + "]", self.w3 - 2)

            frontier_lines = []
            for n in new_nodes:
                state_val = n.bs if hasattr(n, 'bs') else n.state
                lbl = label_mgr.get_label(state_val)
                p_val = n.parent.bs if hasattr(n.parent, 'bs') else n.parent.state if n.parent else None
                p_lbl = label_mgr.get_label(p_val) if p_val else "-"
                
                cost = ""
                if algo_choice == "A*": cost = f",f={getattr(n, 'f_cost', '?')}"
                elif algo_choice in ["Greedy", "HC Simple", "HC Steepest", "HC Stochastic", "HC Restart", "Beam Search", "Simulated Annealing"]: 
                    cost = f",h={getattr(n, 'h_cost', '?')}"
                elif algo_choice == "UCS": cost = f",g={getattr(n, 'g_cost', '?')}"
                
                if hasattr(n, 'bs'):
                    state_str = "{" + ", ".join([f"[{s[0]}{s[1]}{s[2]}/{s[3]}{s[4]}{s[5]}/{s[6]}{s[7]}{s[8]}]" for s in n.bs]) + "}"
                else:
                    s = n.state
                    state_str = f"[{s[0]}{s[1]}{s[2]}/{s[3]}{s[4]}{s[5]}/{s[6]}{s[7]}{s[8]}]"
                    
                line = f"{state_str}, {p_lbl}, {n.action or '-'}{cost} = {lbl}"
                frontier_lines.extend(textwrap.wrap(line, self.w2 - 2))

            max_lines = max(1, len(frontier_lines), len(col3_wrapped))
            for i in range(max_lines):
                c1 = col1 if i == 0 else ""; c2 = frontier_lines[i] if i < len(frontier_lines) else ""; c3 = col3_wrapped[i] if i < len(col3_wrapped) else ""
                self.txt_trace.insert(tk.END, f"{pad(c1, self.w1)}|", "dash")
                self.txt_trace.insert(tk.END, pad(" " + c2, self.w2) + "|", "dash")
                self.txt_trace.insert(tk.END, pad(" " + c3, self.w3) + "\n")
            self.txt_trace.insert(tk.END, self.sep_line + "\n", "dash")
            self.txt_trace.see(tk.END)
            self.top.update()
            
        except tk.TclError:
            raise InterruptedError()

    # Callback phụ dành riêng cho chế độ 3 (Gọi hàm nguyên bản)
    def trace_callback_original(self, label_evt, current_node, new_nodes, frontier_nodes, label_mgr, reached=None):
        try:
            if not self.top.winfo_exists():
                raise InterruptedError()
            
            # SỬ DỤNG BIẾN ĐÃ CACHE TRƯỚC ĐÓ THAY VÌ GỌI GUI COMBOBOX
            algo_choice = self.current_algo_choice
            reached_list = reached if reached is not None else [s for s in label_mgr.mapping.keys()]
            self.trace_callback(label_evt, current_node, new_nodes, frontier_nodes, label_mgr, reached_list, algo_choice)
            
        except tk.TclError:
            raise InterruptedError()
# =====================================================================
# NHÓM 5: CONSTRAINT SATISFACTION PROBLEM (CSP) ÁP DỤNG LÊN 8-PUZZLE
# =====================================================================
class CSP_8Puzzle_UI:
    def __init__(self, root):
        self.top = tk.Toplevel(root)
        self.top.title("Nhóm 5: Thỏa mãn ràng buộc (CSP) - 8 Puzzle")
        self.top.geometry("950x700")

        tk.Label(self.top, text="CSP 8-PUZZLE: ĐIỀN SỐ THỎA MÃN RÀNG BUỘC", font=("Arial", 14, "bold"), fg="#d9534f").pack(pady=10)

        main_frame = tk.Frame(self.top)
        main_frame.pack(fill="both", expand=True, padx=20)

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side="left", fill="y", padx=10)

        # 1. Grid 3x3 cho Start State (Unary Constraints)
        grid_frame = tk.LabelFrame(left_frame, text="Ma trận 8-Puzzle (X0 đến X8)", font=("Arial", 10, "bold"), fg="blue")
        grid_frame.pack(pady=10)
        
        tk.Label(grid_frame, text="Nhập số (0-8) để cố định, hoặc '*' để máy tự tìm:", font=("Arial", 9, "italic")).grid(row=0, column=0, columnspan=3)
        self.entries = []
        for i in range(9):
            e = tk.Entry(grid_frame, width=4, font=("Arial", 16, "bold"), justify="center")
            e.insert(0, "*")
            e.grid(row=(i//3)+1, column=(i%3), padx=5, pady=5)
            # Thêm nhãn X0, X1 mờ ở góc để dễ nhìn
            tk.Label(grid_frame, text=f"X{i}", font=("Arial", 7), fg="gray").grid(row=(i//3)+1, column=(i%3), sticky="se")
            self.entries.append(e)

        # 2. Ràng buộc bổ sung
        constraint_frame = tk.LabelFrame(left_frame, text="Ràng buộc bổ sung (Custom Constraints)", font=("Arial", 10, "bold"))
        constraint_frame.pack(fill="x", pady=5)
        tk.Label(constraint_frame, text="Ví dụ: X0 != X1, X2 + X3 == 5, X4 == 0", font=("Arial", 9)).pack()
        self.txt_constraints = tk.Entry(constraint_frame, font=("Consolas", 11), width=35)
        self.txt_constraints.pack(padx=10, pady=5)

        # 3. Chọn thuật toán
        algo_frame = tk.Frame(left_frame)
        algo_frame.pack(pady=10)
        tk.Label(algo_frame, text="Thuật toán:").pack(side="left")
        self.algo_combo = ttk.Combobox(algo_frame, values=["Backtracking", "AC-3", "Min-Conflicts"], state="readonly", width=15)
        self.algo_combo.current(0)
        self.algo_combo.pack(side="left", padx=5)

        tk.Button(left_frame, text="Giải CSP", font=("Arial", 12, "bold"), bg="#5cb85c", fg="white", command=self.run_csp).pack(pady=10, fill="x")

        # 4. Log hiển thị
        right_frame = tk.LabelFrame(main_frame, text="Tiến trình Giải (Log Trace)", font=("Arial", 10, "bold"))
        right_frame.pack(side="right", fill="both", expand=True)
        self.txt_log = scrolledtext.ScrolledText(right_frame, font=("Consolas", 10), bg="#1e1e1e", fg="#d4d4d4")
        self.txt_log.pack(fill="both", expand=True, padx=5, pady=5)

    def parse_input(self):
        self.variables = [f"X{i}" for i in range(9)]
        self.domains = {v: list(range(9)) for v in self.variables}
        self.assignment = {}
        
        # Đọc Unary Constraints (Các ô người dùng nhập số)
        for i, e in enumerate(self.entries):
            val = e.get().strip()
            if val != "*":
                try:
                    num = int(val)
                    if 0 <= num <= 8:
                        self.domains[f"X{i}"] = [num]
                        self.assignment[f"X{i}"] = num
                    else:
                        raise ValueError
                except:
                    messagebox.showerror("Lỗi", f"Ô X{i} phải là số từ 0-8 hoặc '*'")
                    return False

        # Đọc Custom Constraints
        c_str = self.txt_constraints.get().strip()
        self.custom_constraints = [c.strip() for c in c_str.split(',') if c.strip()]
        return True

    def eval_custom_constraints(self, assign):
        if not self.custom_constraints: return True
        # Chỉ kiểm tra khi biến đã được gán
        locs = {v: assign[v] for v in assign}
        for c in self.custom_constraints:
            # Bỏ qua nếu constraint chứa biến chưa được gán
            if any(v in c and v not in locs for v in self.variables):
                continue
            try:
                if not eval(c, {}, locs): return False
            except:
                pass # Lỗi cú pháp tạm bỏ qua
        return True

    def is_consistent(self, var, val, assign):
        # Ràng buộc mặc định (AllDiff): Mỗi ô 1 số từ 0-8
        for k, v in assign.items():
            if v == val: return False
        
        temp_assign = dict(assign)
        temp_assign[var] = val
        return self.eval_custom_constraints(temp_assign)

    def backtrack(self, assign):
        if not self.top.winfo_exists(): raise InterruptedError()
        if len(assign) == 9: return assign

        var = [v for v in self.variables if v not in assign][0]
        self.txt_log.insert(tk.END, f"-> Chọn biến {var}. Thử giá trị...\n")

        for val in self.domains[var]:
            if self.is_consistent(var, val, assign):
                self.txt_log.insert(tk.END, f"   [+] {var}={val} (Hợp lệ AllDiff & Ràng buộc)\n")
                assign[var] = val
                res = self.backtrack(assign)
                if res: return res
                del assign[var]
            else:
                self.txt_log.insert(tk.END, f"   [-] {var}={val} (Vi phạm ràng buộc)\n")
        return None

    def run_ac3(self):
        # Lọc miền giá trị (Forward Checking & Arc Consistency thu gọn)
        queue = deque([(f"X{i}", f"X{j}") for i in range(9) for j in range(9) if i != j])
        domains = dict(self.domains)

        def remove_inconsistent(xi, xj):
            removed = False
            for x in list(domains[xi]):
                if not any(x != y for y in domains[xj]): # AllDiff constraint
                    domains[xi].remove(x)
                    removed = True
            return removed

        self.txt_log.insert(tk.END, "=== AC-3 KHỞI CHẠY (LỌC MIỀN GIÁ TRỊ) ===\n")
        while queue:
            xi, xj = queue.popleft()
            if remove_inconsistent(xi, xj):
                self.txt_log.insert(tk.END, f"Loại giá trị không hợp lệ khỏi miền {xi} do ràng buộc AllDiff với {xj}.\n")
                self.txt_log.insert(tk.END, f"-> Domain({xi}) = {domains[xi]}\n")
                if not domains[xi]: return False, domains
                for xk in range(9):
                    if xk != int(xi[1]) and xk != int(xj[1]):
                        queue.append((f"X{xk}", xi))
        return True, domains

    def run_min_conflicts(self, max_steps=1000):
        # Bắt đầu với hoán vị ngẫu nhiên 0-8 để luôn thõa mãn AllDiff
        vals = list(range(9))
        random.shuffle(vals)
        current = {f"X{i}": vals[i] for i in range(9)}
        
        # Cố định các Unary Constraint do user nhập
        for k, v in self.assignment.items(): current[k] = v

        def count_conflicts(assign):
            c = 0
            # Conflict AllDiff
            v_list = list(assign.values())
            c += len(v_list) - len(set(v_list))
            # Conflict Custom
            locs = {v: assign[v] for v in assign}
            for constr in self.custom_constraints:
                try:
                    if not eval(constr, {}, locs): c += 1
                except: c += 1
            return c

        self.txt_log.insert(tk.END, f"Khởi tạo ngẫu nhiên: {list(current.values())}\n")
        
        for step in range(max_steps):
            if count_conflicts(current) == 0:
                self.txt_log.insert(tk.END, f"=> Đã giải quyết xong mọi xung đột tại bước {step}!\n")
                return current
            
            # Chọn ngẫu nhiên 1 biến để đổi giá trị
            var = random.choice(self.variables)
            best_val = current[var]
            min_c = count_conflicts(current)

            for val in range(9):
                temp = dict(current)
                temp[var] = val
                c = count_conflicts(temp)
                if c < min_c:
                    min_c = c
                    best_val = val
            
            if current[var] != best_val:
                self.txt_log.insert(tk.END, f"B{step}: Gán {var}={best_val} để giảm thiểu xung đột (Số Xung đột={min_c}).\n")
                current[var] = best_val

        self.txt_log.insert(tk.END, "Thất bại: Chạm giới hạn Min-Conflicts.\n")
        return None

    def run_csp(self):
        if not self.parse_input(): return
        self.txt_log.delete('1.0', tk.END)
        algo = self.algo_combo.get()

        try:
            if algo == "Backtracking":
                self.txt_log.insert(tk.END, f"BẮT ĐẦU BACKTRACKING...\n\n")
                sol = self.backtrack(dict(self.assignment))
            
            elif algo == "AC-3":
                success, d = self.run_ac3()
                if success:
                    self.txt_log.insert(tk.END, "\n=> MIỀN SAU KHI LỌC AC-3:\n")
                    for k, v in d.items(): self.txt_log.insert(tk.END, f"{k}: {v}\n")
                    self.txt_log.insert(tk.END, "\n-> Kết hợp Backtrack để giải tiếp...\n")
                    self.domains = d # Cập nhật domain đã lọc
                    sol = self.backtrack(dict(self.assignment))
                else: sol = None

            elif algo == "Min-Conflicts":
                self.txt_log.insert(tk.END, f"BẮT ĐẦU MIN-CONFLICTS...\n\n")
                sol = self.run_min_conflicts()

            if sol:
                self.txt_log.insert(tk.END, f"\n🎉 TÌM THẤY NGHIỆM CSP:\n{sol}\n")
                # Hiển thị lên UI
                for i in range(9):
                    self.entries[i].delete(0, tk.END)
                    self.entries[i].insert(0, str(sol[f"X{i}"]))
                    self.entries[i].config(fg="green")
            else:
                self.txt_log.insert(tk.END, "\n❌ Không tìm thấy cấu hình thỏa mãn ràng buộc!\n")
        except InterruptedError:
            pass

# =====================================================================
# NHÓM 6: ADVERSARIAL SEARCH (TÌM KIẾM ĐỐI KHÁNG - CARO 3x3)
# =====================================================================
class Caro_UI:
    def __init__(self, root):
        self.top = tk.Toplevel(root)
        self.top.title("Nhóm 6: Tìm kiếm Đối kháng (Caro 3x3)")
        self.top.geometry("850x580")

        self.board = [' '] * 9
        self.human_marker = 'X'
        self.ai_marker = 'O'
        
        tk.Label(self.top, text="TRÍ TUỆ NHÂN TẠO CHƠI CARO (TIC-TAC-TOE)", font=("Arial", 14, "bold"), fg="#17a2b8").pack(pady=10)

        main_frame = tk.Frame(self.top)
        main_frame.pack(fill="both", expand=True, padx=20)

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side="left", padx=10, fill="y")

        # --- KHUNG CÀI ĐẶT TRÒ CHƠI ---
        cfg_frame = tk.LabelFrame(left_frame, text="Cài đặt trò chơi", font=("Arial", 10, "bold"))
        cfg_frame.pack(pady=5, fill="x")
        
        tk.Label(cfg_frame, text="Thuật toán:").grid(row=0, column=0, sticky="e", padx=2, pady=5)
        self.algo_combo = ttk.Combobox(cfg_frame, values=["Minimax", "Alpha-Beta Pruning", "Expectimax"], state="readonly", width=16)
        self.algo_combo.current(1)
        self.algo_combo.grid(row=0, column=1, columnspan=3, padx=2, sticky="w")

        tk.Label(cfg_frame, text="Bạn là:").grid(row=1, column=0, sticky="e", padx=2, pady=5)
        self.symbol_combo = ttk.Combobox(cfg_frame, values=["X", "O"], state="readonly", width=5)
        self.symbol_combo.current(0)
        self.symbol_combo.grid(row=1, column=1, padx=2, sticky="w")

        tk.Label(cfg_frame, text="Đi trước:").grid(row=1, column=2, sticky="e", padx=2, pady=5)
        self.first_turn_combo = ttk.Combobox(cfg_frame, values=["Người", "AI"], state="readonly", width=7)
        self.first_turn_combo.current(0)
        self.first_turn_combo.grid(row=1, column=3, padx=2, sticky="w")

        tk.Button(cfg_frame, text="Làm mới (Chơi lại)", font=("Arial", 10, "bold"), bg="#ffc107", command=self.reset_game).grid(row=2, column=0, columnspan=4, pady=5, padx=10, sticky="we")

        # --- LƯỚI CARO 3X3 ---
        self.buttons = []
        grid_frame = tk.Frame(left_frame, bg="black")
        grid_frame.pack(pady=10)
        for i in range(9):
            btn = tk.Button(grid_frame, text=" ", font=("Arial", 28, "bold"), width=3, height=1,
                            command=lambda idx=i: self.human_move(idx))
            btn.grid(row=i//3, column=i%3, padx=1, pady=1)
            self.buttons.append(btn)

        # --- LOG TIẾN TRÌNH ---
        right_frame = tk.LabelFrame(main_frame, text="Cây Suy Nghĩ của AI", font=("Arial", 10, "bold"))
        right_frame.pack(side="right", fill="both", expand=True)
        self.txt_log = scrolledtext.ScrolledText(right_frame, font=("Consolas", 10), bg="#2d2d2d", fg="#61afef")
        self.txt_log.pack(fill="both", expand=True, padx=5, pady=5)

        # --- GÁN SỰ KIỆN VÀ KHỞI TẠO (Bắt buộc để ở cuối cùng) ---
        self.symbol_combo.bind("<<ComboboxSelected>>", lambda e: self.reset_game())
        self.first_turn_combo.bind("<<ComboboxSelected>>", lambda e: self.reset_game())
        self.reset_game()

    def reset_game(self):
        self.board = [' '] * 9
        for btn in self.buttons:
            btn.config(text=" ", state=tk.NORMAL, fg="black")
        self.txt_log.delete('1.0', tk.END)
        
        self.human_marker = self.symbol_combo.get()
        self.ai_marker = 'O' if self.human_marker == 'X' else 'X'
        
        self.txt_log.insert(tk.END, f"--- VÁN MỚI ---\nBạn: {self.human_marker} | AI: {self.ai_marker}\n")
        
        if self.first_turn_combo.get() == "AI":
            self.txt_log.insert(tk.END, "AI được quyền đi trước...\n")
            self.top.update() 
            self.ai_move()

    def check_winner(self, board, player):
        win_cond = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        for a, b, c in win_cond:
            if board[a] == board[b] == board[c] == player:
                return True
        return False

    def human_move(self, idx):
        if self.board[idx] == ' ':
            self.board[idx] = self.human_marker
            self.buttons[idx].config(text=self.human_marker, fg="blue")
            
            if self.check_winner(self.board, self.human_marker):
                messagebox.showinfo("Kết thúc", "Bạn đã thắng!")
                self.disable_all()
                return
            elif ' ' not in self.board:
                messagebox.showinfo("Kết thúc", "Hòa!")
                return
            
            self.disable_all()
            self.top.update()
            self.ai_move()
            
            for i in range(9):
                if self.board[i] == ' ':
                    self.buttons[i].config(state=tk.NORMAL)

    def ai_move(self):
        if not self.top.winfo_exists(): return
        
        algo = self.algo_combo.get()
        self.nodes_evaluated = 0
        self.prunes = 0

        self.txt_log.insert(tk.END, f"\n=== Lượt của AI ({algo}) ===\n")
        self.txt_log.insert(tk.END, "Đang duyệt cây suy nghĩ...\n")
        self.top.update() 
        
        best_score = -float('inf')
        best_move = -1
        
        for i in range(9):
            if self.board[i] == ' ':
                self.board[i] = self.ai_marker
                if algo == "Minimax":
                    score = self.minimax(self.board, 0, False)
                elif algo == "Alpha-Beta Pruning":
                    score = self.alphabeta(self.board, 0, -float('inf'), float('inf'), False)
                else: # Expectimax
                    score = self.expectimax(self.board, 0, False)
                    
                self.board[i] = ' '
                self.txt_log.insert(tk.END, f"Thử nước đi ở ô {i} -> Điểm: {score:.2f}\n")
                self.top.update() 
                
                if score > best_score:
                    best_score = score
                    best_move = i

        self.txt_log.insert(tk.END, f"-> AI chốt đánh ô {best_move} (Điểm tối ưu: {best_score:.2f})\n")
        self.txt_log.insert(tk.END, f"-> Số Node đã duyệt: {self.nodes_evaluated}\n")
        if algo == "Alpha-Beta Pruning":
            self.txt_log.insert(tk.END, f"-> Cắt tỉa (Pruning) được: {self.prunes} nhánh\n")
        self.txt_log.see(tk.END)

        if best_move != -1:
            self.board[best_move] = self.ai_marker
            self.buttons[best_move].config(text=self.ai_marker, fg="red", state=tk.DISABLED)
            
            if self.check_winner(self.board, self.ai_marker):
                messagebox.showinfo("Kết thúc", "AI đã thắng!")
                self.disable_all()
            elif ' ' not in self.board:
                messagebox.showinfo("Kết thúc", "Hòa!")

    def minimax(self, board, depth, is_max):
        self.nodes_evaluated += 1
        if self.check_winner(board, self.ai_marker): return 10 - depth
        if self.check_winner(board, self.human_marker): return -10 + depth
        if ' ' not in board: return 0

        if is_max:
            best = -float('inf')
            for i in range(9):
                if board[i] == ' ':
                    board[i] = self.ai_marker
                    best = max(best, self.minimax(board, depth+1, False))
                    board[i] = ' '
            return best
        else:
            best = float('inf')
            for i in range(9):
                if board[i] == ' ':
                    board[i] = self.human_marker
                    best = min(best, self.minimax(board, depth+1, True))
                    board[i] = ' '
            return best

    def alphabeta(self, board, depth, alpha, beta, is_max):
        self.nodes_evaluated += 1
        if self.check_winner(board, self.ai_marker): return 10 - depth
        if self.check_winner(board, self.human_marker): return -10 + depth
        if ' ' not in board: return 0

        if is_max:
            best = -float('inf')
            for i in range(9):
                if board[i] == ' ':
                    board[i] = self.ai_marker
                    best = max(best, self.alphabeta(board, depth+1, alpha, beta, False))
                    board[i] = ' '
                    alpha = max(alpha, best)
                    if beta <= alpha:
                        self.prunes += 1
                        break
            return best
        else:
            best = float('inf')
            for i in range(9):
                if board[i] == ' ':
                    board[i] = self.human_marker
                    best = min(best, self.alphabeta(board, depth+1, alpha, beta, True))
                    board[i] = ' '
                    beta = min(beta, best)
                    if beta <= alpha:
                        self.prunes += 1
                        break
            return best

    def expectimax(self, board, depth, is_max):
        self.nodes_evaluated += 1
        if self.check_winner(board, self.ai_marker): return 10 - depth
        if self.check_winner(board, self.human_marker): return -10 + depth
        if ' ' not in board: return 0

        if is_max:
            best = -float('inf')
            for i in range(9):
                if board[i] == ' ':
                    board[i] = self.ai_marker
                    best = max(best, self.expectimax(board, depth+1, False))
                    board[i] = ' '
            return best
        else:
            scores = []
            for i in range(9):
                if board[i] == ' ':
                    board[i] = self.human_marker
                    scores.append(self.expectimax(board, depth+1, True))
                    board[i] = ' '
            return sum(scores) / len(scores)

    def disable_all(self):
        for btn in self.buttons: btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleUI(root)
    root.mainloop()