import pygame
import sys
import math
import heapq
import itertools
import random
from collections import deque

# --- CẤU HÌNH ---
WIDTH, HEIGHT = 1250, 760
GRID_SIZE = 16
CELL_SIZE = 640 // GRID_SIZE
OFFSET_X, OFFSET_Y = 40, 80
FPS = 60

# --- BẢNG MÀU BOARDGAME CAO CẤP ---
BG_COLOR = (245, 247, 250)         
BOARD_BG = (220, 224, 232)         
TILE_COLOR = (252, 253, 255)       
TILE_LINE = (210, 215, 225)        
WALL_COLOR = (55, 65, 81)          
SHADOW_COLOR = (0, 0, 0, 50)       
TARGET_COLOR = (255, 193, 7)       

SIDEBAR_BG = (24, 28, 36)
TEXT_COLOR = (180, 190, 200)

COLORS = {
    "Người Chơi": (250, 250, 250),
    "BFS": (41, 121, 255),
    "DFS": (255, 23, 68),
    "IDS": (255, 145, 0),
    "UCS": (213, 0, 249),
    "Greedy": (0, 230, 118),
    "A*": (255, 234, 0),
    "IDA*": (0, 229, 255),
    "HC Simple": (255, 105, 180),    
    "HC Steepest": (255, 140, 0),    
    "HC Stochastic": (0, 206, 209),  
    "HC Restart": (147, 112, 219)    
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
        pygame.display.set_caption("Ricochet AI: Perfect Trace Edition")
        self.clock = pygame.time.Clock()
        self.font_sm = pygame.font.SysFont("Segoe UI", 16)
        self.font_md = pygame.font.SysFont("Segoe UI", 22, bold=True)
        self.font_lg = pygame.font.SysFont("Segoe UI", 32, bold=True)
        
        self.level = 1
        self.difficulty = "Khó" 
        self.walls = set()
        self.target_pos = (7, 7)
        
        self.is_racing = False
        self.current_racer_idx = 0 
        self.demo_ai_name = None 
        self.leaderboard = {} 
        
        self.counter = itertools.count() 
        self.shadow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        self.level_buttons = {} 
        self.diff_buttons = {} 
        self.ai_buttons = {} 
        
        self.load_level(1)

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

    def get_random_valid_pos(self, obstacles, current_pos=None):
        center_block = {(7,7), (8,7), (7,8), (8,8)}
        while True:
            sx, sy = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            pos = (sx, sy)
            if pos != self.target_pos and pos not in center_block and pos not in obstacles:
                # Bắt buộc vị trí mới phải chéo (khác trục X và Y) để chắc chắn tạo hiệu ứng Teleport
                if current_pos:
                    if pos[0] != current_pos[0] and pos[1] != current_pos[1]:
                        return pos
                else:
                    return pos

    def load_level(self, level):
        self.level = level
        self.demo_ai_name = None 
        self.leaderboard = {} 
        common_start = self.generate_random_map()
        
        if level == 1:
            self.robots = [Robot("Người Chơi", common_start), Robot("BFS", common_start),
                           Robot("DFS", common_start), Robot("IDS", common_start)]
        elif level == 2:
            self.robots = [Robot("Người Chơi", common_start), Robot("UCS", common_start),
                           Robot("Greedy", common_start), Robot("A*", common_start),
                           Robot("IDA*", common_start)]
        elif level == 3: 
            self.robots = [Robot("Người Chơi", common_start), 
                           Robot("HC Simple", common_start),
                           Robot("HC Steepest", common_start), 
                           Robot("HC Stochastic", common_start),
                           Robot("HC Restart", common_start)]
                           
        self.player = self.robots[0]
        self.reset_positions()

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

    # --- THUẬT TOÁN AI ---
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
                h_new = self.heuristic(n)
                g_new = g + h_new
                f_new = g_new + h_new
                if n not in vis or g_new < vis[n]:
                    vis[n] = g_new
                    heapq.heappush(pq, (f_new, g_new, next(self.counter), n, p+[n]))
        return []

    def run_idastar(self, start, obs):
        def search(path, g, bound, vis):
            c = path[-1]; h = self.heuristic(c); f = g + h
            if f > bound: return f
            if c == self.target_pos: return "FOUND"
            min_bound = float('inf')
            for n in self.get_neighbors(c, obs):
                h_new = self.heuristic(n); g_new = g + h_new
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
        curr = start
        curr_h = self.heuristic(curr)
        path = []
        for _ in range(50):
            if curr == self.target_pos: return path
            found_better = False
            for n in self.get_neighbors(curr, obs):
                n_h = self.heuristic(n)
                if n_h < curr_h:
                    curr = n; curr_h = n_h
                    path.append(curr); found_better = True; break 
            if not found_better: break 
        return path if curr == self.target_pos else []

    def run_hc_steepest(self, start, obs):
        curr = start
        curr_h = self.heuristic(curr)
        path = []
        for _ in range(50):
            if curr == self.target_pos: return path
            best_n, best_h = None, curr_h
            for n in self.get_neighbors(curr, obs):
                n_h = self.heuristic(n)
                if n_h < best_h:
                    best_h = n_h; best_n = n
            if best_n:
                curr = best_n; curr_h = best_h
                path.append(curr)
            else: break 
        return path if curr == self.target_pos else []

    def run_hc_stochastic(self, start, obs):
        curr = start
        curr_h = self.heuristic(curr)
        path = []
        for _ in range(50):
            if curr == self.target_pos: return path
            better_neighbors = []
            for n in self.get_neighbors(curr, obs):
                n_h = self.heuristic(n)
                if n_h < curr_h: better_neighbors.append((n, n_h))
            if not better_neighbors: break 
            next_node, next_h = random.choice(better_neighbors)
            curr = next_node; curr_h = next_h
            path.append(curr)
        return path if curr == self.target_pos else []

    def run_hc_random_restart(self, start, obs):
        max_restarts = 15
        global_path = [] # MẢNG MỚI: Lưu trữ TOÀN BỘ hành trình
        curr = start
        
        for i in range(max_restarts):
            if i > 0:
                # Bị kẹt -> Thực hiện bước Teleport và lưu vào mảng đường đi
                curr = self.get_random_valid_pos(obs, curr)
                global_path.append(curr)
                
            curr_h = self.heuristic(curr)
            stuck = False
            
            for _ in range(30):
                if curr == self.target_pos: return global_path
                best_n, best_h = None, curr_h
                for n in self.get_neighbors(curr, obs):
                    n_h = self.heuristic(n)
                    if n_h < best_h:
                        best_h = n_h; best_n = n
                        
                if best_n:
                    curr = best_n; curr_h = best_h
                    global_path.append(curr) # Lịch sử lưu cả bước trượt bình thường
                else:
                    stuck = True
                    break 
                    
            if not stuck and curr == self.target_pos: return global_path
            
        return global_path # Trả về tất cả mọi thứ dù cuối cùng vẫn không tìm ra đích

    # --- KẾT NỐI AI VỚI NÚT BẤM ---
    def compute_path_for_ai(self, r):
        obstacles = set()
        start_pos = tuple(r.logic_pos)
        if r.name == "BFS": return self.run_bfs(start_pos, obstacles)
        elif r.name == "DFS": return self.run_dfs(start_pos, obstacles)
        elif r.name == "IDS": return self.run_ids(start_pos, obstacles)
        elif r.name == "UCS": return self.run_ucs(start_pos, obstacles)
        elif r.name == "Greedy": return self.run_greedy(start_pos, obstacles)
        elif r.name == "A*": return self.run_astar(start_pos, obstacles)
        elif r.name == "IDA*": return self.run_idastar(start_pos, obstacles)
        elif r.name == "HC Simple": return self.run_hc_simple(start_pos, obstacles)
        elif r.name == "HC Steepest": return self.run_hc_steepest(start_pos, obstacles)
        elif r.name == "HC Stochastic": return self.run_hc_stochastic(start_pos, obstacles)
        elif r.name == "HC Restart": return self.run_hc_random_restart(start_pos, obstacles)
        return []

    # ================= HỆ THỐNG ĐỒ HỌA (UI/UX) =================
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
            pygame.draw.line(self.screen, (100, 110, 120), (rect.left, rect.top), (rect.left, rect.bottom), 1)
        else:
            x1, x2 = OFFSET_X + p1[0] * CELL_SIZE, OFFSET_X + (p1[0] + 1) * CELL_SIZE
            y = OFFSET_Y + p2[1] * CELL_SIZE
            rect = pygame.Rect(x1 - thickness//2, y - thickness//2 + 1, CELL_SIZE + thickness, thickness)
            pygame.draw.rect(self.shadow_surface, SHADOW_COLOR, rect.move(3, 4))
            pygame.draw.rect(self.screen, WALL_COLOR, rect, border_radius=4)
            pygame.draw.line(self.screen, (100, 110, 120), (rect.left, rect.top), (rect.right, rect.top), 1)

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.shadow_surface.fill((0,0,0,0)) 
        self.trail_surface.fill((0,0,0,0)) 
        
        mouse_pos = pygame.mouse.get_pos()
        hovering_any = False

        self.level_buttons.clear()
        self.level_buttons[1] = pygame.Rect(OFFSET_X, 15, 160, 50)
        self.level_buttons[2] = pygame.Rect(OFFSET_X + 160, 15, 240, 50)
        self.level_buttons[3] = pygame.Rect(OFFSET_X + 400, 15, 220, 50)
        
        for lvl, rect in self.level_buttons.items():
            if rect.collidepoint(mouse_pos):
                hovering_any = True

        pygame.draw.rect(self.screen, (255,255,255), (OFFSET_X, 15, 620, 50), border_radius=10)
        pygame.draw.rect(self.screen, (200,205,215), (OFFSET_X, 15, 620, 50), width=1, border_radius=10)
        
        c1 = (20,30,40) if self.level == 1 else ((100,110,120) if self.level_buttons[1].collidepoint(mouse_pos) else (150,150,150))
        c2 = (20,30,40) if self.level == 2 else ((100,110,120) if self.level_buttons[2].collidepoint(mouse_pos) else (150,150,150))
        c3 = (20,30,40) if self.level == 3 else ((100,110,120) if self.level_buttons[3].collidepoint(mouse_pos) else (150,150,150))
        
        self.screen.blit(self.font_md.render("Màn 1: Mù", True, c1), (OFFSET_X+20, 25))
        self.screen.blit(self.font_md.render("Màn 2: Thông Tin", True, c2), (OFFSET_X+180, 25))
        self.screen.blit(self.font_md.render("Màn 3: Leo Đồi", True, c3), (OFFSET_X+420, 25))
        
        if self.level == 1: pygame.draw.line(self.screen, (255,60,80), (OFFSET_X+20, 55), (OFFSET_X+130, 55), 4)
        elif self.level == 2: pygame.draw.line(self.screen, (255,60,80), (OFFSET_X+180, 55), (OFFSET_X+380, 55), 4)
        else: pygame.draw.line(self.screen, (255,60,80), (OFFSET_X+420, 55), (OFFSET_X+580, 55), 4)

        board_rect = pygame.Rect(OFFSET_X-8, OFFSET_Y-8, CELL_SIZE*GRID_SIZE+16, CELL_SIZE*GRID_SIZE+16)
        pygame.draw.rect(self.screen, BOARD_BG, board_rect, border_radius=12)
        pygame.draw.rect(self.screen, (200, 205, 215), board_rect, width=3, border_radius=12)
        
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x, y = OFFSET_X + c*CELL_SIZE, OFFSET_Y + r*CELL_SIZE
                tile_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, TILE_COLOR, tile_rect)
                pygame.draw.rect(self.screen, TILE_LINE, tile_rect, 1)
                pygame.draw.line(self.screen, (235, 240, 245), (x + CELL_SIZE//2, y + 10), (x + CELL_SIZE//2, y + CELL_SIZE - 10), 2)
                pygame.draw.line(self.screen, (235, 240, 245), (x + 10, y + CELL_SIZE//2), (x + CELL_SIZE - 10, y + CELL_SIZE//2), 2)

        tx, ty = OFFSET_X + self.target_pos[0]*CELL_SIZE + CELL_SIZE//2, OFFSET_Y + self.target_pos[1]*CELL_SIZE + CELL_SIZE//2
        time_tick = pygame.time.get_ticks()
        pulse = math.sin(time_tick / 150) * 3
        angle = time_tick / 5 % 360
        tgt_color = (230, 40, 40) if self.difficulty == "Địa ngục" else TARGET_COLOR
        
        pygame.draw.circle(self.screen, (*tgt_color, 50), (tx, ty), 18 + pulse)
        
        def draw_rotating_star(surface, color, radius, points, angle_offset):
            pts = []
            for i in range(points * 2):
                r = radius if i % 2 == 0 else radius / 2.5
                theta = math.radians(angle_offset + i * (360 / (points * 2)))
                pts.append((tx + r * math.cos(theta), ty + r * math.sin(theta)))
            pygame.draw.polygon(surface, color, pts)
            
        draw_rotating_star(self.screen, (50,50,50), 16, 4, angle) 
        draw_rotating_star(self.screen, tgt_color, 12, 4, -angle*1.5) 
        pygame.draw.circle(self.screen, (255,255,255), (tx, ty), 4) 

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
        else:
            active_racer = self.player
            
        for r in self.robots:
            if r == active_racer: continue
            rx, ry = OFFSET_X + r.visual_pos[0] + CELL_SIZE//2, OFFSET_Y + r.visual_pos[1] + CELL_SIZE//2
            self.draw_3d_robot(self.screen, rx, ry, r.color)
            if r.name == "Người Chơi": pygame.draw.circle(self.screen, (0,0,0), (rx, ry-3), 4)

        if active_racer:
            rx, ry = OFFSET_X + active_racer.visual_pos[0] + CELL_SIZE//2, OFFSET_Y + active_racer.visual_pos[1] + CELL_SIZE//2
            if self.demo_ai_name: 
                pygame.draw.circle(self.screen, (255,255,255, 100), (rx, ry), 24, 2)
            self.draw_3d_robot(self.screen, rx, ry, active_racer.color)
            if active_racer.name == "Người Chơi": pygame.draw.circle(self.screen, (0,0,0), (rx, ry-3), 4)

        self.screen.blit(self.shadow_surface, (0,0))

        # --- Sidebar Khung Điều khiển ---
        sb_x = OFFSET_X + CELL_SIZE*GRID_SIZE + 40
        pygame.draw.rect(self.screen, SIDEBAR_BG, (sb_x, 0, WIDTH-sb_x, HEIGHT))
        
        y = 20
        self.screen.blit(self.font_lg.render("BẢNG XẾP HẠNG", True, (255, 255, 255)), (sb_x + 30, y))
        y += 50
        
        diff_levels = ["Dễ", "Trung bình", "Khó", "Ác mộng", "Địa ngục"]
        diff_colors = {
            "Dễ": (0, 200, 83), "Trung bình": (255, 145, 0), 
            "Khó": (255, 23, 68), "Ác mộng": (170, 0, 255), "Địa ngục": (213, 0, 0)
        }
        
        self.diff_buttons.clear() 
        bx, by = sb_x + 30, y
        
        for diff in diff_levels:
            text_surf = self.font_sm.render(diff, True, (255, 255, 255))
            bw = text_surf.get_width() + 24
            bh = 32
            if bx + bw > WIDTH - 20: 
                bx = sb_x + 30
                by += 40
            rect = pygame.Rect(bx, by, bw, bh)
            self.diff_buttons[diff] = rect
            is_hovered = rect.collidepoint(mouse_pos)
            if is_hovered: hovering_any = True
            
            base_col = diff_colors[diff] if diff == self.difficulty else ((80, 90, 100) if is_hovered else (45, 55, 65))
            pygame.draw.rect(self.screen, base_col, rect, border_radius=16)
            if diff == self.difficulty: pygame.draw.rect(self.screen, (255,255,255), rect, width=2, border_radius=16)
            self.screen.blit(text_surf, (bx + 12, by + 5))
            bx += bw + 10 
            
        y = by + 50
        
        bg_col = (50, 60, 75) if (not self.is_racing and not self.demo_ai_name) else (30, 35, 45)
        pygame.draw.rect(self.screen, bg_col, (sb_x + 30, y, 260, 55), border_radius=10)
        self.screen.blit(self.font_md.render(f"Người chơi: {self.player.moves} bước", True, (255,255,255)), (sb_x + 45, y + 12))
        y += 70
        
        self.ai_buttons.clear()
        for i, r in enumerate(self.robots[1:], 1):
            rect = pygame.Rect(sb_x + 25, y - 8, 270, 40)
            self.ai_buttons[r.name] = rect
            is_hovered = rect.collidepoint(mouse_pos)
            if is_hovered: hovering_any = True
            
            if r.name == self.demo_ai_name:
                pygame.draw.rect(self.screen, (50, 60, 80), rect, border_radius=8)
                pygame.draw.rect(self.screen, (255,255,255), rect, width=1, border_radius=8)
            elif is_hovered:
                pygame.draw.rect(self.screen, (40, 48, 60), rect, border_radius=8)

            res = self.leaderboard.get(r.name, "--")
            if self.demo_ai_name == r.name:
                left = len(r.full_path)
                res = f"Còn {left} bước" if left > 0 else ("Kẹt!" if r.name == "HC Restart" and res == "Failed" else "Xong")
            elif self.is_racing and i == self.current_racer_idx: 
                res = "Đang chạy 🏃"
            elif self.is_racing and i > self.current_racer_idx:
                res = "Chờ lượt..."
            
            txt = f"{r.name}: {res}"
            pygame.draw.circle(self.screen, r.color, (sb_x + 45, y + 12), 10)
            text_color = (255,255,255) if (self.is_racing and i == self.current_racer_idx) or (r.name == self.demo_ai_name) else TEXT_COLOR
            self.screen.blit(self.font_md.render(txt, True, text_color), (sb_x + 65, y - 2))
            y += 44

        if hovering_any: pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else: pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        y = HEIGHT - 180
        pygame.draw.line(self.screen, (60, 70, 80), (sb_x + 30, y), (WIDTH-30, y), 2)
        
        mode_text = "CHẾ ĐỘ TỪNG BƯỚC" if self.demo_ai_name else "CHẾ ĐỘ CHƠI TỰ DO"
        self.screen.blit(self.font_md.render(mode_text, True, TARGET_COLOR), (sb_x + 30, y + 10))
        
        if self.demo_ai_name:
            instr = [
                ("ENTER:", "Tiến 1 bước (Step-by-step)"),
                ("SPACE:", "Tự động chạy nốt"),
                ("Phím R:", "Thoát chế độ này")
            ]
        else:
            instr = [
                ("Click Chuột:", "Chọn Màn / Độ Khó / Báo cáo"),
                ("Phím M / N:", "Đổi Map mới / Đổi vị trí đứng"),
                ("SPACE:", "Cho AI Đua tất cả"),
                ("Phím R:", "Chơi lại từ đầu")
            ]
            
        y += 45
        for key, desc in instr:
            self.screen.blit(self.font_sm.render(key, True, (255,255,255)), (sb_x + 30, y))
            self.screen.blit(self.font_sm.render(desc, True, TEXT_COLOR), (sb_x + 130, y))
            y += 28

        pygame.display.flip()

    def get_robot_by_name(self, name):
        return next((r for r in self.robots if r.name == name), None)

    def trigger_ai_race(self):
        self.demo_ai_name = None 
        self.reset_positions()
        self.is_racing = True
        self.current_racer_idx = 1 
        for r in self.robots[1:]:
            r.path = self.compute_path_for_ai(r)
            self.leaderboard[r.name] = len(r.path) if r.path else "Failed"

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
                self.leaderboard["Người Chơi"] = self.player.moves

    def update(self):
        speed = 10 
        
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
                
                is_teleport = False
                # Nếu đi chéo (cả dx và dy đều > 0) thì chắc chắn là Teleport
                if abs(dx) > 0 and abs(dy) > 0:
                    is_teleport = True 
                
                if not is_teleport:
                    r.trail.append((OFFSET_X + r.visual_pos[0] + CELL_SIZE//2, OFFSET_Y + r.visual_pos[1] + CELL_SIZE//2, 255, False))
                
                max_speed = 18.0 if self.demo_ai_name else 45.0
                accel = 0.8 if self.demo_ai_name else 2.5
                
                r.current_speed += accel
                if r.current_speed > max_speed:
                    r.current_speed = max_speed

                if is_teleport or dist < r.current_speed:
                    r.visual_pos = target_px
                    r.path.pop(0) 
                    r.current_speed = 5.0 
                else:
                    r.visual_pos[0] += (dx/dist) * r.current_speed
                    r.visual_pos[1] += (dy/dist) * r.current_speed

        if self.demo_ai_name:
            r = self.get_robot_by_name(self.demo_ai_name)
            move_robot_visual(r)
            return

        if not self.is_racing:
            move_robot_visual(self.player)
            return
            
        if self.current_racer_idx >= len(self.robots): return
        r = self.robots[self.current_racer_idx]
        
        if not r.path:
            r.finished = True
            self.current_racer_idx += 1 
            return
            
        move_robot_visual(r)
        if not r.path:
            r.finished = True
            self.current_racer_idx += 1 

    def main_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                    for lvl, rect in self.level_buttons.items():
                        if rect.collidepoint(event.pos):
                            if self.level != lvl:
                                self.load_level(lvl)
                                
                    for diff, rect in self.diff_buttons.items():
                        if rect.collidepoint(event.pos):
                            if self.difficulty != diff:
                                self.difficulty = diff
                                self.load_level(self.level)
                                
                    for ai_name, rect in self.ai_buttons.items():
                        if rect.collidepoint(event.pos):
                            self.demo_ai_name = ai_name
                            self.reset_positions()
                            r = self.get_robot_by_name(ai_name)
                            r.full_path = self.compute_path_for_ai(r)
                            self.leaderboard[r.name] = len(r.full_path) if r.full_path else "Failed"
                                
                if event.type == pygame.KEYDOWN:
                    if self.demo_ai_name:
                        r = self.get_robot_by_name(self.demo_ai_name)
                        if event.key == pygame.K_RETURN or event.key == pygame.K_RIGHT:
                            if not r.path and r.full_path:
                                r.path.append(r.full_path.pop(0))
                        elif event.key == pygame.K_SPACE:
                            if r.full_path:
                                r.path.extend(r.full_path)
                                r.full_path = []
                        elif event.key == pygame.K_r:
                            self.demo_ai_name = None 
                            self.reset_positions()
                    else:
                        if event.key == pygame.K_m: self.load_level(self.level)
                        elif event.key == pygame.K_n: self.randomize_start_position()
                        elif event.key == pygame.K_r: self.reset_positions()
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