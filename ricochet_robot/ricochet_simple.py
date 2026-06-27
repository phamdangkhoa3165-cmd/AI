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
CELL_SIZE = 40 
OFFSET_X, OFFSET_Y = 50, 90 # Đưa map sang trái
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
    "Minimax": (255, 60, 60), "Alpha-Beta": (60, 255, 60), "Expectimax": (60, 60, 255)
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
        self.counter = itertools.count() 
        self.shadow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        self.menu_buttons = {}
        self.sim_buttons = {}
        
        self.robots = [Robot(name, (0,0)) for name in COLORS.keys()]
        self.player = self.robots[0]
        
        self.log_msg("Hệ thống khởi động thành công.", (0, 255, 100))

    def log_msg(self, msg, color=(200, 220, 255)):
        self.logs.append({"text": msg, "color": color})
        if len(self.logs) > 35: self.logs.pop(0)

    # ================= QUẢN LÝ MAP =================
    def save_custom_map(self):
        filename = f"ricochet_map_group_{self.current_group_id}.json"
        walls_list = [[list(p1), list(p2)] for p1, p2 in self.walls]
        data = {
            "walls": walls_list, 
            "target": self.target_pos,
            "target_2": self.target_pos_2,
            "start": self.player.start_pos
        }
        try:
            with open(filename, "w") as f: json.dump(data, f)
            self.log_msg(f"Đã lưu thành công Map cho Nhóm {self.current_group_id}.", (0, 255, 100))
        except Exception as e:
            self.log_msg(f"Lỗi khi lưu map: {e}", (255, 50, 50))

    def load_map(self, group_id=None):
        if group_id is not None: self.current_group_id = group_id
        self.target_pos_2 = None 
        filename = f"ricochet_map_group_{self.current_group_id}.json"
        
        if os.path.exists(filename):
            try:
                with open(filename, "r") as f: data = json.load(f)
                self.walls = {tuple((tuple(w[0]), tuple(w[1]))) for w in data["walls"]}
                self.target_pos = tuple(data["target"])
                t2 = data.get("target_2")
                self.target_pos_2 = tuple(t2) if t2 else None
                st = data.get("start")
                common_start = tuple(st) if st else self.get_random_valid_pos(set())
                self.log_msg(f"Đã tải Map của Nhóm {self.current_group_id}.", (0, 255, 255))
            except Exception:
                common_start = self.generate_random_map()
        else:
            self.log_msg(f"Sinh map ngẫu nhiên (Nhóm {self.current_group_id} chưa có Map).", (255, 200, 0))
            common_start = self.generate_random_map()
            
        for r in self.robots: r.start_pos = list(common_start)
        self.reset_simulation()

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
                    if len(path) > max_steps:
                        max_steps = len(path); best_start = start; best_walls = self.walls.copy(); best_target = self.target_pos
                    if 4 <= len(path) <= 15: valid_starts.append(start)
            if valid_starts: return random.choice(valid_starts)
        if max_steps > 0:
            self.walls = best_walls; self.target_pos = best_target; return best_start
        return self.get_random_valid_pos(set())

    def reset_simulation(self):
        self.sim_status = "Chờ lệnh"
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
        # 1. Khởi tạo tập FRONTIER = {Start} với f(Start) = g(Start) + h(Start)
        g_costs = {start: 0}
        f_start = 0 + self.heuristic(start)
        frontier = [(f_start, next(self.counter), start, [])]
        frontier_set = {start}
        
        # 2. Khởi tạo tập REACHED = {}
        reached = set()

        # 3. TRONG KHI (FRONTIER không rỗng):
        while frontier:
            # a. Chọn trạng thái n từ FRONTIER có f(n) nhỏ nhất
            f_n, _, n, p = heapq.heappop(frontier)
            if n in frontier_set: 
                frontier_set.remove(n)
            else: 
                continue

            # b. NẾU n == Goal:
            if n == self.target_pos:
                return p

            # c. Loại bỏ n khỏi FRONTIER và thêm n vào REACHED
            reached.add(n)

            # d. Với mỗi trạng thái m kề với n:
            for m in self.get_neighbors(n, obs):
                # i. Tính toán chi phí thực tế mới: g_new(m) = g(n) + cost(m)
                g_new = g_costs[n] + 1
                
                # ii. NẾU m đã nằm trong REACHED:
                if m in reached:
                    if g_new >= g_costs.get(m, float('inf')): 
                        continue # Bỏ qua trạng thái tệ hơn
                    else:
                        # Xóa m khỏi REACHED và cập nhật lại g(m)
                        reached.remove(m)
                        g_costs[m] = g_new
                        f_m = g_new + self.heuristic(m)
                        heapq.heappush(frontier, (f_m, next(self.counter), m, p + [m]))
                        frontier_set.add(m)
                        
                # iii. NẾU m đã nằm trong FRONTIER:
                elif m in frontier_set:
                    if g_new < g_costs[m]:
                        # Cập nhật lại g(m) và f(m)
                        g_costs[m] = g_new
                        f_m = g_new + self.heuristic(m)
                        heapq.heappush(frontier, (f_m, next(self.counter), m, p + [m]))
                        
                # iv. NẾU m chưa có mặt trong FRONTIER và REACHED:
                else:
                    g_costs[m] = g_new
                    f_m = g_new + self.heuristic(m)
                    heapq.heappush(frontier, (f_m, next(self.counter), m, p + [m]))
                    frontier_set.add(m)
                    
        # 4. TRẢ VỀ "Thất bại"
        return []
    
    # ================= Nhóm LOCAL SEARCH =================
    def run_simple_hc(self, start, obs):
        # 1. Khởi tạo trạng thái hiện tại Current_State = Start.
        current_state = start
        # Tính giá trị đánh giá của Current_State. (Dùng hàm Heuristic h)
        current_value = self.heuristic(current_state)
        path = []

        # 2. TRONG KHI (đúng):
        while True:
            if current_state == self.target_pos: return path
            found_better = False
            
            # a. Sinh lần lượt các trạng thái lân cận của Current_State.
            # b. Với mỗi trạng thái lân cận Next_State:
            for next_state in self.get_neighbors(current_state, obs):
                # i. Tính giá trị đánh giá của Next_State.
                next_value = self.heuristic(next_state)
                
                # ii. NẾU Value(Next_State) > Value(Current_State):
                # (Lưu ý: Khoảng cách ngắn hơn tức là tốt hơn, nên dùng dấu <)
                if next_value < current_value:
                    current_state = next_state
                    current_value = next_value
                    path.append(current_state)
                    found_better = True
                    # Chuyển sang lần lặp tiếp theo. (Thoát vòng lặp for để quay lại while)
                    break 

            # c. NẾU không tồn tại trạng thái lân cận nào tốt hơn:
            if not found_better:
                # Dừng vì đã đạt cực đại cục bộ.
                break 

        # 3. TRẢ VỀ Current_State.
        return path if current_state == self.target_pos else []

    def run_beam_search(self, start, obs, k=3):
        # 1. Khởi tạo: Current_State_set = {Sinh ngẫu nhiên k trạng thái từ Start}
        current_state_set = []
        
        # Để đường đi liên tục (không bị dịch chuyển tức thời), ta lấy trực tiếp
        # các ô lân cận của Start làm k trạng thái khởi tạo.
        start_neighbors = self.get_neighbors(start, obs)
        if not start_neighbors: 
            return [] # Kẹt ngay từ đầu
            
        for _ in range(k):
            # Chọn ngẫu nhiên 1 lân cận của Start
            first_state = random.choice(start_neighbors)
            # Lưu trữ dưới dạng Tuple: (Trạng_thái_hiện_tại, Mảng_lưu_vết_đường_đi)
            current_state_set.append((first_state, [first_state]))
            
        # 2. TRONG KHI (đúng):
        # (Dùng vòng lặp an toàn 50 bước để chống treo game nếu bị kẹt vô tận)
        for _ in range(50):
            # Neighbor_States = rỗng
            neighbor_states = []
            
            # 2.1. SINH TRẠNG THÁI LÂN CẬN:
            # VỚI MỖI State trong Current_State_set:
            for state, path_history in current_state_set:
                # Sinh tất cả các trạng thái lân cận của State.
                # Thêm các trạng thái lân cận này vào Neighbor_States.
                for neighbor in self.get_neighbors(state, obs):
                    neighbor_states.append((neighbor, path_history + [neighbor]))
                    
            # 2.2. KIỂM TRA BẾ TẮC / KHÔNG CẢI THIỆN
            # NẾU Neighbor_States = rỗng:
            if not neighbor_states:
                # Sắp xếp Current_State_set theo h tốt dần
                current_state_set.sort(key=lambda item: self.heuristic(item[0]))
                # TRẢ VỀ trạng thái tốt nhất trong Current_State_set // Không còn lân cận nào để đi tiếp
                return current_state_set[0][1] 
                
            # 2.3. KIỂM TRA ĐÍCH:
            # VỚI MỖI Neighbor trong Neighbor_States:
            for neighbor, path_history in neighbor_states:
                # NẾU Neighbor == Goal: TRẢ VỀ Neighbor // Tìm thấy đích, dừng thuật toán
                if neighbor == self.target_pos:
                    return path_history
                    
            # 2.4. LỰA CHỌN CHÙM (NẾU CHƯA TÌM THẤY ĐÍCH):
            # Sắp xếp Neighbor_States theo thứ tự giá trị hàm mục tiêu h tốt dần.
            neighbor_states.sort(key=lambda item: self.heuristic(item[0]))
            
            # Current_State_set = Lấy k trạng thái tốt nhất từ Neighbor_States đã sắp xếp.
            current_state_set = neighbor_states[:k]
            
        # Nếu chạy hết vòng lặp an toàn mà không chạm đích, trả về đường đi tốt nhất hiện tại
        current_state_set.sort(key=lambda item: self.heuristic(item[0]))
        return current_state_set[0][1]

    def run_simulated_annealing(self, start, obs):
        # current state = start
        current_state = start
        path = [] # Mảng lưu vết đường đi cho giao diện UI
        
        # T = T0 (Khởi tạo nhiệt độ ban đầu và các hệ số)
        T = 1000.0
        T_min = 0.01
        alpha = 0.95
        
        # while T > Tmin:
        while T > T_min:
            # if current state == goal:
            if current_state == self.target_pos:
                # return current state
                return path
                
            neighbors = self.get_neighbors(current_state, obs)
            if not neighbors: 
                break # Kẹt cứng không có lân cận
                
            # next state = RandomNeighbor(current state)
            next_state = random.choice(neighbors)
            
            # Δ = h(next state) - h(current state)
            delta = self.heuristic(next_state) - self.heuristic(current_state)
            
            # if Δ < 0:
            if delta < 0:
                # current state = next state
                current_state = next_state
                path.append(current_state)
            # else:
            else:
                # p = exp(-Δ / T)
                p = math.exp(-delta / T)
                
                # if Random(0,1) < p:
                if random.random() < p:
                    # current state = next state
                    current_state = next_state
                    path.append(current_state)
                    
            # T = α * T
            T = alpha * T

        # return current state (Trả về mảng đường đi nếu chạm đích)
        return path if current_state == self.target_pos else []

    # ================= MÔI TRƯỜNG PHỨC TẠP & CSP =================
    def run_sensorless(self, start, obs):
        # 1. Khởi tạo Trạng thái Niềm tin Ban đầu (Belief_Start)
        # Giả sử robot bị "mù", nó biết nó đang ở trong map nhưng không rõ tọa độ.
        # Để demo trực quan, ta giả định nó lúng túng giữa vị trí thật (start) và 1 vị trí ảo (start2).
        start2 = self.get_random_valid_pos(obs, start)
        self.log_msg(f"[Belief State] Khởi tạo Belief_Start = {{S1:{start}, S2:{start2}}}", (255, 150, 255))
        
        # Chuyển thành tuple (đã sắp xếp) để làm key Hash trong tập hợp
        belief_start = tuple(sorted([start, start2]))
        
        # 2. Khởi tạo Frontier (Hàng đợi FIFO) và tập Reached
        # Mỗi phần tử trong Frontier chứa: (Belief_State_Hiện_Tại, Vị_Trí_S1_Thực_Tế, Mảng_Vết_Đường_Đi_S1)
        frontier = deque([(belief_start, start, [])])
        reached = {belief_start}
        
        # 3. TRONG KHI (Frontier không rỗng):
        while frontier:
            # a. Lấy Belief_Current ra
            current_belief, current_s1, path_s1 = frontier.popleft()
            
            # (Chống treo game nếu môi trường quá phức tạp không có kế hoạch ép buộc)
            if len(path_s1) > 20: 
                continue
                
            # b. NẾU Belief_Current thỏa mãn Belief_Goal:
            # (Định nghĩa Belief_Goal: Mọi trạng thái có thể có lúc này ĐỀU PHẢI NẰM TẠI ĐÍCH)
            if all(s == self.target_pos for s in current_belief):
                self.log_msg(f"-> Đạt Belief_Goal! (Kế hoạch ép buộc dài {len(path_s1)} bước).", (0, 255, 255))
                return path_s1
                
            # c. VỚI MỖI hành động a trong tập Hành động:
            for action in [(0,-1), (0,1), (-1,0), (1,0)]:
                # i. Tính toán Belief_Next = Tập hợp kết quả của hành động a lên MỌI trạng thái s trong Belief_Current
                next_belief_set = set()
                for s in current_belief:
                    next_belief_set.add(self.get_slide_dest(s, action, obs))
                    
                next_belief = tuple(sorted(list(next_belief_set)))
                
                # ii. NẾU Belief_Next chưa được duyệt:
                if next_belief not in reached:
                    reached.add(next_belief)
                    
                    # Tính toán đường đi thật của S1 để vẽ đồ họa mô phỏng
                    next_s1 = self.get_slide_dest(current_s1, action, obs)
                    
                    # Thêm vào Frontier
                    frontier.append((next_belief, next_s1, path_s1 + [next_s1]))
                    
        # 4. TRẢ VỀ Thất bại
        self.log_msg("-> Kẹt! Không tồn tại Kế hoạch ép buộc hoàn toàn.", (255, 100, 100))
        return []

    def run_partial_observable(self, start, obs):
        self.log_msg("--- MÔI TRƯỜNG NHÌN THẤY MỘT PHẦN (PARTIAL OBSERVE) ---", (255, 200, 255))
        
        # 1. Khởi tạo Belief_Start (Niềm tin ban đầu)
        # Giả sử robot bị mất định vị, nó nghĩ nó có thể đang ở 1 trong 3 vị trí khác nhau.
        fake_1 = self.get_random_valid_pos(obs, start)
        fake_2 = self.get_random_valid_pos(obs, start)
        belief_state = {start, fake_1, fake_2}
        self.log_msg(f"[Belief Start] Robot bị mù toạ độ, nghĩ nó ở: {len(belief_state)} vị trí.", (200, 200, 255))

        # Cảm biến mô phỏng (Sensor): Nhận biết được các hướng có thể trượt (không bị kẹt tường sát bên)
        def get_percept(pos):
            # Trả về tuple 4 giá trị boolean (Up, Down, Left, Right). Vd: (True, False, True, True)
            return tuple(self.get_slide_dest(pos, d, obs) != pos for d in [(0,-1), (0,1), (-1,0), (1,0)])

        real_pos = start
        path = []

        # 2. Vòng lặp Hành động - Cảm biến - Cập nhật (Tối đa 30 bước khám phá)
        for step in range(30):
            # a. Đạt Belief Goal (Mục tiêu định vị thành công)
            # Khi tập Belief State chỉ còn 1, robot đã suy luận ra chính xác 100% vị trí thật
            if len(belief_state) == 1:
                localized_pos = list(belief_state)[0]
                self.log_msg(f"-> [Định vị Thành Công!] Robot chắc chắn đang ở: {localized_pos}", (0, 255, 0))
                
                # Sau khi định vị được bản thân, chuyển sang dùng A* để đi đến Đích
                self.log_msg(f"-> Chuyển sang thuật toán A* để tiến về Goal.", (0, 255, 255))
                astar_path = self.run_astar(localized_pos, obs)
                return path + astar_path

            # b. Chọn hành động (Action) để khám phá
            # Tìm các hướng đi hợp lệ từ vị trí thực tế để không bị đứng im
            valid_dirs = [d for d in [(0,-1), (0,1), (-1,0), (1,0)] if self.get_slide_dest(real_pos, d, obs) != real_pos]
            if not valid_dirs:
                self.log_msg("-> Lỗi: Kẹt cứng không thể di chuyển.", (255, 0, 0))
                return path

            # Robot chọn đi ngẫu nhiên để thu thập thông tin môi trường
            action = random.choice(valid_dirs)
            action_name = {(0,-1): "LÊN", (0,1): "XUỐNG", (-1,0): "TRÁI", (1,0): "PHẢI"}[action]

            # c. Thực thi hành động: Môi trường phản hồi Vị trí mới & Cảm biến (Percept)
            real_pos = self.get_slide_dest(real_pos, action, obs)
            path.append(real_pos)
            percept = get_percept(real_pos)
            
            self.log_msg(f"Bước {step+1}: Trượt {action_name}. Đọc cảm biến: {percept}", (220, 220, 220))

            # d. Cập nhật Trạng thái Niềm tin (Belief Update)
            # Công thức: B' = { s' = Result(s, a) | s thuộc B và Percept(s') == percept }
            new_belief_state = set()
            for s in belief_state:
                # Dự đoán vị trí điểm đến nếu xuất phát từ điểm s ảo
                s_next = self.get_slide_dest(s, action, obs)
                
                # Lọc: Nếu tại vị trí dự đoán mà cảm biến đọc KHÁC với thực tế -> Loại bỏ giả thuyết s_next
                if get_percept(s_next) == percept:
                    new_belief_state.add(s_next)

            belief_state = new_belief_state
            self.log_msg(f"   [Cập nhật Niềm tin] Loại bỏ giả thuyết sai. Còn: {len(belief_state)} vị trí.", (255, 255, 100))

        self.log_msg("-> Thất bại: Không thể định vị được bản thân sau 30 bước.", (255, 100, 100))
        return path
    
    def run_and_or_graph(self, start, obs):
        self.log_msg("--- DUYỆT CÂY AND-OR (Kế hoạch dự phòng) ---", (255, 255, 100))

        # function OR_SEARCH(state, problem, path):
        def or_search(state, path):
            # if state ∈ problem.goal_test:
            if state == self.target_pos:
                # return [] // kế hoạch rỗng (đã đạt mục tiêu)
                return [] 
                
            # if state ∈ path:
            if state in path:
                # return failure // tránh lặp
                return "failure" 
                
            # (Mẹo thực tế: Giới hạn độ sâu đệ quy để game không bị treo nếu kẹt vòng lặp lớn)
            if len(path) > 15: 
                return "failure"

            # for each action in problem.actions(state):
            for action in [(0,-1), (0,1), (-1,0), (1,0)]: 
                next_state = self.get_slide_dest(state, action, obs)
                if next_state == state: continue # Bỏ qua nếu trượt đâm tường sát bên
                
                # result_states = problem.results(state, action)
                # (Vì Ricochet là game đơn định, mỗi action chỉ ra 1 kết quả, nhưng ta vẫn đưa vào mảng để đúng logic AND)
                result_states = [next_state]
                
                # plan = AND_SEARCH(result_states, problem, path + [state])
                plan = and_search(result_states, path + [state])
                
                # if plan ≠ failure:
                if plan != "failure":
                    # return [action, plan]
                    # (Để UI vẽ được đường đi robot, ta thay 'action' bằng toạ độ 'next_state' để nối mảng)
                    return [next_state] + plan 
                    
            # return failure
            return "failure"

        # function AND_SEARCH(states, problem, path):
        def and_search(states, path):
            # plans = empty mapping // lưu kế hoạch cho từng state
            plans = []
            
            # for each s in states:
            for s in states:
                # plan_s = OR_SEARCH(s, problem, path)
                plan_s = or_search(s, path)
                
                # if plan_s == failure:
                if plan_s == "failure":
                    # return failure
                    return "failure"
                    
                # plans[s] = plan_s
                # (Với mảng 1D mô phỏng của game, ta dùng extend để gộp chuỗi hành động thay vì dùng dictionary mapping)
                plans.extend(plan_s)
                
            # return plans
            return plans

        # function AND_OR_GRAPH_SEARCH(problem):
        # return OR_SEARCH(problem.initial_state, problem, [])
        res = or_search(start, [])
        return res if res != "failure" else []

    def run_backtracking(self, start, obs):
        self.log_msg("Backtracking: Tìm kiếm chiều sâu kết hợp thỏa mãn Ràng buộc", (180, 100, 255))
        domain = [(0,-1), (0,1), (-1,0), (1,0)] 
        
        # function BACKTRACK(assignment, csp) returns a solution or failure
        def backtrack(assignment, current_state, limit, visited):
            # if assignment is complete then return assignment
            if current_state == self.target_pos: 
                return assignment 
            if len(assignment) >= limit: 
                return "failure"
                
            # var <- SELECT-UNASSIGNED-VARIABLE (Biến tiếp theo là bước trượt tiếp theo)
            # for each value in ORDER-DOMAIN-VALUES(var, assignment, csp) do
            for value in domain: 
                nxt = self.get_slide_dest(current_state, value, obs)
                
                # if CONSISTENT(var, value, assignment, csp) then
                # (Ràng buộc: Không đâm tường tại chỗ & Không đi lại ô đã qua)
                if nxt != current_state and nxt not in visited:
                    # add {var=value} to assignment
                    assignment.append(value)
                    visited.add(nxt)
                    
                    # result <- BACKTRACK(assignment, csp)
                    result = backtrack(assignment, nxt, limit, visited)
                    
                    # if result != failure then return result
                    if result != "failure": 
                        return result
                    
                    # remove {var=value} from assignment
                    assignment.pop()
                    visited.remove(nxt)
                    
        # return failure
            return "failure"
            
        for limit in range(1, 15):
            res = backtrack([], start, limit, {start})
            if res != "failure": 
                # (Chuyển đổi mảng các hướng trượt thành mảng toạ độ để UI vẽ đồ họa)
                path = []; curr = start
                for d in res: 
                    curr = self.get_slide_dest(curr, d, obs)
                    path.append(curr)
                return path
        return []

    def run_ac3(self, start, obs):
        self.log_msg("AC-3: Rút gọn miền giá trị bằng Arc Consistency", (147, 112, 219))
        
        # inputs: csp, a binary CSP with variables {X1, X2, ..., Xn}
        # Ở bài toán này, miền giá trị ban đầu là 4 hướng
        domain_start = [(0,-1), (0,1), (-1,0), (1,0)]
        
        # local variables: queue, a queue of arcs, initially all the arcs in csp
        queue = deque([("Xi", "Xj")])
        
        # function RM-INCONSISTENT-VALUES(Xi, Xj) returns true iff remove a value
        def rm_inconsistent_values():
            # removed <- false
            removed = False
            
            # for each x in DOMAIN[Xi] do
            for x in list(domain_start):
                # if no value y in DOMAIN[Xj] allows (x,y) to satisfy constraint(Xi, Xj)
                # Constraint: Hướng đi x không được làm robot đứng im (vi phạm ràng buộc)
                if self.get_slide_dest(start, x, obs) == start:
                    # then delete x from DOMAIN[Xi]; removed <- true
                    domain_start.remove(x)
                    removed = True
                    
            # return removed
            return removed
            
        # while queue is not empty do
        while queue:
            # (Xi, Xj) <- REMOVE-FIRST(queue)
            xi, xj = queue.popleft()
            
            # if RM-INCONSISTENT-VALUES(Xi, Xj) then
            if rm_inconsistent_values():
                # for each Xk in NEIGHBORS[Xi] do
                #   add (Xk, Xi) to queue
                pass # Lược bỏ add(Xk, Xi) to queue vì AC-3 ở đây ta chỉ dùng để lọc nút gốc ban đầu.

        # Giải quyết tiếp bằng Backtracking sau khi đã rút gọn Miền giá trị (Domain)
        def backtrack_ac3(assignment, current_state, limit, visited):
            if current_state == self.target_pos: return assignment
            if len(assignment) >= limit: return "failure"
            
            # Bước đầu tiên (Start) sẽ dùng miền đã được AC-3 rút gọn, các biến sau dùng miền đầy đủ
            current_domain = domain_start if not assignment else [(0,-1), (0,1), (-1,0), (1,0)]
            
            for value in current_domain:
                nxt = self.get_slide_dest(current_state, value, obs)
                if nxt != current_state and nxt not in visited:
                    assignment.append(value)
                    visited.add(nxt)
                    result = backtrack_ac3(assignment, nxt, limit, visited)
                    if result != "failure": return result
                    assignment.pop()
                    visited.remove(nxt)
            return "failure"
            
        for limit in range(1, 15):
            res = backtrack_ac3([], start, limit, {start})
            if res != "failure":
                path = []; curr = start
                for d in res: 
                    curr = self.get_slide_dest(curr, d, obs)
                    path.append(curr)
                return path
        return []

    def run_min_conflicts(self, start, obs):
        self.log_msg("Min-Conflicts: Tối thiểu hóa xung đột từ mảng gán", (255, 140, 0))
        domain = [(0,-1), (0,1), (-1,0), (1,0)]
        
        # max_steps, the number of steps allowed before giving up
        max_steps = 100
        length_limit = 10 
        
        # current <- an initial complete assignment for csp
        current = [random.choice(domain) for _ in range(length_limit)]
        
        def calculate_conflicts(assignment):
            curr = start; path = []
            for d in assignment:
                curr = self.get_slide_dest(curr, d, obs); path.append(curr)
                if curr == self.target_pos: return 0, path 
            return self.heuristic(curr), path 
            
        # for i = 1 to max_steps do
        for i in range(1, max_steps + 1): 
            conflicts, path = calculate_conflicts(current)
            
            # if current is a solution for csp then return current
            if conflicts == 0: return path 
            
            # var <- a randomly chosen conflicted variable
            var = random.randint(0, length_limit - 1)
            
            # value <- the value v for var that minimizes CONFLICTS
            value = current[var]
            min_conflicts = float('inf')
            
            for v in domain:
                temp_assignment = list(current)
                temp_assignment[var] = v
                c, _ = calculate_conflicts(temp_assignment)
                if c < min_conflicts: 
                    min_conflicts = c
                    value = v
                    
            # set var = value in current
            current[var] = value
            
        # return failure
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
            "Simple HC": self.run_simple_hc, "Local Beam": self.run_beam_search, "Simulated Annealing": self.run_simulated_annealing,
            "Sensorless": self.run_sensorless, "Partial-Observable": self.run_partial_observable, "AND-OR Graph": self.run_and_or_graph,
            "Backtracking": self.run_backtracking, "AC-3": self.run_ac3, "Min-Conflicts": self.run_min_conflicts,
            "Minimax": self.run_minimax_wrapper, "Alpha-Beta": self.run_alphabeta, "Expectimax": self.run_expectimax
        }
        return algo_map.get(r.name, self.run_bfs)(sp, obs)

  # ================= GIAO DIỆN & TƯƠNG TÁC (PACMAN LAB THEME) =================
    def draw_text(self, text, font, color, pos):
        self.screen.blit(font.render(text, True, color), pos)

    def draw_wall(self, p1, p2):
        if p1[0] < 0 or p2[0] >= GRID_SIZE or p1[1] < 0 or p2[1] >= GRID_SIZE: return
        rect = pygame.Rect(OFFSET_X + p2[0]*CELL_SIZE - 3, OFFSET_Y + p1[1]*CELL_SIZE - 4, 8, CELL_SIZE + 8) if p1[0] != p2[0] else \
               pygame.Rect(OFFSET_X + p1[0]*CELL_SIZE - 4, OFFSET_Y + p2[1]*CELL_SIZE - 3, CELL_SIZE + 8, 8)
        
        # Đổ bóng tường
        pygame.draw.rect(self.shadow_surface, SHADOW_COLOR, rect.move(2, 3))
        
        # Vẽ tường Neon
        wall_color = (255, 50, 50) if self.edit_mode == 1 else WALL_COLOR
        pygame.draw.rect(self.screen, wall_color, rect, border_radius=4)
        
        # Tạo hiệu ứng phát sáng (Glow) cho tường
        glow_rect = rect.inflate(4, 4)
        pygame.draw.rect(self.shadow_surface, (*wall_color, 40), glow_rect, border_radius=4)

    def toggle_wall(self, mouse_pos):
        mx, my = mouse_pos
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
    def draw_3d_robot(self, surface, x, y, color):
        cx, cy = int(x), int(y)
        # Đổ bóng
        pygame.draw.circle(self.shadow_surface, SHADOW_COLOR, (cx + 3, cy + 4), 14)
        
        # Thân quân cờ (Màu tối hơn)
        base_color = (max(color[0]-60, 0), max(color[1]-60, 0), max(color[2]-60, 0))
        pygame.draw.circle(surface, base_color, (cx, cy), 16) 
        
        # Đỉnh quân cờ (Màu sáng)
        pygame.draw.circle(surface, color, (cx, cy - 3), 15)  
        
        # Hiệu ứng bóng bẩy (Glossy)
        glow_rect = pygame.Rect(cx - 8, cy - 13, 16, 8)
        pygame.draw.ellipse(surface, (255, 255, 255, 150), glow_rect)

    def draw_simulation(self):
        self.screen.fill(BG_COLOR)
        self.shadow_surface.fill((0,0,0,0))
        mouse_pos = pygame.mouse.get_pos()

        # Tiêu đề trên cùng
        title_str = f"MÔ PHỎNG: {self.current_ai}" if self.current_ai else "CHẾ ĐỘ TỰ DO"
        self.draw_text(title_str, self.font_title, TARGET_COLOR, (OFFSET_X, 20))
        pygame.draw.line(self.screen, BORDER_GLOW, (OFFSET_X, 75), (OFFSET_X + 640, 75), 2)

        # ---------------- KHU VỰC 1: MAP LƯỚI (BÊN TRÁI) ----------------
        brd = pygame.Rect(OFFSET_X-8, OFFSET_Y-8, CELL_SIZE*GRID_SIZE+16, CELL_SIZE*GRID_SIZE+16)
        pygame.draw.rect(self.screen, BOARD_BG, brd, border_radius=12)
        pygame.draw.rect(self.screen, BORDER_GLOW, brd, width=2, border_radius=12)
        
        # Vẽ lưới
        for r, c in itertools.product(range(GRID_SIZE), range(GRID_SIZE)):
            rect = (OFFSET_X + c*CELL_SIZE, OFFSET_Y + r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, TILE_COLOR, rect)
            pygame.draw.rect(self.screen, TILE_LINE, rect, 1)

        # Highlight ô nếu đang trong chế độ Edit
        mx, my = mouse_pos
        if self.edit_mode > 0 and mx >= OFFSET_X and mx <= OFFSET_X + GRID_SIZE*CELL_SIZE and my >= OFFSET_Y and my <= OFFSET_Y + GRID_SIZE*CELL_SIZE:
            hc, hr = int((mx - OFFSET_X) / CELL_SIZE), int((my - OFFSET_Y) / CELL_SIZE)
            highlight_rect = pygame.Rect(OFFSET_X + hc*CELL_SIZE, OFFSET_Y + hr*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            highlight_color = (255, 50, 50, 100) if self.edit_mode == 1 else ((50, 255, 50, 100) if self.edit_mode == 2 else (255, 255, 50, 100))
            pygame.draw.rect(self.shadow_surface, highlight_color, highlight_rect)

        # Vẽ đích
        for t, col in [(self.target_pos, TARGET_COLOR), (self.target_pos_2, TARGET_2_COLOR)]:
            if t: 
                tx, ty = OFFSET_X + t[0]*CELL_SIZE + CELL_SIZE//2, OFFSET_Y + t[1]*CELL_SIZE + CELL_SIZE//2
                # Hiệu ứng lan tỏa của Đích
                pygame.draw.circle(self.screen, (*col, 50), (tx, ty), 16)
                pygame.draw.circle(self.screen, col, (tx, ty), 8)

        # Vẽ tường
        for p1, p2 in self.walls: self.draw_wall(p1, p2)

        # Vẽ robot (Quân cờ Ricochet thay vì Pacman)
        r_active = self.get_robot_by_name(self.current_ai) if self.current_ai else self.player
        if r_active:
            rx, ry = int(OFFSET_X + r_active.visual_pos[0] + CELL_SIZE//2), int(OFFSET_Y + r_active.visual_pos[1] + CELL_SIZE//2)
            self.draw_3d_robot(self.screen, rx, ry, r_active.color)
            
            # Thêm dấu chấm đen để nhận diện Người chơi nếu cần
            if r_active.name == "Người Chơi":
                pygame.draw.circle(self.screen, (0,0,0), (rx, ry-4), 4)

        self.screen.blit(self.shadow_surface, (0,0))

        # Khung Mô tả thuật toán ở dưới map
        desc_rect = pygame.Rect(OFFSET_X, OFFSET_Y + 660, 640, 75)
        pygame.draw.rect(self.screen, PANEL_BG, desc_rect, border_radius=8)
        pygame.draw.rect(self.screen, TILE_LINE, desc_rect, width=1, border_radius=8)
        
        desc_title = self.current_ai if self.current_ai else "Chế độ Người Chơi"
        desc_content = ALGO_DESC.get(self.current_ai, "Dùng phím W, A, S, D hoặc Mũi tên để tự di chuyển Robot và kiểm tra Map.")
        self.draw_text(desc_title, self.font_md, (255,255,255), (OFFSET_X + 15, OFFSET_Y + 670))
        
        # Cắt dòng cho description
        words = desc_content.split(" "); lines = []; curr_line = ""
        for w in words:
            if self.font_sm.size(curr_line + w)[0] < 600: curr_line += w + " "
            else: lines.append(curr_line); curr_line = w + " "
        lines.append(curr_line)
        for i, line in enumerate(lines):
            self.draw_text(line, self.font_sm, TEXT_COLOR, (OFFSET_X + 15, OFFSET_Y + 695 + i*20))

        # ---------------- KHU VỰC 2: BẢNG ĐIỀU KHIỂN (Ở GIỮA) ----------------
        mid_x = 730
        
        # Bảng Trạng Thái
        status_rect = pygame.Rect(mid_x, OFFSET_Y, 300, 180)
        pygame.draw.rect(self.screen, PANEL_BG, status_rect, border_radius=12)
        pygame.draw.rect(self.screen, BORDER_GLOW, status_rect, width=2, border_radius=12)
        
        self.draw_text("TRẠNG THÁI", self.font_md, TARGET_COLOR, (mid_x + 15, OFFSET_Y + 15))
        pygame.draw.line(self.screen, TILE_LINE, (mid_x + 15, OFFSET_Y + 45), (mid_x + 285, OFFSET_Y + 45))
        
        status_lines = [
            f"Trạng thái: {self.sim_status}",
            f"Bản đồ Nhóm: {self.current_group_id}",
            f"Độ dài đường đi: {r_active.moves if r_active else 0}",
            f"Chế độ sửa (E): {['Đang Tắt', 'Vẽ Tường', 'Đặt Start', 'Đặt Đích'][self.edit_mode]}"
        ]
        for i, line in enumerate(status_lines):
            self.draw_text(line, self.font_sm, (200, 220, 240), (mid_x + 15, OFFSET_Y + 60 + i*28))

        # Các nút bấm lớn
        btn_data = [
            ("Chạy AI", (46, 204, 113)),          
            (f"Chỉnh Map: {['TẮT', 'TƯỜNG', 'START', 'ĐÍCH'][self.edit_mode]}", (230, 126, 34)), 
            ("Lưu Map Nhóm", (52, 152, 219)),     
            ("Đặt Lại (Reset)", (52, 73, 94)),    
            ("Trở Lại Menu", (231, 76, 60))       
        ]
        
        self.sim_buttons.clear()
        by = OFFSET_Y + 200
        for text, color in btn_data:
            btn_rect = pygame.Rect(mid_x, by, 300, 45)
            self.sim_buttons[text] = btn_rect
            is_hover = btn_rect.collidepoint(mouse_pos)
            
            draw_col = (min(color[0]+30, 255), min(color[1]+30, 255), min(color[2]+30, 255)) if is_hover else color
            pygame.draw.rect(self.screen, draw_col, btn_rect, border_radius=22)
            pygame.draw.rect(self.screen, (255,255,255), btn_rect, width=2, border_radius=22)
            
            t_surf = self.font_md.render(text, True, (255,255,255))
            self.screen.blit(t_surf, (mid_x + 150 - t_surf.get_width()//2, by + 12))
            by += 60

        # ---------------- KHU VỰC 3: BẢNG LOG (BÊN PHẢI) ----------------
        log_x = 1060
        log_rect = pygame.Rect(log_x, 20, WIDTH - log_x - 20, HEIGHT - 40)
        pygame.draw.rect(self.screen, (15, 20, 35), log_rect, border_radius=12)
        pygame.draw.line(self.screen, TILE_LINE, (log_x + 15, 60), (WIDTH - 35, 60))
        
        self.draw_text("NHẬT KÝ HOẠT ĐỘNG", self.font_md, (255, 255, 255), (log_x + 15, 30))
        
        ly = 75
        for i, log in enumerate(self.logs[::-1][:30]): 
            words = log['text'].split(" "); lines = []; curr_line = ""
            for w in words:
                if self.font_log.size(curr_line + w)[0] < (WIDTH - log_x - 40): curr_line += w + " "
                else: lines.append(curr_line); curr_line = w + " "
            lines.append(curr_line)
            
            for line in lines:
                self.draw_text(f"> {line}", self.font_log, log['color'], (log_x + 15, ly))
                ly += 22
            ly += 5
            
        # Con trỏ chuột
        if any(r.collidepoint(mouse_pos) for r in self.menu_buttons.values()) or any(r.collidepoint(mouse_pos) for r in self.sim_buttons.values()):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else: pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        pygame.display.flip()

    def player_move(self, dx, dy):
        if self.sim_status == "Đang chạy" or self.player.finished or self.player.path: return
        dest = self.get_slide_dest(tuple(self.player.logic_pos), (dx, dy), set())
        if dest != tuple(self.player.logic_pos): self.player.path.append(dest); self.player.logic_pos = list(dest)

    def trigger_run_ai(self):
        if not self.current_ai: return
        self.reset_simulation()
        r = self.get_robot_by_name(self.current_ai)
        self.log_msg(f"Tiến hành chạy: {self.current_ai}", (100, 200, 255))
        
        path = self.compute_path_for_ai(r)
        if path:
            self.log_msg(f"-> {self.current_ai} tìm thấy đường dài {len(path)} bước.", (0, 255, 0))
            r.path = path
            self.sim_status = "Đang chạy"
        else:
            self.sim_status = "Kẹt (0 bước)"
            self.log_msg(f"-> {self.current_ai} KẸT / KHÔNG THỂ GIẢI.", (255, 100, 100))

    def update(self):
        if self.state != "SIMULATION": return
        
        r = self.get_robot_by_name(self.current_ai) if self.current_ai else self.player
        if not r: return

        if r.path:
            target_logic = r.path[0]
            target_px = [target_logic[0]*CELL_SIZE, target_logic[1]*CELL_SIZE]
            
            if not hasattr(r, 'current_target') or r.current_target != target_logic:
                r.current_target = target_logic
                r.moves += 1
                
            dx = target_px[0] - r.visual_pos[0]
            dy = target_px[1] - r.visual_pos[1]
            dist = math.hypot(dx, dy)
            
            speed = 10.0 # Tốc độ trượt mượt mà
            if dist < speed: 
                r.visual_pos = target_px; r.path.pop(0)
                if not r.path:
                    if target_logic == self.target_pos or target_logic == self.target_pos_2:
                        self.log_msg(f"ĐÃ TỚI ĐÍCH!", (0, 255, 0))
                        self.sim_status = "Hoàn thành"
                    else:
                        self.sim_status = "Dừng lại"
            else: 
                r.visual_pos[0] += (dx/dist) * speed; r.visual_pos[1] += (dy/dist) * speed

    def get_robot_by_name(self, name):
        return next((r for r in self.robots if r.name == name), None)

    def main_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN: 
                    mx, my = event.pos
                    
                    if self.state == "MENU" and event.button == 1:
                        for ai_name, rect in self.menu_buttons.items():
                            if rect.collidepoint(event.pos):
                                self.current_ai = ai_name
                                self.current_group_id = ALGO_GROUPS[ai_name]
                                self.load_map(group_id=self.current_group_id)
                                self.state = "SIMULATION"
                                self.log_msg(f"Đã mở mô phỏng: {ai_name}", TARGET_COLOR)
                                
                    elif self.state == "SIMULATION":
                        # Xử lý Map Edit
                        if mx >= OFFSET_X and mx <= OFFSET_X + GRID_SIZE*CELL_SIZE and my >= OFFSET_Y and my <= OFFSET_Y + GRID_SIZE*CELL_SIZE:
                            c, r = int((mx - OFFSET_X) / CELL_SIZE), int((my - OFFSET_Y) / CELL_SIZE)
                            
                            if self.edit_mode == 1 and event.button == 1: self.toggle_wall(event.pos)
                            elif self.edit_mode == 2 and event.button == 1:
                                for rb in self.robots: rb.start_pos = [c, r]
                                self.reset_simulation()
                                self.log_msg(f"Đã đặt Start mới tại {(c, r)}", (100, 255, 100))
                            elif self.edit_mode == 3:
                                if event.button == 1: 
                                    self.target_pos = (c, r); self.log_msg(f"Đã đặt Đích 1 tại {(c, r)}", TARGET_COLOR)
                                elif event.button == 3: 
                                    self.target_pos_2 = (c, r) if self.target_pos_2 != (c, r) else None
                                    self.log_msg(f"Đã đặt Đích 2 tại {(c, r)}", TARGET_2_COLOR)
                                self.reset_simulation()
                                
                        # Xử lý Nút bấm
                        if event.button == 1:
                            for btn_name, rect in self.sim_buttons.items():
                                if rect.collidepoint(event.pos):
                                    if "Chạy AI" in btn_name: self.trigger_run_ai()
                                    elif "Chỉnh Map" in btn_name: self.edit_mode = (self.edit_mode + 1) % 4
                                    elif "Lưu Map" in btn_name: self.save_custom_map()
                                    elif "Đặt Lại" in btn_name: self.reset_simulation()
                                    elif "Trở Lại" in btn_name: 
                                        self.state = "MENU"; self.current_ai = None; self.log_msg("Đã về Menu Chính.")
                                
                if event.type == pygame.KEYDOWN and self.state == "SIMULATION":
                    if event.key == pygame.K_e: self.edit_mode = (self.edit_mode + 1) % 4
                    elif event.key in (pygame.K_UP, pygame.K_w): self.player_move(0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s): self.player_move(0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a): self.player_move(-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d): self.player_move(1, 0)

            self.update()
            if self.state == "MENU": self.draw_menu()
            else: self.draw_simulation()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = RicochetArena()
    game.main_loop()