import pygame
import sys
import math
import heapq
import itertools
import random
import json
import os
import threading
from collections import deque

# --- CẤU HÌNH ---
WIDTH, HEIGHT = 1280, 720
OFFSET_X, OFFSET_Y = 50, 75 # Đưa map sang trái
FPS = 60

# --- BẢNG MÀU PACMAN LAB THEME ---
BG_COLOR = (10, 15, 30)            # Nền tối
BOARD_BG = (15, 20, 40)            # Nền bảng
TILE_COLOR = (15, 20, 40)          # Ô lưới
TILE_LINE = (30, 45, 80)           # Viền lưới
WALL_COLOR = (0, 150, 255)         # Tường màu xanh neon
SHADOW_COLOR = (0, 0, 0, 150)      
TARGET_COLOR = (255, 193, 7)       
TARGET_2_COLOR = (0, 230, 118)
PANEL_BG = (15, 22, 45)            # Nền các panel
TEXT_COLOR = (180, 200, 220)
BORDER_GLOW = (0, 150, 255)

COLORS = {
    "Người Chơi": (250, 250, 250),
    "BFS": (41, 121, 255), "DFS": (255, 23, 68), "IDS": (255, 145, 0),
    "UCS": (213, 0, 249), "Greedy": (0, 230, 118), "A*": (255, 234, 0),
    "Simple HC": (255, 105, 180), "Local Beam": (100, 181, 246), "Simulated Annealing": (255, 82, 82),
    "Partial-Observable": (0, 255, 127), "Sensorless": (255, 100, 255), "AND-OR Graph": (255, 255, 100),
    "Backtracking": (180, 100, 255), "AC-3": (147, 112, 219), "Min-Conflicts": (255, 140, 0),
    "Minimax": (255, 60, 60), "Alpha-Beta": (60, 255, 60), "Expectimax": (60, 60, 255),
    "Địch": (40, 40, 40)
}

ALGO_GROUPS = {
    "BFS": 1, "DFS": 1, "IDS": 1,
    "UCS": 2, "Greedy": 2, "A*": 2,
    "Simple HC": 3, "Local Beam": 3, "Simulated Annealing": 3,
    "Sensorless": 4, "Partial-Observable": 4, "AND-OR Graph": 4,
    "Backtracking": 5, "AC-3": 5, "Min-Conflicts": 5,
    "Minimax": 6, "Alpha-Beta": 6, "Expectimax": 6
}

ALGO_DESC = {
    "BFS": "Tìm kiếm theo chiều rộng. Mở rộng các nút nông nhất trước. Đảm bảo tối ưu số bước trên đồ thị không trọng số. Dùng Hàng đợi (Queue).",
    "DFS": "Tìm kiếm theo chiều sâu. Đi sâu nhất có thể trước khi quay lui. Dùng Ngăn xếp (Stack). Tốn ít bộ nhớ nhưng không đảm bảo tối ưu.",
    "IDS": "Tìm kiếm sâu lặp lại. Chạy DFS với giới hạn độ sâu tăng dần. Kết hợp ưu điểm tiết kiệm bộ nhớ của DFS và tính tối ưu của BFS.",
    "UCS": "Tìm kiếm chi phí đồng nhất. Mở rộng nút có tổng chi phí g(n) thấp nhất. Dùng Hàng đợi ưu tiên (Priority Queue).",
    "Greedy": "Tìm kiếm tham lam. Chỉ ưu tiên mở rộng nút có khoảng cách ước lượng h(n) gần đích nhất. Nhanh nhưng không đảm bảo tối ưu.",
    "A*": "Thuật toán A*. Kết hợp UCS và Greedy với f(n) = g(n) + h(n). Đảm bảo tìm được đường đi tối ưu nếu heuristic hợp lệ.",
    "Simple HC": "Leo đồi đơn giản (First-choice). Sinh lân cận, nếu gặp trạng thái tốt hơn thì chọn ngay và dừng sinh. Dễ mắc kẹt cực đại cục bộ.",
    "Local Beam": "Local Beam Search. Lưu lại k trạng thái tốt nhất trong mỗi vòng lặp thay vì chỉ 1. Giúp tránh việc bị kẹt ở ngõ cụt cục bộ.",
    "Simulated Annealing": "Luyện kim / Phôi thép. Cho phép đi lùi với xác suất giảm dần theo nhiệt độ T để thoát khỏi cực đại cục bộ.",
    "Sensorless": "Belief State. Tìm kiếm một chuỗi hành động ép buộc giúp robot đến đích bất kể nó xuất phát từ đâu trong tập hợp niềm tin.",
    "Partial-Observable": "Môi trường nhìn thấy một phần. Robot xuất phát với Belief_Start bị mù vị trí, phải tự di chuyển, đọc cảm biến và lọc giả thuyết cho đến khi đạt Belief_Goal (định vị được mình).",
    "AND-OR Graph": "Lập kế hoạch dự phòng (Contingency Plan) đối đối phó với môi trường có yếu tố bất định bằng các nhánh NẾU - THÌ.",
    "Backtracking": "CSP: Thỏa mãn Ràng Buộc. Coi bước đi là Biến, hướng là Miền giá trị. Quay lui nếu vi phạm ràng buộc cấm đâm tường.",
    "AC-3": "Rút gọn Miền giá trị bằng Arc Consistency trước khi tìm kiếm, loại bỏ ngay các hướng đi chắc chắn đâm tường.",
    "Min-Conflicts": "Khởi tạo mảng bước đi ngẫu nhiên đầy đủ, sau đó liên tục chọn và sửa lại các bước vi phạm để tối thiểu hóa xung đột.",
    "Minimax": "Đối kháng: Tìm kiếm nước đi tốt nhất với giả định Môi trường (Min) luôn cố gắng đặt vật cản làm robot (Max) đi xa nhất.",
    "Alpha-Beta": "Tối ưu hóa Minimax bằng cách cắt tỉa (Pruning) các nhánh không cần thiết, giúp tìm kiếm nhanh hơn ở độ sâu lớn hơn.",
    "Expectimax": "Môi trường ngẫu nhiên (Chance Node). Môi trường phản ứng ngẫu nhiên theo xác suất thay vì luôn tìm cách tối ưu để chặn robot."
}

class Robot:
    def __init__(self, name, pos):
        self.name = name
        self.logic_pos = list(pos)
        self.start_pos = list(pos)
        # Sửa lại dòng này: Khởi tạo mặc định bằng 0, Arena sẽ tự tính toán lại sau
        self.visual_pos = [0, 0] 
        self.color = COLORS.get(name, (255, 255, 255))
        self.path = []        
        self.moves = 0
        self.finished = False
        self.current_target = None

class RicochetArena:
    def __init__(self):
        pygame.init()
        # BẬT TÍNH NĂNG RESIZE: Cho phép kéo giãn/Phóng to toàn màn hình
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Ricochet Algorithm Laboratory")
        self.clock = pygame.time.Clock()
        
        self.font_sm = pygame.font.SysFont("Segoe UI", 14)
        self.font_md = pygame.font.SysFont("Segoe UI", 18, bold=True)
        self.font_lg = pygame.font.SysFont("Segoe UI", 28, bold=True)
        self.font_title = pygame.font.SysFont("Times New Roman", 40, bold=True)
        self.font_log = pygame.font.SysFont("Consolas", 13)
        
        self.walls = set()
        self.target_pos = (7, 7)
        self.target_pos_2 = None 
        
        self.state = "MENU" 
        self.current_ai = None
        self.edit_mode = 0 
        self.current_group_id = 1 
        self.sim_status = "Chờ lệnh" 
        
        self.logs = []
        self.log_scroll = 0 # BIẾN MỚI: Quản lý vị trí thanh cuộn
        self.counter = itertools.count() 
        self.shadow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        self.menu_buttons = {}
        self.sim_buttons = {}
        
        self.grid_size = 16
        self.grid_size = 16
        # --- BÀN CỜ TO HẾT CỠ BÁM THEO CHIỀU CAO ---
        self.board_size = HEIGHT - 200 
        self.cell_size = self.board_size // self.grid_size
        
        self.ai_is_computing = False     
        self.ai_result_path = None       
        self.ai_robot_computing = None   
        
        self.robots = [Robot(name, (0,0)) for name in COLORS.keys()]
        self.player = self.robots[0]
        
        # Khởi tạo Robot Địch riêng biệt
        self.enemy = Robot("Địch", (0, 0))

        # --- THÊM: Robot Bóng ma cho nhóm Sensorless ---
        self.sensorless_ghost = Robot("Bóng ma", (0, 0))
        self.sensorless_ghost.color = (120, 120, 120)

        # --- THÊM KHỞI TẠO 3 TRỢ THỦ CHO NHÓM CSP Ở ĐÂY ---
        self.aux_robots = [
            Robot("Trợ thủ 1", (0, 0)),
            Robot("Trợ thủ 2", (0, 0)),
            Robot("Trợ thủ 3", (0, 0))
        ]
        self.aux_robots[0].color = (150, 150, 150)
        self.aux_robots[1].color = (180, 100, 100)
        self.aux_robots[2].color = (100, 180, 100)
        # --------------------------------------------------

        self.log_msg("Hệ thống khởi động thành công.", (0, 255, 100))

    def log_msg(self, msg, color=(200, 220, 255)):
        self.logs.append({"text": msg, "color": color})
        if len(self.logs) > 1000: self.logs.pop(0) # Tăng lên lưu trữ 200 dòng
        self.log_scroll = 0 # Tự động cuộn xuống dưới cùng khi có log mới

    # Lấy đường dẫn của folder chứa file .py hiện tại
    def get_map_path(self, filename):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, filename)

    # ================= QUẢN LÝ MAP =================
    def save_custom_map(self):
        filename = self.get_map_path(f"ricochet_map_group_{self.current_group_id}.json")
        walls_list = [[list(p1), list(p2)] for p1, p2 in self.walls]
        data = {
            "grid_size": self.grid_size,
            "walls": walls_list, 
            "target": self.target_pos,
            "target_2": self.target_pos_2,
            "start": self.player.start_pos,
            "enemy_start": self.enemy.start_pos if hasattr(self, 'enemy') else [2,1],
            # --- LƯU THÊM VỊ TRÍ 3 TRỢ THỦ ---
            "aux_starts": [aux.start_pos for aux in getattr(self, 'aux_robots', [])]
        }
        try:
            with open(filename, "w") as f: json.dump(data, f)
            self.log_msg(f"Đã lưu Map tại: {os.path.basename(filename)}", (0, 255, 100))
        except Exception as e:
            self.log_msg(f"Lỗi lưu: {e}", (255, 50, 50))

    def load_map(self, group_id=None):
        if group_id is not None: self.current_group_id = group_id
        self.target_pos_2 = None 
        filename = self.get_map_path(f"ricochet_map_group_{self.current_group_id}.json")
        
        self.board_size = min(HEIGHT - 100, WIDTH - 680)
        
        if os.path.exists(filename):
            try:
                with open(filename, "r") as f: data = json.load(f)
                
                self.grid_size = data.get("grid_size", 16)
                self.cell_size = self.board_size // self.grid_size
                self.walls = {tuple((tuple(w[0]), tuple(w[1]))) for w in data["walls"]}
                self.target_pos = tuple(data["target"])
                t2 = data.get("target_2")
                self.target_pos_2 = tuple(t2) if t2 else None
                
                # Tải vị trí Ta
                st = data.get("start")
                common_start = tuple(st) if st else self.get_random_valid_pos(set())
                for r in self.robots: r.start_pos = list(common_start)
                
                # Tải vị trí Địch
                est = data.get("enemy_start")
                if hasattr(self, 'enemy'): 
                    self.enemy.start_pos = list(est) if est else list(self.get_random_valid_pos(set()))
                    
                # Tải vị trí Trợ thủ
                aux_st = data.get("aux_starts")
                if hasattr(self, 'aux_robots') and aux_st and len(aux_st) == len(self.aux_robots):
                    for i, aux in enumerate(self.aux_robots):
                        aux.start_pos = list(aux_st[i])
                        
                self.log_msg(f"Đã tải Map: {os.path.basename(filename)}", (0, 255, 255))
                self.reset_simulation()
                return # Tải thành công thì thoát hàm
            except Exception:
                pass # Lỗi file thì rơi xuống xử lý mặc định bên dưới
                
        # --- NẾU KHÔNG CÓ FILE HOẶC FILE LỖI -> DÙNG MAP MẶC ĐỊNH ---
        if self.current_group_id == 5:
            self.setup_csp_map()
        elif self.current_group_id == 6:
            self.setup_adversarial_map()
        else:
            self.grid_size = 16
            self.cell_size = self.board_size // 16
            common_start = self.generate_random_map()
            for r in self.robots: r.start_pos = list(common_start)
            if hasattr(self, 'enemy'): self.enemy.start_pos = list(self.get_random_valid_pos(set()))
            self.reset_simulation()

    def generate_random_map(self):
        best_walls = set(); best_target = (7, 7); best_start = (0, 0); max_steps = -1
        for attempt in range(150):
            self.walls.clear()
            for i in range(self.grid_size):
                self.walls.add(((-1, i), (0, i))); self.walls.add(((self.grid_size-1, i), (self.grid_size, i)))
                self.walls.add(((i, -1), (i, 0))); self.walls.add(((i, self.grid_size-1), (i, self.grid_size)))
            corners = []
            for _ in range(25):
                x, y = random.randint(1, self.grid_size-2), random.randint(1, self.grid_size-2)
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
                start = (random.randint(0, self.grid_size-1), random.randint(0, self.grid_size-1))
                if start == self.target_pos: continue
                path = self.run_bfs(start, set())
                if path:
                    if len(path) > max_steps:
                        max_steps = len(path); best_start = start; best_walls = self.walls.copy(); best_target = self.target_pos
                    if 4 <= len(path) <= 15: valid_starts.append(start)
            if valid_starts: return random.choice(valid_starts)
        if max_steps > 0:
            self.walls = best_walls; self.target_pos = best_target; return best_start
        return self.get_random_valid_pos(set())

    def reset_simulation(self):
        self.sim_status = "Chờ lệnh"
        if not hasattr(self, 'step_mode'): self.step_mode = False
        self.step_queue = [] 
        self.csp_domains = None # Dọn dẹp bóng ma AC-3
        self.belief_history = [] # Dọn dẹp bóng ma Partial-Observable
        
        # --- FIX: Nạp thêm 3 Trợ thủ vào danh sách Reset ---
        enemy_list = [self.enemy] if hasattr(self, 'enemy') else []
        ghost_list = [self.sensorless_ghost] if hasattr(self, 'sensorless_ghost') else []
        aux_list = getattr(self, 'aux_robots', [])
        
        for r in self.robots + enemy_list + ghost_list + aux_list:
            r.logic_pos = list(r.start_pos)
            r.visual_pos = [r.start_pos[0]*self.cell_size, r.start_pos[1]*self.cell_size]
            r.path = []
            r.moves = 0
            r.finished = False
            r.current_target = None 
            r.computed_path = []

    def get_slide_dest(self, pos, direction, obstacles, stop_on=None):
        dx, dy = direction; x, y = pos
        while True:
            nx, ny = x + dx, y + dy
            edge = ((x, y), (nx, ny)) if (x, y) < (nx, ny) else ((nx, ny), (x, y))
            if edge in self.walls or (nx, ny) in obstacles: break
            x, y = nx, ny
            # Nếu truyền vào tham số con mồi, Địch sẽ dừng lại ngay khi nuốt trọn Ta
            if stop_on and (x, y) == stop_on: break 
        return (x, y)

    def get_neighbors(self, pos, obstacles, stop_on=None):
        move = [(0,1), (0,-1), (1,0), (-1,0)]; random.shuffle(move)
        return [dest for d in move if (dest := self.get_slide_dest(pos, d, obstacles, stop_on)) != pos]

    def get_random_valid_pos(self, obstacles, current_pos=None):
        while True:
            pos = (random.randint(0, self.grid_size-1), random.randint(0, self.grid_size-1))
            if pos != self.target_pos and pos not in obstacles: return pos

    # ================= CÁC THUẬT TOÁN AI =================
    def heuristic(self, pos): return abs(pos[0] - self.target_pos[0]) + abs(pos[1] - self.target_pos[1])
    
    # ================= NHÓM 1: TÌM KIẾM MÙ (UNINFORMED SEARCH) =================
    def run_bfs(self, start, obs):
        self.log_msg("--- BẮT ĐẦU BFS (Duyệt theo chiều rộng) ---", COLORS["BFS"])
        
        # [MÃ GIẢ]: node <- NODE(problem.INITIAL)
        # [MÃ GIẢ]: if problem.IS-GOAL(node.STATE) then return node
        if start == self.target_pos: 
            return [] 
        
        # [MÃ GIẢ]: frontier <- a FIFO queue, with node as an element
        frontier = deque([(start, [])])
        # [MÃ GIẢ]: reached <- {problem.INITIAL}
        reached = {start}

        steps = 0
        # [MÃ GIẢ]: while not IS-EMPTY(frontier) do
        while frontier:
            # [MÃ GIẢ]: node <- POP(frontier) (Lấy ra phần tử đầu tiên - FIFO)
            current_node, path = frontier.popleft()

            steps += 1
            if steps <= 15 or steps % 50 == 0: 
                self.log_msg(f"[{steps}] BFS mở rộng: {current_node}, Hàng đợi còn: {len(frontier)}", (150, 180, 255))

            # [MÃ GIẢ]: for each child in EXPAND(problem, node) do
            for neighbor in self.get_neighbors(current_node, obs):
                # [MÃ GIẢ]: s <- child.STATE
                # [MÃ GIẢ]: if problem.IS-GOAL(s) then return child
                if neighbor == self.target_pos: 
                    self.log_msg(f"-> TÌM THẤY ĐÍCH! Tổng số nút đã duyệt: {steps}", (0, 255, 0))
                    return path + [neighbor] 
                
                # [MÃ GIẢ]: if s is not in reached then
                if neighbor not in reached: 
                    # [MÃ GIẢ]: add s to reached
                    reached.add(neighbor)
                    # [MÃ GIẢ]: add child to frontier
                    frontier.append((neighbor, path+[neighbor])) 

        self.log_msg("-> Bế tắc, không tìm thấy đường!", (255, 50, 50))            
        # [MÃ GIẢ]: return failure
        return []
    
    def run_dfs(self, start, obs):
        self.log_msg("--- BẮT ĐẦU DFS (Duyệt theo chiều sâu) ---", COLORS["DFS"])
        # [MÃ GIẢ]: node <- NODE(problem.INITIAL)
        # [MÃ GIẢ]: if problem.IS-GOAL(node.STATE) then return node
        if start == self.target_pos: return [] 
        
        # [MÃ GIẢ]: frontier <- a LIFO stack, with node as an element
        st = [(start, [])]
        frontier_states = {start} # Thêm set phụ để kiểm tra "child is not in frontier" nhanh hơn
        # [MÃ GIẢ]: reached <- {problem.INITIAL}
        reached = {start}
        
        # [MÃ GIẢ]: while not IS-EMPTY(frontier) do
        while st:
            # [MÃ GIẢ]: node <- POP(frontier)
            c, p = st.pop()
            if c in frontier_states: frontier_states.remove(c)
                
            if len(p) > 50: continue # Tránh giật lag
                
            # [MÃ GIẢ]: for each child in EXPAND(problem, node) do
            for n in self.get_neighbors(c, obs):
                # [MÃ GIẢ]: s <- child.STATE
                # [MÃ GIẢ]: if problem.IS-GOAL(s) then return child
                if n == self.target_pos: return p + [n] 
                
                # [MÃ GIẢ]: if s is not in reached and child is not in frontier then
                if n not in reached and n not in frontier_states: 
                    # [MÃ GIẢ]: add s to reached
                    reached.add(n)
                    # [MÃ GIẢ]: add child to frontier
                    st.append((n, p+[n])) 
                    frontier_states.add(n)
                    
        # [MÃ GIẢ]: return failure
        return []

    def run_ids(self, start, obs):
        self.log_msg("--- BẮT ĐẦU IDS (Duyệt sâu lặp lại) ---", COLORS["IDS"])
        # [MÃ GIẢ]: function DEPTH-LIMITED-SEARCH(problem, l)
        def depth_limited_search(limit):
            # [MÃ GIẢ]: frontier <- a LIFO queue (stack)
            st = [(start, [])] 
            # [MÃ GIẢ]: result <- failure
            result = "failure"

            # [MÃ GIẢ]: while not IS-EMPTY(frontier) do
            while st:
                # [MÃ GIẢ]: node <- POP(frontier)
                c, p = st.pop()

                # [MÃ GIẢ]: if problem.IS-GOAL(node.STATE) then return node
                if c == self.target_pos: return p

                # [MÃ GIẢ]: if DEPTH(node) >= l then result <- cutoff
                if len(p) >= limit:
                    result = "cutoff"
                # [MÃ GIẢ]: else if not IS-CYCLE(node) do (Chống chu trình)
                elif c not in p: 
                    # [MÃ GIẢ]: for each child in EXPAND(problem, node) do
                    for n in self.get_neighbors(c, obs):
                        # [MÃ GIẢ]: add child to frontier
                        st.append((n, p + [n]))
            # [MÃ GIẢ]: return result
            return result

        # [MÃ GIẢ]: function ITERATIVE-DEEPENING-SEARCH(problem)
        # [MÃ GIẢ]: for depth = 0 to infinity do
        for depth in range(0, 45): # Giới hạn 45 bước để tránh treo máy
            self.log_msg(f"-> Đang chạy DFS với Limit = {depth}", (200, 200, 200))
            # [MÃ GIẢ]: result <- DEPTH-LIMITED-SEARCH(problem, depth)
            res = depth_limited_search(depth)
            
            # [MÃ GIẢ]: if result != cutoff then return result
            if res != "cutoff" and res != "failure":
                self.log_msg(f"-> TÌM THẤY ĐÍCH tại độ sâu (Depth) = {depth}", (0, 255, 0))
                return res

        return []

    # ================= NHÓM 2: CÓ THÔNG TIN (HEURISTIC SEARCH) =================
    def run_ucs(self, start, obs):
        self.log_msg("--- BẮT ĐẦU UCS (Tìm kiếm chi phí đồng nhất) ---", (200, 150, 255))
        
        # [MÃ GIẢ]: 1. Khởi tạo tập FRONTIER = {Start} với g(Start) = 0
        g_costs = {start: 0}
        # (Dùng heapq để mô phỏng Priority Queue lấy g(n) nhỏ nhất)
        frontier = [(0, next(self.counter), start, [])] 
        frontier_set = {start}
        
        # [MÃ GIẢ]: 2. Khởi tạo tập REACHED = {}
        reached = set()

        steps = 0
        # [MÃ GIẢ]: 3. TRONG KHI (FRONTIER không rỗng):
        while frontier:
            # [MÃ GIẢ]: a. Chọn trạng thái n từ FRONTIER có g(n) nhỏ nhất.
            g_n, _, n, p = heapq.heappop(frontier)
            
            # (Đồng bộ xử lý heapq: Bỏ qua các bản sao cũ có g(n) đắt hơn)
            if n in frontier_set: 
                frontier_set.remove(n)
            else: 
                continue 

            steps += 1
            if steps <= 15 or steps % 50 == 0:
                self.log_msg(f"[{steps}] UCS xét nút {n} | Tổng chi phí g(n) = {g_n}", (200, 150, 255))

            # [MÃ GIẢ]: b. NẾU n == Goal: TRẢ VỀ "Thành công" và truy xuất lại đường đi
            # (UCS kiểm tra đích TRỄ - lấy ra khỏi frontier mới check để đảm bảo đường đi là tối ưu nhất)
            if n == self.target_pos:
                self.log_msg(f"-> TÌM THẤY ĐÍCH! Chi phí tối ưu g(n) = {g_n}", (0, 255, 0))
                return p

            # [MÃ GIẢ]: c. Loại bỏ n khỏi FRONTIER và thêm n vào REACHED.
            reached.add(n)

            # [MÃ GIẢ]: d. Với mỗi trạng thái m kề với n:
            for m in self.get_neighbors(n, obs):
                # [MÃ GIẢ]: i. Tính toán chi phí thực tế mới: g_new(m) = g(n) + cost(m)
                g_new = g_costs[n] + 1 # cost(m) = 1 cho mỗi bước trượt trong game
                
                # [MÃ GIẢ]: ii. NẾU m đã nằm trong REACHED:
                if m in reached:
                    # NẾU g_new(m) >= g(m) hiện tại: Bỏ qua trạng thái m (tệ hơn).
                    if g_new >= g_costs[m]: 
                        continue 
                    # NGƯỢC LẠI: Xóa m khỏi REACHED và cập nhật lại g(m) = g_new(m).
                    else:
                        reached.remove(m)
                        g_costs[m] = g_new
                        heapq.heappush(frontier, (g_new, next(self.counter), m, p + [m]))
                        frontier_set.add(m)
                
                # [MÃ GIẢ]: iii. NẾU m đã nằm trong FRONTIER:
                elif m in frontier_set:
                    # NẾU g_new(m) < g(m) hiện tại: Cập nhật lại g(m) = g_new(m) và đỉnh cha.
                    if g_new < g_costs[m]:
                        g_costs[m] = g_new
                        heapq.heappush(frontier, (g_new, next(self.counter), m, p + [m]))
                
                # [MÃ GIẢ]: iv. NẾU m chưa có mặt trong FRONTIER và REACHED:
                else:
                    # Gán g(m) = g_new(m). Thêm m vào FRONTIER.
                    g_costs[m] = g_new
                    heapq.heappush(frontier, (g_new, next(self.counter), m, p + [m]))
                    frontier_set.add(m)
                    
        # [MÃ GIẢ]: 4. TRẢ VỀ "Thất bại" (Không tìm thấy đường đi tới đích).
        self.log_msg("-> Bế tắc, không tìm thấy đường!", (255, 50, 50))
        return []

    def run_greedy(self, start, obs):
        self.log_msg("--- GREEDY SEARCH (Tìm kiếm Tham lam) ---", COLORS["Greedy"])
        # [MÃ GIẢ]: 1. Khởi tạo tập Frontier = {Start}. Tính hàm đánh giá h(Start)
        frontier = [(self.heuristic(start), next(self.counter), start, [])]
        frontier_set = {start} 
        
        # [MÃ GIẢ]: 2. Khởi tạo tập reached = {}
        reached = set()

        # [MÃ GIẢ]: 3. TRONG KHI (frontier không rỗng):
        while frontier:
            # [MÃ GIẢ]: a. Chọn trạng thái n từ frontier có h(n) nhỏ nhất.
            h_n, _, n, p = heapq.heappop(frontier)
            if n in frontier_set: frontier_set.remove(n)
            else: continue

            # [MÃ GIẢ]: b. NẾU n == Goal: TRẢ VỀ "Thành công" và truy xuất đường đi
            if n == self.target_pos: return p

            # [MÃ GIẢ]: c. Loại bỏ n khỏi frontier và thêm n vào reached.
            reached.add(n)

            # [MÃ GIẢ]: d. Với mỗi trạng thái m kề với n:
            for m in self.get_neighbors(n, obs):
                # [MÃ GIẢ]: i. NẾU m chưa có trong cả frontier và reached:
                if m not in frontier_set and m not in reached:
                    # [MÃ GIẢ]: Gán đỉnh cha. Tính h(m). Thêm m vào frontier.
                    heapq.heappush(frontier, (self.heuristic(m), next(self.counter), m, p + [m]))
                    frontier_set.add(m)
                # [MÃ GIẢ]: ii. NẾU m đã có trong frontier hoặc reached: Bỏ qua m.
                
        # [MÃ GIẢ]: 4. TRẢ VỀ "Thất bại"
        return []

    def run_astar(self, start, obs):
        self.log_msg("--- A* (f = g + h) ---", COLORS["A*"])
        # [MÃ GIẢ]: 1. Khởi tạo tập FRONTIER = {Start} với f(Start) = g(Start) + h(Start)
        g_costs = {start: 0}
        f_start = 0 + self.heuristic(start)
        frontier = [(f_start, next(self.counter), start, [])]
        frontier_set = {start}
        
        # [MÃ GIẢ]: 2. Khởi tạo tập REACHED = {}
        reached = set()
        steps = 0
        
        # [MÃ GIẢ]: 3. TRONG KHI (FRONTIER không rỗng):
        while frontier:
            # [MÃ GIẢ]: a. Chọn trạng thái n từ FRONTIER có f(n) nhỏ nhất.
            f_n, _, n, p = heapq.heappop(frontier)
            if n in frontier_set: frontier_set.remove(n)
            else: continue

            steps += 1
            if steps <= 15 or steps % 20 == 0:
                self.log_msg(f"[{steps}] A* xét {n} | g={g_costs[n]}, h={self.heuristic(n)} -> f={f_n}", (255, 255, 150))
                
            # [MÃ GIẢ]: b. NẾU n == Goal: TRẢ VỀ "Thành công"
            if n == self.target_pos:
                self.log_msg(f"-> TỐI ƯU! Đã tới đích sau khi duyệt {steps} nút.", (0, 255, 0))
                return p

            # [MÃ GIẢ]: c. Loại bỏ n khỏi FRONTIER và thêm n vào REACHED.
            reached.add(n)

            # [MÃ GIẢ]: d. Với mỗi trạng thái m kề với n:
            for m in self.get_neighbors(n, obs):
                # [MÃ GIẢ]: i. Tính toán chi phí thực tế mới: g_new(m) = g(n) + cost(m)
                g_new = g_costs[n] + 1
                
                # [MÃ GIẢ]: ii. NẾU m đã nằm trong REACHED:
                if m in reached:
                    # NẾU g_new(m) >= g(m) hiện tại: Bỏ qua trạng thái m
                    if g_new >= g_costs.get(m, float('inf')): continue 
                    else:
                        # NGƯỢC LẠI: Xóa m khỏi REACHED và cập nhật lại g(m)
                        reached.remove(m)
                        g_costs[m] = g_new
                        f_m = g_new + self.heuristic(m)
                        heapq.heappush(frontier, (f_m, next(self.counter), m, p + [m]))
                        frontier_set.add(m)
                        
                # [MÃ GIẢ]: iii. NẾU m đã nằm trong FRONTIER:
                elif m in frontier_set:
                    # NẾU g_new(m) < g(m) hiện tại: Cập nhật lại g, f, cha.
                    if g_new < g_costs[m]:
                        g_costs[m] = g_new
                        f_m = g_new + self.heuristic(m)
                        heapq.heappush(frontier, (f_m, next(self.counter), m, p + [m]))
                        
                # [MÃ GIẢ]: iv. NẾU m chưa có mặt trong FRONTIER và REACHED:
                else:
                    g_costs[m] = g_new
                    f_m = g_new + self.heuristic(m)
                    heapq.heappush(frontier, (f_m, next(self.counter), m, p + [m]))
                    frontier_set.add(m)
                    
        # [MÃ GIẢ]: 4. TRẢ VỀ "Thất bại"
        return []
    
    # ================= NHÓM 3: TÌM KIẾM CỤC BỘ (LOCAL SEARCH) =================
    def run_simple_hc(self, start, obs):
        self.log_msg("--- BẮT ĐẦU LEO ĐỒI (Simple HC) ---", COLORS["Simple HC"])
        # [MÃ GIẢ]: 1.Khởi tạo trạng thái hiện tại Current_State = Start.
        current_state = start
        # [MÃ GIẢ]: Tính giá trị đánh giá của Current_State.
        current_value = self.heuristic(current_state)
        path = []
        steps = 0

        # [MÃ GIẢ]: 2.TRONG KHI (đúng):
        while True:
            steps += 1
            if current_state == self.target_pos: return path
            found_better = False
            
            # [MÃ GIẢ]: a. Sinh lần lượt các trạng thái lân cận của Current_State.
            # [MÃ GIẢ]: b. Với mỗi trạng thái lân cận Next_State:
            for next_state in self.get_neighbors(current_state, obs):
                # [MÃ GIẢ]: i. Tính giá trị đánh giá của Next_State.
                next_value = self.heuristic(next_state)
                
                # [MÃ GIẢ]: ii. NẾU Value(Next_State) > Value(Current_State):
                # (Vì h(n) càng nhỏ càng tốt, nên dấu > trên slide tương ứng dấu < trong code)
                if next_value < current_value:
                    self.log_msg(f"-> Tìm thấy lân cận tốt hơn (h={next_value}). Di chuyển!", (150, 255, 150))
                    # [MÃ GIẢ]: Current_State = Next_State.
                    current_state = next_state
                    current_value = next_value
                    path.append(current_state)
                    found_better = True
                    # [MÃ GIẢ]: Chuyển sang lần lặp tiếp theo.
                    break 

            # [MÃ GIẢ]: c. NẾU không tồn tại trạng thái lân cận nào tốt hơn:
            if not found_better:
                # [MÃ GIẢ]: Dừng vì đã đạt cực đại cục bộ.
                self.log_msg(f"-> Bế tắc! Cực đại cục bộ (Xung quanh không ô nào tốt hơn {current_value}).", (255, 100, 100))
                break

        # [MÃ GIẢ]: 3.TRẢ VỀ Current_State.
        return path if current_state == self.target_pos else []

    def run_beam_search(self, start, obs, k=3):
        self.log_msg("--- LOCAL BEAM SEARCH ---", COLORS["Local Beam"])
        # [MÃ GIẢ]: 1. Khởi tạo: Current_State_set = {Sinh ngẫu nhiên k trạng thái từ Start}
        current_state_set = []
        start_neighbors = self.get_neighbors(start, obs)
        if not start_neighbors: return [] 
            
        for _ in range(k):
            first_state = random.choice(start_neighbors)
            current_state_set.append((first_state, [first_state]))
            
        # [MÃ GIẢ]: 2. TRONG KHI (đúng):
        for _ in range(50):
            # [MÃ GIẢ]: Neighbor_States = rỗng
            neighbor_states = []
            
            # [MÃ GIẢ]: 2.1. SINH TRẠNG THÁI LÂN CẬN:
            # [MÃ GIẢ]: VỚI MỖI State trong Current_State_set:
            for state, path_history in current_state_set:
                # [MÃ GIẢ]: Sinh tất cả các trạng thái lân cận của State.
                # [MÃ GIẢ]: Thêm các trạng thái lân cận này vào Neighbor_States.
                for neighbor in self.get_neighbors(state, obs):
                    neighbor_states.append((neighbor, path_history + [neighbor]))
                    
            # [MÃ GIẢ]: 2.2. KIỂM TRA BẾ TẮC / KHÔNG CẢI THIỆN
            # [MÃ GIẢ]: NẾU Neighbor_States = rỗng:
            if not neighbor_states:
                # [MÃ GIẢ]: Sắp xếp Current_State_set theo h tốt dần
                current_state_set.sort(key=lambda item: self.heuristic(item[0]))
                # [MÃ GIẢ]: TRẢ VỀ trạng thái tốt nhất trong Current_State_set
                return current_state_set[0][1] 
                
            # [MÃ GIẢ]: 2.3. KIỂM TRA ĐÍCH:
            # [MÃ GIẢ]: VỚI MỖI Neighbor trong Neighbor_States:
            for neighbor, path_history in neighbor_states:
                # [MÃ GIẢ]: NẾU Neighbor == Goal: TRẢ VỀ Neighbor
                if neighbor == self.target_pos: return path_history
                    
            # [MÃ GIẢ]: 2.4. LỰA CHỌN CHÙM (NẾU CHƯA TÌM THẤY ĐÍCH):
            # [MÃ GIẢ]: Sắp xếp Neighbor_States theo thứ tự giá trị hàm mục tiêu h tốt dần.
            neighbor_states.sort(key=lambda item: self.heuristic(item[0]))
            
            # [MÃ GIẢ]: Current_State_set = Lấy k trạng thái tốt nhất từ Neighbor_States
            current_state_set = neighbor_states[:k]
            
        current_state_set.sort(key=lambda item: self.heuristic(item[0]))
        return current_state_set[0][1]

    def run_simulated_annealing(self, start, obs):
        self.log_msg("--- SIMULATED ANNEALING (Luyện kim) ---", COLORS["Simulated Annealing"])
        # [MÃ GIẢ]: current state = start
        current_state = start
        path = []
        
        # [MÃ GIẢ]: T = T0
        T = 1000.0
        T_min = 0.01
        alpha = 0.95
        
        # [MÃ GIẢ]: while T > Tmin:
        while T > T_min:
            # [MÃ GIẢ]: if current state == goal: return current state
            if current_state == self.target_pos: return path
                
            neighbors = self.get_neighbors(current_state, obs)
            if not neighbors: break 
                
            # [MÃ GIẢ]: next state = RandomNeighbor(current state)
            next_state = random.choice(neighbors)
            
            # [MÃ GIẢ]: Δ = h(next state) - h(current state)
            delta = self.heuristic(next_state) - self.heuristic(current_state)
            
            # [MÃ GIẢ]: if Δ < 0:
            if delta < 0:
                # [MÃ GIẢ]: current state = next state
                current_state = next_state
                path.append(current_state)
            # [MÃ GIẢ]: else:
            else:
                # [MÃ GIẢ]: p = exp(-Δ / T)
                p = math.exp(-delta / T)
                
                # [MÃ GIẢ]: if Random(0,1) < p:
                if random.random() < p:
                    # [MÃ GIẢ]: current state = next state
                    current_state = next_state
                    path.append(current_state)
                    
            # [MÃ GIẢ]: T = α * T
            T = alpha * T

        # [MÃ GIẢ]: return current state
        return path if current_state == self.target_pos else []

    # ================= MÔI TRƯỜNG PHỨC TẠP & CSP =================
    def run_sensorless(self, start, obs):
        self.log_msg("--- LẬP KẾ HOẠCH ĐỒNG BỘ (CONFORMANT PLANNING) ---", (255, 100, 255))
        
        start_1 = tuple(start)
        start_2 = tuple(self.sensorless_ghost.start_pos)

        report_lines = []
        report_lines.append("=== BÁO CÁO TÌM KIẾM KHÔNG CẢM BIẾN (CONFORMANT PLANNING) ===")
        report_lines.append(f"Mục tiêu: Tìm 1 chuỗi hành động chung đưa hệ thống về Đích {self.target_pos}.")
        report_lines.append("Cơ chế: Nếu một Trạng thái (State) chạm đích trước, nó sẽ chuyển sang trạng thái dừng (Sink State).")
        
        # [MÃ GIẢ]: b_start = {s | s in INITIAL_STATE_SET}
        belief_start = tuple(sorted([start_1, start_2]))

        # [MÃ GIẢ]: frontier <- a FIFO queue containing b_start
        # Hàng đợi: (Tập Belief, Pos 1, Path 1, Pos 2, Path 2, Lịch sử Hành động)
        frontier = deque([(belief_start, start_1, [], start_2, [], [])])
        
        # [MÃ GIẢ]: explored <- {b_start}
        reached = {belief_start}
        
        steps_explored = 0

        # Hàm di chuyển tuỳ chỉnh: Đã vào đích thì khóa chết (Sink State)
        def get_next_state(pos, action):
            if pos == self.target_pos: return pos
            return self.get_slide_dest(pos, action, obs)

        # [MÃ GIẢ]: loop do
        while frontier:
            # [MÃ GIẢ]: if EMPTY?(frontier) then return failure
            # (Được xử lý ẩn bởi vòng lặp while của Python)
            
            # [MÃ GIẢ]: b <- POP(frontier)
            current_belief, current_1, path_1, current_2, path_2, action_history = frontier.popleft()
            steps_explored += 1
            
            if len(path_1) > 20: continue # Cắt tỉa chống treo máy
                
            # [MÃ GIẢ]: if b is a subset of GOAL then return SOLUTION(b)
            # (Tất cả trạng thái trong Belief đều đã hội tụ tại Đích)
            if current_1 == self.target_pos and current_2 == self.target_pos:
                self.log_msg(f"-> Hội tụ thành công! Cả 2 State đều đã vào Đích sau {len(path_1)} bước.", (0, 255, 255))
                
                report_lines.append("\n=======================================================")
                report_lines.append(f"=> TỔNG KẾT: TÌM THẤY KẾ HOẠCH HỘI TỤ (CONFORMANT PLAN)!")
                report_lines.append(f"Tổng số trạng thái đã duyệt: {steps_explored}")
                report_lines.append(f"Chuỗi hành động chung ({len(action_history)} bước): {' -> '.join(action_history)}")
                
                try:
                    filename = self.get_map_path("BaoCao_ConformantPlanning.txt")
                    with open(filename, "w", encoding="utf-8") as f: f.write("\n".join(report_lines))
                    self.log_msg(f"-> Đã xuất Báo cáo học thuật: {os.path.basename(filename)}", (100, 255, 100))
                except Exception as e: pass

                self.sensorless_ghost.computed_path = path_2 
                return path_1
                
            # [MÃ GIẢ]: for each action in ACTIONS(b) do
            for action in [(0,-1), (0,1), (-1,0), (1,0)]:
                action_name = {(0,-1): "LÊN", (0,1): "XUỐNG", (-1,0): "TRÁI", (1,0): "PHẢI"}[action]
                
                # [MÃ GIẢ]: b_prime <- PREDICT(b, action)
                next_1 = get_next_state(current_1, action)
                next_2 = get_next_state(current_2, action)
                next_belief = tuple(sorted(list({next_1, next_2})))
                
                # [MÃ GIẢ]: if b_prime not in explored then
                if next_belief not in reached:
                    # [MÃ GIẢ]: explored.ADD(b_prime)
                    reached.add(next_belief)
                    
                    # Log báo cáo...
                    if current_1 != self.target_pos and next_1 == self.target_pos:
                        report_lines.append(f" [*] State 1 đã chạm đích {self.target_pos} và chuyển sang dừng (Sink State).")
                    elif current_2 != self.target_pos and next_2 == self.target_pos:
                        report_lines.append(f" [*] State 2 đã chạm đích {self.target_pos} và chuyển sang dừng (Sink State).")
                    elif len(next_belief) < len(current_belief):
                        report_lines.append(f"\n[!] BƯỚC HỘI TỤ (State Convergence): Trượt {action_name} -> {next_belief[0]}")

                    # [MÃ GIẢ]: frontier.INSERT(b_prime)
                    frontier.append((next_belief, next_1, path_1 + [next_1], next_2, path_2 + [next_2], action_history + [action_name]))
                    
        self.log_msg("-> Bế tắc! Không tồn tại Kế hoạch hội tụ.", (255, 100, 100))
        return []

    def run_partial_observable(self, start, obs):
        self.log_msg("--- MÔI TRƯỜNG NHÌN THẤY MỘT PHẦN (PARTIAL OBSERVE) ---", (255, 200, 255))
        report_lines = []
        report_lines.append("=== BÁO CÁO QUÁ TRÌNH LỌC NIỀM TIN (BELIEF STATE UPDATE) ===")

        # [MÃ GIẢ]: b <- b_start (Tập hợp các trạng thái có thể đang đứng)
        fake_1 = self.get_random_valid_pos(obs, start)
        fake_2 = self.get_random_valid_pos(obs, start)
        fake_3 = self.get_random_valid_pos(obs, start)
        fake_4 = self.get_random_valid_pos(obs, start)
        belief_state = {start, fake_1, fake_2, fake_3, fake_4}
        
        self.log_msg(f"[Belief Start] Robot phân thân ở: {len(belief_state)} vị trí.", (200, 200, 255))
        report_lines.append(f"1. Niềm tin ban đầu (Belief Start): Gồm {len(belief_state)} vị trí có thể: {list(belief_state)}")

        # [MÃ GIẢ]: Hàm PERCEPT(s) trả về quan sát tại trạng thái s
        def get_percept(pos):
            # Cảm biến trả về: (Có đi LÊN được không, XUỐNG, TRÁI, PHẢI được không)
            return tuple(self.get_slide_dest(pos, d, obs) != pos for d in [(0,-1), (0,1), (-1,0), (1,0)])

        real_pos = start
        path = []
        self.belief_history = [belief_state.copy()]

        # [MÃ GIẢ]: loop do:
        for step in range(30):
            # [MÃ GIẢ]: if IS-LOCALIZED(b) then return A*(b_pos)
            if len(belief_state) == 1:
                localized_pos = list(belief_state)[0]
                self.log_msg(f"-> [Định vị Thành Công!] Vị trí thật sự là: {localized_pos}", (0, 255, 0))
                report_lines.append(f"\n=> KẾT LUẬN: Đã định vị thành công vị trí {localized_pos} sau {step} bước.")
                
                try:
                    filename = self.get_map_path("BaoCao_PartialObservable.txt")
                    with open(filename, "w", encoding="utf-8") as f: f.write("\n".join(report_lines))
                except Exception: pass

                astar_path = self.run_astar(localized_pos, obs)
                for _ in astar_path: self.belief_history.append(belief_state.copy())
                return path + astar_path

            valid_dirs = [d for d in [(0,-1), (0,1), (-1,0), (1,0)] if self.get_slide_dest(real_pos, d, obs) != real_pos]
            if not valid_dirs: return path

            # [MÃ GIẢ]: action <- CHOOSE-ACTION(b)
            action = random.choice(valid_dirs)
            action_name = {(0,-1): "LÊN", (0,1): "XUỐNG", (-1,0): "TRÁI", (1,0): "PHẢI"}[action]
            
            # [MÃ GIẢ]: thực thi action trên môi trường thực
            real_pos = self.get_slide_dest(real_pos, action, obs)
            path.append(real_pos)
            
            # [MÃ GIẢ]: o <- PERCEPT(environment)
            percept = get_percept(real_pos)
            self.log_msg(f"Bước {step+1}: Trượt {action_name}. Đọc cảm biến: {percept}", (220, 220, 220))
            
            report_lines.append(f"\n--- BƯỚC {step+1} ---")
            report_lines.append(f"Hành động: Trượt {action_name} | Cảm biến đo được: {percept}")

            # [MÃ GIẢ]: b_prime <- UPDATE-BELIEF(b, action, o)
            # Hàm UPDATE: Giữ lại s' nếu s' được tạo từ action và Percept(s') khớp với cảm biến thực
            new_belief_state = set()
            for s in belief_state:
                s_next = self.get_slide_dest(s, action, obs)
                s_percept = get_percept(s_next)
                
                if s_percept == percept:
                    new_belief_state.add(s_next)
                    report_lines.append(f"  [+] Nếu ở {s} -> trượt đến {s_next}. Cảm biến dự kiến {s_percept} KHỚP THỰC TẾ -> Giữ lại.")
                else:
                    report_lines.append(f"  [-] Nếu ở {s} -> trượt đến {s_next}. Cảm biến dự kiến {s_percept} SAI LỆCH -> Loại bỏ.")

            # [MÃ GIẢ]: b <- b_prime
            belief_state = new_belief_state
            self.belief_history.append(belief_state.copy())
            self.log_msg(f"   [Lọc Niềm tin] Còn: {len(belief_state)} vị trí.", (255, 255, 100))

        report_lines.append("\n=> THẤT BẠI: Quá 30 bước không thể định vị.")
        return path
    
    def run_and_or_graph(self, start, obs):
        self.log_msg("--- LẬP KẾ HOẠCH DỰ PHÒNG (AND-OR GRAPH) ---", (255, 255, 100))
        report_lines = []
        MAX_DEPTH = 10 

        # [MÃ GIẢ]: function OR_SEARCH(state, problem, path):
        def or_search(state, path, depth):
            # [MÃ GIẢ]: if state in problem.goal_test: return [] // kế hoạch rỗng
            if state == self.target_pos: return [] 
            # [MÃ GIẢ]: if state in path: return failure // tránh lặp
            if state in path: return "failure"
                
            if depth >= MAX_DEPTH: return "failure"
                
            # [MÃ GIẢ]: for each action in problem.actions(state):
            for action in [(0,-1), (0,1), (-1,0), (1,0)]:
                action_name = {(0,-1): "LÊN", (0,1): "XUỐNG", (-1,0): "TRÁI", (1,0): "PHẢI"}[action]
                normal_dest = self.get_slide_dest(state, action, obs)
                if normal_dest == state: continue 
                
                dx, dy = action
                slip_dest = (normal_dest[0] - dx, normal_dest[1] - dy)
                
                # [MÃ GIẢ]: result_states = problem.results(state, action)
                states_result = [normal_dest, slip_dest] if slip_dest != state else [normal_dest]
                
                # [MÃ GIẢ]: plan = AND_SEARCH(result_states, problem, path + [state])
                plan = and_search(states_result, path + [state], depth + 1, action_name)
                
                # [MÃ GIẢ]: if plan != failure: return [action, plan]
                if plan != "failure": return [normal_dest] + plan 
            # [MÃ GIẢ]: return failure
            return "failure"

        # [MÃ GIẢ]: function AND_SEARCH(states, problem, path):
        def and_search(states, path, depth, action_name):
            # [MÃ GIẢ]: plans = empty mapping
            plan_a_path = None 
            
            # [MÃ GIẢ]: for each s in states:
            for i, s in enumerate(states):
                # [MÃ GIẢ]: plan_s = OR_SEARCH(s, problem, path)
                plan_s = or_search(s, path, depth + 1)
                
                # [MÃ GIẢ]: if plan_s == failure: return failure
                if plan_s == "failure": return "failure"
                if i == 0: plan_a_path = plan_s 
            # [MÃ GIẢ]: return plans
            return plan_a_path

        # [MÃ GIẢ]: return OR_SEARCH(problem.initial_state, problem, [])
        res = or_search(start, [], 0)
        
        if res != "failure": self.log_msg("-> Lập kế hoạch dự phòng thành công! Đã quét hết rủi ro.", (0, 255, 0))
        else: self.log_msg("-> Thất bại: Không có Kế hoạch an toàn tuyệt đối.", (255, 50, 50))
        return res if res != "failure" else []
    
    def setup_csp_map(self):
        self.grid_size = 5  # Bàn cờ 5x5
        self.board_size = min(HEIGHT - 100, WIDTH - 680)
        self.cell_size = self.board_size // self.grid_size
        self.walls.clear()

        # Xây tường bao biên 5x5
        for i in range(self.grid_size):
            self.walls.add(((-1, i), (0, i)))
            self.walls.add(((self.grid_size - 1, i), (self.grid_size, i)))
            self.walls.add(((i, -1), (i, 0)))
            self.walls.add(((i, self.grid_size - 1), (i, self.grid_size)))

        # --- SETUP ĐÚNG TỌA ĐỘ NHƯ KHOA MUỐN ---
        self.target_pos = (2, 3) 
        self.target_pos_2 = None
        for r in self.robots: r.start_pos = [2, 0] # Ta ở trên cùng
            
        # 3 Trợ thủ đứng dàn hàng ngang ở hàng số 1 (Y=1), cột 1, 2, 3
        if hasattr(self, 'aux_robots'):
            self.aux_robots[0].start_pos = [1, 1] 
            self.aux_robots[1].start_pos = [2, 1] 
            self.aux_robots[2].start_pos = [3, 1] 
            
        self.reset_simulation()

    def get_valid_y_domain(self, col_x, start):
        # Trả về các hàng (Y) hợp lệ cho một cột (X)
        domain = []
        for y in range(self.grid_size):
            pos = (col_x, y)
            # Nghiêm cấm Robot Trợ thủ đứng đè lên Start hoặc Target
            if pos != self.target_pos and pos != tuple(start):
                domain.append(y)
        return domain

    def calculate_csp_conflicts(self, assignment, start=None):
        conflicts = 0
        if len(assignment) >= 3:
            y1, y2, y3 = assignment[0], assignment[1], assignment[2]
            # Ràng buộc 1: 1 và 3 cùng hàng
            if y1 != y3: conflicts += 1
            # Ràng buộc 2: 2 cách 1 đúng 4 ô
            if abs(y2 - y1) != 4: conflicts += 1
        return conflicts

    # ================= NHÓM 5: THỎA MÃN RÀNG BUỘC (CSP) =================
    def run_backtracking(self, start, obs):
        self.log_msg("--- BACKTRACKING ---", (180, 100, 255))
        domains = [self.get_valid_y_domain(1, start), self.get_valid_y_domain(2, start), self.get_valid_y_domain(3, start)]
        
        # [MÃ GIẢ]: function BACKTRACK(assignment, csp) returns a solution or failure
        def backtrack(assignment):
            # Cập nhật Giao diện
            if len(assignment) > 0:
                for i, y_val in enumerate(assignment): self.aux_robots[i].visual_pos = [(i+1) * self.cell_size, y_val * self.cell_size]
                if getattr(self, 'step_mode', False):
                    self.sim_status = f"Chờ bước tiếp..."
                    self.csp_waiting = True
                    while getattr(self, 'csp_waiting', False) and self.state == "SIMULATION": pygame.time.delay(20)
                else:
                    self.draw_simulation(); pygame.display.flip(); pygame.time.delay(50)
            
            # [MÃ GIẢ]: if assignment is complete then return assignment
            if len(assignment) == 3:
                if self.calculate_csp_conflicts(assignment, start) == 0: return assignment
                return "failure"
                
            # [MÃ GIẢ]: var <- SELECT-UNASSIGNED-VARIABLE(assignment, csp)
            col_idx = len(assignment)
            
            # [MÃ GIẢ]: for each value in ORDER-DOMAIN-VALUES(var, assignment, csp) do
            for value in domains[col_idx]:
                # [MÃ GIẢ]: add {var = value} to assignment
                # [MÃ GIẢ]: result <- BACKTRACK(assignment, csp)
                res = backtrack(assignment + [value])
                # [MÃ GIẢ]: if result != failure then return result
                if res != "failure": return res
                # [MÃ GIẢ]: remove {var = value} from assignment (Bỏ qua qua logic Python ẩn)
                
            # [MÃ GIẢ]: return failure
            return "failure"
            
        res = backtrack([])
        if res != "failure":
            self.log_msg(f"-> TÌM THẤY NGHIỆM: Y = {res}", (0, 255, 0))
            for i, aux in enumerate(self.aux_robots): aux.logic_pos = [i+1, res[i]]; aux.start_pos = [i+1, res[i]]
            return [self.target_pos]
        return []

    def run_ac3(self, start, obs):
        self.log_msg("--- AC-3 (Arc Consistency) ---", (147, 112, 219))
        domains = { 0: self.get_valid_y_domain(1, start), 1: self.get_valid_y_domain(2, start), 2: self.get_valid_y_domain(3, start) }
        
        # Vẽ Bóng ma trước khi cắt
        self.csp_domains = [[(i+1, y) for y in domains[i]] for i in range(3)]
        self.draw_simulation(); pygame.display.flip(); pygame.time.delay(1000)

        # Ràng buộc: i=0 và j=1 thì khoảng cách bằng 4. i=0 và j=2 thì phải giống nhau (cùng hàng).
        def satisfy(i, x, j, y):
            if (i==0 and j==1) or (i==1 and j==0): return abs(x - y) == 4
            if (i==0 and j==2) or (i==2 and j==0): return x == y
            return True # 1 và 2 không ràng buộc trực tiếp

        # [MÃ GIẢ]: function RM-INCONSISTENT-VALUES(Xi, Xj) returns true iff remove a value
        def rm_inconsistent_values(xi, xj):
            removed = False
            # [MÃ GIẢ]: for each x in DOMAIN[Xi] do
            for x in list(domains[xi]): 
                # [MÃ GIẢ]: if no value y in DOMAIN[Xj] allows (x,y) to satisfy constraint(Xi, Xj)
                if not any(satisfy(xi, x, xj, y) for y in domains[xj]):
                    # [MÃ GIẢ]: then delete x from DOMAIN[Xi]; removed <- true
                    domains[xi].remove(x)
                    removed = True
                    self.csp_domains[xi].remove((xi+1, x)) # Xoá bóng ma trên hình
                    self.draw_simulation(); pygame.display.flip(); pygame.time.delay(150)
            # [MÃ GIẢ]: return removed
            return removed

        # [MÃ GIẢ]: function AC-3(csp)
        # [MÃ GIẢ]: queue, a queue of arcs, initially all the arcs in csp
        queue = deque([(0,1), (1,0), (0,2), (2,0)]) 
        
        # [MÃ GIẢ]: while queue is not empty do
        while queue:
            # [MÃ GIẢ]: (Xi, Xj) <- REMOVE-FIRST(queue)
            xi, xj = queue.popleft()
            # [MÃ GIẢ]: if RM-INCONSISTENT-VALUES(Xi, Xj) then
            if rm_inconsistent_values(xi, xj):
                # [MÃ GIẢ]: for each Xk in NEIGHBORS[Xi] do add (Xk, Xi) to queue
                neighbors = [k for k in range(3) if k != xi and k != xj and ((xi==0) or (k==0))] 
                for xk in neighbors: queue.append((xk, xi))
                    
        self.log_msg(f"-> Đã tỉa miền giá trị thành: {domains}", (0, 255, 255))
        self.csp_domains = None 
            
        def backtrack(assignment):
            col_idx = len(assignment)
            if col_idx == 3:
                return assignment if self.calculate_csp_conflicts(assignment, start) == 0 else "failure"
            for value in domains[col_idx]:
                res = backtrack(assignment + [value])
                if res != "failure": return res
            return "failure"
            
        res = backtrack([])
        if res != "failure":
            for i, aux in enumerate(self.aux_robots): aux.visual_pos = [(i+1)*self.cell_size, res[i]*self.cell_size]; aux.logic_pos = [i+1, res[i]]; aux.start_pos = [i+1, res[i]]
            return [self.target_pos]
        return []

    def run_min_conflicts(self, start, obs):
        self.log_msg("--- MIN-CONFLICTS ---", (255, 140, 0))
        domains = [self.get_valid_y_domain(1, start), self.get_valid_y_domain(2, start), self.get_valid_y_domain(3, start)]
        if not all(domains): return []
            
        # [MÃ GIẢ]: current <- an initial complete assignment for csp
        current = [random.choice(domains[i]) for i in range(3)]
        
        # [MÃ GIẢ]: for i = 1 to max_steps do
        for step in range(50):
            conflicts = self.calculate_csp_conflicts(current, start)
            
            # Cập nhật giao diện
            for i, y_val in enumerate(current): self.aux_robots[i].visual_pos = [(i+1) * self.cell_size, y_val * self.cell_size]
            if getattr(self, 'step_mode', False):
                self.sim_status = "Chờ bước tiếp..."
                self.csp_waiting = True
                while getattr(self, 'csp_waiting', False) and self.state == "SIMULATION": pygame.time.delay(20)
            else: self.draw_simulation(); pygame.display.flip(); pygame.time.delay(50)
                    
            # [MÃ GIẢ]: if current is a solution for csp then return current
            if conflicts == 0:
                self.log_msg(f"-> THÀNH CÔNG! Tọa độ Y: {current}", (0, 255, 0))
                for i, aux in enumerate(self.aux_robots): aux.logic_pos = [i+1, current[i]]; aux.start_pos = [i+1, current[i]]
                return [self.target_pos]
                
            # [MÃ GIẢ]: var <- a randomly chosen conflicted variable from csp.VARIABLES
            var = random.randint(0, 2)
            
            # [MÃ GIẢ]: value <- the value v for var that minimizes CONFLICTS(var, v, current, csp)
            min_c = float('inf'); best_vals = []
            for v in domains[var]:
                temp = list(current); temp[var] = v
                c = self.calculate_csp_conflicts(temp, start)
                if c < min_c: min_c = c; best_vals = [v]
                elif c == min_c: best_vals.append(v)
                    
            # [MÃ GIẢ]: set var = value in current
            current[var] = random.choice(best_vals)
            
        # [MÃ GIẢ]: return failure
        return []

    # ================= NHÓM 6: ĐỐI KHÁNG (ADVERSARIAL SEARCH) =================
    # TERMINAL-TEST(state): xác định xem trạng thái hiện tại (state) đã là trạng thái kết thúc game chưa?
    def is_caught(self, p_pos, e_pos):
        # An toàn nếu đã vào đích
        if tuple(p_pos) == self.target_pos: 
            return False
        # Bị bắt nếu trùng chính xác 100% toạ độ (Khoảng cách = 0)
        return tuple(p_pos) == tuple(e_pos)
    # Khi cây đệ quy Minimax duyệt xuống một trạng thái mà hàm này trả về True (Bị tóm), 
    # hệ thống sẽ lập tức dừng duyệt nhánh đó và gọi hàm UTILITY trả về điểm số âm vô cực (-9999), 
    # báo hiệu đây là một nhánh chết (thua cuộc) để AI của Ta (MAX) biết đường mà né lệnh di chuyển.

    # [MÃ GIẢ]: function UTILITY(state) returns a numeric value
    # Đánh giá điểm số của trạng thái hiện tại (Càng cao thì MAX/Ta càng có lợi)
    def heuristic_adv(self, p_pos, e_pos):
        # [MÃ GIẢ]: if TERMINAL-TEST(state) then return UTILITY(state)
        if self.is_caught(p_pos, e_pos): return -9999 # Bị tóm: Điểm âm vô cực (Thua)
        if p_pos == self.target_pos: return 9999      # Tới đích: Điểm dương vô cực (Thắng)
        
        dist_to_goal = abs(p_pos[0] - self.target_pos[0]) + abs(p_pos[1] - self.target_pos[1])
        dist_to_enemy = abs(p_pos[0] - e_pos[0]) + abs(p_pos[1] - e_pos[1])
        
        # Hàm Utility (Tiện ích): Vừa ưu tiên rút ngắn khoảng cách tới đích, vừa ráng cách xa địch
        return -dist_to_goal * 10 + dist_to_enemy

    # Hàm đệ quy này gộp chung cả 3 thuật toán: Minimax, Alpha-Beta và Expectimax
    def get_best_adv_move(self, p_pos, e_pos, depth, is_max, alpha, beta, algo):
        # [MÃ GIẢ]: if TERMINAL-TEST(state) or depth == 0 then return UTILITY(state)
        if depth == 0 or p_pos == self.target_pos or self.is_caught(p_pos, e_pos):
            return self.heuristic_adv(p_pos, e_pos), None

        if is_max: 
            # ----------------------------------------------------
            # [MÃ GIẢ]: function MAX-VALUE(state, alpha, beta)
            # Lượt của MAX (Ta): Tìm nước đi tối đa hóa điểm số
            # ----------------------------------------------------
            
            # [MÃ GIẢ]: v <- -∞
            best_val = float('-inf'); best_move = None
            
            # (Ta coi Địch là Bức tường cứng để sinh trạng thái lân cận)
            valid_moves = self.get_neighbors(p_pos, obstacles={e_pos})
            if not valid_moves: return self.heuristic_adv(p_pos, e_pos), None
            
            # [MÃ GIẢ]: for each a in ACTIONS(state) do
            for nxt_p in valid_moves:
                # [MÃ GIẢ]: v <- MAX(v, MIN-VALUE(RESULT(state, a), alpha, beta))
                val, _ = self.get_best_adv_move(nxt_p, e_pos, depth-1, False, alpha, beta, algo)
                if val > best_val: best_val = val; best_move = nxt_p
                
                # CẮT TỈA ALPHA-BETA (Nếu thuật toán là Alpha-Beta)
                if algo == "alphabeta": 
                    # [MÃ GIẢ]: if v >= beta then return v
                    if best_val >= beta: break # Cắt tỉa (Pruning) nhánh phía sau
                    # [MÃ GIẢ]: alpha <- MAX(alpha, v)
                    alpha = max(alpha, best_val)
                    
            # [MÃ GIẢ]: return v
            return best_val, best_move
            
        else: 
            # ----------------------------------------------------
            # Lượt của MIN / CHANCE (Robot Địch)
            # ----------------------------------------------------
            valid_moves = self.get_neighbors(e_pos, obstacles=set(), stop_on=p_pos)
            if not valid_moves: return self.heuristic_adv(p_pos, e_pos), None
            
            # 1. TRƯỜNG HỢP EXPECTIMAX (Môi trường ngẫu nhiên - Chance Node)
            if algo == "expectimax": 
                # [MÃ GIẢ]: function EXP-VALUE(state)
                # [MÃ GIẢ]: v <- 0; for each a in ACTIONS(state) do v += P(a) * MAX-VALUE(RESULT(state, a))
                # (Với P(a) là xác suất đồng đều chia cho tổng số nước đi hợp lệ)
                avg_val = sum(self.get_best_adv_move(p_pos, nxt_e, depth-1, True, alpha, beta, algo)[0] for nxt_e in valid_moves) / len(valid_moves)
                return avg_val, random.choice(valid_moves)
            
            # 2. TRƯỜNG HỢP MINIMAX / ALPHA-BETA (Đối thủ hoàn hảo - Min Node)
            else:
                # [MÃ GIẢ]: function MIN-VALUE(state, alpha, beta)
                # [MÃ GIẢ]: v <- +∞
                best_val = float('inf'); best_move = None
                
                # [MÃ GIẢ]: for each a in ACTIONS(state) do
                for nxt_e in valid_moves:
                    # [MÃ GIẢ]: v <- MIN(v, MAX-VALUE(RESULT(state, a), alpha, beta))
                    val, _ = self.get_best_adv_move(p_pos, nxt_e, depth-1, True, alpha, beta, algo)
                    if val < best_val: best_val = val; best_move = nxt_e
                    
                    # CẮT TỈA ALPHA-BETA (Nếu thuật toán là Alpha-Beta)
                    if algo == "alphabeta": 
                        # [MÃ GIẢ]: if v <= alpha then return v
                        if best_val <= alpha: break # Cắt tỉa (Pruning) nhánh phía sau
                        # [MÃ GIẢ]: beta <- MIN(beta, v)
                        beta = min(beta, best_val)
                        
                # [MÃ GIẢ]: return v
                return best_val, best_move
            
    def run_adversarial(self, start, obs, algo):
        self.log_msg(f"--- {algo.upper()} (ĐỐI KHÁNG) ---", (255, 100, 100))
        p_curr = start; e_curr = tuple(self.enemy.start_pos)
        p_path = []; e_path = []
        
        # Tầm nhìn (Depth) - Expectimax duyệt rộng hơn nên giảm depth để tránh treo máy
        search_depth = 7 if algo != "expectimax" else 5
        
        for step in range(1, 15): 
            self.log_msg(f"\n--- LƯỢT {step} ---", (255, 255, 0))
            
            # 1. LƯỢT CỦA TA (MAX)
            self.log_msg(f"1. Lượt của TA (Đang tính toán trước {search_depth} bước)...", (100, 255, 100))
            _, nxt_p = self.get_best_adv_move(p_curr, e_curr, depth=search_depth, is_max=True, alpha=float('-inf'), beta=float('inf'), algo=algo)
            if nxt_p is None: nxt_p = p_curr 
            self.log_msg(f"-> TA quyết định di chuyển tới: {nxt_p}", (100, 255, 100))
            p_curr = nxt_p
            p_path.append(p_curr)
            
            if p_curr == self.target_pos or self.is_caught(p_curr, e_curr): break
                
            # 2. LƯỢT CỦA ĐỊCH (MIN / CHANCE)
            self.log_msg(f"2. Lượt của ĐỊCH (Đang tìm cách chặn đường)...", (255, 100, 100))
            _, nxt_e = self.get_best_adv_move(p_curr, e_curr, depth=search_depth-1, is_max=False, alpha=float('-inf'), beta=float('inf'), algo=algo)
            if nxt_e is None: nxt_e = e_curr
            self.log_msg(f"-> ĐỊCH quyết định chặn tại: {nxt_e}", (255, 100, 100))
            e_curr = nxt_e
            e_path.append(e_curr)
            
            if self.is_caught(p_curr, e_curr): break

        self.enemy.computed_path = e_path 
        return p_path

    # thay vì phải viết 3 hàm Minimax, Alpha-Beta và Expectimax, thì sử dụng hàm bọc (Wrapper): đóngv ai trò cầu nối
    # Sử dụng Wrapper để chuẩn hóa số lượng tham số đầu vào (start, obs)
    # giúp tái sử dụng 1 hàm run_adversarial duy nhất cho cả 3 thuật toán.
    def run_minimax_wrapper(self, start, obs): return self.run_adversarial(start, obs, "minimax")
    def run_alphabeta(self, start, obs): return self.run_adversarial(start, obs, "alphabeta")
    def run_expectimax(self, start, obs): return self.run_adversarial(start, obs, "expectimax")

    def compute_path_for_ai(self, r):
        sp = tuple(r.logic_pos); obs = set()
        algo_map = {
            "BFS": self.run_bfs, "DFS": self.run_dfs, "IDS": self.run_ids,
            "UCS": self.run_ucs, "Greedy": self.run_greedy, "A*": self.run_astar,
            "Simple HC": self.run_simple_hc, "Local Beam": self.run_beam_search, "Simulated Annealing": self.run_simulated_annealing,
            "Sensorless": self.run_sensorless, "Partial-Observable": self.run_partial_observable, "AND-OR Graph": self.run_and_or_graph,
            "Backtracking": self.run_backtracking, "AC-3": self.run_ac3, "Min-Conflicts": self.run_min_conflicts,
            "Minimax": self.run_minimax_wrapper, "Alpha-Beta": self.run_alphabeta, "Expectimax": self.run_expectimax
        }
        
        # --- MỚI SỬA: Lấy tên thuật toán đang chọn thay vì tên Robot ---
        algo_name = self.current_ai if self.current_ai else r.name
        return algo_map.get(algo_name, self.run_bfs)(sp, obs)

  # ================= GIAO DIỆN & TƯƠNG TÁC (PACMAN LAB THEME) =================
    def draw_text(self, text, font, color, pos):
        self.screen.blit(font.render(text, True, color), pos)

    def draw_wall(self, p1, p2):
        if p1[0] < 0 or p2[0] >= self.grid_size or p1[1] < 0 or p2[1] >= self.grid_size: return
        rect = pygame.Rect(OFFSET_X + p2[0]*self.cell_size - 3, OFFSET_Y + p1[1]*self.cell_size - 4, 8, self.cell_size + 8) if p1[0] != p2[0] else \
               pygame.Rect(OFFSET_X + p1[0]*self.cell_size - 4, OFFSET_Y + p2[1]*self.cell_size - 3, self.cell_size + 8, 8)
        
        # Đổ bóng tường
        pygame.draw.rect(self.shadow_surface, SHADOW_COLOR, rect.move(2, 3))
        
        # Vẽ tường Neon
        wall_color = (255, 50, 50) if self.edit_mode == 1 else WALL_COLOR
        pygame.draw.rect(self.screen, wall_color, rect, border_radius=4)
        
        # Tạo hiệu ứng phát sáng (Glow) cho tường
        glow_rect = rect.inflate(4, 4)
        pygame.draw.rect(self.shadow_surface, (*wall_color, 40), glow_rect, border_radius=4)

    def toggle_wall(self, mouse_pos, offset_x=None, offset_y=None, c_size=None):
        if offset_x is None: offset_x = OFFSET_X
        if offset_y is None: offset_y = OFFSET_Y
        if c_size is None: c_size = self.cell_size
        
        mx, my = mouse_pos
        c, r = (mx - offset_x) / c_size, (my - offset_y) / c_size
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

    def draw_menu(self):
        self.screen.fill(BG_COLOR)
        
        title_text = "RICOCHET ALGORITHM LABORATORY"
        title_surf = self.font_title.render(title_text, True, TARGET_COLOR)
        self.screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 80))
        
        subtitle = "Chọn một thuật toán để bắt đầu mô phỏng"
        sub_surf = self.font_lg.render(subtitle, True, (150, 170, 200))
        self.screen.blit(sub_surf, (WIDTH//2 - sub_surf.get_width()//2, 140))

        groups = [
            ("1. TÌM KIẾM MÙ", ["BFS", "DFS", "IDS"]),
            ("2. CÓ THÔNG TIN", ["UCS", "Greedy", "A*"]),
            ("3. CỤC BỘ", ["Simple HC", "Local Beam", "Simulated Annealing"]),
            ("4. PHỨC TẠP", ["Sensorless", "Partial-Observable", "AND-OR Graph"]),
            ("5. RÀNG BUỘC CSP", ["Backtracking", "AC-3", "Min-Conflicts"]),
            ("6. ĐỐI KHÁNG", ["Minimax", "Alpha-Beta", "Expectimax"])
        ]
        
        start_x = 150
        start_y = 220
        col_width = 380
        row_height = 160
        
        self.menu_buttons.clear()
        mouse_pos = pygame.mouse.get_pos()
        
        for g_idx, (title, algos) in enumerate(groups):
            col = g_idx % 3
            row = g_idx // 3
            bx = start_x + col * col_width
            by = start_y + row * row_height
            
            # Khung nhóm
            pygame.draw.rect(self.screen, PANEL_BG, (bx, by, col_width-30, row_height-20), border_radius=12)
            pygame.draw.rect(self.screen, BORDER_GLOW, (bx, by, col_width-30, row_height-20), width=2, border_radius=12)
            self.draw_text(title, self.font_md, (200, 220, 255), (bx + 15, by + 15))
            
            # Các nút thuật toán trong nhóm
            for i, algo in enumerate(algos):
                ax = bx + 15
                ay = by + 45 + i * 30
                btn_rect = pygame.Rect(ax, ay, 320, 25)
                self.menu_buttons[algo] = btn_rect
                
                is_hover = btn_rect.collidepoint(mouse_pos)
                pygame.draw.rect(self.screen, (40, 60, 100) if is_hover else (25, 35, 60), btn_rect, border_radius=6)
                pygame.draw.circle(self.screen, COLORS[algo], (ax + 15, ay + 12), 6)
                self.draw_text(algo, self.font_sm, (255,255,255), (ax + 30, ay + 3))

        pygame.display.flip()

    # --- HÀM VẼ QUÂN CỜ RICOCHET 3D ---
    # --- HÀM VẼ QUÂN CỜ RICOCHET 3D ---
    def draw_3d_robot(self, surface, x, y, color):
        cx, cy = int(x), int(y)
        # Bán kính tự động co giãn theo kích thước ô lưới (tỉ lệ 35%)
        R = max(10, int(self.cell_size * 0.35)) 
        
        # Đổ bóng
        pygame.draw.circle(self.shadow_surface, SHADOW_COLOR, (cx + int(R*0.2), cy + int(R*0.25)), int(R*0.9))
        
        # Thân quân cờ (Màu tối hơn)
        base_color = (max(color[0]-60, 0), max(color[1]-60, 0), max(color[2]-60, 0))
        pygame.draw.circle(surface, base_color, (cx, cy), R) 
        
        # Đỉnh quân cờ (Màu sáng)
        pygame.draw.circle(surface, color, (cx, cy - int(R*0.2)), int(R*0.9))  
        
        # Hiệu ứng bóng bẩy (Glossy)
        glow_rect = pygame.Rect(cx - int(R*0.5), cy - int(R*0.8), R, int(R*0.5))
        pygame.draw.ellipse(surface, (255, 255, 255, 150), glow_rect)

    def draw_mini_board(self, ox, oy, b_size, robot_obj, title_text):
        c_size = b_size // self.grid_size
        
        # Vẽ Tiêu đề
        self.draw_text(title_text, self.font_md, (200, 255, 200), (ox, oy - 30))
        
        # Vẽ Khung Nền
        brd = pygame.Rect(ox-4, oy-4, b_size+8, b_size+8)
        pygame.draw.rect(self.screen, BOARD_BG, brd, border_radius=8)
        pygame.draw.rect(self.screen, BORDER_GLOW, brd, width=2, border_radius=8)
        
        # Vẽ Lưới
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                rect = (ox + c*c_size, oy + r*c_size, c_size, c_size)
                pygame.draw.rect(self.screen, TILE_COLOR, rect)
                pygame.draw.rect(self.screen, TILE_LINE, rect, 1)
                
        # Vẽ Đích
        tx, ty = ox + self.target_pos[0]*c_size + c_size//2, oy + self.target_pos[1]*c_size + c_size//2
        pygame.draw.circle(self.screen, (*TARGET_COLOR, 50), (tx, ty), int(c_size * 0.4))
        pygame.draw.circle(self.screen, TARGET_COLOR, (tx, ty), int(c_size * 0.2))
        
        # Vẽ Tường
        for p1, p2 in self.walls:
            if p1[0] < 0 or p2[0] >= self.grid_size or p1[1] < 0 or p2[1] >= self.grid_size: continue
            if p1[0] != p2[0]: 
                w_rect = pygame.Rect(ox + p2[0]*c_size - 2, oy + p1[1]*c_size - 2, 4, c_size + 4)
            else:
                w_rect = pygame.Rect(ox + p1[0]*c_size - 2, oy + p2[1]*c_size - 2, c_size + 4, 4)
            pygame.draw.rect(self.screen, WALL_COLOR, w_rect)
            
        # Vẽ Robot với tỷ lệ thu nhỏ chuẩn xác (Giữ nguyên Animation trượt mượt mà)
        if robot_obj:
            ratio = c_size / self.cell_size
            rx = ox + robot_obj.visual_pos[0] * ratio + c_size//2
            ry = oy + robot_obj.visual_pos[1] * ratio + c_size//2
            R = max(6, int(c_size * 0.35))
            
            pygame.draw.circle(self.shadow_surface, SHADOW_COLOR, (int(rx)+2, int(ry)+3), R)
            pygame.draw.circle(self.screen, robot_obj.color, (int(rx), int(ry)), R)
            
            # Gắn chữ chỉ thị
            char = "S2" if robot_obj.name == "Bóng ma" else "S1"
            t_surf = self.font_sm.render(char, True, (255,255,255))
            self.screen.blit(t_surf, (int(rx) - t_surf.get_width()//2, int(ry) - t_surf.get_height()//2))

    def draw_simulation(self):
        self.screen.fill(BG_COLOR)
        self.shadow_surface.fill((0,0,0,0))
        mouse_pos = pygame.mouse.get_pos()

        # Tính toán kích thước thực tế
        actual_board_size = self.cell_size * self.grid_size

        # Tiêu đề trên cùng
        title_str = f"MÔ PHỎNG: {self.current_ai}" if self.current_ai else "CHẾ ĐỘ TỰ DO"
        self.draw_text(title_str, self.font_title, TARGET_COLOR, (OFFSET_X, 20))
        pygame.draw.line(self.screen, BORDER_GLOW, (OFFSET_X, 70), (OFFSET_X + actual_board_size, 70), 2)

        # --- FIX LỖI: Dời r_active lên đầu để tất cả các giao diện đều gọi được ---
        r_active = self.get_robot_by_name(self.current_ai) if self.current_ai else self.player
        # --------------------------------------------------------------------------

        # ---------------- CỘT 1: MAP LƯỚI (BÊN TRÁI - RỘNG THOẢI MÁI) ----------------
        # ---------------- CỘT 1: MAP LƯỚI ----------------
        if self.current_ai == "Sensorless":
            mini_size = (actual_board_size // 2) - 20
            
            # Map 1: Vị trí Thực (Player)
            self.draw_mini_board(OFFSET_X, OFFSET_Y + 50, mini_size, self.player, "TRẠNG THÁI NIỀM TIN 1 (State 1)")
            
            # Map 2: Vị trí Ảo (Ghost)
            if hasattr(self, 'sensorless_ghost'):
                self.draw_mini_board(OFFSET_X + mini_size + 40, OFFSET_Y + 50, mini_size, self.sensorless_ghost, "TRẠNG THÁI NIỀM TIN 2 (State 2)")
                
            self.draw_text("Mô hình Belief State: Lập kế hoạch đồng bộ (Conformant Planning)", self.font_md, (255, 150, 255), (OFFSET_X, OFFSET_Y + mini_size + 70))
            self.draw_text("Bật chế độ sửa (Phím E) để nhấp vào từng map và đặt lại State 1 / State 2.", self.font_sm, (150, 150, 150), (OFFSET_X, OFFSET_Y + mini_size + 95))
            
            # Highlight ô Edit cho Mini-map
            if self.edit_mode > 0:
                mx, my = mouse_pos
                m1_rect = pygame.Rect(OFFSET_X, OFFSET_Y + 50, mini_size, mini_size)
                m2_rect = pygame.Rect(OFFSET_X + mini_size + 40, OFFSET_Y + 50, mini_size, mini_size)
                c_size = mini_size / self.grid_size
                color_map = {1: (255, 50, 50, 100), 2: (50, 255, 50, 100), 3: (255, 255, 50, 100), 4: (255, 100, 255, 100)}
                hl_color = color_map.get(self.edit_mode, (255,255,255,50))
                
                for r_rect in [m1_rect, m2_rect]:
                    if r_rect.collidepoint(mx, my):
                        hc, hr = int((mx - r_rect.x) / c_size), int((my - r_rect.y) / c_size)
                        if 0 <= hc < self.grid_size and 0 <= hr < self.grid_size:
                            hl_rect = pygame.Rect(r_rect.x + hc*c_size, r_rect.y + hr*c_size, c_size, c_size)
                            pygame.draw.rect(self.shadow_surface, hl_color, hl_rect)
            self.screen.blit(self.shadow_surface, (0,0))
            
        else:
            # Giao diện Full Map (Cho các thuật toán bình thường)
            brd = pygame.Rect(OFFSET_X-8, OFFSET_Y-8, actual_board_size+16, actual_board_size+16)
            pygame.draw.rect(self.screen, BOARD_BG, brd, border_radius=12)
            pygame.draw.rect(self.screen, BORDER_GLOW, brd, width=2, border_radius=12)
            
            for r, c in itertools.product(range(self.grid_size), range(self.grid_size)):
                rect = (OFFSET_X + c*self.cell_size, OFFSET_Y + r*self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, TILE_COLOR, rect)
                pygame.draw.rect(self.screen, TILE_LINE, rect, 1)
    
            # Highlight ô Edit
            mx, my = mouse_pos
            if self.edit_mode > 0 and OFFSET_X <= mx <= OFFSET_X + actual_board_size and OFFSET_Y <= my <= OFFSET_Y + actual_board_size:
                hc, hr = int((mx - OFFSET_X) / self.cell_size), int((my - OFFSET_Y) / self.cell_size)
                highlight_rect = pygame.Rect(OFFSET_X + hc*self.cell_size, OFFSET_Y + hr*self.cell_size, self.cell_size, self.cell_size)
                color_map = {1: (255, 50, 50, 100), 2: (50, 255, 50, 100), 3: (255, 255, 50, 100), 4: (255, 100, 255, 100)}
                pygame.draw.rect(self.shadow_surface, color_map.get(self.edit_mode, (255,255,255,50)), highlight_rect)
    
            # Vẽ đích & Robot
            for t, col in [(self.target_pos, TARGET_COLOR), (self.target_pos_2, TARGET_2_COLOR)]:
                if t: 
                    tx, ty = OFFSET_X + t[0]*self.cell_size + self.cell_size//2, OFFSET_Y + t[1]*self.cell_size + self.cell_size//2
                    R_target = int(self.cell_size * 0.4)
                    pygame.draw.circle(self.screen, (*col, 50), (tx, ty), R_target)
                    pygame.draw.circle(self.screen, col, (tx, ty), int(R_target * 0.5))
    
            for p1, p2 in self.walls: self.draw_wall(p1, p2)
    
            r_active = self.get_robot_by_name(self.current_ai) if self.current_ai else self.player
            if r_active:
                rx, ry = int(OFFSET_X + r_active.visual_pos[0] + self.cell_size//2), int(OFFSET_Y + r_active.visual_pos[1] + self.cell_size//2)
                self.draw_3d_robot(self.screen, rx, ry, r_active.color)
                if r_active.name == "Người Chơi": pygame.draw.circle(self.screen, (0,0,0), (rx, ry-4), int(self.cell_size*0.1))
    
            # Vẽ thêm Robot Địch nếu đang ở nhóm 6
            if self.current_group_id == 6 and hasattr(self, 'enemy'):
                ex, ey = int(OFFSET_X + self.enemy.visual_pos[0] + self.cell_size//2), int(OFFSET_Y + self.enemy.visual_pos[1] + self.cell_size//2)
                self.draw_3d_robot(self.screen, ex, ey, self.enemy.color)
                R_eye = max(10, int(self.cell_size * 0.35))
                eye_offset = int(R_eye * 0.35)
                eye_radius = max(2, int(R_eye * 0.15))
                pygame.draw.circle(self.screen, (255, 50, 50), (ex - eye_offset, ey - eye_offset), eye_radius)
                pygame.draw.circle(self.screen, (255, 50, 50), (ex + eye_offset, ey - eye_offset), eye_radius)

            # VẼ BÓNG MA CHO PARTIAL-OBSERVABLE
            if self.current_ai == "Partial-Observable" and hasattr(self, 'belief_history') and self.belief_history and r_active:
                
                # Đồng bộ frame của bóng ma với số bước di chuyển của robot thực
                step_idx = min(r_active.moves, len(self.belief_history) - 1)
                current_belief = self.belief_history[step_idx]
                
                for (gx, gy) in current_belief:
                    if list((gx, gy)) != r_active.logic_pos: 
                        alpha = 100 + int(math.sin(pygame.time.get_ticks() * 0.005) * 80)
                        cx = int(OFFSET_X + gx * self.cell_size + self.cell_size//2)
                        cy = int(OFFSET_Y + gy * self.cell_size + self.cell_size//2)
                        
                        pygame.draw.circle(self.shadow_surface, (0, 255, 127, alpha), (cx, cy), int(self.cell_size*0.35))
                        self.draw_text("?", self.font_sm, (0, 0, 0), (cx - 4, cy - 8))
    
            # Vẽ Bóng ma cho AC-3
            if self.current_group_id == 5 and getattr(self, 'csp_domains', None):
                for i, domain in enumerate(self.csp_domains):
                    color = self.aux_robots[i].color
                    for (x, y) in domain:
                        offset_x = (i - 1) * 8 
                        cx = int(OFFSET_X + x * self.cell_size + self.cell_size//2) + offset_x
                        cy = int(OFFSET_Y + y * self.cell_size + self.cell_size//2)
                        pygame.draw.circle(self.shadow_surface, (*color, 120), (cx, cy), max(5, int(self.cell_size*0.15)))

            # Vẽ 3 Trợ thủ CSP
            if self.current_group_id == 5:
                for aux in getattr(self, 'aux_robots', []):
                    ax, ay = int(OFFSET_X + aux.visual_pos[0] + self.cell_size // 2), int(OFFSET_Y + aux.visual_pos[1] + self.cell_size // 2)
                    self.draw_3d_robot(self.screen, ax, ay, aux.color)
                    pygame.draw.line(self.screen, (0, 0, 0), (ax - 3, ay), (ax + 3, ay), 2)
                    pygame.draw.line(self.screen, (0, 0, 0), (ax, ay - 3), (ax, ay + 3), 2)
    
            self.screen.blit(self.shadow_surface, (0,0))

        # ---------------- CỘT 2: BẢNG ĐIỀU KHIỂN CHUNG (Ở GIỮA) ----------------
        mid_x = OFFSET_X + actual_board_size + 30 
        col_width = 300
        
        # 1. KHUNG MÔ TẢ THUẬT TOÁN (Nằm trên cùng)
        desc_title = self.current_ai if self.current_ai else "Chế độ Người Chơi"
        desc_content = ALGO_DESC.get(self.current_ai, "Dùng phím W, A, S, D hoặc Mũi tên để di chuyển. Nhấn '[' hoặc ']' để tăng giảm map.")
        
        words = desc_content.split(" "); lines = []; curr_line = ""
        for w in words:
            if self.font_sm.size(curr_line + w)[0] < col_width - 30: curr_line += w + " "
            else: lines.append(curr_line); curr_line = w + " "
        lines.append(curr_line)
        
        desc_height = max(100, 45 + len(lines)*22)
        desc_rect = pygame.Rect(mid_x, OFFSET_Y, col_width, desc_height)
        pygame.draw.rect(self.screen, PANEL_BG, desc_rect, border_radius=12)
        pygame.draw.rect(self.screen, TILE_LINE, desc_rect, width=1, border_radius=12)
        
        self.draw_text(desc_title, self.font_md, TARGET_COLOR, (mid_x + 15, OFFSET_Y + 12))
        for i, line in enumerate(lines):
            self.draw_text(line, self.font_sm, TEXT_COLOR, (mid_x + 15, OFFSET_Y + 38 + i*22))

        # 2. BẢNG TRẠNG THÁI (Nằm ngay dưới Mô tả)
        status_y = OFFSET_Y + desc_height + 15
        status_rect = pygame.Rect(mid_x, status_y, col_width, 160)
        pygame.draw.rect(self.screen, PANEL_BG, status_rect, border_radius=12)
        pygame.draw.rect(self.screen, BORDER_GLOW, status_rect, width=2, border_radius=12)
        
        self.draw_text("TRẠNG THÁI", self.font_md, TARGET_COLOR, (mid_x + 15, status_y + 12))
        pygame.draw.line(self.screen, TILE_LINE, (mid_x + 15, status_y + 38), (mid_x + col_width - 15, status_y + 38))
        
        status_lines = [
            f"Trạng thái: {self.sim_status}",
            f"Bản đồ Nhóm: {self.current_group_id}",
            f"Kích thước Map: {self.grid_size}x{self.grid_size} ô",
            f"Độ dài đường đi: {r_active.moves if r_active else 0}",
            f"Chế độ sửa (E): {['Đang Tắt', 'Vẽ Tường', 'Start Ta', 'Đặt Đích', 'Start Địch'][self.edit_mode]}"
        ]
        for i, line in enumerate(status_lines):
            self.draw_text(line, self.font_sm, (200, 220, 240), (mid_x + 15, status_y + 48 + i*22))

        # 3. NÚT BẤM (Nằm dưới cùng)
        btn_data = [
            ("Chạy AI", (46, 204, 113)),          
            (f"Chế độ: {'Từng bước' if getattr(self, 'step_mode', False) else 'Tự động'}", (155, 89, 182)),
            ("Bước tiếp (N)", (241, 196, 15))
        ]
        
        if self.current_ai == "Sensorless":
            btn_data.append(("Hoán đổi State 1-2", (255, 105, 180))) # Tên nút mới
            btn_data.append(("Random State 1-2", (155, 89, 182)))     # Tên nút mới
            
        btn_data.extend([
            (f"Chỉnh Map: {['TẮT', 'TƯỜNG', 'START TA', 'ĐÍCH', 'ĐỊCH'][self.edit_mode]}", (230, 126, 34)),
            ("Lưu Map Nhóm", (52, 152, 219)),     
            ("Đặt Lại (Reset)", (52, 73, 94)),    
            ("Trở Lại Menu", (231, 76, 60))       
        ])
        
        self.sim_buttons.clear()
        by = status_y + 160 + 15
        remaining_h = HEIGHT - by - 10
        btn_gap = min(50, max(30, remaining_h // len(btn_data)))
        btn_height = min(40, btn_gap - 8)

        for text, color in btn_data:
            btn_rect = pygame.Rect(mid_x, by, col_width, btn_height)
            self.sim_buttons[text] = btn_rect
            is_hover = btn_rect.collidepoint(mouse_pos)
            draw_col = (min(color[0]+30, 255), min(color[1]+30, 255), min(color[2]+30, 255)) if is_hover else color
            pygame.draw.rect(self.screen, draw_col, btn_rect, border_radius=20)
            pygame.draw.rect(self.screen, (255,255,255), btn_rect, width=2, border_radius=20)
            t_surf = self.font_md.render(text, True, (255,255,255))
            self.screen.blit(t_surf, (mid_x + col_width//2 - t_surf.get_width()//2, by + (btn_height//2 - t_surf.get_height()//2)))
            by += btn_gap

        # ---------------- CỘT 3: BẢNG LOG (HẸP LẠI VÀ CHUYỂN SANG GÓC PHẢI CÙNG) ----------------
        log_x = mid_x + col_width + 20
        log_width = max(250, WIDTH - log_x - 20)
        
        log_rect = pygame.Rect(log_x, 20, log_width, HEIGHT - 40)
        pygame.draw.rect(self.screen, (15, 20, 35), log_rect, border_radius=12)
        pygame.draw.line(self.screen, TILE_LINE, (log_x + 15, 60), (log_x + log_width - 15, 60))
        
        self.draw_text("NHẬT KÝ (Cuộn)", self.font_md, (255, 255, 255), (log_x + 15, 30))
        
        total_logs = len(self.logs)
        if total_logs > 15:
            scrollbar_height = max(30, (HEIGHT - 100) * 15 / total_logs)
            scroll_progress = self.log_scroll / max(1, total_logs - 15)
            sb_y = 70 + scroll_progress * (HEIGHT - 100 - scrollbar_height)
            pygame.draw.rect(self.screen, (60, 80, 120), (log_x + log_width - 15, sb_y, 6, scrollbar_height), border_radius=3)

        ly = 75
        reversed_logs = self.logs[::-1]
        visible_logs = reversed_logs[self.log_scroll : self.log_scroll + 35] 
        
        for i, log in enumerate(visible_logs): 
            words = log['text'].split(" "); lines = []; curr_line = ""
            for w in words:
                if self.font_log.size(curr_line + w)[0] < log_width - 35: curr_line += w + " "
                else: lines.append(curr_line); curr_line = w + " "
            lines.append(curr_line)
            
            for line in lines:
                if ly > HEIGHT - 30: break 
                self.draw_text(f"> {line}", self.font_log, log['color'], (log_x + 15, ly))
                ly += 22
            ly += 5

        # Đổi trỏ chuột khi hover nút
        if any(r.collidepoint(mouse_pos) for r in self.menu_buttons.values()) or any(r.collidepoint(mouse_pos) for r in self.sim_buttons.values()):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else: pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        pygame.display.flip()

    def player_move(self, dx, dy):
        if self.sim_status == "Đang chạy" or self.player.finished or self.player.path: return
        
        # Nếu ở nhóm Đối kháng, người chơi phải coi Địch là Bức tường cứng
        obs = {tuple(self.enemy.logic_pos)} if self.current_group_id == 6 and hasattr(self, 'enemy') else set()
        
        dest = self.get_slide_dest(tuple(self.player.logic_pos), (dx, dy), obs)
        if dest != tuple(self.player.logic_pos): 
            self.player.path.append(dest); self.player.logic_pos = list(dest)

    def trigger_run_ai(self):
        if not self.current_ai: return
        if self.ai_is_computing:
            self.log_msg("AI đang suy nghĩ, vui lòng đợi...", (255, 255, 0))
            return
            
        self.reset_simulation()
        
        # --- MỚI SỬA: CHỌN ĐÚNG ROBOT ĐỂ TÍNH TOÁN ---
        if self.current_ai == "Sensorless":
            r = self.player # Ép dùng Player làm State 1
        else:
            r = self.get_robot_by_name(self.current_ai)
            
        self.log_msg(f"Tiến hành chạy: {self.current_ai}...", (100, 200, 255))
        self.sim_status = "Đang tính toán..."
        
        self.ai_is_computing = True
        self.ai_robot_computing = r
        threading.Thread(target=self.thread_compute_ai, args=(r,), daemon=True).start()

    def thread_compute_ai(self, r):
        # Đây là không gian luồng phụ: Mọi tính toán nặng nề sẽ nằm ở đây mà không làm đơ game
        path = self.compute_path_for_ai(r)
        
        # Tính xong, gán kết quả vào biến để luồng chính nhận diện
        self.ai_result_path = path if path is not None else []

    def update(self):
        if self.state != "SIMULATION": return
        
        # --- 1. LUỒNG CHÍNH NHẬN KẾT QUẢ TỪ LUỒNG PHỤ ---
        if self.ai_is_computing and self.ai_result_path is not None:
            path = self.ai_result_path
            r = self.ai_robot_computing
            
            self.ai_is_computing = False
            self.ai_result_path = None
            self.ai_robot_computing = None
            
            if path:
                self.log_msg(f"-> {self.current_ai} tìm thấy đường dài {len(path)} bước.", (0, 255, 0))
                dirs = []
                curr = r.start_pos
                for p in path:
                    if p[0] < curr[0]: dirs.append("TRÁI")
                    elif p[0] > curr[0]: dirs.append("PHẢI")
                    elif p[1] < curr[1]: dirs.append("LÊN")
                    elif p[1] > curr[1]: dirs.append("XUỐNG")
                    curr = p
                path_str = " -> ".join(dirs)
                if len(path_str) > 110: path_str = path_str[:107] + "..."
                self.log_msg(f"Chi tiết (Ta): {path_str}", (200, 255, 200))

                e_path = getattr(self.enemy, 'computed_path', []) if self.current_group_id == 6 and hasattr(self, 'enemy') else []
                ghost_path = getattr(self.sensorless_ghost, 'computed_path', []) if self.current_ai == "Sensorless" and hasattr(self, 'sensorless_ghost') else []
                
                if getattr(self, 'step_mode', False):
                    self.step_queue = []
                    if self.current_group_id == 6:
                        for idx in range(max(len(path), len(e_path))):
                            if idx < len(path): self.step_queue.append((r, path[idx]))
                            if idx < len(e_path): self.step_queue.append((self.enemy, e_path[idx]))
                    elif self.current_ai == "Sensorless":
                        for idx in range(len(path)):
                            self.step_queue.append((r, path[idx]))
                            self.step_queue.append((self.sensorless_ghost, ghost_path[idx]))
                    else:
                        for p in path: self.step_queue.append((r, p))
                    self.sim_status = f"Chờ bước tiếp (Còn {len(self.step_queue)} bước)"
                else:
                    r.path = path
                    if self.current_group_id == 6 and hasattr(self, 'enemy'): self.enemy.path = e_path
                    elif self.current_ai == "Sensorless" and hasattr(self, 'sensorless_ghost'): self.sensorless_ghost.path = ghost_path
                    self.sim_status = "Đang chạy"
            else:
                self.sim_status = "Kẹt (0 bước)"
                self.log_msg(f"-> {self.current_ai} KẸT / KHÔNG THỂ GIẢI.", (255, 100, 100))

        if self.ai_is_computing: return 
            
        # --- 2. XỬ LÝ DI CHUYỂN TRƯỢT CỦA ROBOT ---
        # --- MỚI SỬA: Nắm đầu State 1 kéo đi ---
        if self.current_ai == "Sensorless":
            r = self.player
        else:
            r = self.get_robot_by_name(self.current_ai) if self.current_ai else self.player
            
        active_robots = [r] if r else []
        if self.current_group_id == 6 and hasattr(self, 'enemy'): active_robots.append(self.enemy)
        if self.current_ai == "Sensorless" and hasattr(self, 'sensorless_ghost'): active_robots.append(self.sensorless_ghost)
            
        is_sliding = False
        for rb in active_robots:
            if rb and rb.path:
                is_sliding = True
                target_logic = rb.path[0]
                target_px = [target_logic[0]*self.cell_size, target_logic[1]*self.cell_size]
                
                if getattr(rb, 'current_target', None) != target_logic:
                    rb.current_target = target_logic; rb.moves += 1
                    
                dx = target_px[0] - rb.visual_pos[0]; dy = target_px[1] - rb.visual_pos[1]
                dist = math.hypot(dx, dy)
                speed = 10.0
                
                if dist < speed: 
                    rb.visual_pos = target_px; rb.path.pop(0)
                    rb.logic_pos = list(target_logic)
                else: 
                    rb.visual_pos[0] += (dx/dist) * speed; rb.visual_pos[1] += (dy/dist) * speed
                    
        # --- 3. KIỂM TRA THẮNG / THUA / HOÀN THÀNH BƯỚC ---
        if r and not is_sliding:
            # Nếu đang ở chế độ từng bước và vẫn còn hàng đợi -> Dừng chờ bấm N
            if getattr(self, 'step_mode', False) and getattr(self, 'step_queue', []):
                self.sim_status = f"Chờ bước tiếp (Còn {len(self.step_queue)} bước)"
            else:
                # Kiểm tra Đích hoặc bị Tóm
                if tuple(r.logic_pos) == self.target_pos:
                    if self.sim_status in ["Đang chạy"] or self.sim_status.startswith("Chờ bước tiếp"):
                        self.log_msg("ĐÃ TỚI ĐÍCH!", (0, 255, 0))
                        self.sim_status = "Ta Thắng!"
                # --- FIX: Đổi điều kiện thua thành trùng ô (0) ---
                elif self.current_group_id == 6 and hasattr(self, 'enemy') and tuple(r.logic_pos) == tuple(self.enemy.logic_pos):
                        if self.sim_status in ["Đang chạy"] or self.sim_status.startswith("Chờ bước tiếp"):
                            self.log_msg("BỊ ĐỊCH TÓM GỌN!", (255, 50, 50))
                            self.sim_status = "Địch Thắng!"
                else:
                        if self.sim_status == "Đang chạy" or self.sim_status.startswith("Chờ bước tiếp"): 
                            self.sim_status = "Dừng lại"

    def trigger_next_step(self):
        # --- FIX: MỞ KHÓA CHO NHÓM CSP NẾU ĐANG NGỦ ĐÔNG CHỜ LỆNH ---
        if getattr(self, 'csp_waiting', False):
            self.csp_waiting = False
            self.sim_status = "Đang tính toán..."
            return
        # -----------------------------------------------------------
        
        # Nếu bất kỳ robot nào đang trượt dở dang -> Khóa nút bấm
        active_robots = self.robots + ([self.enemy] if hasattr(self, 'enemy') else [])
        if any(rb.path for rb in active_robots): 
            return 
            
        if getattr(self, 'step_queue', []):
            next_rb, next_pos = self.step_queue.pop(0)
            next_rb.path.append(next_pos) 
            self.sim_status = "Đang chạy"
            self.log_msg(f"{'Ta' if next_rb.name != 'Địch' else 'Địch'} trượt 1 bước...", (255, 255, 150))
        elif self.sim_status.startswith("Chờ bước tiếp"):
            self.log_msg("Đã hiển thị hết các bước di chuyển!", (255, 200, 100))

    def get_robot_by_name(self, name):
        return next((r for r in self.robots if r.name == name), None)

    def main_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                
                # --- XỬ LÝ PHÓNG TO / THU NHỎ CỬA SỔ ---
                if event.type == pygame.VIDEORESIZE:
                    global WIDTH, HEIGHT
                    WIDTH, HEIGHT = event.w, event.h
                    self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                    self.shadow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    
                    # Bàn cờ sẽ nở to tối đa, nhưng luôn chừa lại đúng 680px cho 2 cột bên phải
                    self.board_size = min(HEIGHT - 100, WIDTH - 680) 
                    self.cell_size = self.board_size // self.grid_size
                    
                    # Cập nhật vị trí đồ hoạ robot để không bị lệch khung
                    for r in self.robots:
                        r.visual_pos = [r.logic_pos[0]*self.cell_size, r.logic_pos[1]*self.cell_size]
                    
                # --- XỬ LÝ LĂN CHUỘT ĐỂ CUỘN LOG ---
                if event.type == pygame.MOUSEWHEEL:
                    mx, my = pygame.mouse.get_pos()
                    if mx > 1060: # Chỉ cuộn khi trỏ chuột đang nằm bên bảng Log
                        self.log_scroll -= event.y * 2 # Lăn 1 nấc cuộn 2 dòng
                        max_scroll = max(0, len(self.logs) - 15)
                        self.log_scroll = max(0, min(self.log_scroll, max_scroll))
                
                if event.type == pygame.MOUSEBUTTONDOWN: 
                    mx, my = event.pos
                    
                    if self.state == "MENU" and event.button == 1:
                        for ai_name, rect in self.menu_buttons.items():
                            if rect.collidepoint(event.pos):
                                self.logs.clear()

                                self.current_ai = ai_name
                                self.current_group_id = ALGO_GROUPS[ai_name]
                                
                                self.load_map(group_id=self.current_group_id)
                                
                                self.state = "SIMULATION"
                                self.log_msg(f"Đã mở mô phỏng: {ai_name}", TARGET_COLOR)
                                
                    elif self.state == "SIMULATION":
                        # 1. XỬ LÝ NÚT BẤM (Gộp chung tất cả các nút vào 1 vòng lặp duy nhất)
                        button_clicked = False
                        if event.button == 1:
                            for btn_name, rect in list(self.sim_buttons.items()):
                                if rect.collidepoint(event.pos):
                                    button_clicked = True
                                    
                                    # CHỈ CHO PHÉP BẤM "BƯỚC TIẾP" VÀ "CHẾ ĐỘ" KHI AI ĐANG CHẠY
                                    if self.ai_is_computing and "Bước tiếp" not in btn_name and "Chế độ" not in btn_name:
                                        self.log_msg("AI đang chạy, vui lòng chờ hoặc bấm Bước tiếp!", (255, 100, 100))
                                        continue
                                        
                                    if "Chạy AI" in btn_name: self.trigger_run_ai()
                                    elif "Chế độ" in btn_name: 
                                        self.step_mode = not getattr(self, 'step_mode', False)
                                        self.log_msg(f"Chuyển sang chế độ: {'Từng bước' if self.step_mode else 'Tự động'}", (200, 255, 200))
                                        
                                        # TỪNG BƯỚC -> TỰ ĐỘNG
                                        if not self.step_mode and getattr(self, 'step_queue', []):
                                            for rb, pos in self.step_queue: rb.path.append(pos)
                                            self.step_queue = []; self.sim_status = "Đang chạy"
                                            
                                        # TỰ ĐỘNG -> TỪNG BƯỚC
                                        elif self.step_mode:
                                            active_robots = []
                                            for r in self.robots + [getattr(self, 'enemy', None), getattr(self, 'sensorless_ghost', None)]:
                                                if r and r.path: active_robots.append(r)
                                                
                                            if active_robots:
                                                self.step_queue = []
                                                max_len = max(len(rb.path) for rb in active_robots)
                                                for i in range(1, max_len):
                                                    for rb in active_robots:
                                                        if i < len(rb.path): self.step_queue.append((rb, rb.path[i]))
                                                for rb in active_robots: rb.path = [rb.path[0]]
                                                self.sim_status = f"Chờ bước tiếp (Còn {len(self.step_queue)} bước)"
                                                
                                    elif "Bước tiếp" in btn_name: self.trigger_next_step()
                                    
                                    # CÁC NÚT RIÊNG CỦA NHÓM SENSORLESS
                                    elif "Hoán đổi State" in btn_name:
                                        temp = self.player.start_pos
                                        self.player.start_pos = self.sensorless_ghost.start_pos
                                        self.sensorless_ghost.start_pos = temp
                                        self.reset_simulation()
                                        self.log_msg("Đã hoán đổi Vị trí State 1 và State 2!", (255, 150, 255))
                                    elif "Random State" in btn_name:
                                        self.player.start_pos = list(self.get_random_valid_pos(set()))
                                        self.sensorless_ghost.start_pos = list(self.get_random_valid_pos(set(), tuple(self.player.start_pos)))
                                        self.reset_simulation()
                                        self.log_msg("Đã random vị trí State 1 và State 2!", (0, 255, 255))
                                        
                                    elif "Chỉnh Map" in btn_name: self.edit_mode = (self.edit_mode + 1) % 5
                                    elif "Lưu Map" in btn_name: self.save_custom_map()
                                    elif "Đặt Lại" in btn_name: self.reset_simulation()
                                    elif "Trở Lại" in btn_name: 
                                        self.state = "MENU"; self.current_ai = None; self.log_msg("Đã về Menu Chính.")
                        
                        # 2. XỬ LÝ CLICK SỬA MAP (CHỈ KHI CHƯA BẤM VÀO BẤT KỲ NÚT NÀO)
                        if not button_clicked:
                            actual_board_size = self.cell_size * self.grid_size
                            mini_size = (actual_board_size // 2) - 20
                            
                            map_clicked = 0
                            c, r = 0, 0
                            map_ox, map_oy, map_csize = OFFSET_X, OFFSET_Y, self.cell_size
                            
                            if self.current_ai == "Sensorless":
                                m1 = pygame.Rect(OFFSET_X, OFFSET_Y + 50, mini_size, mini_size)
                                m2 = pygame.Rect(OFFSET_X + mini_size + 40, OFFSET_Y + 50, mini_size, mini_size)
                                c_size = mini_size / self.grid_size
                                
                                if m1.collidepoint(mx, my):
                                    map_clicked, map_ox, map_oy, map_csize = 1, m1.x, m1.y, c_size
                                elif m2.collidepoint(mx, my):
                                    map_clicked, map_ox, map_oy, map_csize = 2, m2.x, m2.y, c_size
                            else:
                                full = pygame.Rect(OFFSET_X, OFFSET_Y, actual_board_size, actual_board_size)
                                if full.collidepoint(mx, my):
                                    map_clicked = 1
                            
                            if map_clicked > 0:
                                if self.ai_is_computing: 
                                    self.log_msg("Đang tính toán, không thể sửa Map!", (255, 50, 50))
                                    continue
                                
                                c = int((mx - map_ox) / map_csize)
                                r = int((my - map_oy) / map_csize)
                                c = max(0, min(c, self.grid_size - 1))
                                r = max(0, min(r, self.grid_size - 1))
                                
                                if self.edit_mode == 1 and event.button == 1:
                                    self.toggle_wall((mx, my), map_ox, map_oy, map_csize)
                                elif self.edit_mode == 2 and event.button == 1:
                                    if self.current_ai == "Sensorless":
                                        if map_clicked == 1:
                                            self.player.start_pos = [c, r]
                                            self.log_msg(f"Đã đặt State 1 tại {(c, r)}", (100, 255, 100))
                                        elif map_clicked == 2:
                                            self.sensorless_ghost.start_pos = [c, r]
                                            self.log_msg(f"Đã đặt State 2 tại {(c, r)}", (100, 255, 100))
                                    else:
                                        for rb in self.robots: rb.start_pos = [c, r]
                                        self.log_msg(f"Đã đặt Start mới tại {(c, r)}", (100, 255, 100))
                                    self.reset_simulation()
                                elif self.edit_mode == 3:
                                    if event.button == 1: 
                                        self.target_pos = (c, r); self.log_msg(f"Đã đặt Đích 1 tại {(c, r)}", TARGET_COLOR)
                                    elif event.button == 3: 
                                        self.target_pos_2 = (c, r) if self.target_pos_2 != (c, r) else None
                                        self.log_msg(f"Đã đặt Đích 2 tại {(c, r)}", TARGET_2_COLOR)
                                    self.reset_simulation()
                                elif self.edit_mode == 4 and event.button == 1:
                                    if self.current_group_id == 6 and hasattr(self, 'enemy'):
                                        self.enemy.start_pos = [c, r]
                                        self.reset_simulation()
                                        self.log_msg(f"Đã đặt Địch tại tọa độ {(c, r)}", (255, 50, 50))
                                    else:
                                        self.log_msg("Chỉ có thể đặt Địch ở Nhóm Đối kháng!", (255, 150, 0))
                                
                if event.type == pygame.KEYDOWN and self.state == "SIMULATION":
                    # --- XỬ LÝ PHÍM TẮT MỚI ---
                    if event.key == pygame.K_ESCAPE: 
                        self.state = "MENU"; self.current_ai = None; self.log_msg("Đã về Menu Chính.")
                    elif event.key == pygame.K_n: self.trigger_next_step()

                    if self.ai_is_computing: 
                        continue

                    if event.key == pygame.K_n: self.trigger_next_step()
                    elif event.key == pygame.K_m: 
                        self.step_mode = not getattr(self, 'step_mode', False)
                        self.log_msg(f"Chuyển sang chế độ: {'Từng bước' if self.step_mode else 'Tự động'}", (200, 255, 200))
                        
                        if not self.step_mode and getattr(self, 'step_queue', []):
                            for rb, pos in self.step_queue: rb.path.append(pos)
                            self.step_queue = []; self.sim_status = "Đang chạy"
                        elif self.step_mode:
                            active_robots = []
                            for r in self.robots + [getattr(self, 'enemy', None), getattr(self, 'sensorless_ghost', None)]:
                                if r and r.path: active_robots.append(r)
                                
                            if active_robots:
                                self.step_queue = []
                                max_len = max(len(rb.path) for rb in active_robots)
                                for i in range(1, max_len):
                                    for rb in active_robots:
                                        if i < len(rb.path): self.step_queue.append((rb, rb.path[i]))
                                for rb in active_robots: rb.path = [rb.path[0]]
                                self.sim_status = f"Chờ bước tiếp (Còn {len(self.step_queue)} bước)"
                    # --------------------------

                    if event.key == pygame.K_e: self.edit_mode = (self.edit_mode + 1) % 5
                    elif event.key in (pygame.K_UP, pygame.K_w): self.player_move(0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s): self.player_move(0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a): self.player_move(-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d): self.player_move(1, 0)
                    elif event.key == pygame.K_LEFTBRACKET: # Bấm '[' để Giảm map
                        if self.grid_size > 2:
                            self.grid_size -= 1
                            self.cell_size = self.board_size // self.grid_size
                            self.walls.clear() # Xóa tường cũ
                            
                            # Xây lại tường biên (Boundary) để robot không trượt ra vô cực
                            for i in range(self.grid_size):
                                self.walls.add(((-1, i), (0, i))); self.walls.add(((self.grid_size-1, i), (self.grid_size, i)))
                                self.walls.add(((i, -1), (i, 0))); self.walls.add(((i, self.grid_size-1), (i, self.grid_size)))
                            
                            # Ép lại toạ độ để không bị tràn khung
                            self.target_pos = (min(self.target_pos[0], self.grid_size-1), min(self.target_pos[1], self.grid_size-1))
                            
                            # Cập nhật cho cả phe Ta lẫn phe Địch
                            active_robots = self.robots + ([self.enemy] if hasattr(self, 'enemy') else [])
                            for r in active_robots: 
                                r.start_pos = [min(r.start_pos[0], self.grid_size-1), min(r.start_pos[1], self.grid_size-1)]
                            self.reset_simulation()
                            self.log_msg(f"Đã giảm kích thước Map xuống {self.grid_size}x{self.grid_size}", (255, 255, 100))
                            
                    elif event.key == pygame.K_RIGHTBRACKET: # Bấm ']' để Tăng map
                        if self.grid_size < 16: # <--- SỬA SỐ 32 THÀNH SỐ 16 Ở ĐÂY
                            self.grid_size += 1
                            self.cell_size = self.board_size // self.grid_size
                            self.walls.clear()
                            
                            # Xây lại tường biên (Boundary) để robot không trượt ra vô cực
                            for i in range(self.grid_size):
                                self.walls.add(((-1, i), (0, i))); self.walls.add(((self.grid_size-1, i), (self.grid_size, i)))
                                self.walls.add(((i, -1), (i, 0))); self.walls.add(((i, self.grid_size-1), (i, self.grid_size)))
                            
                            self.reset_simulation()
                            self.log_msg(f"Đã tăng kích thước Map lên {self.grid_size}x{self.grid_size}", (255, 255, 100))

            self.update()
            if self.state == "MENU": self.draw_menu()
            else: self.draw_simulation()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = RicochetArena()
    game.main_loop()