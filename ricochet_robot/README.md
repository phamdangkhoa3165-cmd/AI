# 🤖 Ricochet Algorithm Laboratory

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.x-green.svg)
![License](https://img.shields.io/badge/License-MIT-orange.svg)

## 📖 Giới Thiệu
**Ricochet Algorithm Laboratory** là một môi trường mô phỏng (Simulation Environment) được xây dựng bằng Python và Pygame. Dự án này áp dụng và trực quan hóa các nhóm thuật toán Trí tuệ Nhân tạo (AI) khác nhau để giải quyết bài toán tìm đường và lập kế hoạch di chuyển cho robot theo quy tắc trượt của trò chơi Ricochet.

## 🧠 Các Nhóm Thuật Toán Đã Cài Đặt

Chương trình hỗ trợ 6 nhóm thuật toán AI chính, bao gồm:

### 1. Tìm Kiếm Mù (Uninformed Search)
* **BFS (Breadth-First Search):** Tìm kiếm theo chiều rộng, tối ưu số bước.
* **DFS (Depth-First Search):** Tìm kiếm theo chiều sâu.
* **IDS (Iterative Deepening Search):** Tìm kiếm sâu dần lặp lại.

### 2. Tìm Kiếm Có Thông Tin (Informed Search)
* **UCS (Uniform Cost Search):** Tìm kiếm chi phí đồng nhất.
* **Greedy Search:** Tìm kiếm tham lam dựa trên Heuristic (Khoảng cách Manhattan).
* **A* Search:** Kết hợp UCS và Greedy ($f(n) = g(n) + h(n)$).

### 3. Tìm Kiếm Cục Bộ (Local Search)
* **Simple Hill Climbing:** Lựa chọn lân cận tốt hơn đầu tiên (First-choice).
* **Local Beam Search:** Duy trì $k$ trạng thái tốt nhất.
* **Simulated Annealing:** Luyện kim/Lạnh đông - có tỷ lệ chấp nhận rủi ro.

### 4. Môi Trường Phức Tạp (Complex Environments)
* **Sensorless (Conformant Planning):** Lập kế hoạch đồng bộ từ nhiều trạng thái Niềm tin (Belief State).
* **Partial-Observable:** Môi trường mù một phần, robot tự định vị thông qua cảm biến ảo.
* **AND-OR Graph:** Lập kế hoạch dự phòng (Contingency Plan) xử lý bất định.

### 5. Thỏa Mãn Ràng Buộc (CSP)
* **Backtracking:** Quay lui tìm kiếm.
* **AC-3:** Cắt tỉa miền giá trị trước khi tìm kiếm.
* **Min-Conflicts:** Tối thiểu hóa xung đột để xếp chỗ cho các Robot trợ lý.

### 6. Tìm Kiếm Đối Kháng (Adversarial Search)
* **Minimax:** Giả định môi trường luôn chống lại Robot.
* **Alpha-Beta Pruning:** Tối ưu hóa Minimax bằng cách cắt tỉa các nhánh.
* **Expectimax:** Môi trường phản ứng ngẫu nhiên theo xác suất (Nút Chance).

## ⚙️ Yêu Cầu Hệ Thống & Cài Đặt
Yêu cầu máy tính đã cài đặt sẵn Python 3.x.

1. **Clone repository về máy:**
   ```bash
   git clone [https://github.com/phamdangkhoa3165-cmd/Ricochet-AI-HCMUTE.git](https://github.com/phamdangkhoa3165-cmd/Ricochet-AI-HCMUTE.git)

1. Cài đặt thư viện Pygame:
    pip install pygame

2. Khởi chạy chương trình:
    python ricochet_arena.py


## 🎮 Hướng Dẫn Sử Dụng
* Giao diện Menu: Chọn nhóm thuật toán mong muốn.

* Bảng điều khiển:
    - Nhấn **Chạy AI** để hệ thống tự động tính toán.

    - Nhấn **N** hoặc chọn chế độ **Từng bước** để theo dõi trace thuật toán chi tiết.

    - Phím **[** và **]** để thu nhỏ/phóng to ma trận sa bàn.

* Chỉnh sửa bản đồ (Nhấn phím **E**):
    - Tùy ý đặt tường cản, thay đổi vị trí xuất phát (Start) của Ta/Địch và Đích (Goal).

    - Hỗ trợ lưu trữ Map tùy chỉnh dưới dạng file .json.

## 👥 Đội Ngũ Phát Triển (Nhóm 6)
    1. Phạm Đăng Khoa - 24110256
    2. Nguyễn Trung Kiên - 24110263
    3. Trần Nguyễn Minh Hiếu - 24110212

---Dự án Báo cáo Cuối kỳ môn Trí tuệ Nhân tạo.---