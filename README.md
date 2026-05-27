# 🧩 8-Puzzle Solver & Trace Table Generator

Bài tập môn **Trí tuệ Nhân tạo (Artificial Intelligence)**.
Chương trình mô phỏng trực quan các thuật toán tìm kiếm trên không gian trạng thái để giải quyết bài toán 8-Puzzle. Đặc biệt, công cụ này tự động sinh ra **Bảng vết (Trace Table)** với các bước xử lý (Node, Frontier, Reached) chuẩn xác như cách ghi chép trong vở trên lớp học.

---

## 📌 Thông tin Sinh viên
* **Họ và tên:** Phạm Đăng Khoa
* **MSSV:** 24110256
* **Môn học:** Trí tuệ Nhân tạo (AI)

---

## ✨ Tính năng nổi bật

1. **Giao diện trực quan (GUI):** Xây dựng bằng `Tkinter`, dễ dàng nhập trạng thái Start và Goal.
2. **Kiểm tra tính giải được (Solvability Check):** Tự động tính toán Inversions (số cặp nghịch thế). Cảnh báo ngay nếu bài toán vô nghiệm để tránh tràn RAM.
3. **Sinh Bảng Vết (Trace Table) chuẩn giáo trình:**
   * Tự động gán nhãn A, B, C, D... cho các đỉnh.
   * Hiển thị rõ ràng 3 cột: `NODE` | `FRONTIER` | `REACHED`.
   * Hiển thị chi tiết phép toán, đỉnh cha, hành động (UP, DOWN, LEFT, RIGHT).
   * In rõ chi phí đánh giá: `depth=...`, `g=...`, `h=...` hoặc `f=...(g+h)` ngay trong bảng.
4. **Trình phát lại (Playback):** Chế độ tự động chạy hoặc tiến/lùi từng bước để xem cách ma trận di chuyển sau khi tìm thấy đường đi đích.

---

## 🧠 Các thuật toán được triển khai

Chương trình hỗ trợ cả Tìm kiếm mù (Blind Search) và Tìm kiếm có kinh nghiệm (Heuristic Search). Quy tắc tính Heuristic được tinh chỉnh bám sát theo yêu cầu đặc thù của môn học:

### 1. Tìm kiếm mù (Uninformed Search)
* **BFS (Breadth-First Search):** Có 2 phiên bản xử lý tập Reached/Frontier khác nhau.
* **DFS (Depth-First Search):** Có 2 phiên bản ưu tiên độ sâu.
* **IDS (Iterative Deepening Search):** Tìm kiếm sâu dần có giới hạn độ sâu (Limit).

### 2. Tìm kiếm có thông tin (Informed Search)
* **UCS (Uniform Cost Search):** * Ưu tiên duyệt đỉnh có chi phí $g(n)$ nhỏ nhất. 
  * *Quy ước:* $g(n)$ là **số ô sai vị trí (tính cả ô trống 0)** cộng dồn từ nút Start.
* **Greedy Search (Tìm kiếm Tham lam):** * Ưu tiên duyệt đỉnh có $h(n)$ nhỏ nhất.
  * *Quy ước:* $h(n)$ là **khoảng cách Manhattan**.
* **A* (A-Star Search):** * Hàm đánh giá $f(n) = g(n) + h(n)$.
  * *Quy ước:* $g(n)$ là tổng Manhattan cộng dồn từ Start, $h(n)$ là Manhattan hiện tại đến đích.
* **IDA* (Iterative Deepening A*):** * Kết hợp tư tưởng DFS sâu dần với hàm đánh giá $f(n)$ của A*.
  * Ngưỡng (Threshold) khởi tạo bằng $h(Start)$ và tăng dần dựa trên chi phí vượt ngưỡng nhỏ nhất (min_exceeded).

---

## 🚀 Cài đặt & Sử dụng

### Yêu cầu hệ thống
* Python 3.x.
* Thư viện `tkinter` (Thường được cài sẵn kèm theo Python).

### Cách chạy chương trình
1. Clone repository về máy:
   https://github.com/phamdangkhoa3165-cmd/AI
   
2. Mở file UI_8_puzzle.ipynb bằng Jupyter Notebook, JupyterLab hoặc VS Code và chạy toàn bộ các cell.