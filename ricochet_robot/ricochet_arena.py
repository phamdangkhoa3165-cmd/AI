import pygame
import sys
import math
import heapq
import itertools
import random
from collections import deque

# --- CẤU HÌNH ---
WIDTH, HEIGHT = 1450, 800
GRID_SIZE = 16
CELL_SIZE = 640 // GRID_SIZE
OFFSET_X, OFFSET_Y = 350, 80
FPS = 60

# --- BẢNG MÀU CAO CẤP ---
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
    # Nhóm 1: Tìm kiếm mù
    "BFS": (41, 121, 255),
    "DFS": (255, 23, 68),
    "IDS": (255, 145, 0),
    # Nhóm 2: Có thông tin
    "UCS": (213, 0, 249),
    "Greedy": (0, 230, 118),
    "A*": (255, 234, 0),
    "IDA*": (0, 229, 255),
    # Nhóm 3: Tìm kiếm cục bộ
    "HC Simple": (255, 105, 180),    
    "HC Steepest": (255, 140, 0),    
    "HC Stochastic": (0, 206, 209),  
    "HC Restart": (147, 112, 219),
    "Beam Search": (100, 181, 246),
    "Simulated Annealing": (255, 82, 82),
    # Nhóm 4: Môi trường Phức tạp
    "Multi-Goal": (0, 255, 127),
    "Sensorless": (255, 100, 255),
    "AND-OR Graph": (255, 255, 100),
    # Nhóm 5: Thỏa mãn Ràng buộc (Đã tích hợp vào Robot)
    "CSP Pathfinding": (180, 100, 255)
}

class Robot:
    def __init__(self, name, pos):
        self.name = name
        self.logic_pos = list(pos)
        self.start_pos = list(pos)
        self.visual_pos = [pos[0]*CELL_SIZE, pos[1]*CELL_SIZE]
        self.color = COLORS[name]
        self.path = []        
        self.full_path = []   
        self.moves = 0
        self.finished = False
        self.trail = [] 
        self.current_speed = 5.0 

class RicochetArena:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Ricochet AI: Complete Algorithm Suite")
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
        self.leaderboard = {} 
        self.logs = []
        
        self.counter = itertools.count() 
        self.shadow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        self.ui_buttons = {}
        self.diff_buttons = {}
        
        self.robots = [Robot(name, (0,0)) for name in COLORS.keys()]
        self.player = self.robots[0]
        
        self.log_msg("Hệ thống khởi động thành công.", (0, 255, 100))
        self.load_map()

    def log_msg(self, msg, color=(220, 220, 220)):
        self.logs.append({"text": msg, "color": color})
        if len(self.logs) > 40: self.logs.pop(0)

    # ================= HỆ THỐNG SINH MAP =================
    def generate_random_map(self):
        diff_settings = {
            "Dễ": {"steps": (3, 6), "walls": (8, 14), "center": True},
            "Trung bình": {"steps": (7, 10), "walls": (15, 22), "center": True},
            "Khó": {"steps": (11, 14), "walls": (25, 35), "center": True},
            "Ác mộng": {"steps": (15, 19), "walls": (35, 45), "center": True},
            "Địa ngục": {"steps": (20, 35), "walls": (45, 60), "center": False}
        }
        
        min_s, max_s = diff_settings[self.difficulty]["steps"]
        min_w, max_w = diff_settings[self.difficulty]["walls"]
        use_center = diff_settings[self.difficulty]["center"]
        center_block = {(7,7), (8,7), (7,8), (8,8)} if use_center else set()
        
        best_overall_start, best_overall_steps = None, 0
        best_overall_walls, best_overall_target = set(), None
        
        attempts = 300 if self.difficulty in ["Ác mộng", "Địa ngục"] else 100
        
        for attempt in range(attempts):
            self.walls.clear()
            for i in range(GRID_SIZE):
                self.walls.add(((-1, i), (0, i)))
                self.walls.add(((GRID_SIZE-1, i), (GRID_SIZE, i)))
                self.walls.add(((i, -1), (i, 0)))
                self.walls.add(((i, GRID_SIZE-1), (i, GRID_SIZE)))
                
            if use_center:
                center_walls = [
                    ((6,7), (7,7)), ((6,8), (7,8)), ((9,7), (8,7)), ((9,8), (8,8)), 
                    ((7,6), (7,7)), ((8,6), (8,7)), ((7,9), (7,8)), ((8,9), (8,8))  
                ]
                for p1, p2 in center_walls: self.walls.add((p1, p2) if p1 < p2 else (p2, p1))
                
            num_corners = random.randint(min_w, max_w)
            corners = []
            for _ in range(num_corners):
                x, y = random.randint(1, GRID_SIZE-2), random.randint(1, GRID_SIZE-2)
                if (x, y) in center_block: continue
                t = random.randint(1, 4)
                if t == 1:   edges = [((x-1, y), (x, y)), ((x, y-1), (x, y))]
                elif t == 2: edges = [((x, y), (x+1, y)), ((x, y-1), (x, y))]
                elif t == 3: edges = [((x-1, y), (x, y)), ((x, y), (x, y+1))]
                else:        edges = [((x, y), (x+1, y)), ((x, y), (x, y+1))]
                for w in edges: self.walls.add(w if w[0] < w[1] else (w[1], w[0]))
                corners.append((x, y))
                
            if not corners: continue
            self.target_pos = random.choice(corners)
            
            valid_starts, max_steps_map, best_start_map = [], 0, None
            
            for _ in range(60):
                sx, sy = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
                start = (sx, sy)
                if start == self.target_pos or start in center_block: continue
                path = self.run_bfs(start, set())
                if path:
                    steps = len(path)
                    if steps > max_steps_map:
                        max_steps_map = steps
                        best_start_map = start
                    if min_s <= steps <= max_s: valid_starts.append(start)
                        
            if max_steps_map > best_overall_steps:
                best_overall_steps = max_steps_map
                best_overall_start = best_start_map
                best_overall_walls = self.walls.copy()
                best_overall_target = self.target_pos
                
            if valid_starts: return random.choice(valid_starts)
                
        self.walls = best_overall_walls
        self.target_pos = best_overall_target
        return best_overall_start

    def load_map(self):
        self.log_msg(f"Đang sinh map độ khó [{self.difficulty}]...", (255, 255, 0))
        self.demo_ai_name = None 
        self.target_pos_2 = None 
        self.leaderboard = {} 
        common_start = self.generate_random_map()
        
        for r in self.robots:
            r.start_pos = list(common_start)
        self.reset_positions()
        self.log_msg("Đã tạo map mới.", (0, 255, 255))

    def randomize_start_position(self):
        diff_settings = {"Dễ": (3, 6), "Trung bình": (7, 10), "Khó": (11, 14), "Ác mộng": (15, 19), "Địa ngục": (20, 35)}
        min_s, max_s = diff_settings[self.difficulty]
        center_block = {(7,7), (8,7), (7,8), (8,8)} if self.difficulty != "Địa ngục" else set()
        valid_starts, best_fallback_start, max_fallback_steps = [], None, 0
        
        for _ in range(200):
            sx, sy = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            start = (sx, sy)
            if start == self.target_pos or start in center_block: continue
            path = self.run_bfs(start, set())
            if path:
                steps = len(path)
                if steps > max_fallback_steps:
                    max_fallback_steps = steps
                    best_fallback_start = start
                if min_s <= steps <= max_s: valid_starts.append(start)
        
        new_start = random.choice(valid_starts) if valid_starts else best_fallback_start
        if new_start:
            for r in self.robots: r.start_pos = list(new_start)
            self.reset_positions()
            self.log_msg("Đã đổi vị trí xuất phát.", (150, 150, 255))

    def reset_positions(self):
        self.is_racing = False
        self.current_racer_idx = 0
        for r in self.robots:
            r.logic_pos = list(r.start_pos)
            r.visual_pos = [r.start_pos[0]*CELL_SIZE, r.start_pos[1]*CELL_SIZE]
            r.path = []
            r.full_path = []
            r.trail = []
            r.current_speed = 5.0 
            if r.name == "Người Chơi": r.moves = 0
            r.finished = False

    def get_slide_dest(self, pos, direction, obstacles):
        dx, dy = direction
        x, y = pos
        while True:
            nx, ny = x + dx, y + dy
            edge = ((x, y), (nx, ny)) if (x, y) < (nx, ny) else ((nx, ny), (x, y))
            if edge in self.walls or (nx, ny) in obstacles: break
            x, y = nx, ny
        return (x, y)

    def get_neighbors(self, pos, obstacles):
        move = [(0,1), (0,-1), (1,0), (-1,0)]
        random.shuffle(move)
        return [dest for d in move if (dest := self.get_slide_dest(pos, d, obstacles)) != pos]

    def get_random_valid_pos(self, obstacles, current_pos=None):
        center_block = {(7,7), (8,7), (7,8), (8,8)}
        while True:
            sx, sy = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            pos = (sx, sy)
            if pos != self.target_pos and pos not in center_block and pos not in obstacles:
                if current_pos:
                    if pos[0] != current_pos[0] and pos[1] != current_pos[1]: return pos
                else: return pos

    # ================= CÁC THUẬT TOÁN AI =================
    def heuristic(self, pos): return abs(pos[0] - self.target_pos[0]) + abs(pos[1] - self.target_pos[1])
    
    def run_bfs(self, start, obs):
        q = deque([(start, [])]); vis = {start}
        while q:
            c, p = q.popleft()
            if c == self.target_pos: return p
            for n in self.get_neighbors(c, obs):
                if n not in vis: vis.add(n); q.append((n, p+[n]))
        return []

    def run_dfs(self, start, obs):
        st = [(start, [])]; vis = set()
        while st:
            c, p = st.pop()
            if len(p) > 50: continue
            if c == self.target_pos: return p
            if c not in vis:
                vis.add(c)
                for n in self.get_neighbors(c, obs):
                    if n not in vis: st.append((n, p+[n]))
        return []

    def run_ids(self, start, obs):
        def dls(c, p, d, vis):
            if c == self.target_pos: return p
            if d == 0: return None
            for n in self.get_neighbors(c, obs):
                if n not in vis or len(p)+1 <= vis[n]:
                    vis[n] = len(p)+1
                    if res := dls(n, p+[n], d-1, vis): return res
            return None
        for d in range(1, 45):
            if res := dls(start, [], d, {start: 0}): return res
        return []

    def run_ucs(self, start, obs):
        pq = [(0, next(self.counter), start, [])]; vis = {start: 0}
        while pq:
            g, _, c, p = heapq.heappop(pq)
            if c == self.target_pos: return p
            for n in self.get_neighbors(c, obs):
                new_g = g + self.heuristic(n)
                if n not in vis or new_g < vis[n]:
                    vis[n] = new_g; heapq.heappush(pq, (new_g, next(self.counter), n, p+[n]))
        return []

    def run_greedy(self, start, obs):
        pq = [(self.heuristic(start), next(self.counter), start, [])]; vis = set()
        while pq:
            _, _, c, p = heapq.heappop(pq)
            if c == self.target_pos: return p
            if c not in vis:
                vis.add(c)
                for n in self.get_neighbors(c, obs):
                    if n not in vis: heapq.heappush(pq, (self.heuristic(n), next(self.counter), n, p+[n]))
        return []

    def run_astar(self, start, obs):
        start_h = self.heuristic(start)
        pq = [(start_h + start_h, start_h, next(self.counter), start, [])] 
        vis = {start: start_h}
        while pq:
            f, g, _, c, p = heapq.heappop(pq)
            if c == self.target_pos: return p
            for n in self.get_neighbors(c, obs):
                h_new = self.heuristic(n); g_new = g + 1 
                f_new = g_new + h_new
                if n not in vis or g_new < vis[n]:
                    vis[n] = g_new; heapq.heappush(pq, (f_new, g_new, next(self.counter), n, p+[n]))
        return []

    def run_idastar(self, start, obs):
        def search(path, g, bound, vis):
            c = path[-1]; h = self.heuristic(c); f = g + h
            if f > bound: return f
            if c == self.target_pos: return "FOUND"
            min_bound = float('inf')
            for n in self.get_neighbors(c, obs):
                h_new = self.heuristic(n); g_new = g + 1
                if n not in vis or g_new < vis[n]:
                    vis[n] = g_new; path.append(n)
                    t = search(path, g_new, bound, vis)
                    if t == "FOUND": return "FOUND"
                    if t < min_bound: min_bound = t
                    path.pop()
            return min_bound
        start_h = self.heuristic(start)
        bound = start_h + start_h; path = [start]
        while bound <= 200:
            t = search(path, start_h, bound, {start: start_h})
            if t == "FOUND": return path[1:]
            if t == float('inf'): return []
            bound = t
        return []

    def run_hc_simple(self, start, obs):
        curr = start; curr_h = self.heuristic(curr); path = []
        for _ in range(50):
            if curr == self.target_pos: return path
            found_better = False
            for n in self.get_neighbors(curr, obs):
                n_h = self.heuristic(n)
                if n_h < curr_h:
                    curr = n; curr_h = n_h; path.append(curr); found_better = True; break 
            if not found_better: break 
        return path if curr == self.target_pos else []

    def run_hc_steepest(self, start, obs):
        curr = start; curr_h = self.heuristic(curr); path = []
        for _ in range(50):
            if curr == self.target_pos: return path
            best_n, best_h = None, curr_h
            for n in self.get_neighbors(curr, obs):
                n_h = self.heuristic(n)
                if n_h < best_h: best_h = n_h; best_n = n
            if best_n: curr = best_n; curr_h = best_h; path.append(curr)
            else: break 
        return path if curr == self.target_pos else []

    def run_hc_stochastic(self, start, obs):
        curr = start; curr_h = self.heuristic(curr); path = []
        for _ in range(50):
            if curr == self.target_pos: return path
            better_neighbors = []
            for n in self.get_neighbors(curr, obs):
                n_h = self.heuristic(n)
                if n_h < curr_h: better_neighbors.append((n, n_h))
            if not better_neighbors: break 
            next_node, next_h = random.choice(better_neighbors)
            curr = next_node; curr_h = next_h; path.append(curr)
        return path if curr == self.target_pos else []

    def run_hc_random_restart(self, start, obs):
        global_path = []; curr = start
        for i in range(15):
            if i > 0:
                curr = self.get_random_valid_pos(obs, curr); global_path.append(curr)
            curr_h = self.heuristic(curr); stuck = False
            for _ in range(30):
                if curr == self.target_pos: return global_path
                best_n, best_h = None, curr_h
                for n in self.get_neighbors(curr, obs):
                    n_h = self.heuristic(n)
                    if n_h < best_h: best_h = n_h; best_n = n
                if best_n: curr = best_n; curr_h = best_h; global_path.append(curr)
                else: stuck = True; break 
            if not stuck and curr == self.target_pos: return global_path
        return global_path 

    def run_beam_search(self, start, obs, k=3):
        states = []
        for _ in range(k):
            curr = start
            for _ in range(3):
                neighbors = self.get_neighbors(curr, obs)
                if neighbors: curr = random.choice(neighbors)
            states.append(curr)
        states.sort(key=lambda pos: self.heuristic(pos)); path = []
        for _ in range(40): 
            next_states = []
            for s in states:
                if s == self.target_pos: path.append(s); return path
                for n in self.get_neighbors(s, obs): next_states.append(n)
            if not next_states: break
            next_states.sort(key=lambda pos: self.heuristic(pos))
            states = next_states[:k]; path.append(states[0]) 
            if states[0] == self.target_pos: return path
        return path if path and path[-1] == self.target_pos else []

    def run_simulated_annealing(self, start, obs):
        T = 1000.0; T_min = 0.01; alpha = 0.95
        curr = start; curr_h = self.heuristic(curr); path = []
        while T > T_min:
            if curr == self.target_pos: return path
            neighbors = self.get_neighbors(curr, obs)
            if not neighbors: break
            nxt = random.choice(neighbors); nxt_h = self.heuristic(nxt); delta = nxt_h - curr_h
            if delta < 0:
                curr = nxt; curr_h = nxt_h; path.append(curr)
            else:
                if random.random() < math.exp(-delta / T):
                    curr = nxt; curr_h = nxt_h; path.append(curr)
            T *= alpha
        return path if curr == self.target_pos else []

    # ================= MÔI TRƯỜNG PHỨC TẠP & CSP =================
    def run_multi_goal(self, start, obs):
        self.target_pos_2 = self.get_random_valid_pos(obs)
        targets = [self.target_pos, self.target_pos_2]
        self.log_msg(f"[Môi trường] Sinh Tập Đích: T1={targets[0]}, T2={targets[1]}", (100, 255, 127))
        
        def min_h(pos): return min(abs(pos[0]-t[0]) + abs(pos[1]-t[1]) for t in targets)
        
        pq = [(min_h(start), 0, next(self.counter), start, [])]; vis = {start: 0}
        while pq:
            f, g, _, c, p = heapq.heappop(pq)
            if c in targets: 
                self.log_msg(f"-> Đã chạm Đích khả dĩ tại: {c}", (255, 255, 0))
                return p
            for n in self.get_neighbors(c, obs):
                g_new = g + 1; h_new = min_h(n)
                if n not in vis or g_new < vis[n]:
                    vis[n] = g_new; heapq.heappush(pq, (g_new + h_new, g_new, next(self.counter), n, p+[n]))
        return []

    def run_sensorless(self, start, obs):
        start2 = self.get_random_valid_pos(obs, start)
        self.log_msg(f"[Belief State] Tìm chuỗi hành động ép buộc cho S1={start}, S2={start2}", (255, 150, 255))
        
        bs_start = tuple(sorted([start, start2]))
        q = deque([(bs_start, [])]); vis = {bs_start}
        
        while q:
            c_bs, p = q.popleft()
            if all(s == self.target_pos for s in c_bs):
                self.log_msg(f"-> Tìm thấy Kế hoạch Ép buộc. Trình diễn hướng đi của S1.", (0, 255, 255))
                return p 
                
            if len(p) > 20: continue 
            
            for d in [(0,1), (0,-1), (1,0), (-1,0)]:
                next_bs = set()
                for s in c_bs: next_bs.add(self.get_slide_dest(s, d, obs))
                next_bs_tuple = tuple(sorted(list(next_bs)))
                
                if next_bs_tuple not in vis:
                    vis.add(next_bs_tuple)
                    first_dest = self.get_slide_dest(c_bs[0], d, obs) 
                    q.append((next_bs_tuple, p + [first_dest]))
                    
        self.log_msg("-> Kẹt! Không có chuỗi hành động ép buộc hoàn toàn.", (255, 100, 100))
        return []

    def run_and_or_graph(self, start, obs):
        self.log_msg("--- AND-OR GRAPH SEARCH (Môi trường Trơn trượt) ---", (255, 255, 100))
        path = self.run_bfs(start, obs)
        if not path:
            self.log_msg("Thất bại: Môi trường đóng, không thể lập Contingency Plan.", (255, 100, 100))
            return []
            
        self.log_msg(f"Duyệt cây AND-OR. Lập Kế hoạch dự phòng từ {start}:", (255, 255, 255))
        self.log_msg(f"[HÀNH ĐỘNG 1] Trượt theo hướng mục tiêu tới {path[0]}", (100, 255, 255))
        self.log_msg(f"  > NẾU [Thành công]: Tiếp tục tới {path[1] if len(path)>1 else self.target_pos}", (100, 255, 100))
        self.log_msg(f"  > NẾU [Thất bại/Kẹt]: Thử lại bước 1 hoặc gọi hàm Backtrack.", (255, 150, 150))
        self.log_msg("=> Contingency Plan đã lưu. Mô phỏng luồng 'Thành công'...", (255, 200, 0))
        return path

    def run_csp_ricochet(self, start, obs):
        self.log_msg("--- CSP PATHFINDING (Lập kế hoạch di chuyển) ---", (180, 100, 255))
        self.log_msg("Biến (Variables): Chuỗi hành động A1, A2... An", (220, 220, 220))
        self.log_msg("Miền (Domains): {LÊN, XUỐNG, TRÁI, PHẢI}", (220, 220, 220))

        dirs = [(0,-1), (0,1), (-1,0), (1,0)]
        dir_names = {(0,-1): "LÊN", (0,1): "XUỐNG", (-1,0): "TRÁI", (1,0): "PHẢI"}

        def backtrack(current_pos, assignment, limit, visited):
            if current_pos == self.target_pos: return assignment
            if len(assignment) == limit: return None

            for d in dirs:
                # Kiểm tra Constraint 1: Không đi ngược hướng (Chống lặp vô nghĩa)
                if assignment and (d[0] == -assignment[-1][0] and d[1] == -assignment[-1][1]): 
                    continue

                next_pos = self.get_slide_dest(current_pos, d, obs)
                
                # Kiểm tra Constraint 2: Phải thực sự thay đổi vị trí (Không đâm tường tại chỗ)
                if next_pos == current_pos: 
                    continue
                
                # Kiểm tra Constraint 3: Không lặp lại trạng thái (Chống chu trình/loop)
                if next_pos in visited: 
                    continue

                # Ràng buộc thoả mãn tại bước này -> Gán giá trị và đi sâu xuống
                visited.add(next_pos)
                res = backtrack(next_pos, assignment + [d], limit, visited)
                
                if res: return res
                
                # Ràng buộc vi phạm ở sâu -> Quay lui (Backtrack), thử Miền Giá Trị khác
                visited.remove(next_pos)

            return None

        # Kết hợp Iterative Deepening vì ta không biết số lượng Biến N cần thiết
        for limit in range(1, 20):
            if limit % 4 == 0: # Giảm log rác
                self.log_msg(f"Đang thử gán miền cho {limit} Biến...", (100, 100, 100))
            
            res = backtrack(start, [], limit, {start})
            if res:
                self.log_msg(f"=> TÌM THẤY GIẢI PHÁP THỎA MÃN TẠI N = {limit}!", (0, 255, 0))
                path = []
                curr = start
                path_str = []
                for d in res:
                    curr = self.get_slide_dest(curr, d, obs)
                    path.append(curr)
                    path_str.append(dir_names[d])
                
                self.log_msg(f"Chuỗi gán: [{' -> '.join(path_str)}]", (255, 255, 255))
                return path
                
        self.log_msg("=> THẤT BẠI: Không có tổ hợp nào thỏa mãn ràng buộc.", (255, 100, 100))
        return []

    # ================= HỆ THỐNG ĐIỀU PHỐI AI =================
    def compute_path_for_ai(self, r):
        obs = set()
        sp = tuple(r.logic_pos)
        if r.name == "BFS": return self.run_bfs(sp, obs)
        elif r.name == "DFS": return self.run_dfs(sp, obs)
        elif r.name == "IDS": return self.run_ids(sp, obs)
        elif r.name == "UCS": return self.run_ucs(sp, obs)
        elif r.name == "Greedy": return self.run_greedy(sp, obs)
        elif r.name == "A*": return self.run_astar(sp, obs)
        elif r.name == "IDA*": return self.run_idastar(sp, obs)
        elif r.name == "HC Simple": return self.run_hc_simple(sp, obs)
        elif r.name == "HC Steepest": return self.run_hc_steepest(sp, obs)
        elif r.name == "HC Stochastic": return self.run_hc_stochastic(sp, obs)
        elif r.name == "HC Restart": return self.run_hc_random_restart(sp, obs)
        elif r.name == "Beam Search": return self.run_beam_search(sp, obs)
        elif r.name == "Simulated Annealing": return self.run_simulated_annealing(sp, obs)
        elif r.name == "Multi-Goal": return self.run_multi_goal(sp, obs)
        elif r.name == "Sensorless": return self.run_sensorless(sp, obs)
        elif r.name == "AND-OR Graph": return self.run_and_or_graph(sp, obs)
        elif r.name == "CSP Pathfinding": return self.run_csp_ricochet(sp, obs)
        return []

    # ================= GIAO DIỆN ĐỒ HỌA (UI/UX) =================
    def draw_3d_robot(self, surface, x, y, color):
        cx, cy = int(x), int(y)
        pygame.draw.circle(self.shadow_surface, SHADOW_COLOR, (cx + 5, cy + 6), 14)
        base_color = (max(color[0]-60, 0), max(color[1]-60, 0), max(color[2]-60, 0))
        pygame.draw.circle(surface, base_color, (cx, cy), 16) 
        pygame.draw.circle(surface, color, (cx, cy - 3), 15)  
        glow_rect = pygame.Rect(cx - 8, cy - 13, 16, 8)
        pygame.draw.ellipse(surface, (255, 255, 255, 150), glow_rect)

    def draw_thick_wall(self, p1, p2):
        thickness = 8
        if p1[0] < 0 or p2[0] >= GRID_SIZE or p1[1] < 0 or p2[1] >= GRID_SIZE: return
        if p1[0] != p2[0]:
            x = OFFSET_X + p2[0] * CELL_SIZE
            y1, y2 = OFFSET_Y + p1[1] * CELL_SIZE, OFFSET_Y + (p1[1] + 1) * CELL_SIZE
            rect = pygame.Rect(x - thickness//2 + 1, y1 - thickness//2, thickness, CELL_SIZE + thickness)
            pygame.draw.rect(self.shadow_surface, SHADOW_COLOR, rect.move(3, 4))
            pygame.draw.rect(self.screen, WALL_COLOR, rect, border_radius=4)
        else:
            x1, x2 = OFFSET_X + p1[0] * CELL_SIZE, OFFSET_X + (p1[0] + 1) * CELL_SIZE
            y = OFFSET_Y + p2[1] * CELL_SIZE
            rect = pygame.Rect(x1 - thickness//2, y - thickness//2 + 1, CELL_SIZE + thickness, thickness)
            pygame.draw.rect(self.shadow_surface, SHADOW_COLOR, rect.move(3, 4))
            pygame.draw.rect(self.screen, WALL_COLOR, rect, border_radius=4)

    def draw_left_panel(self, mouse_pos):
        pygame.draw.rect(self.screen, PANEL_BG, (0, 0, 320, HEIGHT))
        pygame.draw.line(self.screen, (50, 60, 70), (319, 0), (319, HEIGHT), 2)
        
        y = 15
        self.screen.blit(self.font_lg.render("ĐIỀU KHIỂN & AI", True, (255, 255, 255)), (20, y))
        y += 40
        
        diff_levels = ["Dễ", "Trung bình", "Khó", "Ác mộng", "Địa ngục"]
        diff_colors = { "Dễ": (0, 200, 83), "Trung bình": (255, 145, 0), "Khó": (255, 23, 68), "Ác mộng": (170, 0, 255), "Địa ngục": (213, 0, 0) }
        
        self.diff_buttons.clear() 
        bx, by = 20, y
        for diff in diff_levels:
            text_surf = self.font_sm.render(diff, True, (255, 255, 255))
            bw = text_surf.get_width() + 16
            if bx + bw > 300: bx = 20; by += 30
            rect = pygame.Rect(bx, by, bw, 24)
            self.diff_buttons[diff] = rect
            
            is_hovered = rect.collidepoint(mouse_pos)
            base_col = diff_colors[diff] if diff == self.difficulty else ((80, 90, 100) if is_hovered else (45, 55, 65))
            pygame.draw.rect(self.screen, base_col, rect, border_radius=12)
            if diff == self.difficulty: pygame.draw.rect(self.screen, (255,255,255), rect, width=2, border_radius=12)
            self.screen.blit(text_surf, (bx + 8, by + 4))
            bx += bw + 8 
            
        y = by + 35
        
        groups = [
            ("NHÓM 1: TÌM KIẾM MÙ", ["BFS", "DFS", "IDS"]),
            ("NHÓM 2: CÓ THÔNG TIN", ["UCS", "Greedy", "A*", "IDA*"]),
            ("NHÓM 3: TÌM KIẾM CỤC BỘ", ["HC Simple", "HC Steepest", "HC Stochastic", "HC Restart", "Beam Search", "Simulated Annealing"]),
            ("NHÓM 4: MÔI TRƯỜNG PHỨC TẠP", ["Multi-Goal", "Sensorless", "AND-OR Graph"]),
            ("NHÓM 5: CSP & RÀNG BUỘC", ["CSP Pathfinding"])
        ]
        
        self.ui_buttons.clear()
        
        for g_title, algos in groups:
            pygame.draw.line(self.screen, (60, 70, 80), (20, y), (300, y), 1)
            y += 8
            self.screen.blit(self.font_md.render(g_title, True, (200, 210, 220)), (20, y))
            y += 25
            
            for i, algo in enumerate(algos):
                col = i % 2
                rx = 20 + col * 140
                rect = pygame.Rect(rx, y, 135, 28)
                self.ui_buttons[algo] = rect
                
                is_hovered = rect.collidepoint(mouse_pos)
                if algo == self.demo_ai_name:
                    pygame.draw.rect(self.screen, (70, 80, 100), rect, border_radius=6)
                    pygame.draw.rect(self.screen, (255,255,255), rect, width=1, border_radius=6)
                else:
                    pygame.draw.rect(self.screen, (40, 48, 60) if is_hovered else (30, 35, 45), rect, border_radius=6)
                    
                pygame.draw.circle(self.screen, COLORS[algo], (rx + 12, y + 14), 5)
                self.screen.blit(self.font_sm.render(algo, True, (255,255,255)), (rx + 24, y + 6))
                
                if col == 1 or i == len(algos)-1: y += 35

        y += 10
        pygame.draw.rect(self.screen, (40, 50, 60), (20, y, 280, 45), border_radius=8)
        self.screen.blit(self.font_md.render(f"Người chơi: {self.player.moves} bước", True, TARGET_COLOR), (35, y + 12))
        
        y += 60
        instr = [
            ("M / N:", "Đổi Map / Đổi vị trí đứng"),
            ("SPACE:", "Cho AI Đua tất cả"),
            ("Chuột:", "Click chọn AI chạy đơn")
        ]
        for key, desc in instr:
            self.screen.blit(self.font_sm.render(key, True, (255,255,255)), (20, y))
            self.screen.blit(self.font_sm.render(desc, True, TEXT_COLOR), (80, y))
            y += 22

    def draw_right_panel(self):
        px = OFFSET_X + GRID_SIZE*CELL_SIZE + 40
        pygame.draw.rect(self.screen, PANEL_BG, (px, 0, WIDTH - px, HEIGHT))
        pygame.draw.line(self.screen, (50, 60, 70), (px, 0), (px, HEIGHT), 2)
        
        self.screen.blit(self.font_lg.render("BẢNG HIỂN THỊ LOG", True, (255, 255, 255)), (px + 20, 15))
        pygame.draw.line(self.screen, (60, 70, 80), (px + 20, 55), (WIDTH - 20, 55), 1)
        
        ly = 70
        for log in self.logs[::-1]: 
            text = log["text"]; color = log["color"]
            words = text.split(" ")
            lines = []; curr_line = ""
            for w in words:
                if self.font_log.size(curr_line + w)[0] < (WIDTH - px - 40): curr_line += w + " "
                else: lines.append(curr_line); curr_line = w + " "
            lines.append(curr_line)
            
            for line in lines:
                self.screen.blit(self.font_log.render("> " + line, True, color), (px + 20, ly))
                ly += 20
            
            ly += 5
            if ly > HEIGHT - 30: break

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.shadow_surface.fill((0,0,0,0)) 
        self.trail_surface.fill((0,0,0,0)) 
        
        mouse_pos = pygame.mouse.get_pos()
        self.draw_left_panel(mouse_pos)
        self.draw_right_panel()

        board_rect = pygame.Rect(OFFSET_X-8, OFFSET_Y-8, CELL_SIZE*GRID_SIZE+16, CELL_SIZE*GRID_SIZE+16)
        pygame.draw.rect(self.screen, BOARD_BG, board_rect, border_radius=12)
        pygame.draw.rect(self.screen, (200, 205, 215), board_rect, width=3, border_radius=12)
        
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x, y = OFFSET_X + c*CELL_SIZE, OFFSET_Y + r*CELL_SIZE
                tile_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, TILE_COLOR, tile_rect)
                pygame.draw.rect(self.screen, TILE_LINE, tile_rect, 1)

        def draw_target(pos, base_col):
            tx, ty = OFFSET_X + pos[0]*CELL_SIZE + CELL_SIZE//2, OFFSET_Y + pos[1]*CELL_SIZE + CELL_SIZE//2
            pulse = math.sin(time_tick / 150) * 3
            pygame.draw.circle(self.screen, (*base_col, 50), (tx, ty), 18 + pulse)
            pts = []
            for i in range(8):
                r = 16 if i % 2 == 0 else 6
                theta = math.radians(angle + i * 45)
                pts.append((tx + r * math.cos(theta), ty + r * math.sin(theta)))
            pygame.draw.polygon(self.screen, (50,50,50), pts)
            
            pts2 = []
            for i in range(8):
                r = 12 if i % 2 == 0 else 5
                theta = math.radians(-angle*1.5 + i * 45)
                pts2.append((tx + r * math.cos(theta), ty + r * math.sin(theta)))
            pygame.draw.polygon(self.screen, base_col, pts2)
            pygame.draw.circle(self.screen, (255,255,255), (tx, ty), 4)

        time_tick = pygame.time.get_ticks()
        angle = time_tick / 5 % 360
        tgt_color = (230, 40, 40) if self.difficulty == "Địa ngục" else TARGET_COLOR
        
        draw_target(self.target_pos, tgt_color)
        if self.target_pos_2: draw_target(self.target_pos_2, TARGET_2_COLOR)

        for p1, p2 in self.walls: self.draw_thick_wall(p1, p2)

        for r in self.robots:
            if r.trail:
                for i, (tr_x, tr_y, alpha, is_teleport) in enumerate(r.trail):
                    if alpha > 0 and not is_teleport:
                        size = 8 * (alpha / 255)
                        pygame.draw.circle(self.trail_surface, (*r.color, int(alpha)), (int(tr_x), int(tr_y)), int(size))
        self.screen.blit(self.trail_surface, (0,0))

        active_racer = None
        if self.demo_ai_name:
            active_racer = next((r for r in self.robots if r.name == self.demo_ai_name), None)
        elif self.is_racing and self.current_racer_idx < len(self.robots):
            active_racer = self.robots[self.current_racer_idx]
        else: active_racer = self.player
            
        for r in self.robots:
            if r == active_racer: continue
            rx, ry = OFFSET_X + r.visual_pos[0] + CELL_SIZE//2, OFFSET_Y + r.visual_pos[1] + CELL_SIZE//2
            self.draw_3d_robot(self.screen, rx, ry, r.color)
            if r.name == "Người Chơi": pygame.draw.circle(self.screen, (0,0,0), (rx, ry-3), 4)

        if active_racer:
            rx, ry = OFFSET_X + active_racer.visual_pos[0] + CELL_SIZE//2, OFFSET_Y + active_racer.visual_pos[1] + CELL_SIZE//2
            if self.demo_ai_name: pygame.draw.circle(self.screen, (255,255,255, 100), (rx, ry), 24, 2)
            self.draw_3d_robot(self.screen, rx, ry, active_racer.color)
            if active_racer.name == "Người Chơi": pygame.draw.circle(self.screen, (0,0,0), (rx, ry-3), 4)

        self.screen.blit(self.shadow_surface, (0,0))
        
        hovering = any(rect.collidepoint(mouse_pos) for rect in self.diff_buttons.values()) or \
                   any(rect.collidepoint(mouse_pos) for rect in self.ui_buttons.values())
        if hovering: pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else: pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        pygame.display.flip()

    def get_robot_by_name(self, name):
        return next((r for r in self.robots if r.name == name), None)

    def trigger_ai_race(self):
        self.demo_ai_name = None 
        self.target_pos_2 = None 
        self.reset_positions()
        self.is_racing = True
        self.current_racer_idx = 1 
        self.log_msg("Đang chạy tính toán cuộc đua tất cả AI...", (255, 200, 0))
        
        for r in self.robots[1:]:
            r.path = self.compute_path_for_ai(r)
            status = len(r.path) if r.path else "Failed"
            self.leaderboard[r.name] = status
            
        self.log_msg("Bắt đầu cuộc đua trực tiếp!", (0, 255, 0))

    def trigger_demo_ai(self, algo_name):
        self.demo_ai_name = algo_name
        self.target_pos_2 = None 
        self.reset_positions()
        r = self.get_robot_by_name(algo_name)
        
        self.log_msg(f"Tiến hành chạy: {algo_name}", (100, 200, 255))
        r.full_path = self.compute_path_for_ai(r)
        
        if r.full_path:
            self.log_msg(f"-> {algo_name} tìm thấy đích sau {len(r.full_path)} bước.", (0, 255, 0))
            r.path.extend(r.full_path)
            r.full_path = []
        else:
            if algo_name in ["HC Simple", "HC Steepest", "HC Stochastic"]:
                self.log_msg(f"-> {algo_name} KẸT CỤC BỘ (Local Minimum).", (255, 100, 100))
            else:
                self.log_msg(f"-> {algo_name} Không tìm thấy đường đi.", (255, 100, 100))

    def player_move(self, dx, dy):
        if self.is_racing or self.demo_ai_name or self.player.finished or self.player.path: return
        obstacles = set() 
        dest = self.get_slide_dest(tuple(self.player.logic_pos), (dx, dy), obstacles)
        
        if dest != tuple(self.player.logic_pos):
            self.player.path.append(dest) 
            self.player.logic_pos = list(dest)
            self.player.moves += 1
            if dest == self.target_pos:
                self.player.finished = True
                self.log_msg(f"Player đã hoàn thành trong {self.player.moves} bước!", (255, 255, 0))

    def update(self):
        for r in self.robots:
            new_trail = []
            for tx, ty, alpha, is_teleport in r.trail:
                if alpha > 8: new_trail.append((tx, ty, alpha - 8, is_teleport)) 
            r.trail = new_trail

        def move_robot_visual(r):
            if r.path:
                target_px = [r.path[0][0]*CELL_SIZE, r.path[0][1]*CELL_SIZE]
                dx, dy = target_px[0] - r.visual_pos[0], target_px[1] - r.visual_pos[1]
                dist = math.hypot(dx, dy)
                is_teleport = abs(dx) > 0 and abs(dy) > 0
                if not is_teleport: r.trail.append((OFFSET_X + r.visual_pos[0] + CELL_SIZE//2, OFFSET_Y + r.visual_pos[1] + CELL_SIZE//2, 255, False))
                
                max_speed = 30.0 if self.demo_ai_name else 45.0
                accel = 1.5 if self.demo_ai_name else 2.5
                r.current_speed += accel
                if r.current_speed > max_speed: r.current_speed = max_speed

                if is_teleport or dist < r.current_speed:
                    r.visual_pos = target_px; r.path.pop(0); r.current_speed = 5.0 
                else:
                    r.visual_pos[0] += (dx/dist) * r.current_speed; r.visual_pos[1] += (dy/dist) * r.current_speed

        if self.demo_ai_name: r = self.get_robot_by_name(self.demo_ai_name); move_robot_visual(r); return
        if not self.is_racing: move_robot_visual(self.player); return
            
        if self.current_racer_idx >= len(self.robots): return
        r = self.robots[self.current_racer_idx]
        
        if not r.path: r.finished = True; self.current_racer_idx += 1; return
        move_robot_visual(r)
        if not r.path: r.finished = True; self.current_racer_idx += 1 

    def main_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                    for diff, rect in self.diff_buttons.items():
                        if rect.collidepoint(event.pos) and self.difficulty != diff: self.difficulty = diff; self.load_map()
                                
                    for ai_name, rect in self.ui_buttons.items():
                        if rect.collidepoint(event.pos): self.trigger_demo_ai(ai_name)
                                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m: self.load_map()
                    elif event.key == pygame.K_n: self.randomize_start_position()
                    elif event.key == pygame.K_SPACE: self.trigger_ai_race()
                    elif event.key in (pygame.K_UP, pygame.K_w): self.player_move(0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s): self.player_move(0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a): self.player_move(-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d): self.player_move(1, 0)

            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = RicochetArena()
    game.main_loop()