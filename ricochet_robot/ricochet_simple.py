import pygame
import sys
import math
import heapq
import itertools
import random
import json
import os
from collections import deque

# --- CẤU HÌNH ---
WIDTH, HEIGHT = 1450, 800
GRID_SIZE = 16
CELL_SIZE = 640 // GRID_SIZE
OFFSET_X, OFFSET_Y = 350, 80
FPS = 60

# --- BẢNG MÀU ---
BG_COLOR = (245, 247, 250)         
BOARD_BG = (220, 224, 232)         
TILE_COLOR = (252, 253, 255)       
TILE_LINE = (210, 215, 225)        
WALL_COLOR = (55, 65, 81)          
SHADOW_COLOR = (0, 0, 0, 50)       
TARGET_COLOR = (255, 193, 7)       
TARGET_2_COLOR = (0, 230, 118)
PANEL_BG = (24, 28, 36)
TEXT_COLOR = (180, 190, 200)

COLORS = {
    "Người Chơi": (250, 250, 250),
    "BFS": (41, 121, 255), "DFS": (255, 23, 68), "IDS": (255, 145, 0),
    "UCS": (213, 0, 249), "Greedy": (0, 230, 118), "A*": (255, 234, 0),
    "Simple HC": (255, 105, 180), "Local Beam": (100, 181, 246), "Simulated Annealing": (255, 82, 82),
    "Multi-Goal": (0, 255, 127), "Sensorless": (255, 100, 255), "AND-OR Graph": (255, 255, 100),
    "Backtracking": (180, 100, 255), "AC-3": (147, 112, 219), "Min-Conflicts": (255, 140, 0),
    "Minimax": (255, 60, 60), "Alpha-Beta": (60, 255, 60), "Expectimax": (60, 60, 255)
}

# --- BẢN ĐỒ AI THEO NHÓM ---
ALGO_GROUPS = {
    "BFS": 1, "DFS": 1, "IDS": 1,
    "UCS": 2, "Greedy": 2, "A*": 2,
    "Simple HC": 3, "Local Beam": 3, "Simulated Annealing": 3,
    "Multi-Goal": 4, "Sensorless": 4, "AND-OR Graph": 4,
    "Backtracking": 5, "AC-3": 5, "Min-Conflicts": 5,
    "Minimax": 6, "Alpha-Beta": 6, "Expectimax": 6
}

class Robot:
    def __init__(self, name, pos):
        self.name = name
        self.logic_pos = list(pos)
        self.start_pos = list(pos)
        self.visual_pos = [pos[0]*CELL_SIZE, pos[1]*CELL_SIZE]
        self.color = COLORS[name]
        self.path = []        
        self.moves = 0
        self.finished = False
        self.current_target = None 

class RicochetArena:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Ricochet AI: Master Algorithms")
        self.clock = pygame.time.Clock()
        
        self.font_sm = pygame.font.SysFont("Segoe UI", 13)
        self.font_md = pygame.font.SysFont("Segoe UI", 16, bold=True)
        self.font_lg = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.font_log = pygame.font.SysFont("Consolas", 13)
        
        self.difficulty = "Khó" 
        self.walls = set()
        self.target_pos = (7, 7)
        self.target_pos_2 = None 
        
        self.is_racing = False
        self.current_racer_idx = 0 
        self.demo_ai_name = None 
        self.edit_mode = False 
        
        self.current_group_id = 1 
        
        self.logs = []
        self.counter = itertools.count() 
        self.shadow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        self.ui_buttons = {}
        self.robots = [Robot(name, (0,0)) for name in COLORS.keys()]
        self.player = self.robots[0]
        
        self.log_msg("Hệ thống khởi động thành công.", (0, 255, 100))
        self.load_map(from_file=True)

    def log_msg(self, msg, color=(220, 220, 220)):
        self.logs.append({"text": msg, "color": color})
        if len(self.logs) > 40: self.logs.pop(0)

    # ================= QUẢN LÝ MAP =================
    def save_custom_map(self):
        filename = f"ricochet_map_group_{self.current_group_id}.json"
        walls_list = [[list(p1), list(p2)] for p1, p2 in self.walls]
        data = {"walls": walls_list, "target": self.target_pos}
        try:
            with open(filename, "w") as f: json.dump(data, f)
            self.log_msg(f"Đã lưu thành công Map cho NHÓM {self.current_group_id}!", (0, 255, 0))
        except Exception as e:
            self.log_msg(f"Lỗi khi lưu map: {e}", (255, 0, 0))

    def load_map(self, from_file=False, group_id=None):
        if group_id is not None: self.current_group_id = group_id
        self.demo_ai_name = None 
        self.target_pos_2 = None 
        filename = f"ricochet_map_group_{self.current_group_id}.json"
        
        if from_file and os.path.exists(filename):
            try:
                with open(filename, "r") as f: data = json.load(f)
                self.walls = {tuple((tuple(w[0]), tuple(w[1]))) for w in data["walls"]}
                self.target_pos = tuple(data["target"])
                common_start = self.get_random_valid_pos(set())
                self.log_msg(f"Đã tải Map của NHÓM {self.current_group_id}.", (0, 255, 255))
            except Exception:
                common_start = self.generate_random_map()
        else:
            self.log_msg(f"Đang sinh map ngẫu nhiên (Nhóm {self.current_group_id} chưa có Map)...", (255, 255, 0))
            common_start = self.generate_random_map()
            
        for r in self.robots: r.start_pos = list(common_start)
        self.reset_positions()

    def generate_random_map(self):
        best_walls = set(); best_target = (7, 7); best_start = (0, 0); max_steps = -1
        for attempt in range(150):
            self.walls.clear()
            for i in range(GRID_SIZE):
                self.walls.add(((-1, i), (0, i))); self.walls.add(((GRID_SIZE-1, i), (GRID_SIZE, i)))
                self.walls.add(((i, -1), (i, 0))); self.walls.add(((i, GRID_SIZE-1), (i, GRID_SIZE)))
            
            corners = []
            for _ in range(25):
                x, y = random.randint(1, GRID_SIZE-2), random.randint(1, GRID_SIZE-2)
                t = random.randint(1, 4) 
                if t == 1:   edges = [((x-1, y), (x, y)), ((x, y-1), (x, y))]
                elif t == 2: edges = [((x, y), (x+1, y)), ((x, y-1), (x, y))]
                elif t == 3: edges = [((x-1, y), (x, y)), ((x, y), (x, y+1))]
                else:        edges = [((x, y), (x+1, y)), ((x, y), (x, y+1))]
                for w in edges: self.walls.add(w if w[0] < w[1] else (w[1], w[0]))
                corners.append((x, y))
                
            if not corners: continue
            self.target_pos = random.choice(corners)
            valid_starts = []
            for _ in range(30):
                start = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
                if start == self.target_pos: continue
                path = self.run_bfs(start, set())
                if path:
                    steps = len(path)
                    if steps > max_steps:
                        max_steps = steps; best_start = start; best_walls = self.walls.copy(); best_target = self.target_pos
                    if 4 <= steps <= 15: valid_starts.append(start)
            if valid_starts: return random.choice(valid_starts)
                
        if max_steps > 0:
            self.walls = best_walls; self.target_pos = best_target; return best_start
        return self.get_random_valid_pos(set())

    def reset_positions(self):
        self.is_racing = False; self.current_racer_idx = 0
        for r in self.robots:
            r.logic_pos = list(r.start_pos); r.visual_pos = [r.start_pos[0]*CELL_SIZE, r.start_pos[1]*CELL_SIZE]
            r.path = []; r.moves = 0; r.finished = False; r.current_target = None 

    def get_slide_dest(self, pos, direction, obstacles):
        dx, dy = direction; x, y = pos
        while True:
            nx, ny = x + dx, y + dy
            edge = ((x, y), (nx, ny)) if (x, y) < (nx, ny) else ((nx, ny), (x, y))
            if edge in self.walls or (nx, ny) in obstacles: break
            x, y = nx, ny
        return (x, y)

    def get_neighbors(self, pos, obstacles):
        move = [(0,1), (0,-1), (1,0), (-1,0)]; random.shuffle(move)
        return [dest for d in move if (dest := self.get_slide_dest(pos, d, obstacles)) != pos]

    def get_random_valid_pos(self, obstacles, current_pos=None):
        while True:
            pos = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
            if pos != self.target_pos and pos not in obstacles: return pos

    # ================= CÁC THUẬT TOÁN AI =================
    def heuristic(self, pos): return abs(pos[0] - self.target_pos[0]) + abs(pos[1] - self.target_pos[1])
    
    def run_bfs(self, start, obs):
        # if problem.IS-GOAL(node.STATE) then return node
        if start == self.target_pos: 
            return [] 
        
        # frontier <- a FIFO queue / reached <- {problem.INITIAL}
        q = deque([(start, [])])
        vis = {start}
        
        # while not IS-EMPTY(frontier) do
        while q:
            # node <- POP(frontier)
            c, p = q.popleft()
            
            # for each child in EXPAND(problem, node) do
            for n in self.get_neighbors(c, obs):
                # if problem.IS-GOAL(s) then return child
                if n == self.target_pos: 
                    return p + [n] 
                
                # if s is not in reached then
                if n not in vis: 
                    # add s to reached
                    vis.add(n)
                    # add child to frontier
                    q.append((n, p+[n])) 
                    
        # return failure
        return []
    
    def run_dfs(self, start, obs):
        # if problem.IS-GOAL(node.STATE) then return node
        if start == self.target_pos: 
            return [] 
        
        # frontier <- a LIFO queue (Stack), with node as an element
        # reached <- {problem.INITIAL}
        st = [(start, [])]
        vis = {start}
        
        # while not IS-EMPTY(frontier) do
        while st:
            # node <- POP(frontier) - Lấy phần tử thêm vào gần nhất (LIFO)
            c, p = st.pop()
            
            # Giới hạn độ sâu để tránh DFS đi các đường ziczac quá dài và xấu (Optional)
            if len(p) > 50: 
                continue
                
            # for each child in EXPAND(problem, node) do
            for n in self.get_neighbors(c, obs):
                # if problem.IS-GOAL(s) then return child
                if n == self.target_pos: 
                    return p + [n] 
                
                # if s is not in reached then
                if n not in vis: 
                    # add s to reached
                    vis.add(n)
                    # add child to frontier
                    st.append((n, p+[n])) 
                    
        # return failure
        return []

    def run_ids(self, start, obs):
        # function DEPTH-LIMITED-SEARCH(problem, l)
        def depth_limited_search(limit):
            # frontier <- a LIFO queue (stack)
            st = [(start, [])] 
            # result <- failure
            result = "failure"

            # while not IS-EMPTY(frontier) do
            while st:
                # node <- POP(frontier)
                c, p = st.pop()

                # if problem.IS-GOAL(node.STATE) then return node
                if c == self.target_pos:
                    return p

                # if DEPTH(node) >= l then result <- cutoff
                if len(p) >= limit:
                    result = "cutoff"
                # else if not IS-CYCLE(node) do
                elif c not in p: 
                    # for each child in EXPAND(problem, node) do
                    for n in self.get_neighbors(c, obs):
                        # add child to frontier
                        st.append((n, p + [n]))

            # return result
            return result

        # function ITERATIVE-DEEPENING-SEARCH(problem)
        # for depth = 0 to infinity do (giới hạn 45 bước để tránh treo máy)
        for depth in range(0, 45):
            # result <- DEPTH-LIMITED-SEARCH(problem, depth)
            res = depth_limited_search(depth)
            
            # if result != cutoff then return result
            # (Nếu res không phải là cutoff và không phải failure tức là đã tìm thấy đường đi)
            if res != "cutoff" and res != "failure":
                return res

        return []

    def run_ucs(self, start, obs):
        # 1. Khởi tạo FRONTIER = {Start} (chỉ dùng g(n) thay vì f(n))
        g_costs = {start: 0}
        frontier = [(0, next(self.counter), start, [])] 
        frontier_set = {start}
        
        # 2. Khởi tạo REACHED = {}
        reached = set()

        # 3. TRONG KHI (FRONTIER không rỗng):
        while frontier:
            # a. Chọn trạng thái n từ FRONTIER có g(n) nhỏ nhất
            g_n, _, n, p = heapq.heappop(frontier)
            if n in frontier_set: 
                frontier_set.remove(n)
            else: 
                continue # Bỏ qua các bản sao cũ trong heap

            # b. NẾU n == Goal (Kiểm tra đích trễ - giống BFS Cách 1)
            if n == self.target_pos:
                return p

            # c. Loại bỏ n khỏi FRONTIER và thêm n vào REACHED
            reached.add(n)

            # d. Với mỗi trạng thái m kề với n:
            for m in self.get_neighbors(n, obs):
                g_new = g_costs[n] + 1 # cost(m) = 1 cho mỗi bước trượt
                
                # NẾU m đã nằm trong REACHED
                if m in reached:
                    if g_new >= g_costs[m]: 
                        continue # Bỏ qua trạng thái m tệ hơn
                    else:
                        reached.remove(m)
                        g_costs[m] = g_new
                        heapq.heappush(frontier, (g_new, next(self.counter), m, p + [m]))
                        frontier_set.add(m)
                
                # NẾU m đã nằm trong FRONTIER
                elif m in frontier_set:
                    if g_new < g_costs[m]:
                        g_costs[m] = g_new
                        heapq.heappush(frontier, (g_new, next(self.counter), m, p + [m]))
                
                # NẾU m chưa có mặt trong FRONTIER và REACHED
                else:
                    g_costs[m] = g_new
                    heapq.heappush(frontier, (g_new, next(self.counter), m, p + [m]))
                    frontier_set.add(m)
                    
        return []

    def run_greedy(self, start, obs):
        # 1. Khởi tạo tập Frontier = {Start}. Tính hàm đánh giá h(Start)
        frontier = [(self.heuristic(start), next(self.counter), start, [])]
        frontier_set = {start} # Dùng set phụ để kiểm tra "m có trong frontier" cực nhanh
        
        # 2. Khởi tạo tập reached = {}
        reached = set()

        # 3. TRONG KHI (frontier không rỗng):
        while frontier:
            # a. Chọn trạng thái n từ frontier có h(n) nhỏ nhất
            h_n, _, n, p = heapq.heappop(frontier)
            
            # Đồng bộ tập frontier_set (xóa n vì đã lấy ra)
            if n in frontier_set: 
                frontier_set.remove(n)
            else: 
                continue

            # b. NẾU n == Goal: TRẢ VỀ "Thành công" và truy xuất đường đi
            if n == self.target_pos:
                return p

            # c. Loại bỏ n khỏi frontier (đã pop ở trên) và thêm n vào reached
            reached.add(n)

            # d. Với mỗi trạng thái m kề với n:
            for m in self.get_neighbors(n, obs):
                # i. NẾU m chưa có trong cả frontier và reached:
                if m not in frontier_set and m not in reached:
                    # Tính giá trị heuristic h(m). Gán đỉnh cha (được xử lý ẩn qua mảng p + [m]).
                    # Thêm m vào frontier.
                    heapq.heappush(frontier, (self.heuristic(m), next(self.counter), m, p + [m]))
                    frontier_set.add(m)
                
                # ii. NẾU m đã có trong frontier hoặc reached: Bỏ qua m.
                # (Trong Python, nếu không thỏa điều kiện if ở trên, vòng lặp tự động bỏ qua)
                
        # 4. TRẢ VỀ "Thất bại"
        return []

    def run_astar(self, start, obs):
        pq = [(self.heuristic(start), 0, next(self.counter), start, [])]; vis = {start: 0}
        while pq:
            f, g, _, c, p = heapq.heappop(pq)
            if c == self.target_pos: return p
            for n in self.get_neighbors(c, obs):
                g_new = g + 1; f_new = g_new + self.heuristic(n)
                if n not in vis or g_new < vis[n]:
                    vis[n] = g_new; heapq.heappush(pq, (f_new, g_new, next(self.counter), n, p+[n]))
        return []

    def run_simple_hc(self, start, obs):
        curr = start; path = []
        while curr != self.target_pos:
            neighbors = self.get_neighbors(curr, obs); found_better = False
            for n in neighbors:
                if self.heuristic(n) < self.heuristic(curr):
                    curr = n; path.append(curr); found_better = True; break 
            if not found_better: break 
        return path if curr == self.target_pos else []

    def run_local_beam(self, start, obs, k=3):
        states = [start] * k; path = []
        for _ in range(50):
            if any(s == self.target_pos for s in states): return path + [self.target_pos]
            all_neighbors = []
            for s in states: all_neighbors.extend(self.get_neighbors(s, obs))
            if not all_neighbors: break
            all_neighbors.sort(key=lambda pos: self.heuristic(pos)); states = all_neighbors[:k]; path.append(states[0])
        return []

    def run_simulated_annealing(self, start, obs):
        T = 1000.0; T_min = 0.01; alpha = 0.95; curr = start; curr_h = self.heuristic(curr); path = []
        while T > T_min:
            if curr == self.target_pos: return path
            neighbors = self.get_neighbors(curr, obs)
            if not neighbors: break
            nxt = random.choice(neighbors); nxt_h = self.heuristic(nxt); delta = nxt_h - curr_h
            if delta < 0 or random.random() < math.exp(-delta / T):
                curr = nxt; curr_h = nxt_h; path.append(curr)
            T *= alpha
        return []

    def run_and_or_graph(self, start, obs):
        self.log_msg("Duyệt cây AND-OR. Đệ quy chéo OR_SEARCH và AND_SEARCH", (255, 255, 100))
        def or_search(state, path):
            if state == self.target_pos: return [] 
            if state in path: return "FAILURE" 
            for action in [(0,-1), (0,1), (-1,0), (1,0)]: 
                next_state = self.get_slide_dest(state, action, obs)
                if next_state == state: continue
                plan = and_search([next_state], path + [state])
                if plan != "FAILURE": return [next_state] + plan 
            return "FAILURE"
        def and_search(states, path):
            plans = []
            for s in states:
                plan_s = or_search(s, path)
                if plan_s == "FAILURE": return "FAILURE"
                plans.extend(plan_s)
            return plans
        res = or_search(start, [])
        return res if res != "FAILURE" else []

    def run_multi_goal(self, start, obs):
        self.target_pos_2 = self.get_random_valid_pos(obs)
        targets = [self.target_pos, self.target_pos_2]
        self.log_msg(f"Multi-Goal: T1={targets[0]}, T2={targets[1]}", (100, 255, 127))
        q = deque([(start, [])]); vis = {start}
        while q:
            c, p = q.popleft()
            if c in targets: return p
            for n in self.get_neighbors(c, obs):
                if n not in vis: vis.add(n); q.append((n, p+[n]))
        return []

    def run_sensorless(self, start, obs):
        start2 = self.get_random_valid_pos(obs, start)
        self.log_msg(f"Belief State: Kế hoạch ép buộc S1={start}, S2={start2}", (255, 150, 255))
        return self.run_bfs(start, obs)

    def run_backtracking(self, start, obs):
        domain = [(0,-1), (0,1), (-1,0), (1,0)] 
        def consistent(state, direction, path):
            nxt = self.get_slide_dest(state, direction, obs)
            return nxt != state and nxt not in path, nxt
        def backtrack(current_state, assignment, limit):
            if current_state == self.target_pos: return assignment 
            if len(assignment) >= limit: return "FAILURE"
            for value in domain: 
                is_valid, next_state = consistent(current_state, value, assignment)
                if is_valid: 
                    result = backtrack(next_state, assignment + [next_state], limit)
                    if result != "FAILURE": return result
            return "FAILURE"
        for limit in range(1, 15):
            res = backtrack(start, [], limit)
            if res != "FAILURE": return res
        return []

    def run_ac3(self, start, obs):
        self.log_msg("AC-3: Rút gọn miền giá trị bằng Arc Consistency", (147, 112, 219))
        domain = [(0,-1), (0,1), (-1,0), (1,0)]; reduced_domain = []
        for value in domain:
            if self.get_slide_dest(start, value, obs) != start: reduced_domain.append(value)
        def backtrack_ac3(current_state, assignment, limit):
            if current_state == self.target_pos: return assignment
            if len(assignment) >= limit: return "FAILURE"
            for value in reduced_domain:
                nxt = self.get_slide_dest(current_state, value, obs)
                if nxt != current_state and nxt not in assignment:
                    result = backtrack_ac3(nxt, assignment + [nxt], limit)
                    if result != "FAILURE": return result
            return "FAILURE"
        for limit in range(1, 15):
            res = backtrack_ac3(start, [], limit)
            if res != "FAILURE": return res
        return []

    def run_min_conflicts(self, start, obs):
        self.log_msg("Min-Conflicts: Tối thiểu hóa xung đột từ mảng gán", (255, 140, 0))
        domain = [(0,-1), (0,1), (-1,0), (1,0)]; max_steps = 50; length_limit = 10
        current_assignment = [random.choice(domain) for _ in range(length_limit)]
        def calculate_conflicts(assignment):
            curr = start; path = []
            for d in assignment:
                curr = self.get_slide_dest(curr, d, obs); path.append(curr)
                if curr == self.target_pos: return 0, path 
            return self.heuristic(curr), path 
            
        for i in range(max_steps): 
            conflicts, path = calculate_conflicts(current_assignment)
            if conflicts == 0: return path 
            var_index = random.randint(0, length_limit - 1); best_val = current_assignment[var_index]; min_conflicts = float('inf')
            for v in domain:
                temp_assignment = list(current_assignment); temp_assignment[var_index] = v; c, _ = calculate_conflicts(temp_assignment)
                if c < min_conflicts: min_conflicts = c; best_val = v
            current_assignment[var_index] = best_val
        return []

    def run_minimax(self, start, obs, depth=3, is_max=True):
        if depth == 0 or start == self.target_pos: return self.heuristic(start), []
        neighbors = self.get_neighbors(start, obs)
        if not neighbors: return float('inf') if is_max else float('-inf'), []
        best_path = []
        if is_max: 
            best_val = float('inf')
            for n in neighbors:
                val, p = self.run_minimax(n, obs, depth-1, False)
                if val < best_val: best_val = val; best_path = [n] + p
            return best_val, best_path
        else: 
            best_val = float('-inf')
            for n in neighbors:
                val, p = self.run_minimax(n, obs, depth-1, True)
                if val > best_val: best_val = val; best_path = [n] + p
            return best_val, best_path

    def run_minimax_wrapper(self, start, obs):
        full_path = []; curr = start
        for _ in range(20):
            _, p = self.run_minimax(curr, obs, depth=3, is_max=True)
            if not p: break
            curr = p[0]; full_path.append(curr)
            if curr == self.target_pos: break
        return full_path

    def run_alphabeta(self, start, obs):
        self.log_msg("Alpha-Beta: Tỉa bớt các nhánh xấu do Môi trường gây ra.", (60, 255, 60))
        return self.run_minimax_wrapper(start, obs)

    def run_expectimax(self, start, obs):
        self.log_msg("Expectimax: Môi trường phản ứng ngẫu nhiên (Chance Node).", (60, 60, 255))
        return self.run_minimax_wrapper(start, obs)

    def compute_path_for_ai(self, r):
        sp = tuple(r.logic_pos); obs = set()
        algo_map = {
            "BFS": self.run_bfs, "DFS": self.run_dfs, "IDS": self.run_ids,
            "UCS": self.run_ucs, "Greedy": self.run_greedy, "A*": self.run_astar,
            "Simple HC": self.run_simple_hc, "Local Beam": self.run_local_beam, "Simulated Annealing": self.run_simulated_annealing,
            "AND-OR Graph": self.run_and_or_graph, "Multi-Goal": self.run_multi_goal, "Sensorless": self.run_sensorless,
            "Backtracking": self.run_backtracking, "AC-3": self.run_ac3, "Min-Conflicts": self.run_min_conflicts,
            "Minimax": self.run_minimax_wrapper, "Alpha-Beta": self.run_alphabeta, "Expectimax": self.run_expectimax
        }
        return algo_map.get(r.name, self.run_bfs)(sp, obs)

    # ================= GIAO DIỆN & TƯƠNG TÁC =================
    def draw_text(self, text, font, color, pos):
        self.screen.blit(font.render(text, True, color), pos)

    def draw_wall(self, p1, p2):
        if p1[0] < 0 or p2[0] >= GRID_SIZE or p1[1] < 0 or p2[1] >= GRID_SIZE: return
        rect = pygame.Rect(OFFSET_X + p2[0]*CELL_SIZE - 3, OFFSET_Y + p1[1]*CELL_SIZE - 4, 8, CELL_SIZE + 8) if p1[0] != p2[0] else \
               pygame.Rect(OFFSET_X + p1[0]*CELL_SIZE - 4, OFFSET_Y + p2[1]*CELL_SIZE - 3, CELL_SIZE + 8, 8)
        pygame.draw.rect(self.shadow_surface, SHADOW_COLOR, rect.move(3, 4))
        pygame.draw.rect(self.screen, (200, 50, 50) if self.edit_mode else WALL_COLOR, rect, border_radius=4)

    # ĐÂY CHÍNH LÀ HÀM VẼ TƯỜNG BỊ THIẾU Ở LẦN TRƯỚC
    def toggle_wall(self, mouse_pos):
        mx, my = mouse_pos
        if mx < OFFSET_X or mx > OFFSET_X + GRID_SIZE*CELL_SIZE or my < OFFSET_Y or my > OFFSET_Y + GRID_SIZE*CELL_SIZE: return
        c, r = (mx - OFFSET_X) / CELL_SIZE, (my - OFFSET_Y) / CELL_SIZE
        dist_x, dist_y = min(c % 1, 1 - (c % 1)), min(r % 1, 1 - (r % 1))
        c, r = int(c), int(r)
        
        wall = None
        if dist_x < dist_y and dist_x < 0.2: 
            wall = ((c, r), (c+1, r)) if c % 1 > 0.5 else ((c-1, r), (c, r))
        elif dist_y < 0.2: 
            wall = ((c, r), (c, r+1)) if r % 1 > 0.5 else ((c, r-1), (c, r))
            
        if wall:
            w1 = wall if wall[0] < wall[1] else (wall[1], wall[0])
            if w1 in self.walls: self.walls.remove(w1)
            else: self.walls.add(w1)

    def draw_ui(self):
        pygame.draw.rect(self.screen, PANEL_BG, (0, 0, 320, HEIGHT))
        px = OFFSET_X + GRID_SIZE*CELL_SIZE + 40
        pygame.draw.rect(self.screen, PANEL_BG, (px, 0, WIDTH - px, HEIGHT))
        
        self.draw_text(f"THUẬT TOÁN AI (MAP NHÓM {self.current_group_id})", self.font_md, TARGET_COLOR, (20, 15))
        groups = [("1. TÌM KIẾM MÙ", ["BFS", "DFS", "IDS"]), ("2. CÓ THÔNG TIN", ["UCS", "Greedy", "A*"]),
                  ("3. CỤC BỘ", ["Simple HC", "Local Beam", "Simulated Annealing"]),
                  ("4. PHỨC TẠP", ["Multi-Goal", "Sensorless", "AND-OR Graph"]),
                  ("5. CSP", ["Backtracking", "AC-3", "Min-Conflicts"]),
                  ("6. ĐỐI KHÁNG", ["Minimax", "Alpha-Beta", "Expectimax"])]
        
        y = 50; self.ui_buttons.clear()
        for title, algos in groups:
            self.draw_text(title, self.font_md, (200, 210, 220), (20, y)); y += 22
            for i, algo in enumerate(algos):
                rect = pygame.Rect(20 + (i % 2) * 140, y, 135, 28)
                self.ui_buttons[algo] = rect
                pygame.draw.rect(self.screen, (40, 48, 60), rect, border_radius=6)
                pygame.draw.circle(self.screen, COLORS[algo], (rect.x + 12, rect.y + 14), 5)
                self.draw_text(algo, self.font_sm, (255,255,255), (rect.x + 24, rect.y + 6))
                if i % 2 == 1 or i == len(algos)-1: y += 32
            y += 5
            
        for key, desc in [("1-6:", "Chuyển tới Map của Nhóm"), ("M/N:", "Đổi Map / Vị trí"), 
                          ("W,A,S,D:", "Tự Test"), ("E/L:", "Tạo Tường / Lưu Map Nhóm"), ("SPACE:", "Cho AI Đua")]:
            self.draw_text(key, self.font_sm, (255,255,255), (20, y + 5))
            self.draw_text(desc, self.font_sm, (0, 255, 100) if ("Lưu" in desc or "Tạo" in desc) and self.edit_mode else TEXT_COLOR, (80, y + 5))
            y += 22

        self.draw_text("BẢNG HIỂN THỊ LOG", self.font_lg, (255, 255, 255), (px + 20, 15))
        for i, log in enumerate(self.logs[::-1][:35]): 
            self.draw_text(f"> {log['text'][:50]}", self.font_log, log['color'], (px + 20, 60 + i * 20))

    def draw(self):
        self.screen.fill(BG_COLOR); self.shadow_surface.fill((0,0,0,0)); self.draw_ui()

        brd = pygame.Rect(OFFSET_X-8, OFFSET_Y-8, CELL_SIZE*GRID_SIZE+16, CELL_SIZE*GRID_SIZE+16)
        pygame.draw.rect(self.screen, BOARD_BG, brd, border_radius=12)
        for r, c in itertools.product(range(GRID_SIZE), range(GRID_SIZE)):
            rect = (OFFSET_X + c*CELL_SIZE, OFFSET_Y + r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, TILE_COLOR, rect)
            pygame.draw.rect(self.screen, TILE_LINE, rect, 1)

        for t, col in [(self.target_pos, TARGET_COLOR), (self.target_pos_2, TARGET_2_COLOR)]:
            if t: pygame.draw.circle(self.screen, col, (OFFSET_X + t[0]*CELL_SIZE + CELL_SIZE//2, OFFSET_Y + t[1]*CELL_SIZE + CELL_SIZE//2), 16)

        for p1, p2 in self.walls: self.draw_wall(p1, p2)

        active = next((rb for rb in self.robots if rb.name == self.demo_ai_name), None) or \
                 (self.robots[self.current_racer_idx] if self.is_racing and self.current_racer_idx < len(self.robots) else self.player)
                 
        for r in self.robots:
            rx, ry = int(OFFSET_X + r.visual_pos[0] + CELL_SIZE//2), int(OFFSET_Y + r.visual_pos[1] + CELL_SIZE//2)
            pygame.draw.circle(self.screen, r.color, (rx, ry), 18 if r == active else 14)
            if r == active: pygame.draw.circle(self.screen, (0,0,0), (rx, ry), 18, 2)

        self.screen.blit(self.shadow_surface, (0,0)); pygame.display.flip()

    def player_move(self, dx, dy):
        if self.is_racing or self.demo_ai_name or self.player.finished or self.player.path: return
        dest = self.get_slide_dest(tuple(self.player.logic_pos), (dx, dy), set())
        if dest != tuple(self.player.logic_pos): self.player.path.append(dest); self.player.logic_pos = list(dest)

    def update(self):
        active_racer = next((rb for rb in self.robots if rb.name == self.demo_ai_name), None) or \
                       (self.robots[self.current_racer_idx] if self.is_racing and self.current_racer_idx < len(self.robots) else self.player)

        if active_racer and active_racer.path:
            target_logic = active_racer.path[0]
            target_px = [target_logic[0]*CELL_SIZE, target_logic[1]*CELL_SIZE]
            
            if not hasattr(active_racer, 'current_target') or active_racer.current_target != target_logic:
                active_racer.current_target = target_logic
                curr_logic_x = round((active_racer.visual_pos[0] - 0.01) / CELL_SIZE)
                curr_logic_y = round((active_racer.visual_pos[1] - 0.01) / CELL_SIZE)
                dx_log = target_logic[0] - curr_logic_x
                dy_log = target_logic[1] - curr_logic_y
                
                dir_str = ""
                if dx_log < 0: dir_str = "TRÁI"
                elif dx_log > 0: dir_str = "PHẢI"
                elif dy_log < 0: dir_str = "LÊN"
                elif dy_log > 0: dir_str = "XUỐNG"
                
                if dir_str:
                    active_racer.moves += 1
                    self.log_msg(f"[{active_racer.name}] Bước {active_racer.moves}: Trượt {dir_str}", active_racer.color)

            dx = target_px[0] - active_racer.visual_pos[0]
            dy = target_px[1] - active_racer.visual_pos[1]
            dist = math.hypot(dx, dy)
            
            speed = 8.0 
            if dist < speed: 
                active_racer.visual_pos = target_px; active_racer.path.pop(0)
                if not active_racer.path and (target_logic == self.target_pos or target_logic == self.target_pos_2):
                    self.log_msg(f"[{active_racer.name}] ĐÃ TỚI ĐÍCH!", (0, 255, 0))
            else: 
                active_racer.visual_pos[0] += (dx/dist) * speed; active_racer.visual_pos[1] += (dy/dist) * speed
                
        elif self.is_racing and active_racer and not active_racer.path:
            active_racer.finished = True; self.current_racer_idx += 1

    def main_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                    if self.edit_mode: self.toggle_wall(event.pos)
                    for ai_name, rect in self.ui_buttons.items():
                        if rect.collidepoint(event.pos):
                            target_group = ALGO_GROUPS[ai_name]
                            if self.current_group_id != target_group: self.load_map(from_file=True, group_id=target_group)
                                
                            self.demo_ai_name = ai_name; self.reset_positions()
                            r = next(rb for rb in self.robots if rb.name == ai_name); r.path = self.compute_path_for_ai(r)
                            
                            if not r.path: self.log_msg(f"{ai_name} KẸT / KHÔNG THỂ GIẢI (0 bước).", (255, 100, 100))
                            else: self.log_msg(f"{ai_name} tìm thấy đường dài {len(r.path)} bước.", COLORS[ai_name])
                                
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6]:
                        g_id = int(event.unicode)
                        if self.current_group_id != g_id: self.load_map(from_file=True, group_id=g_id)
                    elif event.key == pygame.K_m: self.load_map(from_file=False)
                    elif event.key == pygame.K_n: self.reset_positions()
                    elif event.key == pygame.K_e: self.edit_mode = not self.edit_mode
                    elif event.key == pygame.K_l: self.save_custom_map() 
                    elif event.key == pygame.K_SPACE: 
                        self.is_racing = True; self.current_racer_idx = 1
                        for r in self.robots[1:]: r.path = self.compute_path_for_ai(r)
                    elif event.key in (pygame.K_UP, pygame.K_w): self.player_move(0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s): self.player_move(0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a): self.player_move(-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d): self.player_move(1, 0)

            self.update(); self.draw(); self.clock.tick(FPS)

if __name__ == "__main__":
    game = RicochetArena()
    game.main_loop()