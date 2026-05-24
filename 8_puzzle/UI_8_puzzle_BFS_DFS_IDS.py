import tkinter as tk
from tkinter import scrolledtext
import time
from collections import deque
import textwrap
from tkinter import messagebox

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
        # Đã cập nhật: Đếm TẤT CẢ các ô khác nhau (tính cả ô trống 0)
        if state[i] != goal_state[i]:
            count += 1
    return count

# --- HÀM HEURISTIC 2: Khoảng cách Manhattan (Dùng cho Greedy) ---
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

# --- THUẬT TOÁN TÌM KIẾM CƠ BẢN ---
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

# --- THUẬT TOÁN UCS (Cộng dồn chi phí cha) ---
def UCS_search(initial_state, goal_state, callback, label_mgr):
    label_mgr.reset_all()
    node = Node(initial_state)
    
    node.f_cost = uncorrect(initial_state, goal_state)
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
            child.f_cost = node.f_cost + uncorrect(child_state, goal_state)
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

# --- THUẬT TOÁN GREEDY SEARCH (Tham lam) - Dùng Manhattan ---
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

# --- GIAO DIỆN ĐỒ HỌA ---
class SimpleUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-puzzle - Trace Table (Chuẩn Ghi Chép Vở)")

        self.start_state = (1,2,3,4,0,6,7,5,8)
        self.goal_state = (1,2,3,4,5,6,7,8,0)
        self.label_mgr = LabelManager()

        self.solution_path = []
        self.current_step = 0
        self.is_playing = False

        left_frame = tk.Frame(root)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        self.buttons = []
        for i in range(9):
            btn = tk.Button(left_frame, font=("Arial", 24, "bold"), width=4, height=1)
            row, col = divmod(i, 3)
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.buttons.append(btn)

        input_frame = tk.LabelFrame(left_frame, text="Nhập trạng thái (0-8, 0 là ô trống)", font=("Arial", 9, "bold"))
        input_frame.grid(row=3, column=0, columnspan=3, sticky="we", pady=5)
        
        start_frame = tk.Frame(input_frame)
        start_frame.grid(row=0, column=0, padx=5, pady=5)
        tk.Label(start_frame, text="Bắt đầu:", font=("Arial", 9, "bold"), fg="blue").grid(row=0, column=0, columnspan=3)
        
        self.entries_start = []
        default_start = [1, 2, 3, 4, 0, 6, 7, 5, 8]
        for i in range(9):
            e = tk.Entry(start_frame, width=3, font=("Arial", 14, "bold"), justify="center")
            e.insert(0, str(default_start[i]))
            e.grid(row=(i//3)+1, column=(i%3), padx=2, pady=2)
            self.entries_start.append(e)

        goal_frame = tk.Frame(input_frame)
        goal_frame.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(goal_frame, text="Đích:", font=("Arial", 9, "bold"), fg="red").grid(row=0, column=0, columnspan=3)
        
        self.entries_goal = []
        default_goal = [1, 2, 3, 4, 5, 6, 7, 8, 0]
        for i in range(9):
            e = tk.Entry(goal_frame, width=3, font=("Arial", 14, "bold"), justify="center")
            e.insert(0, str(default_goal[i]))
            e.grid(row=(i//3)+1, column=(i%3), padx=2, pady=2)
            self.entries_goal.append(e)
        
        tk.Button(input_frame, text="Cập\nnhật", font=("Arial", 10, "bold"), bg="#5cb85c", fg="white", 
                  command=self.apply_input).grid(row=0, column=2, padx=5, pady=5, sticky="ns")

        tk.Button(left_frame, text="BFS 1", font=("Arial", 11), command=lambda: self.run_algo(bfs_cach_1)).grid(row=4, column=0, sticky="we", padx=1, pady=2)
        tk.Button(left_frame, text="BFS 2", font=("Arial", 11), command=lambda: self.run_algo(bfs_cach_2)).grid(row=4, column=1, sticky="we", padx=1, pady=2)
        tk.Button(left_frame, text="DFS 1", font=("Arial", 11), command=lambda: self.run_algo(dfs_cach_1)).grid(row=4, column=2, sticky="we", padx=1, pady=2)
        
        tk.Button(left_frame, text="DFS 2", font=("Arial", 11), command=lambda: self.run_algo(dfs_cach_2)).grid(row=5, column=0, sticky="we", padx=1, pady=2)
        tk.Button(left_frame, text="UCS / A*", font=("Arial", 11, "bold"), bg="#d1ecf1", command=lambda: self.run_algo(UCS_search)).grid(row=5, column=1, sticky="we", padx=1, pady=2)
        tk.Button(left_frame, text="Greedy", font=("Arial", 11, "bold"), bg="#d1ecf1", command=lambda: self.run_algo(Greedy_Search)).grid(row=5, column=2, sticky="we", padx=1, pady=2)
        
        tk.Button(left_frame, text="Giải bằng IDS", font=("Arial", 12, "bold"), bg="#fff3cd", command=lambda: self.run_algo(IDS)).grid(row=6, column=0, columnspan=3, sticky="we", pady=5)
        
        tk.Button(left_frame, text="Reset", font=("Arial", 12, "bold"), fg="white", bg="#d9534f", command=self.reset).grid(row=7, column=0, columnspan=3, sticky="we", pady=5)
        self.cancel_algo = False
        
        play_frame = tk.LabelFrame(left_frame, text="Điều khiển xem bước", font=("Arial", 10, "bold"), fg="purple")
        play_frame.grid(row=8, column=0, columnspan=3, sticky="we", pady=5)
        self.btn_prev = tk.Button(play_frame, text="<", state=tk.DISABLED, width=3, command=self.prev_step)
        self.btn_prev.grid(row=0, column=0, padx=2, pady=5)
        self.btn_play = tk.Button(play_frame, text="Tự động", state=tk.DISABLED, width=10, command=self.toggle_play)
        self.btn_play.grid(row=0, column=1, padx=2, pady=5)
        self.btn_next = tk.Button(play_frame, text=">", state=tk.DISABLED, width=3, command=self.next_step)
        self.btn_next.grid(row=0, column=2, padx=2, pady=5)

        self.txt_log = scrolledtext.ScrolledText(left_frame, width=42, height=8, font=("Consolas", 10), bg="#f8f9fa")
        self.txt_log.grid(row=9, column=0, columnspan=3, pady=10, sticky="we")

        tk.Button(left_frame, text="Thoát", font=("Arial", 12, "bold"), fg="white", bg="red", command=self.exit).grid(row=10, column=0, columnspan=3, sticky="we")

        right_frame = tk.LabelFrame(root, text="BẢNG TRẠNG THÁI TIẾN TRÌNH", font=("Arial", 12, "bold"), padx=10, pady=10)
        right_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        self.txt_trace = tk.Text(right_frame, width=120, height=45, font=("Consolas", 10), wrap="none", bg="#1e1e1e", fg="#d4d4d4", borderwidth=0)
        
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

        self.w1 = 16 
        self.w2 = 62
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
                
                if hasattr(n, 'f_cost'):
                    cost = f"f={n.f_cost}"
                elif hasattr(n, 'h_cost'):
                    cost = f"h={n.h_cost}"
                else:
                    cost = str(n.depth)

                lbl = label_mgr.get_label(n.state)

                l1 = f"{{[{s[0]} {s[1]} {s[2]}]"
                l2 = f" [{s[3]} {s[4]} {s[5]}],{p_lbl},{act},{cost}}}={lbl}"
                l3 = f" [{s[6]} {s[7]} {s[8]}]"

                p_lines[0] += pad(l1, 30)
                p_lines[1] += pad(l2, 30)
                p_lines[2] += pad(l3, 30)
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

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleUI(root)
    root.mainloop()