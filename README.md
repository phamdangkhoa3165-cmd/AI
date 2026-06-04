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

### 1. Tìm kiếm mù (Uninformed Search)
* **BFS (Breadth-First Search):** Có 2 phiên bản xử lý tập Reached/Frontier khác nhau.
* **DFS (Depth-First Search):** Có 2 phiên bản ưu tiên độ sâu.
* **IDS (Iterative Deepening Search):** Tìm kiếm sâu dần có giới hạn độ sâu.

### 2. Tìm kiếm có thông tin (Informed Search)
* **UCS (Uniform Cost Search):** Ưu tiên duyệt đỉnh có chi phí $g(n)$ nhỏ nhất (đếm số ô sai vị trí).
* **Greedy Search (Tìm kiếm Tham lam):** Ưu tiên duyệt đỉnh có $h(n)$ nhỏ nhất (khoảng cách Manhattan).
* **A* (A-Star Search):** Hàm đánh giá $f(n) = g(n) + h(n)$.
* **IDA* (Iterative Deepening A*):** Kết hợp DFS sâu dần với hàm đánh giá $f(n)$ của A*.

### 3. Tìm kiếm cục bộ (Local Search)
Mục tiêu là đưa hàm $h(n)$ (Khoảng cách Manhattan) về 0.
* **Simple Hill Climbing (Leo đồi đơn giản):** Khảo sát từng lân cận, nếu có 1 lân cận tốt hơn ($h(Neighbor) < h(Current)$) sẽ chuyển ngay lập tức.
* **Steepest-Ascent Hill Climbing (Leo đồi dốc nhất):** Sinh TOÀN BỘ lân cận, tìm ra lân cận có $h(n)$ thấp nhất rồi mới quyết định chuyển trạng thái.
* **Stochastic Hill Climbing (Leo đồi ngẫu nhiên):** Sinh toàn bộ lân cận để lọc ra tập `Better_Neighbors` (tập các trạng thái tốt hơn hiện tại), sau đó **lựa chọn ngẫu nhiên** 1 trạng thái trong tập này.
* **Random-Restart Hill Climbing:** Thực hiện thuật toán Stochastic Hill Climbing. Nếu rơi vào cực tiểu cục bộ (bế tắc), thuật toán sẽ khởi động lại vòng lặp (Giới hạn `MAX_RESTART = 5`).
* **Local Beam Search (Tìm kiếm chùm cục bộ - k=3):** * Sinh ngẫu nhiên $k$ trạng thái ban đầu từ Start. 
  * Mỗi bước, lấy toàn bộ lân cận của cả $k$ trạng thái. 
  * Sắp xếp và chỉ giữ lại $k$ lân cận tốt nhất để làm hạt giống cho bước tiếp theo, loại bỏ phần còn lại.

---

## 🚀 Cài đặt & Sử dụng

### Yêu cầu hệ thống
* Python 3.x.
* Thư viện `tkinter` (Thường được cài sẵn kèm theo Python).

### Cách chạy chương trình
1. Clone repository về máy:
   https://github.com/phamdangkhoa3165-cmd/AI
   
2. Mở file `UI_8_puzzle.ipynb` hoặc `UI_8_puzzle.py` bằng IDE (VS Code, Jupyter...) và tiến hành chạy mã nguồn.